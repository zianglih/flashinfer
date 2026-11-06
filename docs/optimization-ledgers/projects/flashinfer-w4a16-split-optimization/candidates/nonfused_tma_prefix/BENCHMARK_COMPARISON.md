# Split W4A16 non-fused finalize comparison

Before: `logs/retained-bounds-ep8-nonfused.json` SHA `50fdb26f6960de45489b7b8c76b02808bb0481e1fa9e11160c53e12b87a72f92`; after: `logs/candidate005-tma-prefix-ep8-nonfused.json` SHA `bba15abc63406410ce287539c0bf719c09a79c169c0b1b5bcc3a41004fe1e52c`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0645 | 37.5045 | 1.014932× |
| 2 | 44.1125 | 43.0080 | 1.025681× |
| 4 | 58.5290 | 58.1125 | 1.007167× |
| 8 | 70.6245 | 72.5925 | 0.972890× |
| 16 | 81.7610 | 82.2400 | 0.994176× |
| 32 | 113.2015 | 112.9605 | 1.002133× |
| 64 | 148.9135 | 148.4175 | 1.003342× |
| 128 | 151.8090 | 152.2730 | 0.996953× |
| 256 | 160.0970 | 160.2900 | 0.998796× |
| 512 | 164.4170 | 165.3460 | 0.994381× |
| 1024 | 182.6100 | 181.0420 | 1.008661× |
| 2048 | 224.5620 | 222.0340 | 1.011386× |
| 4096 | 329.0115 | 325.1070 | 1.012010× |
| 8192 | 630.3580 | 626.4380 | 1.006258× |

Tokens 8–8192: 1.000034× geometric speedup; -0.003383% latency; 6/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
