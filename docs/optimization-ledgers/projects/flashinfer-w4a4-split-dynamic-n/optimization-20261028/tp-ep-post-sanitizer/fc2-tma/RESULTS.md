# Routed FC2 2D TMA: first matched screen

Status: **not retained**. The isolated four-file candidate remains unstaged in `flashinfer-fc2-tma-review`, based on d1767. Canonical source is managed separately by the parent effort.

Fixed-winner C–A–A–C, d1767 control versus routed-TMA candidate; public functional API, cold-L2 CUDA graphs,10 warmups and100 CUPTI samples per pass. NV arms include input quantization. Source hashes, actual routes, GPU UUID, every raw sample median, winner identities and cache immutability were independently verified.72cells/288medians/28,800samples;56affected cells plus16unchanged W4A16 sanity cells.

| Topology | Decode ≤64 | Prefill ≥4096 | All affected |
|---|---:|---:|---:|
| EP | -0.401% | -0.719% | -0.560% |
| TP | -1.307% | +8.907% | +3.674% |

Speedup is `mean(C1,C2) / mean(A1,A2) − 1`; positive is faster. TP prefill gains do not yet justify retention: decode regresses, EP is slightly slower, and the routing capacity adds substantial output storage. Host allocation and descriptor encoding are outside warmed GPU timing.

## Complete paired results

