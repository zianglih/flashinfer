# Nemo3 Ultra NVFP4 T16384 existing-tactic comparison

Retained `0b7fe901`, EP8, standard NVFP4, input quantization included, unfused public functional API. GPU6; ABBA order; 10 warmups and 100 cold-L2 CUPTI graph samples per pass. No production changes or native AUTO rerun. Original campaign results and caches are unchanged.

| Arm | Tactic | First pass (µs) | Second pass (µs) | Geomean (µs) |
|---|---|---:|---:|---:|
| A, native winner | N128, 256×128 FC1/FC2 tiles, K8/4, 2 CTA, static | 577.635 | 574.146 | 575.888 |
| B, existing alternative | N256, 256×256 FC1/FC2 tiles, K4/4, 2 CTA, static | 612.434 | 609.651 | 611.041 |

B speedup relative to A is **-5.75%** (`100*(A/B-1)`), corresponding to 6.10% greater latency. Within-arm drift: A -0.60%, B -0.45%. The native winner remains better in this controlled comparison.

Both tactics are in the original 320 admitted candidates. Each replay reconstructs the same ordered list using the unchanged host admission method; its SHA-256 exactly matches the original native AUTO admission receipt. The original search persisted the winner but not the complete tactic ranking or individual measured times, so the historical rank of B cannot be recovered. Native telemetry records no profiling failures. Actual runtime dispatches confirm the requested geometry, K steps, static scheduling, and PDL for both FC1 and FC2.

The source-traced timing policies differ:

- The frozen benchmark passes `autotune_use_cuda_graph=False` for NVFP4. The runner sets `use_cold_l2_cache=True`; the plain `autotune(...)` context supplies no v2 measurement policy. `_profile_single_kernel` therefore takes its CUDA-event cold-L2 path, not CUPTI, and directly invokes the runner between events. The 2×L2 flush is outside the event interval.
- Public timing calls `bench_gpu_time(..., cold_l2_cache=True, enable_cupti=True, use_cuda_graph=True)`. Its CUPTI path likewise flushes 2×L2 between samples, then measures graph kernel spans. Input quantization is inside this public graph but outside the native runner profile. Thus cold-cache intent agrees, while launch/timer scope and the quantizer-to-MoE dependency chain differ.
- A bounded general policy experiment could use the existing public `autotune_use_cuda_graph=True` knob in a separately identified benchmark snapshot/cache and compare the resulting winners. This was not launched: the already-supported alternative lost this ABBA check, so there is no evidence here that a graph-tuning change closes this gap.

Source path references: frozen benchmark lines 197–205, 825–827, 835–840, and 376–386; `flashinfer/fused_moe/cute_dsl/tuner.py` lines 687–694; `flashinfer/autotuner/autotuner.py` lines 3542–3627 and 3767–3854; `flashinfer/testing/utils.py` lines 1049–1056 and 1680–1691. Exact source/cache identities, runtime dispatches, raw 400 samples, helper scripts and logs are alongside this report.
