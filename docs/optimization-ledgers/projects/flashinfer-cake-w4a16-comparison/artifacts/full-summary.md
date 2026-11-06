# CAKE versus CuTe-DSL O2 dense W4A16 evidence

NVFP4 W4A16: BF16 activations/output, E2M1 weights, E4M3 block-16 scales, FP32 alpha.

Sweep finished: **True**. Valid workers: **115/115**. All scheduled evidence valid: **True**.

The sequence for each shape is A1 CuTe-DSL O2 → CAKE native → A2 CuTe-DSL O2 → CAKE tiled → A3 CuTe-DSL O2. Every entry is a separate fresh process. Native speedup is mean(A1 median, A2 median) / native median; tiled speedup is mean(A2 median, A3 median) / tiled median. A ratio above 1 means CAKE takes less measured GPU time. Latency reduction is 100 × (1 − 1 / speedup).

Timing uses CUPTI with CUDA graphs, cold L2, PDL enabled, preallocated output, and sleep after each run. It covers the GPU activity span from the first activity start to the last activity end. Weight preparation and autotuning are outside timing. Raw per-iteration milliseconds, correctness evidence, source fingerprints, environment metadata, and selected tactics remain in the linked worker JSON files.

## Coverage and geometric means

Historical 16 shapes, supplemental shapes, and smoke checks are reported separately. Small M (M≤32) is decode-like dense GEMM, not an end-to-end decode benchmark. Geometric means use only valid matched rows; a partial-coverage value describes that subset and cannot represent the full suite. The ±1% label is a descriptive noise band, not a statistical confidence interval.

| Suite | M group | CAKE backend | Valid / scheduled | Standard suite size | Geomean speedup | Label |
|---|---|---|---:|---:|---:|---|
| historical | all scheduled M | native | 16/16 | 16 | 0.095 | slower |
| historical | all scheduled M | tiled | 16/16 | 16 | 0.152 | slower |
| historical | small-M/decode-like (M<=32) | native | 6/6 | 16 | 0.287 | slower |
| historical | small-M/decode-like (M<=32) | tiled | 6/6 | 16 | 0.210 | slower |
| historical | larger-M (M>32) | native | 10/10 | 16 | 0.049 | slower |
| historical | larger-M (M>32) | tiled | 10/10 | 16 | 0.125 | slower |
| supplemental | all scheduled M | native | 7/7 | 7 | 0.443 | slower |
| supplemental | all scheduled M | tiled | 7/7 | 7 | 0.540 | slower |
| supplemental | small-M/decode-like (M<=32) | native | 5/5 | 7 | 0.667 | slower |
| supplemental | small-M/decode-like (M<=32) | tiled | 5/5 | 7 | 0.692 | slower |
| supplemental | larger-M (M>32) | native | 2/2 | 7 | 0.159 | slower |
| supplemental | larger-M (M>32) | tiled | 2/2 | 7 | 0.290 | slower |

## Historical raw worker medians and matched comparisons

All medians below are microseconds. Raw medians remain visible even when their evidence is invalid; only validated comparisons receive a speedup. Drift is signed change between the two bracketing CuTe medians. Span is max(A1,A2,A3) / min(A1,A2,A3) − 1.

