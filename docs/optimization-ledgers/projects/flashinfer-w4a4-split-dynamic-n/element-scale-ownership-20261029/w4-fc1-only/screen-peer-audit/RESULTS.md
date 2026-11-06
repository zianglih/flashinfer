# Thin W4 FC1-only: independent initial 16-cell audit

**Passed the evidence audit; this is not a retention recommendation.** Candidate W4 kernel `1debc908790cd7fc67f6b9f16f498adf5350053012ba7f913d07b0245d282484` is compared with retained `658a0c8942c7454050f990c0be3083aa61b6a89f`. This screen is separate from the full elements/scales A and crossed B experiments.

| Scope | Cells | Speedup |
|---|---:|---:|
| All | 16 | +0.511% |
| Decode, 4 tokens | 8 | +0.541% |
| Prefill, 4096 tokens | 8 | +0.481% |
| EP, all | 8 | +1.634% |
| TP, all | 8 | −0.600% |
| EP decode / prefill | 4 / 4 | +1.228% / +2.041% |
| TP decode / prefill | 4 / 4 | −0.142% / −1.055% |

The metric is `100 × (sqrt(C1 × C2 / (A1 × A2)) − 1)`, using each phase's median of 100 CUPTI samples. Group summaries are geometric means of these ratios. This follows this campaign's existing analyzer; it is not the arithmetic phase-average estimator used by some older W4 experiments. All six negative cells are preserved. See [all 16 raw phase rows](table.md) and [machine-readable rows](cells.csv).

## Replayed evidence

- All 6,400 raw samples across 32 complete C–A–A–C phases: finite durations, exact reported medians, no CUDA-event fallback, and CUPTI activity-span equality. Exactly two W4 GEMMs and no quantizer execute in each sample; routing may have additional kernels. Component durations are descriptive; overlapping kernels are not added to infer end-to-end time.
- Same physical GPU within each four-phase job; frozen routing identities, tuner keys, runners and explicit FC1/FC2 tactics match saved native winners. No profiling/autotuning or new admitted tactics. The actual loaded route-N, instruction CTA-group and K match those tactics; the instruction CTA-group derives from M=256, not merely the cluster size.
- Source comparison verifies all 3,165 bound source files in both arms. Only the W4 kernel differs. Benchmark, quantization, routing, shared helpers and swap kernel are unchanged. All seven observer/helper hashes, logs, result and source receipts, managed-cache manifests and original frozen entry bytes are checked.
- 32 actual-driver guard receipts / 128 loaded functions: 64 FC1 functions have 96 initial registers and 640 threads; 64 FC2 functions have 128 initial registers and 512 threads. Every function reports LOCAL=0; donation/pool checks are independently recomputed. Original FC1 `-maxrregcount=96` options and normal FC2 options are preserved. This is loaded-driver evidence, not a new SASS inspection.
- The completed V41F TP pilot is reused unchanged for two of the 16 cells. Its original `triage/perf-config.json` hash is `a005b938dcf1959d2e7ad81ee92dad360ca3a1fa0eed647889e6db794bf5e1d7`; its receipt is byte-identical. All shared settings and the selected job match the later screen config; only output path, prose and the added seven jobs differ. Seven other jobs are fresh extensions. No phases from failed/incomplete jobs are salvaged.
- Eight candidate smoke cases passed the existing bit-exact W4 oracle, with 16 source-bound loaded functions, all LOCAL=0. Coverage includes one/two CTA, static/CLC, PDL off/on, tiny/partial and long K, repeated metadata work, and original/swap weight layouts. Correctness-only cluster caps do not enter performance runs. This is focused coverage, not the full correctness matrix or sanitizer.

## Repeat and clock limits

All 256 quartile windows have NVML samples. Maximum within-arm phase spread is 2.796% control and 2.536% candidate. The following observed quartile medians differ from 2032 MHz; no clock settings were changed:

| Cell | Phase / quartile | SM MHz median | Event reasons |
|---|---|---:|---|
| V41F EP, 4096 | A1 / Q4 | 1605 | 0 |
| K3 TP, 4096 | C1 / Q4 | 1799.5 | 0 |
| K3 TP, 4096 | C2 / Q4 | 1972 | 0, 4 |

These observations do not establish the cause of an individual timing change. In particular, K3 TP prefill is −2.983% with control/candidate spreads 1.545% / 2.536%; V41F TP prefill is −1.397% with 0.233% / 2.432% spread even though its quartile medians remain 2032 MHz. K3 EP prefill is +6.335%, with 1.995% / 0.061% spread. V41F EP prefill is +1.748%, with 2.796% / 0.689% spread and the clock exception above. Two phase repeats do not provide statistical confidence intervals. Nothing is filtered or replaced.

## Reproduction and extension boundary

Run `python3 element-scale-ownership-20261029/audit_thin_w4.py screen` from the project root. It reads frozen raw evidence and writes only derived local audit artifacts. [summary.json](summary.json) binds the script, source and config hashes; [evidence-hashes.json](evidence-hashes.json) lists 241 directly bound evidence documents. [phase-components-and-clocks.json](phase-components-and-clocks.json) preserves all phase components and quartile telemetry.

The broader 24 points at 64/512/16384 tokens are a separate pending data audit. Its passive resolved-default observer needs an additional check when this replay is extended: seven recorded `-1` choices must resolve through the unchanged host default and join to actual native geometry, without cache misses. The initial 16 do not use that default expansion and remain immutable.
