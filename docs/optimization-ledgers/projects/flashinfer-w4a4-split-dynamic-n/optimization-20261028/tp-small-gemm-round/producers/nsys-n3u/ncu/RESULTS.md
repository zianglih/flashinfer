# N3U EP MXFP4x8 FC1/FC2 diagnostic

Source `1054743780dda2919c1424124c1e3258248b8c19`, N3U EP8 / TP1, 16,384 tokens, frozen 83df A2 cache and identical route identity. Unmodified public benchmark profile path; no tuning. Both FCs select M256/N256, two CTA, static scheduling, Ksteps4.

B300, NVIDIA PyTorch `26.05-py3`, CUDA13.2, driver595.91.07, Nsight Compute2026.1.1.0. Application replay, five passes, clocks/cache control disabled, profiler range from the public benchmark, exactly two GEMMs. These are counters/diagnostic timings, not retention medians. NCU profiling changes concurrency, so its FC2 duration is not a replacement for the NSYS critical-span result.

| Metric | FC1 | FC2 |
|---|---:|---:|
| NCU duration (us) | 321.280 | 288.320 |
| Tensor peak, elapsed (%) | 72.250 | 75.710 |
| Tensor peak, active (%) | 76.210 | 80.560 |
| DRAM peak (%) | 29.310 | 36.740 |
| DRAM read (MB) | 461.633 | 620.713 |
| DRAM write (MB) | 260.691 | 191.802 |
| L2 read (GB) | 3.916 | 3.982 |
| L2 hit (%) | 74.270 | 66.260 |
| Warp instructions (million) | 83.884 | 16.182 |
| Issue active (%) | 27.960 | 5.710 |
| Eligible warps/scheduler | 0.300 | 0.060 |
| Barrier stall (%) | 19.150 | 21.280 |
| Long scoreboard stall (%) | 39.340 | 68.130 |
| Short scoreboard stall (%) | 8.550 | 1.530 |
| Wait stall (%) | 9.220 | 3.290 |
| Math pipe throttle (%) | 0.160 | 0.010 |
| MIO throttle (%) | 0.460 | 1.080 |
| Registers/thread | 234.000 | 110.000 |
| Dynamic shared memory (B) | 206592.000 | 206592.000 |

- Persistent grid148, 256threads/CTA, twoCTA/cluster; both shared-memory-limited to one CTA/SM. FC1 also has a oneCTA register limit. SM active-cycle average/max is96.84% /95.54%, so this capture does not show a large load-imbalance tail.
- Tensor utilization72.25%/75.71% is substantial; DRAM29.31%/36.74% rules out gross HBM saturation for these captures. Tensor utilization is a busy-cycle metric, not proof that arithmetic alone is the only bottleneck.
- FC1 executes5.18x FC2's warp instructions and has more short-scoreboard/wait activity, consistent with its activation+quantization epilogue work. This is a useful next attribution target, not proof that every added instruction lies on the critical path.
- Long-scoreboard/barrier totals are aggregated across producer, MMA and epilogue warps. They cannot distinguish TMA latency, TMEM dependencies and intentional ring waits without per-PC/role attribution. Do not delete barriers or enlarge pipeline depth based solely on these totals.
- Next bounded lead: inspect FC1 epilogue versus MMA/producer wait PCs and determine which creates tensor-idle intervals, retaining oneCTA/SM policy. Existing traces do not justify a new stage-count heuristic, another tactic axis or HBM-focused policy.

All12 raw archive files verified, including `.ncu-rep`, CSV, source/runtime bindings, exact command/environment, cache/route selection receipt and logs. `analysis.json` binds hashes. Earlier NSYS stages remain in parent `RESULTS.md`; neither matches the older N3U W4A4 T16K profile, so no causal old-versus-new profile claim.
