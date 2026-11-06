## Native before/after performance

H7168/I2048/E256/top-k8, native precomputed routing, runtime unit FP32 FC1/FC2 alphas, deterministic combine, O3. Each arm freshly autotunes all eight native tactics. Three warmups and 100 cold-L2 CUDA-graph CUPTI samples per row; take each iteration's rank maximum, then its median. The full public-forward activity span includes alpha copies and all forward kernels. Fixture preparation, compilation, tuning, capture and L2 flushing are excluded. No samples are trimmed.

| Global tokens | EP4 before us | EP4 after us | Speedup | EP8 before us | EP8 after us | Speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 65.633 | 67.841 | 0.9674x | 79.953 | 64.944 | 1.2311x |
| 2 | 84.240 | 93.936 | 0.8968x | 88.288 | 90.945 | 0.9708x |
| 4 | 110.929 | 119.185 | 0.9307x | 102.160 | 98.849 | 1.0335x |
| 8 | 142.913 | 159.138 | 0.8980x | 131.936 | 122.961 | 1.0730x |
| 16 | 196.722 | 196.258 | 1.0024x | 143.073 | 137.234 | 1.0426x |
| 32 | 262.914 | 269.443 | 0.9758x | 168.113 | 164.977 | 1.0190x |
| 64 | 302.466 | 294.435 | 1.0273x | 189.569 | 193.745 | 0.9784x |
| 128 | 323.154 | 320.212 | 1.0092x | 195.840 | 193.522 | 1.0120x |
| 256 | 329.379 | 330.323 | 0.9971x | 203.857 | 191.746 | 1.0632x |
| 512 | 354.788 | 346.707 | 1.0233x | 207.041 | 203.169 | 1.0191x |
| 4096 | 814.855 | 795.143 | 1.0248x | 465.188 | 460.692 | 1.0098x |
| 8192 | 1462.221 | 1484.748 | 0.9848x | 790.070 | 786.690 | 1.0043x |
| 16384 | 2858.201 | 2857.385 | 1.0003x | 1522.037 | 1480.067 | 1.0284x |

Decode geometric speedup (global T4–512): EP4 **0.9820x**, EP8 **1.0297x**. T1/T2 and each prefill row are shown separately; EPs are not pooled.

All selected tactics (`epi` = epilogue return; `dispatch` = dispatch-warp return):

| Global tokens | EP4 before | EP4 after | EP8 before | EP8 after |
|---:|---|---|---|---|
| 1 | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N128/K256, G1024, epi | M256/N64/K256, G512, epi |
| 2 | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 4 | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 8 | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi |
| 16 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 32 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi |
| 64 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 128 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G512, epi |
| 256 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi | M256/N64/K256, G1024, epi |
| 512 | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G1024, epi | M256/N64/K256, G512, epi |
| 4096 | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |
| 8192 | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |
| 16384 | M256/N128/K256, G512, dispatch | M256/N128/K256, G512, dispatch | M256/N128/K256, G1024, dispatch | M256/N128/K256, G1024, dispatch |

Source bindings and complete raw benchmark console rows:

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
EP4 after: kernel-source-sha256=7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234; log-sha256=444e80879408d7b94c33507f845636ce9861f3f89362e94fb6c3d55c93621748
PERFORMANCE_CSV,hashinfer,1,0.067841
PERFORMANCE_CSV,hashinfer,2,0.093937
PERFORMANCE_CSV,hashinfer,4,0.119185
PERFORMANCE_CSV,hashinfer,8,0.159138
PERFORMANCE_CSV,hashinfer,16,0.196258
PERFORMANCE_CSV,hashinfer,32,0.269443
PERFORMANCE_CSV,hashinfer,64,0.294435
PERFORMANCE_CSV,hashinfer,128,0.320211
PERFORMANCE_CSV,hashinfer,256,0.330323
PERFORMANCE_CSV,hashinfer,512,0.346708
PERFORMANCE_CSV,hashinfer,4096,0.795143
PERFORMANCE_CSV,hashinfer,8192,1.484748
PERFORMANCE_CSV,hashinfer,16384,2.857385
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
EP8 after: kernel-source-sha256=7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234; log-sha256=5ccfbc584140d11a3a8c33171d8065d6900f8578dbaf96fe57b0f56abef70eb7
PERFORMANCE_CSV,hashinfer,1,0.064944
PERFORMANCE_CSV,hashinfer,2,0.090944
PERFORMANCE_CSV,hashinfer,4,0.098849
PERFORMANCE_CSV,hashinfer,8,0.122961
PERFORMANCE_CSV,hashinfer,16,0.137234
PERFORMANCE_CSV,hashinfer,32,0.164977
PERFORMANCE_CSV,hashinfer,64,0.193745
PERFORMANCE_CSV,hashinfer,128,0.193522
PERFORMANCE_CSV,hashinfer,256,0.191746
PERFORMANCE_CSV,hashinfer,512,0.203170
PERFORMANCE_CSV,hashinfer,4096,0.460692
PERFORMANCE_CSV,hashinfer,8192,0.786690
PERFORMANCE_CSV,hashinfer,16384,1.480067
BENCHMARK_COMPLETE
```

All rank/shape output fingerprints match before and after; finite repeated-output checks and source closure pass. Native T128 also passes the independent reference on all 12 ranks. These selected checks are separate from the final correctness suite. Raw per-iteration arrays, fixtures, exact tactic dictionaries and source-bound logs remain in the local experiment ledger.
