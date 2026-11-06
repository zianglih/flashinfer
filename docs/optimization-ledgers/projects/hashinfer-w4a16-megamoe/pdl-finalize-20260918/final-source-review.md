# Final PDL source and code-generation review

Reviewed HashInfer `230907919e2ee91ad82d1c209d85abf7e843c133` against baseline
`68eb1fefb84701131213e423f2c20cf953bb5918`. **No required source correction
found.** The PDL dependency placement preserves deterministic external
finalize and the existing cross-rank completion protocol. The register cap
has one accepted address spill; this is not a spill-free implementation.

Only three production files differ. Re-running `audit_cap_override.py`
recovered the baseline ASTs after removing exactly the PDL additions and
reducer compile options; all eight host constructor cases passed. No other
kernel math, transport, barrier, tactic, role budget, or launch geometry
changed. This review did not edit production or launch GPU work.

## Dependency and remote-memory correctness

- `megamoe_kernel.py:793–799` retains ordinary incoming stream ordering.
  It does not opt into PDL as a consumer of input staging. Staging writes the
  local activation, index, and FP32 score buffers; optional alpha copies
  remain before the producer on the same current stream
  (`backend.py:200–211`, `frontend.py:448`).
- `megamoe_kernel.py:969–972` signals from one elected lane of warp 0 in
  **every** CTA, before cluster-leader selection. It is independent of token
  count or assigned expert work and includes both members of a two-CTA
  cluster. The condition is compile-time false for in-kernel FC2 reduction.
  Fresh producer PTX/SASS already reviewed under `fresh-codegen-review/`
  confirms the signal is not leader-predicated.
- Score prefetch is independent of producer results: source scores and
  combine output have distinct symmetric allocations (`frontend.py:586–590`).
  Token communication reads those scores and copies them to a different
  routed-input pool, rather than modifying the local source-score array.
- PDL does not itself establish cross-device completion. The retained
  transport protocol does: direct epilogue peer stores or completed dispatch
  bulk copies feed the all-role CTA tail rendezvous (`token_comm.py:1795`),
  the cross-rank drain (`:1829–1840`), shared-counter reset, and publication
  barrier (`:1843–1861`). Cross-rank publication uses system release and
  system acquire (`:1534`, `:1547`); local reset remains last (`:1864–1870`).
  Dispatch bulk-copy groups retain their completion waits (`:1415–1416`,
  `:1460–1461`). These NVSHMEM-backed symmetric-memory/peer-transport rules
  are unchanged. No local FC2 readiness signal replaces remote completion.
- `topk_reduce.py:424–427` then waits for **full** producer-grid completion,
  not merely its early launch signal. The first combine-buffer read is
  `:434`. The [PTX griddepcontrol contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-griddepcontrol)
  requires prerequisite completion and memory visibility for the executing
  thread. Thus completed local producer plus the retained remote drain is
  the dependency chain protecting local combine reads.

## Tail lanes, graph lifetime, and default isolation

- The original valid-worker guard encloses score loads, the wait, combine
  reads, and output writes (`topk_reduce.py:392–475`). Invalid tail lanes
  perform none of these accesses. The PTX wait is thread-local, so it does
  not require inactive lanes to join a CTA collective. Empty source ranks
  still participate in collective MegaMoE, then skip the zero-grid reducer
  (`frontend.py:426–429`).
- Metadata/pointer calculations before the wait do not read combine values.
  Prefetch-off cases also remain safe: their score loads and all combine
  reads occur after the wait. No output accumulation is moved before it.
- Existing warmup/capture checks, compiled-object ownership, symmetric
  buffers, and stream selection are unchanged. This patch does not shorten
  buffer lifetimes or start a subsequent workspace reuse early.
- Shared `TopkReduce` callers default to `enable_pdl=False`; non-BF16 formats
  reject explicit opt-in. Only this W4A16 external-finalize frontend enables
  PDL and applies the compiler cap. In-kernel reduction bypasses the reducer
  (`frontend.py:659–662`) and removes the producer trigger at compile time.
