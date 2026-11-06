## Validation

The focused run used `0c1e00fc3e4f913c8c241796c70a29673737c542` plus patch `4eae30d3cd181737b3a42ca5ac3bd1415c401d7b70109d75352a33abf6eeaff1` before commit. All 83 recorded benchmark, kernel and test files are byte-identical to `853aaf69d706b291afee477f738956b997033f53`; source hashes were unchanged during testing. This is an explicit byte binding, not a claim that the test checkout already had the final commit ID.

Reproduce from the final checkout and environment above:

```bash
CUDA_VISIBLE_DEVICES=7 python -m pytest -q -ra --tb=short --rootdir=. -o cache_dir=../focused49-cache tests/moe/test_cute_dsl_moe_can_implement.py 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-1-64]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-17-512]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[32-17-192]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[64-17-384]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[128-17-64]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[256-17-512]' 'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-off]' 'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-on]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-tensor]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-token]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]' tests/moe/test_cute_dsl_fused_moe.py::TestInputsHelperContract::test_assignments_match_requested_expert_counts --junitxml=../focused49.xml
```

<details>
<summary>Complete focused pytest output</summary>

```text
.................................................                        [100%]
=============================== warnings summary ===============================
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/tests/conftest.py:30
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/tests/conftest.py:30
  /workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/cute_dsl/availability.py:136
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/cute_dsl/availability.py:136
  /workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:739: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:740: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
  /workspace/flashinfer-w4a4-split-dynamic-n/mixed-epilogue-overlap-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:899: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    sched_params = utils.ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:232: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    new_params = ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:421: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

tests/moe/test_cute_dsl_fused_moe.py: 36 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:359: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
49 passed, 98 warnings in 19.19s
```

</details>

**Additional checks:** 12 static/SM-budget and 12 CLC/clamped-activation cases compare initialized output payload and scale-factor bytes exactly. They include K tails, padded routes and persistent scheduling. Scoped pre-commit passed on the retained change. Existing layout, per-token, PDL and activation contracts are covered by the selected 49 cases.

**Boundary:** broad correctness and sanitizer campaigns remain deferred. Unretained experiments, profiler captures and incremental measurements stay in the local ledger. Benchmark sweeps do not replace numerical validation.
