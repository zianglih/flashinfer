# TP report preparation

No benchmark, GPU, network, Git mutation, or publication occurs in these helpers. Current source is d1767be1; non-swap source e2728a290; pre-PR W4A16 source002529e17 with its previously qualified benchmark-only adapter. TP8/EP1 applies to V3/K3/N3U and TP4/EP1 to V41F. Communication is outside this local-compute benchmark.

The independent report contract contains468 comparison slots across13 token counts, including104 unsupported slots and364 measured comparisons. The underlying runs contain221 current cells and364 control cells, each with two accepted passes:1170 medians and117000 raw CUPTI samples. All84 phases, including28 fresh-tuning phases, are checked; tuning measurements are excluded from output. The44×9 display excludes tokens1/2 and has308 measured cells plus88 N/As.

Skip V41F TP4 MX entirely (logical intermediate576 versus external alignment128), K3 MXFP8 (no external SiTU support), and unsupported individual K3 controls. The seven active jobs still produce eight family sections, with an explicit skipped V41F MX section. Old non-swap MX uses its required fused finalize; all swap-AB arms remain unfused.

Both devboxes share the campaign filesystem. Fetch it into one project-local evidence root, preserving these paths from the remote campaign root:

- `config.json` and all files listed in `config.observer_hashes` under `benchmark-tools/`.
- `runs/tp/<model>/<family>/receipt.json`, every phase's `results.json` and sibling `.log`.
- Per-arm `*-frozen-cache.json`, full `*-managed-cache/` directories, and native `*-native-auto.json` files.
- The V41F MX skipped receipt. Do not synthesize benchmark results for it.

Keep the archive verification receipts alongside each evidence root. The builder accepts multiple roots and rejects duplicate or missing jobs. Remote paths in receipts are resolved beneath the corresponding fetched root without modifying evidence.

From the project directory:

```sh
audit-final-cleanup/.venv-cpu/bin/python optimization-20261028/tp-ep-post-sanitizer/report/check_contract.py

audit-final-cleanup/.venv-cpu/bin/python optimization-20261028/tp-ep-post-sanitizer/report/build_manifest.py \
  --evidence-root <evidence-root>

audit-final-cleanup/.venv-cpu/bin/python optimization-20261028/tp-ep-post-sanitizer/report/assemble_tp.py \
  --manifest optimization-20261028/tp-ep-post-sanitizer/report/measurements.json

# Use the existing plotting Python environment with matplotlib and NumPy.
python optimization-20261028/tp-ep-post-sanitizer/report/plot_tp.py
```

`assemble_tp.py` reuses the prior report's CSV and geometric-mean helpers. It independently verifies pinned source blobs (347 current,342 legacy,338 pre-PR plus the approved adapter hash), source-specific arm selection, exact phase ordering, source/helper/log/result hashes, argv/environment, same GPU UUID, matched routes, sample medians, replay hits and winner identity against fresh tuning, and unchanged cache contents. It also checks source-script CSV lines against the raw logs, preserving native A2 candidate and C2 control output. Unexpected failures cannot become N/A.

Outputs in `assembled/`: `summary-cells.csv`, `summary-table.md`, `accepted-pass-medians.csv`, `raw-pass-medians.md`, `native-a2-c2-output.md`, and hash-bound `provenance.json`. Percentages are100×(geometric-mean control latency / geometric-mean current latency−1). A positive value is faster. Both means use the two matching same-GPU accepted passes.

`plot_tp.py` imports the existing red/white/green renderer unchanged and supplies the compact TP model labels. It emits the usual PNG/SVG and extends the plot manifest with wrapper/contract hashes. Inspect the rendered image before any publication. No image or timing report has been generated without real complete TP evidence.

`preparation.json` records only CPU preparation checks. It is not a benchmark or runtime qualification.
