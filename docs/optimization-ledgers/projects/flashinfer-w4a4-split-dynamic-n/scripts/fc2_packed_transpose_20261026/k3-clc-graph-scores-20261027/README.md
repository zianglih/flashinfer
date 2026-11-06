# K3 NVFP4 T16384 public graph-tuning diagnostic

Graph tuning selected the same native all-CLC tactic as the eager/cold control. Enabling the public graph-profiling flag alone did not resolve the N256 versus N128 selection gap at this point.

| Tactic | Eager/cold profile (µs) | Graph/cold profile (µs) |
|---|---:|---:|
| Native winner: N256, M256/256, 2CTA/2CTA, K4/4 | 952.784 | 952.096 |
| Best N128: M256/512, 2CTA/2CTA, K4/4 | 957.424 | 956.432 |

Both searches completed 160 successful W4A4 tactic profiles. The best N128 trails N256 by 0.49% with eager profiling and 0.46% with graph profiling. Both phases use CLC for every candidate. The selected tactic is `[256, [[256,256],[2,1],false], [[256,256],[2,1],false], [4,4], true,true]`.

The public measurement retained 10 warmups and 100 cold-L2 CUDA-graph/CUPTI samples with initial activation quantization included. The real sigmoid route IDs, weights and histogram match the eager diagnostic exactly. Public medians are 909.670 µs (eager-selected) and 904.103 µs (graph-selected); these sequential single measurements use the identical winning kernel and are not paired performance-retention evidence.

## Scope and provenance

- Frozen all-CLC source: `7f4e1703d984831efc13eea63a868b3e558d243b` plus source patch `97cf417da9591d530dd5febf3163c1525fabd9c399ce1a6c4a089cba4992f528`. Source hashes match the eager diagnostic and were verified unchanged after the run. This source predates the retained metadata and packed-output cleanup.
- The task-local benchmark changes only the wrapper call's public `autotune_use_cuda_graph=True` argument. Original benchmark SHA256: `544a572f0560d15a93e63a666b8b7d0ba41e1f4a323616cc7d42e4fb049994a2`; modified SHA256: `c74dd346d6845b4c73832c4a186f88e426d455ee6e20fc819da5caddb50470a7`. The exact patch is `../graph-benchmark.patch`. Production benchmark and kernel files were not edited.
- Public `autotune(tuning_buckets=(16384,))` limits the diagnostic to one token bucket without filtering native tactics. The observer uses the existing `profile_backend='cute-dsl'` selector with `profile_cuda=False` to skip W4A16, which explicitly rejects graph tuning, while preserving the normal public measurement path.
- The selection cache started empty and contains the `cuda_graph` key component. Every successful profile was directly observed with `use_cuda_graph=True` and `use_cold_l2_cache=True`; every timed call hit the resulting native winner. Source-private compilation storage reused the persistent native C++ modules.
- Hardware/environment: one B300 (GPU4) in `fi-moe-nvfp4-port-1026`, c3/infra, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. GPU4 was verified idle before and after; `gpu-release.json` records release.
- This changes the profiling execution method only. Synthetic balanced routes, omission of initial quantization from the internal profile, and real-route public timing remain distinct. The result does not isolate the separate effects of scheduler mapping, geometry, buffer depths or routing distribution.

Full profile scores and raw 100-sample timings are in `observed/results.json`; full DEBUG output is `driver.log`; frozen source/launch/verification metadata is `receipt.json`. `summary.json` is independently generated and validated by `../analyze_graph_scores.py`. W4A16 was not invoked in this graph diagnostic.
