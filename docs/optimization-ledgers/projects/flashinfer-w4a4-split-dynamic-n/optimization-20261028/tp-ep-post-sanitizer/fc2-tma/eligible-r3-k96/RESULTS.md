# Operation-eligible compact FC2 output, on retained K96

Status: exact/codegen and the complete matched performance screen passed evidence checks. Retention is pending review; nothing from this experiment is committed.

- Control: `21fbe72c6f70643a2b61c7461f42937dbfb307e9`, immutable remote retained source.
- Candidate: the same head plus five unstaged files in `flashinfer-fc2-tma-review`; patch SHA256 `4913604b69bf91dacc50ddce60ef81e7f5102732fcc043aa1541a1f1187cf03a`.
- Kernel SHA256: control `9617d7da660d201a5e7c56bf33613cc24b1a20c05f8d1e022cd545c37efc31b5`; candidate `031483d37c95cb0e451791add466e5422bbbc35335950f0c923f55928a145d61`.
- General policy: select compact FC2 output only when the existing automatic epilogue planner reserves a bulk-store slab. No added tactic axis or token/model/dtype-specific enable rule. Non-bulk plans keep the original expanded output and compile out all new prefix/dense-index work.
- Storage: unchanged BF16 output capacity `tokens * top_k * hidden`; eligible plans add int32 metadata per expanded route and reserved routing tile. No host readback or new caller alignment requirement.
- K96 integration: the retained 1024-byte operand alignment and its shared-memory reserve remain intact. `planner_proof.py` checks336 automatic plans; independent `scheduler-review/planner-proof.json` checks1260 admitted geometries with additional output-width coverage. No automatic eligible plan loses its actual32/64-row slab. Existing explicit forced-depth fallback remains valid.

## Exact and code generation

Three paired gates cover K384/K2304 and a forced32-row bulk stage: 256 output-storage-bit comparisons, changing balanced/skewed/empty/reactivated CUDAgraph routing, static/CLC, PDL off/on, one/two CTA, NVFP4 standard/per-token, MXFP8/MXFP4x8, and gated/non-gated activation cases. Metadata checks independently verify prefix sums, dense-index uniqueness/range, and unchanged original inverse/reverse routing maps.

128 paired GEMM specializations were independently checked. All64 FC1 and16 non-bulk FC2 instruction streams are identical. The48 bulk FC2 pairs add80…328 static instructions and change registers by−14…+30. Both32-row/one-stage and64-row/two-stage stores are covered. All have zero local/stack traffic. Uniform-register `MOV.SPILL`/`R2UR.FILL` sites are reported separately in `codegen-analysis.json`; they are present in both sources, so this is not a spill-free claim.

Evidence: `gate-evidence/` contains1136 SHA-verified files; archive SHA256 `cebaa9cd3c19d3c58ba3170393487a080cce014c61ff3ef929f8ef72966f1c33`. Unsupported partial-channel shapes were not enabled. No candidate sanitizer has run.

## Performance contract

All four model shapes, EP and TP, tokens4/64/4096/16384, supported format arms only. Skip TP V41F MX and K3 MXFP8. Fifteen family jobs produce144 cells, including32 unchanged W4A16 sanity cells. Frozen previously selected tactics, C–A–A–C,10warmups and100 strict CUPTI cold-L2 CUDAgraph samples per pass; NV includes input quantization. Expected576 medians/57,600samples. Per-cell speedup is the geometric mean of the two control pass medians divided by the geometric mean of the two candidate pass medians, minus one. Source hashes, GPU UUIDs, routes, cache/winner identity, native argv, and absence of tuning are bound in each receipt. Host allocation and descriptor encoding are outside warmed GPU timing. No external-baseline results are replaced.

## Helpers

- `prepare_helpers.py`, `deploy_template.py`: source receipt and isolated remote candidate deployment; preserve existing native C++ cache links.
- `gate_campaign.py`, `run_gate.py`, `probe_pair.py`: paired exact/codegen gates, with private compiler working directories.
- `analyze_codegen.py`, `audit_codegen_local.py`: native artifact checks, including uniform-register spill/fill sites.
- `prepare_perf_remote.py`, `perf_campaign.py`, `run_perf.py`: complete15-job fixed-winner screen on eight disjoint GPU lanes.
- `fetch_evidence.py`, `audit_perf.py`: immutable archive fetch and independent local sample/median/cache/source audit.

