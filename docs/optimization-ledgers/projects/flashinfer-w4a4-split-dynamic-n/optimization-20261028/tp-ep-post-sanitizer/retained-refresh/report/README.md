# Retained candidate refresh

This CPU-only helper replaces candidate A1/A2 values in the existing verified EP
and TP reports. It does not run benchmarks or publish a PR body. The external
baseline latency strings, evidence paths, labels, unsupported cells and reasons
are preserved exactly; only `current_ms`, `speed_percent`, and
`current_evidence` may change in a measured cell. No baseline file is written.

Required fetched layout:

```text
retained-refresh/<head>/evidence/
  source.json
  runtime.json
  benchmark-tools/*.py
  runs/{ep,tp}/{model}/{family}/
    receipt.json
    frozen-cache-manifest.json
    managed-cache/**
    {tune,a1,a2}.log
    {tune,a1,a2}/results.json
    {tune,a1,a2}/token_*.managed-cache-manifest.json
```

The TP V41 MX receipt is required and must explicitly record its skipped state;
it has no phases/cache. K3 MX results must contain MXFP4x8 only. Both topology
tables retain 13 token values in CSV and display the 11 values starting at 4.

From the project root, after the complete evidence is fetched:

```bash
python3 optimization-20261028/tp-ep-post-sanitizer/retained-refresh/report/assemble.py \
  --evidence optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/evidence \
  --parallel ep \
  --output optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/report/ep
python3 optimization-20261028/tp-ep-post-sanitizer/retained-refresh/report/assemble.py \
  --evidence optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/evidence \
  --parallel tp \
  --output optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/report/tp
swap-ab-full-rerun-20261027/.venv-plot/bin/python optimization-20261028/tp-ep-post-sanitizer/retained-refresh/report/plot.py \
  --parallel ep \
  --csv optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/report/ep/summary-cells.csv \
  --output-dir optimization-20261028/tp-ep-post-sanitizer/retained-refresh/<head>/report/ep/plots
```

Repeat the renderer command with `tp`. It imports the existing red/green table
renderer, changes only the topology labels, and binds the output to the new
provenance hash. Report output directories must be new, preventing accidental
overwriting of previous evidence.

Acceptance checks cover pinned Git source blobs, qualified observer hashes,
receipt/log/result hashes, exact EP/TP scope, original route identities, frozen
cache files and per-token snapshots, the same native winners in AUTO/A1/A2,
matching v1 NV and v2 MX measurement policy, public functional API selection,
NV input quantization, unfused finalize, 10 warmups, cold L2, graph timing, 100
positive CUPTI samples and exact raw medians. CUDA-event fallback and tuning
during public measurement are rejected. Saved external baseline means are
recomputed from their original two raw result files. Output uses the geometric
mean of the two standard 100-sample medians, never pooled samples or strata.

`baseline-roundtrip.json` qualifies the cell updater against both existing
468-cell reports. Python compilation and CLI checks pass. The fresh campaign
acceptance path awaits actual refresh data; this preparation is not a new
performance result. External native raw output remains in its original EP/TP
report; `native-a2-output.md` contains only the fresh candidate output.
