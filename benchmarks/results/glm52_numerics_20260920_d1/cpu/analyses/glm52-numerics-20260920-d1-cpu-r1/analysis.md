# Independent CPU replay of d1 captured numerics

No GPU work or benchmark timing was performed. Original strict tolerance remains atol=rtol=.01. Input payload hashes are checked before and after analysis.

| N | Input/route checks | FC2 terms equal | Mega FMA replay | Split partial replay | Original strict failures |
|---:|---|---:|---|---|---:|
| 1 | True | True (49152 terms) | True | True | 0 / 6144 |

## N=1

Entire-row candidate BF16 sum trees reproducing actual collective output:

```json
{
  "0": [
    "(0+((1+2)+3))"
  ]
}
```

| 3 | True | True (147456 terms) | True | True | 2 / 18432 |

## N=3

Entire-row candidate BF16 sum trees reproducing actual collective output:

```json
{
  "0": [
    "(0+((1+2)+3))"
  ],
  "1": [
    "((0+(2+3))+1)"
  ],
  "2": [
    "(((0+3)+1)+2)"
  ]
}
```

### Token 2, hidden 295

```json
{
  "global_token": 2,
  "source_rank": 2,
  "hidden": 295,
  "mega_actual": 0.62890625,
  "split_actual": 0.609375,
  "absolute_error": 0.01953125,
  "fixed_threshold": 0.016093749552965164,
  "error_over_threshold": 1.213592290878296,
  "expert_ids": [
    152,
    28,
    22,
    165,
    119,
    223,
    11,
    43
  ],
  "expert_owner_ranks": [
    2,
    0,
    0,
    2,
    1,
    3,
    0,
    0
  ],
  "fp32_route_weights": [
    0.334473192691803,
    0.32887136936187744,
    0.3028431832790375,
    0.3071669042110443,
    0.31060823798179626,
    0.3129969537258148,
    0.3016016483306885,
    0.30143874883651733
  ],
  "shared_bf16_route_fc2": [
    -1.3125,
    0.390625,
    -0.318359375,
    -3.1875,
    -0.78515625,
    3.84375,
    2.9375,
    0.55859375
  ],
  "weighted_route_terms_fp64": [
    -0.4389960654079914,
    0.12846537865698338,
    -0.09641296655172482,
    -0.9790945071727037,
    -0.24387599935289472,
    1.2030820408836007,
    0.8859548419713974,
    0.16838180110789835
  ],
  "mega_fma32_sum": 0.6275045275688171,
  "mega_replayed_bf16": 0.62890625,
  "owner_partial_fma32": [
    1.0863890647888184,
    -0.24387599527835846,
    -1.418090581893921,
    1.2030820846557617
  ],
  "owner_partial_actual_bf16": [
    1.0859375,
    -0.244140625,
    -1.421875,
    1.203125
  ],
  "weighted_all_route_sum_fp64": 0.6275045241345651,
  "sum_actual_owner_bf16_partials_fp64": 0.623046875,
  "owner_partial_rounding_shift": -0.004457649134565145,
  "collective_final_shift": -0.013671875,
  "full_fp64_sum_cast_once_bf16": 0.62890625,
  "rounded_partials_sum_cast_once_bf16": 0.625,
  "bf16_tree_candidates_at_element": {
    "(0+(1+(2+3)))": 0.625,
    "(0+((1+2)+3))": 0.625,
    "(0+((1+3)+2))": 0.625,
    "((0+1)+(2+3))": 0.625,
    "((0+2)+(1+3))": 0.625,
    "((0+3)+(1+2))": 0.6171875,
    "((0+(1+2))+3)": 0.625,
    "(((0+1)+2)+3)": 0.625,
    "(((0+2)+1)+3)": 0.625,
    "((0+(1+3))+2)": 0.625,
    "(((0+1)+3)+2)": 0.625,
    "(((0+3)+1)+2)": 0.609375,
    "((0+(2+3))+1)": 0.625,
    "(((0+2)+3)+1)": 0.625,
    "(((0+3)+2)+1)": 0.6171875
  },
  "matching_bf16_tree_candidates_at_element": [
    "(((0+3)+1)+2)"
  ]
}
```

