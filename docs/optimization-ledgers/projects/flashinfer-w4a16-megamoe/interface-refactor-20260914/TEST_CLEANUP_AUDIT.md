# Test audit and cleanup after b83cbedb

Reviewed the full PR test diff against `8c94` and the interface changes in `b83cbedb`. This subtask changed only `test_knob_cache.py`, `test_mega_cuda_graph.py`, and `test_mega_layer_validation.py`; `test_fused_quant_stage.py` was audited and kept. No production edits, commits, pushes, or GPU actions were performed by this subtask.

## Changes

- Replaced the eight-way no-warmup graph product with four exact scenarios: NVFP4/W4A16, each with the original unallocated/nonempty case and the allocated/empty regression. Added `stage.assert_not_called()` so the test verifies the error precedes staging, rather than accepting a later reducer error. The original upstream test case is retained.
- Replaced four cached geometry combinations with three useful factory cases: original NVFP4 M256 cache control, W4A16 partial M128 cache lookup, and W4A16 partial M128 explicit override. The explicit case records a different cached flag value, proving both tile normalization and explicit-cache bypass. Removed redundant added M128-NVFP4 and M256-W4A16 cases.
- Replaced repeated graph-helper config construction with a keyed config-class map and common arguments. Unknown modes cannot fall back to another backend.
- Made the global-scale validation test's split branch explicit; unknown backend names now fail the config map instead of silently using split. Both scale fields and all three backend contracts remain covered.

## Counts

Counts are static parameter expansion from the real test AST, not pytest collection or execution. No test functions were removed. `test-cleanup-counts.json` contains full per-function details.

| File | Upstream 8c94 | Before b83cbedb | After cleanup |
|---|---:|---:|---:|
| test_knob_cache.py | 10 | 13 | 12 |
| test_mega_cuda_graph.py | 8 | 18 | 14 |
| test_mega_layer_validation.py | 26 | 40 | 40 |
| test_fused_quant_stage.py | 11 | 16 | 16 |
| Total | 55 | 87 | 82 |

The cleanup removes five added parameter combinations while strengthening the exact regressions. It is not a line-count reduction: the three edited files add 30/remove 27 lines relative to b83cbedb, because explicit-cache bypass and pre-staging assertions add coverage. `test-cleanup-source.json` records source hashes and both diff baselines.

## Deliberately retained

- Global-scale support checks cover W4A4, W4A16 and split, with each FC1/FC2 field separately; this guards the two public fields from being silently ignored.
- W4A16 activation/routing dtype and forbidden activation-scale inputs cover distinct precision/contract boundaries.
- BF16 staging tests retain bitwise activation/routing comparison, disabled-path and enabled-path dispatch assertions, dirty tail masking, empty/refill sequencing, and both ID widths. The environment-toggle regression does not merely compare equal outputs; it verifies which implementation executes.
- Graph replay numerical assertions and all reference/tolerance code are unchanged.
- The unrelated upstream `test_mega_layer_prepare_workspace_requires_dist` is unchanged.

An inherited weakness in the existing staging cache test remains: its description mentions same-pointer input mutation, but `_make_batch` allocates fresh inputs each round. It still covers repeated staging and token-count changes; it does not deterministically prove a launch-argument cache hit. Reported to root rather than expanding this cleanup into an unrelated rewrite.

## Validation

Ruff lint, Ruff format checks, Python syntax compilation and `git diff --check` pass for the four audited files. No real pytest or GPU claim is made for this cleanup by this subtask. Root is independently validating b83cbedb on the new C2 CUDA13.2 B300 box; those results must remain attributed to that commit until the changed tests run there.