## Full matched performance screen

144cells/576medians/57,600samples;112 affected cells and32 unchanged W4A16 sanity cells. All native raw medians, routes, source, winner/cache identity, argv and GPU UUID were independently verified. Per-cell speedup is `geomean(C1,C2) / geomean(A1,A2) − 1`; positive is faster. No correction for unchanged-path noise or pass drift is applied.

| Topology | Decode ≤64 | Prefill ≥4096 | All affected |
|---|---:|---:|---:|
| EP | -0.009% | +0.027% | +0.009% |
| TP | -0.000% | +4.678% | +2.312% |

| Topology/model | Decode | Prefill | All affected |
|---|---:|---:|---:|
| EP v3 | -0.022% | +0.493% | +0.235% |
| EP v41-flash | -0.044% | +0.325% | +0.140% |
| EP kimi-k3 | +0.036% | +0.518% | +0.277% |
| EP nemo3-ultra | +0.004% | -1.096% | -0.548% |
| TP v3 | -0.018% | +7.968% | +3.898% |
| TP v41-flash | +0.020% | +3.904% | +1.943% |
| TP kimi-k3 | +0.063% | +3.602% | +1.817% |
| TP nemo3-ultra | -0.039% | +2.658% | +1.301% |

| Format | EP decode | EP prefill | TP decode | TP prefill |
|---|---:|---:|---:|---:|
| CuteDSL W4A4 | -0.021% | +0.063% | -0.081% | +6.227% |
| CuteDSL PER-TOKEN | +0.049% | +0.200% | +0.091% | +3.020% |
| CuteDSL MXFP4x8 | -0.009% | +0.264% | -0.003% | +5.376% |
| CuteDSL MXFP8 | -0.073% | -0.565% | -0.016% | +3.905% |
| CuteDSL W4A16 | -0.013% | -0.186% | +0.018% | +0.391% |

