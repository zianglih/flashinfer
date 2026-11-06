# Gathered FC1 integration performance artifacts

Historical candidate measurements: swap formats b52e4e09; W4A16 1e4b127a. Historical TRTLLM, non-swap and pre-PR W4A16 baselines are reused. Subsequent absmax/tail reverts and module cleanup at 4376662a were not remeasured.

Both full heatmaps use the existing quantizer-style red/white/green palette, centered at equal latency, with common ratio bounds 0.5–2.0. They show 44 rows (four model presets × eleven token counts) and nine same-dtype baseline columns per topology. Tokens 1–2 remain in source CSV evidence but are omitted from plots, tables and aggregates. † marks old non-swap MX backends requiring fused finalize; every measured candidate uses unfused finalize.

- `plots/swap-ab-speedup-table-{ep,tp}.{png,svg}`: full end-to-end heatmaps.
- `external/{ep,tp}/summary-table.md`: corresponding signed-percentage tables.
- `comparison-latencies.csv`: all 792 displayed comparison cells, with absolute latencies, source refs and N/A reasons.
- `all-comparison-cells.csv`: all 936 comparison cells including tokens 1–2.
- `stats.{json,csv,md}`: geometric aggregates with explicit cell counts.
- `report/cells.csv`: all 468 measured candidates versus historical d35 PR-head controls, retained for history.
- `candidate-latencies.md`: absolute candidate latency tables for displayed tokens.

Regenerate with `python assemble_stats.py`, then `python plot_speedup_table.py --csv external/ep/summary-cells.csv --output-dir plots --topology ep` and the TP equivalent. No benchmarks or GPU jobs were run to generate these artifacts.
