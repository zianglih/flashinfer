# Transitive FC1 drain and common epilogue loop audit

The existing `empty_bulk_drain.patch` remains sufficient and independently applicable. It removes the conditional empty bulk commit/wait only; no FC1/FC2 loop rewrite or additional synchronization removal is warranted by this audit. `git apply --check` also passes against the current halfguard-v3 source because the common loop is unchanged. The original baseline/proposed snapshots and historical manifest remain intact.

All source paths below are relative to `flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/` unless stated otherwise.

| Reachable path | Evidence / conclusion |
| --- | --- |
| Kernel → authored epilogue | `shim/w4a16/kernel.py:648–662,1281–1301` forces BF16 output/combine, `non_ubulk_fc2_store=True`, no in-kernel reduction and no overlapped accumulators. Only warps0–3 call it; FC1 TMA atom and epilogue SMEM are both `None`. |
| W4A16 FC1 body | `shim/w4a16/epilogue.py:278–314` overrides the parent's quantized `__call__`; the inherited FP4 FC1 body and its shared-to-global TMA are unreachable. Current v3 helper code at `:355–463` loads/updates TMEM, activates in registers, then uses `CopyUniversalOp` ordinary BF16 global stores. No bulk copy or bulk reduction is issued. |
| FC1 transpose | `src/moe_nvfp4_swapab/epilogue_refactor.py:769–873` contains only register permutations and tcgen05 TMEM load/store copies. These operations do not create a cp.async bulk group. |
| FC2 selection | Same vendor file `:1941–1979` chooses `make_fc2_stg_process_pipeline` because bulk, quantization and in-kernel reduction are rejected by the W4A16 constructor. Factory `:3126–3148` binds TMEM loads, register BF16 conversion, TMEM transpose and `fc2_stg_store_function`. The store at `:2918–2996` uses `CopyUniversalOp`; quantized SF branch is absent. |
| FC2 epilogue return | Router `:2012–2071` selects peer pointers from metadata, then ordinary STG. Completion `:1995–2009` uses a null address and compile-time `no_fire=True` for BF16 epilogue return. No per-tile FC2 release atomic or bulk store is issued. |
| FC2 dispatch return | Same STG pipeline writes the local full output workspace. Completion publishes the GPU-release FC2 done counter, which dispatch warps await before pushing. This publication remains unchanged. Actual push bulk copies and drains at `src/token_comm.py:1415–1416,1460–1461` belong to dispatch warps, not epilogue warps. |
| Input dispatch | Real G2S bulk copies/drains at `src/token_comm.py:1113–1114` also run in dispatch warps. The 512 role-reuse proposal reuses those warps for decode, never for epilogue; it does not alter the empty-group proof for warps0–3. |

Required ordering retained by the tiny patch:

- FC1's initial TMEM load fence before in-place transpose protects loaded gate/up registers from scratch reuse. Its final TMEM load fence and accumulator `consumer_release` protect all remaining transpose reads before the next MMA reuses the stage (`epilogue.py:313–314,402`). Neither is replaced by the bulk drain.
- The four-warp named barrier remains before completion signaling (`epilogue.py:217`). FC1's inherited signaling resolves the correct in-bound done slot and calls the phase-aware tracker (`epilogue_refactor.py:1323–1343`). The tracker ultimately executes `red.release.gpu.global.add.s32` (`src/flag_batch.py:111–119`, `src/ptx_helpers.py:429–447`), ordering ordinary stores through the preserved CTA rendezvous. The activation warp's counter wait uses GPU-acquire loads (`src/moe_nvfp4_swapab/moe_utils.py:93–114`).
- The next work item is still consumed before the prior tile's completion publication. It supplies the next phase required for batched-flag flushing; moving publication earlier without that state is not equivalent. FC2 metadata is already independent of FC1 completion, as documented in `FC2_METADATA_WAIT_MAP.md`.
- FC2 accumulator fences/releases, flag tracker tail flush, epilogue system fence, and the all-thread/peer tail rendezvous remain unchanged. Tail reset is explicitly bracketed by peer barriers (`src/token_comm.py:1783–1872`) for back-to-back launches. No source proof was established that removes another wait or fence.

The persistent scheduler supplies FC1/FC2 phase at runtime. The two distinct bodies are already statically selected Python/JIT helpers within that runtime branch, and overlapping-accumulator policy is already constexpr-disabled. A generic constexpr phase helper would still need the outer branch and would duplicate scheduler consumption/common state handling into each arm. The earlier scoped512 codegen demonstrates why such a broad loop/state rewrite should not be bundled with two empty instructions.

One separate bookkeeping simplification did survive actual codegen: BF16 epilogue-return FC2 still updates a null flag-batch state. It is not an additional synchronization removal. Exact source/phase proof, current SASS excerpts and an independently applicable candidate are in `../w4a16_fc2_no_publish_tracker/`. Keep it separate from the bulk-drain candidate and from halfguard/role reuse.

Validation boundary: CPU source/AST/Ruff and patch applicability only; no new GPU, compiler, numerical or timing run was performed here. Fresh codegen must confirm the removed UTMACMDFLUSH/DEPBAR and inspect control flow/resources before the normal numerical/lifecycle and adjacent timing gates.
