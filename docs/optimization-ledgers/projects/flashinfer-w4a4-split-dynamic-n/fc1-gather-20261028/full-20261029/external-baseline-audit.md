# External baseline audit for fb66a27e

Historical same-B300-class scoreboard; not a new causal rerun. Candidate measurements are the fresh fb66a27e C-A-A-C campaign against d35fcfda. Saved external controls were collected on other C3 B300 GPU instances. No B200 data is used.

## Reuse authority

- `optimization-20261028/post-hybrid-polish/composed/publication/report/{ep,tp}/summary-cells.csv` supplies only `baseline_ms`, `baseline_evidence`, baseline status/reason/labels. Its old current measurements must not be reused.
- `provenance.json` alongside each file records all raw input hashes and unchanged baseline/status fields. This audit checked 88 raw result hashes, 660 measured comparisons (including 88 W4A16 diagnostics), exact routing identities, input-quantization boundaries and per-arm quantization contracts against fresh candidate rows. Zero contract mismatches. All raw timing lists have 100 CUPTI samples and prohibit event fallback.
- Raw EP controls: `optimization-20261027/retained-rerun/evidence/runs/<model>/<family>/.../results.json`. TRT uses a1/a2; legacy/pre-PR use the exact paths in each CSV row. Raw TP controls: `optimization-20261028/tp-ep-post-sanitizer/evidence/runs/tp/<model>/<family>/c{1,2}-<arm>/results.json`.
- External CuTe legacy source `e2728a2908f38cbcfa997c031bea059e3724ccde`; pre-PR W4A16 `002529e17b22567a071091053c6c4dc2a55e050e`. Configs in both evidence roots record source manifests. W4A16 pre-PR only adapts benchmark script.
- Baseline benchmark SHA b8e81fd1f40798a7f1395188565b4a707bfab78fbc8c8504ac7592c193a568ae; fresh benchmark SHA differs. Measured model/routing/activation/quantization contracts were compared directly rather than assuming identical script bytes. Arm-contract helper SHA remains 28e52529706096aa7d3823f0c622cec96090b3dd2bba2c5a6690ba66f7f78a5d.
- Recorded environment is CUDA13.2, CuTeDSL4.8.0, CUPTI13.4.0, PyTorch26.05 (`nvcr.io/nvidia/pytorch:26.05-py3`). Fresh environment/driver/GPU UUIDs are in `evidence/environment.json`. Baseline environment is traced via `swap-ab-full-rerun-20261027/README.md`, `swap-ab-benchmark-table-20261027/evidence/cupti-runtime.json`, and the two campaign configs/receipts. Historical versus fresh physical GPU UUIDs differ; do not describe this as paired same-GPU testing.
- NVFP4 includes initial activation quantization; MX starts prequantized. Per-token activation uses MSE4over6, E4M3max256, fastmath4over6 and disables ordinary FP4 fastmath. All match fresh rows.
- Candidate is unfused. Non-swap MX requires fused finalize and retains dagger marker. This is the explicit allowed baseline exception. Unsupported K3 MXFP8 and V41F TP MX modes remain N/A. Tokens1/2 excluded from scoreboard.

## Builder

Original table logic is `optimization-20261028/post-hybrid-polish/composed/publication/assemble.py`, importing `optimization-20261028/tp-ep-post-sanitizer/retained-refresh/report/assemble.py`, then `optimization-20261028/tp-ep-post-sanitizer/report/assemble_tp.py`. Do not run latest assembler unmodified: it binds stale source receipts and checkout HEAD. Companion `audit_external_baselines.py` builds current values without mutating publication.

## Largest cohort gaps

Metric is `100*(baseline_ms/candidate_ms-1)`; negative means candidate is slower. Geometric means use equal-weight token cells.

|Topology|Control|Model|Dtype|Cohort|Speed|
|---|---|---|---|---|---:|
|ep|legacy|nemo3-ultra|w4a4|prefill|-27.14%|
|tp|trtllm|nemo3-ultra|per_token|prefill|-16.96%|
|tp|legacy|v3|mxfp4x8|prefill|-16.82%|
|tp|legacy|nemo3-ultra|mxfp4x8|prefill|-16.49%|
|tp|legacy|v3|mxfp8|prefill|-15.52%|
|tp|trtllm|nemo3-ultra|w4a4|prefill|-14.55%|
|tp|legacy|nemo3-ultra|mxfp8|prefill|-13.99%|
|ep|trtllm|nemo3-ultra|w4a4|prefill|-13.32%|
|tp|legacy|nemo3-ultra|w4a4|prefill|-10.16%|
|tp|trtllm|v41-flash|per_token|prefill|-9.24%|
|ep|legacy|nemo3-ultra|mxfp4x8|prefill|-8.66%|
|ep|legacy|nemo3-ultra|mxfp8|prefill|-8.35%|
|ep|trtllm|nemo3-ultra|per_token|prefill|-7.55%|
|tp|trtllm|v3|w4a4|prefill|-6.07%|
|tp|legacy|nemo3-ultra|per_token|prefill|-5.70%|

## Retention companion

Keep three separate references: fresh paired d35, historical non-swap, historical TRT. For each EP/TP × model × dtype show decode4–64, middle128–512, prefill4096–16384 geometric mean and worst token, plus paired phase drift for d35. Do not average the three references together. Prefer priorities supported by both d35 and external gaps. N3U EP W4A4 prefill is the largest such signal: worst T16384 is −31.37% vs fresh d35 and −32.92% vs saved non-swap. TP V3/N3U MX prefill gaps versus legacy fused kernels also remain, despite improvements versus d35. W4A16 current campaign remains a diagnostic until a W4A16 candidate is implemented.

Full raw-pointer companion: `external-baseline-cells.csv`; cohort summaries: `external-baseline-audit.json`. No GPU work, GitHub changes or kernel source modifications were performed.
