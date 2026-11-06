### Current-head C2 follow-up (`9c39a455`)

- **Result:** 72 existing upstream cases passed (8 CI regressions + 64 W4A16), zero failures/errors/skips. Original assertions/tolerances retained; no upstream tests added.
- **Source:** `9c39a45529c4bbffd866f7ae6255b19eaf835aa7`, base `a31c72523ae37d82fd657de36ce2b35156c3c559`. Full Python/JIT/native checkout; current `csrc`/`include`, unchanged nightly vendor headers. Source archive SHA256 `c5abb6a5e58ca945d54fdf91dded36810e4742bc539977eb2c20acb02bcbbd6b`.
- **Environment:** c2, `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2); one NVIDIA B300 SXM6 AC / SM103 GPU0 of 8 allocated, driver 590.48.01; Python 3.12.3, Torch `2.12.0a0+5aff3928d8.nv26.05`. Official FlashInfer Python/cubin `0.7.0.dev20260923`, JIT/SM103a `0.7.0.dev20260923+cu130`; CuTe DSL 4.7.1, TVM FFI 0.1.11, pytest 9.1.1, cuda-bindings 13.2.0. Source version `0.0.0+unknown`; JIT enabled, no version-check override.
- **Coverage:** corrected SiTU rejection regexes and generated activation matrix; W4A16 deterministic accuracy, route-tile boundaries, wrapper CUDA graphs and simulated EP8, with fused/unfused controls. Inter-GPU transport and the full repository suite were not tested. Earlier 155/214/96 evidence remains pinned to `bde42729`; **no new benchmark** was run.
- **GitHub CI:** the initial [run 36480641864](https://github.com/flashinfer-ai/flashinfer/actions/runs/36480641864) skipped GPU jobs pending authorization. The authorized replacement [run 36482176398](https://github.com/flashinfer-ai/flashinfer/actions/runs/36482176398) targets `9c39a455`: Permission/Setup passed, builds are starting, and GPU jobs are queued. Docs, API checks and pre-commit pass. The C2 results below are independent executions; GitHub GPU results are not yet available.

<details>
<summary>Exact native test commands</summary>

Use the full-source/nightly setup below with `TASK_ROOT=/hai-workspace/fi5319-ci` and both Git fetch/checkout revisions set to `9c39a45529c4bbffd866f7ae6255b19eaf835aa7`. After preparing that fresh checkout and its native-source links:

```bash
export PYTHONPATH=/hai-workspace/fi5319-ci/repo
export FLASHINFER_WORKSPACE_BASE=/hai-workspace/fi5319-ci/cache
export CUDA_VISIBLE_DEVICES=0 MAX_JOBS=16 PYTHONUNBUFFERED=1
unset FLASHINFER_DISABLE_JIT FLASHINFER_DISABLE_VERSION_CHECK FLASHINFER_DIST_AWARE_AUTOTUNE
cd /hai-workspace/fi5319-ci/repo
mkdir -p /hai-workspace/fi5319-ci/artifacts/tests
python -m pytest -v --tb=short --durations=10 --junitxml=/hai-workspace/fi5319-ci/artifacts/tests/ci-regressions.xml tests/moe/test_cute_dsl_fused_moe.py::test_invalid_situ_config tests/moe/test_cute_dsl_bf16_gather_grouped_gemm.py::test_cute_dsl_bf16_gather_grouped_gemm_rejects_bad_activation_config tests/moe/test_cute_dsl_bf16_moe.py::test_sm90_moe_runner_rejects_bad_activation_config tests/moe/test_unified_moe_activation_matrix.py
python -m pytest -v --tb=short --durations=10 --junitxml=/hai-workspace/fi5319-ci/artifacts/tests/w4a16.xml -k w4a16 tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep
```

</details>

<details>
<summary>All 72 per-case results and raw pytest summaries</summary>

Append `[Parameter ID]` to each exact method prefix; `(none)` means unparameterized. No case durations are shown.

**ci-regressions: 8 cases**

`tests/moe/test_cute_dsl_fused_moe.py::test_invalid_situ_config`

| Parameter ID | Status |
|---|---|
| 3-None-1.0-requires situ_beta | PASS |
| 3-0.0-None-positive and finite | PASS |
| 8-1.0-None-require ActivationType&#92;&#92;.Situ or Swiglu | PASS |

`tests/moe/test_cute_dsl_bf16_gather_grouped_gemm.py::test_cute_dsl_bf16_gather_grouped_gemm_rejects_bad_activation_config`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

`tests/moe/test_cute_dsl_bf16_moe.py::test_sm90_moe_runner_rejects_bad_activation_config`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

`tests/moe/test_unified_moe_activation_matrix.py::test_activation_matrix_rows_are_unique_and_complete`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

`tests/moe/test_unified_moe_activation_matrix.py::test_documented_activation_matrix_matches_runner_registry`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

`tests/moe/test_unified_moe_activation_matrix.py::test_quant_specific_activation_mapping_must_cover_exact_variants`

| Parameter ID | Status |
|---|---|
| (none) | PASS |

**w4a16: 64 cases**

`tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy`

| Parameter ID | Status |
|---|---|
| w4a16-swiglu | PASS |
| w4a16-relu2 | PASS |

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
| 256-64-w4a16-False | PASS |
| 256-64-w4a16-True | PASS |
| 256-128-w4a16-False | PASS |
| 256-128-w4a16-True | PASS |
| 256-256-w4a16-False | PASS |
| 256-256-w4a16-True | PASS |
| 384-64-w4a16-False | PASS |
| 384-64-w4a16-True | PASS |
| 384-128-w4a16-False | PASS |
| 384-128-w4a16-True | PASS |
| 384-256-w4a16-False | PASS |
| 384-256-w4a16-True | PASS |

`tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep`

| Parameter ID | Status |
|---|---|
| 8-w4a16-False | PASS |
| 8-w4a16-True | PASS |

Raw summary lines (verbatim):

```text
# ci-regressions.log
======================== 8 passed, 4 warnings in 0.56s =========================
# w4a16.log
========= 64 passed, 30 deselected, 1069 warnings in 388.62s (0:06:28) =========
```

</details>
