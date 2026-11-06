# Startup weight cache priority — rejected

Root rejected R1 after the complete supported 56-cell CAAC screen: overall
−0.090791%, T32 −0.018427%, T16384 −0.163103%, with 34 negative cells.
The added lifetime count/select work has no demonstrated end-to-end benefit.
No repeat, narrowed rescue or full-matrix expansion; no production source,
public cache, historical baseline, commit or PR change is retained.
Independent raw replay passed; the exact source/patch are preserved and the
owned review worktree/local branch are retired. Canonical c1ac remains clean.

All 23 jobs completed with full source/cache postflight and seven GPUs idle.
The unchanged public timer measured 22,400 CUPTI samples and 448 loaded main
kernel records. All 59 clock-exception quartiles and two missing quartiles
remain in the report; no sample or row was discarded. Large EP losses have
repeat/clock caveats, and are not assigned a causal explanation. GPU3 ran the
separate parent-authorized NCU diagnostic while seven other GPUs ran one
whole CAAC job at a time; profiler durations are not benchmark timings.

Raw evidence: [sealed data](../../evidence/startup-weight-cache-screen/1793404912968334000/data),
[fetch manifest](../../evidence/startup-weight-cache-screen/1793404912968334000/fetch-receipt.json),
[report](../../evidence/startup-weight-cache-screen/1793404912968334000/report/summary.json).
Archive SHA256: `a89919d78c908aad1ed040fc558d94116d0cbd1f962ade39cb2a51fe7f5db7a7`.

## Exact/native qualification

R1 `585aaeac` passes the three existing paired cases against immutable retained
`c1ac8ce7`: six exact calls and nine paired native images. The two successful
R0 controls are reused after matching the complete source inventories and the
current release-library cohort. R0's failed Int64 selector compiles and passing
postflight remain unchanged in `qualification/`; R1 is in `qualification-r1/`.

| Case | FC2 registers | Dynamic shared bytes | Driver CTA capacity | FC2 non-NOP | Exact |
| --- | ---: | ---: | ---: | ---: | --- |
| NVFP4, one CTA, CLC, PDL | 76 → 76 | 222,208 → 222,208 | 1 → 1 | 873 → 876 | Pass |
| MXFP4x8, two CTA, static, PDL | 82 → 82 | 214,912 → 214,912 | 1 → 1 | 904 → 906 | Pass |
| MXFP8, one CTA, static, PDL off | 82 → 82 | unchanged | 1 → 1 | 718 → 718 | Pass |

All captured kernels have zero local memory and valid actual launches. The
resource gate permits register changes and theoretical capacity changes while
requiring at least the intended one CTA per SM; neither changed in these
cases. Seven pairs have byte-identical PTX, cubin and SASS: all FC1/finalizers
and the PDL-off FC2. The native count includes compiler instruction substitutions
and scheduling changes, not just source-level additions.

The affected FC2 PTX initializes a distinct lifetime count once, compares it
with nine/eleven stages, and increments it on every produced stage without
resetting it at ring wrap or work-tile transitions. Actual SASS contains this
compare/increment and the typed hint selection. Both weight and SFA TMA
instructions consume the selected descriptor hint; the separate ring index
still wraps. The initial fill uses FIRST, then the existing route-aware choice.
All source, native-cache and fresh-idle checks passed before and after; GPUs 2/4
were released. Compiler options and numerical oracles were unchanged.

Evidence: [qualification summary](qualification-summary.json),
[native policy chains](native-policy.json),
[complete R1 receipt](qualification-r1/evidence/receipt.json),
[archive receipt](qualification-r1/fetch.json),
[preserved R0 failure](qualification/failure-summary.json).

This gate establishes exactness, launch/resource validity and actual native
policy lowering for the three cases. It does not establish throughput benefit
or full-shape resource behavior. The complete 56-cell performance screen above is separate from this qualification.


## Complete primary screen

