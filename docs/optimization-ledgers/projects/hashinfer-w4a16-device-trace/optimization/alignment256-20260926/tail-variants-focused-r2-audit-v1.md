# Focused tail and score variant audit

PASS; eight serial fresh sweeps in A1/B1/C1/D1/D2/C2/B2/A2 order.

Counts: `{"cold_rank_max_samples": 3200, "cold_rows": 32, "cross_arm_rank_shape_keys": 16, "finite_repeat_output_rank_records": 128, "hot_rank_samples": 10240, "independent_reference_rank_records": 32, "pooled_samples_per_arm_per_shape": 200, "trials": 8, "winner_rank_exports": 128}`.

- A: `before`, commit `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`.
- B: `late-no-prefetch-candidate`, commit `679aa752f9292d5cbfe4f129c076e347089b58f2`.
- C: `late-participant96-candidate`, commit `f8c97bb6eb9026ec6af87c825a5bd99c157a1d52`.
- D: `score-only-candidate`, commit `adadbd6b63fa43c4e5a305ccc08fa1f103ee15f6`.

| Global T | A original µs | B late/no-prefetch µs | C participant96 µs | D score-only µs | A/B | A/C | A/D |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 282.514000 | 283.938000 | 283.234500 | 284.307500 | 0.994985 | 0.997456 | 0.993692 |
| 4096 | 594.007000 | 596.388000 | 595.269000 | 597.189500 | 0.996008 | 0.997880 | 0.994671 |
| 8192 | 1141.351000 | 1146.776000 | 1148.570500 | 1143.385500 | 0.995269 | 0.993714 | 0.998221 |
| 16384 | 2346.006500 | 2352.493500 | 2364.445000 | 2368.071000 | 0.997243 | 0.992202 | 0.990683 |

## A_over_B: A1 / B1 / B2 / A2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 0.992422 | 0.997620 | 0.997964 | 0.992764 |
| 4096 | 1.000701 | 0.988523 | 0.996632 | 1.008910 |
| 8192 | 0.997051 | 0.993729 | 0.995161 | 0.998489 |
| 16384 | 0.998877 | 0.994024 | 1.000174 | 1.005057 |

## A_over_C: A1 / C1 / C2 / A2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 1.021020 | 0.986194 | 0.997964 | 1.033206 |
| 4096 | 0.997454 | 0.996768 | 0.996632 | 0.997318 |
| 8192 | 0.998251 | 0.989254 | 0.995161 | 1.004213 |
| 16384 | 0.990670 | 0.993811 | 1.000174 | 0.997013 |

## A_over_D: A1 / D1 / D2 / A2

| Global T | First ratio | Reverse ratio | Numerator repeat drift | Denominator repeat drift |
|---:|---:|---:|---:|---:|
| 128 | 0.998301 | 0.987568 | 0.997964 | 1.008809 |
| 4096 | 0.995928 | 0.991856 | 0.996632 | 1.000724 |
| 8192 | 1.002200 | 0.991579 | 0.995161 | 1.005821 |
| 16384 | 0.993240 | 0.988870 | 1.000174 | 1.004595 |

Focused uniform EP4 H6144/I2048/E256/top8 at128/4096/8192/16384 global tokens only; no full native EP4/EP8 retention claim.
A is the original retained baseline. B is late/no-prefetch wide payload; C is late/participant96 wide payload; D is score-only widening with the original128-bit payload. Exact source labels and identities are recorded, and none is a retained cumulative stack.
Every sweep is a fresh process with an independent eight-candidate AUTO search and fresh caches. Pooled200 samples per source/shape are untrimmed cold-L2 CUDA-graph CUPTI per-iteration rank maxima.
The original eight-phase A1/B1/C1/D1/D2/C2/B2/A2 sequence is preserved. Common four-run comparison aliases are explicitly mapped to actual phases; intervening runs do not change the source sample pools.
Independent reference is checked at T128 only. Every measured shape has finite/repeated output checks and matching input/route/weight/output hashes across all eight sweeps, with each source separately bound.
All earlier wide-B/original128/fixed diagnostics and their baseline samples are excluded; every sample is from this fresh campaign. AUTO tactic differences and drift remain visible.
