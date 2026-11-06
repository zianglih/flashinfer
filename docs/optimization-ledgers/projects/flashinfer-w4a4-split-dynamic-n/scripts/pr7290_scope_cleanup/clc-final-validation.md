**Targeted final-source gate:** 49 passed on B200 GPU 7 (`GPU-fda1e899-fdcf-494b-7f11-35be262f3fb8`), using clean commit `0c1e00fc3e4f913c8c241796c70a29673737c542` and the CUDA 13.2 virtual environment. All 83 recorded source files were verified unchanged before and after the run. The six helper cases extend the existing contract test class.

Portable equivalent from the final-source checkout after the setup above (same test flags and selectors). The exact recorded argv, environment, source hashes and JUnit report remain in the local validation audit.

```bash
CUDA_VISIBLE_DEVICES=0 \
CUTE_DSL_CACHE_DIR="$PWD/../cache/validation-final" \
FLASHINFER_WORKSPACE_BASE="$PWD/../cache/native" \
FLASHINFER_CUDA_ARCH_LIST=10.0a PYTHONPATH="$PWD" \
python -m pytest -q -ra --tb=short --rootdir=. \
  -o cache_dir=../cache/validation-final/pytest-cache \
  tests/moe/test_cute_dsl_moe_can_implement.py \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-1-64]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-17-512]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[32-17-192]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[64-17-384]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[128-17-64]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[256-17-512]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-off]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-on]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]' \
  tests/moe/test_cute_dsl_fused_moe.py::TestInputsHelperContract::test_assignments_match_requested_expert_counts \
  --junitxml=pytest-final.xml
```

Complete pytest output:

```text
.................................................                        [100%]
=============================== warnings summary ===============================
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/tests/conftest.py:30
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/tests/conftest.py:30
  /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/cute_dsl/availability.py:136
../../../../../../workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/cute_dsl/availability.py:136
  /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:739: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:740: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
  /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-v3-clc-final-tables-r1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:899: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
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
49 passed, 98 warnings in 10.94s
```

**Additional focused checks:** the unchanged CLC core passed 57 persistent exact/padded/zero-live diagnostic cases, and 360 actual-layout/storage policies were checked. The final host admission guard passed all 156 observed dispatches, all 338 model/token/tactic cases and the 65,535/65,536 boundary audit. Complete diagnostic logs remain local. Scoped pre-commit passed on the three retained CLC files; the benchmark source is byte-identical between the paired campaign and final public tables.

**Boundary:** the final 49 cases cover the selected shape/layout, activation, per-token, PDL and helper contracts listed above. The full MoE suite and sanitizer campaign remain deferred. Large-grid fallback is verified at the host-policy/SDK level, without a giant end-to-end allocation. Benchmark sweeps do not substitute for numerical testing.
