## Validation

**Retained head `99f4d0c27`:** 28 existing B300 accuracy cases passed, plus 144 source-paired exact public replays, 96 prepare byte replays, 110 routed quantizer replays and six unchanged default-quantizer contracts. The gated kernel/preparation/quantizer sources are identical to this commit; frontend type annotations and formatting were separately verified to preserve the AST and executable bytecode. Coverage includes static/CLC, PDL on/off, one/two CTA, narrow/wide N, M512, and empty/reactivated routes across all four blockscaled formats.

All 72 inspected candidate variants use 256 threads, with no spills or scalar async activation-scale loads. All applicable commit hooks passed, including Ruff and mypy. **Sanitizer runs were explicitly skipped at the user's request.** This is focused coverage, not an exhaustive cross-product; Rubin is untested.

<details>
<summary>Existing accuracy command and raw result</summary>

Run from the FlashInfer checkout in the CUDA 13.2 / CuTe DSL 4.8.0 environment above:

```bash
/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -m pytest -q --disable-warnings --maxfail=1 \
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
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-17-128]' \
  tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_moe \
  --junitxml /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261027/warp-specialization/r2/aux-gate/accuracy.xml
```

```text
............................                                             [100%]
28 passed, 1108 warnings in 62.63s (0:01:02)
```

</details>
