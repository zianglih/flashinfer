# Scheduler, accumulator and epilogue synchronization audit

Audited the split SM100 CuTe DSL MoE implementation at `9334cb34fe9c81653dc4748632f44449e9aecd8d` on 2026-10-27. The canonical checkout remains unchanged. This audit covers CLC/static work delivery, TMEM lifetime, accumulator handoff and epilogue stores. It does not modify MegaMoE, Rubin, autotune policy or the operand pipeline owned by the parallel audit.

**V1 candidate:** remove only the final 128-thread named barrier2 between allocation-permit relinquishment and TMEM free. All TMEM users have already joined named barrier1; both allocation operations execute in the same allocator warp, and the SDK retains its two-CTA deallocation rendezvous. The proof and focused validation boundary are in [terminal-barrier-proof.md](terminal-barrier-proof.md); its immutable patch/source hashes are in `source-receipt.json`. Root approved its source proof and the benchmark agent captured it in an immutable deployment before the active clone changed.

**V2 candidate:** move the existing bulk-store SMEM reuse wait after independent TMEM loads and conversion, immediately before the first shared overwrite. [Proof and validation boundary](v2-bulk-wait/README.md). This independent candidate is now unstaged in `flashinfer-sync-scheduler-20261027` at9334; it does not include V1. Its separate receipt is `v2-bulk-wait/source-receipt.json`.

## Source anchors

- **K:** `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` at the audited FlashInfer commit.
- **E:** `flashinfer/fused_moe/cute_dsl/blackwell/utils.py`, same commit.
- **P:** `flashinfer/fused_moe/cute_dsl/blackwell/custom_pipeline.py`, same commit.
- **SDK:** exact benchmark environment CUTLASS 4.7.1 captures in `scripts/clc_reference_audit_20261026/sdk-*.py`, especially `sdk-TmemAllocator.py`, `sdk-PipelineClcFetchAsync.py` and `sdk-ClcDynamicPersistentTileScheduler.py`. The `sdk-MbarrierArray.py` capture is in `scripts/clc_elected_owner_20261026/`.
- **CUTLASS reference:** `91843b71d90737e0a9b86f7d9df213cff5a3526f`, a separate current source reference, not a replacement for the installed SDK.
- **FlashMLA reference:** `395cb3afbb331fef7b1b21e9340861b9436b42d8`.

## Ownership, phases and lifetimes

| Object / source | Participants and protected lifetime | Audit decision |
|---|---|---|
| Common init fence and startup joins, K1359–1443 | All barrier constructors defer publication to K1437. Two-CTA launch joins the cluster before use; all worker and scheduler threads join TMEM retrieval barrier3. | Preserve the retained single final init fence. Removing constructor fences is already retained in `9c9ed58a`. TMEM startup role bypass variants were tested and rejected; do not repeat them. |
| TMEM pointer / barrier3, K1418–1443 | Allocator warp0 publishes the pointer; all CTA threads currently retrieve it. The same startup join also orders CTA-local barrier initialization before divergent roles begin. | Keep. A role that does not need TMEM could theoretically start sooner, but tested scheduler-only and actual-reader-only changes added control instructions without useful end-to-end gains. |
| Local decoded metadata ring, K1232–1248,1395–1405,2093–2148 | One elected publisher per CTA; all non-scheduler workers consume three integers and release the slot. Ring state advances for routed and terminal work, not padded cancellation tickets. | Keep one stage and independent phase. Metadata slot reuse follows worker **reads**, whereas operand/accumulator reuse follows asynchronous data processing; these are distinct lifetimes and cannot share an empty phase. |
| CLC request/raw response slot, K1406–1416,2112–2145 | Leader acquires empty, issues one query; exact SDK arms local/peer full barriers from lanes0/1 for two CTAs. Full scheduler warps read the response, execute the response reuse fence, and release CTA0's empty barrier. | Keep full-warp ownership, response fence and explicit cluster cardinality. Elected-loop variants regressed; SIMT participation count does not imply proportionally fewer instructions. |
| Metadata acquire before CLC request, K2109–2119 | Current metadata slot is secured before another cancellation is issued. Query overlaps current decode/publication. | Keep. The request-before-slot-acquire experiment regressed every measured decode case. Sharing this backpressure with accumulator emptiness would delay independent scheduling and alter the measured policy. |
| CLC terminal drain, K2150–2154 | CTA0 drains the final raw response; scheduler waits for the delayed PDL dependency before the final CTA join. | Keep raw response tail. It protects remote response/empty-barrier storage, unlike the already-removed local info tail. Final local CTA join is not independently a cluster-wide drain. |
| Accumulator full, K1385–1394,1745,1832,2084–2092 | MMA leader commits after all K work. All 128 epilogue threads per CTA wait before reading. | Keep. Operand full completion says inputs arrived, not that MMA output finished. Distinct phase/lifetime. |
| Accumulator empty, K1778–1779,1895–1898; E610–614,640–644,667–670,775–776,928–931 | Normal paths fence TMEM reads before release. Overlap paths release after the protected 64-column prefix, so later MMA can overlap remaining epilogue work. | Keep early-release boundary and caller final load fence. The helper can continue TMEM reads after its early fence; the caller fence is not an unconditional duplicate. |
| Accumulator producer tail, K2092; P395–408 | Leader waits for the final relevant empty phase; empty arrivals cover epilogue readers in both CTAs. | Keep pending a separate proof/codegen need. The final local CTA join alone does not establish completion of the peer CTA's last asynchronous/remote operations; removing tail and relying on later dealloc needs stronger cross-CTA lifetime reasoning. No candidate here. |
| SF32 shared maxima, E442–452 | Four epilogue warps publish maxima, join, read adjacent warp maxima, then join before the shared slot can be reused. | Both barriers are necessary for the current one-buffer exchange. The first is publication; the second prevents a fast warp's next store racing a slow warp's prior read. |
| Bulk-store SMEM ring reuse, E898–904 | Each issuing warp waits for its prior bulk-copy reads; 128-thread barrier then joins all readers before any writer reuses the shared stage. | Keep both, but V2 moves them after independent TMEM/register preparation and immediately before overwrite. A per-thread/warp bulk wait is insufficient for another warp overwriting that issuer's source rows. |
| Bulk-store publication, E958–988 | Threads write the transposed stage, issue the generic-to-async proxy fence and join all 128 threads before distributed row-copy issuers read the stage. | Keep proxy fence and join: visibility and inter-thread completion are different guarantees. |
| Bulk-store terminal drain, E994–995 | Complete all outstanding shared-memory reads and join every epilogue warp before scratch reuse by the next helper/channel tile or kernel teardown. | Keep. Global-write completion is not required for scratch reuse, so the retained `read=True` wait is appropriate. Carrying the ring across helper calls would require a separate lifetime/state redesign. |
| Whole-CTA final join, K2155–2157 | All producer, MMA, epilogue and scheduler roles have completed their loops/tails. Epilogue final load fences and bulk-copy read drains precede the join. | Keep: this is the actual common local TMEM/barrier lifetime boundary. |
| TMEM permit/free barrier2, K2158–2161 | Both SDK operations are internally restricted to allocator warp0. Warps1–3 have no intervening production or consumption. Named barrier1 already joined their prior work. | **Remove barrier2 only.** Keep the allocator warp guards and the SDK two-CTA peer handshake unchanged. |

