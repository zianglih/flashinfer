# Width16 L1 retention

Unpromoted. The primary A2 comparison gives1.008089× decode4–512 geometric speedup, but only3/8 decode rows improve and all three prefill medians regress. T4 supplies the aggregate gain; removing T4 only as an explanatory diagnostic gives0.995829× for the other seven decode rows (the official aggregate remains all eight rows). Historical A1 gives1.003953×. Do not introduce a per-shape selector from this one serial arm.

| Tokens | A2 µs | L1 µs | A2/L1 | A2/L1 MAD µs | A1 µs | A1/L1 | Same A2 tactic |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 67.2640 | 67.2800 | 0.999762 | 1.0080/1.1035 | 66.6560 | 0.990725 | no |
| 2 | 86.4325 | 81.0565 | 1.066324 | 0.8800/0.9595 | 79.5685 | 0.981642 | yes |
| 4 | 97.6480 | 88.9125 | 1.098248 | 1.0080/0.9595 | 97.1200 | 1.092310 | yes |
| 8 | 121.1045 | 120.7370 | 1.003044 | 0.9285/1.1685 | 117.2655 | 0.971247 | yes |
| 16 | 133.9045 | 134.8480 | 0.993003 | 0.7845/0.8470 | 134.6410 | 0.998465 | yes |
| 32 | 160.9280 | 159.9530 | 1.006096 | 0.7185/0.8160 | 160.7360 | 1.004895 | yes |
| 64 | 181.5205 | 182.6410 | 0.993865 | 0.9280/0.7850 | 182.8005 | 1.000873 | yes |
| 128 | 188.7045 | 190.5290 | 0.990424 | 0.6565/0.6245 | 188.1450 | 0.987487 | yes |
| 256 | 191.9045 | 192.4800 | 0.997010 | 0.9765/0.7360 | 190.4660 | 0.989537 | yes |
| 512 | 195.7290 | 198.2080 | 0.987493 | 1.0560/1.0395 | 196.4970 | 0.991368 | yes |
| 4096 | 464.6090 | 466.7710 | 0.995368 | 4.4160/3.1520 | 465.0895 | 0.996398 | yes |
| 8192 | 777.6180 | 786.0525 | 0.989270 | 16.2400/24.3685 | 759.9215 | 0.966757 | yes |
| 16384 | 1489.1595 | 1500.0135 | 0.992764 | 63.6295/66.7520 | 1497.7690 | 0.998504 | yes |

T4 is a measured same-tactic improvement, not an AUTO tactic switch: all8 ranks in both arms select MMA[256,64,256], cluster[2,1,1], epi_warps return, external deterministic combine. Median97.6480→88.9125µs, or8.9459% lower latency, versus MAD1.0080/0.9595µs. Chronological25-sample quarter medians remain clearly separated: A2[97.568,98.304,97.312,97.632]µs; L1[89.120,88.801,88.897,88.736]µs. This supports that the observed T4 separation is not driven by one outlier, while serial-arm environmental drift remains uncancelled. Twelve of13 rows select the same tactics; T1 differs and is excluded from retention.

Prefill quarter medians (µs), with upward within-arm drift retained:

| Tokens | A2 quarters | L1 quarters |
|---:|---|---|
| 4096 | 463.362, 461.953, 509.697, 464.577 | 465.442, 465.795, 468.579, 467.747 |
| 8192 | 762.659, 761.538, 780.258, 812.194 | 765.700, 769.765, 815.045, 826.628 |
| 16384 | 1346.664, 1461.925, 1526.308, 1561.540 | 1369.164, 1478.217, 1563.789, 1566.638 |

CPU full-file audit PASS, executed once with the project timing-audit interpreter. All1300 raw samples/arm retained;104 finite repeat-exact outputs in each arm and104 cross-version bit-exact comparisons against each A2 and historical A1. The unchanged comparison methods reproduce both sealed comparisons. Source104, source-review/runtime/helper pins, current source benchmarka82f versus executed304a, same hu15 boot/environment, predecessor stop and post-run source/process/GPU closure are bound. Exact59 original members were reconstructed from51 verified compact members plus8 SHA-identical audited A1 files; original gzip bytes were not downloaded/locally verified.

Audit: `decode13-benchmark/independent-file-timing-audit.json`, SHA`a44929ec021a957cc23cc04b431dc1af1199b01607e1a9eb68ae305878786f36`. Original seal archive`cc6ec77c69addb53c137bcec37d0c1680844a37dfa45f8ce2a832c2622fdda52`; compact bundle`cdbc3ade761dde8822fe969e84104d8493b8cf528f92cd425550a978eca5328c`.

Source d9d510f is isolated from retained3de and other trials. No fresh codegen establishes why T4 differs; wider workers reduce score/address overhead but also reduce CTA coverage and alter memory instruction coalescing/register scheduling. These are hypotheses, not measured causes. No sanitizer or additional GPU work requested. The general implementation does not show broad enough benefit to promote.