| Case (M,N,K) | A1 µs | Native µs | A2 µs | Tiled µs | A3 µs | Native × | Native label | Native drift % | Tiled × | Tiled label | Tiled drift % | A span % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|
| down-m1 (1,6656,19968) | 37.137 | 116.417 | 37.232 | 160.690 | 37.152 | 0.319 | slower | 0.26 | 0.231 | slower | -0.21 | 0.26 |
| down-m8 (8,6656,19968) | 37.249 | 116.594 | 37.377 | 160.450 | 37.280 | 0.320 | slower | 0.34 | 0.233 | slower | -0.26 | 0.34 |
| down-m32 (32,6656,19968) | 37.408 | 159.425 | 37.072 | 160.721 | 37.200 | 0.234 | slower | -0.90 | 0.231 | slower | 0.35 | 0.91 |
| down-m128 (128,6656,19968) | 41.360 | 477.829 | 42.560 | 236.050 | 42.561 | 0.088 | slower | 2.90 | 0.180 | slower | 0.00 | 2.90 |
| down-m512 (512,6656,19968) | 100.257 | 1836.340 | 100.209 | 709.863 | 100.290 | 0.055 | slower | -0.05 | 0.141 | slower | 0.08 | 0.08 |
| down-m1024 (1024,6656,19968) | 149.730 | 3596.278 | 150.034 | 1416.895 | 149.922 | 0.042 | slower | 0.20 | 0.106 | slower | -0.07 | 0.20 |
| down-m2048 (2048,6656,19968) | 285.907 | 7089.673 | 286.467 | 2716.492 | 286.308 | 0.040 | slower | 0.20 | 0.105 | slower | -0.06 | 0.20 |
| down-m4096 (4096,6656,19968) | 569.062 | 14139.007 | 569.734 | 5313.862 | 568.998 | 0.040 | slower | 0.12 | 0.107 | slower | -0.13 | 0.13 |
| up-m1 (1,19968,6656) | 30.113 | 92.577 | 30.336 | 161.986 | 30.288 | 0.326 | slower | 0.74 | 0.187 | slower | -0.16 | 0.74 |
| up-m8 (8,19968,6656) | 31.024 | 92.657 | 30.752 | 162.001 | 30.880 | 0.333 | slower | -0.88 | 0.190 | slower | 0.42 | 0.88 |
| up-m32 (32,19968,6656) | 31.424 | 146.338 | 31.456 | 162.097 | 31.712 | 0.215 | slower | 0.10 | 0.195 | slower | 0.81 | 0.92 |
| up-m128 (128,19968,6656) | 40.641 | 484.197 | 40.145 | 200.818 | 40.224 | 0.083 | slower | -1.22 | 0.200 | slower | 0.20 | 1.24 |
| up-m512 (512,19968,6656) | 89.873 | 1824.835 | 87.601 | 677.463 | 89.905 | 0.049 | slower | -2.53 | 0.131 | slower | 2.63 | 2.63 |
| up-m1024 (1024,19968,6656) | 150.881 | 3630.645 | 150.945 | 1351.742 | 150.994 | 0.042 | slower | 0.04 | 0.112 | slower | 0.03 | 0.07 |
| up-m2048 (2048,19968,6656) | 277.987 | 7230.551 | 278.499 | 2700.074 | 278.115 | 0.038 | slower | 0.18 | 0.103 | slower | -0.14 | 0.18 |
| up-m4096 (4096,19968,6656) | 561.861 | 14436.302 | 562.149 | 5356.981 | 561.446 | 0.039 | slower | 0.05 | 0.105 | slower | -0.13 | 0.13 |

## Supplemental raw worker medians and matched comparisons

All medians below are microseconds. Raw medians remain visible even when their evidence is invalid; only validated comparisons receive a speedup. Drift is signed change between the two bracketing CuTe medians. Span is max(A1,A2,A3) / min(A1,A2,A3) − 1.

