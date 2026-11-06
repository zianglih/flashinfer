# Benchmark and test simplicity review

Reviewed the nine changed benchmark/test files against `215f83cb`, starting from clean `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`. Read `CLAUDE.md` and the agent code-review guidance. No GPU work, new upstream tests, commits, or source clones.

## Change

Only `tests/moe/test_cute_dsl_fused_moe.py::TestTacticEnumeration.test_all_moe_tactics_pair_gemm1_and_gemm2_consistently` changes: expect the host cleanup's single `use_clc_scheduler` key instead of duplicate GEMM1/GEMM2 keys. Remove two standalone legacy-default assertions already covered by the exact dictionary comparisons. Keep the 360-tactic enumeration, explicit boolean axis, legacy Blackwell defaults, Rubin defaults/rejection, and geometry/K contracts.

## Reviewed and retained

- `bench_moe_deepseek.py`: format-specific CuTe/TRT setup is necessary for the distinct public APIs, scale layouts, and per-token activation recipe. The common routing, timing, dispatch, and table paths already avoid independent implementations. Leave all model, family, selector, explicit skip, saved-cache, timing, and formatting behavior unchanged. The longer autotune explanation is inherited upstream, so this pass does not add unrelated prose churn.
- Distributed/Frost benchmark preparation, `benchmarks/routines/moe.py`, and `tests/moe/utils.py`: retain the shared architecture-specific gated-weight interleave; it is required by the replacement Blackwell layout and keeps the existing Rubin layout.
- Capability and homogeneous-MX tests: the former channel-N192 cases must become channel-M/route-N cases for the replacement implementation. Partial tiles and two-CTA cases exercise real changed behavior.
- Unified/public MX tests: retain SiTU and unfused-finalize checks, public wrapper/function parity, and invalid-weight validation. Existing Rubin-specific rejection tests are unchanged.

## Validation

- Scoped pre-commit passed: `/opt/homebrew/bin/pre-commit run --files tests/moe/test_cute_dsl_fused_moe.py`.
- `git diff --check -- benchmarks tests` passed.
- All nine PR-changed benchmark/test files compile as Python source.
- Every benchmark file is byte-identical to `ed67c485`; this preserves table output, column order, EP defaults, routing/activation recipes, `include_activation_quant=False`, and native timing/cache behavior exactly.
- All other test files are byte-identical. AST comparison confirms that only the existing scheduler expectation method changed; the test-name list is unchanged.
- Hash-bound static receipt: `benchmark-static-checks.json` in this directory.
- Existing tactic-test execution belongs to the parent's final source validation after the host parser cleanup lands; this review makes no new GPU or full-pytest claim.

Files are unstaged. No further edits planned by this owner.

## Final user steering

The separate GEMM scheduler parameters and parser keys were preserved. The temporary expectation change is reverted. Every PR-modified benchmark and test file is byte-identical to ed67c485; no benchmark/test changes remain in this cleanup. See the final fields in benchmark-static-checks.json.
