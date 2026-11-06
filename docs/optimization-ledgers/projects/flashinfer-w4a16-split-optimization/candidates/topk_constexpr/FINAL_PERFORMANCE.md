# Split W4A16 top-k specialization

### Final performance

- **Workload:** upstream DeepSeek-like benchmark, H7168/I2048,256 global experts, top-k8,32 local experts (single-GPU simulated EP8,TP1), SwiGLU, fused finalize, BF16 activations/output and NVFP4 weights. Routing is timed; weight preparation/autotuning and inter-GPU communication are excluded.
- **Timing:** normal autotuning for every complete sweep; ten warmups and100 cold-L2 CUDA-graph CUPTI iterations per row, reporting each row's median. Two complete before/after pairs on the same GPU; no row minima or fixed-tactic timing substitutions. Speedup is `sqrt((Before R1 / After R1) * (Before R2 / After R2))`.
- **Result:** geometric-mean speedup over8–8192 is **1.0147×** (**1.45% lower latency**). The two pairs separately give1.38% and1.52% lower latency. All11 combined retention rows improve; the repeat's32-token change is+0.0134% latency. Smaller gains remain close to run/tuning variation; two pairs do not establish statistical significance. Tokens1/2/4 are included below and excluded from the aggregate.

| Tokens | Before R1 (µs) | After R1 (µs) | Before R2 (µs) | After R2 (µs) | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 36.6720 | 36.4485 | 37.4885 | 36.4005 | 1.0179× |
| 2 | 42.7365 | 43.9370 | 44.1600 | 43.0880 | 0.9984× |
| 4 | 61.1360 | 58.8970 | 59.2320 | 59.2165 | 1.0190× |
| 8 | 74.8965 | 74.5765 | 76.0010 | 75.2485 | 1.0071× |
| 16 | 84.4805 | 84.0645 | 84.4325 | 81.6640 | 1.0193× |
| 32 | 116.4490 | 115.3620 | 115.7290 | 115.7445 | 1.0046× |
| 64 | 150.1130 | 149.8415 | 150.1770 | 150.1455 | 1.0010× |
| 128 | 154.2255 | 153.6330 | 154.2095 | 153.8890 | 1.0030× |
| 256 | 161.7455 | 161.3460 | 161.5210 | 160.8970 | 1.0032× |
| 512 | 166.4020 | 165.9530 | 166.7220 | 165.4405 | 1.0052× |
| 1024 | 186.6250 | 183.7770 | 186.6580 | 183.7130 | 1.0158× |
| 2048 | 232.5460 | 228.6420 | 232.8340 | 228.8335 | 1.0173× |
| 4096 | 362.3400 | 353.1870 | 363.1075 | 352.6265 | 1.0278× |
| 8192 | 711.8145 | 666.4225 | 700.0385 | 666.5000 | 1.0592× |

R1/R2 retain all measured row medians. The8192-token row selects the same GEMM1/GEMM2 tactic in all four sweeps and improves1.0503–1.0681×. Other rows can select different tactics under normal autotuning.
