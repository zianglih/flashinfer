## Native before/after performance

H7168/I2048/E256/top-k8, native precomputed routing, runtime unit FP32 FC1/FC2 alphas, deterministic combine, O3. Each arm freshly autotunes all eight native tactics. Three warmups and 100 cold-L2 CUDA-graph CUPTI samples per row; take each iteration's rank maximum, then its median. The full public-forward activity span includes alpha copies and all forward kernels. Fixture preparation, compilation, tuning, capture and L2 flushing are excluded. No samples are trimmed.

| Global tokens | EP4 before us | EP4 after us | Speedup | EP8 before us | EP8 after us | Speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 65.633 | 75.073 | 0.8742x | 79.953 | 73.216 | 1.0920x |
| 2 | 84.240 | 95.537 | 0.8818x | 88.288 | 94.704 | 0.9322x |
| 4 | 110.929 | 117.777 | 0.9419x | 102.160 | 101.761 | 1.0039x |
| 8 | 142.913 | 156.433 | 0.9136x | 131.936 | 129.440 | 1.0193x |
| 16 | 196.722 | 205.058 | 0.9594x | 143.073 | 137.921 | 1.0374x |
| 32 | 262.914 | 260.418 | 1.0096x | 168.113 | 163.809 | 1.0263x |
| 64 | 302.466 | 290.355 | 1.0417x | 189.569 | 186.704 | 1.0153x |
| 128 | 323.154 | 320.131 | 1.0094x | 195.840 | 196.273 | 0.9978x |
| 256 | 329.379 | 327.443 | 1.0059x | 203.857 | 199.568 | 1.0215x |
| 512 | 354.788 | 350.707 | 1.0116x | 207.041 | 201.825 | 1.0258x |
| 4096 | 814.855 | 807.494 | 1.0091x | 465.188 | 468.068 | 0.9938x |
| 8192 | 1462.221 | 1435.323 | 1.0187x | 790.070 | 788.245 | 1.0023x |
| 16384 | 2858.201 | 2862.633 | 0.9985x | 1522.037 | 1521.209 | 1.0005x |

Decode geometric speedup (global T4–512): EP4 **0.9858x**, EP8 **1.0183x**. T1/T2 and each prefill row are shown separately; EPs are not pooled.

All selected tactics (`epi` = epilogue return; `dispatch` = dispatch-warp return). Common fields for every row: `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","use_2cta_instrs":true,"flag_batch":4,"in_kernel_fc2_reduce":false,"num_sched_stages":2}`.

| Global tokens | EP4 before | EP4 after | EP8 before | EP8 after |
|---:|---|---|---|---|
| 1 | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N128/K256, G1024, epi | M256/N128/K256, G1024, epi |
| 2 | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 4 | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 8 | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi |
| 16 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 32 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi |
| 64 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 128 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 256 | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 512 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi |
| 4096 | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |
| 8192 | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |
| 16384 | M256/N128/K256, G512, dispatch | M256/N128/K256, G512, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |

Source bindings and complete raw benchmark console rows (`PERFORMANCE_CSV` time is milliseconds):

```text
EP4 before: kernel-source-sha256=c366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff; log-sha256=3cbc3127b5f39c423abbaeaf20e27be4216c6e5c4bd3be21b9377c3df85a9c40
PERFORMANCE_CSV,hashinfer,1,0.065633
PERFORMANCE_CSV,hashinfer,2,0.084240
PERFORMANCE_CSV,hashinfer,4,0.110929
PERFORMANCE_CSV,hashinfer,8,0.142913
PERFORMANCE_CSV,hashinfer,16,0.196722
PERFORMANCE_CSV,hashinfer,32,0.262914
PERFORMANCE_CSV,hashinfer,64,0.302466
PERFORMANCE_CSV,hashinfer,128,0.323155
PERFORMANCE_CSV,hashinfer,256,0.329379
PERFORMANCE_CSV,hashinfer,512,0.354788
PERFORMANCE_CSV,hashinfer,4096,0.814855
PERFORMANCE_CSV,hashinfer,8192,1.462221
PERFORMANCE_CSV,hashinfer,16384,2.858201
BENCHMARK_COMPLETE
EP4 after: kernel-source-sha256=a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29; log-sha256=d91598e16cf32271edc219b9bbc7dcdf7e1e72b37cb7123f743e7febc01185e4
PERFORMANCE_CSV,hashinfer,1,0.075073
PERFORMANCE_CSV,hashinfer,2,0.095537
PERFORMANCE_CSV,hashinfer,4,0.117777
PERFORMANCE_CSV,hashinfer,8,0.156433
PERFORMANCE_CSV,hashinfer,16,0.205058
PERFORMANCE_CSV,hashinfer,32,0.260418
PERFORMANCE_CSV,hashinfer,64,0.290355
PERFORMANCE_CSV,hashinfer,128,0.320131
PERFORMANCE_CSV,hashinfer,256,0.327443
PERFORMANCE_CSV,hashinfer,512,0.350707
PERFORMANCE_CSV,hashinfer,4096,0.807494
PERFORMANCE_CSV,hashinfer,8192,1.435323
PERFORMANCE_CSV,hashinfer,16384,2.862633
BENCHMARK_COMPLETE
EP8 before: kernel-source-sha256=c366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff; log-sha256=d893b77c2336e3203d848299521170c6c54f6fa30f69e416fdd538c52cfcc1c0
PERFORMANCE_CSV,hashinfer,1,0.079952
PERFORMANCE_CSV,hashinfer,2,0.088288
PERFORMANCE_CSV,hashinfer,4,0.102160
PERFORMANCE_CSV,hashinfer,8,0.131937
PERFORMANCE_CSV,hashinfer,16,0.143073
PERFORMANCE_CSV,hashinfer,32,0.168113
PERFORMANCE_CSV,hashinfer,64,0.189569
PERFORMANCE_CSV,hashinfer,128,0.195840
PERFORMANCE_CSV,hashinfer,256,0.203857
PERFORMANCE_CSV,hashinfer,512,0.207041
PERFORMANCE_CSV,hashinfer,4096,0.465188
PERFORMANCE_CSV,hashinfer,8192,0.790070
PERFORMANCE_CSV,hashinfer,16384,1.522037
BENCHMARK_COMPLETE
EP8 after: kernel-source-sha256=a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29; log-sha256=60ad241d8fcf50948da36a4b74f077d11d9b5a9268119e4412af05ddc8047f71
PERFORMANCE_CSV,hashinfer,1,0.073216
PERFORMANCE_CSV,hashinfer,2,0.094704
PERFORMANCE_CSV,hashinfer,4,0.101761
PERFORMANCE_CSV,hashinfer,8,0.129440
PERFORMANCE_CSV,hashinfer,16,0.137921
PERFORMANCE_CSV,hashinfer,32,0.163809
PERFORMANCE_CSV,hashinfer,64,0.186704
PERFORMANCE_CSV,hashinfer,128,0.196273
PERFORMANCE_CSV,hashinfer,256,0.199568
PERFORMANCE_CSV,hashinfer,512,0.201825
PERFORMANCE_CSV,hashinfer,4096,0.468068
PERFORMANCE_CSV,hashinfer,8192,0.788245
PERFORMANCE_CSV,hashinfer,16384,1.521209
BENCHMARK_COMPLETE
```

All rank/shape output fingerprints match before and after; finite repeated-output checks and source closure pass. Native T128 also passes the independent reference on all 12 ranks. These selected checks are separate from the final correctness suite. Raw per-iteration arrays, fixtures, exact tactic dictionaries and source-bound logs remain in the local experiment ledger.
