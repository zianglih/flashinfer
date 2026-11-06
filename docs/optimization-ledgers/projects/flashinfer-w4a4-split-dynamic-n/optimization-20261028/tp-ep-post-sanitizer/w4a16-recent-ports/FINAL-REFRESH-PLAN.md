# Final W4A16-only report refresh (preparation; no new run/publication)

If the combined port is retained, rerun only W4A16 from the pushed head using the eight existing83df frozen winner/cache and route anchors: four models × EP/TP × all13tokens. Two fresh CUPTI/cold-L2 replay passes; no retune. This yields104cells,208medians,20,800 timed samples total (52cells/104medians per topology). Tokens1/2 remain measured but hidden/excluded from retention.

## Existing inputs and reusable functions

- Immutable complete table baseline: `retained-refresh/83dfef8a6563/report/{ep,tp}/summary-cells.csv`, `provenance.json`, `native-a2-output.md`. Each has468slots and44display rows×9columns. Original raw receipts/caches live under `retained-refresh/83dfef8a6563/evidence/runs/{ep,tp}/{model}/nvfp4/`.
- Latest local published body: `compact-policy-cleanup/publication/pr-body.md` (root should re-read current PR before any eventual write).
- Existing `retained-refresh/report/assemble.py::update_cells(original,values,evidence)` computes geometric-mean A1/A2 latency and same-dtype ratio while checking baseline fields. Call it on only the52 rows with `column == "w4a16"`, then merge those rows back into the original468row ordering. Do not feed fake/re-labeled measurements for reused formats.
- Reuse `retained-refresh/report/assemble.py` CUPTI sample/median, cache, route, source, rawCSV/log verification logic for the new one-backend receipts. Its current outer loop requires all formats and a tune phase; the W4 adapter must instead require exactly eight W4 jobs and two frozen phases. Strict cache hits must equal the saved83df winners, never only each other.
- `retained-refresh/report/plot.py` wraps the existing `swap-ab-full-rerun-20261027/plot_speedup_table.py` red/green renderer. Regenerate both full plots using the new table CSVs; preserve all396 visible slots/topology, existing colors, model labels, column order and N/A marks. Caption/commit label must distinguish new-head W4A16 from reused83df other formats.
- `retained-refresh/publication/prepare_body.py` contains reusable details parsing, table replacement, LOC accounting, asset/source-hash and template-preservation guards. Its full-refresh `load_report`/`build` require494EP/442TP fresh medians and d176 anchors, so **do not call unchanged or present the old full-matrix sample totals as newly rerun**. A small W4-only adapter should reuse those low-level helpers while accepting mixed source provenance.

## Minimal table/native-output substitution

Only the W4A16-before-PR column changes (52all/44visible cells per table). It continues to compare old pre-PR non-swap legacy layout against the new swap-AB layout; existing `baseline_ms`, baseline evidence and every other field are immutable. All416non-W4 rows/topology must compare byte-for-byte as dictionaries with83df, including unsupported cells. All468baseline records must remain identical. No incremental performance table is added to the PR.

Replace only the13 `CuteDSL W4A16` A2 CSV lines in each of the eight NV-family blocks with the lines printed by the new script. Each replacement must match its new log verbatim, and every non-W4 line plus all MX/external-control blocks must remain byte-identical. These are assembled source-verified rows, not one monolithic new log; label them concisely as W4A16 at the new head / other CuTe at83df. Preserve raw latency and TFLOPS strings without formatting/recomputation.

New provenance should include `fresh_formats=["w4a16"]`,104fresh medians/topology,390EP/338TP reused medians, source heads by format, new source/receipt/helper/cache/route hashes, and hashes of the inherited83df provenance and outputs. Ratios continue to use the geometric mean of the two100-sample pass medians. Preserve baseline/unsupported-field assertions,44×9display shape and checksum every assembled output.

Before publication, bind full plots to the new table/provenance hashes and immutable asset URLs, update only the table/plot/nativeW4 rows plus concise implementation/validation wording/LOC, preserve issue/template sections and existing83df sanitizer boundaries, and independently verify all832unchanged non-W4 table rows across both topologies. Root owns any GitHub publication.
