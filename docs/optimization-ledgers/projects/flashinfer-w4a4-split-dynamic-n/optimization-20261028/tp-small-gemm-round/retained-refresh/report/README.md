# Full retained-source report adapter

Prepared for the final clean-head campaign; no measurement data is fabricated or substituted. Root owns GPU launches and publication.

The assembler consumes the existing `run_refresh.py` receipt schema unchanged. Extract the shared campaign archive into a project-local evidence directory containing `archive-manifest.json`, `config.json`, `source.json`, `qualification.json`, `run_refresh.py`, `launch-<box>.json`, `observer/*.py`, and `runs/<topology>-<model>-<family>/` with both candidate results/logs and the frozen managed cache. The archive preserves deployment/source postflight receipts and available runtime notes. The separately named archive manifest never replaces source/local manifests.

```sh
python3 report/fetch_evidence.py --head FULL_RETAINED_SHA --remote-root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-small-gemm-round/retained-refresh/HEAD --box fi-moe-nvfp4-port-1026 --output-dir HEAD
python3 report/assemble.py --head FULL_RETAINED_SHA --evidence HEAD/evidence --output HEAD/report
python3 report/plot.py --parallel ep --csv HEAD/report/ep/summary-cells.csv --output-dir HEAD/report/ep/plots
python3 report/plot.py --parallel tp --csv HEAD/report/tp/summary-cells.csv --output-dir HEAD/report/tp/plots
```

Run these commands from `optimization-20261028/tp-small-gemm-round/retained-refresh`. Use the existing plotting environment if the system Python lacks matplotlib.

- Audit: 348 Git source hashes, helper/observer/config/archive hashes, 15 launcher/job assignments, GPU UUIDs and nonoverlapping phase windows, exact public argv/environment, frozen83df winner/cache/route identities, 100 finite strict-CUPTI samples per median, no profiling or cache mutation, and exact printed native CSV lines. MX's existing graph measurement policy is preserved separately from the NV policy.
- Evidence: 468 unique current cells, 936 A1/A2 medians, 93,600 samples. Pass aggregation is the geometric mean of the two medians. EP has247 cells/494medians; TP221/442. All13 tokens remain in raw CSV;1/2 are excluded from the44-row display tables.
- Reuse: `tp-ep-post-sanitizer/retained-refresh/report/assemble.py:update_cells` updates current values only; every saved external-control field and unsupported slot remains unchanged. The two CSV tables together contain936 comparison slots,468 per topology. Revalidate baseline pass values and route identities from their bound raw evidence. No external-control rerun.
- Outputs: EP/TP `summary-cells.csv`, `summary-table.md`, `fresh-a1-a2-medians.csv`, full eight-section `native-a2-output.md` (explicit skipped TP V41F MX section), and `provenance.json`; campaign `replacement-data.json`; existing red/green renderer produces plots with the final retained head label.
- Preparation checks: Python syntax/CLI imports and a read-only preflight of saved83df data. These are helper checks, not qualification of the upcoming source or fresh timings. No sanitizer is run.

The fetch helper installs only its collector under the campaign evidence directory and uses the existing `remote_box.py` transport. It refuses incomplete campaigns, rechecks all source348 files and30 pass receipts, keeps all remote files, and copies only metadata/raw results/managed-cache JSON. Source checkout, source bundle, native compiler caches, Triton cache and private compile artifacts are omitted. Transfers resume by byte offset; the complete tar SHA and each extracted file hash must match before the final evidence directory is accepted.