| Case (M,N,K) | A1 µs | Native µs | A2 µs | Tiled µs | A3 µs | Native × | Native label | Native drift % | Tiled × | Tiled label | Tiled drift % | A span % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|
| small-m1-n4096-k4096 (1,4096,4096) | 11.760 | 17.136 | 11.712 | 35.473 | 11.520 | 0.685 | slower | -0.41 | 0.327 | slower | -1.64 | 2.08 |
| small-m768-n2112-k2048 (768,2112,2048) | 11.265 | 40.512 | 11.440 | 32.897 | 11.424 | 0.280 | slower | 1.55 | 0.348 | slower | -0.14 | 1.55 |
| small-m7-n4160-k192 (7,4160,192) | 4.800 | 5.664 | 4.736 | 5.808 | 4.784 | 0.842 | slower | -1.33 | 0.820 | slower | 1.01 | 1.35 |
| small-m13-n11008-k128 (13,11008,128) | 4.992 | 6.272 | 4.960 | 6.240 | 5.008 | 0.793 | slower | -0.64 | 0.799 | slower | 0.97 | 0.97 |
| small-m17-n3072-k3072 (17,3072,3072) | 9.760 | 20.992 | 9.665 | 12.576 | 9.808 | 0.463 | slower | -0.98 | 0.774 | slower | 1.49 | 1.49 |
| small-m16-n1024-k1024 (16,1024,1024) | 5.824 | 9.344 | 5.824 | 5.984 | 5.648 | 0.623 | slower | 0.00 | 0.959 | slower | -3.02 | 3.12 |
| small-m256-n4096-k4096 (256,4096,4096) | 12.384 | 137.121 | 12.512 | 51.553 | 12.384 | 0.091 | slower | 1.04 | 0.241 | slower | -1.03 | 1.04 |

## Actual selected CuTe tactics and worker evidence

