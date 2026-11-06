# Blackwell comment/docstring pass

Reviewed the full Blackwell PR diff against `215f83cb` on review base `54f5c682`. Only two recognized docstrings changed, left unstaged in `flashinfer-comment-review-20261027`:

- `moe_unpermute`: restore the upstream wording and line wrapping of the still-correct W4A16/metadata-read ordering sentences. Keep the new blockscaled routing-publication and rounding contracts; the former FTZ and pre-wait-routing claims are no longer accurate.
- `_configure_pipeline_storage`: remove the new aside about Rubin's separate implementation. Keep the SM100 capacity and explicit-stage-depth description.

The previous cleanup already restored the original pipeline helpers/comments and utility descriptions. No further rewrites are justified there. The new TMEM ownership, SF publication/join, shared-empty ring, CLC, PDL, native-fragment layout and rounding explanations remain intact. The old kernel's gather/operand-layout descriptions do not describe the replacement and were not restored. Headers were not changed.

`check.py` verifies all ten assigned Blackwell Python files against `54f5c682`. It removes only the first string-expression statement recognized by `ast.get_docstring` in modules/classes/functions, then compares the entire executable AST. All other constants (including inline PTX), operations, signatures and control flow are preserved. The check and `git diff --check` pass. No runtime tests or GPU work are needed for this documentation-only change.
