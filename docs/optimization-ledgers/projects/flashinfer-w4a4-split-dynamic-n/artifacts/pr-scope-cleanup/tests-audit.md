# PR 7290 test scope audit

Reviewed the three test-file diffs from base `a65d5b09e7e4c4c5c160b0161c48becd100b3970` to measured implementation `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` and the cleanup working tree in `flashinfer-pr-scope-review`.

## Cleanup

- Removed the new `TestKernelInputValidation.test_tactic_matches_weight_layout_architecture` monkeypatch/tripwire matrix. Existing input-validation tests remain.
- Removed the dedicated `test_gemm1_logical_m512_geometry` dtype cross-product. Folded the accepted M512/N128 two-CTA geometry and three invalid geometry cases into the existing `test_gemm1_n_tiling_guard` table.
- Replaced repeated W4A8 geometry assertions with equality to the shared Blackwell tactic set. Per-GEMM geometry checks remain in the existing tactic tests.
- Removed exact tactic-count assertions and duplicated geometry checks from the pair test; it still requires all five routing capacities and matching FC1/FC2 N dimensions.

No test function present at the base was removed. There are no newly added standalone test functions after cleanup. No edits to `tests/moe/utils.py` were necessary in this cleanup; its PR changes select the architecture-correct group16/group64 weight layout and must remain.

## Required retained adaptations

- K-tail test routing metadata and MMA shape now follow activation-on-B/token-on-N geometry, including N16 with 17 tokens and K64/K192.
- Tuner output-dtype interception follows the shared implementation's class and argument names.
- Existing tactic tests, explicit routing-geometry rejection, fixed numerical tactics, and host can_implement tables use the replacement kernel's supported geometry.
- Existing PDL forwarding tests were already present at the base and are not removed.
- Existing input validation, per-token activation-scale coverage, and all numerical accuracy tests remain.

## Checks

`pre-commit run --files tests/moe/test_cute_dsl_fused_moe.py tests/moe/test_cute_dsl_moe_can_implement.py tests/moe/utils.py` passed. Ruff lint/format, `git diff --check`, and Python AST parsing passed. An AST comparison found no base test-function names removed and no new test-function names remaining. GPU tests were not rerun for this cleanup.

The cleanup modifies two test files; GPU validation for the restored existing cluster-padding cases is delegated to the parent task.

## Existing cluster-padding coverage restored

The 8c1a adaptation of `test_finalize_handles_cluster_padding_and_partial_tiles` used N16/M128 one-CTA W4A4 tactics, so it no longer verified two-CTA channel padding despite the test name. The cleanup restores the original intended coverage with M256/(2,1), N128 for both FC1 and FC2. Hidden size384 leaves a padding CTA in the last channel tile; T129 with topk2 guarantees a partial routing tile. Both W4A4 cases explicitly disable fused finalize. The W4A16 cases are unchanged.

Focused GPU nodes (each loops H256/H384):

- `tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-tensor]`
- `tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a4-per-token]`

Scoped pre-commit and diff checks passed again after this adaptation. GPU results are owned by the parent task and are not claimed here.