| Case | Worker | Status | Median µs | Selected CuTe tactic | Raw samples / provenance |
|---|---|---|---:|---|---|
| down-m1 | a1 | complete; valid | 37.137 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a1.log>) |
| down-m1 | native | complete; valid | 116.417 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/native.log>) |
| down-m1 | a2 | complete; valid | 37.232 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a2.log>) |
| down-m1 | tiled | complete; valid | 160.690 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/tiled.log>) |
| down-m1 | a3 | complete; valid | 37.152 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1/a3.log>) |
| down-m8 | a1 | complete; valid | 37.249 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a1.log>) |
| down-m8 | native | complete; valid | 116.594 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/native.log>) |
| down-m8 | a2 | complete; valid | 37.377 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a2.log>) |
| down-m8 | tiled | complete; valid | 160.450 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/tiled.log>) |
| down-m8 | a3 | complete; valid | 37.280 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m8/a3.log>) |
| down-m32 | a1 | complete; valid | 37.408 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a1.log>) |
| down-m32 | native | complete; valid | 159.425 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/native.log>) |
| down-m32 | a2 | complete; valid | 37.072 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a2.log>) |
| down-m32 | tiled | complete; valid | 160.721 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/tiled.log>) |
| down-m32 | a3 | complete; valid | 37.200 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m32/a3.log>) |
| down-m128 | a1 | complete; valid | 41.360 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a1.log>) |
| down-m128 | native | complete; valid | 477.829 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/native.log>) |
| down-m128 | a2 | complete; valid | 42.560 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a2.log>) |
| down-m128 | tiled | complete; valid | 236.050 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/tiled.log>) |
| down-m128 | a3 | complete; valid | 42.561 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m128/a3.log>) |
| down-m512 | a1 | complete; valid | 100.257 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a1.log>) |
| down-m512 | native | complete; valid | 1836.340 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/native.log>) |
| down-m512 | a2 | complete; valid | 100.209 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a2.log>) |
| down-m512 | tiled | complete; valid | 709.863 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/tiled.log>) |
| down-m512 | a3 | complete; valid | 100.290 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m512/a3.log>) |
| down-m1024 | a1 | complete; valid | 149.730 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a1.log>) |
| down-m1024 | native | complete; valid | 3596.278 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/native.log>) |
| down-m1024 | a2 | complete; valid | 150.034 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a2.log>) |
| down-m1024 | tiled | complete; valid | 1416.895 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/tiled.log>) |
| down-m1024 | a3 | complete; valid | 149.922 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m1024/a3.log>) |
| down-m2048 | a1 | complete; valid | 285.907 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a1.log>) |
| down-m2048 | native | complete; valid | 7089.673 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/native.log>) |
| down-m2048 | a2 | complete; valid | 286.467 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a2.log>) |
| down-m2048 | tiled | complete; valid | 2716.492 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/tiled.log>) |
| down-m2048 | a3 | complete; valid | 286.308 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m2048/a3.log>) |
| down-m4096 | a1 | complete; valid | 569.062 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a1.log>) |
| down-m4096 | native | complete; valid | 14139.007 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/native.log>) |
| down-m4096 | a2 | complete; valid | 569.734 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a2.log>) |
| down-m4096 | tiled | complete; valid | 5313.862 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/tiled.log>) |
| down-m4096 | a3 | complete; valid | 568.998 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,192,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/down-m4096/a3.log>) |
| up-m1 | a1 | complete; valid | 30.113 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a1.log>) |
| up-m1 | native | complete; valid | 92.577 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/native.log>) |
| up-m1 | a2 | complete; valid | 30.336 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a2.log>) |
| up-m1 | tiled | complete; valid | 161.986 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/tiled.log>) |
| up-m1 | a3 | complete; valid | 30.288 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1/a3.log>) |
| up-m8 | a1 | complete; valid | 31.024 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a1.log>) |
| up-m8 | native | complete; valid | 92.657 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/native.log>) |
| up-m8 | a2 | complete; valid | 30.752 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a2.log>) |
| up-m8 | tiled | complete; valid | 162.001 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/tiled.log>) |
| up-m8 | a3 | complete; valid | 30.880 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m8/a3.log>) |
| up-m32 | a1 | complete; valid | 31.424 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a1.log>) |
| up-m32 | native | complete; valid | 146.338 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/native.log>) |
| up-m32 | a2 | complete; valid | 31.456 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a2.log>) |
| up-m32 | tiled | complete; valid | 162.097 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/tiled.log>) |
| up-m32 | a3 | complete; valid | 31.712 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m32/a3.log>) |
| up-m128 | a1 | complete; valid | 40.641 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a1.log>) |
| up-m128 | native | complete; valid | 484.197 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/native.log>) |
| up-m128 | a2 | complete; valid | 40.145 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a2.log>) |
| up-m128 | tiled | complete; valid | 200.818 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/tiled.log>) |
| up-m128 | a3 | complete; valid | 40.224 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m128/a3.log>) |
| up-m512 | a1 | complete; valid | 89.873 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a1.log>) |
| up-m512 | native | complete; valid | 1824.835 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/native.log>) |
| up-m512 | a2 | complete; valid | 87.601 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a2.log>) |
| up-m512 | tiled | complete; valid | 677.463 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/tiled.log>) |
| up-m512 | a3 | complete; valid | 89.905 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m512/a3.log>) |
| up-m1024 | a1 | complete; valid | 150.881 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a1.log>) |
| up-m1024 | native | complete; valid | 3630.645 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/native.log>) |
| up-m1024 | a2 | complete; valid | 150.945 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a2.log>) |
| up-m1024 | tiled | complete; valid | 1351.742 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/tiled.log>) |
| up-m1024 | a3 | complete; valid | 150.994 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m1024/a3.log>) |
| up-m2048 | a1 | complete; valid | 277.987 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a1.log>) |
| up-m2048 | native | complete; valid | 7230.551 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/native.log>) |
| up-m2048 | a2 | complete; valid | 278.499 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a2.log>) |
| up-m2048 | tiled | complete; valid | 2700.074 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/tiled.log>) |
| up-m2048 | a3 | complete; valid | 278.115 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m2048/a3.log>) |
| up-m4096 | a1 | complete; valid | 561.861 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a1.log>) |
| up-m4096 | native | complete; valid | 14436.302 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/native.log>) |
| up-m4096 | a2 | complete; valid | 562.149 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a2.log>) |
| up-m4096 | tiled | complete; valid | 5356.981 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/tiled.log>) |
| up-m4096 | a3 | complete; valid | 561.446 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[256,128,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/up-m4096/a3.log>) |
| small-m1-n4096-k4096 | a1 | complete; valid | 11.760 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a1.log>) |
| small-m1-n4096-k4096 | native | complete; valid | 17.136 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/native.log>) |
| small-m1-n4096-k4096 | a2 | complete; valid | 11.712 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a2.log>) |
| small-m1-n4096-k4096 | tiled | complete; valid | 35.473 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/tiled.log>) |
| small-m1-n4096-k4096 | a3 | complete; valid | 11.520 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,32,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m1-n4096-k4096/a3.log>) |
| small-m768-n2112-k2048 | a1 | complete; valid | 11.265 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,128,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a1.log>) |
| small-m768-n2112-k2048 | native | complete; valid | 40.512 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/native.log>) |
| small-m768-n2112-k2048 | a2 | complete; valid | 11.440 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,128,256],[1,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a2.log>) |
| small-m768-n2112-k2048 | tiled | complete; valid | 32.897 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/tiled.log>) |
| small-m768-n2112-k2048 | a3 | complete; valid | 11.424 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,128,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m768-n2112-k2048/a3.log>) |
| small-m7-n4160-k192 | a1 | complete; valid | 4.800 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a1.log>) |
| small-m7-n4160-k192 | native | complete; valid | 5.664 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/native.log>) |
| small-m7-n4160-k192 | a2 | complete; valid | 4.736 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[1,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a2.log>) |
| small-m7-n4160-k192 | tiled | complete; valid | 5.808 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/tiled.log>) |
| small-m7-n4160-k192 | a3 | complete; valid | 4.784 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[1,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m7-n4160-k192/a3.log>) |
| small-m13-n11008-k128 | a1 | complete; valid | 4.992 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a1.log>) |
| small-m13-n11008-k128 | native | complete; valid | 6.272 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/native.log>) |
| small-m13-n11008-k128 | a2 | complete; valid | 4.960 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a2.log>) |
| small-m13-n11008-k128 | tiled | complete; valid | 6.240 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/tiled.log>) |
| small-m13-n11008-k128 | a3 | complete; valid | 5.008 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m13-n11008-k128/a3.log>) |
| small-m17-n3072-k3072 | a1 | complete; valid | 9.760 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a1.log>) |
| small-m17-n3072-k3072 | native | complete; valid | 20.992 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/native.log>) |
| small-m17-n3072-k3072 | a2 | complete; valid | 9.665 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a2.log>) |
| small-m17-n3072-k3072 | tiled | complete; valid | 12.576 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/tiled.log>) |
| small-m17-n3072-k3072 | a3 | complete; valid | 9.808 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m17-n3072-k3072/a3.log>) |
| small-m16-n1024-k1024 | a1 | complete; valid | 5.824 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a1.log>) |
| small-m16-n1024-k1024 | native | complete; valid | 9.344 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/native.log>) |
| small-m16-n1024-k1024 | a2 | complete; valid | 5.824 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,16,256],[1,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a2.log>) |
| small-m16-n1024-k1024 | tiled | complete; valid | 5.984 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/tiled.log>) |
| small-m16-n1024-k1024 | a3 | complete; valid | 5.648 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,8,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m16-n1024-k1024/a3.log>) |
| small-m256-n4096-k4096 | a1 | complete; valid | 12.384 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[2,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a1.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a1.log>) |
| small-m256-n4096-k4096 | native | complete; valid | 137.121 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/native.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/native.log>) |
| small-m256-n4096-k4096 | a2 | complete; valid | 12.512 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[1,1],false]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a2.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a2.log>) |
| small-m256-n4096-k4096 | tiled | complete; valid | 51.553 | — | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/tiled.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/tiled.log>) |
| small-m256-n4096-k4096 | a3 | complete; valid | 12.384 | {"custom_op":"bf16_fp4_cute_dsl_sm100_gemm","runner":"CuteDslSm100Bf16Fp4Runner","tactic":[[128,64,256],[1,1],true]} | [JSON](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a3.json>) / [log](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/small-m256-n4096-k4096/a3.log>) |

