# Retained9037 full EP/TP refresh

Source `9037f6d46fcb45eac04be04c182104336c8b1e7c`. All31 jobs /62 phases /468 candidate cells /93,600 strict CUPTI samples finished. All514 source files equal canonical Git blobs. All candidate cells, including W4A16, are fresh; existing historical baseline values are unchanged.

| Mode | Decode4–64 | Middle128–512 | Prefill4096–16384 | Overall4+ |
|---|---:|---:|---:|---:|
|EP|+1.48%|+0.64%|-0.29%|+0.77%|
|TP|+1.63%|+4.54%|+15.49%|+6.05%|

Percentages compare geometric means of two candidate and two saved d35 phase medians. Historical controls use another B300 instance: this is a scoreboard refresh, not a new causal same-GPU comparison. Tokens1/2 are measured but excluded from displayed tables and aggregates. All five backend formats enter the aggregates.

- Runtime guards: 62 phase receipts; 1088 loaded MoE observations, all0 local bytes and unchanged compile options. This excludes native quantizer resource claims.
- Row validation:468 fresh /0 reused candidate cells;396 displayed, including60 negative cells. Both EP/TP external tables refresh same-dtype values while preserving9 columns, unsupported cells and fused marks.
- Timing telemetry: all3744 quartile windows observed; stock clocks unchanged. Maximum candidate A-A spread7.5227%. All repeats retained without best-of selection.
- Artifacts: 109,330,521 archive bytes, 2,602 hash-verified result files. Per-job archives and fetch receipts preserve provenance.
- GPUs3/4/5/6/7 released after verifying all workers complete and idle. No sanitizer, no baseline rerun, no GitHub writes.

## Artifacts

- `publication/body-draft.md`: current final-state PR body with asset placeholders for parent publication.
- `publication/report/cells.csv`: all468 paired historical/current medians.
- `publication/report/{ep,tp}-table.md`: full4+ table.
- `publication/plots/fc1-gather-vs-pr-head-{ep,tp}.{png,svg}`: full heatmaps, visually inspected.
- `publication/external/{ep,tp}/summary-table.md`: TRTLLM/non-swap comparisons.
- `publication/report/raw-a2-compact.md`: eight finalA2 panels.
- `publication/validation-receipt.json`: source, data, table, plot and body validation.
- `largest-historical-gaps.json`: absolute gaps and repeat spreads for follow-up diagnosis; not causal source attribution.
