# Routing-preparation overlap performance trial

The frozen772 candidate passed its bounded capture, strict1024-token random/skewed GLM5 EP4 all-tactic/O2/O3 eager/graph, and queued replay gates before this trial. These are not full-matrix or sanitizer qualifications.

This trial uses a fresh same-node7dc baseline then772 candidate on hu-pdx-7. It measures the fully fused public API with unchanged benchmark/worker/timer/process-owner/comparator/environment helpers. Source manifests, environment, GPU idleness and process closure are gated. All14 token rows and all100 samples per row are retained. Retention aggregate covers8–8192; one serial pair does not remove temporal drift.

- Bounded qualification: ../qualification/BOUNDED_VALIDATION.json
- Preparation review: independent-helper-review.json
- Exact workload and exclusions: PLAN.md and remote-command.json
- Driver delta: run.py.diff
- Current process: benchmark-launch.json, supervisor/PGID73447
- State: Running A1(retained7dc) then B1(routing-preparation772); no performance conclusion or promotion yet.

## Completed result

Independent audit passed: all2,800 timing samples,112 finite BF16 exact cross-arm outputs,208 frozen source files, all90 archive members and clean per-arm/source/process closure. Source/control/tactics match the declared method; all14 rows select the same tactics.

The8–8192 geometric ratio is **0.999078×** (4/11 rows faster, including an effectively tied8-token row).1024/2048/4096 improve1.27%/1.61%/2.15%;16/32/64/256 regress. This does not demonstrate a material overall benefit for the added transport orchestration. Retain7dc as current best; preserve772 as an unpromoted experiment. A serial pair does not eliminate temporal drift.

Full medians,MADs and ordered quarters: [independent audit](independent-timing-audit.md).

Audit SHA256: `130e549b0758359e9cc858c9537b54f6f17837e0c8b9aac47bfecafe53d3f2e8`. Archive SHA256: `0163b202e5f0517dbb5f49c54a0fc96acac49e9022e5d627b0d7750f68cd0dc5`.
