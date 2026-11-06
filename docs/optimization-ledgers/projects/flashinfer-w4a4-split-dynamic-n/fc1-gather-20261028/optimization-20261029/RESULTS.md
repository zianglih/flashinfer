# Dedicated-warpgroup Gather4 optimization

Combined R14 is kept in `../../flashinfer-fc1-gather-review` as **unstaged, unpushed experimental work**. The canonical PR checkout remains clean at `d35fcfda`. FC1 keeps its dedicated four-warp gather group; FC2 keeps regular TMA and W4A16 is unchanged.

## Retained changes

- Three non-reconverging warpgroup regions scope the register budgets: control 80, gather 128, epilogue 256. In the captured N3U TP8 T16384 MX kernels, the 208-byte stack and 26 LDL / 46 STL sites become zero. Donation alone did not recover the large performance gap; its purpose here is eliminating the observed spills and giving each role usable register resources.
- Shared-memory-only release/acquire around relaxed cluster barrier publication retains local completion, proxy ordering, phases and reuse. K3 iKET localized approximately 0.8 µs per K stage to the broad cluster arrival; emitted GPU-wide fences drop 29→1. The matching consumer scope covers both CTAs.
- Complete routing groups use 128-bit loads; scalar tails remain predicated. Valid nonnegative routing indices use unsigned division and lane/row arithmetic avoids signed correction instructions.
- No new model/dtype/TP/EP policy branches or autotune axes. Staging, arithmetic, routing ownership, CLC counts and PDL dependencies remain unchanged from the gathered prototype. R8 ordering-only and R9 early-reconverging register experiments were not retained.

## Measured results

Against previous Gather4 R6: **+65.99%** geometric speedup over 28 affected cells in four matched workloads; worst cell−0.42%. This is not a PR-head comparison. [Full paired table](../r14-r6/REPORT.md) includes 32 measured cells with four unchanged W4A16 diagnostics and 12,800 raw CUPTI samples.

Against PR head d35: 15 jobs, 144 cells, 57,600 raw CUPTI samples. The 112 affected cells exclude 32 W4A16 diagnostics. This screen uses 8/256/4096/16384 tokens, all four models and EP/TP where the existing comparison is supported.

| Model/topology | 8 tokens | 256 tokens | Prefill 4096/16384 | All sampled |
| --- | ---: | ---: | ---: | ---: |
| All models EP | +2.91% | +0.37% | -5.71% | -2.11% |
| V3 EP8 | +3.10% | +0.57% | -3.89% | -1.07% |
| V41F EP4 | +0.50% | +0.25% | -0.53% | -0.08% |
| K3 EP8 | +2.74% | +0.37% | -3.43% | -0.98% |
| N3U EP8 | +5.31% | +0.29% | -13.88% | -5.92% |
| All models TP | +0.90% | +2.70% | +8.37% | +5.03% |
| V3 TP8 | +1.68% | +2.97% | +15.60% | +8.76% |
| V41F TP4 | +2.12% | +0.56% | +1.12% | +1.23% |
| K3 TP8 | -1.13% | +3.83% | +12.81% | +6.91% |
| N3U TP8 | +1.07% | +2.67% | +2.05% | +1.96% |

**Remaining gap:** EP prefill remains −5.71% overall; N3U EP8 W4A4 T16384 is −30.78%. The gathered implementation is not ready to replace the PR implementation universally. TP gains are +5.03% overall and +8.37% on prefill.

[EP heatmap](../r14/plots/fc1-gather-vs-retained-ep.png) · [TP heatmap](../r14/plots/fc1-gather-vs-retained-tp.png)

## Validation and measurement boundary

