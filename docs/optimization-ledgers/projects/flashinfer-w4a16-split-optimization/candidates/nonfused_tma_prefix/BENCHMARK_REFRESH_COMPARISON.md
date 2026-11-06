# Split W4A16 non-fused finalize comparison

Before: `logs/baseline005-refresh-ep8-nonfused.json` SHA `d107025912d32113f846cf87cc3bf06c318cdeff2d3e3410828102137325d7e1`; after: `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` SHA `853295010250d8d1be1f84fd60741a35da55dbd68b4d15fb7b545cb112f3fdbd`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.2565 | 38.0800 | 1.004635× |
| 2 | 44.0000 | 44.0485 | 0.998899× |
| 4 | 58.3680 | 58.3690 | 0.999983× |
| 8 | 70.5445 | 70.7520 | 0.997067× |
| 16 | 81.6010 | 81.7130 | 0.998629× |
| 32 | 114.2410 | 113.1375 | 1.009754× |
| 64 | 149.7935 | 149.6980 | 1.000638× |
| 128 | 152.0810 | 151.8095 | 1.001788× |
| 256 | 159.5860 | 159.6970 | 0.999305× |
| 512 | 164.6730 | 164.4815 | 1.001164× |
| 1024 | 182.1295 | 181.3775 | 1.004146× |
| 2048 | 224.5940 | 222.0660 | 1.011384× |
| 4096 | 329.2190 | 325.9070 | 1.010162× |
| 8192 | 628.0225 | 625.4940 | 1.004042× |

Tokens 8–8192: 1.003451× geometric speedup; -0.343890% latency; 8/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
