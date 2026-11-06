# PR7290 cleanup validation

Committed source: `d35fcfda03875077b3af8455575cc1d20e866a8c`. Tested as its parent `33b7e526` plus patch `47a0ca625c8959ed7292b598bc9ea8f9b998ad9072ce5b378ed6d95503a7a8a9`; all 513 frozen source hashes match the committed files.

95 existing tests passed: 33 MoE accuracy cases and 62 API/wrapper/graph/autotuner cases, with zero failures, errors or skips. No new repository tests, sanitizer or performance rerun. The PR performance tables remain measurements of `33b7e526`.

Environment: 2 NVIDIA B300 SXM6 AC GPUs, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.8.0, pytest 9.1.1, TVM FFI 0.1.15.post1. Both suites ran concurrently on separate GPUs. Nine native compilation-cache links were retained on persistent cluster storage.

## Reproduction

Use the image and package versions above, initialize the repository submodules, and install the checkout with `python -m pip install --no-build-isolation -e .`. Run from the repository root with the existing GPU environment:

```bash
git checkout d35fcfda03875077b3af8455575cc1d20e866a8c
export FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_CUDA_ARCH_LIST=10.3a
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
export TRTLLM_ENABLE_PDL=1
export MAX_JOBS=8
export OMP_NUM_THREADS=1
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
```

Set `FLASHINFER_WORKSPACE_BASE` to an existing persistent compilation-cache directory. Do not clear it. These are the exact selected test nodes; no full-suite or timing claim is made.

### exact: 33 cases

```bash
CUDA_VISIBLE_DEVICES=0 python -m pytest -q --disable-warnings --maxfail=1 \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[True-swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-clamp-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-and-up-clamp-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep[8-swap-ab-w4a16]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max448-swap-ab-fast]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max256-swap-ab-strict]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-swiglu-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-swiglu-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-and-up-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-and-up-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-swiglu-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-swiglu-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-and-up-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-and-up-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-1-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-17-128]' \
  tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_moe \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[True-relu2-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max448-swap-ab-strict]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max256-swap-ab-fast]' \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_weight_scale_update
```

### api: 62 cases

```bash
CUDA_VISIBLE_DEVICES=1 python -m pytest -q --disable-warnings --maxfail=1 \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-tensor-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-tensor-fused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-fused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a16-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-tensor-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-token-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a16-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-tensor-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-tensor-fused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-fused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a16-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a16]' \
  tests/moe/test_unified_moe.py::test_cute_dsl_typed_activation_matches_flat_reference \
  tests/moe/test_cute_dsl_fused_moe.py::test_w4a8_fused_moe_tactics_and_apis \
  tests/autotuner/test_autotune_cache_scope.py \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_overrides_profiling_config \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_isolates_store_identity \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_attach_carries_to_serving \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_execution_mode_resolution \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_all_none_is_default_identity \
  tests/autotuner/test_autotune_cache_v2.py::test_policy_switch_reprofiles_in_process
```

## Raw summaries

```text
.................................                                        [100%]
33 passed, 1275 warnings in 122.35s (0:02:02)
..............................................................           [100%]
62 passed, 2406 warnings in 94.57s (0:01:34)
```

## Static checks and boundaries

- All changed PR files and the cleanup commit passed pre-commit, including mypy and Ruff.
- All 28 production device-function ASTs are unchanged. Two host planner simplifications passed 1,779,592 equivalence cases.
- The 360 swap-AB tactics retain their order and values; 2,904 forwarding cases, 27 invalid-input rejections, 30 legacy forwards, and 288 output-SF cases matched. W4A16 tactics are unchanged.
- 32 table fixtures preserve columns, measurements and winner formatting; only mode-dependent skip notices and missing-row checks are corrected.
- 24 sanitizer-option comparisons preserve the standalone script's kernel coverage. The sanitizer was not run.
- Reusing the existing exact multiply helper preserves the expanded reference AST; GPU accuracy tests exercise the reference against the implementation.
- 3,070 tracked Python/shell files per test group were hashed and rechecked. The saved 30-file test archive has SHA256 `d6b98ac46c6293601e9728d2d96ded5d8f5f16c0d12b0386d5903f7ee8b85577`.
- These checks do not qualify every tactic or Rubin hardware, and are not fresh performance measurements.
