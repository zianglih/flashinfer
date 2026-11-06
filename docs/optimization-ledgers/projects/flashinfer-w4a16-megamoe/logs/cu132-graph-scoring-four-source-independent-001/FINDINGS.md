# Graph scoring: complete four-source findings

- All four strict analyzers pass in separate CPU processes:208 raw values,832 split records,832 compiled records,416 returned rank choices and52 full16-candidate rankings. The new graph sweep contributes52/208/208/104/13. Its208 selected objects all attest REG128,512threads,two decode groups,pool65536,local0. Ten cache capacities retain the correct last winner, while all13 actual row choices are preserved.
- The graph source differs from28a only at autotune.py. All104 fixed-control config/compiled/gate records match exactly; separate fixed-process Mega movement spans−4.01%..+4.80%, and paired split movement−13.17%..+13.51%. This is context, not a scorer-induced kernel change or a correction factor for auto.
- Graph auto is lower at11/13 points versus its fixed arm. T1 is4.35% slower andT4096 is0.62% slower. T2048 andT4096 use exactly the same observed config/compiled/gate as fixed on every rank; their−1.75%/+0.62% changes cannot be credited to a changed tactic.
- Versus complete host-scored28a auto, graph auto improves8/13 rows and changes10 choices. T8/T16/T64 improve7.40%/6.08%/7.84%, useful selection evidence. It regressesT1 by14.85% andT2 by11.48%; T256 is1.73% slower with the same selected configuration, andT4096 is0.71% slower with the same selected configuration. Small differences and repeated same configurations need context, not a new-best label.
- Versus base512 e2d auto, graph auto improves9/13, butT1 is22.97% slower. Versus freshC1 auto it improves6/13, whileT1 is8.11% slower andT4096 is7.03% slower. At4096, C1 selected the same M256/N128/C2/F4 geometry with reused-dispatch return; graph selects epilogue return on the later512-thread/static-FC2 implementation. This is not an isolated scorer or return-mode comparison across those sources.
- The complete graph table beats its own paired split at12/13 shapes, including all seven shapes above32. T64 is only1.0102x andT512 only1.0060x; split independently retunes and those narrow margins do not establish repeatable nonregression. T1 remains below split at0.8449x.
- All13 graph selections use epi_warps. Most printed first/second score gaps are below1%; T1 andT8 are equal at the displayed0.1us precision, which does not prove exact ties. T4096 has a1.82% printed graph-score gap. Host wall-clock scores and hot graph GPU-event scores remain distinct from unchanged cold-L2 CUPTI final latency; no score ratio is interpreted as a kernel speedup.
- Continue graph scoring as a meaningful general trial baseline, as directed by the parent. These observations do not justify an unqualified new overall-best claim or replacing the PR table. Preserve the full table; no minimum across rows/sources or workload weighting is invented. New CUDA13.0 recovery targets0d, while CUDA13.2 first32 predecode CPU capture and the separate input trial continue independently.

## Complete graph fixed andauto table

EP8, H7168/I2048/E256/top8, global tokens; nvcr.io/nvidia/pytorch:26.05-py3 on fresh recovery0908b/hu-pdx-88. CUDA13.2 runtime, DSL4.7.1/native13.3, direct BF16 decoder. Original100-iteration cold-L2 graph CUPTI full-forward GPU span, median of per-iteration rank maxima. Same source0d795 for both fixed andauto.

| T | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Auto split/Mega | Auto vs fixed | Actual auto choice |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.085153 | 0.091520 | 0.080688 | 0.095504 | 0.8449x | +4.35% | M128/N64, C1, F8, epi |
| 2 | 0.101377 | 0.115585 | 0.116752 | 0.114497 | 1.0197x | -0.94% | M128/N64, C1, F8, epi |
| 4 | 0.144385 | 0.136800 | 0.138161 | 0.126609 | 1.0912x | -7.45% | M128/N64, C1, F4, epi |
| 8 | 0.163041 | 0.152129 | 0.160992 | 0.147153 | 1.0940x | -3.27% | M256/N64, C2, F8, epi |
| 16 | 0.166977 | 0.178113 | 0.177841 | 0.156673 | 1.1351x | -12.04% | M256/N64, C2, F4, epi |
| 32 | 0.205441 | 0.203266 | 0.200866 | 0.193250 | 1.0394x | -4.93% | M256/N64, C2, F8, epi |
| 64 | 0.209682 | 0.232882 | 0.220977 | 0.218738 | 1.0102x | -6.07% | M256/N64, C2, F8, epi |
| 128 | 0.239042 | 0.237410 | 0.231955 | 0.225282 | 1.0296x | -5.11% | M256/N64, C2, F4, epi |
| 256 | 0.245042 | 0.246849 | 0.244785 | 0.229217 | 1.0679x | -7.14% | M256/N64, C2, F8, epi |
| 512 | 0.239554 | 0.250626 | 0.237201 | 0.235794 | 1.0060x | -5.92% | M256/N64, C2, F4, epi |
| 1024 | 0.260274 | 0.257250 | 0.259714 | 0.250225 | 1.0379x | -2.73% | M256/N64, C2, F4, epi |
| 2048 | 0.351874 | 0.344578 | 0.348210 | 0.338531 | 1.0286x | -1.75% | M256/N128, C2, F4, epi |
| 4096 | 0.557699 | 0.527445 | 0.549221 | 0.530692 | 1.0349x | +0.62% | M256/N128, C2, F4, epi |

Every tactic keeps K256,group512,atomic scheduling,epi_flag_batch(2,4),two decode groups andno in-kernel FC2 reducer. C denotes cluster count; M128 uses one-CTA MMA instructions andM256 uses two-CTA instructions. Full per-rank dictionaries and resources are retained in comparison.json.

## Complete auto comparisons

| T | Graph vs host28a | Graph vs e2d88 | Graph vs freshC1 | Same graph/host choice | Graph fixed/host fixed change |
| ---: | ---: | ---: | ---: | --- | ---: |
| 1 | +14.85% | +22.97% | +8.11% | False | -0.44% |
| 2 | +11.48% | -3.32% | -3.23% | False | -1.39% |
| 4 | -2.45% | -6.07% | -1.87% | False | +4.80% |
| 8 | -7.40% | -7.79% | -6.55% | False | +0.24% |
| 16 | -6.08% | -1.86% | -5.11% | False | +2.12% |
| 32 | -1.81% | -4.28% | +2.26% | False | +1.86% |
| 64 | -7.84% | -5.48% | -9.15% | False | +1.16% |
| 128 | -0.09% | -4.43% | +2.36% | False | -1.20% |
| 256 | +1.73% | +1.88% | +0.57% | True | +3.59% |
| 512 | -0.27% | +0.80% | +3.19% | False | +1.70% |
| 1024 | -1.39% | -0.79% | -0.69% | True | -4.01% |
| 2048 | +0.16% | -0.93% | +0.80% | False | +0.74% |
| 4096 | +0.71% | +0.09% | +7.03% | True | -0.85% |

The raw208-value CSV, all832 split/compiled records,416 actual selected rank dictionaries,52 online rankings and original strict source/native/cache evidence remain in this folder. Before-only native-cache inventories do not attest later cache immutability. Saved preflight/compiler gates do not newly capture per-run loaded-library maps. No tensor-byte rerun or statistical confidence interval is claimed.
