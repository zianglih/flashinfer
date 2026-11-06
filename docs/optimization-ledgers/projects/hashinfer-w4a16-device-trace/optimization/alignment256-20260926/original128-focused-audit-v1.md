# Focused original128 A/C/D audit

PASS; six serial fresh sweeps in A1/C1/D1/D2/C2/A2 order.

Counts: `{"cold_rank_max_samples": 2400, "cold_rows": 24, "cross_arm_rank_shape_keys": 16, "finite_repeat_output_rank_records": 96, "hot_rank_samples": 7680, "independent_reference_rank_records": 24, "pooled_samples_per_arm_per_shape": 200, "trials": 6, "winner_rank_exports": 96}`.

| Global T | A original µs | C all96 µs | D all96+late µs | A/C | A/D | C/D |
|---:|---:|---:|---:|---:|---:|---:|
| 128 | 282.738000 | 286.690500 | 291.026500 | 0.986213 | 0.971520 | 0.985101 |
| 4096 | 594.918000 | 597.301000 | 597.734000 | 0.996010 | 0.995289 | 0.999276 |
| 8192 | 1139.673000 | 1151.675000 | 1155.994000 | 0.989579 | 0.985881 | 0.996264 |
| 16384 | 2357.044000 | 2380.516000 | 2374.242000 | 0.990140 | 0.992756 | 1.002643 |

## A_over_C: A1 / C1 / C2 / A2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 0.984056 | 0.997043 | 0.987565 | 0.974702 |
| 4096 | 0.992629 | 1.001153 | 1.004006 | 0.995458 |
| 8192 | 0.991638 | 0.988452 | 0.993637 | 0.996839 |
| 16384 | 0.992546 | 0.986645 | 0.996075 | 1.002032 |

## A_over_D: A1 / D1 / D2 / A2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 0.995910 | 0.955422 | 0.987565 | 1.029415 |
| 4096 | 0.992683 | 1.001313 | 1.004006 | 0.995353 |
| 8192 | 0.987953 | 0.985848 | 0.993637 | 0.995759 |
| 16384 | 0.994145 | 0.990390 | 0.996075 | 0.999851 |

## C_over_D: C1 / D1 / D2 / C2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 1.012046 | 0.958256 | 0.974702 | 1.029415 |
| 4096 | 1.000054 | 1.000159 | 0.995458 | 0.995353 |
| 8192 | 0.996284 | 0.997365 | 0.996839 | 0.995759 |
| 16384 | 1.001611 | 1.003796 | 1.002032 | 0.999851 |

Focused uniform EP4 H6144/I2048/E256/top8 at128/4096/8192/16384 global tokens only; no full native EP4/EP8 retention claim.
All sources retain the original128-bit combine. C changes the register allocation to all96; D also moves retirement later.
Every sweep is a fresh process with an independent eight-candidate AUTO search and fresh caches. Pooled200 samples per source/shape are untrimmed cold-L2 CUDA-graph CUPTI per-iteration rank maxima.
The original six-phase sequence is preserved. Common four-run comparison aliases are explicitly mapped to actual phases; intervening runs do not change the source sample pools.
Independent reference is checked at T128 only. Every measured shape has finite/repeated output checks and identical source/route/weight/output hashes across all six sweeps.
Earlier wide-B measurements, incomplete campaigns, and their baselines are excluded. AUTO tactic differences and drift remain visible.
