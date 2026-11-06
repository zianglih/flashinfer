# Final recorded-cluster pipeline analysis

`analyze_final_pipeline.py` is a CPU-only consumer of the existing native IKET JSON, correctness records, source closure, and native instrument-point audit. It does not capture or modify traces. The final capture must first be copied and bound to its matching original PMTRIG cubin by `audit_causal_instrumentation.py`.

```sh
python3 optimization/analyze_final_pipeline.py \
  --capture optimization/results/owned-r2-final-winner-1/final \
  --source optimization/retained_owned_r2 \
  --rank 2 \
  --instrument-binding-audit optimization/results/owned-r2-final-winner-1/final/instrument-binding-audit.json \
  --output-prefix optimization/results/owned-r2-final-winner-1/rank2-pipeline
```

Adjust only the audit path if the native audit was deliberately written into a separate new report directory. The helper refuses existing report outputs. Its default package hash is `a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29`, the owned R2 source at `55cd345d57ccc56327966201bd0725767a11593a`. The report records the source identity, input trace hash, metadata hash, tactic, and supplied binding-report hash.

The Markdown report and JSON/CSV contain:

- The three dispatch subsections, each required exactly once on CTA0/warp8, ordered inside `dispatch_exchange_counts_sync` by the existing structural validator. Both CTAs' first weight, decode and MMA markers use this same rank's `dispatch_wait_input_publication.end` anchor. CTA1 does not issue MMA and is reported as absent, not zero.
- FC1 and FC2 separately: MMA-control warp explicit weight-ready and activation-ready waits, asynchronous issue ranges, and the time from the latest of all 16 transform producer store/commit marker ends to the matching consumer weight-wait end.
- Decode-start and store-end skew across the two recorded CTAs and four transform warp groups. Work ordinal plus K identifies the join because phase/expert payload alone is not unique.
- Per-warp raw-ready wait, explicit TMEM-free wait, decode and store/fence/commit ranges. Group rows are arithmetic means of four individual warp timelines. Concurrent warp durations are never presented as elapsed GPU time.
- Unmarked time inside transform parents, with the inter-K gap shown as a subset. The retained source has zero raw readiness probes and two static TMEM readiness-probe calls: before the first K and after commit before the next K. These probes are outside the explicit free-slot marker. Neither named waits nor unmarked gaps are total TMEM stall time.

Interpretation order: first explain the dispatch subsections, then first-work offsets, then FC1/FC2 steady-state timing and producer skew. Compare same-K producer completion against consumer readiness, and inspect long outliers by work ordinal/K. A transform warp may wait for a future TMEM slot while the MMA warp waits for the current decoded tile; overlap alone is not evidence of redundant waits or deadlock. Marker windows include instrumentation and scheduling effects, and MMA issue is not MMA completion. Native generated-code observations and cold CUPTI performance remain separate evidence.

The JSON trace proves CTA/warp ownership, not lane uniformity. Lane safety is established by the owned source predicates and native instrument-point audit. This analysis covers one recorded cluster on one GPU while the full grid executes; it makes no cross-rank clock, full-grid occupancy, hardware utilization, or uninstrumented speedup claim.

CPU validation: `python3 optimization/test_final_pipeline.py --output <new-project-local-directory>` passed 14 synthetic/contract checks and all three historical rank2 traces. Evidence is in `final-pipeline-cpu-v2/summary.json`; synthetic times are explicitly not GPU results. The historical CLI regression additionally verifies exact source closure, matching capture metadata, matching native binding report, and refusal to overwrite output. Historical captures without dispatch subsections require the explicit compatibility flag and never receive an invented input-publication anchor.

Helper SHA256 at preparation: `d7cc12201b6b99fff2994179052bf51e11b3d4b9d4e7e346b0c6c87624fb8813`. The final capture passed this analysis: outputs are `results/owned-r2-final-winner-1/rank2-pipeline.*`, with the source-grounded interpretation in `rank2-interpretation.md` and the startup overlap intervals in `rank2-startup-overlap.json`.
