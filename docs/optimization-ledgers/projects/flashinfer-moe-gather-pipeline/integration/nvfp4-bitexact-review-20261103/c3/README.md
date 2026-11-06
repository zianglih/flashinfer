# C3 NVFP4 bit-exact reference-plan validation

The four existing unified NVFP4 swap-AB fixtures **passed before the fix**. Their native kernels nevertheless selected K96 while the unobserved reference used K64. This run confirms the structural mismatch; it does not reproduce a numerical failure on those fixtures.

The shared observer fix passed all **8 selected zero-tolerance tests**: four unified typed activations, two functional NVFP4/per-token cases, and two wrapper NVFP4/per-token cases. Including the four before executions, there were 12 successful executions / 8 unique test IDs, with no failures or skips.

- Production source: `2b4732791a3ce48bc3ae6c030a283fab73854e0e`, unchanged in both phases.
- After patch: `../shared-observer.patch`, SHA256 `0264b46cf8980d3079a07447b2673cf59643e16d6b5f68ba244611391737d911`.
- Test-file after hashes match all three current canonical files: `tests/moe/conftest.py`, `tests/moe/test_cute_dsl_fused_moe.py`, and `tests/moe/test_unified_moe.py`.
- C3 devbox: `fi-pr7290-perf-1102`, NVIDIA B300 SXM6 AC (SM103), driver `595.91.07`; GPUs 0–2 used for the three parallel after groups.
- Existing image: `nvcr.io/nvidia/pytorch:26.05-py3`; Torch `2.12.0a0+5aff3928d8.nv26.05` / CUDA 13.2; PTXAS 13.2.78; CuTe DSL 4.8.0 with embedded compiler CUDA 13.4.
- No sanitizer, benchmark, production-kernel edit, oracle-arithmetic edit, tactic override, or tolerance relaxation.

## Raw pytest summaries

```text
before-unified-selected:
================ 4 passed, 12 deselected, 71 warnings in 29.63s ================
after-unified:
================ 4 passed, 12 deselected, 71 warnings in 23.66s ================
after-functional:
================ 2 passed, 18 deselected, 96 warnings in 53.82s ================
after-wrapper:
======================= 2 passed, 96 warnings in 12.66s ========================
```

Warnings are the existing CuTe deprecated API warnings. Full logs, JUnit, native plans, and exact invocation/environment receipts are under `evidence/<group>/`.

## Selected tests

Before and after:

```bash
pytest -v -s tests/moe/test_unified_moe.py::test_cute_dsl_typed_activation_matches_flat_reference -k 'NVFP4xNVFP4 and True'
```

This selects SwiGLU, SiTU, GeGLU-tanh, and ReLU2 at T=8, H=1024, I=512, E=8, top-k=2, swap-AB=True, unfused finalization.

Additional after groups:

```bash
pytest -v -s tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy -k 'swap-ab-True'
pytest -v -s 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-tensor-128]' 'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-token-128]'
```

The functional cases cover SwiGLU/per-tensor at H=256/I=512 and ReLU2/per-token at H=1024/I=2048. Both wrapper cases use H=256/I=512. All are unfused.

## Observed instruction plan and provenance

The passive diagnostic plugin wraps `cute.compile` only to record kernel metadata. It does not change tactics, native plans, cache contents, or references. Native K96 was observed in FC1 and FC2 for every compiled NVFP4 case; stage widths were FC1 K512 and FC2 K256.

For the unified H=1024/I=512 case, the shared observer therefore supplies:

- FC1: `(96, 96, 96, 96, 64, 64)` twice, preserving both K512 stages.
- FC2: `(96, 96, 64)` twice, preserving both K256 stages.

The per-tensor H=256 FC1 has a partial K512 stage, which uses `(96, 96, 64)`. Thus the bounded selection covers K96, K64 tails, stage boundaries, partial stages, and FC2 cache reuse across typed activations without adding tactic tests.

The isolated test tree was copied from all 34,759 verified source/submodule files. To avoid unnecessary C++ rebuilding for this test-only patch, each process preimports the immutable 2b production package and then puts the isolated test tree first for pytest. Original test files are archived in `evidence/original-tests/`. Correct production data symlinks, launch-source hashes, native ELF/Ninja hashes, and normal Ninja no-op checks passed. The native cache was reused through the normal loader, with no ELF transplant; separate CuTe/driver cache directories were used.

Two earlier setup attempts selected zero cases because they used a nonmatching generic parameter ID. Their output is retained; they are excluded from successful execution counts. A metadata-export import typo was corrected after testing and did not cause any GPU rerun.

## Evidence

- `evidence/summary.json`: canonical results and exact patch/test-file hashes.
- `evidence/production-postflight.json`: unchanged production and native cache, normal Ninja no-op output.
- `evidence/runtime.json`: current versions, hardware, and GPU UUIDs.
- `evidence/<group>/mma-plans.jsonl`: passive native-plan records.
- `fetch-receipt.json`: all 43 evidence-file hashes verified after download.
- Archive: `evidence.tar.gz`, 108,592 bytes, SHA256 `a8b134371728918d9bfc1b364c18c7068c1a01bdd704f9ebde0cb9ca01e38ed8`.
