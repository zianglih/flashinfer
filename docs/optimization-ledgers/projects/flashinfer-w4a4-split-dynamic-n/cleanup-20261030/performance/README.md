# Cleanup-head performance refresh

Fresh candidate head: `326c4a793085e79b64b9c7fd79e77320c220ccba`. Existing source qualification and full 31-job/468-cell A-A measurements are owned by the GPU agent. `harness/` and `evidence/` are its files; publication scripts do not alter them or launch GPU work.

After all fresh evidence and per-job clock analyses are downloaded:

```bash
python cleanup-20261030/performance/assemble.py --head 326c4a793085e79b64b9c7fd79e77320c220ccba
python cleanup-20261030/performance/plot_speedup_table.py --csv cleanup-20261030/performance/external/ep/summary-cells.csv --output-dir cleanup-20261030/performance/plots --topology ep --commit-label 'Measured 326c4a79'
python cleanup-20261030/performance/plot_speedup_table.py --csv cleanup-20261030/performance/external/tp/summary-cells.csv --output-dir cleanup-20261030/performance/plots --topology tp --commit-label 'Measured 326c4a79'
python cleanup-20261030/performance/prepare_assets.py
python cleanup-20261030/performance/build_body.py --validation cleanup-20261030/performance/validation-summary.md --environment cleanup-20261030/performance/environment.md
```

The final two Markdown inputs must state completed source-qualified validation and the actual measured runtime; do not create success placeholders. The body keeps the two heatmaps prominent and links native table output in four comments. The unchanged benchmark printer combines468 fresh candidate cells with390 original TRTLLM cells in15 family tables, including all13 tokens; plots and aggregates exclude1/2. CSV remains downloadable data, never embedded raw output. Exact unmodified both-format stdout is archived separately.

The user requested literal script output, then authorized comments because the original tables exceed the PR-body limit. They subsequently requested reusing original TRTLLM results to fill the table columns. `completed-tables/render_comments.py` executes the measured benchmark's unchanged table functions on saved records; it first reproduces all31 original native outputs byte-for-byte, then combines preserved latency/TFLOPS pairs. `baseline-index.json` records the historical sources and missing cases, including the older BF16 timing-guard boundary. `completed-tables/publish_comments.py` updates the same four comments with readback verification and writes `native-output-index.md`, which `build_body.py` includes. `raw-output.md`, `verbatim-tables/` and earlier receipts remain historical artifacts.

Historical baseline fields and their evidence are reused unchanged. The GLM5 section is not remeasured: only its raw phase CSV is converted losslessly to a Markdown table. Its source scope, numbers and URLs remain unchanged. `build_body.py` recomputes current committed LOC counts with W4 and swap separate.

`publish_assets.py` and the comment publication scripts perform authorized remote publication. Root approves completed raw/source/runtime/clock audit and visual QA, then publishes the artifacts/comments, rebuilds the final body and verifies GitHub readback. Previous publication artifacts are left intact.
