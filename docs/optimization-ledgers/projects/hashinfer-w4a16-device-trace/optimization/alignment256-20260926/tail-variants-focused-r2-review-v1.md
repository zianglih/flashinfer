# R2 focused results: repeat drift and AUTO winners

Completed A1/B1/C1/D1/D2/C2/B2/A2 on hu-pdx-43. Arithmetic independently recomputed from the audited raw samples; no source-node mixing.

| Global T | A1 µs | B1 µs | C1 µs | D1 µs | D2 µs | C2 µs | B2 µs | A2 µs |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 282.866000 | 285.026000 | 277.042500 | 283.347500 | 285.843500 | 286.242000 | 282.963500 | 282.290000 |
| 4096 | 594.551000 | 594.134500 | 596.068500 | 596.982000 | 597.414000 | 594.470000 | 599.428000 | 592.548500 |
| 8192 | 1144.103000 | 1147.486500 | 1146.107000 | 1141.591500 | 1148.236500 | 1150.935500 | 1145.752500 | 1138.567000 |
| 16384 | 2345.745000 | 2348.382500 | 2367.837500 | 2361.709500 | 2372.561500 | 2360.764500 | 2360.258500 | 2346.154000 |

| Global T | A1 tactic | B1 tactic | C1 tactic | D1 tactic | D2 tactic | C2 tactic | B2 tactic | A2 tactic |
|---:|---|---|---|---|---|---|---|---|
| 128 | N64/G512/epi | N64/G1024/epi | N64/G1024/epi | N64/G1024/epi | N64/G512/epi | N64/G512/epi | N64/G512/epi | N64/G512/epi |
| 4096 | N128/G512/reuse-dispatch | N128/G512/reuse-dispatch | N128/G512/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G512/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch |
| 8192 | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch |
| 16384 | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G512/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G1024/reuse-dispatch | N128/G512/reuse-dispatch |

N is MMA tile N; G is group hint. epi/reuse-dispatch are the recorded token-back modes. Full knob dictionaries and catalog indices remain in the JSON.

| Global T | A1→A2 latency change | A repeat tactic changed |
|---:|---:|---|
| 128 | -0.204% | False |
| 4096 | -0.337% | True |
| 8192 | -0.484% | False |
| 16384 | +0.017% | True |

## A versus B: late-no-prefetch-candidate

| Global T | A pooled µs | Candidate pooled µs | Pooled A/candidate | First A1/candidate1 | Reverse A2/candidate2 | Candidate repeat latency change | Repeat tactic changed | Pair tactics match first/reverse |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 128 | 282.514000 | 283.938000 | 0.994985 | 0.992422 | 0.997620 | -0.724% | True | False/True |
| 4096 | 594.007000 | 596.388000 | 0.996008 | 1.000701 | 0.988523 | +0.891% | True | True/True |
| 8192 | 1141.351000 | 1146.776000 | 0.995269 | 0.997051 | 0.993729 | -0.151% | False | True/True |
| 16384 | 2346.006500 | 2352.493500 | 0.997243 | 0.998877 | 0.994024 | +0.506% | False | True/False |

## A versus C: late-participant96-candidate

| Global T | A pooled µs | Candidate pooled µs | Pooled A/candidate | First A1/candidate1 | Reverse A2/candidate2 | Candidate repeat latency change | Repeat tactic changed | Pair tactics match first/reverse |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 128 | 282.514000 | 283.234500 | 0.997456 | 1.021020 | 0.986194 | +3.321% | True | False/True |
| 4096 | 594.007000 | 595.269000 | 0.997880 | 0.997454 | 0.996768 | -0.268% | True | True/True |
| 8192 | 1141.351000 | 1148.570500 | 0.993714 | 0.998251 | 0.989254 | +0.421% | False | True/True |
| 16384 | 2346.006500 | 2364.445000 | 0.992202 | 0.990670 | 0.993811 | -0.299% | False | True/False |

## A versus D: score-only-candidate

| Global T | A pooled µs | Candidate pooled µs | Pooled A/candidate | First A1/candidate1 | Reverse A2/candidate2 | Candidate repeat latency change | Repeat tactic changed | Pair tactics match first/reverse |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 128 | 282.514000 | 284.307500 | 0.993692 | 0.998301 | 0.987568 | +0.881% | True | False/True |
| 4096 | 594.007000 | 597.189500 | 0.994671 | 0.995928 | 0.991856 | +0.072% | True | False/False |
| 8192 | 1141.351000 | 1143.385500 | 0.998221 | 1.002200 | 0.991579 | +0.582% | False | True/True |
| 16384 | 2346.006500 | 2368.071000 | 0.990683 | 0.993240 | 0.988870 | +0.459% | True | True/True |

Fresh R2 hu-pdx-43 uniform EP4 only. No original-node samples and no native EP4/EP8 broad retention claim.
AUTO tactic changes and repeat drift remain possible contributors. A pooled difference alone is not an isolated kernel-source causal effect. This review establishes no full-catalog spill coverage.
All samples are retained. There is no trimming, repeat selection, tactic filtering or adjustment for drift.
