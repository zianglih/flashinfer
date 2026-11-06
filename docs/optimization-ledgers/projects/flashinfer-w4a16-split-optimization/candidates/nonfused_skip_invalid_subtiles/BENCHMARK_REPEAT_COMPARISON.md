# Split W4A16 non-fused finalize comparison

Before: `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` SHA `853295010250d8d1be1f84fd60741a35da55dbd68b4d15fb7b545cb112f3fdbd`; after: `logs/candidate007-useful-subtiles-repeat-ep8-nonfused.json` SHA `60f8bd7539d7f311004b1be5d636816d45e8e2223ebdaa0cf61f6dc65f0a9b2d`.

Complete same-mode 1–8192 normal-auto sweeps, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations. H7168/I2048/E256/top-k8; EP8/TP1 simulation on one B300, routing included, no inter-GPU transport. Source bytes, all row-cache hashes, routing histograms and protocol fields verified.

| Tokens | Before (µs) | After (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0800 | 38.0645 | 1.000407× |
| 2 | 44.0485 | 44.1920 | 0.996753× |
| 4 | 58.3690 | 58.3525 | 1.000283× |
| 8 | 70.7520 | 70.6085 | 1.002032× |
| 16 | 81.7130 | 81.7130 | 1.000000× |
| 32 | 113.1375 | 113.0250 | 1.000995× |
| 64 | 149.6980 | 149.7775 | 0.999469× |
| 128 | 151.8095 | 151.7935 | 1.000105× |
| 256 | 159.6970 | 159.6495 | 1.000298× |
| 512 | 164.4815 | 164.3535 | 1.000779× |
| 1024 | 181.3775 | 181.2495 | 1.000706× |
| 2048 | 222.0660 | 222.1295 | 0.999714× |
| 4096 | 325.9070 | 325.4750 | 1.001327× |
| 8192 | 625.4940 | 643.4625 | 0.972075× |

Tokens 8–8192: 0.997920× geometric speedup; +0.208398% latency; 7/11 lower. Tokens 1/2/4 are reported and excluded from retention.

One whole run per arm, no row selection or statistical-significance claim. Normal autotuning may select different tactics; individual timing differences may be noise.
