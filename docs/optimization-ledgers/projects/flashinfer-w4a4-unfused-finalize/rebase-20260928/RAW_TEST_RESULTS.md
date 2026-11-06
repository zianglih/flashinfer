### Complete C2 per-case test results

Source `bde427290b33c55489e39c75d7e2a25365358ca0`. All **155 pytest executions pass** (129 core, 15 prepared, 11 prepared-unfused); zero failures, errors, or skips. Tables retain every executed parameter ID. `(none)` denotes an unparameterized method; append `[ID]` to the exact method prefix otherwise. `—` means not selected in that suite, not a skipped test. Full logs/XML/reports are archived locally in `c2-evidence.tar.gz`; no external upload is implied.

#### Core native tests (`core.xml`, 129 cases)

`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy`

| Parameter ID | Status |
|---|---|
| swiglu-per-tensor | PASS |
| relu2-per-token | PASS |
| w4a16-swiglu | PASS |
| w4a16-relu2 | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles`

| Parameter ID | Status |
|---|---|
| w4a4-per-tensor | PASS |
| w4a4-per-token | PASS |
| w4a16-ordinary | PASS |
| w4a16-fused | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy`

| Parameter ID | Status |
|---|---|
| False-2-tail1-route8-1cta | PASS |
| False-2-tail1-route16-1cta | PASS |
| False-2-tail1-route32-mixed | PASS |
| False-2-tail1-route64-mixed | PASS |
| False-2-tail1-route128-2cta | PASS |
| False-2-tail1-route192 | PASS |
| False-2-tail-half-plus1-route8-1cta | PASS |
| False-2-tail-half-plus1-route16-1cta | PASS |
| False-2-tail-half-plus1-route32-mixed | PASS |
| False-2-tail-half-plus1-route64-mixed | PASS |
| False-2-tail-half-plus1-route128-2cta | PASS |
| False-2-tail-half-plus1-route192 | PASS |
| False-3-tail1-route8-1cta | PASS |
| False-3-tail1-route16-1cta | PASS |
| False-3-tail1-route32-mixed | PASS |
| False-3-tail1-route64-mixed | PASS |
| False-3-tail1-route128-2cta | PASS |
| False-3-tail1-route192 | PASS |
| False-3-tail-half-plus1-route8-1cta | PASS |
| False-3-tail-half-plus1-route16-1cta | PASS |
| False-3-tail-half-plus1-route32-mixed | PASS |
| False-3-tail-half-plus1-route64-mixed | PASS |
| False-3-tail-half-plus1-route128-2cta | PASS |
| False-3-tail-half-plus1-route192 | PASS |
| True-2-tail1-route8-1cta | PASS |
| True-2-tail1-route16-1cta | PASS |
| True-2-tail1-route32-mixed | PASS |
| True-2-tail1-route64-mixed | PASS |
| True-2-tail1-route128-2cta | PASS |
| True-2-tail1-route192 | PASS |
| True-2-tail-half-plus1-route8-1cta | PASS |
| True-2-tail-half-plus1-route16-1cta | PASS |
| True-2-tail-half-plus1-route32-mixed | PASS |
| True-2-tail-half-plus1-route64-mixed | PASS |
| True-2-tail-half-plus1-route128-2cta | PASS |
| True-2-tail-half-plus1-route192 | PASS |
| True-3-tail1-route8-1cta | PASS |
| True-3-tail1-route16-1cta | PASS |
| True-3-tail1-route32-mixed | PASS |
| True-3-tail1-route64-mixed | PASS |
| True-3-tail1-route128-2cta | PASS |
| True-3-tail1-route192 | PASS |
| True-3-tail-half-plus1-route8-1cta | PASS |
| True-3-tail-half-plus1-route16-1cta | PASS |
| True-3-tail-half-plus1-route32-mixed | PASS |
| True-3-tail-half-plus1-route64-mixed | PASS |
| True-3-tail-half-plus1-route128-2cta | PASS |
| True-3-tail-half-plus1-route192 | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph`

| Parameter ID | Status |
|---|---|
| 256-64-w4a4-per-tensor-False | PASS |
| 256-64-w4a4-per-tensor-True | PASS |
| 256-64-w4a4-per-token-False | PASS |
| 256-64-w4a4-per-token-True | PASS |
| 256-64-w4a16-False | PASS |
| 256-64-w4a16-True | PASS |
| 256-128-w4a4-per-tensor-False | PASS |
| 256-128-w4a4-per-tensor-True | PASS |
| 256-128-w4a4-per-token-False | PASS |
| 256-128-w4a4-per-token-True | PASS |
| 256-128-w4a16-False | PASS |
| 256-128-w4a16-True | PASS |
| 256-256-w4a4-per-tensor-False | PASS |
| 256-256-w4a4-per-tensor-True | PASS |
| 256-256-w4a4-per-token-False | PASS |
| 256-256-w4a4-per-token-True | PASS |
| 256-256-w4a16-False | PASS |
| 256-256-w4a16-True | PASS |
| 384-64-w4a4-per-tensor-False | PASS |
| 384-64-w4a4-per-tensor-True | PASS |
| 384-64-w4a4-per-token-False | PASS |
| 384-64-w4a4-per-token-True | PASS |
| 384-64-w4a16-False | PASS |
| 384-64-w4a16-True | PASS |
| 384-128-w4a4-per-tensor-False | PASS |
| 384-128-w4a4-per-tensor-True | PASS |
| 384-128-w4a4-per-token-False | PASS |
| 384-128-w4a4-per-token-True | PASS |
| 384-128-w4a16-False | PASS |
| 384-128-w4a16-True | PASS |
| 384-256-w4a4-per-tensor-False | PASS |
| 384-256-w4a4-per-tensor-True | PASS |
| 384-256-w4a4-per-token-False | PASS |
| 384-256-w4a4-per-token-True | PASS |
| 384-256-w4a16-False | PASS |
| 384-256-w4a16-True | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep`

