# Integrated planner storage-fit cleanup

Applied only to the shared review core, on the frozen narrow two-CTA candidate. The new SF readiness metadata term is passed through automatic K selection and final operand stage fitting. Scratch reservation and capacity fitting each have one implementation. There is no new module, planning object, API flag, or policy.

The before/after CPU equivalence check covers 14,976 stage configurations and 810 automatic K/depth choices, including 3,456 narrow two-CTA stage cases and 360 narrow two-CTA automatic choices. Results and errors match; all other module AST is identical. SDK layout sizes are mocked from the existing stage-size formula here; actual layout agreement belongs to the separately captured planner/narrow gates.

Python compilation and scoped repository pre-commit pass. No GPU work was launched for this equivalent cleanup. The complete integration snapshot also contains the root-owned sole-warp quantizer publication change, separately identified in source.json and excluded from this equivalence claim. The other 84 source files exactly match the frozen narrow candidate. Combined GPU validation is pending.

```bash
python3 scripts/generality_host/check_planner_cleanup_narrow.py
```

`cleanup-only.patch` is the isolated refactor. `source.json` and `source.patch` capture the integration-only combined candidate. Production and prior frozen receipts are unchanged.
