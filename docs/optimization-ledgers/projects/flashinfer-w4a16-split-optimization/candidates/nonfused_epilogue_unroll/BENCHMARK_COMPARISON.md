# Split W4A16 non-fused finalize comparison

Before: `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` SHA `853295010250d8d1be1f84fd60741a35da55dbd68b4d15fb7b545cb112f3fdbd`; after: `logs/candidate006-unroll-ep8-nonfused.json` SHA `d1f4bd9f15d1ac2f41a9de68bb21ec8cf9fce9b9fad3b5bb340583dc0b825e95`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0800 | 39.0720 | 0.974611× |
| 2 | 44.0485 | 44.1285 | 0.998187× |
| 4 | 58.3690 | 58.2085 | 1.002757× |
| 8 | 70.7520 | 70.5285 | 1.003169× |
| 16 | 81.7130 | 81.5365 | 1.002165× |
| 32 | 113.1375 | 112.9930 | 1.001279× |
| 64 | 149.6980 | 149.8890 | 0.998726× |
| 128 | 151.8095 | 152.0490 | 0.998425× |
| 256 | 159.6970 | 159.5855 | 1.000699× |
| 512 | 164.4815 | 164.4820 | 0.999997× |
| 1024 | 181.3775 | 181.3615 | 1.000088× |
| 2048 | 222.0660 | 221.2820 | 1.003543× |
| 4096 | 325.9070 | 325.1390 | 1.002362× |
| 8192 | 625.4940 | 626.5340 | 0.998340× |

Tokens 8–8192: 1.000798× geometric speedup; -0.079706% latency; 7/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