### Token 2, hidden 3363

```json
{
  "global_token": 2,
  "source_rank": 2,
  "hidden": 3363,
  "mega_actual": 0.76171875,
  "split_actual": 0.7421875,
  "absolute_error": 0.01953125,
  "fixed_threshold": 0.017421875149011612,
  "error_over_threshold": 1.121076226234436,
  "expert_ids": [
    152,
    28,
    22,
    165,
    119,
    223,
    11,
    43
  ],
  "expert_owner_ranks": [
    2,
    0,
    0,
    2,
    1,
    3,
    0,
    0
  ],
  "fp32_route_weights": [
    0.334473192691803,
    0.32887136936187744,
    0.3028431832790375,
    0.3071669042110443,
    0.31060823798179626,
    0.3129969537258148,
    0.3016016483306885,
    0.30143874883651733
  ],
  "shared_bf16_route_fc2": [
    -1.625,
    3.984375,
    -1.765625,
    -3.84375,
    1.03125,
    3.171875,
    1.1171875,
    0.197265625
  ],
  "weighted_route_terms_fp64": [
    -0.5435189381241798,
    1.3103468623012304,
    -0.5347074954770505,
    -1.1806727880612016,
    0.3203147454187274,
    0.9927872125990689,
    0.33694559149444103,
    0.059463503188453615
  ],
  "mega_fma32_sum": 0.7609586119651794,
  "mega_replayed_bf16": 0.76171875,
  "owner_partial_fma32": [
    1.1720484495162964,
    0.3203147351741791,
    -1.7241917848587036,
    0.99278724193573
  ],
  "owner_partial_actual_bf16": [
    1.171875,
    0.3203125,
    -1.7265625,
    0.9921875
  ],
  "weighted_all_route_sum_fp64": 0.7609586933394894,
  "sum_actual_owner_bf16_partials_fp64": 0.7578125,
  "owner_partial_rounding_shift": -0.0031461933394894004,
  "collective_final_shift": -0.015625,
  "full_fp64_sum_cast_once_bf16": 0.76171875,
  "rounded_partials_sum_cast_once_bf16": 0.7578125,
  "bf16_tree_candidates_at_element": {
    "(0+(1+(2+3)))": 0.7578125,
    "(0+((1+2)+3))": 0.7578125,
    "(0+((1+3)+2))": 0.7578125,
    "((0+1)+(2+3))": 0.7578125,
    "((0+2)+(1+3))": 0.7578125,
    "((0+3)+(1+2))": 0.75,
    "((0+(1+2))+3)": 0.7578125,
    "(((0+1)+2)+3)": 0.7578125,
    "(((0+2)+1)+3)": 0.7578125,
    "((0+(1+3))+2)": 0.7578125,
    "(((0+1)+3)+2)": 0.7578125,
    "(((0+3)+1)+2)": 0.7421875,
    "((0+(2+3))+1)": 0.7578125,
    "(((0+2)+3)+1)": 0.7578125,
    "(((0+3)+2)+1)": 0.75
  },
  "matching_bf16_tree_candidates_at_element": [
    "(((0+3)+1)+2)"
  ]
}
```

## Interpretation boundary

Per-route FC2/input/route bit equality localizes an observed final-output discrepancy to post-FC2 reduction for these captured executions. Bit-exact CPU FMA replay is checked against the saved GPU outputs and partials; it is not a universal GPU arithmetic guarantee. Intermediate BF16 rank-partial rounding and collective reduction are reported separately. The NCCL order was not logged, so candidate trees are arithmetic explanations rather than an identified transport algorithm.

[Full checks, comparisons, exact violating values and input hashes](analysis.json)
