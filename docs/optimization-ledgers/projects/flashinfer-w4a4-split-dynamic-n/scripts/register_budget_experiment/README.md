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

## Result: reject register reallocation

The96/224 policy passed270 paired exact cases:144 one-CTA cases atN32/128/256 and126 two-CTA cases atN128/256, across all six formats, FC2/quantized FC1/per-token FC1, partial routes, M384 channel tails, and sentinel guards. Every emitted reconfigured kernel reported168 initial registers/thread and passed the pre-launch budget guard. The128/192 alternative was checked byte-exact on the five native phase calls below; it did not receive the full270-case matrix because it had no material performance gain.

NativeT16384,N256,FC1M256/twoCTA,FC2M128/oneCTA medians in microseconds:

| Mode/phase | Frozen7829 | Producer96/epilogue224 | Producer128/epilogue192 |
| :--- | ---: | ---: | ---: |
| NVFP4 FC1 |326.481|327.8885|326.993|
| NVFP4 FC2 |193.504|193.857|193.776|
| MXFP8 FC1 |446.081|450.625|445.025|
| MXFP8 FC2 |280.1765|279.9835|280.416|
| Mixed FC2 |266.2235|266.272|266.432|

Both variants are byte-exact on these native calls. Mixed FC1 uses the unchanged inline path. Apparent gains are at most0.24%; no reversed timing or primary screen was justified. No production changes are retained.

The first nativeNVFP4 FC1 comparison used independently allocated outputs, and failed on unspecified padding bytes. Its log remains archived. The corrected harness reuses the captured output and scale buffers, clears them before each exact call, and then compares their entire byte storage. This passes. No arithmetic/layout workaround was applied to the kernel.

Generated native controls use80 registers for FC2,90 for NVFP4 FC1,88 for MXFP8 FC1, and118 for mixed inline FC1. The reconfigured kernels launch at168 registers/thread. All inspected native CUBINs have zero stack/local storage and no LDL/STL instructions in SASS. This is static generated-code evidence, not a new NCU run. Giving the epilogue more registers does not remove a measured spill bottleneck here. Adding12 warps solely to return more control registers therefore lacks a demonstrated benefit; an8-warp redesign would instead require changing the four-warp Gather4/scale producer ownership and synchronization, outside this rejected budget-only experiment.

Complete logs,100-sample arrays, generatedPTX/CUBINs, resource/SASS inspection, and frozen source snapshots are in `../../evidence/register-budget-7829fc00/raw/`. The original evidence archive is2,136,037bytes, SHA256 `a606328a0f802d58a77dc832883cb732eb9209329e8f890852e4286bb59a17a7`.
