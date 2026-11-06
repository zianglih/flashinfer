# Future native-qualification controller

For the next paired swap exact/native probe, copy `paired-native/run.py` into the new experiment's `qualification/run.py` instead of copying a sealed historical controller. Keep the existing matching `harness/`, new plan, source/guard manifests and recovery receipts beside it, as before. The controller derives its output directory from its copied location; it does not point at a previous evidence leaf.

This is the CLC qualification controller with only two-arm source verification scheduled concurrently at the existing preflight and postflight boundaries. Both 13,245-file inventories still receive their original byte-level SHA checks; every failure remains fatal. Native preflight, caches, exact cases, capture/resource guards, subprocess behavior and receipt fields are unchanged. It introduces no GPU or benchmark policy.

The inherited plan/case selection and any explicitly requested control-reuse provenance must still be prepared for the new experiment. Do not run the template directory itself, copy old results into a new run without the existing reuse proof, or modify a sealed/active controller to adopt this change.

Evidence and measured CPU-only verification timings: `../../audits/iteration-speed-tooling/`. No source inventories, historical controller copies, production repository files or active harnesses were edited.