| Model | EP/TP | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | EP8 | CuteDSL MXFP4x8 | 32 | 167.409 | 167.425 | 167.666 | 167.217 | -0.139% | 0.115% | 0.144% |
| kimi-k3 | EP8 | CuteDSL MXFP4x8 | 16384 | 1048.839 | 1060.296 | 1049.784 | 1020.583 | -1.935% | 2.769% | 1.001% |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | 32 | 180.529 | 180.642 | 180.690 | 180.657 | -0.040% | 0.071% | 0.027% |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | 16384 | 1065.720 | 1073.784 | 1031.576 | 1032.392 | -0.337% | 3.228% | 4.092% |
| kimi-k3 | EP8 | CuteDSL W4A4 | 32 | 174.768 | 174.752 | 174.945 | 174.721 | -0.059% | 0.027% | 0.110% |
| kimi-k3 | EP8 | CuteDSL W4A4 | 16384 | 856.180 | 796.452 | 840.212 | 821.682 | +2.532% | 4.198% | 5.494% |
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | 32 | 100.785 | 100.801 | 100.801 | 100.865 | +0.024% | 0.079% | 0.000% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | 32 | 168.257 | 168.178 | 168.081 | 168.034 | +0.009% | 0.133% | 0.058% |
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | 16384 | 781.718 | 808.759 | 788.807 | 782.599 | -2.074% | 0.113% | 2.529% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | 16384 | 864.455 | 868.631 | 865.415 | 863.175 | -0.370% | 0.148% | 0.372% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 32 | 110.129 | 109.986 | 110.145 | 110.273 | +0.123% | 0.131% | 0.145% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | 16384 | 949.802 | 951.722 | 952.394 | 950.122 | -0.220% | 0.034% | 0.071% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | 32 | 103.456 | 103.280 | 103.265 | 103.472 | +0.185% | 0.016% | 0.015% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | 16384 | 555.444 | 555.891 | 555.812 | 555.652 | -0.055% | 0.037% | 0.014% |
| v3 | EP8 | CuteDSL MXFP4x8 | 32 | 97.088 | 97.264 | 97.185 | 97.072 | -0.149% | 0.016% | 0.082% |
| v3 | EP8 | CuteDSL MXFP8 | 32 | 163.745 | 163.825 | 163.809 | 163.937 | +0.015% | 0.117% | 0.010% |
| v3 | EP8 | CuteDSL MXFP4x8 | 16384 | 641.877 | 624.164 | 626.660 | 627.284 | +1.459% | 2.326% | 0.400% |
| v3 | EP8 | CuteDSL MXFP8 | 16384 | 745.525 | 725.990 | 717.317 | 693.733 | -0.343% | 7.466% | 1.209% |
| v3 | EP8 | CuteDSL PER-TOKEN | 32 | 106.273 | 106.177 | 106.289 | 106.209 | +0.007% | 0.060% | 0.106% |
| v3 | EP8 | CuteDSL PER-TOKEN | 16384 | 624.436 | 624.165 | 623.833 | 623.812 | +0.020% | 0.100% | 0.053% |
| v3 | EP8 | CuteDSL W4A4 | 32 | 99.617 | 99.649 | 99.570 | 99.585 | -0.009% | 0.032% | 0.080% |
| v3 | EP8 | CuteDSL W4A4 | 16384 | 523.236 | 523.236 | 524.084 | 523.284 | -0.076% | 0.009% | 0.162% |
| v41-flash | EP4 | CuteDSL MXFP4x8 | 32 | 119.040 | 119.361 | 119.376 | 118.977 | -0.302% | 0.053% | 0.013% |
| v41-flash | EP4 | CuteDSL MXFP8 | 32 | 210.817 | 211.009 | 211.008 | 211.137 | -0.015% | 0.152% | 0.000% |
| v41-flash | EP4 | CuteDSL MXFP4x8 | 16384 | 820.851 | 849.187 | 816.309 | 804.340 | -2.406% | 2.053% | 4.028% |
| v41-flash | EP4 | CuteDSL MXFP8 | 16384 | 931.108 | 969.973 | 986.357 | 986.260 | -2.029% | 5.923% | 1.689% |
| v41-flash | EP4 | CuteDSL PER-TOKEN | 32 | 130.369 | 130.209 | 130.305 | 130.209 | +0.025% | 0.123% | 0.074% |
| v41-flash | EP4 | CuteDSL PER-TOKEN | 16384 | 772.087 | 779.230 | 775.046 | 781.335 | -0.056% | 1.198% | 0.540% |
| v41-flash | EP4 | CuteDSL W4A4 | 32 | 125.345 | 125.218 | 125.362 | 125.377 | +0.056% | 0.026% | 0.115% |
| v41-flash | EP4 | CuteDSL W4A4 | 16384 | 608.086 | 605.126 | 602.454 | 608.966 | +0.785% | 0.145% | 0.444% |
| kimi-k3 | TP8 | CuteDSL MXFP4x8 | 32 | 164.417 | 164.721 | 164.435 | 164.433 | -0.093% | 0.010% | 0.175% |
| kimi-k3 | TP8 | CuteDSL MXFP4x8 | 16384 | 1610.619 | 1584.667 | 1598.503 | 1604.907 | +1.017% | 0.356% | 0.873% |
| kimi-k3 | TP8 | CuteDSL PER-TOKEN | 32 | 177.809 | 177.857 | 177.793 | 178.161 | +0.090% | 0.198% | 0.036% |
| kimi-k3 | TP8 | CuteDSL PER-TOKEN | 16384 | 1940.414 | 1941.854 | 1941.182 | 1941.390 | -0.032% | 0.050% | 0.035% |
| kimi-k3 | TP8 | CuteDSL W4A4 | 32 | 170.049 | 169.841 | 170.034 | 169.905 | +0.023% | 0.085% | 0.113% |
| kimi-k3 | TP8 | CuteDSL W4A4 | 16384 | 1395.594 | 1410.795 | 1392.747 | 1396.779 | -0.396% | 0.085% | 1.296% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | 32 | 125.633 | 125.793 | 125.889 | 125.553 | -0.197% | 0.063% | 0.076% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | 32 | 182.433 | 182.338 | 182.466 | 182.273 | -0.027% | 0.088% | 0.070% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | 16384 | 1222.459 | 1208.907 | 1238.107 | 1223.899 | -0.020% | 0.118% | 2.415% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | 16384 | 1289.372 | 1278.891 | 1296.923 | 1284.635 | -0.068% | 0.369% | 1.410% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 32 | 124.433 | 123.793 | 123.617 | 123.425 | +0.180% | 0.816% | 0.142% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16384 | 1802.569 | 1799.642 | 1800.602 | 1800.281 | +0.072% | 0.127% | 0.053% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | 32 | 114.737 | 114.785 | 114.801 | 114.544 | -0.133% | 0.168% | 0.014% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | 16384 | 1137.834 | 1137.834 | 1138.634 | 1137.274 | -0.060% | 0.049% | 0.070% |
| v3 | TP8 | CuteDSL MXFP4x8 | 32 | 103.650 | 103.089 | 103.041 | 103.345 | +0.420% | 0.294% | 0.047% |
| v3 | TP8 | CuteDSL MXFP8 | 32 | 168.034 | 167.666 | 168.338 | 167.730 | -0.071% | 0.181% | 0.401% |
| v3 | TP8 | CuteDSL MXFP4x8 | 16384 | 1229.374 | 1228.510 | 1226.717 | 1229.614 | +0.153% | 0.019% | 0.146% |
| v3 | TP8 | CuteDSL MXFP8 | 16384 | 1324.096 | 1319.855 | 1328.478 | 1323.102 | -0.042% | 0.075% | 0.653% |
| v3 | TP8 | CuteDSL PER-TOKEN | 32 | 116.048 | 116.241 | 116.209 | 116.225 | -0.076% | 0.153% | 0.028% |
| v3 | TP8 | CuteDSL PER-TOKEN | 16384 | 1395.850 | 1395.818 | 1394.363 | 1394.986 | +0.023% | 0.062% | 0.104% |
| v3 | TP8 | CuteDSL W4A4 | 32 | 105.713 | 105.969 | 105.680 | 105.585 | -0.166% | 0.121% | 0.273% |
| v3 | TP8 | CuteDSL W4A4 | 16384 | 1093.144 | 1092.073 | 1092.345 | 1092.936 | +0.076% | 0.019% | 0.025% |
| v41-flash | TP4 | CuteDSL PER-TOKEN | 32 | 145.793 | 146.113 | 145.921 | 145.985 | -0.087% | 0.131% | 0.132% |
| v41-flash | TP4 | CuteDSL PER-TOKEN | 16384 | 1276.937 | 1280.042 | 1279.305 | 1276.456 | -0.233% | 0.038% | 0.058% |
| v41-flash | TP4 | CuteDSL W4A4 | 32 | 138.882 | 138.993 | 138.977 | 138.785 | -0.109% | 0.070% | 0.012% |
| v41-flash | TP4 | CuteDSL W4A4 | 16384 | 1044.216 | 1041.721 | 1043.033 | 1044.425 | +0.186% | 0.020% | 0.126% |

