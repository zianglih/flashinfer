# Wider-K FC1 screen: rejected

B = immutable 442d2aa53; A = internal K512, two operand stages for NVFP4 FC1. Fixed existing NB2/N128 or M256/N256 geometry. No production change.

Same GPU7 UUID on restored B200-83 environment; candidate native-cache epoch under cache/candidate-442. Actual DeepSeek routing, H7168/I2048, top-k8,32 local experts, seed42; no per-token activation, unfused finalizer. Each phase and full-chain measurement has 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Phase timings are diagnostic and not additive.

| Geometry | Tokens | FC1 B us | FC1 A us | FC1 slowdown | Full B us | Full A us | Full slowdown |
|:---|---:|---:|---:|---:|---:|---:|---:|
| M256/N256 | 16384 | 315.841 | 329.024 | 4.17% | 561.570 | 574.930 | 2.38% |
| NB2/N128 | 8192 | 152.384 | 165.569 | 8.65% | 302.145 | 315.041 | 4.27% |
| NB2/N128 | 16384 | 258.769 | 284.913 | 10.10% | 527.473 | 553.778 | 4.99% |

Summary uses medians of the three per-arm medians for each variant across both orders. Raw per-arm medians follow; all 100 samples for every measurement remain in results JSON. FC2 is byte-identical source and displays environmental/timing variation, not an implementation change.

| Geometry | Tokens | Order | Arm | FC1 us | FC2 us | Full us |
|:---|---:|:---|:---|---:|---:|---:|
| NB2/N128 | 8192 | forward | baseline | 152.513 | 91.105 | 301.889 |
| NB2/N128 | 8192 | forward | candidate | 165.360 | 91.232 | 315.088 |
| NB2/N128 | 8192 | forward | baseline | 151.441 | 91.200 | 302.145 |
| NB2/N128 | 16384 | forward | baseline | 258.144 | 158.720 | 533.441 |
| NB2/N128 | 16384 | forward | candidate | 284.097 | 149.569 | 553.778 |
| NB2/N128 | 16384 | forward | baseline | 259.361 | 151.025 | 526.322 |
| NB2/N128 | 8192 | reverse | candidate | 165.697 | 91.136 | 315.041 |
| NB2/N128 | 8192 | reverse | baseline | 152.384 | 91.200 | 302.209 |
| NB2/N128 | 8192 | reverse | candidate | 165.569 | 91.153 | 315.025 |
| NB2/N128 | 16384 | reverse | candidate | 284.913 | 150.192 | 556.689 |
| NB2/N128 | 16384 | reverse | baseline | 258.769 | 149.728 | 527.473 |
| NB2/N128 | 16384 | reverse | candidate | 285.473 | 152.672 | 549.505 |
| M256/N256 | 16384 | forward | baseline | 315.345 | 139.793 | 561.298 |
| M256/N256 | 16384 | forward | candidate | 329.585 | 133.697 | 574.386 |
| M256/N256 | 16384 | forward | baseline | 317.041 | 137.409 | 561.570 |
| M256/N256 | 16384 | reverse | candidate | 328.993 | 133.809 | 574.930 |
| M256/N256 | 16384 | reverse | baseline | 315.841 | 133.601 | 561.697 |
| M256/N256 | 16384 | reverse | candidate | 329.024 | 133.569 | 575.090 |

Validation: 72 compile-time SF layout cases, 3072 ownership cases, 24 paired NVFP4 byte-exact cases (K64/384/1280, per-token paths, M768 channel tails, protected96 N80/96/112). All 18 native arms matched final output bytes within their configuration. Full six-format and 264 boundary suites were prepared but intentionally deferred after this clear performance regression. No primary baseline/AUTO rerun or sanitizer run. GPU7 released.
