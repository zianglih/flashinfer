# Read-only PR builder audit

Audited `build_pr_body.py`, `assemble_results.py`, `tools/run_full.py`, `make_deploy.py`, and the previous `swap-ab-full-rerun-20261027/pr-body-fresh.md` template. No source edits, GPU work, or public writes.

Builder source SHA256 at review: `b4bcd34364e59af35b1f1322054dbb8a2a691a248ccec5bd8a7aea2a11f3cc5b`.

## Requested small fixes

1. Bind assembled provenance to the loaded campaign config: assert its `config_sha256` equals the exact evidence/config.json hash and `source_heads` equals the config source heads. The builder already verifies current production bytes against the measured config, final commit/clean-tree identity, assembled output hashes, and shape counts, but those are two unjoined checks. A stale prior assembled directory with 44 rows / 416 measured cells can otherwise pass.
2. Replace inherited “For same-head non-swap controls” in the workload-command prose with the exact unchanged `e2728a290` control. The new assembler footnote already correctly identifies this control, while W4A16 remains pre-PR `002529e1`.
3. Remove one repeated native-A2 CSV introduction: the template's setup slice already includes it, and `native-a2-output.md` emits it again.

## Verified design and counts

- New native AUTO applies to swap-AB/TRTLLM; 15 unchanged control winner files are reused with receipt/source/cache/workload proof. All displayed timings come from the new C0/A1/A2/C3 logs; old timing JSON is not consumed.
- 8 new AUTO phases +46 frozen phases =54, with 442 AUTO medians and1352 frozen medians, each100 CUPTI samples. The smaller AUTO count is deliberate; previous full campaign had controls freshly autotuned too.
- Four model labels remain V3 EP8, V41F EP4, K3 EP8, N3U EP8. Summary has44 rows excluding1/2 tokens and9 same-dtype comparison columns. All-token cells are468 =416 measured +52 unsupported. Current swap-AB always unfused; legacy MX fused; unsupported K3 arms N/A; NV includes input quantization.
- Ratios use100*(sqrt(C0*C3)/sqrt(A1*A2)-1), with TRTLLM numerator from its A1/A2 medians. Raw output is verified original printed CSV, not regenerated from historical data or replaced by rounded summaries.
- The setup replacement accurately says candidate native AUTO is fresh and control winners are verified reuse. Scope text retains default legacy behavior, unchanged23 W4A16 tactics, shared360 swap-AB tactics, and manual-only sanitizer.
- Final validation text is intentionally supplied separately. It must distinguish the earlier51 accuracy-case result from the combined candidate's24 existing accuracy cases and96 exact static/CLC-PDL graph replays; no new sanitizer claim.

Final numeric artifacts are pending completion, so this is a builder/source audit rather than final data verification.

## Remediation readback

Parent addressed all three findings. Independent reread confirms config SHA + exact source-head map +54-phase guards, explicitly pinned e2728 command prose, and setup slicing before the A2 intro. Updated builder SHA256: `b4bcd34364e59af35b1f1322054dbb8a2a691a248ccec5bd8a7aea2a11f3cc5b`. No remaining builder finding from this review; final assembled-table arithmetic awaits completed evidence.
