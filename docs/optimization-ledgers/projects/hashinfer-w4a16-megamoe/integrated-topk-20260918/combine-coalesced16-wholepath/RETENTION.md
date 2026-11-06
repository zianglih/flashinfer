# N1 coalesced width16 — unconfirmed, repeat pending

Complete-file audit PASS: `decode13-benchmark/independent-file-timing-audit.json` SHA256 `5fb9e4104b514ee4b25ec4059a8318c72412fbba60daca8d0183be00e962243a`. All 59 original sealed members are verified: 51 compact-bundle files plus 8 exact SHA-identical A1 serialized outputs. All 1300 raw samples per arm and 104 finite/repeat-exact outputs pass. Cross-arm 104 exact outputs pass independently against primary A3, historical A1, and adjacent-width16 L2. The original gzip is **not locally verified**; the complete member files are verified by the original seal hashes. Source, setup, boot, immutable controls and process/GPU closure are checked.

Executed source is `21f598d8db88df87302e96e233599eab2f6db048`, on the same hu15 / 8 B300 boot as the controls. Method stays EP8/H7168/I2048/E256/K8, O3/AUTO4, 3 warmups and 100 cold-L2 graph-CUPTI rank-MAX samples per case. Every one of the 13 selected tactics matches A3 and L2 on all eight ranks.

Decode T4–512 GM: A3/N1 **1.007560295×**, 6/8 wins; L2/N1 **1.007094073×**. Historical A1/N1 is **0.998530620×**. The separately derived A2/N1 GM is 1.002644823×. Serial comparisons do not cancel temporal drift.

| T | A1 µs | A2 µs | A3 µs | L1 µs | L2 µs | N1 µs | A3/N1 | L2/N1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 66.6560 | 67.2640 | 68.0640 | 67.2800 | 66.8000 | 68.4800 | 0.993925 | 0.975467 |
| 2 | 79.5685 | 86.4325 | 84.8330 | 81.0565 | 84.0000 | 87.4560 | 0.970008 | 0.960483 |
| 4 | 97.1200 | 97.6480 | 97.6650 | 88.9125 | 96.8165 | 98.3050 | 0.993490 | 0.984858 |
| 8 | 117.2655 | 121.1045 | 121.6165 | 120.7370 | 122.4170 | 118.8325 | 1.023428 | 1.030164 |
| 16 | 134.6410 | 133.9045 | 135.9210 | 134.8480 | 134.9445 | 133.3920 | 1.018959 | 1.011639 |
| 32 | 160.7360 | 160.9280 | 162.1290 | 159.9530 | 159.6970 | 161.7605 | 1.002278 | 0.987243 |
| 64 | 182.8005 | 181.5205 | 184.0335 | 182.6410 | 185.7925 | 184.1930 | 0.999134 | 1.008684 |
| 128 | 188.1450 | 188.7045 | 189.2325 | 190.5290 | 188.6410 | 187.5375 | 1.009038 | 1.005884 |
| 256 | 190.4660 | 191.9045 | 190.9920 | 192.4800 | 192.8645 | 189.0570 | 1.010235 | 1.020139 |
| 512 | 196.4970 | 195.7290 | 195.8410 | 198.2080 | 196.7535 | 195.0090 | 1.004266 | 1.008946 |
| 4096 | 465.0895 | 464.6090 | 460.7050 | 466.7710 | 462.5325 | 459.7610 | 1.002053 | 1.006028 |
| 8192 | 759.9215 | 777.6180 | 798.4855 | 786.0525 | 766.5295 | 786.7585 | 1.014905 | 0.974288 |
| 16384 | 1497.7690 | 1489.1595 | 1499.5880 | 1500.0135 | 1488.1030 | 1477.0970 | 1.015226 | 1.007451 |

