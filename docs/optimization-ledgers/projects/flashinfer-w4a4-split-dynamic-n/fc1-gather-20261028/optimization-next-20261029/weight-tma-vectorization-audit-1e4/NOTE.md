# Weight TMA channel coalescing: compile-time feasibility only

Current source `1e4b127a` emits A/SFA copies for each of up to two physical MMA channel tiles. A read-only CuTe4.8 probe tried merging the channel coordinate into each stage's M mode while preserving every existing shared-memory offset. It also tried the general TMA builder with an explicit gapped-M logical tiler instead of the MMA-specific builder. Three formats cover NVFP4 K256, MXFP4x8 K128 and MXFP8 K256.

All three representations produce the same TMA atom vector length as the existing one-channel builder. This does not establish fewer hardware copy instructions: the extra channel remains a residual copy dimension. No production change or GPU benchmark is justified by these two layout-only formulations. An explicit higher-rank global descriptor or a different shared layout remains a distinct, untested design; this is not a hardware impossibility claim.

The probe used `CUDA_VISIBLE_DEVICES=""`, `CUTE_DSL_ARCH=sm_103a` and compiled host-only layout/descriptor IR. No compiled function was called, no owned kernel was launched, no device was allocated and no performance claim is made. Existing persistent compiler caches were preserved. Source probes and raw compiler output remain here. No review clone was created.
