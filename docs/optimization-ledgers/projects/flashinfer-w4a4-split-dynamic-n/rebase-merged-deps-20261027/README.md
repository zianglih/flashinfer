# PR #7290 rebase onto merged dependencies

- Previous head: `ee88cf2acc59748a64ee2614fed2f16f05f67988`.
- New upstream base: `002529e17b22567a071091053c6c4dc2a55e050e`, including merged #7196 (`03d7f4a`) and #7501 (`fb022756`).
- Rebased head: `1496b557f9b606f3a0bb36bcebf5293d3e11555a`; 23 retained commits replayed, followed by one integration fix.
- Local pre-rebase backup: `archive/7290-before-merged-deps-20261027`. No additional review checkout was created.

The textual conflicts were three tuner tuple-unpack updates; the upstream `_tactic_ok` docstring was preserved. The integration fix threads the prepared gated-row size through the private W4A16 compile cache/kernel, retains the upstream 64-to-16 decode composition on Rubin, and updates only the split adapter of the shared exact reference for Blackwell 16-row versus Rubin 64-row storage. Dense and MegaMoE reference contracts are unchanged.

The retained shared blockscaled core, FC1 adapter, packed combine and per-token quantizer are byte-identical to the pre-rebase head. The updated upstream CUDA quantization headers are inherited. Validation uses source-owned include/csrc links and a fresh persistent native/DSL cache namespace; previous persistent compilation caches are preserved.

## Evidence

- [Rebase context and old refs](rebase-context.json), [range diff](range-diff.txt), [final source checks](source-validation.json).
- [#7196 semantic audit](7196-audit.md), [#7501 arithmetic/reference audit](7501-audit.md).
- [Full PR-diff scoped pre-commit](pre-commit-pr-diff.log): passed; all 26 changed Python files parse.
- [GPU validation artifacts](validation/): 104/104 existing tests pass (39 W4A16 exact, 16 unfused split, 49 quantization); zero failures/skips. A separate B300 legacy64 layout check matches all 4,352 BF16 output elements exactly. Rubin hardware and sanitizers were not run; no fresh performance claim.
- [Published PR body](pr-body.md), [component LOC](pr-loc.json), [preserved fenced-output hashes](pr-body-receipt.json).

The six raw benchmark tables remain attributed to `f7182d5c`; the rebase and merged native quantizer changes have not been benchmarked. Historical source IDs and raw outputs are deliberately unchanged.

Published with explicit force-with-lease against the observed remote heads. During validation, upstream added unrelated GDN benchmark commit `002529e1`; the final replay includes it. The full PR diff is byte-identical to the initially validated replay at `4172db64` on `fb022756`. Focused GPU validation and PR body publication are complete. GitHub confirms head `1496b557`, base `002529e1`, draft status preserved, and `MERGEABLE`; the body matches the saved draft exactly. See [publication receipt](publication.json) and [final fenced-output audit](final-body-checks.json).
