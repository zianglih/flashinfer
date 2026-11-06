# Valid-route payload copy gate

All126 checks passed:90 grow/shrink graph cases and36 paired FC1→quantizer/FC2→combine cases. All six FC1 formats, original-token scales, generated quantized output, NaN-poisoned invalid FP8 rows, N16 physical tails and invalid mapping canaries were covered. Frozen442 supplies the paired core control; LDG256 full-zero prep supplies the timing control.

Only the private invalid payload store predicate changes. Full canonical SF initialization and every physical allocation/descriptor extent remain unchanged.

| Case | ABA control / variant / control (µs) | BAB variant / control / variant (µs) | Paired prep speedup |
|---|---|---|---|
| mxfp8-16384-256-r1 | 47.0720 / 42.5920 / 46.8480 | 42.6080 / 47.0240 / 42.5120 | 1.1037× |
| nvfp4-16384-256-r1 | 31.2800 / 29.3760 / 31.2965 | 29.4720 / 31.4395 / 29.5200 | 1.0655× |
| nvfp4-8192-128-r1 | 16.9280 / 16.1600 / 16.9600 | 16.0965 / 17.0405 / 16.0805 | 1.0538× |

Timing uses the unchanged10-warmup/100-sample cold-L2 CUDA-graph CUPTI callback. All1800 samples, resource reports, PTX/cubins and source hashes are archived. This is preparation-only evidence, not a full-MoE retention decision.

Initcheck was not requested or run. Default torch.empty scratch may contain physically read uninitialized invalid payload; no initcheck warning is waived. The first attempt passed90 graph checks then stopped at a positional-argument observer TypeError before candidate GEMM launch; the observer was corrected, source stayed unchanged, and the complete rerun passed.

The original source copies, historical tests/oracles and production repository were not modified.
