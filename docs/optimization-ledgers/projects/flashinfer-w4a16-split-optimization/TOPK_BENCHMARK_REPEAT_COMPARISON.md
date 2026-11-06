# Split W4A16 top-k comparison

Complete BEFORE: `logs/baseline-repeat-ep8-fused.json` (`4a6b7731e660dad19769f432741bfa9ee9488030c4482f3c04ff9735f7ffc61b`). Complete AFTER: `logs/candidate-topk-repeat-ep8-fused.json` (`0fa87eb84e88ee1d58a80e0c88e72ff99769a2c9783096048e3048d05d64cf2e`).

hu-pdx-43, NVIDIA B300 SXM6 AC; single-GPU EP/TP simulation; upstream routing plus split W4A16; no inter-GPU communication. H7168/I2048/E256/top-k8, EP8/TP1, fused finalize. Ten warmups, 100 iterations, upstream cold-L2 CUDA-graph CUPTI medians. Routing is included.

| Tokens | Before (µs) | After (µs) | Speedup (before/after) | Latency change |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 37.488500 | 36.400500 | 1.029890× | -2.902223% |
| 2 | 44.160000 | 43.088000 | 1.024879× | -2.427536% |
| 4 | 59.232000 | 59.216500 | 1.000262× | -0.026168% |
| 8 | 76.001000 | 75.248500 | 1.010000× | -0.990119% |
| 16 | 84.432500 | 81.664000 | 1.033901× | -3.278951% |
| 32 | 115.729000 | 115.744500 | 0.999866× | +0.013393% |
| 64 | 150.177000 | 150.145500 | 1.000210× | -0.020975% |
| 128 | 154.209500 | 153.889000 | 1.002083× | -0.207834% |
| 256 | 161.521000 | 160.897000 | 1.003878× | -0.386327% |
| 512 | 166.722000 | 165.440500 | 1.007746× | -0.768645% |
| 1024 | 186.658000 | 183.713000 | 1.016030× | -1.577752% |
| 2048 | 232.834000 | 228.833500 | 1.017482× | -1.718177% |
| 4096 | 363.107500 | 352.626500 | 1.029723× | -2.886473% |
| 8192 | 700.038500 | 666.500000 | 1.050320× | -4.790951% |

Tokens 8–8192: geometric-mean speedup **1.015450×**, latency change **-1.521506%**; 10/11 lower latencies, 0/11 equal. Tokens 1/2/4 are reported and excluded from this aggregate.

One complete run per source; no row selection or statistical-significance claim. Saved results contain row medians, not the 100 underlying samples. Each row's saved tactic cache hash was checked; normal autotuning may select different tactics. This is single-GPU EP simulation and does not include inter-GPU transport. The adjacent JSON preserves full-precision medians, arithmetic, environment and measured-source hashes.
