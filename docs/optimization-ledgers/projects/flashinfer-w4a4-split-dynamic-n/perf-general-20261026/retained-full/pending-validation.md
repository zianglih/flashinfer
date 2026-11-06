## Validation

**82 existing tests passed; no failures or skips:** cache names, large-row grid reuse/addressing, FP16/BF16 wide rows and all scale layouts, output-scale padding, GeGLU/SiTU, wrapper accuracy and graph replay. No upstream tests were added for these optimizations.

<details>
<summary>Existing test commands and raw output</summary>

```bash
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 TRTLLM_ENABLE_PDL=1 python -m pytest -q -x \
  tests/jit/test_cute_dsl_cache.py -k nvfp4_kernel_name
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 TRTLLM_ENABLE_PDL=1 python -m pytest -q -x \
  tests/utils/test_nvfp4_per_token_quantize_large_m.py \
  tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_out_scale_fold \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-1536-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-1536-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-18432-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-18432-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-69632-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-0-130-69632-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-1536-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-1536-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-18432-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-18432-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-69632-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-1-130-69632-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-1536-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-1536-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-18432-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-18432-dtype1]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-69632-dtype0]' \
  'tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_per_token_cute_dsl_wide_rows[cuda:0-2-130-69632-dtype1]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-clamp-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-and-up-clamp-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-False]'
```

### cache-names

```text
.....................................                                    [100%]
=============================== warnings summary ===============================
tests/conftest.py:30
tests/conftest.py:30
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
37 passed, 32 deselected, 3 warnings in 1.12s
```

### large-m

```text
....                                                                     [100%]
=============================== warnings summary ===============================
tests/conftest.py:30
tests/conftest.py:30
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
4 passed, 3 warnings in 3.46s
```

### quantizer-defaults

```text
....................................                                     [100%]
=============================== warnings summary ===============================
tests/conftest.py:30
tests/conftest.py:30
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
36 passed, 108 deselected, 3 warnings in 10.61s
```

### gated-moe

```text
.....                                                                    [100%]
=============================== warnings summary ===============================
tests/conftest.py:30
tests/conftest.py:30
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-and-up-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-False]
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:994: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-and-up-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-False]
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:995: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-and-up-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-False]
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/retained-policy-r2/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1165: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    sched_params = utils.ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py: 10 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/control-0def601d/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:232: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    new_params = ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[gate-and-up-clamp-w4a4-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-False-128]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-False]
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/control-0def601d/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:421: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

tests/moe/test_cute_dsl_fused_moe.py: 105 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/control-0def601d/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:359: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
5 passed, 143 warnings in 13.08s
```

</details>

Broad correctness and sanitizer campaigns remain deferred. Rubin hardware was not exercised.