| Job | Backend | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | FC2 before→after MiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 50.800 | 51.649 | 51.633 | 50.800 | -1.628% | 0.438→7.000 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 229.249 | 229.234 | 229.330 | 228.913 | -0.088% | 7.000→18.484 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 395.027 | 403.139 | 403.187 | 395.459 | -1.965% | 448.000→545.125 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 1085.142 | 1092.807 | 1045.350 | 1035.014 | -0.842% | 1792.000→1889.125 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 51.489 | 52.576 | 52.592 | 51.584 | -1.992% | 0.438→7.000 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 56.864 | 57.760 | 57.712 | 56.736 | -1.621% | 0.438→7.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 57.329 | 57.264 | 57.297 | 57.392 | +0.140% | 0.438→0.438 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 237.953 | 237.329 | 237.474 | 237.793 | +0.199% | 7.000→30.625 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 244.706 | 243.970 | 243.841 | 244.737 | +0.335% | 7.000→18.484 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 250.721 | 249.618 | 249.762 | 250.498 | +0.368% | 7.000→7.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 387.378 | 392.082 | 391.235 | 387.426 | -1.087% | 448.000→545.125 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 447.314 | 454.771 | 454.514 | 446.931 | -1.654% | 448.000→545.125 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 588.067 | 603.732 | 597.507 | 552.164 | -5.079% | 448.000→448.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 782.549 | 752.117 | 772.437 | 771.205 | +1.915% | 1792.000→1889.125 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1063.206 | 1068.566 | 1044.647 | 1031.175 | -0.891% | 1792.000→1889.125 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 2074.045 | 2074.061 | 2068.014 | 2069.229 | +0.029% | 1792.000→1792.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4 | 67.969 | 68.208 | 68.128 | 68.032 | -0.246% | 0.438→7.000 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4 | 46.592 | 46.560 | 46.641 | 46.496 | -0.121% | 0.438→7.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 64 | 219.474 | 219.554 | 219.410 | 219.218 | -0.062% | 7.000→13.562 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 64 | 129.313 | 129.185 | 129.169 | 129.425 | +0.149% | 7.000→13.562 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4096 | 305.795 | 310.994 | 309.826 | 305.954 | -1.461% | 448.000→556.500 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 228.562 | 234.818 | 235.057 | 228.529 | -2.721% | 448.000→556.500 |
| ep-v3-mxfp | CuteDSL MXFP8 | 16384 | 700.245 | 740.149 | 707.141 | 715.893 | -2.152% | 1792.000→1900.500 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 682.229 | 693.462 | 678.197 | 688.917 | -0.037% | 1792.000→1846.250 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4 | 46.321 | 46.336 | 46.337 | 46.241 | -0.120% | 0.438→7.000 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 51.952 | 52.032 | 52.192 | 51.936 | -0.322% | 0.438→14.000 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4 | 52.128 | 52.000 | 52.112 | 52.000 | +0.015% | 0.438→0.438 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 64 | 130.529 | 130.833 | 130.769 | 130.561 | -0.196% | 7.000→13.562 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 136.449 | 136.194 | 136.321 | 136.433 | +0.135% | 7.000→13.562 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 64 | 142.561 | 142.593 | 142.593 | 142.593 | -0.011% | 7.000→7.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4096 | 207.681 | 209.986 | 209.649 | 207.522 | -1.056% | 448.000→556.500 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 249.890 | 253.394 | 253.555 | 249.650 | -1.461% | 448.000→556.500 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4096 | 287.026 | 286.530 | 286.355 | 287.042 | +0.207% | 448.000→448.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 16384 | 500.324 | 490.724 | 490.884 | 499.603 | +1.866% | 1792.000→1900.500 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 638.037 | 627.541 | 626.901 | 636.773 | +1.624% | 1792.000→1846.250 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 16384 | 1200.234 | 1168.185 | 1174.024 | 1197.193 | +2.357% | 1792.000→1792.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 41.857 | 43.425 | 43.456 | 41.873 | -3.627% | 0.438→7.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 242.930 | 238.962 | 239.474 | 242.386 | +1.438% | 7.000→98.875 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 717.269 | 672.214 | 672.438 | 716.773 | +6.648% | 448.000→1225.875 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 2095.633 | 1883.984 | 1875.264 | 2091.506 | +11.382% | 1792.000→2569.875 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 43.424 | 45.520 | 45.456 | 43.360 | -4.609% | 0.438→7.000 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 46.065 | 48.737 | 48.992 | 46.065 | -5.730% | 0.438→7.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 50.928 | 50.880 | 50.848 | 50.880 | +0.079% | 0.438→0.438 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 249.378 | 248.114 | 248.210 | 249.474 | +0.509% | 7.000→98.875 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 258.482 | 258.802 | 258.514 | 258.162 | -0.130% | 7.000→98.875 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 282.322 | 282.659 | 282.643 | 282.306 | -0.119% | 7.000→7.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 695.669 | 671.590 | 671.685 | 695.621 | +3.575% | 448.000→1225.875 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 854.839 | 823.351 | 823.335 | 854.887 | +3.828% | 448.000→1225.875 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 843.463 | 835.543 | 842.663 | 851.144 | +0.977% | 448.000→448.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 1809.455 | 1594.285 | 1598.349 | 1812.191 | +13.438% | 1792.000→2569.875 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 2409.844 | 2239.907 | 2235.107 | 2405.524 | +7.606% | 1792.000→2569.875 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 2967.033 | 2963.352 | 2990.009 | 2962.937 | -0.393% | 1792.000→1792.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4 | 46.752 | 47.024 | 47.200 | 46.769 | -0.748% | 0.438→7.000 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4 | 35.360 | 35.776 | 35.776 | 35.328 | -1.207% | 0.438→14.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 64 | 227.538 | 228.401 | 228.289 | 227.602 | -0.339% | 7.000→59.500 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 64 | 144.113 | 141.553 | 141.585 | 144.161 | +1.814% | 7.000→59.500 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4096 | 634.421 | 587.412 | 587.348 | 634.308 | +7.999% | 448.000→892.500 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 557.124 | 491.571 | 491.236 | 556.724 | +13.333% | 448.000→892.500 |
| tp-v3-mxfp | CuteDSL MXFP8 | 16384 | 1788.220 | 1645.579 | 1641.675 | 1787.357 | +8.771% | 1792.000→2684.500 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 1735.356 | 1580.891 | 1582.588 | 1733.437 | +9.651% | 1792.000→2684.500 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4 | 36.800 | 37.633 | 37.648 | 36.769 | -2.274% | 0.438→14.000 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 40.384 | 42.000 | 42.049 | 40.480 | -3.789% | 0.438→7.000 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4 | 39.904 | 40.032 | 40.064 | 39.969 | -0.279% | 0.438→0.438 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 64 | 143.185 | 141.313 | 141.249 | 143.441 | +1.438% | 7.000→59.500 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 151.281 | 152.274 | 152.353 | 151.297 | -0.672% | 7.000→59.500 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 64 | 155.025 | 154.722 | 154.786 | 154.386 | -0.031% | 7.000→7.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4096 | 524.708 | 477.507 | 477.507 | 523.908 | +9.801% | 448.000→892.500 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 621.765 | 592.037 | 592.404 | 621.380 | +4.956% | 448.000→892.500 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4096 | 644.197 | 644.213 | 644.294 | 644.036 | -0.021% | 448.000→448.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 16384 | 1544.570 | 1368.729 | 1369.498 | 1543.451 | +12.774% | 1792.000→2684.500 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1888.990 | 1691.964 | 1691.883 | 1887.949 | +11.617% | 1792.000→2684.500 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 16384 | 2232.352 | 2235.345 | 2239.056 | 2238.960 | -0.069% | 1792.000→1792.000 |

