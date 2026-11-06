# Final retained-head benchmark refresh

Head: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. All 15 jobs and 30 candidate passes completed across 15 B300 GPUs: **936 medians / 93,600 strict CUPTI samples**, covering 468 unique current workloads. EP contributes 494 medians; TP contributes 442. The 1,303-file archive, 348 source files, frozen selected tactics, routes, caches, raw sample medians, native output and clean source postflight passed independent checks.

- [EP table](report/ep/summary-table.md) · [EP plot](report/ep/plots/swap-ab-speedup-table.png) · [raw native A2 output](report/ep/native-a2-output.md)
- [TP table](report/tp/summary-table.md) · [TP plot](report/tp/plots/swap-ab-speedup-table.png) · [raw native A2 output](report/tp/native-a2-output.md)
- [Independent raw/report audit](scheduler-refresh-review.json) · [archive verification](evidence-verification.json) · [runtime/image binding](runtime-image-binding.json)

Each plot/table has 44 rows and nine comparison columns; tokens 1 and 2 were measured but are excluded from display. All 936 saved baseline slots remain unchanged, including 156 unsupported slots. TP V41F MX and K3 MXFP8 remain unsupported; those cells are N/A. Positive percentages mean swap-AB is faster, computed as `(baseline/current - 1) * 100`. Non-swap MX controls that require fused finalize remain marked; current swap-AB is unfused.

**Remaining gaps:** 78 of 84 displayed TP prefill comparison cells are negative, versus 11 of 96 for EP. These count comparisons, not unique workloads. V3 TP8 MXFP4x8 at 8,192 tokens remains 37.16% below the saved fused non-swap CuTe control; V3 EP8 MXFP4x8 at 16,384 tokens remains 9.52% below it. This refresh does not show that the prefill gaps are closed.

Runtime: two existing `nvcr.io/nvidia/pytorch:26.05-py3` devboxes, Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA 13.2, CuTe DSL 4.8.0, cupti-python 13.4.0. CPU-only live runtime/tool captures match the historical image request/preflight and GPU UUID sets; the image tag is a receipt-bound reuse, not an inferred live digest. Timing uses the existing public API, frozen winners, input quantization for NVFP4, 10 warmups and 100 CUPTI cold-L2 samples per median. External baseline measurements were not rerun.

The [concise validation text](validation.md) and [command/result artifact](commands-and-results.md) are frozen for publication. No broad pytest or sanitizer rerun was performed this iteration. Historical qualification remains labeled by its original source.

Collection preserved `fetch-attempt1.log`: an output-path error occurred after verified extraction. The corrected helper resumed archive verification; no GPU work or benchmark data was repeated or substituted. No public writes were made by this collector.


Publication completed and read back exactly: [PR #7290](https://github.com/flashinfer-ai/flashinfer/pull/7290), source `61249e0b`, immutable assets `de8e93dd544f754b2e8d72441a52901fef7c7e05`. Receipt: `publication/publication.json`.
