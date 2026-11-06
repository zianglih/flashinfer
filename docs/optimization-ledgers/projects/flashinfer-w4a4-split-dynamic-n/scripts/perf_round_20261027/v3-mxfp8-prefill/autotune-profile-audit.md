# Native AUTO profiling audit

Source: retained `f7182d5c871b367f4641d6d7e2098254d63147e3`; canonical HEAD verified. This is a read-only audit of the completed final public run, not a rerun or a new published result.

- `benchmarks/bench_moe_deepseek.py:170` uses plain `autotune(True, cache=...)`. Its public `--warmup 10 --iters 100` and CUPTI setting configure the final public timer, not native per-tactic profiling.
- `flashinfer/autotuner/autotuner.py:1714` defaults to 3 warmups and 10 profiling repetitions. The singleton is created with those defaults at line2095. The benchmark and observation helpers do not override them.
- `cute_dsl/tuner.py:687–694` enables cold L2 and CUDA graphs. Unspecified `TuningConfig.cuda_graph_profile_replays` defaults to1; there is no input arena/cold-chain override.
- Native v1 has no `MeasurementPolicy(timer="cupti")`, so `_profile_single_kernel` takes the CUDA-event cold-L2 path. It does 3 eager warmups, captures the runner, exercises the graph once, waits for stream completion, then queues a 100us delay and10 cold samples. Each sample zeroes a twice-L2-sized flush buffer before the start event, replays the graph, then records its end event. It synchronizes once after all samples and returns their median. The flush is outside each measured interval.
- Each admitted tactic is visited once in deterministic enumeration order. `choose_one` updates the winner whenever the new median is strictly smaller. There is no finalist recheck, confidence interval, randomized/counterbalanced candidate order, or clock/temperature stabilization measurement in this path. Route widths are enumerated16,32,64,128,256, so N128 precedes N256.
- V3 MXFP8 T8192 admitted320 tactics, admission hash `544c9757168f83f80ffa941eb787635e83cd5be041cd7800ef3e070420b89243`; admission0.00394318s, entire native context12.1450267s. The subsequent mixed-format context was11.1074282s. These contexts include profiling, graph/pre-warm setup, JIT/cache IO; they are not pure GPU time.
- The completed receipts retain the chosen tactic and aggregate nested host spans, not each tactic's median, sample vector, measurement timestamp, or thermal/clock telemetry. Debug per-tactic messages were not enabled. We cannot reconstruct the selected N128 versus N256 native timing margin or prove search-noise/thermal causation retrospectively.

## Bounded diagnostics on the unchanged source

All three comparisons retain4×100 raw cold-L2/CUPTI/graph public samples,10 warmups, exact route/source/cache checks, and CAAC ordering. Only task-local selection-cache copies change between the two already-supported tactics. Native cache files remain unchanged.

| Comparison | C1 / C2 us | A1 / A2 us | Paired C/A |
|---|---:|---:|---:|
| K3 T64 actual routes: N32 vs N16 |237.9215 /237.7290|238.7850 /238.8175|0.995913x|
| V3 MXFP8 T8192 actual routes: N128 vs N256 |481.4110 /480.5000|442.7070 /442.9470|1.086102x|
| V3 MXFP8 T8192 synthetic routes: N128 vs N256 |537.0600 /539.6510|528.2280 /529.6520|1.017799x|

The synthetic diagnostic substitutes only expert IDs with the exact existing `inputs_pre_hook` result. Public activations/weights/scales and outer routing remain unchanged. It is a routing-only intervention, not a complete reconstruction of native profiling's synthesized tensor values or CUDA-event timer.

Actual V3 routes need77 N128 tiles versus45 N256 tiles; synthetic balanced260/261-token expert counts need96 versus64. Synthetic routing materially shrinks N256's measured advantage but does not reverse the pair's ranking. This evidence does not justify changing the sampler or adding shape-based selection rules. K3 N16 is slightly slower; the width direction is stopped rather than expanding the tactic list to N8.

Evidence: `width-evidence/validation.json`, `synthetic-evidence/validation.json`, `../k3-n-width/evidence/validation.json`; phase-level diagnostic trace in `evidence/nsys-summary.json`. The public six-table results are unchanged.

## Existing API and timing tradeoff

At this exact revision, public `autotune()` has no `use_cupti` or `benchmark_iters` argument. Its timing-related override is `cuda_graph_profile_replays`. The public benchmark's `use_cupti` and iteration options affect final timing only. Native CUPTI is available through experimental `autotune_v2` with `MeasurementPolicy(execution_mode="cuda_graph", _timer="cupti")`; `_timer` is documented as an internal diagnostic override, and v2 persistence is deliberately disjoint from the existing JSON-cache workflow. Directly forwarding a flag to the current v1 context is therefore unsupported.

The native CUPTI implementation uses two device synchronizations per sample and activity enable/flush/disable per tactic; it returns the median of10 GPU kernel spans. The current event route queues10 cold samples and synchronizes after the batch. CUPTI could better match the public measurement objective, but it adds host/profiling overhead and does not remove the synthetic-input difference or fixed traversal ordering. No quantitative CUPTI AUTO cost has been measured for this run. A bounded task-local comparison of the same existing N128/N256 tactics via the existing diagnostic policy would distinguish timing-objective effects without changing global autotuner code, production benchmark cache semantics, or the tactic set. No such rerun has been started.
