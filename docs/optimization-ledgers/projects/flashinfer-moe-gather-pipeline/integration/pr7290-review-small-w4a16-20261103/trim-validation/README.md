# Narrowed reviewer-fix diff

User requested retaining only necessary edits. All changes remain unstaged.

- Restore the autotune test's original call/reference structure; add swap-AB
  parametrization, correct weight/finalize/reference layout, and clear the
  autotuner cache so enumeration cannot silently be skipped.
- Remove the extra cached second invocation and general reference rewrite.
  The functional API already executes the selected winner after `choose_one`
  (`flashinfer/fused_moe/cute_dsl/fused_moe.py:2136`).
- Reduce mixed-candidate activation cases to one gated and one non-gated type.
- Tag only new gated swap-AB manual views; preserve original untagged legacy
  views. Keep all six distinct layout-pack cases and the real preparation
  metadata assertion in the shared accuracy matrix.
- Remove the redundant metadata assertion in the unrelated explicit-tactic test.

Production/API/docs bytes exactly match the previously validated snapshot;
no kernels, tactics, benchmark inputs, or measured source bytes changed.
The diff shrank from +159/-42 (201 lines) to +115/-15 (130 lines).
Targeted pre-commit passed, including mypy, Ruff, and formatting.
Focused C3 validation is recorded separately under `c3/`; earlier full GPU and
benchmark evidence is preserved without modification.