## All negative cells

| Job | Backend | Tokens | Speedup | Control spread | Candidate spread | Clock MHz | Reasons |
|---|---|---:|---:|---:|---:|---|---|
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 16384 | -2.405958% | 2.052801% | 4.027705% | 1455/1665/2032 | 0 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 16384 | -2.073607% | 0.112637% | 2.529454% | 2032 | 0/4 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 16384 | -2.028679% | 5.923266% | 1.689172% | 1252/1275/1297.0/2032 | 0/4 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | -1.934749% | 2.768614% | 1.001397% | 1800/2032 | 0/4 |
| tp-kimi-k3-w4a4 | CuteDSL W4A4 | 16384 | -0.396334% | 0.084910% | 1.295856% | 1995/2032 | 0 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP8 | 16384 | -0.369887% | 0.148232% | 0.371614% | 1350.0/1440/2032 | 0/4 |
| ep-v3-mxfp | CuteDSL MXFP8 | 16384 | -0.343323% | 7.465696% | 1.208949% | 1747.0/2032.0 | 0/4 |
| ep-kimi-k3-per-token | CuteDSL PER-TOKEN | 16384 | -0.336784% | 3.228280% | 4.091604% | 1920/2032.0 | 0/4 |
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 32 | -0.301800% | 0.053372% | 0.013405% | 2032 | 0 |
| tp-v41-flash-per-token | CuteDSL PER-TOKEN | 16384 | -0.232616% | 0.037682% | 0.057570% | 2032 | 0 |
| ep-nemo3-ultra-per-token | CuteDSL PER-TOKEN | 16384 | -0.220176% | 0.033691% | 0.070661% | 2032 | 0 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 32 | -0.196873% | 0.063320% | 0.076316% | 2032 | 0 |
| tp-v3-w4a4 | CuteDSL W4A4 | 32 | -0.166002% | 0.121229% | 0.272993% | 2032.0 | 0 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 32 | -0.148617% | 0.015967% | 0.081803% | 2032 | 0 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 32 | -0.138610% | 0.114821% | 0.143646% | 2032 | 0 |
| tp-nemo3-ultra-w4a4 | CuteDSL W4A4 | 32 | -0.132665% | 0.168057% | 0.013939% | 2032 | 0 |
| tp-v41-flash-w4a4 | CuteDSL W4A4 | 32 | -0.109190% | 0.069532% | 0.011513% | 2032 | 0 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 32 | -0.092927% | 0.009731% | 0.174538% | 2032 | 0 |
| tp-v41-flash-per-token | CuteDSL PER-TOKEN | 32 | -0.087490% | 0.131350% | 0.131578% | 2032 | 0 |
| ep-v3-w4a4 | CuteDSL W4A4 | 16384 | -0.076353% | 0.009174% | 0.162068% | 2032.0 | 0 |
| tp-v3-per-token | CuteDSL PER-TOKEN | 32 | -0.076173% | 0.152523% | 0.027537% | 2032 | 0 |
| tp-v3-mxfp | CuteDSL MXFP8 | 32 | -0.071269% | 0.181244% | 0.400797% | 2032.0 | 0 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 16384 | -0.067892% | 0.368704% | 1.409972% | 1515/1642.0/1792.0/2032 | 0/4 |
| tp-nemo3-ultra-w4a4 | CuteDSL W4A4 | 16384 | -0.059760% | 0.049329% | 0.070265% | 2032.0 | 0 |
| ep-kimi-k3-w4a4 | CuteDSL W4A4 | 32 | -0.059323% | 0.027186% | 0.109870% | 2032 | 0 |
| ep-v41-flash-per-token | CuteDSL PER-TOKEN | 16384 | -0.056322% | 1.197662% | 0.539774% | 2025.0/2032 | 0 |
| ep-nemo3-ultra-w4a4 | CuteDSL W4A4 | 16384 | -0.054602% | 0.037448% | 0.014393% | 2032 | 0 |
| tp-v3-mxfp | CuteDSL MXFP8 | 16384 | -0.042315% | 0.075089% | 0.653329% | 1961.0/2032 | 0/4 |
| ep-kimi-k3-per-token | CuteDSL PER-TOKEN | 32 | -0.039996% | 0.071180% | 0.026572% | 2032.0 | 0 |
| tp-kimi-k3-per-token | CuteDSL PER-TOKEN | 16384 | -0.031742% | 0.050299% | 0.034592% | 2032 | 0 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 32 | -0.026867% | 0.087780% | 0.070199% | 2032 | 0 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 16384 | -0.019707% | 0.117714% | 2.415405% | 1740/2032.0 | 0/4 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 32 | -0.014957% | 0.151790% | 0.000474% | 2032.0 | 0 |
| ep-v3-w4a4 | CuteDSL W4A4 | 32 | -0.008527% | 0.031631% | 0.079844% | 2032.0 | 0 |

