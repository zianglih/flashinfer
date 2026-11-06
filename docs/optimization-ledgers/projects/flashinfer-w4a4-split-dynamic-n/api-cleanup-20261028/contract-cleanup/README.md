# PR7290 unpublished-contract cleanup, 2026-10-28

Current review changes remain unstaged in the canonical `flashinfer/` checkout on `17bff619c`. This supersedes the earlier companion-cache proposal in the parent directory.

## Current contract

- Swap-AB tactics have one five-field format: `(route_tile, gemm1, gemm2, (fc1_k_steps, fc2_k_steps), use_clc)`. The explicit default uses `(None, None)` for resource-derived K depth and `True` for shared CLC. The 360 enumerated candidates and extracted parameters are unchanged. Three-/four-field development formats and prefix matching are removed.
- Cache identity retains the semantic `swap_ab` distinction; the `blockscaled_route_n_v5` development marker is removed. JSON list normalization remains necessary for the current cache representation.
- Benchmark `--cache` is a managed cache directory for all backends, with context-scoped policy identities for both tuning and replay. There is no legacy JSON bridge or companion directory. Native timing modes are inherited; CuTe MX graph profiling remains explicit. The shared v2 tuner races the untuned default along with candidates. Fresh tuning may therefore select a different winner; no published measurements are relabeled as current-source measurements.
- Removed unused `PipelineCpAsyncUmma.empty_owner` and custom `PipelineTmaUmma.defer_sync` additions; both classes exactly match the branch base. Active `PipelineUmmaAsync.defer_sync` remains intact.
- FC1 CLC is a boolean with explicit `True` default throughout private dispatch, removing the redundant `None` normalization.
- Removed the remaining prepared-weight mode tags in the distributed benchmark and unified test fixture after the user removed the layout assertion. Explicit execution and preparation mode options remain; matching layout is the caller's responsibility.
- Published non-swap functionality, W4A16 group64 handling, current untuned execution defaults, and required dependency/data-layout capability handling remain supported. Upstream functional autotuning arguments are untouched.

## Validation

Affected-file pre-commit (including mypy and Ruff), syntax, and diff checks passed. Both existing functional API definitions are AST-identical to the retained head. CPU checks compare all 360 generated tactics and parameter dictionaries, 361 JSON roundtrips, 1,440 stale-format rejection cases, and the unchanged 23 upstream W4A16 tactics. The real generic tuner/cache probe passes 10 grouped checks covering directory persistence, policy isolation, fresh-process replay, memory-only behavior, and profiling disabled during measurement. Device/profiler utilities are mocked in that probe; no GPU capture, numerical, performance, or sanitizer validation was run.

No staging, commits, pushes, or PR-body changes. Detailed evidence is in `tactic-check.json`, `autotune-context-cpu.json`, and `receipt.json`.
