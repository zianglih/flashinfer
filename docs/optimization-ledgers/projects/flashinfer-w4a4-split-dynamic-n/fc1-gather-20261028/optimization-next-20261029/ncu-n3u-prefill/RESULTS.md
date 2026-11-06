# N3U EP8 16K: CUPTI completion breakdown

The fixed-tactic W4A4 slowdown is entirely in the FC1 portion of the timeline after accounting for the removed prepare kernel. FC2 has a longer reported kernel duration because it overlaps more of FC1; its completion tail is unchanged. MXFP4x8 shows the same FC1 direction, but capture drift prevents precise attribution of its total gap.

- **Sources:** retained PR7290 `d35fcfda03875077b3af8455575cc1d20e866a8c` versus the frozen composition now retained as `7106faf3082f63f3c94a4dc04b7fd0a77388f209`. Candidate kernel SHA256 `0d44e4d71465b29a565995febdad42ef168060d1ae2858df5b2611ca998f70ee`; remote checkout is still fb66 plus the measured patch.
- **Run:** B300, C3 `fi-fc1-gather-1028`, `nvcr.io/nvidia/pytorch:26.05-py3` / CUDA13.2. W4A4 on GPU0 and MXFP4x8 on GPU3, one control then one candidate capture each. Same frozen winners/routes, no autotuning, 10 warmups and 100 strict CUPTI samples, CUDA Graph / cold L2, public API, swap-AB unfused. W4A4 includes the input quantizer.
- **Instrumentation:** only CPU-side activity serialization after CUPTI flush/disable/finalize. Removing the callback reproduces the original public timer AST exactly. No repository edits, GPU work or launch order changes.
- **Validation:** all400 spans equal their public CUPTI timing samples exactly. Expected kernel sequence and increasing end times hold in every iteration. Routes, winners, public caller, benchmark and timer hashes match across each pair. Candidate runtime guards pass with zero local bytes and unchanged compiler options.
- **Boundary:** diagnostic captures, not interleaved CAAC retention measurements. Kernel durations include PDL waits and overlap. Completion increments are additive timeline accounting, not exclusive execution time or causal per-stage costs.

## W4A4

Frozen tactic: `[128, [[256, 128], [2, 1], False], [[512, 128], [2, 1], False], [4, 4], False]`. Both stages use static scheduling and two-CTA MMA.

| Stage | d35 duration (µs) | 7106 duration (µs) | d35 completion increment (µs) | 7106 completion increment (µs) | Increment change (µs) |
|---|---:|---:|---:|---:|---:|
| quantize | 17.015 | 17.034 | 17.015 | 17.034 | +0.020 |
| route_init | 3.443 | 3.474 | 0.925 | 0.926 | +0.001 |
| route_indices | 10.236 | 10.229 | 9.925 | 9.916 | -0.009 |
| prepare | 19.863 | 0.000 | 19.505 | 0.000 | -19.505 |
| fc1 | 226.620 | 447.702 | 224.391 | 447.360 | +222.969 |
| fc2 | 202.029 | 217.665 | 186.580 | 186.291 | -0.289 |
| combine | 57.844 | 58.012 | 54.272 | 54.217 | -0.056 |
| **Total span** | — | — | **512.613** | **715.744** | **+203.131** |

The table uses means so the completion increments sum exactly. Public end-to-end medians: **512.675→715.748 µs**.

| Overlap | d35 mean (µs) | 7106 mean (µs) |
|---|---:|---:|
| fc1_fc2 | 15.449 | 31.374 |
| fc2_combine | 3.571 | 3.795 |

Consecutive 25-sample span means (µs):

- d35: 512.56, 512.29, 513.03, 512.57.
- 7106: 715.74, 715.78, 715.80, 715.66.

Both captures are stable over their 100 samples. FC1 reaches completion203.48 µs later from the beginning of the pipeline despite saving19.51 µs of prepare completion time. FC2 and combine account for approximately−0.35 µs of the total203.13 µs increase. This corroborates the saved iKET signal of slower FC1 accumulator production; it does not identify whether the underlying cause is TMA issuing, repeated traffic or dependency latency.

## MXFP4x8

Frozen tactic: `[256, [[256, 256], [2, 1], False], [[256, 256], [2, 1], False], [4, 4], False]`. Both stages use static scheduling and two-CTA MMA.

| Stage | d35 duration (µs) | 7106 duration (µs) | d35 completion increment (µs) | 7106 completion increment (µs) | Increment change (µs) |
|---|---:|---:|---:|---:|---:|
| route_init | 1.338 | 1.239 | 1.338 | 1.239 | -0.099 |
| route_indices | 11.192 | 10.521 | 11.019 | 10.355 | -0.664 |
| prepare | 31.965 | 0.000 | 31.786 | 0.000 | -31.786 |
| fc1 | 354.277 | 472.152 | 349.877 | 471.807 | +121.930 |
| fc2 | 351.276 | 344.293 | 325.757 | 307.451 | -18.306 |
| combine | 60.209 | 58.057 | 56.051 | 54.259 | -1.791 |
| **Total span** | — | — | **775.827** | **845.112** | **+69.284** |

The table uses means so the completion increments sum exactly. Public end-to-end medians: **779.060→831.605 µs**.

| Overlap | d35 mean (µs) | 7106 mean (µs) |
|---|---:|---:|
| fc1_fc2 | 25.520 | 36.842 |
| fc2_combine | 4.159 | 3.798 |

Consecutive 25-sample span means (µs):

- d35: 739.56, 749.29, 805.07, 809.40.
- 7106: 831.19, 830.21, 828.07, 890.98.

The control drifts from739.56 to809.40 µs and the candidate from831.19 to890.98 µs across quartiles. Thus the apparent−18.31 µs FC2-tail improvement and the exact+69.28 µs total change must not be treated as stable causal measurements. FC1 completion-increment growth is visible even with that uncertainty, consistent with the W4A4 diagnosis.

## Next useful direction

Existing native retuning on clean fb66 selected FC1 M512 for N3U EP16K W4A4 and improved end-to-end performance 21.86%, without adding tactics. This reduces repeated activation gather across output-channel tiles. Replay that winner on the final composition before considering more resource or scheduling axes. The metadata simplification now under full validation is also consistent with reducing gather issue overhead. This diagnostic does not justify changing FC2 for these N3U EP gaps.

## NCU limitation

Nsight Compute 2026.1.1.0 connected but did not pass the first CUDA allocation in two bounded smokes. A native sm_103 fixed binary completes unprofiled, then hangs under one-metric NCU with clock/cache control disabled and config-file disabled. The Python smoke was stopped at 90s and native smoke at 60s; processes were cleaned up and GPUs released. No full MoE NCU run or usable hardware counters were produced. This does not establish a MoE correctness failure or a profiler root cause.

## Evidence

- `summary.json` includes all400 per-iteration timelines and aggregate statistics; `analyze_timeline.py` validates source, routes, tactics, runtime guards, raw hashes and exact timer agreement.
- `evidence/timeline-{nvfp4,mxfp}/{control,candidate}/{receipt.json,capture/timeline.json,observer/results.json}` contains source-bound raw evidence.
- `evidence.tar.gz`: SHA256 `8c797f86ccdeb04873eb453b015c4a389aab73611e1c25b5740c32035112aa36`.
- `evidence/{smoke-receipt.json,native-smoke-receipt.json,native-smoke.cu}` preserves profiler failures.
