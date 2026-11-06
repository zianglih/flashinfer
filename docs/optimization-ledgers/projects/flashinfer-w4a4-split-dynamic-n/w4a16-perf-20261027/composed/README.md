# Final W4A16 composition evidence

The analyzed source is `1496b557f9b606f3a0bb36bcebf5293d3e11555a` plus full-index patch SHA256 `e0234935df4e703d30cfdd82c50d6366a66493782c2f24e5368936c7969ea91c`, deployed as `composed-final-e0234935df4e`. The canonical deployment receipt is `../composed-final/deployment.json`; this folder's older `deployment.json` is not the timed source. The composition includes shared prepare, one shared FC1/FC2 CLC tactic flag, metadata synchronization cleanup, static weight dimensions/K-loop count and the max-active-cluster compile-cache key fix.

`collect.py` independently collected the remote source manifests, current source file hashes/diff/HEAD, native-cache receipt, worker/config/launch evidence, per-model phase receipts, observer source, all results/logs and per-token autotune snapshots. `analyze.py` verifies these bindings before writing the summaries. It does not run GPU workloads or mutate remote data. All 195 result-row routing identities and cache snapshots, 975 reported tactic-cache hits, both source manifests and all benchmark/observer hashes pass. Every CAAC measurement has exactly 100 raw samples whose median equals the recorded public benchmark row.

- `speedups.md`: full 13×3 speedup table, retention aggregates and compile/profile timing.
- `raw-median-speedups.csv`: all 39 model/token cells with C0/A1/A2/C3 medians, geometric means, repeat ratios and actual selected tactics.
- `raw-samples.csv`: all 15,600 CAAC samples.
- `summary.json`: exact numerical values, group definitions, tactic choices, routing identities, source identity and validation counts.
- `evidence/`: 247 raw/source/launch files, including the candidate's native 46-tactic AUTO results and cached controls.

The benchmark uses `benchmarks/bench_moe_deepseek.py`, V3 EP8 on GPU4, V4.1-Flash EP4 on GPU5 and Kimi K3 EP8 on GPU6. Each candidate performed fresh native AUTO over 46 W4A16 tactics, then the same GPU ran control/candidate/candidate/control cache-only replay. The control is the original1496 implementation with its existing native AUTO winners. Timing uses 10 warmups and 100 CUPTI CUDA-graph replays with cold L2. The family flag includes activation quantization for quantized-input arms, but W4A16 takes BF16 input directly and has no standalone activation quantizer. Fused finalize is disabled. See the saved phase commands for exact invocation.

Retention excludes tokens1/2. Decode is tokens4,8,16,32,64,128,256,512; prefill is4096,8192,16384. The 33-cell aggregate is effectively neutral (0.9999x); per-model aggregate is0.9961x V3,0.9943x V4.1-Flash and1.0093x K3. These results support the implementation consolidation and instruction simplification but do not establish a broad end-to-end speedup.

The largest apparent regression, V4.1-Flash T16384 at0.9475x, has a control-repeat shift from1.4433ms to1.5564ms, and every arm spans roughly1.28–1.64ms. Candidate medians are1.5754ms and1.5881ms; it chose N192/shared CLC versus control N128. Preserve the measured ratio, but this single run does not establish a stable5.2% kernel regression. K3 T4096 at1.0629x also has control drift (0.5710/0.5398ms), though both candidate medians (0.5224/0.5223ms) are faster than both controls. Smaller decode regressions at K3 T8/T16 and V4.1-Flash T512 are repeat-stable and use different selected tactics. No repeated run was launched for this analysis.

AUTO times are host wall time: `cute.compile` includes SDK cache work; profile-exclusive time excludes nested compilation but still includes warmup, graph capture, GPU waits and profiling machinery. It is not pure tactic traversal. All converted fields explicitly use `_seconds`; raw nanoseconds remain in evidence.

Correctness gates are owned and reported separately by the root agent. An earlier gate command selected an incorrect pytest class; that collection error is unrelated to these complete timing runs.
