# Per-token public NVFP4 audit

Read-only capability audit at clean2b7. Recipe: `NVFP44Over6Config(e4m3_max=256, err_mode="MSE", err_use_fast_math=True)`; separate base math setting `FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1`. Use the same recipe for initial and FC2 activation quantization; CuTe FC2 inverse scale is1/(256*6), not the current benchmark1.0. Sharedweights remain standardNone and outside per-token math context.

The C++ env getter rereads both FLASHINFER and TRTLLM aliases every call. CuTe reads perhostcall and keys compilation bybool+recipe. Keep context active acrosswarmup/AUTO/capture/timing; restorebeforeotherarms. Global4over6env is unnecessary andmustnot contaminate per-tensor/W4A16/MX.

Dedicated per-tokenselectors replace globalCLIflag. Full native medians needuniquelabels andper-armmetadata; no CuTe before/after campaigns. TRT is the performance baseline. Focused verification isplannedonly; noGPUlaunch fromthis audit.
