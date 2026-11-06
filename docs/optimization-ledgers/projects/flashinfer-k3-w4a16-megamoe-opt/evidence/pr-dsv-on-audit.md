# Published DSV table audit and scheduler-removal body plan

Audited `PR_BODY_DSV_ON_UPDATE.md` against `evidence/cross-model-validation-dsv-complete-v1.json` and the saved publication receipt `evidence/pr6277-published-dsv-on-table.json`. Body SHA256 `3e8d93d4b55d30ab1cd48792b4f1d94a0d0683ae16f34de3d0ba44803337157a`, 51,977 bytes. Read-only for repository, publication and GPU; this note is the only new artifact.

## Published table

No substantive numerical or protocol issue found:

- The receipt body is byte-identical to the local body. All13 token rows match the strict report's BEFORE/candidate medians to4 decimals, ratios to5 decimals, and selected tactic identities exactly.
- GM all11=1.0017767876, decode=1.0015127630, prefill=1.0024811937 correctly round to the displayed values. T32 latency increase is10.4018565%. All13 candidate winners belong to final16; actual measured selection used24.
- Both recorded arms use AUTO, 8GPU/EP8, 100 CUPTI samples, 3 warmups, one process group/sweep, PDL on, fused reduction off, FC1 routing weights off, same model metadata and benchmark overlay. The strict report separately validates all104 rank-winner records. The original BEFORE remains a7103 source plus its model-driver overlay.
- Scheduler-OFF is never called fixed-tactic in this body. The only remaining “fixed” column describes the earlier K3 residual-prefix screen and remains accurate. The new pending comparison is AUTO24, and the body makes no causal claim from the ON table.

Two small wording clarifications for the next body update:

1. Replace “Both arms keep FC2 routing weights” with “Both arms apply routing weights in deterministic combine.” That is the precise existing `apply_topk_in_fc1=False` contract.
2. Replace “T64–512 improve by1.9–4.3%” with “T64–512 latency falls1.9–4.3%.” The numbers are latency reductions; speedup-percentage gains reach4.5%.

## If the scheduler change is removed

Make the final body describe the retained source and recompute evidence from the chosen arms; do not merely switch a label:

- Remove FC1-prefix reuse from the opening scope and the Scheduler design bullet. Describe original scheduler preservation under unchanged contracts if useful. Keep N32/M128, native SiTU, model presets and the immutable decoder contracts.
- Main K3 layout can remain the user-requested BEFORE/native/+residual/full-AUTO comparison. If retaining the residual column as history, label it “+ residual (historical fixed)” and state that it was not retained. Do not reintroduce fixed-N32/M256-only columns or the M128-axis section. Full-AUTO must use the selected OFF capture and its actual selected tactic for every token. The simpler alternative of removing historical residual evidence needs an explicit parent editorial decision.
- Replace full-AUTO medians, speedups, geometric means, winners, raw arrays and hashes with the chosen OFF arms. K3 ON `expanded-auto-v1` and DSV ON `dsv41-flash-expanded-auto-v1` remain historical evidence, not the retained implementation's final performance. Do not pool ON/OFF samples or reuse ON-selected tactics in an OFF row.
- Both pending OFF captures independently use the same **AUTO24** catalog/order. This is an AUTO policy comparison, not a fixed-tactic causal scheduler estimate: selected tactics may differ. Keep scan24 versus final16 separate and recheck all13 OFF winners' membership before saying the narrowed catalog retains them.
- Update the current commit and kernel source-map statements. A restored scheduler no longer matches the scheduler bytes in ce03 or the combined/M128 gates. Those exact-gate reports remain historical passes with their tested source identity; do not claim the new assembled source was tested by a previous gate. The original scheduler was already upstream, but that does not manufacture a new exact-gate receipt.
- Baseline restoration becomes seven changed kernel/tuner files if the scheduler is byte-identical to a7103, rather than the current eight-file list. Preserve model-specific driver overlays and current benchmark hash. Update changed-file/static-check counts only from fresh receipts, not by inference.
- K3 ON/OFF source differs in driver bytes (old K3 driver versus new DSV-capable driver), scheduler, and the documented kernel comment change; DSV ON/OFF differs only in scheduler. Keep the strict normalized fixture/source contract rather than calling both pairs literal one-file source A/Bs. Current OFF source scheduler hash is `9edeb7437d8ee49ae50e0b87be39aaa056e54140beb02e94c5fc3bc4ac82d0df`.

## Concrete renderer changes required after the decision

`runner/render_pr_cross_model.py` currently takes K3 full-AUTO from hardcoded `expanded-auto-v1`, checks existing template tactic columns against it, and inherits summary numbers/prose from the template. To render OFF correctly, add an explicit chosen K3 arm/policy and rebuild both K3 tables and summary from validated captures. Update the public raw export arm list likewise; all historical captures stay local. Validate selected-tactic membership in the final catalog separately from recording its identity.

DSV already reads the actual candidate arm/count from the cross report, but `runner/summarize_cross_model.py` currently describes any non-default DSV arm as final16 in its pending policy/selector prose. An OFF AUTO24 arm needs its actual count/policy from the sealed manifest/report, not inference from its name. This was reported to the benchmark agent.

Do not regenerate/publish a final-retention body until complete OFF results and the parent's scheduler/catalog decision exist. Preserve all13 points, excluding only T1/T2 from retention aggregates. No new source edit, compilation, test or GPU run is prescribed by this audit.