## Failures, unsupported cells, and integrity checks

All scheduled workers and matched comparison contracts passed reducer validation.

A failed or unsupported backend cell is retained in coverage and receives no speedup. No unsupported status is inferred from an exception: the worker's recorded error is the evidence. A canonical input mismatch blocks both comparisons for that shape. Any sweep-wide source, host/GPU/package, worker-code, or timing mismatch blocks all speedup aggregation. Timing uncertainty and baseline drift are not corrected away.

## Recorded environment and source

Source provenance uses the supplied local manifest: its exact base commit, the verified local patch SHA256, and a required equality check between every critical worker source hash and the manifest. Remote Git metadata may be absent because the devbox received a source snapshot. This does not fabricate a remote commit or remote Git diff.

```json
{
  "baseline": "current main with #4686 30 tactics, CuTe opt-level2, fresh production autotune",
  "cake": "source-identical #5138 backends; native CUDA nvcc -O3 unchanged",
  "commit": "e500442f83fe9aac7969eb1c8731b6921fa6f180",
  "image": "nvcr.io/nvidia/pytorch:26.05-py3",
  "image_selection_note": "26.05 newest CUDA13.2 container; 26.06 and 26.07 use13.3,26.08 uses13.4",
  "image_selection_source": "https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html",
  "manifest_file": "/Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/source-manifest.json",
  "manifest_file_sha256": "02ddfd791a45c8c674f39e23998be68b087b266f4f474636bc7b7f624ce33e23",
  "orchestrator_sha256": "7e84da359e20fefbc3502cd332f6dea54a6a6bce4e4594d8d9ba2ce72bff3c22",
  "patch": "cute-o2.patch",
  "patch_sha256": "5eaf3115f87e466cc978551d36ff90a63df679676dc01c3d6336b12ff5be9d60",
  "provenance_route": "local base commit and patch manifest -> exact critical-source hash match in every worker; remote Git metadata may be absent",
  "remote_git_metadata": "h sync excludes .git; worker source file hashes are checked against this local commit-plus-patch manifest",
  "source_sha256": {
    "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_binding.cu": "f9b2479c831c9bbb12f0b7460bc17acd4a69c742faabc284f00e104d95e7979d",
    "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm100.cu": "bb86ff8230d25b743d4ae3787f86bd7cdb83c3495ed123b2e2c24421cbae9c38",
    "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu": "a4a24f87813b6d77525841032e8543531f55147b30747510d5d850152f681ad0",
    "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_kernel_specs.h": "09eb2bae420d81bbc688dcc3dad3c85e99277aab9c3f71810041ffc73a43945d",
    "flashinfer/autotuner/autotuner.py": "b637b91e762a1deadf7fc8202f944f5633797504a4d73e693e54987702b452d0",
    "flashinfer/gemm/gemm_bf16_fp4.py": "e113cdd93817d6553a4ec8a0ccb0728bf061f06e0ec25cf810c5803e0c0339fb",
    "flashinfer/gemm/gemm_bf16_fp4_blackwell.py": "b5a0d8ef74895d7f790b533dd858f6aff9dfb0d4e9b3013a204bbe73fc3bbb8e",
    "flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py": "b230998afe8795f0fa2b7f535b20ed62718b58dba10f7c6d3bd5f68a04eaa9e7",
    "flashinfer/gemm/kernels/cute_dsl/dense_gemm_bf16_fp4_sm100.py": "d286ba16c3007139c5d3526d066cec452b4933f74f26d723f19dceb06e496a30",
    "flashinfer/jit/blackwell_bf16_fp4.py": "2a411784d099bda74ccb647fc60f4c6f1c9711a6e966679c2bff5815b8ab8dd8",
    "flashinfer/testing/utils.py": "3a7515a237a3c6531ffa15829a5d46e3d399b3c23f7d3dba853f9e6be46da490"
  },
  "verified_patch_file": "/Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/cute-o2.patch",
  "worker_sha256": "db802a875455d6ee762a323856c53147b5f10e37a9f93525582bfa964c80804e"
}
```

