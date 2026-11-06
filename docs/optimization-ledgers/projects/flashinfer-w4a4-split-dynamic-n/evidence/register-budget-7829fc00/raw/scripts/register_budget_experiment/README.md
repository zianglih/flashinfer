# Register-budget experiment (production frozen at 7829fc00)

This isolated experiment keeps the production core, layout, dynamic MMA N, all dtype branches, shared-memory stage count, scheduling, and public API unchanged. Only complete loader/epilogue warpgroups in the nine-warp overlap kernel reconfigure registers. The five-warp inline kernel is unchanged. GPU2 is assigned exclusively to this experiment on fi-w4a4-dyn-n-1024 (c1/ziangli), NVIDIA B200, image nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, CuTe DSL4.7.1.

## Source-traced contract

- Official PTX `setmaxnreg` requires the same instruction across all four warps in a warpgroup, explicit synchronization before subsequent reconfiguration, absolute counts in24..256 divisible by8, and a valid launch allocation. An increase blocks until the CTA register pool can satisfy it. Source: https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg .
- CuTe DSL4.7.1 `cute.arch.setmaxregister_decrease/increase` lower directly to NVVM setmaxregister. The older `warpgroup_reg_dealloc/alloc` aliases are deprecated. This was verified against the active remote package, not assumed from a local submodule version.
- CUTLASS input-transform GEMM explicitly computes the default as floor8(512/ceil(threads/128)) and leaves roles at that default unreconfigured: `include/cutlass/gemm/kernel/sm100_gemm_tma_warpspecialized_input_transform.hpp:392-406`. Read-only source checkout `/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/3rdparty/cutlass`, commit b46b16d003484063bca4ed365e44095c4c6ed633.
- Current FlashInfer blockscaled MegaMoE lean/base FC12 does not emit setmaxnreg. Its token-communication subclass enables an epilogue256/control72 policy, with control roles uniform at72. `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py:194-198,1609-1611,2279-2281`. No Mega sources are edited.
- Read-only DeepGEMM checkout `/Users/ziangli/playground/projects/muse-spark-open-nvfp4-audit/deepgemm`, commit cbe1727eacd9ad704795584ce1421dd1f5a8d67e: plain SM100 FP8/FP4 GEMM uses launch_bounds(total_threads,1) and no setmaxnreg; SM100 FP8/FP4 MegaMoE uses dispatch48/control40/epilogue208 or96/88/160 with an explicit <=64512 register budget assertion. That communication-heavy allocation is a precedent, not a directly reusable split-kernel budget.
- Prior W4A16 evidence: `../flashinfer-w4a16/w4a16_warp_specialization_constraints.md` and `w4a16_optimization_experiments.md:5093-5109,5281-5298`. Mixed targets within the control warpgroup hung. Later uniform budget changes were exact but noise/slower because long-scoreboard latency, not spills, was limiting.

## Bounded variants

- baseline: frozen7829 core and utility sources.
- r96: rejected loaderWG0 dec96/epilogueWG1 inc256. The first smoke stalled and was terminated; the actual nine-warp CTA register pool is smaller than64K.
- r128: generated but never launched; its128/256 budget is likewise invalid for the observed allocation.
- r96224: loaderWG0 dec96, epilogueWG1 inc224, MMA warp8 leaves its launch allocation untouched.
- r128192: same design with producer128/epilogue192, available if producer96 spills or loses performance.

The emitted CUBIN reports168 initial registers/thread. The physical CTA therefore owns288×168=48,384 registers. The rejected96/256 split requests128×96+128×256+32×168=50,432, exceeding that pool by2,048. The conservative96/224 and128/192 splits both require46,336. This distinguishes the launch allocation from the SM's64K physical capacity; simply satisfying a64K bound is insufficient.

`launch_guard.py` inspects every newly emitted register-reconfigured PTX/CUBIN before allowing its launch. It checks the physical thread count, uniform policy instruction counts, decrease/increase direction relative to the actual register count, and the physical CTA budget. This covers compilation-dependent differences across tactics and dtypes. The partial MMA warpgroup executes no reconfiguration instruction. All existing barriers retain their288 participants; no extra idle warps are introduced. Shared-memory footprints already constrain large shapes to one CTA per SM, so this experiment makes no occupancy-improvement assumption.

## Validation boundary

Task-local paired exact probes use all six supported format combinations, raw FC2/quantized FC1/per-token FC1, partial N, M384 channel tails, and sentinel output/SF storage. Native fixed-tactic phases use actual DeepSeek routing atT16384 and unchanged10/100 cold-L2 CUDA graph CUPTI timing with fallback fatal. These are diagnostic phase measurements, not new primary A1/B1 or retention results. No broad test/sanitizer campaign, no old baseline rerun, and no production edits.
