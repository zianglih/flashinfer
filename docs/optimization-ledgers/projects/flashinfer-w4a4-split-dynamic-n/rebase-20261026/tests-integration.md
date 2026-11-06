# PR #7290 rebase: test integration

Changed only the three assigned existing test files in `flashinfer-generality-review`. No staging, commit, rebase continuation, GPU work, or devbox operation was performed.

- Resolved `tests/moe/test_cute_dsl_fused_moe.py` by retaining the replacement physical channel-M/routed-token-N tactic checks, private K pair and scheduler checks, and all existing test functions. Preserved upstream's removal of the obsolete Rubin unfused-finalize fixture skip. Used upstream's canonical `quant_mode="mxfp8"` in the former `"w8a8"` cases, following the user's latest instruction; no alias was added.
- Adapted upstream's newly added `test_cute_dsl_mxfp8_moe.py` to the replacement kernel contract. Its two MXFP8 numerical tactic cases retain the 2688-wide ReLU2 workload and now exercise partial channel M256/M512 tiles at routed N128. The two W4A8 numerical tactic cases retain their 384-wide partial-channel workload. Removed the obsolete partial-N192 rejection test because those numerical cases now verify supported partial-channel execution. Replaced the removed legacy `is_valid_mma_tiler_and_cluster_shape` calls with the current FC1 `can_implement` checks for gated and non-gated channel widths; N192 remains rejected as an unsupported routed-token capacity. Kept upstream's `quant_mode="mxfp8"`, input validation, row-major scale conversion, default accuracy cases, and numerical references.
- Updated the unified runner's declared MX activation expectations to include SiTU. Replaced its obsolete W4A8 fused-only rejection test with SiTU/unfused acceptance for the two existing MX formats. The test remains in the existing support class; no standalone file or GPU matrix expansion was added.

## Validation

`audit-final-cleanup/.venv-cpu/bin/python rebase-20261026/check_test_integration.py` completed successfully; output is in `tests-integration-checks.json`, `tests-integration.stdout`, and `tests-integration.stderr`.

- 12 existing source-extracted tactic test invocations, including all 360 JSON roundtrips, passed.
- Six capability assertions passed against the real current FC1 adapter and core admission/resource arithmetic, with previously audited SDK byte-layout constant stubs.
- Both actual unified support checks accepted SiTU plus unfused finalize using real config dataclasses and Torch 2.13. Both MX formats still rejected SM107 when the architecture query was stubbed to Rubin.
- All three changed files parse. No retained fused-MoE test function was removed. After normalizing the requested `w8a8` to `mxfp8` spelling, every retained function AST is unchanged except the upstream Rubin feature-skip fixture. This preserves the prior focused selector coverage while inheriting Rubin unfused coverage.
- Ruff check, Ruff format check, and `git diff --check` passed for all three files.

The local runtime warns that NumPy is absent; no NumPy operation was requested. The harness source-extracts support methods to avoid importing CUDA extensions, so these checks do not claim full-package import, JIT compilation, or GPU numerical validation. The adapted numerical tests were not run on a GPU during this integration.
