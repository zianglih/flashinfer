# Performance evidence ledger

The published headline is the fresh main68→7dc pair on replacement hu-pdx-9. Detailed samples, per-rank tactics, MAD, quarter medians, source/environment/process provenance and exact-output checks are retained in `independent-timing-audit.json`, its Markdown table, and `collected-perf-ab1/`. This ledger does not replace those raw records.

- `pr8-before.json` preserves the previous published incremental04/1ad/7dc table and full body.
- The older same-node incremental table remains at `../input-stage-fusion-compile-warmup/independent-timing-audit.json`; its ratios are not mixed into the new headline.
- Rejected cache-hint and three-WG trials remain under `../input-stage-source-cache-hint-compile-warmup/` and `../input-stage-multiwg-retrieve/`, with complete tables and retention decisions.
- The hu99 NCU zero-launch path failure and later node-loss interruption remain in the original profiling namespace; neither is claimed as completed full profiling.
- Replacement profiling uses explicit B1 selection from the new pair and has its own `profiling/` artifacts. Metric diagnostics are separate from the CUPTI timing table.
