# Full-chain cache contract audit, 2026-10-25

Read-only audit of corrected `aab93f854`. The PDL candidates change no cache
policy, so this inventory also applies to their tensor accesses. No MegaMoE,
production, source experiment, or GPU execution changes were made here.
Resolve the measured PDL code-generation confounder before implementing
cache changes.

**Decision update:** parent selected a different first bounded candidate after
the all-thread trigger restored FC1/FC2 codegen: FC2 nonfused output stores
LAST, paired with combine expert-input reads FIRST. All A/B/SF policies stay
unchanged; the final model-output store stays normal. The SFB proposal below
is an earlier audit option, not an active experiment. Actual source and
installed-API review is pinned in
`PDL_HANDOFF_CACHE_SOURCE_REVIEW_5f005c87_cb100e0a.json`.
This pair has a known last-use boundary, but does not guarantee residency:
FC2 output exceeds L2 and can displace active FC2 inputs before combine starts
reading it. Judge full-chain and FC2 costs, not combine alone. FIRST is a
priority hint, not an eager invalidation/reset. The shared finalizer also
changes W4A16 input-read priority; its output stores and arithmetic stay normal.

## Current accesses and data lifetimes

Paths below are relative to the source clone. “Default” means no explicit
priority in the inspected source, not a claim that the hardware bypasses a
cache. W4A16 is a read-only reference.

| Data / access | Current source policy | Reuse and lifetime | Proposed priority principle |
|---|---|---|---|
| Sort counts, tile→expert/limit, route maps and router weights | Native routing ordinary loads/stores/atomics; no explicit eviction priority found in the inspected `RoutingKernel.cuh` path. CuTe scalar metadata loads are bare `ld.global`. | Small, reused by preparation, many FC1/FC2 channel tiles and combine. Counts/offset construction is complete before its consumers' waits permit use. | Reusable metadata deserves LAST if a later narrow experiment needs it; do not change native sorting or atomics in the first candidate. |
| Original activation payload and linear SF → preparation | `moe_prepare.py:109–162`: 256-bit `CopyUniversalOp` payload, scalar U32 SF; no hint. Fresh PTX confirms `ld/st.global.v4.b64` and `ld/st.global.b32`. | One original token can feed several routed expert rows. Thus the input is not necessarily a one-use stream. | Keep NORMAL initially. Blind FIRST/no-allocate can destroy top-k reuse. |
| Prepared routed activation payload/SF → FC1 | Preparation stores default. Core B TMA default at `core:1122–1127`; SFB TMA helper passes explicit policy0 at `core:104`; small-N SFB uses 4-byte `cp.async.ca` with no priority. | Routed B panel/SFB reused across output-channel tiles and both group-2 CTAs. New preparation workspace is per invocation, alive through FC1. After FC1 it is dead. | Keep payload NORMAL to avoid retaining a large dead generation into FC2. The smaller SFB working set is a more conservative LAST candidate. Small-copy API support differs. |
| Weight payload A | `core:381–386,1096`: EVICT_FIRST (`0x12F0000000000000`) only for existing one-CTA K8; policy0 otherwise. | Streams over channels/K, but the same expert weights can be reused across multiple route panels. Wider geometry/NB2 changes this reuse. Weights are immutable and shared across invocations. | Preserve current policy. A global FIRST replacement is a previously losing axis; “all weights are streaming” is too strong. |
| Weight scales SFA | TMA default (`core:1098–1116`). | Follow weight tiles, smaller footprint; potentially reused across expert route panels. | Keep NORMAL first. Their weight association does not justify blindly using weight-FIRST or indiscriminate LAST. |
| FC1 quantized output and output SF → FC2 B/SFB | `blackwell/utils.py:495–529`: scalar SF store and ordinary vector payload stores, no hint. FC2 reads via the same B/SFB paths as FC1. | Producer→consumer handoff, then repeated across FC2 output-channel tiles. The original FC1 input is dead while this new intermediate is live. | Same payload-NORMAL / small-SFB-LAST candidate as FC1, without token/model/phase tuning. Default producer stores avoid prematurely retaining both generations. |
| FC2 BF16 output → combine | Default vector stores for the small path; bulk path uses bare `cp.async.bulk.global.shared::cta.bulk_group` in `utils.py:116–124`, with no L2 hint. Combine uses default 128-bit `CopyUniversalOp` (`moe_finalize.py:127–128,150–156`). | Each valid expanded row/channel sector is consumed once by combine. It is an immediate handoff, so the FC2 store is not dead streaming output. After combine reads it, it is dead. | Keep FC2 stores NORMAL. A later separate candidate can use FIRST on combine's input reads to demote consumed sectors, preserving the producer handoff. |
| Final combined output | Default 128-bit stores (`moe_finalize.py:170–173`). | The caller/next layer can consume it immediately; this backend does not own its future reuse. | Keep NORMAL/write-back. Do not mark final output FIRST merely because it leaves this function. |

`core` abbreviates
`flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`.
The host preparation placement is
`flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:139–158`.

## PDL overlap does not imply simultaneous tensor streams