- All 44 existing cases passed: 32 primary and 12 supplemental, including narrow/two-CTA, partial K, activation variants, CLC and PDL toggles. No new repository tests or oracle changes. Sanitizer was skipped as requested.
- Applicable pre-commit hooks passed, including mypy, ruff check and ruff format. Both changed files remain unstaged. The final review file differs from measured R14 only in module documentation and one explanatory comment; normalized device AST equality is recorded in `final-review-proof.json`.
- Final full-screen runtime guard: 376 compiled-kernel instances, including 192 FC1 instances; every physical register-pool check passed. 52 FC1 instances use 8–16 bytes of local storage, maximum 16 bytes. Thus the specific 208→0 improvement is established, not an all-kernels-spill-free claim. [Per-cell local storage](../r14/guarded-validation/fc1-local-storage-cells.md).
- C3 `fi-fc1-gather-1028`, 8×B300, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2 runtime/container, CuTe DSL 4.8.0. Bundled compiler codegen separately reports NVVM 13.4.59 / PTX 9.4. Persistent native compilation caches and normal CuTe caching retained.
- Same-GPU C-A-A-C; 10 warmups and 100 strict CUPTI cold-L2 CUDA-graph samples per phase. Frozen routing and retained-head tactics; no autotuning. NVFP4 includes initial quantization, swap-AB uses unfused finalize. Existing unsupported comparisons skipped. No TRTLLM/non-swap baseline reruns.
- Speedup is 100×(geometric mean control phase medians / geometric mean candidate phase medians−1). Raw phase samples, source hashes, routes, winner/cache identities and GPU identities are in the linked evidence folders. W4A16 is an unchanged diagnostic excluded from optimization aggregates.
- Current-head maximum within-arm repeated-phase spread is 6.21% for control and 3.14% for candidate; small individual changes should not be overinterpreted. The W4A16 diagnostic aggregate is +0.045%. Paired R6/R14 maximum spreads are 2.77%/3.18%.

## Source and reproducibility

- Measured R14 kernel SHA: `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372`.
- R6 kernel SHA: `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`.
- [Full15 configuration](../r14/evidence/perf-config.json), [raw data](../r14/evidence/perf), [validated CSV](../r14/report/cells.csv), [summary](../r14/report/summary.json).
- [R6 paired campaign](../r14-r6/README.md), [ordering proof](relay-publication/ORDERING.md), [iKET evidence](iket/RESULT.md), [combined codegen](relay-publication/combined-codegen/REPORT.md), [static ownership audit](unsigned-metadata/README.md).
- Every arm verifies 513 source files and frozen patch hashes. The launch receipts retain exact commands, environment and cache links. R14 full15 uses `r14/perf-full15-runtime-launch.json` in the evidence tree. Failed compiler-artifact guard attempts are retained as harness diagnostics and excluded from performance results; the final guard queries the actual loaded CUDA kernel before launch.

```bash
# From the project root; analyses/plots can be regenerated locally.
python3 fc1-gather-20261028/r11/guarded-validation/analyze_perf.py \
  fc1-gather-20261028/r14/evidence/perf --expected-jobs 15 --expected-cells 144 \
  --output fc1-gather-20261028/r14/report
fc1-gather-20261028/plot-venv/bin/python \
  fc1-gather-20261028/r14/plot_heatmap.py fc1-gather-20261028/r14
```

## Full raw pass medians vs PR head

Latencies are µs; C1/A1/A2/C2 are the four retained phase medians. Percentages are derived from those medians, not rounded table values.

