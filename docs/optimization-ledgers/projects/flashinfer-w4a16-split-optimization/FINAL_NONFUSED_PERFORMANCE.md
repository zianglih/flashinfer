# Split W4A16 non-fused finalize comparison

Before: `logs/baseline-ep8-nonfused.json` SHA `8840cdf9772295391e834664621f254f67153e7f591edb4c0a99828a7b48ef54`; after: `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` SHA `853295010250d8d1be1f84fd60741a35da55dbd68b4d15fb7b545cb112f3fdbd`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0165 | 38.0800 | 0.998332× |
| 2 | 44.1925 | 44.0485 | 1.003269× |
| 4 | 58.4010 | 58.3690 | 1.000548× |
| 8 | 70.9120 | 70.7520 | 1.002261× |
| 16 | 81.5210 | 81.7130 | 0.997650× |
| 32 | 113.2335 | 113.1375 | 1.000849× |
| 64 | 150.2895 | 149.6980 | 1.003951× |
| 128 | 152.2260 | 151.8095 | 1.002744× |
| 256 | 159.8730 | 159.6970 | 1.001102× |
| 512 | 165.0575 | 164.4815 | 1.003502× |
| 1024 | 182.4180 | 181.3775 | 1.005737× |
| 2048 | 223.9215 | 222.0660 | 1.008356× |
| 4096 | 328.1150 | 325.9070 | 1.006775× |
| 8192 | 643.3660 | 625.4940 | 1.028573× |

Tokens 8–8192: 1.005561× geometric speedup; -0.553015% latency; 10/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
