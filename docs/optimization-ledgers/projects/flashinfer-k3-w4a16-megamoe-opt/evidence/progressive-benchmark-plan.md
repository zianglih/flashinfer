# Progressive candidate comparisons

Keep `full-base-v2` as BEFORE and `full-native-v2` as the current optimized result. Each new candidate gets one fresh 13-point measurement and is compared against both saved runs. No baseline repeats are queued. Report cumulative baseline/candidate and incremental current/candidate ratios from their raw medians, preserving each implementation separately.

Every future candidate covers `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only 1 and 2 are excluded from retention. Keep 100 samples / 3 warmups unless wall evidence changes. No minimum process count or request for another baseline is introduced.

## Recorded wall cost

| Run | Process wall s | Four final timing calls s | Timing share |
|---|---:|---:|---:|
| native-auto-v3-a1 | 275.844 | 1.692 | 0.613% |
| native-auto-v3-tanh-b | 263.152 | 1.724 | 0.655% |
| native-auto-v3-a2 | 273.430 | 1.737 | 0.635% |

Per-point final timing calls were 0.35–0.57s with 100 samples. Reducing those samples cannot remove the ~99.4% outside this timing scope. Existing logs do not separate fixture creation, compilation, autotuning, allocation and teardown; do not label the remainder solely compilation. Exact data are in `progressive-benchmark-overhead.json`.

## Faster screening without changing token coverage

The native driver recreates shared EP weights at every token point. Its W4A16 AUTO warmup evaluates 8 tactics; each has 3 eager warmups, 6 untimed graph replays and 10 event-timed replays. The user-facing `--iters` controls the later CUPTI measurement, not this sweep.

A recorded-winner screen can choose one tactic per exact global token from `full-native-v2`, avoiding the other candidate compilations/allocations while preserving all 13 workloads. A small external wrapper around `_benchmark_distributed_megamoe` could copy `args`, set that point’s fixed knob dictionary, call the unchanged native function, and record the mapping plus its source capture. It should leave fixtures, PDL, reduction/combine controls, cold-L2 graph timing and raw sample collection unchanged. This wrapper is proposed, not implemented or launched.

Do not substitute the existing persistent knob cache: its key uses `ceil(global_tokens/8)`, so T1/T2/T4/T8 share capacity 1 and later winners overwrite earlier ones. Nor does the current native CLI accept a different fixed dictionary per point. A global fixed tactic would change the comparison at some shapes.

A fixed-winner result is screening evidence. Promising candidates receive a fresh native AUTO run over all 13 points; compare that new result against the saved BEFORE and current AUTO results. Reuse completed intermediate results directly. Label policy/tactic differences and retain per-process counts; never pool different implementations or average their medians.

For future per-point overhead diagnosis, host-only timestamps around fixture creation and `layer.warmup()` can distinguish setup from tuning without changing timed work. Existing captures cannot recover that split. No source edits, active-queue edits, remote processing or GPU work were performed for this plan.
