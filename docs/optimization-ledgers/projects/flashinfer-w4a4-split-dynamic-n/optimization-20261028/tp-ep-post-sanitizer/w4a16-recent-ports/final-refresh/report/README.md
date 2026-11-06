# W4-only report adapter

This adapter has no GPU/runtime imports and makes no GitHub writes. It reuses the verified `retained-refresh/report/assemble.py::update_cells` and TP report helpers; it does not rerun their all-format campaign assembly.

After the qualified retained head's eight W4-only jobs finish and their archive is hash-verified:

```sh
python3 optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/report/assemble.py \
  --head <full-retained-sha> \
  --evidence optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/evidence \
  --output optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/assembled

swap-ab-full-rerun-20261027/.venv-plot/bin/python \
  optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/report/plot.py \
  --parallel ep \
  --csv optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/assembled/ep/summary-cells.csv \
  --output-dir optimization-20261028/tp-ep-post-sanitizer/w4a16-recent-ports/final-refresh/assembled/ep/plot
```

Repeat the plot command with `tp` in all three topology positions. The renderer is the existing red/green heatmap implementation; only its compact model labels and explicit mixed-source caption are configured.

The assembler verifies all archive/source/helper/runtime hashes, clean-head Git blobs, GPU UUIDs and launch assignments, public benchmark command/environment, frozen83df winner/cache/route identities, native CSV lines, graph/CUPTI/no-retune policy, and every100-sample median. It requires104cells/208medians/20,800samples exactly.

Outputs contain both full468-slot CSVs,44×9visible tables and source-verified native A2 documents. The W4A16 column and52native W4rows per topology are replaced. All832non-W4table rows acrossEP/TP and all936baseline records remain unchanged; every inherited measured control is independently re-read and its two-pass geometric mean checked. Native non-W4lines, MXsections and unsupported slots are unchanged. Tokens1/2remainrawonly.

`replacement-data.json` binds the output files and preservation counts for root's eventual PR update. Each topology's provenance explicitly records104fresh medians plus390EP/338TP reused medians, all format source heads, input hashes and old83df provenance. The plot label also distinguishes new-head W4 from other formats at83df. Do not call the old all-format publication builder unchanged: it assumes494/442fresh medians.

Prepared state is not benchmark evidence. No synthetic/relabelled rows or copied old measurements are used to exercise the fresh-data path before the new results exist. Source/parser checks and a read-only audit of inherited inputs can run now; final assembler acceptance requires the real receipts.
