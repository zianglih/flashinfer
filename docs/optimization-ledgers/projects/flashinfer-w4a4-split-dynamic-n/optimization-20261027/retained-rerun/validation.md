## Validation

**`1e69d0a39`:** 24 selected existing bit-exact accuracy cases passed, plus 96 public-API graph replays matching baseline output bytes across static/CLC scheduling, PDL on/off, and balanced/skewed/empty/reactivated routes. Same B300/CUDA 13.2 environment as above. All changed-file pre-commit checks passed. This is bounded coverage; the full suite, Rubin and GPU sanitizers were not run in this iteration. No standalone reference tests were added.

```text
........................                                                 [100%]
24 passed, 858 warnings in 50.43s
```

<details><summary>Exact pytest selections</summary>

```bash
python -m pytest -q --disable-warnings --maxfail=1 \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[True-swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-clamp-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-and-up-clamp-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a16-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a16]' \
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
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-17-128]'
```

</details>
