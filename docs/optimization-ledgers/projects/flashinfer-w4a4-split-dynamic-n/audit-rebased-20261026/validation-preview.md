## Validation

Final `65c2c5c4` passed scoped pre-commit; source checks confirm the 32 CPU trace cases, 1,080 tactic roundtrips, and host/Rubin equivalence remain valid. At `eb141478` on B300, 24/24 `MoELayer`/wrapper parity cases matched exactly with finite outputs across both MX pairs, nondefault SwiGLU/SiTU, PDL on/off, and changed/empty local routes at nonzero EP offset. Focused B300 pytest at `eb141478`: **71 passed, 0 skipped, 0 failed, 0 errors**.

<details>
<summary>Focused pytest command and raw output</summary>

```bash
CUDA_VISIBLE_DEVICES=0 python -m pytest -q -ra --tb=short tests/moe/test_cute_dsl_moe_can_implement.py 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-1-64]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[16-17-512]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[32-17-192]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[64-17-384]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[128-17-64]' 'tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail[256-17-512]' 'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-off]' 'tests/moe/test_cute_dsl_fused_moe.py::test_moe_core_forwards_enable_pdl[pdl-on]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-tensor]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-token]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]' tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis tests/moe/test_cute_dsl_fused_moe.py::test_situ_changes_autotuner_cache_key tests/moe/test_cute_dsl_fused_moe.py::test_invalid_situ_config tests/moe/test_cute_dsl_mxfp8_moe.py --junitxml=../focused.xml -o cache_dir=../focused-cache
```

```text
.......................................................................  [100%]
=============================== warnings summary ===============================
../../../../../workspace/flashinfer-w4a4-split-dynamic-n/rebased-audit-1026-source/tests/conftest.py:30
../../../../../workspace/flashinfer-w4a4-split-dynamic-n/rebased-audit-1026-source/tests/conftest.py:30
  /workspace/flashinfer-w4a4-split-dynamic-n/rebased-audit-1026-source/tests/conftest.py:30: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    from cutlass.cute.nvgpu.tcgen05 import OperandMajorMode

flashinfer/cute_dsl/availability.py:136
flashinfer/cute_dsl/availability.py:136
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025/rebased-audit-1026-source/flashinfer/cute_dsl/availability.py:136: DeprecationWarning: Arch from arch.py is deprecated. Use Arch from enums.py instead.
    from cutlass.base_dsl.arch import Arch

tests/moe/test_cute_dsl_fused_moe.py: 37 warnings
tests/moe/test_cute_dsl_mxfp8_moe.py: 11 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025/rebased-audit-1026-source/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:994: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py: 37 warnings
tests/moe/test_cute_dsl_mxfp8_moe.py: 11 warnings
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025/rebased-audit-1026-source/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:995: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead
    tcgen05.OperandMajorMode.K,

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_moe[64-640-3584-384-8]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_partial_channel_tile[256]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_partial_channel_tile[512]
  /data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025/rebased-audit-1026-source/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1165: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    sched_params = utils.ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py: 8 warnings
tests/moe/test_cute_dsl_mxfp8_moe.py: 6 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:232: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    new_params = ClcDynamicPersistentTileSchedulerParams(

tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.05]
tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_swiglu_limit_accuracy[w4a4-0.1]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_moe[64-640-3584-384-8]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_partial_channel_tile[256]
tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_partial_channel_tile[512]
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:421: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

tests/moe/test_cute_dsl_fused_moe.py: 84 warnings
tests/moe/test_cute_dsl_mxfp8_moe.py: 63 warnings
  /workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/utils/dynamic_persistent_tile_scheduler.py:359: DeprecationWarning: Migrated to examples/CuTeDSL/helpers/dynamic_persistent_tile_scheduler.py (BSD-3). The wheel copy will be removed in a future release.
    return ClcDynamicPersistentTileScheduler(

tests/moe/test_cute_dsl_fused_moe.py: 16 warnings
tests/moe/test_cute_dsl_mxfp8_moe.py: 11 warnings
  <string>:13: DeprecationWarning: tcgen05.OperandMajorMode is deprecated, use cute.nvgpu.OperandMajorMode instead

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
71 passed, 302 warnings in 448.90s (0:07:28)
```

</details>

Broad correctness and sanitizer campaigns remain deferred. Rubin hardware was not exercised.
