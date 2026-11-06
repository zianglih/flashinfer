# Initial operand-ring weight cache priority

**Rejected; review worktree/local branch retired.** Experiment based on `c1ac8ce7341039db65195b99445fcdeb193cf226`.
The exact source/patch are preserved under `r1/` and `retirement/`.
Canonical source remains clean. See [final results](RESULTS.md).

Current revision is **R1**, source `585aaeacc331b6d56e8376e63902262644c41e07ae94d1c7f35fbe1e22a4b015`.
Its artifacts and scoped hook log are in `r1/`. R0 source/patch/proof are retained
under `r0-preserved/`; its qualification failure remains in `qualification/`.
R0's `cutlass.select_` result failed the CuTe `cache_policy` Int64 type check.
R1 only substitutes the typed ternary idiom already used by `weight_cache_hint`.

`load_weight_stage` selects FIRST for `producer.count < self.num_stages`
inside the existing `enable_pdl and prefetch_weights_before_wait` compile-time
condition, then uses the existing route-aware hint. Weight payload and SFA
copies share this selection. Public construction enables that condition for
non-gather FC2 with PDL; FC1 and PDL-off specialize away the addition.

This counts the initial lifetime ring fill, including short-K work-tile
transitions. It does not observe the exact time payload dependency completes.
No producer state, wait, arrival, expected-byte count, copy address, tactic or
API changes. Existing comments and license are preserved. The paired-error
quantizer is not included. The new use of `producer.count` may materialize a
counter and compare/select. R1 exact/native qualification passed three pairs:
affected FC2 adds two/three static non-NOP instructions with unchanged registers
and zero local memory; all seven unaffected images are byte-identical. See
[the native result](RESULTS.md). R0 reached compilation but no affected FC2
native image. Performance remains pending in the separate frozen screen.

This is an independent, unretained cache-policy experiment. The isolated
paired-error quantizer diagnostic also regressed without FC2, so FC2 overlap
is not an established explanation of that rejected candidate's loss.

History and the publication argument are in
[the bounded audit](../../audits/startup-weight-cache-priority-c1ac.md).
Constant FIRST/NORMAL failures remain separate evidence.

`r1/source_proof.py` reproduces `r1/source-proof.json`, `r1/candidate.patch` and the
frozen source copy. Removing exactly the seven added lines restores the full
retained source byte-for-byte and AST-for-AST. Git metadata stays inside the
project. Scoped `pre-commit run --files
flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py` passed every
applicable hook, including mypy, ruff check and ruff format; `git diff --check`
and Python AST parsing passed. See `r1/static-checks.json`.
