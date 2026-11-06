# Read-only GPU clock telemetry

`nvml_clock_wrapper.py` wraps an unchanged benchmark command in a separate host process. It reads SM/graphics/memory clocks, performance state, clock-event reasons, power, temperature and utilization. It neither creates a CUDA context nor enables CUPTI activities; `cupti.get_timestamp()` provides the activity-timestamp clock domain for correlation. It does not change clock, power, persistence or benchmark settings.

```sh
<runtime-python> nvml_clock_wrapper.py --gpu 6 --interval-ms 2 --output <new-output> -- <unchanged-command>
```

Use the existing runtime's `python_deps` in `PYTHONPATH`. Physical NVML indices and UUIDs are supported independently of the child's `CUDA_VISIBLE_DEVICES`. Polling can affect host scheduling, so these are diagnostic runs, not replacement retention measurements. Ten milliseconds is sufficient for broad campaigns; two milliseconds gives finer evidence for short K3 prefill kernels. NVML values themselves can update more slowly than sampling.

Each row brackets NVML reads in CUPTI timestamp and `perf_counter_ns`; receipt calibration records the relationship to wall time. On the current B300 runtime, CUPTI timestamps are epoch-like and differ substantially from `perf_counter_ns`, so do not compare those raw domains directly. Prefer CUPTI timestamps against captured activity events.

Smoke test on `fi-gather-opt-1029`, GPU6, 2026-10-29: 26 samples at 10ms, all fields supported, exit0; no compute context left behind. The first timestamp read lazily initializes its library; subsequent calibration reads are submicrosecond. Raw smoke receipt lives in `w4a16-k3-clock-profile/evidence/smoke/` after download.
