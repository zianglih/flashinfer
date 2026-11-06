# Full EP/TP FC1 gather comparison helpers

The historical full campaign measures tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
It does not include 1024. Tokens 1–2 are measured but excluded from displayed tables,
heatmaps and retention aggregates. Sources: `optimization-20261028/fc2-hybrid-vs-head/README.md`
and `optimization-20261028/warp-polish/final-polish/prepare_campaign.py`.

The current 15-job support matrix contains 468 measured cells and 396 displayed cells:
308 affected cells and 88 unchanged W4A16 diagnostics. K3 MXFP8 and V41F TP MX formats
are N/A. W4A16 is excluded from geometric means. Aggregate bands follow the prior
analyzer: 4–64, 128–512, and 4096–16384 tokens.

Run from the project directory after collecting the full evidence:

```bash
python3 fc1-gather-20261028/full-20261029/plotting/analyze_perf.py \
  fc1-gather-20261028/full-20261029/evidence/perf \
  --output fc1-gather-20261028/full-20261029/report
fc1-gather-20261028/plot-venv/bin/python \
  fc1-gather-20261028/full-20261029/plotting/plot_heatmap.py \
  fc1-gather-20261028/full-20261029
python3 fc1-gather-20261028/full-20261029/plotting/write_tables.py \
  fc1-gather-20261028/full-20261029
python3 fc1-gather-20261028/full-20261029/plotting/build_pr_body.py \
  fc1-gather-20261028/full-20261029
```

The analyzer validates complete receipts, C-A-A-C order, source consistency, exact
cell/token coverage, CUPTI with no event fallback, all 100 raw samples per phase,
latency medians, fixed routes/tactics and output layout invariants. The plotter
recomputes every percentage from the four unrounded phase medians, checks the full
displayed support matrix, and records source/output hashes in `plots/plot-manifest.json`.
Its commit labels default to retained `d35fcfda` and experiment `fb66a27e`.

Helper validation only: `qa-r14` reproduces the prior 144-cell report exactly;
`qa-full` uses historical FC2-hybrid results labelled **QA-OLD** to inspect the full
44-row geometry. These are not new gather benchmark results and must not be published.

`build_pr_body.py` reads the previous fork body, preserves its design/template and
prior-validation boundary, and replaces the screening evidence with full results.
It emits `publication/body-draft.md` with `EP_HEATMAP_URL`, `TP_HEATMAP_URL`, and
`RAW_CSV_URL` placeholders. It requires the measured baseline/kernel hashes and
full sample counts to match before generating a publishable draft.
