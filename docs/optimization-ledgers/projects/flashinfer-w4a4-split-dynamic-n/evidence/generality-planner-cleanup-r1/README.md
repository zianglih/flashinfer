# Planner storage-fit cleanup (unapplied)

This isolated follow-up factors repeated epilogue-scratch reservation and operand-ring fitting into two private helpers. It adds no module, planning object, public argument, or policy. The frozen planner and shared review checkout are unchanged.

- Base core SHA256: `8fd85e01b993660fa5fc815d3e7d504c535867eaaa8bb0008fa9e19a9ec4748f`.
- Candidate core SHA256: `c695546b82069bffdd4c37ef365645a6bdbdc20dbf7fc1cfcbd471e9b2bc3d23`.
- Patch: `cleanup-only.patch` (65 added / 51 removed lines). Two small helpers replace three scratch-selection loops and two resource-fit loops.
- CPU equivalence: 11,520 explicit K/depth/storage configurations and 450 automatic K/depth choices preserve results and ValueError text. All other module AST is identical. These checks use source-extracted constructors/storage methods with mocked SDK layouts; actual-layout formula agreement is separately established by the frozen planner SDK census.
- Static validation: Python compilation, Ruff lint, and Ruff format check pass. No GPU work was launched for this equivalent cleanup.

Reproduce from the project directory:

```bash
python3 scripts/generality_host/check_planner_cleanup.py
```

Wait for the planner performance decision before applying. The narrow two-CTA SF readiness experiment owns the shared core next; rebase the cleanup after its additional metadata byte term is captured.
