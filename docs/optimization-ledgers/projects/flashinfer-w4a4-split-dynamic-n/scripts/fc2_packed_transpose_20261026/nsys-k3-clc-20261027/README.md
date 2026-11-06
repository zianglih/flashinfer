# K3 NVFP4 T16384: published versus all-CLC native choices

B300 GPU4, CUDA13.2 PyTorch26.05 container, three cold-L2 public CUDA-graph profile replays per source. Initial NVFP4 quantization is included; fused finalize is disabled. Saved AUTO cache hits and route identity are verified. These traces diagnose phases and overlap; they do not replace the CAAC retention benchmark.

| Phase | Published (µs) | All-CLC (µs) | Difference (µs) |
|---|---:|---:|---:|
| input quantization | 27.424 | 27.584 | +0.160 |
| route count init | 3.968 | 4.064 | +0.096 |
| route indexing | 6.528 | 6.688 | +0.160 |
| input prepare | 27.168 | 28.865 | +1.697 |
| FC1 | 434.339 | 533.892 | +99.553 |
| FC2 | 224.258 | 234.369 | +10.111 |
| combine | 75.809 | 75.649 | -0.160 |

Published native tactic: N128, FC1 M128/1CTA/K8/3operand/2acc stages; FC2 M256/2CTA/K4/6operand/2acc stages, static scheduling in both phases. All-CLC native tactic: N256, FC1/FC2 M256/2CTA/K4/5operand/1acc stage. Thus the comparison changes geometry and buffering as well as scheduler; it is not causal evidence that the scheduler alone adds this cost.

The FC1 phase accounts for most of the visible slowdown. Adjacent PDL overlap and total chain spans are in summary.json; overlapping kernel durations must not be summed as total latency. No instruction-stall cause can be inferred from NSYS alone. Follow-up work should compare equivalent geometries and investigate why the CLC search prefers the wider single-accumulator tile.

Sources/caches and exact commands are in receipt.json; effective core configs are in each observed receipt. Both source trees and cache files remained unchanged. GPU4 was released after successful capture/export.

## Native tuning evidence boundary

The saved standard-NV T16384 winner is N256 M256/256 K4/4 CLC/CLC. Its cache entry explicitly records `l2_cache_policy=cold`; `CuteDslFusedMoERunner.tuning_config` sets `use_cold_l2_cache=True`, and the current autotuner cold event path flushes twice the device L2 before every independently timed graph sample. This is not evidence of a warm-tuner/cold-benchmark mismatch. Original logs are INFO-level and the JSON cache retains winner plus profiling policy, not per-tactic times. No historical N128-versus-N256 score ranking can be reconstructed.

A distinct profile-input boundary exists: `_inputs_helper.py` replaces routes with balanced approximate maximum-rank load. At K3 EP8 T16384/top16, it creates33030 local rows, 294 or295 per expert:336 N128 token tiles or224 N256 tiles. The public sigmoid-route workload has33208 local rows,148–550 per expert:314 N128 tiles or189 N256 tiles. These distributions differ even though both timing paths start cold. The synthetic profile also times the MoE wrapper without the benchmark's initial quantizer. These facts justify measuring existing candidate scores under matched real routes before changing generic selection policy; they do not establish the cause of the observed FC1 slowdown.

Source references, relative to the frozen7f4 candidate tree: `flashinfer/fused_moe/cute_dsl/tuner.py:577-685`, `flashinfer/fused_moe/cute_dsl/_inputs_helper.py:82-109`, and `flashinfer/autotuner/autotuner.py:3538-3634`.
