# Merged PR7290 fresh performance publication

Measured source: `a620ce7790b32f7f0ae524a811417d2c6cee1152`, the two-parent merge of upstream `82254e20` and retained fork `8bc69ee4`; its tree equals `8bc69ee4`. This folder is a local publication workspace. Root owns asset uploads and PR/body/comment writes.

- Candidate data: all 468 cases freshly measured in two complete candidate passes, 100 strict-CUPTI cold-L2 graph samples per pass and 10 warmups. All 93,600 samples, both process logs, negative rows, repeat spreads and clock observations remain. No retuning; public functional API and frozen recorded routes/tactics. Tokens 1/2 are raw only; 396 candidate cases appear in displayed aggregates.
- Denominators: immutable original TRTLLM, non-swap and pre-PR W4A16 values. These are historical cross-instance comparisons. No old candidate rows are reused. NVFP4 includes initial quantization; W4A16 takes BF16. Non-swap MX retains required fused-finalize settings. Unsupported columns remain N/A.
- Native tables: actual unchanged benchmark printer, saved structured JSON only. Every final-pass output is first checked byte-for-byte against its original stdout. Tables use the final pass; heatmaps use the geometric mean of two pass medians. Original table-only BF16 rows retain their older timing-guard limitation and are excluded from the heatmaps.
- Current validation: seven exact smoke calls and 21 zero-local native kernels on merged source, stored separately from historical suites. The smoke fixtures never enter performance processes. Original GLM5 evidence remains explicitly historical and unchanged.
- Runtime: C2 B300, `fi-gather-pipeline-resume-1030`, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1, driver 595.91.07, PyTorch package `2.12.0a0+5aff3928d8.nv26.5.50603568`, CuTe DSL 4.8.0/CUPTI Python 13.2. Current release cohort has `moe_utils` ELF `046552b8…`; historical denominators belong to their original cohorts.

Run only after the data owner seals `evidence/pr7290-retained-refresh/<stamp>/{data,report}`:

```bash
python3 publication-pr7290-a620/assemble.py --data evidence/pr7290-retained-refresh/<stamp>/data
python3 publication-pr7290-a620/completed-tables/render_comments.py
.venv-publication/bin/python publication-pr7290-a620/plot_external.py --csv publication-pr7290-a620/external/ep/summary-cells.csv --output-dir publication-pr7290-a620/plots --commit-label a620ce77 --topology ep
.venv-publication/bin/python publication-pr7290-a620/plot_external.py --csv publication-pr7290-a620/external/tp/summary-cells.csv --output-dir publication-pr7290-a620/plots --commit-label a620ce77 --topology tp
python3 publication-pr7290-a620/verify_numeric.py
python3 publication-pr7290-a620/write_pr_body.py --draft
python3 publication-pr7290-a620/build_bundle.py --prepare
```

The numerical checker independently recomputes all CUPTI spans, phase medians, candidate aggregates, preserved baseline fields and plot/table values. The independent peer owns full routing/default/resource/clock checks. Root visually inspects both PNGs and binds all four PNG/SVG hashes in `visual-review.json` (`passed`, `plots`). Sealing requires `audits/pr7290-a620-{data,publication}-peer.json`:

```bash
python3 publication-pr7290-a620/build_bundle.py
```

The XZ uses an explicit hash-bound allowlist: fresh raw data, original stdout, smoke native evidence, current receipts, scripts and derived outputs. `dependencies.json` pins the previous 97,169,580-byte archive and historical publications; none is nested or copied into this incremental archive. Every new asset must remain below 100,000,000 bytes. Body/comment URL drafts and publisher logs are excluded. Complete joined table records remain in `completed-tables/manifest.json`; its bytes do not depend on the final asset URL. Four local comments and their IDs/hashes live in separate `comment-manifest.json`.

Root-only publication, after independent XZ peer:

```bash
python3 tools/publish_pr7290_a620_assets.py          # validates locally; no writes/network
python3 tools/publish_pr7290_a620_assets.py --publish
python3 publication-pr7290-a620/completed-tables/render_comments.py
python3 publication-pr7290-a620/write_pr_body.py
```

The publisher checks the clean source and asset heads, every archive member and peer receipt, the 100 MB bound, and immutable prior asset prefixes. It writes `assets-published.json` for root's existing guarded PR writer. The final renderer changes only the URL-dependent drafts; root verifies the stable table manifest before/after. No GitHub update runs automatically from any publication renderer.