| Job | Backend | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | Compact | BF16 FC2 MiB (both) | Added metadata KiB |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 50.624 | 50.656 | 50.624 | 50.720 | +0.063% | False | 0.438 | 0.000 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 229.312 | 229.217 | 229.185 | 228.961 | -0.028% | False | 7.000 | 0.000 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 393.538 | 393.762 | 394.034 | 393.138 | -0.142% | True | 448.000 | 258.434 |
| ep-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 1012.708 | 998.757 | 991.413 | 1027.668 | +2.521% | True | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 51.489 | 51.407 | 51.489 | 51.408 | +0.001% | False | 0.438 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 56.817 | 56.736 | 56.721 | 56.848 | +0.184% | False | 0.438 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 57.104 | 57.072 | 57.104 | 57.088 | +0.014% | False | 0.438 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 237.489 | 237.760 | 237.825 | 237.794 | -0.064% | False | 7.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 244.673 | 244.577 | 244.305 | 244.497 | +0.059% | False | 7.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 251.073 | 250.930 | 250.818 | 251.201 | +0.105% | False | 7.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 388.578 | 387.906 | 387.313 | 388.306 | +0.215% | True | 448.000 | 258.434 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 447.267 | 446.642 | 445.489 | 446.163 | +0.145% | True | 448.000 | 258.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 532.706 | 535.811 | 563.683 | 573.092 | +0.539% | False | 448.000 | 0.000 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 703.331 | 705.971 | 706.164 | 709.796 | +0.069% | True | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1025.126 | 1027.909 | 1021.717 | 1031.205 | +0.327% | True | 1792.000 | 1032.434 |
| ep-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 1982.762 | 1987.754 | 2001.930 | 1987.738 | -0.480% | False | 1792.000 | 0.000 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP8 | 4 | 48.657 | 48.624 | 48.800 | 48.704 | -0.066% | False | 0.344 | 0.000 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 4 | 35.296 | 35.232 | 35.297 | 35.264 | +0.045% | False | 0.344 | 0.000 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP8 | 64 | 216.082 | 216.034 | 216.050 | 216.082 | +0.019% | False | 5.500 | 0.000 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 64 | 127.297 | 127.281 | 127.425 | 127.346 | -0.025% | False | 5.500 | 0.000 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP8 | 4096 | 312.450 | 314.531 | 314.466 | 312.930 | -0.575% | True | 352.000 | 353.621 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 4096 | 247.843 | 249.458 | 249.282 | 247.858 | -0.609% | True | 352.000 | 353.621 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP8 | 16384 | 823.959 | 818.327 | 847.447 | 815.303 | -1.578% | True | 1408.000 | 1413.746 |
| ep-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 16384 | 764.726 | 755.686 | 767.591 | 746.406 | -0.802% | True | 1408.000 | 1413.746 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 4 | 36.625 | 36.625 | 36.641 | 36.609 | -0.043% | False | 0.344 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 4 | 42.080 | 42.081 | 41.920 | 41.984 | +0.075% | False | 0.344 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 4 | 41.920 | 41.920 | 41.952 | 41.873 | -0.095% | False | 0.344 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 64 | 132.642 | 132.641 | 132.642 | 132.657 | +0.006% | False | 5.500 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 64 | 140.498 | 140.498 | 140.578 | 140.641 | +0.023% | False | 5.500 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 64 | 142.977 | 142.962 | 142.865 | 143.137 | +0.100% | False | 5.500 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 4096 | 216.578 | 218.913 | 218.754 | 216.610 | -1.023% | True | 352.000 | 354.996 |
| ep-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 4096 | 317.139 | 319.827 | 319.587 | 317.459 | -0.753% | True | 352.000 | 354.996 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 4096 | 392.868 | 392.196 | 393.844 | 392.132 | -0.132% | False | 352.000 | 0.000 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 16384 | 514.101 | 525.717 | 526.053 | 515.029 | -2.153% | True | 1408.000 | 1419.246 |
| ep-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 16384 | 846.376 | 857.399 | 857.847 | 847.144 | -1.267% | True | 1408.000 | 1419.246 |
| ep-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 16384 | 1492.525 | 1508.094 | 1460.125 | 1457.821 | -0.596% | False | 1408.000 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4 | 67.888 | 67.825 | 67.824 | 67.856 | +0.071% | False | 0.438 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4 | 46.432 | 46.449 | 46.496 | 46.432 | -0.087% | False | 0.438 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 64 | 219.537 | 219.713 | 219.617 | 219.313 | -0.109% | False | 7.000 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 64 | 129.249 | 129.313 | 129.217 | 129.313 | +0.012% | False | 7.000 | 0.000 |
| ep-v3-mxfp | CuteDSL MXFP8 | 4096 | 305.922 | 307.938 | 308.145 | 305.890 | -0.693% | True | 448.000 | 128.621 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 228.226 | 230.465 | 230.641 | 228.065 | -1.044% | True | 448.000 | 128.621 |
| ep-v3-mxfp | CuteDSL MXFP8 | 16384 | 709.285 | 692.708 | 719.796 | 694.916 | -0.575% | True | 1792.000 | 514.121 |
| ep-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 665.140 | 664.660 | 657.028 | 676.851 | +1.534% | True | 1792.000 | 516.121 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4 | 46.225 | 46.144 | 46.337 | 46.241 | -0.015% | False | 0.438 | 0.000 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 51.904 | 51.808 | 51.921 | 51.728 | -0.093% | False | 0.438 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4 | 51.920 | 51.952 | 52.032 | 51.985 | -0.076% | False | 0.438 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 64 | 130.913 | 130.737 | 130.913 | 130.753 | +0.006% | False | 7.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 136.609 | 136.448 | 136.592 | 136.529 | +0.036% | False | 7.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 64 | 142.577 | 142.513 | 142.657 | 142.625 | +0.011% | False | 7.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 4096 | 207.649 | 207.889 | 207.906 | 207.649 | -0.119% | True | 448.000 | 128.621 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 250.642 | 248.673 | 248.578 | 249.809 | +0.644% | True | 448.000 | 128.621 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 4096 | 284.081 | 284.146 | 284.369 | 284.081 | -0.062% | False | 448.000 | 0.000 |
| ep-v3-nvfp4 | CuteDSL W4A4 | 16384 | 491.267 | 478.467 | 478.099 | 490.099 | +2.593% | True | 1792.000 | 514.121 |
| ep-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 630.868 | 620.883 | 621.300 | 631.988 | +1.664% | True | 1792.000 | 516.121 |
| ep-v3-nvfp4 | CuteDSL W4A16 | 16384 | 1133.959 | 1148.743 | 1114.935 | 1153.927 | +1.077% | False | 1792.000 | 0.000 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 4 | 50.625 | 50.769 | 50.800 | 50.657 | -0.284% | False | 0.234 | 0.000 |
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 4 | 33.984 | 33.952 | 34.016 | 33.952 | -0.046% | False | 0.234 | 0.000 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 64 | 350.178 | 350.018 | 350.595 | 349.971 | -0.066% | False | 3.750 | 0.000 |
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 64 | 194.225 | 194.273 | 194.242 | 194.258 | -0.008% | False | 3.750 | 0.000 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 4096 | 585.732 | 586.548 | 586.484 | 585.749 | -0.132% | True | 240.000 | 97.121 |
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 4096 | 355.827 | 357.923 | 357.890 | 356.275 | -0.519% | True | 240.000 | 97.121 |
| ep-v41-flash-mxfp | CuteDSL MXFP8 | 16384 | 961.224 | 969.560 | 935.431 | 946.839 | +0.174% | True | 960.000 | 387.371 |
| ep-v41-flash-mxfp | CuteDSL MXFP4x8 | 16384 | 841.414 | 829.878 | 822.663 | 831.479 | +1.231% | True | 960.000 | 387.371 |
| ep-v41-flash-nvfp4 | CuteDSL W4A4 | 4 | 33.280 | 33.184 | 33.344 | 33.216 | -0.048% | False | 0.234 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 4 | 39.728 | 39.680 | 39.728 | 39.680 | -0.001% | False | 0.234 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL W4A16 | 4 | 39.104 | 39.168 | 39.168 | 39.136 | -0.123% | False | 0.234 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL W4A4 | 64 | 202.690 | 202.594 | 202.690 | 202.561 | -0.008% | False | 3.750 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 64 | 208.754 | 208.562 | 208.530 | 208.802 | +0.111% | False | 3.750 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL W4A16 | 64 | 213.554 | 213.682 | 213.554 | 213.522 | -0.037% | False | 3.750 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL W4A4 | 4096 | 350.755 | 349.555 | 349.875 | 350.659 | +0.284% | True | 240.000 | 97.121 |
| ep-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 4096 | 408.067 | 407.651 | 407.683 | 407.875 | +0.075% | True | 240.000 | 97.121 |
| ep-v41-flash-nvfp4 | CuteDSL W4A16 | 4096 | 447.411 | 447.684 | 445.299 | 445.427 | -0.016% | False | 240.000 | 0.000 |
| ep-v41-flash-nvfp4 | CuteDSL W4A4 | 16384 | 585.396 | 580.932 | 581.188 | 584.885 | +0.702% | True | 960.000 | 387.371 |
| ep-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 16384 | 746.726 | 741.094 | 742.086 | 748.246 | +0.795% | True | 960.000 | 387.371 |
| ep-v41-flash-nvfp4 | CuteDSL W4A16 | 16384 | 1512.844 | 1548.397 | 1544.620 | 1524.668 | -1.795% | False | 960.000 | 0.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4 | 41.424 | 41.233 | 41.264 | 41.200 | +0.154% | False | 0.438 | 0.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 64 | 242.769 | 242.561 | 242.562 | 243.009 | +0.135% | False | 7.000 | 0.000 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 4096 | 717.685 | 698.133 | 699.477 | 718.229 | +2.741% | True | 448.000 | 261.473 |
| tp-kimi-k3-mxfp | CuteDSL MXFP4x8 | 16384 | 2069.148 | 1940.172 | 1938.045 | 2073.166 | +6.810% | True | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4 | 42.464 | 42.480 | 42.672 | 42.608 | -0.094% | False | 0.438 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4 | 45.616 | 45.600 | 45.600 | 45.697 | +0.123% | False | 0.438 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4 | 50.464 | 50.352 | 50.401 | 50.496 | +0.205% | False | 0.438 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 64 | 249.425 | 249.058 | 249.458 | 249.217 | +0.025% | False | 7.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 64 | 257.873 | 257.649 | 258.082 | 258.034 | +0.034% | False | 7.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 64 | 282.578 | 282.418 | 282.722 | 282.706 | +0.025% | False | 7.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 4096 | 689.636 | 663.812 | 664.724 | 690.517 | +3.885% | True | 448.000 | 261.473 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 859.301 | 861.046 | 861.477 | 856.166 | -0.410% | True | 448.000 | 261.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 4096 | 835.365 | 830.005 | 830.390 | 830.646 | +0.338% | False | 448.000 | 0.000 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A4 | 16384 | 1776.188 | 1646.651 | 1647.692 | 1776.733 | +7.849% | True | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 2424.081 | 2402.385 | 2397.313 | 2422.977 | +0.987% | True | 1792.000 | 1035.473 |
| tp-kimi-k3-nvfp4 | CuteDSL W4A16 | 16384 | 2907.860 | 2914.581 | 2902.901 | 2903.861 | -0.099% | False | 1792.000 | 0.000 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 4 | 51.120 | 51.264 | 51.136 | 51.200 | -0.079% | False | 0.344 | 0.000 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 4 | 36.529 | 36.608 | 36.576 | 36.560 | -0.130% | False | 0.344 | 0.000 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 64 | 218.833 | 218.946 | 218.801 | 218.049 | -0.198% | False | 5.500 | 0.000 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 64 | 134.881 | 135.056 | 134.865 | 135.281 | +0.089% | False | 5.500 | 0.000 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 4096 | 517.539 | 515.603 | 516.355 | 517.347 | +0.284% | True | 352.000 | 355.367 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 4096 | 466.083 | 454.819 | 454.755 | 466.018 | +2.477% | True | 352.000 | 355.367 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP8 | 16384 | 1626.954 | 1625.962 | 1613.577 | 1625.274 | +0.392% | True | 1408.000 | 1415.492 |
| tp-nemo3-ultra-mxfp | CuteDSL MXFP4x8 | 16384 | 1564.714 | 1535.929 | 1546.105 | 1561.961 | +1.449% | True | 1408.000 | 1415.492 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 4 | 38.240 | 38.368 | 38.209 | 38.240 | -0.126% | False | 0.344 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 4 | 42.897 | 42.912 | 42.880 | 42.928 | +0.038% | False | 0.344 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 4 | 47.745 | 47.728 | 47.712 | 47.648 | -0.050% | False | 0.344 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 64 | 137.441 | 137.601 | 137.441 | 137.393 | -0.076% | False | 5.500 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 64 | 147.809 | 147.585 | 147.696 | 147.969 | +0.168% | False | 5.500 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 64 | 154.481 | 154.433 | 154.401 | 154.306 | -0.015% | False | 5.500 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 4096 | 441.314 | 425.907 | 425.842 | 441.283 | +3.622% | True | 352.000 | 355.367 |
| tp-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 4096 | 674.389 | 658.468 | 658.851 | 673.412 | +2.314% | True | 352.000 | 356.734 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 4096 | 616.644 | 616.292 | 618.628 | 630.404 | +0.976% | False | 352.000 | 0.000 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A4 | 16384 | 1402.153 | 1321.688 | 1321.320 | 1403.289 | +6.146% | True | 1408.000 | 1415.492 |
| tp-nemo3-ultra-nvfp4 | CuteDSL PER-TOKEN | 16384 | 2131.981 | 2034.269 | 2034.892 | 2129.532 | +4.727% | True | 1408.000 | 1415.492 |
| tp-nemo3-ultra-nvfp4 | CuteDSL W4A16 | 16384 | 2319.151 | 2317.999 | 2293.198 | 2289.711 | -0.051% | False | 1408.000 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4 | 46.752 | 46.577 | 46.785 | 46.768 | +0.170% | False | 0.438 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4 | 35.392 | 35.408 | 35.456 | 35.360 | -0.158% | False | 0.438 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 64 | 227.602 | 227.489 | 227.393 | 227.474 | +0.042% | False | 7.000 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 64 | 144.289 | 144.369 | 144.417 | 144.193 | -0.105% | False | 7.000 | 0.000 |
| tp-v3-mxfp | CuteDSL MXFP8 | 4096 | 634.564 | 595.509 | 595.349 | 634.773 | +6.590% | True | 448.000 | 129.992 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 4096 | 556.515 | 509.267 | 508.788 | 556.884 | +9.365% | True | 448.000 | 129.992 |
| tp-v3-mxfp | CuteDSL MXFP8 | 16384 | 1787.324 | 1646.780 | 1644.027 | 1787.085 | +8.618% | True | 1792.000 | 514.996 |
| tp-v3-mxfp | CuteDSL MXFP4x8 | 16384 | 1733.932 | 1580.954 | 1579.643 | 1734.365 | +9.736% | True | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4 | 36.417 | 36.592 | 36.705 | 36.704 | -0.241% | False | 0.438 | 0.000 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4 | 40.464 | 40.257 | 40.448 | 40.304 | +0.079% | False | 0.438 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4 | 39.984 | 40.000 | 40.032 | 40.000 | -0.061% | False | 0.438 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 64 | 143.456 | 143.601 | 143.297 | 143.361 | -0.028% | False | 7.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 64 | 151.697 | 151.778 | 151.521 | 151.889 | +0.095% | False | 7.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 64 | 154.577 | 154.274 | 154.257 | 154.401 | +0.145% | False | 7.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 4096 | 524.899 | 491.651 | 491.204 | 524.115 | +6.731% | True | 448.000 | 129.992 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 4096 | 615.524 | 616.228 | 615.780 | 615.668 | -0.066% | True | 448.000 | 129.992 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 4096 | 644.084 | 643.956 | 643.988 | 644.340 | +0.037% | False | 448.000 | 0.000 |
| tp-v3-nvfp4 | CuteDSL W4A4 | 16384 | 1541.675 | 1362.362 | 1362.522 | 1539.867 | +13.089% | True | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1885.357 | 1710.988 | 1712.044 | 1886.014 | +10.176% | True | 1792.000 | 514.996 |
| tp-v3-nvfp4 | CuteDSL W4A16 | 16384 | 2241.328 | 2227.360 | 2228.816 | 2235.392 | +0.461% | False | 1792.000 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A4 | 4 | 35.632 | 35.649 | 35.584 | 35.600 | -0.001% | False | 0.234 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 4 | 40.368 | 40.288 | 40.368 | 40.352 | +0.079% | False | 0.234 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A16 | 4 | 41.729 | 41.792 | 41.824 | 41.792 | -0.114% | False | 0.234 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A4 | 64 | 205.250 | 205.553 | 205.409 | 205.266 | -0.109% | False | 3.750 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 64 | 213.089 | 213.169 | 212.977 | 213.522 | +0.109% | False | 3.750 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A16 | 64 | 233.730 | 233.553 | 233.729 | 233.586 | +0.007% | False | 3.750 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A4 | 4096 | 490.660 | 490.722 | 490.275 | 490.611 | +0.028% | False | 240.000 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 4096 | 586.916 | 587.316 | 586.740 | 587.317 | +0.015% | False | 240.000 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A16 | 4096 | 627.908 | 631.332 | 627.509 | 636.804 | +0.464% | False | 240.000 | 0.000 |
| tp-v41-flash-nvfp4 | CuteDSL W4A4 | 16384 | 1139.159 | 1045.624 | 1044.408 | 1138.424 | +8.974% | True | 960.000 | 386.992 |
| tp-v41-flash-nvfp4 | CuteDSL PER-TOKEN | 16384 | 1439.929 | 1347.194 | 1346.234 | 1439.659 | +6.912% | True | 960.000 | 386.992 |
| tp-v41-flash-nvfp4 | CuteDSL W4A16 | 16384 | 2153.566 | 2111.903 | 2152.126 | 2153.247 | +1.008% | False | 960.000 | 0.000 |

## Evidence

- `perf-analysis.json`, `perf-cells.csv`, `audit_perf.py`: complete raw pass medians and independent source/cache/CUPTI checks.
- `perf-evidence/`: archive SHA256 `6a1982e26a90116284b3aacf1868acc2617b79c4aefe746908caab00484a9cdf`.
- `gate-evidence/`, `codegen-analysis.json`: source-bound exact metadata/output and native codegen checks.
- `scheduler-review/`: independent source/planner safety review.

This is an optimization screen, not a replacement of the published full-token benchmark matrix. Candidate sanitizers and final full benchmarks remain deferred. Historical R2 diagnostic reports deliberately retain their labeled arithmetic-mean calculation.
