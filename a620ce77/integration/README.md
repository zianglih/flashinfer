# PR7290 retained-source refresh

This is integration validation and a fresh candidate measurement, not an optimization experiment. Source is merge commit `a620ce7790b32f7f0ae524a811417d2c6cee1152`, parents `82254e20` and `8bc69ee4`, tree `781f85c3` (identical to the retained fork). The complete 13,245-file inventory differs from `c1ac` only in the requested W4 helper restoration to `d5105227`.

- `plan.json` and `screen/perf-config.json` bind 31 frozen jobs, 36 supported arms, 468 cells and two fresh candidate phases. Both 100-sample medians are retained: 93,600 strict CUPTI spans, 10 warmups, cold-L2 CUDA graphs. Tokens 1/2 remain raw; 396 rows are eligible for retention summaries.
- `harness-proof.json` pins all 12 performance helpers byte-identically to the completed current-runtime cumulative campaign. NVFP4 input quantization is timed. Original routes/tactics and ten existing W4 default choices are preserved; no autotuning or baseline reruns.
- `screen/launch-preflight.json` binds the current 046 native cohort, canonical generated/CUBIN inputs, private cached_ops/CuTe roots, normal loads/no-op, full source bytes and GPU UUIDs. `screen/gpu-release.json` records terminal source/cache closure and all eight GPUs idle.
- `smoke-summary.json` and `smoke-evidence/data` preserve seven existing exact calls and 21 actual captured native kernels, all LOCAL0, using unchanged compiler options. Smoke-only scheduler fixtures are confined to separate subprocesses and never enter performance.
- `fetch.py`, `report.py` and `postflight.py` reuse existing transport, AA replay and closure logic. All negatives, phase spreads, resource records and clock flags stay in the report.

Historical TRTLLM, legacy and pre-PR W4 denominators are reused without remeasurement. Fresh candidate versus historical baseline ratios are reference comparisons, not same-run causal comparisons. Publication is owned by the parent task.
