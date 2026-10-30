# FC1 integer-store refresh evidence

Retained source: `49c91adf47d30fc2049c76cbaf34d0ccf3291434`.
The fresh experiment measured `bf072d26` plus the frozen `482b636a` swap kernel;
the retained commit has exactly these qualified production bytes. Earlier
records keep their original measured source and provenance.

- **Paired causal result:** all 104 N3U EP8/TP8 swap cells, C/A/A/C and 41,600
  untrimmed CUPTI samples. Tokens 1/2 are included in raw data but excluded from
  retention. The 88 retained cells have +0.643% GM; decode 4–64 is +0.054%,
  middle 128–512 is −0.022%, and prefill is +2.309%. The 18 quantized-output
  prefill cells all improve (+3.144% GM); unchanged-store-width per-token is
  not a binary-null control and retains EP8 8K/16K losses of −0.787%/−0.544%.
  All 32 negative retention rows remain. Variable MX large-token repeats are
  marked rather than filtered. See `integer-store-causal/` for all four phase
  medians and `plots/integer-store-vs-retained.png` for the paired comparison.
- **Full matrix:** 104 fresh plus 364 exactly reused candidate rows, 468 total.
  Reuse comprises 104 untouched W4 cells and 260 gated swap cells. The unchanged
  gated branch has representative byte-identical native qualification across
  FP4, FP8, per-token, SwiGLU and SiTU; this is not a claim that all 260
  specializations were recompiled. Previous W4-tail results remain unchanged.
- **Historical comparisons:** original TRTLLM, non-swap CuTe and pre-PR W4
  baselines are unchanged. The full retained baseline is the historical
  `326c4a79` data, production-equivalent to `82254e20`. These 468-cell plots are
  not a new paired comparison. The 396 displayed cells omit tokens 1/2 and
  preserve 161 negative historical rows; historical GM is +0.335% (swap +0.245%,
  W4 +0.649%).
- **Timing/resource evidence:** 93,600 selected candidate samples (20,800 fresh
  plus 72,800 reused), 1,162 loaded native function records with zero local
  memory. The fresh paired screen independently covers 155 unchanged resource
  pairs and 620 loaded function records. Its 1,664 clock quartiles have 17
  exceptions and no missing observations. The mixed full-matrix candidate view
  has 3,744 quartiles, 90 exceptions and 5 missing NVML observations; those
  historical gaps are preserved. No clock edits, sample filtering, new tuning,
  sanitizer or distributed timing are implied by this refresh.
- **Qualification:** the final source passed 12 unfused exact calls plus four
  direct FP32 fused boundary calls. Unfused resources are unchanged/LOCAL0.
  Fused two-CTA registers increase 122→125; that path is not timed here and the
  analytic boundary calls are not a general bit-exact fused test claim. The
  earlier `cdb2` generic recast failed its resource gate with LOCAL272 before
  launch. The final qualification also preserves a harness-only metadata
  failure and its successful retry rather than rewriting the failed receipt.

## Contents

- `report/`, `external/`, `plots/`: full comparison rows, unchanged historical
  baseline fields, per-row provenance, native resource and clock summaries,
  the two full EP/TP comparison pairs, and the paired 104-cell plot.
- `stdout/`: all 134 original stdout logs, including 48 new CAAC logs and 86
  inherited logs. Their bytes are preserved, including native table/CSV output.
- `completed-tables/`: 15 tables across 16 model/topology/family groups, emitted
  by the unchanged benchmark printer from 104 fresh and 364 reused final-pass
  CuTe records plus 390 historical TRTLLM records (338 low precision, 52 BF16).
  All 49 source final-pass stdout table suffixes reproduce byte-for-byte before
  joining the families. These final-pass tables intentionally differ from the
  two-pass heatmap aggregates. Missing/unsupported entries stay N/A.
- `evidence/`: all files from the two immutable fresh CAAC fetch manifests,
  including raw timing records, routes, frozen choices, cache/source proofs,
  all four phase logs, telemetry, resource guards and independent reports.
- `source/`, `audits/`, `experiments/`: retained source and patch, reuse and
  qualification boundaries, the preserved failed metadata receipt, and the
  independent raw/component/combined audit receipts.
- `previous-w4-publication/`: every member of the previously sealed W4-tail
  evidence archive, verified against its original manifest. Its historical
  gzip-to-XZ transport notes describe that prior publication only. This refresh
  is built directly as XZ and never embeds another archive.

Older BF16 records report CUDA Graph/CUPTI timing but predate strict per-record
timing guards. The original GLM5 comparison is preserved unchanged; no new
MegaMoE timing is implied. All prior publication directories remain untouched.
The PR-body draft and publisher logs are excluded from the archive.
