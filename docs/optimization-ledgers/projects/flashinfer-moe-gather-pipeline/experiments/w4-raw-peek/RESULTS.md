# W4 raw TRY → TEST: rejected

Candidate `0871b67f` on retained `2b8eb9d8` replaces only the two existing raw readiness queries. It adds no new helper or state, but exposes index/phase at the call sites and adds three native control instructions in multistage split kernels.

| Retention group | Cells | GM speedup | Negative cells |
|---|---:|---:|---:|
| all | 88 | +0.08345% | 43 |
| decode | 40 | -0.06722% | 23 |
| middle | 24 | +0.06710% | 12 |
| prefill | 24 | +0.35146% | 8 |

All 104 cells and 41,600 CUPTI samples are preserved; tokens 1/2 remain in raw tables but are excluded from the 88-cell retention metric. This is a neutral result, not evidence of a general speedup.

The tightest material loss is V41F EP T8: 50.3917 → 51.0160 µs (−1.2237%), control/candidate spreads 0.285%/0.157%, normal clocks. Its FC1 span increases in both candidate phases. K3 TP T8 loses 0.9925%; most of that observed E2E delta is in the unchanged routing span, so it is not all attributable to the query. Neither row is excluded.

The motivating V41F TP T4096 case improves 0.52475% with tight 0.065%/0.062% spreads: FC1 duration drops about 3.84 µs while FC2 duration rises about 2.03 µs. This localized improvement does not establish broad benefit.

Prefill GM is +0.35146%, but repeat spreads reach 8.39%/3.85% and the complete run contains 93 clock-exception quartiles out of 1,664, with zero missing. These observations remain attached to every original row; no trimming or substitute repeats were performed.

All 208 actual FC1/FC2 configuration/resource pairs match across phases; 448 loaded kernel records have zero local bytes. Ten recorded defaults produce 80 source/library/resource joins. Split/Mega exact/native qualification passed 16 calls / 20 pairs with all resources equal and inverse-identical PTX; that correctness result does not imply performance benefit.

Decision: reject. No rescue repeat, shape policy, or distributed GLM5 timing. Main 2b8 and published results remain unchanged. All eight GPUs passed release/cache postflight.

[All 104 phase medians](../../evidence/w4-raw-peek-screen/1793387093939213000/report/table.md) · [88-cell matrix](../../evidence/w4-raw-peek-screen/1793387093939213000/report/matrix.md) · [All clocks](../../evidence/w4-raw-peek-screen/1793387093939213000/report/clock-quartiles.json) · [Independent raw replay](../../audits/w4-raw-peek-data-root.json)
