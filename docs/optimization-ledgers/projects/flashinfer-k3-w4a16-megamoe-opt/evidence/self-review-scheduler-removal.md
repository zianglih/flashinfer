# Focused removal review

Reviewed `bacf4861..48fce528` after the earlier full candidate review. The
scheduler file is byte-identical to `a7103ae`; it is absent from the final PR
diff. Removed two scheduler-specific parameter rows and their single-boundary
helper. The four N32 parameter AST rows and zero-tolerance oracle remain
identical; static/atomic parametrization still gives eight logical EP2 cases.
The fallback D/E and activation branches are unchanged for every remaining
non-N32 row. `git diff --check`, focused pre-commit and commit hooks passed.
No confirmed new defect. Final GPU N32 qualification follows the GLM sweep;
no pass is inferred from earlier combined-source receipts.