## Branch and teardown checks

- **Static versus CLC:** static next-work has no metadata wait; CLC workers consume exactly one terminal record before leaving. Every role still reaches barrier1 once. No early return bypasses it.
- **Inline versus separate epilogue:** inline producer warps wait and consume accumulators before their producer tail; separate epilogue warps finish output work before barrier1. Both call the final TMEM-load completion fence.
- **Accumulator overlap:** reverse traversal changes which 64-column prefix may be overwritten next, not the final TMEM lifetime. Invalid/slab-skipped paths still release the expected empty phase exactly once. A release can precede unprotected TMEM reads, which is why the final caller fence remains.
- **Padded/empty work:** the scheduler may skip metadata for padded valid tickets, but publishes an invalid terminal record. Zero-tile paths still execute initialization and final joins; removing barrier2 does not create another bypass or change the deallocation count.
- **PDL:** scheduler metadata and weight-only startup may run before payload dependency completion. The scheduler's final dependency wait remains outside its loop; cleanup still follows it. No payload access moves ahead of its dependency wait.
- **Two CTAs:** local barrier1 joins all roles per CTA; SDK free then exchanges 32 arrivals per allocator warp with its peer before collective deallocation. The candidate retains both levels of synchronization.

## External references and transferable limits

[CUTLASS dense dynamic GEMM](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/examples/python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_dynamic.py#L1396-L1406) finishes its output/tmem completion join and then calls `relinquish_alloc_permit` and `free` adjacently. Its dense blockscaled example places a completion barrier between these calls, but that barrier supplies its reader join; it is not evidence for a universal additional barrier after relinquishment. Our independent barrier1 already supplies that join.

The [FlashMLA fused-core CLC loop](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/prefill/sparse/fused_norm_rope_attn_rope_cast_fwd/core_attn/kernel.cuh#L1188-L1212) explicitly drains cluster response consumers before exit. That supports preserving our raw-response tail. Its first work is directly derived; our initial weight prefetch already derives first work directly, and bypassing first metadata publication would require changing several worker phase machines. That remains a distinct unmeasured design, not a drop-in barrier removal.

FlashMLA's [head64 sparse decode epilogue](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/decode/sparse/head64/kernel.cuh#L375-L404) separately fences/joins shared-store publication and restricts TMEM free to warp0. Its attention pipeline has different ownership, so it cannot prove our epilogue barriers redundant.

## Closed axes and deferred ideas

The audit read `CLC_GENERALITY_2026-10-27.md`, elected-owner V2/V3 receipts, both TMEM startup dispositions, and retained init-fence evidence. Do not reopen elected-owner scheduling, request-before-acquire, deeper metadata queues, scheduler-only/reader-only TMEM bypass, or an extra tuning axis under a new name.

A ping-pong SF32-max scratch could potentially remove the second per-exchange barrier by carrying slot parity across every helper invocation. Likewise a bulk-store ring spanning helper calls could avoid repeated terminal drains. Both change lifetime/state protocols and can increase registers/SMEM; neither is claimed safe or beneficial here. V2 instead retains every bulk barrier and moves only independent work before the existing wait.

## Validation boundary

AST parsing, `git diff --check`, and scoped pre-commit (including mypy/ruff) pass. This is a source proof, not GPU validation. Before retention, reuse the existing exact/codegen machinery with both CTA groups, CLC and static schedules, inline/separate epilogues, PDL both ways, invalid/padded work and repeated launches. Verify the only intended synchronization removal is terminal `bar.sync 2,128`, with allocator peer handshake and all loop fences unchanged. No GPU work was launched by this audit.
