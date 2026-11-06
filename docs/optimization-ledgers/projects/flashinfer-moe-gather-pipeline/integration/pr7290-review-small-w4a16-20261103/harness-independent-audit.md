# Independent three-arm replay harness review

Read-only review of `payload/configure.py`, `payload/run_job.py`, current observer/resolution helpers, `payload/warm_native.py`, `payload/nvml_clock_wrapper.py`, frozen expected choices, and `report.py`.

- No launch-blocking issue found in the inspected source.
- OFF cache migration reconstructs the old baseline key and verifies equality before removing the upstream-deleted `local_expert_offset` field. ON retains the recorded swap-AB winner. Before/native metadata rebinding preserves entries. All 24 baseline and 24 swap-AB selected small-token choices are explicit, with no `-1` default tactic.
- Runtime checks reject cache misses, fresh profiling, cache mutation, different fresh routes across arms, non-CUPTI timing, changed source Python files, mismatched native data symlinks, and malformed sample counts. Existing strict timer wrapper enforces cold L2 and CUDA graphs. W4 resolution observation checks actual tiler/cluster/raster against the selected tactic.
- Configuration is three-arm before/OFF/ON/ON/OFF/before on one GPU per workload, four model geometries in EP and TP at tokens 4/8/16. 8 jobs × 3 tokens × 6 phases × 100 samples = 14,400 per GPU family.
- Report uses the geometric mean of two phase medians for each arm and `before/current - 1`. It checks exact before/OFF tactic equality, repeated tactic identity, routes, results hashes, raw medians, sample validity, and expected topologies. The aggregate geometric mean and phase-spread marker are consistent with this design.

Boundaries: B200 replays B300-origin frozen choices, explicitly disclosed; this is not independently optimal B200 autotuning. Both current arms use the same native source/cache, while pre-PR uses its own normal-loader native cache. All measured phases include read-only 2ms NVML polling; the polling helper already describes its diagnostic host-scheduling boundary. The plot marks repeat spread, not clock stability. Inspect the retained telemetry before attributing any negative cell to source changes. No performance result is inferred by this source audit; runtime receipts and final sample datasets remain pending.
