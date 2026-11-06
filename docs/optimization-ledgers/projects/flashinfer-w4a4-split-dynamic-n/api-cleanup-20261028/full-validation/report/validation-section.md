## Validation

**Current `d1767be1f`:** 95 existing pytest cases and 11 Linux CI compile-cache tests passed, with zero failures, errors or skipped pytest cases. This includes 72 MoE cases and 23 autotuner/cache cases: swap-AB exact-reference checks across the four blockscaled formats and supported activations, W4A16 layouts and scale updates, strict/fast quantization recipes, K tails, one/two CTA, legacy/swap-AB wrapper and unified APIs, scoped replay and CUDA graph capture. Legacy controls retain their existing tolerance.

Tests used GPUs 6–7 on the same B300 source snapshot and CUDA 13.2 image as the benchmark; their source hashes were checked before/after execution. Full repository pre-commit passed, including Ruff and mypy. This is focused coverage, not every tactic or Rubin qualification. **Sanitizer runs remain skipped; Rubin is untested.**

<details>
<summary>Existing test commands and complete raw output</summary>

Run from the FlashInfer checkout in the environment above:

```bash
python -m pytest -q --disable-warnings --maxfail=1 \
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
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_weight_scale_update \
  --junitxml \
  gpu6-exact.xml
```

```text
.................................                                        [100%]
33 passed, 1287 warnings in 122.48s (0:02:02)
```

```bash
python -m pytest -q --disable-warnings --maxfail=1 \
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
  tests/autotuner/test_autotune_cache_v2.py::test_policy_switch_reprofiles_in_process \
  --junitxml \
  gpu7-api.xml
```

```text
..............................................................           [100%]
62 passed, 2424 warnings in 71.48s (0:01:11)
```

```bash
python3 -m unittest discover -s ci/tests -p test_compile_cache.py -v
```

```text
test_disk_pressure_and_stale_image_eviction (test_compile_cache.CompileCacheTest.test_disk_pressure_and_stale_image_eviction) ... ok
test_docker_failure_preserves_exit_status_and_prunes (test_compile_cache.CompileCacheTest.test_docker_failure_preserves_exit_status_and_prunes) ... ok
test_failed_pull_does_not_run_or_mutate_cache (test_compile_cache.CompileCacheTest.test_failed_pull_does_not_run_or_mutate_cache) ... ok
test_invalid_configuration_disables_caching (test_compile_cache.CompileCacheTest.test_invalid_configuration_disables_caching) ... ok
test_opt_out_and_cpu_mode (test_compile_cache.CompileCacheTest.test_opt_out_and_cpu_mode) ... ok
test_private_entrypoint_preserves_timestamps_and_command_status (test_compile_cache.CompileCacheTest.test_private_entrypoint_preserves_timestamps_and_command_status) ... ok
test_pruning_retains_content_keyed_objects (test_compile_cache.CompileCacheTest.test_pruning_retains_content_keyed_objects) ... ok
test_pulled_image_identity_isolates_rebuilt_tags (test_compile_cache.CompileCacheTest.test_pulled_image_identity_isolates_rebuilt_tags) ... ok
test_read_only_jobs_preserve_seed_and_cleanup_on_success_or_failure (test_compile_cache.CompileCacheTest.test_read_only_jobs_preserve_seed_and_cleanup_on_success_or_failure) ... ok
test_runner_eviction_cannot_remove_another_runners_cache (test_compile_cache.CompileCacheTest.test_runner_eviction_cannot_remove_another_runners_cache) ... ok
test_same_runner_is_locked_across_eviction_and_execution (test_compile_cache.CompileCacheTest.test_same_runner_is_locked_across_eviction_and_execution) ... ok

----------------------------------------------------------------------
Ran 11 tests in 5.169s

OK
```

</details>
