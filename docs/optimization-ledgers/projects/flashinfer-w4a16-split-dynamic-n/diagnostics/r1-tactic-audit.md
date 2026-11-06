# R1 tactic audit and bounded diagnostic plan

Superseded diagnostic selection: see `unfused-r1-r2-tactic-audit.md`; queue T8/T4096 plus one common-N128-cache T16384 pair.

Primary evidence is the saved R1 unfused pair plus the separate baseline T16384 appendix. All row-cache SHA256 values were checked; each row has exactly one matching W4A16 token profile. Compared rows have identical input shapes, runner extras and routing histogram summaries. No GPU work was launched.

Full tactic notation below is M/N/K, cluster and raster-along-M for FC1 and FC2; equality compares the entire two-stage tactic, not N alone. All selected tactics have K256 and raster=True.

| Tokens | Before µs | After µs | Speedup | Same full tactic | Before tactic | After tactic |
| ---: | ---: | ---: | ---: | :---: | :--- | :--- |
| 1 | 34.2730 | 34.0160 | 1.007555× | True | FC1 128/8/256 c1x1 r1; FC2 128/8/256 c1x1 r1 | FC1 128/8/256 c1x1 r1; FC2 128/8/256 c1x1 r1 |
| 2 | 40.3840 | 39.7925 | 1.014865× | False | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 | FC1 128/16/256 c1x1 r1; FC2 128/16/256 c1x1 r1 |
| 4 | 54.8640 | 54.4165 | 1.008224× | False | FC1 128/16/256 c1x1 r1; FC2 128/16/256 c1x1 r1 | FC1 128/32/256 c1x1 r1; FC2 128/32/256 c1x1 r1 |
| 8 | 68.6730 | 69.7610 | 0.984404× | False | FC1 128/16/256 c2x1 r1; FC2 256/16/256 c2x1 r1 | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 |
| 16 | 76.8970 | 76.2880 | 1.007983× | True | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 |
| 32 | 109.7130 | 109.1370 | 1.005278× | True | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 | FC1 128/8/256 c2x1 r1; FC2 128/8/256 c2x1 r1 |
| 64 | 143.2010 | 141.9375 | 1.008902× | False | FC1 256/16/256 c2x1 r1; FC2 256/16/256 c2x1 r1 | FC1 128/16/256 c1x1 r1; FC2 128/16/256 c1x1 r1 |
| 128 | 145.8900 | 144.1300 | 1.012211× | False | FC1 256/16/256 c2x1 r1; FC2 256/16/256 c2x1 r1 | FC1 128/16/256 c1x1 r1; FC2 128/16/256 c1x1 r1 |
| 256 | 152.7530 | 151.4895 | 1.008341× | False | FC1 128/16/256 c2x1 r1; FC2 256/16/256 c2x1 r1 | FC1 128/16/256 c1x1 r1; FC2 128/16/256 c1x1 r1 |
| 512 | 159.0090 | 156.9455 | 1.013148× | False | FC1 128/32/256 c2x1 r1; FC2 256/32/256 c2x1 r1 | FC1 256/32/256 c2x1 r1; FC2 256/32/256 c2x1 r1 |
| 1024 | 174.8340 | — | — | None | FC1 256/64/256 c2x1 r1; FC2 256/64/256 c2x1 r1 | — |
| 2048 | 211.6820 | — | — | None | FC1 256/64/256 c2x1 r1; FC2 256/64/256 c2x1 r1 | — |
| 4096 | 308.8670 | 295.1390 | 1.046514× | False | FC1 256/128/256 c2x1 r1; FC2 256/128/256 c2x1 r1 | FC1 256/192/256 c2x1 r1; FC2 256/192/256 c2x1 r1 |
| 8192 | 627.3330 | 573.9090 | 1.093088× | True | FC1 256/128/256 c2x1 r1; FC2 256/128/256 c2x1 r1 | FC1 256/128/256 c2x1 r1; FC2 256/128/256 c2x1 r1 |
| 16384 | 1183.9945 | 1199.2750 | 0.987259× | True | FC1 256/128/256 c2x1 r1; FC2 256/128/256 c2x1 r1 | FC1 256/128/256 c2x1 r1; FC2 256/128/256 c2x1 r1 |

