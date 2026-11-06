# Test conflict resolution

Compared current rebase worktree against upstream `e29bf6d52` and pre-PR base
`002529e17`. Only `tests/moe/test_cute_dsl_mxfp8_moe.py` was edited by this audit.

- `_run_kernel` retains upstream's runtime `clamp_limit` and the PR's `swap_ab`
  selector. Activation selection is kept in the shared input dictionary, avoiding
  duplicated `activation_type`/`output_dtype` keyword arguments.
- Legacy calls keep fused finalization and the unchanged ClampedRelu2 runtime
  tensor. Swap calls retain unfused finalization and bit-exact oracle assertions.
  No unsupported swap-AB ClampedRelu2 test combination was added.
- All new upstream functions in both MXFP8 and general CuTe DSL suites are
  AST-identical after the rebase resolution. No upstream function disappeared.
  The general suite's nine clamp helper/test functions are unchanged.
- Python AST parse and scoped `git diff --check` pass. Runtime qualification is
  delegated to the C3 test campaign; these static checks are not GPU validation.

Machine-readable comparison: `test-conflict-audit.json`.
