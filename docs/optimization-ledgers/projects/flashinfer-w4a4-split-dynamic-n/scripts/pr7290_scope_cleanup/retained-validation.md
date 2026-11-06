**Targeted gate:** 49 passed on one B200 GPU (UUID `GPU-a4c14cdc-d487-e8b3-9e76-1fdbbb5e1a21`), using the same CUDA 13.2 virtual environment. This ran on the unchanged pre-commit experiment snapshot; all five retained production/test files are byte-identical to `fca8462cbd9096059d0019a206aa760fb34ca8c4`. The six new cases extend the existing inputs-helper contract class.

Portable equivalent from the final-source checkout after the setup above (same test flags and selectors). The recorded run used GPU 5 and an unchanged experiment snapshot; exact original argv, paths and five-file hash bindings remain in the local validation audit.

```bash
CUDA_VISIBLE_DEVICES=0 \
CUTE_DSL_CACHE_DIR="$PWD/../cache/validation-final" \
FLASHINFER_WORKSPACE_BASE="$PWD/../cache/native" \
FLASHINFER_CUDA_ARCH_LIST=10.0a PYTHONPATH="$PWD" \
python -m pytest -q -ra --tb=short \
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
tests/conftest.py:30
tests/conftest.py:30
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025/pr7290-v41-stage-ghost-r1-a1/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025/pr7290-v41-stage-ghost-r1-a1/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025/pr7290-v41-stage-ghost-r1-a1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:724: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py: 21 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025/pr7290-v41-stage-ghost-r1-a1/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:725: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
49 passed, 46 warnings in 9.67s
```

**Static checks:** scoped pre-commit passed for the five retained files and benchmark display cleanup; Python compilation and Ruff passed. The paired benchmark and final script have identical preparation, routing, backend dispatch and timing ASTs. Changes to family defaults and display plumbing retain six byte-identical 13-row formatter fixtures.

**Boundary:** these are the selected existing shape/layout, activation, per-token, PDL and helper checks listed above. The full MoE suite and sanitizer campaign were not run in this gate. Benchmark sweeps do not substitute for numerical testing.
