**Current accuracy cleanup — `658a0c89`:** fold the two standalone swap-AB tests into the existing K-tail and deterministic-finalize accuracy tests, preserving all 76 tail cases and all 16 numerical cases. MXFP4x8/MXFP8 still exercise both public APIs with zero tolerance, including SiTU, N16 and two-CTA tactics. Existing Rubin skips are preserved; numerical references are unchanged.

One B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.8.0, pytest 8.4.2. The GPU-tested file exactly matches the committed file; production is unchanged from `4376662a`. Scoped pre-commit and commit hooks pass. No sanitizer was run.

```bash
python3 -m pytest -q --full \
  tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy
```

```text
92 passed, 1132 warnings in 633.19s (0:10:33)
```

Warnings are CuTe deprecations. [Complete test output](@@TEST_ARTIFACT_BASE@@/pytest.log) · [Validation receipt](@@TEST_ARTIFACT_BASE@@/run.json).
