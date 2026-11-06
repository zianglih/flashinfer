# Decode reduction during transport cleanup

Design only; no production changes or GPU execution. Reviewed against the
decode-two-WG source `f4aea692749db40ba91a77a2e63c865c0dbf8572`. Paths below
are relative to `hashinfer-decode2wg/`.

## Conclusion

The first normal tail NVLink barrier is a valid combine-readiness boundary.
The two retired decode WGs can begin the unchanged ordered FP32 reduction
after that drain, while the dispatch WG resets counters and performs the
existing second publication barrier. Move the current second 640-thread
handoff to this earlier point; keep every existing transport fence, wait,
counter reset, cross-rank barrier and its order. This is a bounded opportunity,
not a measured improvement: reduction traffic could also delay cleanup.

## Smallest generic split

In `hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py`:

- Extract `kernel_tail_drain(...)`: the existing 640-thread named barrier 8
  (1791–1795), followed by the dispatch-only branch containing the optional
  `MEGA_USE_NCU` padding barrier and the first normal barrier (1799–1840).
- Extract `kernel_tail_cleanup(...)`: dispatch-only shared-prefix reset,
  publication barrier, then local-prefix reset, retaining 1841–1870 exactly.
  Its role guard and CTA/dispatch-relative indices are local to this helper.
- Keep `kernel_tail(...)` as consecutive drain/cleanup calls with the same
  existing arguments. It adds no handoff and preserves other callers' order
  and synchronization. These are two meaningful transport phases, not callbacks
  or a new public mode.

In `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py`, replace the
tail call and current finalizer handoff (1355–1366) with this structure:

```python
self.token_comm.kernel_tail_drain(...)
if cutlass.const_expr(not self.in_kernel_fc2_reduce and reduced_output is not None):
    # Same barrier 8, same next phase, all 640 threads, moved before cleanup.
    pipeline.NamedBarrier(barrier_id=..., num_threads=640).arrive_and_wait()
self.token_comm.kernel_tail_cleanup(...)
if cutlass.const_expr(not self.in_kernel_fc2_reduce and reduced_output is not None):
    if warp >= 12:
        # Existing WG-striped 256-worker loop and BF16 worker unchanged.
        ...
```

Cleanup is internally dispatch-only. Its eight decode warps skip that branch
and proceed with reduction while dispatch warps execute it. Do not place a CTA
barrier inside the dispatch-only cleanup branch. No final CTA barrier is needed:
normal kernel completion waits for both the cleanup and reduction threads.
IKR remains the original drain/cleanup sequence with no new handoff or reducer.
Zero-output raw thunks still join the handoff before their empty worker loop.

## Why data is ready after the first drain

For `epi_warps`, `tmem_epilogue.py:585–625` emits ordinary global stores, and
`megamoe_kernel.py:1342` performs a system fence before every epilogue thread
joins the first 640-thread tail rendezvous. The constructor requires this
non-ubulk FC2 store path (183–193).

For `reuse_dispatch_warps`, `token_comm.py:1390–1416` completes each outgoing
TMA store with a full `cp_async_bulk_wait_group(0)`, without `.read`; the
dispatch body ends with a system fence at 1480. The existing upstream
FC2-ready release/acquire and async-proxy publication remain unchanged.
`integrated-store-completion-review.md` records the exact chain and the pinned
CuTe wrapper's full-wait semantics. Its historical PTX excerpt was an input
pull, not outgoing return; an actual return-tactic PTX check remains part of
the new profiling plan and must not be claimed from that older excerpt.

All writers finish before the first tail rendezvous. The normal drain then
collects local dispatch CTAs, performs peer system-release/acquire signaling,
and redistributes completion to all local dispatch CTAs. See
`token_comm.py:1484–1559` and `src/src/grid_sync.py:98–134`. The moved next phase
of barrier 8 transfers that established readiness to every decode thread in
each CTA. It is essential: non-dispatch threads otherwise return from the
drain helper immediately after its initial rendezvous, before dispatch's
cross-rank barrier finishes.

The subsequent resets do not touch reduction inputs:

- Shared prefix ends before `src_token_topk_idx`; it contains only expert
  receive counters (`megamoe_kernel.py:1533–1560`).
- Local prefix ends before `l1_token_buffer`, covering accumulating counters
  (`1417–1482`). The actual `nvlink_barrier_counter` is deliberately **after**
  that boundary (`1484–1491`) and persists across launches; do not infer its
  placement from the more generic transport docstring.
- BF16 combine and FP32 top-k scores are separate symmetric allocations
  (`frontend.py:614–621`). The final output is a distinct local allocation.
  The worker uses global memory/registers only and does not reuse transport
  shared memory or TMEM.

## Next-invocation safety

1. All current combine stores are complete and visible before decode starts.
2. Dispatch performs the same shared reset, publication barrier and local reset
   while decode reads only combine/scores and writes final output. Preserve
   that publication barrier: it prevents a fast rank's next invocation from
   racing a slow rank's old shared-counter reset.
3. A rank cannot enqueue its next same-stream input staging/core past this
   kernel's completion until **both** its reducer and cleanup are finished.
   Therefore local scores cannot be overwritten during reduction.
4. A faster rank may start its next dispatch preparation while another rank
   still reduces, but that preparation does not overwrite combine slots.
   The next `dispatch_barrier` is before scheduler release and activation pull
   (`token_comm.py:1597–1622`); its internal NVLink rendezvous is at 787–798.
   A slower rank cannot join it until its prior local reduction finishes.
   Thus no next-invocation FC2 output can overwrite the previous combine data.

This retains the existing single-stream workspace ownership contract. It does
not make concurrent use of one workspace on independent streams safe.

## Constraints and checks before retaining

- Every actual CTA, including both members of a two-CTA cluster, and all 640
  threads must join both barrier-8 phases even with zero active output rows.
  Retain current persistent-grid residency assumptions and all barrier IDs.
- Keep the first drain's epilogue grid synchronization; a CTA-local arrival
  alone cannot establish all-rank readiness. Keep the existing number/order of
  NVLink barriers and `MEGA_USE_NCU` padding. Do not reset live grid counters
  before the second barrier finishes.
- Keep two 96-register decode WGs and all other role budgets unchanged. Do not
  promote an all-five-WG version of this ordering without another handoff:
  the dispatch WG is still occupied by cleanup.
- Static proof should compare the transport wrapper's expanded statement
  order with the original and verify only handoff placement changed in the
  W4A16 caller. Generated PTX must retain full return-store completion and
  place the reducer's first combine read after the moved handoff.
- Validate both return modes, N64/N128, O2/O3, empty-rank and graph cases,
  especially queued consecutive graph replays without an intervening host
  rank barrier. Run scoped sanitizer coverage. Compare paired 1–8192 timing
  against the unchanged decode-two-WG baseline, not against standalone split
  MoE, and inspect cleanup/reduction traffic before attributing gains.