MAD and consecutive 25-sample quarter medians are descriptive dispersion checks, not confidence intervals. The material decode changes are not isolated outliers: T8 and T16 N1 quarter medians sit below A3/L2, and T256 also improves in each quarter. T32 regresses against L2 in every quarter. T4 is slower than A3/L2; the original L1 T4 result already failed to reproduce in L2 despite identical source and tactics.

| T | A3 / N1 / L2 MAD µs | A3 quarter medians µs | N1 quarter medians µs | L2 quarter medians µs |
|---:|---|---|---|---|
| 4 | 0.7365 / 0.8315 / 1.1365 | 97.696, 97.569, 97.856, 97.665 | 98.529, 98.208, 97.952, 98.208 | 97.728, 96.384, 95.968, 96.928 |
| 8 | 0.8955 / 1.0880 / 0.9755 | 122.273, 121.312, 121.441, 121.697 | 118.849, 119.169, 118.656, 119.041 | 122.752, 122.976, 122.528, 121.152 |
| 16 | 0.9280 / 0.8475 / 0.7205 | 136.481, 135.425, 135.680, 136.320 | 134.464, 133.152, 133.057, 133.505 | 135.488, 135.009, 134.848, 134.784 |
| 32 | 0.7520 / 0.8640 / 0.7040 | 162.049, 162.241, 162.050, 162.145 | 161.569, 161.665, 162.304, 161.697 | 160.001, 159.937, 159.713, 159.137 |
| 64 | 0.7995 / 1.1840 / 0.8480 | 184.353, 183.521, 184.609, 183.713 | 184.257, 183.905, 184.544, 184.033 | 186.272, 185.633, 185.376, 185.952 |
| 128 | 0.8485 / 0.8000 / 0.7830 | 189.857, 189.153, 188.577, 189.249 | 187.841, 186.881, 187.426, 187.905 | 189.024, 188.417, 188.832, 188.288 |
| 256 | 0.7520 / 0.7050 / 0.7685 | 191.361, 191.105, 190.721, 190.913 | 189.601, 189.057, 188.833, 188.865 | 192.992, 192.512, 192.960, 192.864 |
| 512 | 1.2160 / 0.9440 / 0.9600 | 196.737, 195.457, 195.329, 195.936 | 195.650, 195.521, 194.657, 194.626 | 196.737, 196.898, 196.513, 197.344 |
| 8192 | 30.0335 / 28.5930 / 5.9815 | 764.003, 762.850, 810.499, 826.757 | 754.757, 754.405, 793.958, 819.495 | 763.682, 765.378, 761.794, 825.281 |
| 16384 | 80.8170 / 96.5095 / 39.5350 | 1357.764, 1483.333, 1558.404, 1587.460 | 1350.504, 1374.856, 1487.657, 1567.434 | 1358.405, 1464.995, 1498.089, 1530.150 |

N1 T8 remains inside the retained A1/A2/A3 range: 118.8325 µs versus 117.2655–121.6165 µs. T128, T256 and T512 fall below all three retained medians, but by only about 0.3–0.75% versus the fastest historical control. The aggregate A1–A3 variation exceeds N1’s 0.75% advantage over A3. These observations justify a same-source repeat; they do not establish a general retained improvement.

Prefill is mixed across controls. At 8K, N1 is 1.49% faster than A3 but 2.57% slower than L2, with large late-run shifts in all three distributions. At 16K, the N1 median is favorable, while the large MAD and increasing quarter medians prevent a stable causal inference. The 4K result is nearly flat. No instruction count, cache-sector or scheduling cause is claimed from timing alone.

Keep retained3de as the default pending the separately recorded N2 repeat. Preserve N1 and all earlier arms without averaging runs or selecting the favorable control. N2 has been authorized with identical source/cwd and corresponding CUDA/CuTe cache paths, fresh AUTO4 knob/output paths and unchanged timing helpers. `cute.compile` forces no-cache in installed CuTe4.7.1; no compiled-kernel hit or compilation savings are claimed. No sanitizer was run for this performance iteration.
