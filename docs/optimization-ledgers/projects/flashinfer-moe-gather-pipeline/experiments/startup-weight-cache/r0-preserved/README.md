# Initial operand-ring weight cache priority

Active, unretained experiment on `c1ac8ce7341039db65195b99445fcdeb193cf226`.
The sole unstaged source is in `../../flashinfer-startup-weight-cache-review`,
branch `codex/startup-weight-cache`. Canonical source remains clean.

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
counter and compare/select; native instruction/register and timing effects
remain unqualified. No GPU work has run for this candidate.

History and the publication argument are in
[the bounded audit](../../audits/startup-weight-cache-priority-c1ac.md).
Constant FIRST/NORMAL failures remain separate evidence.

`source_proof.py` reproduces `source-proof.json`, `candidate.patch` and the
frozen source copy. Removing exactly the seven added lines restores the full
retained source byte-for-byte and AST-for-AST. Git metadata stays inside the
project. Scoped `pre-commit run --files
flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py` passed every
applicable hook, including mypy, ruff check and ruff format; `git diff --check`
and Python AST parsing passed. See `static-checks.json`.
