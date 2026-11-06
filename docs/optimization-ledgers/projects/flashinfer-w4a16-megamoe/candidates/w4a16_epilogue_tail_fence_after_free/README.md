# Epilogue tail fence after TMEM free — held source candidate

Move the existing system fence below TMEM relinquish/free in the four epilogue warps. Keep it unconditional for both direct and reused-dispatch return, before the common kernel tail. This is a one-line reorder (+1/-1); it changes no pipeline, barrier participant count, record, tactic, interface, or vendor file. Primary remains untouched.

- Base repository HEAD: `8d7718c9a6c76e5722e1cf201395b0df538b081e`.
- Base kernel SHA-256: `5d6d7c6c5a4265b98feef5603ad215909dd60262fae628878dcc89f154786fab`.
- Proposed kernel SHA-256: `b6ba2019e2197246509c23c8ce3f74ab3fd07d0506b977142dac3a943e2e8d6f`.
- Patch SHA-256: `bd48468216901aafdd3247bd8483163c03071ca433fad79246a4b052fd71a4f5`.
- `base/` and `proposed/` contain only the affected repository-relative kernel file.

## Ownership and ordering

1. The target is `megamoe_kernel.py:1378–1415`. Epilogue work ends before relinquish/free in both versions. All epilogue threads still execute the same `fence_acq_rel_sys()` before `token_comm.kernel_tail`; its full-CTA rendezvous and cross-rank drain/reset sequence are unchanged.
2. Final accumulator/scratch reads already finish at retained `fence_view_async_tmem_load()` and accumulator releases (`epilogue.py:462–477` for FC2, `689–706` for FC1; empty/tail arms `449–450` and `607–608`). The final 128-thread epilogue rendezvous is retained at `241`, before the final completion publication and return at `252`. The store payload is RMEM by then (`tmem_epilogue.py:681–722`), so eventual global output visibility is independent of TMEM lifetime. No global output address aliases the shared TMEM holding/deallocation slots or the TMEM allocation.
3. CUTLASS 4.7.1 `TmemAllocator.relinquish_alloc_permit` selects only the allocator warp. `free` uses the shared TMEM pointer, and for C2 performs the peer deallocation mbarrier arrive/wait before deallocation. Neither method reads or publishes output data or readiness counters. See [the pinned allocator source, lines 514–581](https://github.com/NVIDIA/cutlass/blob/v4.7.1/python/CuTeDSL/cutlass/utils/tmem_allocator.py#L514). The current constructor selects allocator warp 0 and the existing dedicated shared deallocation barrier (`megamoe_kernel.py:1096–1105`).
4. Retained compiled N64 control independently exposes the relevant runtime operations at `profiles/cu132-recovery0910a-clc-removal-default-n64-001/codegen/dsl/*.ptx:6553–6588`: warp predicate; system fence; allocator-warp relinquish; shared TMEM pointer load; C2 peer mbarrier arrival/wait; TMEM deallocation. The allocator interval contains no global output load, global publication, or readiness test. This is inspection of saved control code, not candidate native validation.
5. Direct FC2 output is ordinary generic STG through `fc2_stg_store_function`; its `signal_fc2_done` uses `no_fire` (`epilogue.py:282–294`). The candidate retains each writer's system fence before the common tail rather than treating the GPU release tracker as system publication. Reused-dispatch return retains GPU release/acquire readiness and the separate dispatch return completion/system fence (`token_comm.py:1480`). Both modes retain `kernel_tail`'s NB8 (`1791–1795`), first rank barrier (`1829–1840`), reset, and final barrier (`1850–1861`). Thus moving the fence cannot let reset or consumer completion precede the existing system publication.
6. The vendor BF16 kernel already orders `relinquish_alloc_permit`, `free`, then the `enable_token_comm`-guarded system fence (`src/moe_bf16_glu/kernel_bf16_glu_fc12.py:1780–1783`). The guard is communication enablement, not return mode. The NVFP4 SwapAB kernel retains fence-before-free (`src/moe_nvfp4_swapab/kernel_fc12.py:2371–2373`); neither vendor file changes.

## Scope and evidence boundary

The opportunity is to issue TMEM release and, in C2, start the peer deallocation rendezvous while preceding global stores may still be completing. Benefit is unmeasured: ptxas may retain other dependencies, and other epilogue warps still fence before NB8. No sampled-PC bottleneck or speedup is asserted. The next native comparison should confirm the fence is after deallocation on the allocator path, still reached by all four epilogue warps before NB8, with unchanged MMA/decode code and resources. Existing numerical/performance adapters remain the runtime evidence path; this candidate adds no harness or knob.

A narrow search of `PERFORMANCE_LEDGER.md` and `w4a16_optimization_experiments.md` found only the earlier tail-scope extraction at `w4a16_optimization_experiments.md:1273`. It moved the unchanged three statements into the caller and explicitly preserved their order; this reorder is distinct.

Complete fence elision is not part of the candidate. The possible cumulative chain (epilogue stores → CTA tail barrier → dispatch grid barrier → system release/acquire rank barrier) is recorded only as an unproven, held idea. CTA synchronization or `GpuReleaseFlagBatchTracker.fire` alone is not a proof of direct peer-store system visibility.

Preparation used a unique exact-byte replacement and its inverse to establish the one-statement movement, then saved the diff and SHA-256 pins. No test, runtime import, compilation, GPU execution, remote operation, or primary edit was performed.
