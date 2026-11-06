# Compact FC2 TMA R2

Unretained candidate on retained `2cfb06afd`. Both source roles include the retained partial-K peel. Source: `local-source.json`; kernel SHA `c44172ecc91263a748990d1543d7729df15b0944a775a70665ac9b5330122808`.

- Exact gate: **256/256** final-output storage-bit comparisons plus 256 independently checked compact metadata states. Short K384, long K2304; N16/32/128/256; one/two-CTA; shared static/CLC; PDL off/on; standard/per-token NVFP4, MXFP8, MXFP4x8; SwiGLU, SiTU and Relu2 pairwise. Mutable graph routing includes balanced, skewed, empty and reactivated local routes. Original inverse/reverse sort maps remain reciprocal and unchanged in contract; dense indices cover the local compact domain exactly once.
- Codegen: **128 paired kernels**, 64 FC1 instruction-identical pairs; no stack/local traffic. Uniform MOV.SPILL/R2UR.FILL sites are present in both roles:24/64 FC2 kernels each,544→521 spill sites in total (matching fill counts), per-pair delta−20 to+9; this is not an all-spill-free claim. Natural `(bulk_tokens,bulk_stages)` geometries `(64,2)` and `(32,1)` both qualified. Complete/partial slab selection occurs before shared writes; no transpose is added. R2 adds **80–328 static FC2 instruction sites**, with registers **−14 to +30**, because both complete-slab TMA and compact-tail row stores exist. These are static counts, not executed counts.
- Storage: original BF16 output capacity retained. Added integer metadata is at most **1.386 MiB** across 87 saved model/topology/format/token winner cells, at most **0.1954%** of control FC2 allocation; see `ALLOCATION.md`. Host allocation/descriptor construction remains outside warmed CUDAgraph timing.
- Boundary: existing hidden dimension multiple-of-128 capability preserved. No unsupported m320 kernel, exhaustive tactic matrix, Rubin test or candidate sanitizer. Original full sanitizer results do not qualify R2.

Gate archive SHA `5692c5a08962f88723327f8ba19239e2f135595cbd28bbce2d73cadd7349a6a8`; **1,118 files** hash-verified locally. `audit_codegen_local.py` independently checks copied PTX/SASS/resource evidence.


## Full matched performance screen

Fixed winners, C–A–A–C, 2cfb06afd control versus compact candidate; public functional API, cold-L2 CUDAgraphs, 10warmups and100 strict CUPTI samples per pass. NV includes input quantization. 72cells/288medians/28,800samples;56affected cells plus16unchanged W4A16 sanity cells. Raw medians, routes, source, winner/cache identity and GPU UUID were independently verified.

| Topology | Decode ≤64 | Prefill ≥4096 | All affected |
|---|---:|---:|---:|
| EP | -1.072% | +0.032% | -0.522% |
| TP | -4.164% | +6.063% | +0.820% |

Speedup is `mean(C1,C2) / mean(A1,A2) − 1`; positive is faster. No correction for unchanged-path noise or pass drift is applied. Host allocation/descriptor encoding are outside warmed GPU timing.