Core startup allocates SMEM/TMEM and prepares descriptors before its wait,
but expert/route metadata and every operand TMA remain after that wait.
The early FC1→FC2 signal therefore lets FC2 initialize and then wait; it
does not let FC2 weights/activations stream while FC1 produces outputs.
Combine only preloads routing rows/scales before its wait; expert-output
loads are after it (`moe_finalize.py:131–156`).

Consequently, the observed full-chain overlap can cause scheduling/resource
competition and small metadata traffic, but is not evidence of concurrent
FC1 and FC2 payload streams competing in L2. L2 handoff/reuse still matters
after the wait. The N256 all-thread FC1 codegen restoration is a separate,
demonstrated mechanism and should not be attributed to cache priorities.

## Smallest uniform candidate after PDL codegen is settled

Use **NORMAL payloads, LAST for the smaller reusable SFB set**, preserving
the existing A/SFA/store policies. Apply the same semantic SF priority to
FC1 and FC2 at every geometry/dtype; implementing it for small cp.async
copies needs the explicit support described below. Metadata LAST and
consumed-combine-input FIRST are separate follow-ups, not changes to bundle
into the first comparison. This introduces no decode/prefill selector,
new public argument, new launch, or changed synchronization.

W4A16's B-LAST precedent (`blackwell/moe_w4a16_kernel.py:1457`, weight-FIRST
at1544, constants74–75) establishes a supported hint mechanism, not a proof
that the same complete allocation should remain promoted here. Parent's
native T16K footprint estimate is about79MB routed FC1 B+SFB,22MB FC2 B,
and235MB valid BF16 output. Retaining the first generation after FC1 can
displace the next handoff. The smallest B-LAST edit is still a useful
optional diagnostic after PDL is stable, but it is not the recommended
whole-chain default on source reasoning alone.

There is no reliable last-use demotion point in the current API: final
logical channel tile order does not imply completion order, while FC2's
post-predecessor wait proves FC1 completion but has no old routed-B pointer.
Adding that pointer and a demotion traversal would complicate the API and
add work. Do not add it before a demonstrated cache benefit. No proposed
priority is a retained optimization.

## Installed CuTe 4.7.1 implementation constraints

Read-only inspection of the active wheel under
`.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages`:

- `cutlass/cute/nvgpu/cpasync/copy.py:71–124`: `CopyG2SOp` accepts
  `cache_mode` (default ALWAYS); its `CopyG2STrait` has no cache-policy
  unpack override. Do not silently pass a TMA-style `cache_policy` to this
  small-copy path and claim it was honored.
- `cutlass/cute/nvgpu/common.py:339–393`: `CopyUniversalOp` is the ordinary
  copy with no extra memory attributes. `CopyG2ROp` and `CopyR2GOp` are the
  supported explicit-memory-attribute alternatives; their traits accept
  `cache_policy` at457–479 and536–558. A future combine read hint should
  preserve its existing vector width, addresses, masks and math.
- SFB TMA already uses a private inline-PTX helper with a policy operand;
  replacing its zero constant with LAST is straightforward. Uniform SFB
  coverage also needs an explicitly verified 4-byte cp.async hint helper;
  it is not provided by the current small-copy abstraction.
- The 4-byte SF transfer cannot simply become `.cg`: PTX permits only
  16-byte transfers for `cp.async.cg`. Preserve 4-byte predicates and
  zero-fill, source extent and the corrected proxy fence.

See [PTX cp.async](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async)
and [cache operators](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#cache-operators).
Cache hints do not establish memory visibility or replace barriers.

## Conflicts and evidence boundaries

- LAST is not a reservation. Marking all weights, both activation
  generations, SF and large FC2 output LAST removes useful priority
  separation. Dead FC1 input can remain promoted and displace live FC2
  input; logical last-channel-tile order is not actual last use under
  persistent scheduling, so it cannot safely identify a final demotion.
- FIRST on FC2 stores can evict data before combine reads it. FIRST on
  raw preparation reads can defeat repeated-token reuse. Final output
  is not known dead to this backend.
- Hints do not authorize input reads before PDL waits, remove the FC2
  metadata release fence, or replace source/TMEM ownership. Do not use
  invariant/noncoherent loads merely because metadata is read-only inside
  one invocation: graph replays can update those buffers.
- No process-wide persisting-L2 window, global cache setting or graph
  mutation is proposed. Those would change attribution and other kernels.
- `scripts/cache13_experiment/README.md` records prior B-LAST evidence:
  insufficient for retention, approximately neutral at NV8K NB2 and a
  small NV16K improvement, with decode mixed. Its older Gather4 input
  path differs from the current prepared-B path. A-FIRST globally and
  broad descriptor prefetch were already tested negatively; see also
  `scripts/pipeline_cache_experiment/README.md:95`.
- No new benchmark run is requested by this audit. If authorized later,
  inspect emitted hint operands and unchanged resources first, then use
  adjacent native full-chain pairs after PDL source is frozen. Isolated
  phase cache wins cannot substitute for decode-and-prefill chain gains.
