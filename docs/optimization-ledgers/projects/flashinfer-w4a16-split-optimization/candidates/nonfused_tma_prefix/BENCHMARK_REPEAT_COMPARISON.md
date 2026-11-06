# Split W4A16 non-fused finalize comparison

Before: `logs/retained-bounds-ep8-nonfused.json` SHA `50fdb26f6960de45489b7b8c76b02808bb0481e1fa9e11160c53e12b87a72f92`; after: `logs/candidate005-tma-prefix-repeat-ep8-nonfused.json` SHA `6122a952ea7d4c1d1cd0306d1e25efb4c3cd2a38b317e3ba5a738d96f5511f54`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0645 | 38.0170 | 1.001249× |
| 2 | 44.1125 | 44.0000 | 1.002557× |
| 4 | 58.5290 | 58.0810 | 1.007713× |
| 8 | 70.6245 | 70.8490 | 0.996831× |
| 16 | 81.7610 | 81.6490 | 1.001372× |
| 32 | 113.2015 | 113.0250 | 1.001562× |
| 64 | 148.9135 | 149.8090 | 0.994022× |
| 128 | 151.8090 | 151.5690 | 1.001583× |
| 256 | 160.0970 | 160.2895 | 0.998799× |
| 512 | 164.4170 | 164.2895 | 1.000776× |
| 1024 | 182.6100 | 181.3140 | 1.007148× |
| 2048 | 224.5620 | 221.9700 | 1.011677× |
| 4096 | 329.0115 | 326.1150 | 1.008882× |
| 8192 | 630.3580 | 649.0790 | 0.971158× |

Tokens 8–8192: 0.999384× geometric speedup; +0.061598% latency; 7/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
