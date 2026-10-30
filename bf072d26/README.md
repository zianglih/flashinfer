# W4 partial-K refresh evidence

Retained source: `bf072d26b163e71458e7e4dfb12e615b19bd2c9a`.
New measurements retain their actual base `02de7785` plus the frozen two-file
patch (`25aa126d` W4 kernel / `66ec9ae8` Mega caller). The retained commit has
exactly those qualified bytes. Existing records retain their original source.

- **Fresh causal result:** 39 affected W4 cells, C/A/A/C, 15,600 CUPTI samples.
  Tokens 1/2 are retained in raw data and excluded from the 33-cell retention
  aggregate. All 24 token-4–512 cases improve; decode +1.701%, middle +2.110%,
  affected-scope overall +1.471%. Six prefill cases regress, worst −0.746%.
  The +0.456% prefill aggregate includes variable +3.59%/+2.90% 8K cases and
  should not be described as a reliable prefill improvement.
- **Full matrix:** 39 fresh and 429 reused candidate cells, 468 total. The 429
  unchanged rows comprise 364 swap rows and 65 W4 specializations where the
  new predicate is inactive. Reuse is justified by source/geometry and aligned
  native qualification; it is not a claim that all 65 native images were
  recaptured. All original fields of the reused rows remain exact.
- **Historical comparisons:** the full retained baseline remains measured
  `326c4a79`, production-equivalent to `82254e20`; external TRTLLM, legacy CuTe
  and pre-PR W4A16 baselines are unchanged. These heatmaps are not a fresh paired
  468-cell comparison. Full historical GM is +0.174% (swap +0.039%, W4 +0.649%).
  The 396 displayed cells omit tokens 1/2 and retain all 172 negative rows.
- **Candidate timing/resource view:** 936 candidate phase measurements,
  93,600 samples (7,800 newly measured plus 85,800 reused), 1,114 loaded MoE
  function records with zero local memory. All 78 fresh cell/stage resource
  configurations are unchanged across arms. Of 3,744 selected candidate clock
  quartiles, 94 are exceptional and 5 lack NVML observations. The full causal
  39-cell evidence separately has 624 quartiles, 49 exceptions and 1 missing.
  No samples or negative rows were removed, no clocks changed, and no new
  sanitizer or distributed timing run was performed for this refresh.

## Contents

- `report/`: complete comparison rows, per-row fresh/reused provenance,
  candidate clocks/resources and summary. `source-reuse-proof.json` binds the
  qualified source, previous publication and explicit 39-key coverage.
- `plots/`: retained/external EP and TP heatmaps, original compact labels and
  red/white/green style. Only three TP W4 groups change numerically; all external
  baseline fields and unsupported/fused markers remain unchanged.
- `stdout/`: 62 untouched published logs plus 24 original new CAAC logs. These
  are the native stdout bytes, including the original table and CSV output;
  nothing was parsed and reformatted as an alleged original log.
- `completed-tables/`: 15 family tables emitted by the unchanged benchmark
  printer from saved structured records: 39 fresh CuTe records, 429 reused CuTe
  records and 390 historical TRTLLM records (338 low precision, 52 BF16). The 31
  prior and 6 new partial final-candidate table outputs reproduce byte-for-byte.
  New candidate rows use phase 2; reused rows keep their original final AA pass.
  The two-pass heatmaps and final-pass tables intentionally use different
  aggregation. Only three TP NVFP4 family tables change numerically.

Older BF16 records report CUDA Graph/CUPTI timing but predate the newer strict
per-record timing guards. All tables retain original precision, columns, N/A,
winner rules and source references. The archive includes all fresh CAAC raw candidate/control data, telemetry,
source inventories and independent replay receipts under evidence/ and audits/.
It also preserves the original GLM5 table; no new distributed timing is implied. The previous
`publication/` and published PR assets are untouched.