Of the 11 retention rows, identical full tactics occur at **[16, 32, 8192, 16384]**, with descriptive geometric speedup **1.022601×**. The seven changed-tactic rows have **1.011538×**. These partitions explain selection effects; they do not exclude any point from retention.

## Three consequential rows

1. **T8: changed-tactic regression.** Before 68.6730 µs, after 69.7610 µs (0.984404×). Baseline uses FC1 M128/N16 and FC2 M256/N16, both cluster2x1; candidate selects M128/N8 for both. The actual maximum local expert count is only 2. Replay each saved tactic cache on both source revisions. The baseline-cache pair asks whether the original tactic regresses under dynamic N; the candidate-cache pair distinguishes a source improvement/regression from the new AUTO choice.

2. **T4096: largest gain involving a tactic change.** Before 308.8670 µs, after 295.1390 µs (1.046514×). Both GEMMs move from M256/N128 to M256/N192, cluster2x1. Local expert counts range 81–147, median 117. N192 covers these experts in one logical token tile while N128 has partial second tiles for experts above 128; runtime width reduction can make N192 competitive. This is a source-derived hypothesis, not measured attribution. Replay both saved caches on both sources to distinguish a faster fixed kernel from the newly useful tile choice.

3. **T16384: identical-tactic regression, conditional.** Before 1183.9945 µs, after 1199.2750 µs (0.987259×), both FC1/FC2 M256/N128 cluster2x1. If the already planned R2 confirms a consequential regression, replay the baseline appendix cache on both sources. One cache is sufficient because the selected full tactics already match.

T8192 is the largest gain (1.093088×) and both sources already select identical FC1/FC2 M256/N128 cluster2x1. The planned R2 provides its next consistency check; no extra T8192 diagnostic is proposed initially. T1/T2 do not drive retention; unpaired T1024/T2048 remain supplemental.

## Commands, after the primary campaign releases GPU0

Copy the existing `scripts/bench_fixed_tactic_row.py` and new `scripts/run_fixed_diagnostics_r1.sh` to the remote effort workspace. These are secondary measurements only. The command refuses to overwrite or rerun existing diagnostic output. It uses unchanged saved R1 caches, fresh processes, do_autotune=False, native cold-L2 CUPTI100/10 warmups and records the actual tactic/cache hash.

```bash
cd /workspace/flashinfer-w4a16-split-dynamic-n
bash scripts/run_fixed_diagnostics_r1.sh 8 4096
# Only if the planned R2 leaves the T16384 regression consequential:
bash scripts/run_fixed_diagnostics_r1.sh 16384
```

T8/T4096 each use four source/cache combinations, in baseline→candidate order for baseline cache and candidate→baseline order for candidate cache. T16384 uses one two-source pair. Results stay under `diagnostics/r1-crossover/`; no primary file is changed, no tuning runs, and no primary AUTO row is rescheduled.

For each cache, require matching cache SHA256, selected tactic, input/histogram/software and intended source heads before computing baseline/candidate. Do not mix these diagnostic medians into the AUTO aggregate. If R2 changes the interpretation, narrow or cancel the proposed diagnostics rather than launch all three mechanically.

## Retention boundary

Use full 11 / decode 8 / prefill 3 AUTO results, including every regression. Review planned repeat consistency and fixed-tactic evidence without a fabricated numeric cutoff. Marginal gains explained entirely by changed selection do not establish a kernel improvement; a useful improvement may instead be a tile choice becoming viable, but that claim needs the crossover evidence. Continue rigorous correctness/sanitizer only after retaining the optimization.

Full cache keys, tactics, file hashes and input records are preserved in `r1-tactic-audit.json`.