## Full-screen resource boundary

The pilot resource equality does not generalize to the full matrix. The peer
joined all measured stages: 11 FC2 specializations increase registers by
2–16, with LOCAL0, unchanged dynamic shared memory and driver CTA capacity.
No instruction/resource improvement is inferred from the two pilot counts.

| Job | Mode | Tokens | FC2 registers | CTA capacity |
|---|---|---:|---:|---:|
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 32 | 80 → 88 | 1 → 1 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 112 → 122 | 1 → 1 |
| tp-kimi-k3-w4a4 | CuteDSL W4A4 | 16384 | 112 → 122 | 1 → 1 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 16384 | 106 → 122 | 1 → 1 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 16384 | 106 → 122 | 1 → 1 |
| tp-nemo3-ultra-per-token | CuteDSL PER-TOKEN | 16384 | 136 → 142 | 1 → 1 |
| tp-nemo3-ultra-w4a4 | CuteDSL W4A4 | 32 | 76 → 78 | 1 → 1 |
| tp-v3-mxfp | CuteDSL MXFP8 | 32 | 80 → 88 | 1 → 1 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 32 | 80 → 88 | 1 → 1 |
| tp-v41-flash-per-token | CuteDSL PER-TOKEN | 32 | 88 → 98 | 1 → 1 |
| tp-v41-flash-w4a4 | CuteDSL W4A4 | 32 | 71 → 82 | 1 → 1 |

[Independent peer](../../audits/startup-weight-cache-data-peer.json),
[readable peer](../../audits/startup-weight-cache-data-peer.md),
[retirement receipt](retirement/receipt.json). No repeat or rescue.