W4A16 code is unchanged and excluded from aggregates. Its K3 EP4096 sanity cell varies−5.08% and V3 EP16384+2.36%, illustrating residual pass-dependent timing variability; no correction or subtraction is applied to any other cell.

## Correctness/codegen boundaries

The supported public gate covers256 paired output-storage comparisons across four formats, N16–256, one/twoCTA, static/CLC, PDL off/on, K384/2304 and four graph route mutations. A separate16-comparison smoke also passed. The32-row fallback was explicitly exercised with one shared stage. Local artifact verification and generated instruction/resource summaries are in `codegen-analysis.json`. No candidate sanitizer has run.

H320 is unsupported in the unchanged control: public SF preparation, the low-level m%128 capability guard and the wrapper cute.assume(m,128) reject it. The diagnostic-only guard override stopped before kernel execution at the unchanged assume. No bypass of that assume or supported-capability extension was made. H384 covers a final empty half of a twoCTA channel tile; within128-channel clipping is outside the supported contract.

## Evidence

- `perf-analysis.json`, `perf-cells.csv`, `audit_perf.py`: independent timing/source/cache audit and every raw-pass median.
- `perf-evidence/`:1,089 hashed raw files; archive SHA256 `06e3e92069b0d03cf7a5e8825c7ba8d78c2b2517da3e987db26108b48cb56a73`.
- `gate-evidence/`:1,224 hashed files including native PTX/cubin/SASS, source and failed unsupported fixtures.
- `ALLOCATION.md`, `allocation-cells.csv`: source-derived capacity using actual winners; no change to routing capacity policy.
- `stage-profile/`: paired stage attribution, when completed; diagnostic only, not a timing replacement.

Next design question: can ordinary TMA publish into a compact expert-routed domain without full-tile output padding or overwriting adjacent live rows? Avoid a TP-only switch or new tactics.


## Matched stage attribution

Independent20-graph NSYS diagnostic, V3 MXFP4x8 T16384, same fixed winners. These traces are not substituted into the CAAC matrix; PDL-overlapped durations are not added.

| Topology | Stage | Control µs | Candidate µs | Change |
|---|---|---:|---:|---:|
| TP | Graph span | 1733.340 | 1577.531 | -8.99% |
| TP | Prepare | 315.122 | 313.571 | -0.49% |
| TP | FC1 | 443.571 | 442.851 | -0.16% |
| TP | FC2 | 713.589 | 513.012 | -28.11% |
| TP | Combine | 346.210 | 388.867 | +12.32% |
| EP | Graph span | 655.365 | 660.548 | +0.79% |
| EP | Prepare | 40.017 | 40.081 | +0.16% |
| EP | FC1 | 321.090 | 320.578 | -0.16% |
| EP | FC2 | 222.002 | 216.242 | -2.59% |
| EP | Combine | 83.424 | 92.352 | +10.70% |

TP FC2 registers122→108; EP108→100. Combine registers80→86 in both. Prepare/FC1 instruction ownership unchanged. The ordinary-TMA store removes a significant FC2 issue bottleneck under TP, but the changed global order increases combine cost. Compacting output capacity alone is not proof that this locality penalty disappears.

All26 profile files were SHA-verified. Native traces and SQLite: `profile-evidence/stage-profile`. Archive SHA256 `8cd44820d91959b4ee577f7e8e3b868de56ff5f8a52f24cf6de4a336bd10ca23`.
