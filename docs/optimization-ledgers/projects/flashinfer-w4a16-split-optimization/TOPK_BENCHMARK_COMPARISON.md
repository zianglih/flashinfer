# Split W4A16 top-k comparison

Complete BEFORE: `logs/baseline-ep8-fused.json` (`0fdb419648d83b340566eef9d800c0958efd405a0a874f4bb35cad8a822f357d`). Complete AFTER: `logs/candidate-topk-ep8-fused.json` (`586ccdb4578d1b02058e6c221aff528909091b47d35e6b911a030a19b333fd40`).

hu-pdx-43, NVIDIA B300 SXM6 AC; single-GPU EP/TP simulation; upstream routing plus split W4A16; no inter-GPU communication. H7168/I2048/E256/top-k8, EP8/TP1, fused finalize. Ten warmups, 100 iterations, upstream cold-L2 CUDA-graph CUPTI medians. Routing is included.

| Tokens | Before (µs) | After (µs) | Speedup (before/after) | Latency change |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 36.672000 | 36.448500 | 1.006132× | -0.609457% |
| 2 | 42.736500 | 43.937000 | 0.972677× | +2.809074% |
| 4 | 61.136000 | 58.897000 | 1.038016× | -3.662327% |
| 8 | 74.896500 | 74.576500 | 1.004291× | -0.427256% |
| 16 | 84.480500 | 84.064500 | 1.004949× | -0.492421% |
| 32 | 116.449000 | 115.362000 | 1.009423× | -0.933456% |
| 64 | 150.113000 | 149.841500 | 1.001812× | -0.180864% |
| 128 | 154.225500 | 153.633000 | 1.003857× | -0.384178% |
| 256 | 161.745500 | 161.346000 | 1.002476× | -0.246993% |
| 512 | 166.402000 | 165.953000 | 1.002706× | -0.269828% |
| 1024 | 186.625000 | 183.777000 | 1.015497× | -1.526055% |
| 2048 | 232.546000 | 228.642000 | 1.017075× | -1.678808% |
| 4096 | 362.340000 | 353.187000 | 1.025915× | -2.526080% |
| 8192 | 711.814500 | 666.422500 | 1.068113× | -6.376942% |

Tokens 8–8192: geometric-mean speedup **1.014026×**, latency change **-1.383239%**; 11/11 lower latencies, 0/11 equal. Tokens 1/2/4 are reported and excluded from this aggregate.

One complete run per source; no row selection or statistical-significance claim. Saved results contain row medians, not the 100 underlying samples. Each row's saved tactic cache hash was checked; normal autotuning may select different tactics. This is single-GPU EP simulation and does not include inter-GPU transport. The adjacent JSON preserves full-precision medians, arithmetic, environment and measured-source hashes.
