# MoE gather-pipeline benchmark evidence

Retained candidate: `02de7785c10847b3528340840bed40bd405d85b4`.
The immutable measurements record base `82254e20` plus their frozen source patches;
`retained-source-equivalence.json` verifies the retained source bytes.

- `report/`: all 468 candidate cells, both phase medians, repeated-pass variation,
  clock quartiles, and runtime-resource receipts. The 396 displayed cells omit
  tokens 1 and 2; every measured cell remains in the data.
- `plots/retained-speedup-{ep,tp}.png`: comparison with the historical full run
  measured at `326c4a79`, whose production implementation is equivalent to
  `82254e20`. This is a historical comparison, not fresh paired causal evidence.
- `external/` and `plots/swap-ab-speedup-table-{ep,tp}.png`: unchanged historical
  TRTLLM/non-swap baselines and pre-PR W4A16 layout baseline. Fused legacy MX
  measurements are marked with a dagger.
- `stdout/`: all 62 original native stdout files, including both printed CSV and
  native table output. Their bytes are preserved; 31 are final-pass logs.
- `completed-tables/`: 15 native family tables printed by the unchanged benchmark
  formatter from saved structured records: 468 current final-pass records and
  390 reused TRTLLM records (338 low precision, 52 BF16). No timing was rerun.
  All 31 original partial final-pass table outputs were first reproduced
  byte-for-byte. These single-pass tables differ from the two-pass heatmap
  aggregates. Original column order, precision, missing values and winner rules
  come directly from the benchmark printer.

The full refresh contains 93,600 strict CUPTI samples and 1,088 loaded MoE
functions with zero reported local memory. Ten recorded W4A16 defaults were
resolved to their existing native configurations and joined to 40 actual
FC-stage resource records; no retuning or event fallback was used. The runs used
stock clocks. Of 3,744 clock quartiles, 97 had a non-2032 MHz median or nonzero
clock-event reason; four lacked NVML observations, all in an excluded token-1
W4A16 phase. The largest candidate repeated-pass spread was 9.08%. All negative
rows and variation remain visible; no run was replaced to improve a result.

Against the historical production-equivalent baseline, the displayed geometric
mean is +0.059% overall (+0.039% swap-AB, +0.128% W4A16). These small changes are
instruction cleanups, not a claim of a broad throughput improvement. Independent
fresh paired experiments remain separate under the project evidence folders.

The older reused BF16 records report CUDA Graph/CUPTI timing but predate the
newer per-record strict timing guards. Full native CUPTI activity/sample JSON is
preserved in source-bound project and persistent-cluster evidence; this archive
contains the complete stdout, comparison data, provenance and plots.