The first completed worker's metadata is shown below; identity-group mismatches, if any, are listed above and in the machine-readable summary. The full package list is preserved in each raw worker JSON.

```json
{
  "environment": {
    "allow_tf32": false,
    "compute_capability": [
      10,
      3
    ],
    "container_image": "nvcr.io/nvidia/pytorch:26.05-py3",
    "cuda_bindings": "13.2.0",
    "cuda_visible_devices": "0",
    "cupti_preflight_timestamp": 1789343255390201235,
    "cupti_python": "13.2.0",
    "cutlass_dsl": "4.7.0",
    "flashinfer_file": "/hai-workspace/flashinfer-cake-w4a16-comparison/flashinfer/flashinfer/__init__.py",
    "flashinfer_version": "0.7.0",
    "float32_matmul_precision": "highest",
    "gpu_name": "NVIDIA B300 SXM6 AC",
    "gpu_total_memory_bytes": 287431131136,
    "hostname": "hu-pdx-10",
    "l2_cache_bytes": 132644864,
    "multiprocessor_count": 148,
    "nvcc_version": "nvcc: NVIDIA (R) Cuda compiler driver\nCopyright (c) 2005-2026 NVIDIA Corporation\nBuilt on Thu_Mar_19_11:12:51_PM_PDT_2026\nCuda compilation tools, release 13.2, V13.2.78\nBuild cuda_13.2.r13.2/compiler.37668154_0",
    "nvidia_cuda_cupti": "13.2.86",
    "nvidia_smi": "0, NVIDIA B300 SXM6 AC, GPU-35bac470-aab6-9e0d-e54b-5d3842d60401, 590.48.01, 1100.00, 2032\n1, NVIDIA B300 SXM6 AC, GPU-501333eb-6795-30bf-f198-b2e2a9ee26e3, 590.48.01, 1100.00, 2032\n2, NVIDIA B300 SXM6 AC, GPU-34278b34-a751-b4ba-49b8-8e8a70c84df1, 590.48.01, 1100.00, 2032\n3, NVIDIA B300 SXM6 AC, GPU-00a587e3-a492-0172-d870-a7db683fb027, 590.48.01, 1100.00, 2032\n4, NVIDIA B300 SXM6 AC, GPU-2df41b6e-e36a-1d25-a69f-dfbe61008e30, 590.48.01, 1100.00, 2032\n5, NVIDIA B300 SXM6 AC, GPU-9fb74b72-1da6-2f66-64b5-d230c6fafb3c, 590.48.01, 1100.00, 2032\n6, NVIDIA B300 SXM6 AC, GPU-7f37ccec-f6fc-07e6-71e1-ffd3e201f42d, 590.48.01, 1100.00, 2032\n7, NVIDIA B300 SXM6 AC, GPU-92f7dc53-4596-032e-225a-85b07484afc1, 590.48.01, 1100.00, 2032",
    "packages_sha256": "eae6bc9b6bf96d076d57f9d0b537661dc6518b98327815f99f6fa801f32735af",
    "python": "3.12.3",
    "python_executable": "/usr/bin/python",
    "repo": {
      "branch": null,
      "diff_sha256": null,
      "diff_stat": null,
      "revision": null,
      "status_short": null
    },
    "selected_environment": {
      "CUDA_CACHE_PATH": "/hai-workspace/flashinfer-cake-w4a16-comparison/results/compiled-cache-o2/cuda",
      "CUTE_DSL_CACHE_DIR": "/hai-workspace/flashinfer-cake-w4a16-comparison/results/compiled-cache-o2/cute",
      "CUTE_DSL_LIBS": "/usr/local/lib/python3.12/dist-packages/nvidia_cutlass_dsl/cu13/lib/libcute_dsl_runtime.so",
      "FLASHINFER_NVCC_THREADS": "4",
      "FLASHINFER_WORKSPACE_BASE": "/hai-workspace/flashinfer-cake-w4a16-comparison/results/compiled-cache-o2/flashinfer"
    },
    "torch": "2.12.0a0+5aff3928d8.nv26.05",
    "torch_cuda": "13.2"
  },
  "source": {
    "cute_sm100_compile_opt_level": 2,
    "cute_sm100_compile_options": [
      "--opt-level 2 --enable-tvm-ffi"
    ],
    "cute_sm100_o2_source_verified": true,
    "files_sha256": {
      "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_binding.cu": "f9b2479c831c9bbb12f0b7460bc17acd4a69c742faabc284f00e104d95e7979d",
      "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm100.cu": "bb86ff8230d25b743d4ae3787f86bd7cdb83c3495ed123b2e2c24421cbae9c38",
      "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu": "a4a24f87813b6d77525841032e8543531f55147b30747510d5d850152f681ad0",
      "csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_kernel_specs.h": "09eb2bae420d81bbc688dcc3dad3c85e99277aab9c3f71810041ffc73a43945d",
      "flashinfer/autotuner/autotuner.py": "b637b91e762a1deadf7fc8202f944f5633797504a4d73e693e54987702b452d0",
      "flashinfer/gemm/gemm_bf16_fp4.py": "e113cdd93817d6553a4ec8a0ccb0728bf061f06e0ec25cf810c5803e0c0339fb",
      "flashinfer/gemm/gemm_bf16_fp4_blackwell.py": "b5a0d8ef74895d7f790b533dd858f6aff9dfb0d4e9b3013a204bbe73fc3bbb8e",
      "flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py": "b230998afe8795f0fa2b7f535b20ed62718b58dba10f7c6d3bd5f68a04eaa9e7",
      "flashinfer/gemm/kernels/cute_dsl/dense_gemm_bf16_fp4_sm100.py": "d286ba16c3007139c5d3526d066cec452b4933f74f26d723f19dceb06e496a30",
      "flashinfer/jit/blackwell_bf16_fp4.py": "2a411784d099bda74ccb647fc60f4c6f1c9711a6e966679c2bff5815b8ab8dd8",
      "flashinfer/testing/utils.py": "3a7515a237a3c6531ffa15829a5d46e3d399b3c23f7d3dba853f9e6be46da490"
    },
    "manifest_sha256": "897c51d586bd6803d8ac8c9b7e80b584c75456ae5cbd01ca075104a88d602f9b",
    "repo": {
      "branch": null,
      "diff_sha256": null,
      "diff_stat": null,
      "revision": null,
      "status_short": null
    }
  },
  "timing": {
    "autotune_timed": false,
    "backend": "cupti",
    "cold_l2": true,
    "cuda_graph": true,
    "enable_pdl": true,
    "iters": 30,
    "l2_flush_multiple": 2,
    "metric": "last_GPU_activity_end_minus_first_GPU_activity_start",
    "preallocated_output": true,
    "sleep_after_run": true,
    "warmup": 5,
    "weight_preparation_timed": false
  },
  "worker_sha256": "db802a875455d6ee762a323856c53147b5f10e37a9f93525582bfa964c80804e"
}
```

## Scope and limitations

- Dense GEMM only; these results do not establish grouped-MoE or end-to-end serving speedups.
- Correctness uses the historical FP32 dequantization/accumulation reference, FP32 alpha before BF16 conversion, rtol=atol=0.015, finite-output checks, and bitwise eager/graph repeatability. Different backends need not be bitwise identical to each other.
- CuTe uses a fresh production autotune at the exact M bucket and verified O2 compilation. CAKE uses each explicit native/tiled production dispatch. Backend-specific weight preparation is excluded from timing.
- Three CuTe worker medians expose temporal baseline drift. A ±1% comparison label does not prove significance, and large drift may obscure small differences.
- Historical-suite results are fresh measurements of historical shapes, not historical timings presented as reruns.

[Sweep manifest](</Users/ziangli/playground/projects/flashinfer-cake-w4a16-comparison/artifacts/final/full/sweep.json>)