- The abandoned `min_blocks_per_mp=16` alternative is absent. There is no
  new shared-memory carveout or cache-config request. The producer's
  `min_blocks_per_mp=1` and 96-register CTA budget remain unchanged.

## Fresh cap32 generated code

Full-forward artifact:
`collected-profiles-cap32-override/evidence/profile-B2-t128-cap32-override/rank0/`.
It records final source `23090791` and manifest
`ccbd9971c24dfb9cf971d184096eb40e767ab15097aa096b8c437247946c19a2`.
Scope: H7168, top-k8, global128, EP8, fixed N64 two-CTA tactic.

- The full-forward reducer PTX and CUBIN are byte-identical to the isolated
  accepted leaf in `collected-leaf-cap32-override/`.
  Reducer CUBIN SHA256:
  `82f8c3880088860f9f75ea5545f0d623c15b0cb80d89f68b4f83ec7a5e21bad3`.
- Reducer PTX remains byte-identical to the uncapped PDL reducer. The cap
  affects backend register allocation, not the PTX arithmetic or wait.
- Actual SASS executes the two score `LDG.E.128` instructions at `0x1a0`
  and `0x1b0`, `ACQBULK` at `0x1c0`, then all eight combine vector loads
  beginning at `0x1d0`. No branch occurs before the valid specialization's
  exit. It contains four `FMUL2`, 28 `FFMA2`, and one output vector store,
  matching the baseline arithmetic counts and ordered top-k recurrence.
- REG32, STACK8, SHARED0, LOCAL0. Despite LOCAL0, the SASS has one actual
  spill/store and reload: `IMAD.WIDE` at `0x110` forms the hidden-element
  offset, `STL.64` saves it at `0x120`, `LDL.LU.64` reloads it at `0x730`,
  and output-address `IMAD.WIDE` consumes it at `0x940`. No accumulator or
  routing-weight value is spilled. It is private per-thread stack storage,
  not communication state. This adds traffic/instructions whose performance
  cost must be measured, but does not change reduction precision/order.
- Producer PTX and CUBIN match the uncapped PDL producer exactly; CUBIN SHA256
  `c9fa948417caeb8983758402773b95672fb08f4e348ae86e4382785097df094c`.
  The override has not leaked into producer compilation.

## Optimization-level and evidence boundaries

`opt_level` applies to producer compilation (`frontend.py:262`); reducer
compilation retains the existing default O3. Therefore O2/O3 model cases
exercise two producer optimization levels with the same capped reducer,
not two reducer compiler levels. The explicit
`-maxrregcount=32 --override-directive-values` string is accepted by the
actual pinned parser (`runtime-source/parser-check.json`). The native
resource result establishes its effect for the sampled specialization.

The deterministic BF16 cast, FP32 routing multiplication, and ordered FP32
FMA combine are source-unchanged across token counts, N64/N128 producer
tactics, and supported hidden sizes. Other reducer specializations can have
different spill costs or register outcomes; REG32/STACK8 should not be
generalized as their measured resources. The cap is a resource request,
not evidence of concurrent execution or performance gain.

The collected final-commit native suite passed 25 EP1 cases and 17 cases
per EP2 rank (`collected-native-override/verification.json`), including
tail/empty/refill and graph behavior in the existing suite. The sampled
leaf output is bit-exact with the baseline. This audit does not substitute
for the separately tracked full O2/O3 accuracy matrix, sanitizer status, or
1–8192 timing results. It also does not claim graph-edge metadata from the
missing debug DOT. Actual overlap is a separate Nsight timeline finding.

**Approval:** no PDL, remote-completion, inactive-lane, API-isolation, or
arithmetic blocker found in the final implementation. No additional fence
or barrier is warranted by this change.