| Job | Backend | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | BF16 FC2 MiB (both) | Added metadata KiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 50.720 | 52.305 | 52.353 | 50.753 | -3.043% | 0.438 | 0.500 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 228.929 | 229.873 | 230.129 | 229.346 | -0.375% | 7.000 | 4.660 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 395.250 | 395.874 | 395.699 | 394.867 | -0.184% | 448.000 | 258.434 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 1029.542 | 1066.486 | 1047.975 | 1074.966 | -0.471% | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 51.632 | 53.200 | 53.312 | 51.601 | -3.079% | 0.438 | 0.500 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 56.672 | 58.401 | 58.240 | 56.736 | -2.771% | 0.438 | 0.500 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 57.360 | 57.280 | 57.393 | 57.392 | +0.069% | 0.438 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 237.857 | 238.689 | 238.626 | 237.793 | -0.349% | 7.000 | 4.547 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 244.434 | 245.250 | 245.393 | 244.322 | -0.385% | 7.000 | 4.660 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 250.321 | 250.130 | 250.274 | 250.305 | +0.045% | 7.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 387.794 | 386.227 | 386.115 | 387.410 | +0.371% | 448.000 | 258.434 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 448.419 | 449.523 | 447.026 | 447.827 | -0.034% | 448.000 | 258.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 551.315 | 564.371 | 554.788 | 564.212 | -0.325% | 448.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 768.853 | 749.541 | 765.588 | 749.173 | +0.191% | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1045.431 | 1029.654 | 1031.463 | 1050.359 | +1.682% | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 2011.725 | 2082.333 | 2077.421 | 2040.014 | -2.597% | 1792.000 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4 | 68.001 | 68.544 | 68.480 | 68.017 | -0.735% | 0.438 | 0.250 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4 | 46.529 | 47.024 | 47.088 | 46.433 | -1.223% | 0.438 | 0.250 |
| ep-v3-mxfp | CuteDSL MXFP8 | 64 | 219.474 | 219.681 | 219.714 | 219.490 | -0.098% | 7.000 | 2.242 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 64 | 129.313 | 129.776 | 129.921 | 129.313 | -0.412% | 7.000 | 2.242 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4096 | 306.082 | 307.074 | 307.187 | 306.131 | -0.333% | 448.000 | 128.621 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 228.513 | 230.210 | 230.354 | 228.450 | -0.782% | 448.000 | 128.621 |
| ep-v3-mxfp | CuteDSL MXFP8 | 16384 | 703.990 | 715.861 | 736.822 | 705.717 | -2.958% | 1792.000 | 514.121 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 674.933 | 670.421 | 696.597 | 683.093 | -0.658% | 1792.000 | 516.121 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4 | 46.321 | 46.768 | 46.752 | 46.416 | -0.837% | 0.438 | 0.250 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 51.936 | 52.305 | 52.481 | 51.889 | -0.917% | 0.438 | 0.250 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4 | 51.952 | 52.097 | 52.032 | 51.985 | -0.185% | 0.438 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 64 | 130.401 | 130.977 | 131.120 | 130.657 | -0.397% | 7.000 | 2.242 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 136.369 | 136.865 | 137.025 | 136.657 | -0.315% | 7.000 | 2.242 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 64 | 142.465 | 142.657 | 142.881 | 142.898 | -0.061% | 7.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4096 | 207.682 | 207.730 | 207.633 | 207.618 | -0.015% | 448.000 | 128.621 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 249.458 | 248.673 | 248.833 | 250.275 | +0.447% | 448.000 | 128.621 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4096 | 287.330 | 287.666 | 287.939 | 286.594 | -0.292% | 448.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 16384 | 500.243 | 490.388 | 490.724 | 500.468 | +1.998% | 1792.000 | 514.121 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 636.710 | 630.053 | 628.292 | 637.877 | +1.291% | 1792.000 | 516.121 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 16384 | 1172.969 | 1197.065 | 1179.753 | 1166.009 | -1.592% | 1792.000 | 0.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 41.824 | 45.345 | 45.312 | 41.856 | -7.695% | 0.438 | 0.500 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 241.681 | 249.762 | 249.730 | 241.346 | -3.296% | 7.000 | 7.531 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 716.486 | 688.262 | 689.382 | 716.341 | +4.006% | 448.000 | 261.473 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 2093.057 | 1955.760 | 1952.896 | 2082.994 | +6.841% | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 43.344 | 46.673 | 46.721 | 43.360 | -7.162% | 0.438 | 0.500 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 46.112 | 50.785 | 50.705 | 46.177 | -9.065% | 0.438 | 0.500 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 50.896 | 50.912 | 50.817 | 50.849 | +0.016% | 0.438 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 248.642 | 252.355 | 252.050 | 248.690 | -1.402% | 7.000 | 7.531 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 257.602 | 269.394 | 269.602 | 257.971 | -4.346% | 7.000 | 7.531 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 282.226 | 282.162 | 282.114 | 282.019 | -0.006% | 7.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 690.118 | 660.885 | 661.013 | 689.831 | +4.391% | 448.000 | 261.473 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 855.319 | 863.687 | 862.471 | 855.640 | -0.881% | 448.000 | 261.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 830.758 | 833.959 | 842.167 | 845.415 | +0.003% | 448.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 1786.942 | 1659.918 | 1661.901 | 1785.776 | +7.553% | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 2407.764 | 2398.964 | 2398.756 | 2406.725 | +0.350% | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 2935.176 | 2933.512 | 2977.401 | 2985.899 | +0.172% | 1792.000 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4 | 46.688 | 48.032 | 47.936 | 46.800 | -2.584% | 0.438 | 0.250 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4 | 35.424 | 36.752 | 36.640 | 35.361 | -3.553% | 0.438 | 0.250 |
| tp-v3-mxfp | CuteDSL MXFP8 | 64 | 227.426 | 230.754 | 230.961 | 227.537 | -1.462% | 7.000 | 3.062 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 64 | 144.257 | 145.985 | 146.001 | 144.017 | -1.271% | 7.000 | 3.062 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4096 | 634.821 | 595.844 | 595.876 | 634.980 | +6.552% | 448.000 | 129.992 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 556.468 | 509.172 | 509.811 | 557.076 | +9.280% | 448.000 | 129.992 |
| tp-v3-mxfp | CuteDSL MXFP8 | 16384 | 1786.557 | 1648.524 | 1643.148 | 1787.101 | +8.567% | 1792.000 | 514.996 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 1733.228 | 1582.795 | 1583.932 | 1735.661 | +9.542% | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4 | 36.704 | 38.273 | 38.320 | 36.576 | -4.324% | 0.438 | 0.250 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 40.384 | 42.896 | 42.784 | 40.320 | -5.808% | 0.438 | 0.250 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4 | 39.983 | 39.968 | 40.096 | 40.000 | -0.102% | 0.438 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 64 | 143.297 | 144.865 | 144.834 | 143.473 | -1.011% | 7.000 | 3.062 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 151.313 | 159.041 | 159.073 | 151.345 | -4.858% | 7.000 | 3.062 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 64 | 154.834 | 154.706 | 154.706 | 154.513 | -0.021% | 7.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4096 | 524.132 | 491.268 | 490.979 | 523.524 | +6.659% | 448.000 | 129.992 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 615.476 | 615.476 | 614.933 | 615.605 | +0.055% | 448.000 | 129.992 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4096 | 643.268 | 644.389 | 644.021 | 643.780 | -0.106% | 448.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 16384 | 1541.915 | 1368.202 | 1369.483 | 1543.435 | +12.699% | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1888.574 | 1712.540 | 1712.285 | 1889.198 | +10.306% | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 16384 | 2234.544 | 2239.137 | 2228.512 | 2246.769 | +0.306% | 1792.000 | 0.000 |

## Evidence and retention

- `perf-analysis.json`, `perf-cells.csv`, `audit_perf.py`: complete raw pass medians and independent source/cache/CUPTI checks.
- `perf-evidence/`: archive SHA256 `917d79814329dada0871a213d50fbab47b532e700c8caea477bbd14e35553e80`.
- `gate-evidence/`, `codegen-analysis.json`: source-bound exact metadata/output and native codegen checks.

**Not retained.** Compact storage removes R1’s allocation increase, but the candidate still adds decode latency, slightly slows EP, and increases FC2 code and register pressure. No production policy or new shape-specific enable switch was added to hide these regressions.
