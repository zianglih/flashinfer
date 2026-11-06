# Conditional count-publication fence hypothesis

Status: source/memory-model review only, 2026-09-25. No candidate changes or GPU runs were made for this review. Do not implement this hypothesis unless matched `counts_overlap` SASS shows repeated per-expert release-fence cost, or measured timing warrants a separate controlled experiment. This note makes no performance claim.

## Verdict and exact proposed scope

The weakening is valid for the current early-consumer contract: finalized packed expert sizes and this rank's already-staged top-k scores. After the existing first `software_grid_sync`, every CTA0 dispatch thread that issues a count RED would execute one system acquire-release fence before entering the expert-publication loop. Each count contribution would then use the existing relaxed system u64 RED helper. Retain the trailing system fence, NB10 rendezvous, complete NVLink barrier, and its epilogue grid sync unchanged.

“One fence” means one dynamic fence per publishing thread before its loop, not a fence issued only by CTA0's leader. A leader-only fence with no additional synchronization does not order other threads' later count REDs.

## Proof for the current source

1. `stage_inputs` writes each live top-k score before dispatch preparation. The first grid synchronization in `dispatch_barrier` gathers those writes: NB10 transfers participant writes to each CTA's elected leader; its release GPU atomic, final-count observation, and acquire fence gather all CTA arrivals; the closing NB10 transfers visibility to every publishing thread. The new system fence would be after that complete sequence.
2. In PTX, a release/acquire-release fence followed in program order by a strong write forms a release pattern. A relaxed system RED supplies that write; the same fence can head patterns for multiple later REDs. Release patterns cover operations before the fence, including causally preceding operations from other threads. [PTX release/acquire patterns](https://docs.nvidia.com/cuda/parallel-thread-execution/#release-and-acquire-patterns).
3. For each destination expert, every source contributes exactly one u64 RMW with high word 1 and its finalized token count in the low word. An acquire load observing high word `world_size` observes all those contributions through atomic RMW observation order. It therefore synchronizes with every source's pre-loop fence, not merely the last contributor. RED need not acquire prior contributors itself; the scheduler's load is the acquire endpoint. [PTX observation order and synchronization](https://docs.nvidia.com/cuda/parallel-thread-execution/#observation-order).
4. Local count loads occur after the proposed fence, but their final values are operands of the REDs. No early reader needs the source's local count array; the grid barrier already finalized that array, and the atomic sum directly conveys the values. Assuming no low-word overflow, high-word completion also establishes the final low-word sum.
5. The scheduler's full-warp synchronization and existing scheduler publication preserve the downstream handoff. In particular, immediate scheduler DONE on a rank with no local expert work still publishes that rank's staged scores before idle workers prepare reduction. This proposal does not change those handoffs or authorize reading pending combine outputs.

## Why the original dispatch publication remains necessary

`expert_recv_count[src_rank, expert]` is written inside the publication loop, after the proposed pre-loop fence. Count readiness would **not** order these STGs. The current per-expert release RED orders them; the proposed weakening deliberately stops promising that ordering to early consumers. The scheduler does not read this matrix, so its present use is safe. `dispatch_pull` does read it to choose a source rank, and must remain after the trailing fence/NVLink/grid publication.

Source-token/top-k-slot metadata is scattered by `dispatch_prep` before the initial grid sync. Although those stores precede the proposed fence, dispatch warps do not consume the scheduler's acquire result. NB9 is not a scheduler-to-dispatch completion transfer: the scheduler arrives before polling, and dispatch arrives after its existing full publication. Therefore the current metadata reads in `dispatch_pull` continue to rely on the original dispatch publication. Do not move pulls or metadata reads ahead based only on scheduler count readiness. Input TMA pulls also retain their existing async-proxy publication requirements and payload-ready protocol.

The trailing fence drains in-loop metadata stores, NB10 transfers those writes to the NVLink-publishing warp, and the existing system release/acquire barrier plus epilogue grid sync transfers visibility to destination dispatch warps. This is a separate publication edge from early count readiness.

## Caveats and qualification gate

- Preserve system scope, aligned/full-width u64 atomic contributions and acquire loads, exactly one contribution per rank/expert, and the no-low-word-carry bound. The high word counts ranks, never CTA count; heterogeneous grids remain compatible.
- Preserve bank initialization, previous-bank cleanup, and invocation-generation retirement. A stale ready word from another invocation is not a valid acquire of current writes.
- Keep the fence after local grid synchronization and before every participating thread's first RED. Inspect emitted PTX/SASS; do not infer the generated ordering or cost from Python source.
- Any new early reader of in-loop metadata, or any write to scores after this fence, requires a new ordering proof. This fence does not wait for later dispatch/TMA/combine work.
- The existing generic/async-proxy and peer-memory atomic contracts remain prerequisites; this change does not replace proxy fences or extend supported transport scope.
- If implemented later, compare matched compiled variants before claiming a saving. Run the same changing-routing, empty/refill, graph-replay, partial-local-expert, and heterogeneous-grid qualification already prepared for `counts_overlap`.

## Source locations inspected

Paths are relative to `optimization/counts_overlap/` at the time of review:

- `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py:26`: NB9 arrival, system acquire count polling, full-warp visibility handoff; lines 111–137 stage route IDs and scores.
- `hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/grid_sync.py:73`: opening NB10; lines 113–120 release atomic, relaxed polling, acquire fence; line 134 closing NB10.
- `hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:737`: initial local grid sync; lines 745–783 publication loop, in-loop STG at 772, packed release RED at 782, trailing fence at 783.
- Same file, lines 1483–1533: NVLink publication/acquire and epilogue grid sync; lines 1570–1595: full publication, NB9 arrival, then pull; lines 915 and 963: per-source counts and source-token metadata reads.
- `hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/ptx_helpers.py:342`: release u64 RED helper; line 362 relaxed system counterpart.
- `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1006`: early score-register preparation contract; lines 1443–1463: input staging precedes dispatch body.
