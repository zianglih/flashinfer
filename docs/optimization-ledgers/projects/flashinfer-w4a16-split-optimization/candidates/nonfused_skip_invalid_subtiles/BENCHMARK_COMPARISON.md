# Split W4A16 non-fused finalize comparison

Before: `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` SHA `853295010250d8d1be1f84fd60741a35da55dbd68b4d15fb7b545cb112f3fdbd`; after: `logs/candidate007-useful-subtiles-ep8-nonfused.json` SHA `0673dacda369c4f6db2b7c31cb4440da4c324bbdb83003a85d34dd5c98d99e5c`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0800 | 38.0480 | 1.000841× |
| 2 | 44.0485 | 44.0490 | 0.999989× |
| 4 | 58.3690 | 58.4325 | 0.998913× |
| 8 | 70.7520 | 70.4805 | 1.003852× |
| 16 | 81.7130 | 81.6330 | 1.000980× |
| 32 | 113.1375 | 113.1850 | 0.999580× |
| 64 | 149.6980 | 149.7770 | 0.999473× |
| 128 | 151.8095 | 151.8730 | 0.999582× |
| 256 | 159.6970 | 160.1780 | 0.996997× |
| 512 | 164.4815 | 164.6100 | 0.999219× |
| 1024 | 181.3775 | 181.1690 | 1.001151× |
| 2048 | 222.0660 | 221.6660 | 1.001805× |
| 4096 | 325.9070 | 324.9155 | 1.003052× |
| 8192 | 625.4940 | 621.8620 | 1.005841× |

Tokens 8–8192: 1.001045× geometric speedup; -0.104435% latency; 6/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
