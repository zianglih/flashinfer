# Swap-AB benchmark heatmap

`swap-ab-speedup-table.png` is the 3000 × 3800 raster plot; the SVG is scalable with selectable text. Both show the published 44 × 9 comparison table from the completed `e2728a290` CUPTI campaign. Tokens 1 and 2 are omitted. No benchmark was rerun to generate this figure.

The palette and normalization follow `benchmarks/bench_nvfp4_quantize_backend_comparison.py:create_heatmap`: `RdYlGn` with ratio limits 0.5 / 1.0 / 2.0 and neutral at 1.0. Labels use the PR's equivalent signed percentages, so the shared colorbar spans −50% / 0% / +100%. Gray cells are unsupported, not zero. Group separators distinguish models, and dashed lines precede prefill rows.

Regenerate from the campaign directory:

```bash
.venv-plot/bin/python plot_speedup_table.py
```

For a new environment, install `plots/requirements.txt` in a virtual environment and run the same script. `plot-manifest.json` records the CSV/script/output hashes and every plotted value. The script and outputs are local project artifacts outside the FlashInfer repository; nothing was committed or uploaded.
