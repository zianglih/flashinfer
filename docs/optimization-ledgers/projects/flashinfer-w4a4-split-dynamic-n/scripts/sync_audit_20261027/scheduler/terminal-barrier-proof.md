# Terminal TMEM barrier2 removal

Candidate base: `9334cb34fe9c81653dc4748632f44449e9aecd8d`. One deleted line in the SM100 split CuTe DSL common kernel. The entire `warp < 4` cleanup block, both SDK calls, final barrier1, pipeline tails, TMEM wait fences and two-CTA handshake remain unchanged.

## Happens-before argument

1. Before the existing all-CTA named barrier1 (kernel2155–2157), each epilogue path completes its final TMEM loads. Bulk-copy paths also complete all asynchronous shared-memory reads before recycling their shared staging buffers. MMA/operand/CLC producer tails remain in place.
2. Barrier1 joins every local role, including all four epilogue warps, producer warps, MMA warp and optional scheduler warp. Consequently no local thread still uses TMEM when the cleanup block begins.
3. In the exact installed CUTLASS4.7.1 `TmemAllocator.relinquish_alloc_permit` (`sdk-TmemAllocator.py:305–324`), only `allocator_warp_id` issues the instruction. This kernel sets that id to0. Warps1–3 do not publish any new state in this call.
4. `TmemAllocator.free` (`:326–376`) similarly restricts its device operations to allocator warp0. The relinquish and free operations are therefore sequential instructions of the same participating warp. There is no producer in another warp whose post-barrier1 operation the removed barrier2 could order before free.
5. For two CTAs, `free` retains a separate peer-CTA mbarrier arrive/wait before collective deallocation (`:358–369`). Each CTA's allocator warp can enter this handshake only after its own barrier1. Thus neither CTA deallocates until both local TMEM-use joins have completed. Removing the additional **CTA-local** barrier2 does not remove this peer rendezvous.
6. The branch `warp < 4` is warp-uniform and includes every lane of allocator warp0. It is unchanged. There are no new early exits, partial-warp calls, changed participant counts, or phase advances.

The official [PTX TMEM allocation-management contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-instructions-tcgen05-alloc-dealloc-relinquish-alloc-permit) requires all lanes of each issuing warp to execute the aligned synchronous instruction. Two-CTA deallocation additionally requires peer TMEM accesses to be synchronized. It does not require 128 threads to rendezvous between relinquishing the permit and deallocating storage. The existing local join and SDK peer rendezvous meet those distinct requirements.

## Why an older local note said to keep it

`scripts/epilogue_codesign_audit/PIPELINE_SYNC.md` and `REGISTER_ROLES.md` conservatively described barrier2 as part of the allocation/free collective and preserved it while changing other pipelines. That scope decision did not inspect the exact allocator's internal warp guard or establish a dependency involving warps1–3 after barrier1. This audit supplies that missing ownership proof. It does not remove the true final TMEM-use join or the cluster handshake.

## Independent precedent, not proof by analogy

The pinned [CUTLASS dynamic dense GEMM](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/examples/python/CuTeDSL/cute/blackwell/kernel/dense_gemm/dense_gemm_persistent_dynamic.py#L1396-L1406) performs its completion join and then calls relinquish/free directly. This corroborates the allocator contract; the proof above depends on our actual phases and installed4.7.1 SDK, not this newer example.

## Expected effect and limits

The source removes one terminal128-thread named barrier per launched CTA, without adding an instruction or state variable at source level. Compiler/codegen validation must confirm that removal and unchanged resource usage. A visible end-to-end speedup is not assumed; this is also a synchronization/instruction simplification candidate. No GPU or sanitizer claim is made until the coordinated gates run.
