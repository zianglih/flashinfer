# Retention: payload-publication Q1

Unpromoted. The independent complete-file/raw-output audit passed. Q1 improves over its metadata-first P1 parent but remains slower than fresh same-node retained d01/A1: decode T4–512 speedup **0.974915998× versus A1**, **1.026313676× versus P1**. Both comparisons use unchanged full13/100/O3/AUTO4 and require all104 finite bit-exact cross-arm outputs.

| Tokens | A1 d01 (µs) | P1 3cd (µs) | Q1 44b5 (µs) | A1/Q1 | P1/Q1 |
|---:|---:|---:|---:|---:|---:|
| 1 | 65.6805 | 75.8880 | 71.0560 | 0.924348 | 1.068003 |
| 2 | 84.7690 | 92.0965 | 87.3445 | 0.970513 | 1.054405 |
| 4 | 94.7040 | 103.0725 | 98.3050 | 0.963369 | 1.048497 |
| 8 | 120.8970 | 123.5205 | 115.8570 | 1.043502 | 1.066146 |
| 16 | 134.5290 | 142.3690 | 139.6650 | 0.963226 | 1.019361 |
| 32 | 159.7930 | 166.8495 | 164.3210 | 0.972444 | 1.015388 |
| 64 | 182.9625 | 191.0895 | 188.6415 | 0.969895 | 1.012977 |
| 128 | 184.9770 | 198.2255 | 195.9545 | 0.943979 | 1.011589 |
| 256 | 191.0255 | 200.1460 | 196.3055 | 0.973103 | 1.019564 |
| 512 | 195.5375 | 204.6900 | 201.0100 | 0.972775 | 1.018308 |
| 4096 | 464.0205 | 474.1160 | 475.8130 | 0.975216 | 0.996433 |
| 8192 | 797.7025 | 810.8860 | 813.3015 | 0.980820 | 0.997030 |
| 16384 | 1530.8020 | 1539.4850 | 1547.2475 | 0.989371 | 0.994983 |

All13 selected tactics are identical in each comparison. T1/T2 remain visible but are excluded from decodeGM;4096/8192/16384 are separate prefill guards. These serial runs do not cancel drift. The result does not establish whether earlier scheduler release caused useful weight/decode overlap.

| Tokens | A1 quarter medians (µs) | Q1 quarter medians (µs) | A1/Q1 MAD (µs) |
|---:|---|---|---|
| 1 | 65.664, 65.793, 65.249, 65.824 | 71.072, 70.592, 70.944, 71.168 | 0.736 / 0.752 |
| 2 | 85.185, 85.089, 84.257, 84.096 | 87.105, 87.265, 88.129, 87.328 | 1.023 / 1.648 |
| 4 | 94.720, 94.849, 94.273, 94.849 | 98.752, 98.272, 98.881, 97.729 | 0.655 / 1.343 |
| 8 | 120.897, 120.897, 121.057, 120.673 | 116.449, 115.873, 115.425, 115.585 | 1.008 / 0.960 |
| 16 | 135.009, 134.529, 134.433, 134.401 | 139.426, 139.809, 139.777, 139.649 | 0.960 / 0.944 |
| 32 | 159.906, 160.161, 159.650, 159.297 | 164.705, 164.225, 164.193, 164.418 | 0.688 / 0.912 |
| 64 | 183.362, 182.626, 182.979, 182.947 | 189.474, 188.865, 187.714, 188.450 | 0.704 / 0.992 |
| 128 | 185.249, 185.537, 184.544, 184.673 | 196.034, 195.489, 195.457, 196.194 | 0.832 / 0.816 |
| 256 | 191.394, 190.594, 190.818, 191.201 | 196.577, 196.002, 196.289, 196.354 | 0.720 / 0.881 |
| 512 | 195.458, 194.817, 196.322, 195.490 | 201.666, 200.161, 201.122, 201.058 | 0.991 / 1.007 |
| 4096 | 463.235, 463.044, 464.388, 465.059 | 475.366, 473.190, 474.885, 481.509 | 2.753 / 3.968 |
| 8192 | 771.174, 769.638, 818.662, 833.830 | 774.374, 777.062, 816.551, 840.775 | 26.097 / 32.081 |
| 16384 | 1372.752, 1481.041, 1551.506, 1565.970 | 1380.624, 1495.084, 1573.105, 1577.649 | 49.969 / 41.008 |

Evidence: `decode13-benchmark-hu59/independent-file-timing-audit.json`. All170 original member files were reconstructed and rehashed (162 transferred plus8 exact content-cache output files), with current source/runtime/closure, audited A1 and P1 bindings, and recomputed primary/incremental comparisons. **Original gzip bytes were not locally verified.** The remote sealed archive is670bd6e7140f6455fecf4c00981d8b030eee8930655e15b72ad35370a175cb74. No qualification or promotion follows this negative retained-control result.