| Parameter ID | Status |
|---|---|
| 8-w4a4-per-tensor-False | PASS |
| 8-w4a4-per-tensor-True | PASS |
| 8-w4a4-per-token-False | PASS |
| 8-w4a4-per-token-True | PASS |
| 8-w4a16-False | PASS |
| 8-w4a16-True | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail`

| Parameter ID | Status |
|---|---|
| 128-1-128 | PASS |
| 128-1-256 | PASS |
| 128-1-384 | PASS |
| 128-1-512 | PASS |
| 128-17-128 | PASS |
| 128-17-256 | PASS |
| 128-17-384 | PASS |
| 128-17-512 | PASS |
| 256-1-128 | PASS |
| 256-1-256 | PASS |
| 256-1-384 | PASS |
| 256-1-512 | PASS |
| 256-17-128 | PASS |
| 256-17-256 | PASS |
| 256-17-384 | PASS |
| 256-17-512 | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::test_w4a8_fused_moe_tactics_and_apis`

| Parameter ID | Status |
|---|---|
| n128-bias-off | PASS |
| n64-custom-bias | PASS |
| n192-2cta-oai | PASS |
| n128-2cta-oai | PASS |
| n192-1cta | PASS |
| n64-2cta-custom-bias | PASS |
| n192-partial-oai | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestMoeSortBufferInitPoisoned::test_wrapper_with_poisoned_moe_sort_buffers`

| Parameter ID | Status |
|---|---|
| 1-256 | PASS |
| 8-256 | PASS |
| 16-256 | PASS |
| 32-256 | PASS |
| 8-1280 | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestOddTileCountBoundsContract::test_odd_tile_count_with_poisoned_buffers`