| Model | Mode | Tokens | Backend | C1 µs | A1 µs | A2 µs | C2 µs | Speedup |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| K3 | EP8 | 8 | CuteDSL MXFP4x8 | 78.209 | 76.257 | 76.337 | 78.081 | +2.42% |
| K3 | EP8 | 256 | CuteDSL MXFP4x8 | 320.098 | 317.075 | 316.947 | 320.083 | +0.97% |
| K3 | EP8 | 4096 | CuteDSL MXFP4x8 | 397.219 | 396.739 | 393.475 | 396.403 | +0.43% |
| K3 | EP8 | 16384 | CuteDSL MXFP4x8 | 1025.288 | 1078.232 | 1067.017 | 1072.697 | -2.23% |
| K3 | EP8 | 8 | CuteDSL W4A4 | 81.889 | 79.921 | 79.888 | 81.984 | +2.54% |
| K3 | EP8 | 8 | CuteDSL PER-TOKEN | 86.320 | 83.456 | 83.616 | 86.176 | +3.25% |
| K3 | EP8 | 8 | CuteDSL W4A16 | 84.177 | 84.817 | 84.848 | 84.352 | -0.67% |
| K3 | EP8 | 256 | CuteDSL W4A4 | 328.705 | 327.713 | 327.809 | 328.081 | +0.19% |
| K3 | EP8 | 256 | CuteDSL PER-TOKEN | 337.025 | 338.129 | 338.050 | 338.720 | -0.06% |
| K3 | EP8 | 256 | CuteDSL W4A16 | 350.800 | 350.786 | 350.706 | 350.882 | +0.03% |
| K3 | EP8 | 4096 | CuteDSL W4A4 | 384.929 | 389.649 | 389.778 | 385.089 | -1.21% |
| K3 | EP8 | 4096 | CuteDSL PER-TOKEN | 448.913 | 461.474 | 460.786 | 448.850 | -2.66% |
| K3 | EP8 | 4096 | CuteDSL W4A16 | 535.122 | 538.578 | 539.090 | 539.217 | -0.31% |
| K3 | EP8 | 16384 | CuteDSL W4A4 | 705.123 | 770.067 | 765.891 | 704.611 | -8.22% |
| K3 | EP8 | 16384 | CuteDSL PER-TOKEN | 1011.108 | 1085.493 | 1084.516 | 1019.236 | -6.44% |
| K3 | EP8 | 16384 | CuteDSL W4A16 | 2001.303 | 1980.920 | 1979.431 | 1967.063 | +0.20% |
| N3U | EP8 | 8 | CuteDSL MXFP8 | 72.192 | 70.257 | 70.289 | 72.177 | +2.72% |
| N3U | EP8 | 8 | CuteDSL MXFP4x8 | 50.337 | 47.200 | 47.264 | 50.240 | +6.47% |
| N3U | EP8 | 256 | CuteDSL MXFP8 | 233.473 | 232.977 | 233.010 | 232.946 | +0.09% |
| N3U | EP8 | 256 | CuteDSL MXFP4x8 | 134.993 | 134.897 | 134.961 | 135.361 | +0.18% |
| N3U | EP8 | 4096 | CuteDSL MXFP8 | 311.794 | 329.938 | 330.018 | 311.426 | -5.57% |
| N3U | EP8 | 4096 | CuteDSL MXFP4x8 | 251.569 | 277.058 | 277.809 | 251.281 | -9.37% |
| N3U | EP8 | 16384 | CuteDSL MXFP8 | 862.470 | 951.110 | 967.125 | 856.069 | -10.41% |
| N3U | EP8 | 16384 | CuteDSL MXFP4x8 | 798.469 | 880.117 | 893.621 | 793.510 | -10.25% |
| N3U | EP8 | 8 | CuteDSL W4A4 | 51.601 | 47.392 | 47.185 | 51.233 | +8.73% |
| N3U | EP8 | 8 | CuteDSL PER-TOKEN | 52.705 | 51.008 | 50.945 | 52.736 | +3.42% |
| N3U | EP8 | 8 | CuteDSL W4A16 | 52.449 | 52.513 | 52.609 | 52.545 | -0.12% |
| N3U | EP8 | 256 | CuteDSL W4A4 | 140.161 | 140.673 | 140.561 | 140.289 | -0.28% |
| N3U | EP8 | 256 | CuteDSL PER-TOKEN | 152.065 | 150.305 | 150.320 | 152.097 | +1.18% |
| N3U | EP8 | 256 | CuteDSL W4A16 | 153.649 | 153.249 | 153.200 | 153.793 | +0.32% |
| N3U | EP8 | 4096 | CuteDSL W4A4 | 227.041 | 285.186 | 285.538 | 227.282 | -20.40% |
| N3U | EP8 | 4096 | CuteDSL PER-TOKEN | 319.010 | 366.195 | 365.875 | 318.834 | -12.87% |
| N3U | EP8 | 4096 | CuteDSL W4A16 | 401.170 | 401.970 | 400.771 | 402.531 | +0.12% |
| N3U | EP8 | 16384 | CuteDSL W4A4 | 522.771 | 752.821 | 752.964 | 519.508 | -30.78% |
| N3U | EP8 | 16384 | CuteDSL PER-TOKEN | 853.013 | 932.261 | 931.413 | 853.157 | -8.45% |
| N3U | EP8 | 16384 | CuteDSL W4A16 | 1472.042 | 1579.737 | 1581.530 | 1563.481 | -4.02% |
| V3 | EP8 | 8 | CuteDSL MXFP8 | 91.569 | 88.689 | 88.689 | 91.553 | +3.24% |
| V3 | EP8 | 8 | CuteDSL MXFP4x8 | 59.024 | 55.937 | 55.840 | 59.024 | +5.61% |
| V3 | EP8 | 256 | CuteDSL MXFP8 | 241.281 | 242.513 | 242.258 | 241.329 | -0.45% |
| V3 | EP8 | 256 | CuteDSL MXFP4x8 | 142.289 | 139.969 | 140.033 | 142.209 | +1.61% |
| V3 | EP8 | 4096 | CuteDSL MXFP8 | 304.274 | 296.690 | 296.834 | 304.530 | +2.57% |
| V3 | EP8 | 4096 | CuteDSL MXFP4x8 | 229.217 | 229.953 | 237.185 | 229.025 | -1.89% |
| V3 | EP8 | 16384 | CuteDSL MXFP8 | 769.189 | 786.533 | 791.988 | 754.708 | -3.46% |
| V3 | EP8 | 16384 | CuteDSL MXFP4x8 | 688.724 | 678.388 | 663.988 | 676.981 | +1.74% |
| V3 | EP8 | 8 | CuteDSL W4A4 | 58.800 | 57.937 | 58.000 | 59.009 | +1.61% |
| V3 | EP8 | 8 | CuteDSL PER-TOKEN | 63.792 | 62.608 | 62.464 | 63.761 | +1.98% |
| V3 | EP8 | 8 | CuteDSL W4A16 | 65.984 | 65.920 | 65.873 | 65.856 | +0.04% |
| V3 | EP8 | 256 | CuteDSL W4A4 | 146.273 | 145.408 | 145.153 | 146.017 | +0.60% |
| V3 | EP8 | 256 | CuteDSL PER-TOKEN | 152.737 | 151.937 | 151.921 | 152.705 | +0.52% |
| V3 | EP8 | 256 | CuteDSL W4A16 | 152.946 | 152.481 | 152.641 | 152.768 | +0.19% |
| V3 | EP8 | 4096 | CuteDSL W4A4 | 205.713 | 202.962 | 202.242 | 205.601 | +1.51% |
| V3 | EP8 | 4096 | CuteDSL PER-TOKEN | 248.289 | 247.425 | 247.377 | 248.546 | +0.41% |
| V3 | EP8 | 4096 | CuteDSL W4A16 | 294.210 | 293.425 | 291.505 | 292.434 | +0.29% |
| V3 | EP8 | 16384 | CuteDSL W4A4 | 479.554 | 559.891 | 559.891 | 479.459 | -14.36% |
| V3 | EP8 | 16384 | CuteDSL PER-TOKEN | 609.907 | 721.540 | 722.101 | 608.387 | -15.61% |
| V3 | EP8 | 16384 | CuteDSL W4A16 | 1197.079 | 1227.031 | 1193.896 | 1216.246 | -0.31% |
| V41F | EP4 | 8 | CuteDSL MXFP8 | 73.312 | 73.280 | 73.217 | 73.201 | +0.01% |
| V41F | EP4 | 8 | CuteDSL MXFP4x8 | 47.392 | 49.921 | 49.889 | 47.489 | -4.94% |
| V41F | EP4 | 256 | CuteDSL MXFP8 | 529.300 | 530.949 | 531.220 | 528.917 | -0.37% |
| V41F | EP4 | 256 | CuteDSL MXFP4x8 | 290.770 | 288.291 | 288.098 | 290.707 | +0.88% |
| V41F | EP4 | 4096 | CuteDSL MXFP8 | 587.444 | 575.173 | 575.141 | 587.269 | +2.12% |
| V41F | EP4 | 4096 | CuteDSL MXFP4x8 | 360.019 | 352.307 | 351.716 | 359.668 | +2.22% |
| V41F | EP4 | 16384 | CuteDSL MXFP8 | 985.704 | 951.304 | 951.000 | 949.672 | +1.72% |
| V41F | EP4 | 16384 | CuteDSL MXFP4x8 | 850.759 | 814.326 | 810.982 | 802.407 | +1.67% |
| V41F | EP4 | 8 | CuteDSL W4A4 | 45.969 | 44.385 | 44.224 | 46.113 | +3.92% |
| V41F | EP4 | 8 | CuteDSL PER-TOKEN | 52.176 | 50.481 | 50.512 | 52.097 | +3.25% |
| V41F | EP4 | 8 | CuteDSL W4A16 | 51.617 | 51.744 | 51.648 | 51.585 | -0.18% |
| V41F | EP4 | 256 | CuteDSL W4A4 | 301.283 | 299.971 | 300.276 | 301.172 | +0.37% |
| V41F | EP4 | 256 | CuteDSL PER-TOKEN | 310.579 | 310.084 | 309.988 | 310.308 | +0.13% |
| V41F | EP4 | 256 | CuteDSL W4A16 | 316.756 | 316.612 | 316.707 | 316.676 | +0.02% |
| V41F | EP4 | 4096 | CuteDSL W4A4 | 350.420 | 340.644 | 340.980 | 350.788 | +2.87% |
| V41F | EP4 | 4096 | CuteDSL PER-TOKEN | 406.724 | 397.429 | 397.797 | 407.541 | +2.39% |
| V41F | EP4 | 4096 | CuteDSL W4A16 | 454.597 | 454.997 | 456.517 | 454.229 | -0.29% |
| V41F | EP4 | 16384 | CuteDSL W4A4 | 574.487 | 671.192 | 672.600 | 579.015 | -14.16% |
| V41F | EP4 | 16384 | CuteDSL PER-TOKEN | 748.856 | 764.633 | 759.178 | 747.560 | -1.80% |
| V41F | EP4 | 16384 | CuteDSL W4A16 | 1637.779 | 1500.370 | 1545.459 | 1581.186 | +5.68% |
| K3 | TP8 | 8 | CuteDSL MXFP4x8 | 76.129 | 79.648 | 79.648 | 75.984 | -4.51% |
| K3 | TP8 | 256 | CuteDSL MXFP4x8 | 339.921 | 325.922 | 325.745 | 339.554 | +4.27% |
| K3 | TP8 | 4096 | CuteDSL MXFP4x8 | 654.819 | 553.139 | 552.771 | 654.932 | +18.43% |
| K3 | TP8 | 16384 | CuteDSL MXFP4x8 | 1901.978 | 1662.986 | 1660.873 | 1902.091 | +14.45% |
| K3 | TP8 | 8 | CuteDSL W4A4 | 77.633 | 78.145 | 78.225 | 77.697 | -0.66% |
| K3 | TP8 | 8 | CuteDSL PER-TOKEN | 83.425 | 81.889 | 81.904 | 83.489 | +1.91% |
| K3 | TP8 | 8 | CuteDSL W4A16 | 86.736 | 86.609 | 86.688 | 86.721 | +0.09% |
| K3 | TP8 | 256 | CuteDSL W4A4 | 354.820 | 342.531 | 342.179 | 354.931 | +3.66% |
| K3 | TP8 | 256 | CuteDSL PER-TOKEN | 373.715 | 360.707 | 360.579 | 373.299 | +3.57% |
| K3 | TP8 | 256 | CuteDSL W4A16 | 411.027 | 411.139 | 411.188 | 410.675 | -0.08% |
| K3 | TP8 | 4096 | CuteDSL W4A4 | 641.925 | 552.644 | 552.212 | 641.654 | +16.18% |
| K3 | TP8 | 4096 | CuteDSL PER-TOKEN | 807.990 | 712.422 | 711.990 | 808.407 | +13.48% |
| K3 | TP8 | 4096 | CuteDSL W4A16 | 866.232 | 835.798 | 851.415 | 850.823 | +1.77% |
| K3 | TP8 | 16384 | CuteDSL W4A4 | 1547.740 | 1435.995 | 1437.533 | 1559.134 | +8.12% |
| K3 | TP8 | 16384 | CuteDSL PER-TOKEN | 2161.426 | 2025.711 | 2025.457 | 2160.578 | +6.69% |
| K3 | TP8 | 16384 | CuteDSL W4A16 | 2970.745 | 2952.951 | 2950.714 | 2955.145 | +0.38% |
| N3U | TP8 | 8 | CuteDSL MXFP8 | 86.481 | 85.809 | 85.761 | 86.497 | +0.82% |
| N3U | TP8 | 8 | CuteDSL MXFP4x8 | 58.752 | 59.537 | 59.569 | 58.721 | -1.37% |
| N3U | TP8 | 256 | CuteDSL MXFP8 | 246.147 | 240.931 | 240.995 | 246.323 | +2.19% |
| N3U | TP8 | 256 | CuteDSL MXFP4x8 | 149.489 | 144.050 | 144.018 | 149.601 | +3.83% |
| N3U | TP8 | 4096 | CuteDSL MXFP8 | 497.317 | 444.725 | 444.310 | 497.685 | +11.92% |
| N3U | TP8 | 4096 | CuteDSL MXFP4x8 | 437.157 | 411.221 | 411.173 | 437.318 | +6.33% |
| N3U | TP8 | 16384 | CuteDSL MXFP8 | 1494.706 | 1407.873 | 1406.945 | 1491.538 | +6.09% |
| N3U | TP8 | 16384 | CuteDSL MXFP4x8 | 1438.401 | 1330.560 | 1332.048 | 1428.001 | +7.65% |
| N3U | TP8 | 8 | CuteDSL W4A4 | 60.112 | 60.080 | 60.145 | 60.192 | +0.07% |
| N3U | TP8 | 8 | CuteDSL PER-TOKEN | 67.504 | 64.321 | 64.448 | 67.520 | +4.86% |
| N3U | TP8 | 8 | CuteDSL W4A16 | 66.401 | 66.385 | 66.304 | 66.416 | +0.10% |
| N3U | TP8 | 256 | CuteDSL W4A4 | 153.281 | 149.617 | 149.617 | 153.025 | +2.36% |
| N3U | TP8 | 256 | CuteDSL PER-TOKEN | 172.113 | 168.241 | 168.288 | 172.129 | +2.29% |
| N3U | TP8 | 256 | CuteDSL W4A16 | 175.650 | 176.690 | 176.465 | 175.729 | -0.50% |
| N3U | TP8 | 4096 | CuteDSL W4A4 | 410.114 | 419.443 | 419.523 | 410.146 | -2.23% |
| N3U | TP8 | 4096 | CuteDSL PER-TOKEN | 622.995 | 626.340 | 626.004 | 623.380 | -0.48% |
| N3U | TP8 | 4096 | CuteDSL W4A16 | 625.940 | 634.308 | 627.891 | 624.388 | -0.94% |
| N3U | TP8 | 16384 | CuteDSL W4A4 | 1189.990 | 1292.007 | 1291.736 | 1190.054 | -7.88% |
| N3U | TP8 | 16384 | CuteDSL PER-TOKEN | 1933.371 | 2003.772 | 2001.517 | 1933.580 | -3.45% |
| N3U | TP8 | 16384 | CuteDSL W4A16 | 2316.062 | 2332.126 | 2322.669 | 2334.126 | -0.10% |
| V3 | TP8 | 8 | CuteDSL MXFP8 | 72.144 | 70.977 | 71.168 | 72.032 | +1.43% |
| V3 | TP8 | 8 | CuteDSL MXFP4x8 | 50.305 | 50.513 | 50.576 | 50.400 | -0.38% |
| V3 | TP8 | 256 | CuteDSL MXFP8 | 256.947 | 252.099 | 252.115 | 257.042 | +1.94% |
| V3 | TP8 | 256 | CuteDSL MXFP4x8 | 156.098 | 153.442 | 153.458 | 156.161 | +1.75% |
| V3 | TP8 | 4096 | CuteDSL MXFP8 | 543.796 | 447.972 | 447.860 | 543.284 | +21.35% |
| V3 | TP8 | 4096 | CuteDSL MXFP4x8 | 475.731 | 393.683 | 394.051 | 475.460 | +20.75% |
| V3 | TP8 | 16384 | CuteDSL MXFP8 | 1557.212 | 1362.652 | 1363.564 | 1555.645 | +14.18% |
| V3 | TP8 | 16384 | CuteDSL MXFP4x8 | 1498.764 | 1253.724 | 1244.315 | 1499.724 | +20.03% |
| V3 | TP8 | 8 | CuteDSL W4A4 | 51.424 | 50.129 | 50.129 | 51.328 | +2.49% |
| V3 | TP8 | 8 | CuteDSL PER-TOKEN | 56.673 | 54.929 | 54.913 | 56.689 | +3.21% |
| V3 | TP8 | 8 | CuteDSL W4A16 | 64.417 | 64.385 | 64.545 | 64.529 | +0.01% |
| V3 | TP8 | 256 | CuteDSL W4A4 | 162.081 | 155.394 | 155.042 | 161.698 | +4.30% |
| V3 | TP8 | 256 | CuteDSL PER-TOKEN | 175.266 | 168.690 | 168.770 | 175.394 | +3.91% |
| V3 | TP8 | 256 | CuteDSL W4A16 | 181.507 | 181.714 | 181.683 | 181.682 | -0.06% |
| V3 | TP8 | 4096 | CuteDSL W4A4 | 445.798 | 391.509 | 391.317 | 445.829 | +13.90% |
| V3 | TP8 | 4096 | CuteDSL PER-TOKEN | 563.735 | 501.478 | 502.198 | 564.167 | +12.38% |
| V3 | TP8 | 4096 | CuteDSL W4A16 | 646.792 | 647.447 | 647.064 | 647.191 | -0.04% |
| V3 | TP8 | 16384 | CuteDSL W4A4 | 1258.560 | 1123.565 | 1123.630 | 1259.263 | +12.04% |
| V3 | TP8 | 16384 | CuteDSL PER-TOKEN | 1610.629 | 1454.449 | 1454.690 | 1610.851 | +10.74% |
| V3 | TP8 | 16384 | CuteDSL W4A16 | 2282.717 | 2265.275 | 2279.308 | 2297.596 | +0.79% |
| V41F | TP4 | 8 | CuteDSL W4A4 | 52.896 | 51.648 | 51.840 | 52.976 | +2.30% |
| V41F | TP4 | 8 | CuteDSL PER-TOKEN | 58.592 | 57.441 | 57.441 | 58.513 | +1.94% |
| V41F | TP4 | 8 | CuteDSL W4A16 | 61.776 | 61.664 | 61.616 | 61.633 | +0.10% |
| V41F | TP4 | 256 | CuteDSL W4A4 | 318.113 | 317.249 | 317.298 | 317.441 | +0.16% |
| V41F | TP4 | 256 | CuteDSL PER-TOKEN | 326.370 | 323.553 | 323.697 | 327.058 | +0.95% |
| V41F | TP4 | 256 | CuteDSL W4A16 | 359.202 | 359.362 | 359.713 | 359.233 | -0.09% |
| V41F | TP4 | 4096 | CuteDSL W4A4 | 484.002 | 441.026 | 440.994 | 483.825 | +9.73% |
| V41F | TP4 | 4096 | CuteDSL PER-TOKEN | 592.099 | 557.570 | 558.002 | 592.274 | +6.17% |
| V41F | TP4 | 4096 | CuteDSL W4A16 | 617.218 | 622.115 | 624.802 | 628.594 | -0.09% |
| V41F | TP4 | 16384 | CuteDSL W4A4 | 1031.700 | 1026.436 | 1026.260 | 1031.060 | +0.49% |
| V41F | TP4 | 16384 | CuteDSL PER-TOKEN | 1333.638 | 1493.365 | 1493.478 | 1334.005 | -10.69% |
| V41F | TP4 | 16384 | CuteDSL W4A16 | 2120.441 | 2120.376 | 2122.825 | 2097.161 | -0.60% |
