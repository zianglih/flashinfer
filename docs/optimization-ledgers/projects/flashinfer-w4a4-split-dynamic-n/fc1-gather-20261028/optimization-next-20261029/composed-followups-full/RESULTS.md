# Composed follow-up full refresh

Retained source: `374ed4c07ee3a8c30a30026018a96d8f613ac4b5`. The frozen remote source matches all 514 measured files byte for byte. Existing integration gates passed: 23 swap-AB and 4 W4A16 cases. No sanitizer was run.

- Full refresh: 31 jobs, 468 cells, two fresh 100-sample CUPTI passes per cell; 93,600 samples. All four models, EP and TP, with the frozen native winners; no autotuning or baseline reruns.
- Ordinary NVFP4 and per-token NVFP4 include input quantization; W4A16 receives BF16 directly. All swap-AB outputs are unfused. The 13 measured token counts include 1/2; displayed and aggregate rows begin at 4.
- All 62 phase receipts, source hashes, routes, native winner cache hits and CUPTI-only timing checks passed. All 1,088 loaded MoE kernel records passed their runtime register guards. No instrumentation compile flags were added; W4 FC1 retains its native `maxrregcount=96` option. All recorded MoE kernel local-memory attributes are zero; this does not inspect native quantizers.
- Stock GPU clocks were not changed. NVML observed 3,741 of 3,744 quartile windows; three empty windows are explicitly unavailable. Largest A1/A2 spread: 6.68% (V41F EP W4A16, 8,192 tokens), followed by 5.66% (K3 EP W4A16, 8,192 tokens). Small differences in these cells are inconclusive.

| Topology | Decode 4–64 | Middle 128–512 | Prefill 4096–16384 |
|---|---:|---:|---:|
| EP | +1.49% | +0.57% | −0.34% |
| TP | +1.64% | +4.52% | +15.22% |

These are geometric-mean speedups against the saved original PR7290 `d35fcfda` controls. The baseline is reused historical data, so this is a refreshed scoreboard, not a new same-GPU causal comparison. All 468 candidate measurements are fresh. Supplementary nine-column tables reuse the previous TRTLLM and non-swap baseline fields exactly, preserving unsupported cells and legacy fused-finalize markers.

Evidence:

- `completion.json`: hashes of source, gates, archives, analyses and publication data.
- `evidence/analysis.json`: all raw-sample timing and component analyses.
- `evidence/runtime-guard-summary.json`: loaded MoE kernel guard audit.
- `evidence/clock-summary.json`: repeat spread and telemetry limitations.
- `publication/report/`: primary five-dtype tables and eight compact A2 raw panels.
- `publication/external/`: unchanged historical external baselines with fresh candidate timings.
- `incremental-0.tar.gz` and `incremental-13.tar.gz`: all raw job evidence; SHA checks are recorded in their JSON receipts.

The original downloaded telemetry analyzer assumed every quartile had an NVML sample. The local `analyze_perf_with_telemetry_gaps.py` / `analyze_full_with_telemetry_gaps.py` postprocessors explicitly record absent samples instead. This changes no timing, source or GPU execution. Original raw helpers are preserved in `evidence/`.