| Parameter ID | Status |
|---|---|
| 9 | PASS |
| 11 | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestOddTileCountBoundsContract::test_cuda_graph_replay_with_changed_routing`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

#### Prepared controls (26 executions)

`prepared.xml`: `MXFP4_DENSE_TWO_STAGE=0`, 15 cases. `prepared-unfused.xml`: `MXFP4_DENSE_TWO_STAGE=1`, 11 cases. A shared parameter row below represents two separate executions when both cells contain a status.

`tests/moe/test_cute_dsl_mxfp4_situ.py::test_dense_dual_tile_routing_follows_rows_per_expert`

| Parameter ID | Prepared | Prepared-unfused |
|---|---|---|
| (none) | PASS | PASS |

`tests/moe/test_cute_dsl_mxfp4_situ.py::test_dense_dual_tile_keeps_128_where_256_pads`

| Parameter ID | Prepared | Prepared-unfused |
|---|---|---|
| 73 | PASS | PASS |
| 293 | PASS | PASS |

`tests/moe/test_cute_dsl_mxfp4_situ.py::test_dense_route_preprocess_pdl_matches_torch`

| Parameter ID | Prepared | Prepared-unfused |
|---|---|---|
| False-False | PASS | — |
| False-True | PASS | — |
| True-False | PASS | — |
| True-True | PASS | — |

`tests/moe/test_cute_dsl_mxfp4_situ.py::test_dense_gemm1_cluster_split_k_matches_plain`

| Parameter ID | Prepared | Prepared-unfused |
|---|---|---|
| 256-False-256 | PASS | PASS |
| 256-False-384 | PASS | PASS |
| 256-True-256 | PASS | PASS |
| 256-True-384 | PASS | PASS |
| 584-False-256 | PASS | PASS |
| 584-False-384 | PASS | PASS |
| 584-True-256 | PASS | PASS |
| 584-True-384 | PASS | PASS |

#### Standalone finalizer (107 configuration rows, two layouts each)

H=264, top-k=3, BF16 input/output. Each layout passes 104 nonempty comparisons plus **three zero-token no-ops** (one per scale dtype): 107 cases/layout, 214 total executions. `PASS` means byte-exact native comparison in eager and graphs with PDL off/on, plus changed-input replay (two replays/phase). `NOOP` means candidate-only eager/graph PDL-off/on validation; native's invalid zero-grid launch is not called.

Scales: `f32`=FP32, `f16`=FP16, `bf16`=BF16. FP16's native oracle receives exactly promoted FP32 scales; there is no native FP16 binding or timing claim. Patterns: `R`=random, `C`=cancellation, `SI`=subnormal_input, `SO`=subnormal_output, `TW`=tiny_weights. Routes: `E`=random_ep8, `A`=all_masked. `TW` runs only with FP32 scales. Expanded rows ignore positive mapping values; permuted rows use them as row addresses, including zero, with unused rows poisoned by NaNs. These standalone checks do not establish overlap with a live FC2 producer.

| Tokens | Scale | Pattern | Routes | Expanded | Permuted |
|---:|---|---|---|---|---|
| 0 | f32 | R | E | NOOP | NOOP |
| 0 | f16 | R | E | NOOP | NOOP |
| 0 | bf16 | R | E | NOOP | NOOP |
| 8 | f32 | R | E | PASS | PASS |
| 8 | f32 | R | A | PASS | PASS |
| 8 | f32 | C | E | PASS | PASS |
| 8 | f32 | C | A | PASS | PASS |
| 8 | f32 | SI | E | PASS | PASS |
| 8 | f32 | SI | A | PASS | PASS |
| 8 | f32 | SO | E | PASS | PASS |
| 8 | f32 | SO | A | PASS | PASS |
| 8 | f32 | TW | E | PASS | PASS |
| 8 | f32 | TW | A | PASS | PASS |
| 8 | f16 | R | E | PASS | PASS |
| 8 | f16 | R | A | PASS | PASS |
| 8 | f16 | C | E | PASS | PASS |
| 8 | f16 | C | A | PASS | PASS |
| 8 | f16 | SI | E | PASS | PASS |
| 8 | f16 | SI | A | PASS | PASS |
| 8 | f16 | SO | E | PASS | PASS |
| 8 | f16 | SO | A | PASS | PASS |
| 8 | bf16 | R | E | PASS | PASS |
| 8 | bf16 | R | A | PASS | PASS |
| 8 | bf16 | C | E | PASS | PASS |
| 8 | bf16 | C | A | PASS | PASS |
| 8 | bf16 | SI | E | PASS | PASS |
| 8 | bf16 | SI | A | PASS | PASS |
| 8 | bf16 | SO | E | PASS | PASS |
| 8 | bf16 | SO | A | PASS | PASS |
| 9 | f32 | R | E | PASS | PASS |
| 9 | f32 | R | A | PASS | PASS |
| 9 | f32 | C | E | PASS | PASS |
| 9 | f32 | C | A | PASS | PASS |
| 9 | f32 | SI | E | PASS | PASS |
| 9 | f32 | SI | A | PASS | PASS |
| 9 | f32 | SO | E | PASS | PASS |
| 9 | f32 | SO | A | PASS | PASS |
| 9 | f32 | TW | E | PASS | PASS |
| 9 | f32 | TW | A | PASS | PASS |
| 9 | f16 | R | E | PASS | PASS |
| 9 | f16 | R | A | PASS | PASS |
| 9 | f16 | C | E | PASS | PASS |
| 9 | f16 | C | A | PASS | PASS |
| 9 | f16 | SI | E | PASS | PASS |
| 9 | f16 | SI | A | PASS | PASS |
| 9 | f16 | SO | E | PASS | PASS |
| 9 | f16 | SO | A | PASS | PASS |
| 9 | bf16 | R | E | PASS | PASS |
| 9 | bf16 | R | A | PASS | PASS |
| 9 | bf16 | C | E | PASS | PASS |
| 9 | bf16 | C | A | PASS | PASS |
| 9 | bf16 | SI | E | PASS | PASS |
| 9 | bf16 | SI | A | PASS | PASS |
| 9 | bf16 | SO | E | PASS | PASS |
| 9 | bf16 | SO | A | PASS | PASS |
| 1024 | f32 | R | E | PASS | PASS |
| 1024 | f32 | R | A | PASS | PASS |
| 1024 | f32 | C | E | PASS | PASS |
| 1024 | f32 | C | A | PASS | PASS |
| 1024 | f32 | SI | E | PASS | PASS |
| 1024 | f32 | SI | A | PASS | PASS |
| 1024 | f32 | SO | E | PASS | PASS |
| 1024 | f32 | SO | A | PASS | PASS |
| 1024 | f32 | TW | E | PASS | PASS |
| 1024 | f32 | TW | A | PASS | PASS |
| 1024 | f16 | R | E | PASS | PASS |
| 1024 | f16 | R | A | PASS | PASS |
| 1024 | f16 | C | E | PASS | PASS |
| 1024 | f16 | C | A | PASS | PASS |
| 1024 | f16 | SI | E | PASS | PASS |
| 1024 | f16 | SI | A | PASS | PASS |
| 1024 | f16 | SO | E | PASS | PASS |
| 1024 | f16 | SO | A | PASS | PASS |
| 1024 | bf16 | R | E | PASS | PASS |
| 1024 | bf16 | R | A | PASS | PASS |
| 1024 | bf16 | C | E | PASS | PASS |
| 1024 | bf16 | C | A | PASS | PASS |
| 1024 | bf16 | SI | E | PASS | PASS |
| 1024 | bf16 | SI | A | PASS | PASS |
| 1024 | bf16 | SO | E | PASS | PASS |
| 1024 | bf16 | SO | A | PASS | PASS |
| 1025 | f32 | R | E | PASS | PASS |
| 1025 | f32 | R | A | PASS | PASS |
| 1025 | f32 | C | E | PASS | PASS |
| 1025 | f32 | C | A | PASS | PASS |
| 1025 | f32 | SI | E | PASS | PASS |
| 1025 | f32 | SI | A | PASS | PASS |
| 1025 | f32 | SO | E | PASS | PASS |
| 1025 | f32 | SO | A | PASS | PASS |
| 1025 | f32 | TW | E | PASS | PASS |
| 1025 | f32 | TW | A | PASS | PASS |
| 1025 | f16 | R | E | PASS | PASS |
| 1025 | f16 | R | A | PASS | PASS |
| 1025 | f16 | C | E | PASS | PASS |
| 1025 | f16 | C | A | PASS | PASS |
| 1025 | f16 | SI | E | PASS | PASS |
| 1025 | f16 | SI | A | PASS | PASS |
| 1025 | f16 | SO | E | PASS | PASS |
| 1025 | f16 | SO | A | PASS | PASS |
| 1025 | bf16 | R | E | PASS | PASS |
| 1025 | bf16 | R | A | PASS | PASS |
| 1025 | bf16 | C | E | PASS | PASS |
| 1025 | bf16 | C | A | PASS | PASS |
| 1025 | bf16 | SI | E | PASS | PASS |
| 1025 | bf16 | SI | A | PASS | PASS |
| 1025 | bf16 | SO | E | PASS | PASS |
| 1025 | bf16 | SO | A | PASS | PASS |

#### Additional W4A8 unfused pipeline results (all six report rows)

H256/I128, 256 global/32 local experts, top-k8. Each row runs PDL off and on, four phases, and three graph replays/phase: 12 pipeline configurations, 48 phases, 96 native-oracle comparisons. The fixed tactic is `(128, ((128,128),(1,1),False), ((128,128),(1,1),False))`.

| Tokens | Expert offset | Native oracle | Graph/eager | PDL off/on | Restored inputs |
|---:|---:|---|---|---|---|
| 1 | 0 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |
| 1 | 128 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |
| 17 | 0 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |
| 17 | 128 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |
| 1025 | 0 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |
| 1025 | 128 | bitwise_equal | bitwise_equal | bitwise_equal | bitwise_equal |

#### Raw summary lines

```text
# native-tests/core.log
================ 129 passed, 3016 warnings in 349.30s (0:05:49) ================
# native-tests/prepared.log
====================== 15 passed, 713 warnings in 25.03s =======================
# native-tests/prepared-unfused.log
====================== 11 passed, 470 warnings in 16.55s =======================
# standalone-expanded.log
PASS: 107 cases; 0 timing rows
# standalone-permuted.log
PASS: 107 cases; 0 timing rows
# w4a8-unfused.log
PASS: 12 pipeline configurations, 48 phases, 96 native-oracle comparisons
```
