# K3 EP8 incremental performance

Speedup is the saved BEFORE median divided by the candidate median; values above 1 are faster. Every column reuses the same BEFORE. Native and both combined columns use AUTO; fixed scheduler/N32 screens are independent. No samples are pooled.

| Tokens | BEFORE (µs) | Native SiTU | + Scheduler prefix | N32 screen | M256 AUTO (12) | Expanded AUTO (24) | Final measured tactic |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 84.1930 | 0.9908× | 1.0310× | 1.0057× | 1.0533× | 0.9957× | `M128/N32/G1024/epi` |
| 2 | 97.7445 | 1.0411× | 0.9980× | 1.0011× | 1.0377× | 1.0358× | `M128/N32/G512/epi` |
| 4 | 108.1610 | 0.9508× | 1.0058× | 1.0378× | 0.9643× | 1.0236× | `M128/N32/G1024/epi` |
| 8 | 137.8255 | 1.0081× | 1.0267× | 1.0266× | 1.0110× | 1.0024× | `M128/N32/G1024/epi` |
| 16 | 160.0815 | 1.0111× | 1.0474× | 1.0356× | 1.0488× | 1.1067× | `M256/N32/G1024/epi` |
| 32 | 238.0665 | 1.0111× | 1.0239× | 1.0610× | 1.0677× | 1.0569× | `M256/N32/G1024/epi` |
| 64 | 321.8110 | 0.9960× | 0.9988× | 1.0326× | 1.0276× | 1.0300× | `M256/N32/G1024/epi` |
| 128 | 377.0445 | 1.0024× | 1.0027× | 1.0307× | 1.0211× | 1.0260× | `M256/N32/G512/epi` |
| 256 | 400.7560 | 0.9998× | 1.0020× | 1.0211× | 1.0124× | 1.0155× | `M256/N32/G1024/epi` |
| 512 | 415.9410 | 1.0098× | 1.0101× | 1.0355× | 1.0399× | 1.0446× | `M256/N32/G1024/epi` |
| 4096 | 593.6060 | 0.9870× | 1.0231× | 0.5478× | 0.9970× | 1.0121× | `M256/N128/G1024/epi` |
| 8192 | 1069.0370 | 0.9837× | 1.0131× | 0.5453× | 0.9851× | 0.9941× | `M256/N128/G512/epi` |
| 16384 | 2089.7810 | 1.0107× | 1.0168× | 0.5547× | 1.0085× | 1.0148× | `M256/N128/G1024/dispatch` |

Tactic legend: M/N are the feature/token tile dimensions; K=256 and cluster=(2,1,1) throughout. G is group size; epi=`epi_warps`, dispatch=`reuse_dispatch_warps`. M128 uses one-CTA MMA and M256 uses two-CTA MMA. The last column records the measured 24-tactic sweep winner; each remains in the final 16-tactic catalog.
Only T1/T2 are excluded from retention. All prefill points remain included. The expanded sweep selected M128 only at N32 for T1/T2/T4/T8; all larger decode points used M256/N32 and prefill used M256/N128.

| M128-selected tokens | M256-only µs | Expanded µs | Saved µs | Latency reduction |
|---:|---:|---:|---:|---:|
| 1 | 79.9360 | 84.5605 | -4.6245 | -5.785% |
| 2 | 94.1930 | 94.3690 | -0.1760 | -0.187% |
| 4 | 112.1610 | 105.6650 | +6.4960 | +5.792% |
| 8 | 136.3215 | 137.4890 | -1.1675 | -0.856% |

Retain the user-requested four-tile list: `((128,32,256), (256,32,256), (256,64,256), (256,128,256))`. It has 16 default tactics, preserves all 13 measured winners, and removes the unused M128/N64 and M128/N128 candidates. The 16-tactic catalog itself has not been benchmarked; the measured expanded column remains the 24-tactic sweep.

M128 is a selective small-shape option: T4 improves by 5.792% relative to the M256-only capture, while T8 is 0.856% slower. Hot-input selection scores favor M128 by only 1.07%/0.17% at T4/T8. Those selection timings are separate from final cold-L2 CUPTI medians. Improved points still selecting M256 are not evidence of an M128 benefit.

New M128/N32 exact gate passed four logical EP2 cases (8 rank-local passes), with zero failures/skips and unchanged zero tolerance. Earlier eight-case M256 combined gate passed separately. All source changes retain the established two decoder warp groups.

Full medians/raw samples/provenance: `evidence/progressive-expanded-auto-v1.{md,json}`. Selection diagnostics: `evidence/expanded-auto-v1-selection-scoreboard.{md,json}`. Winner subset proof: `evidence/m128-n32-narrow-membership.json`.
