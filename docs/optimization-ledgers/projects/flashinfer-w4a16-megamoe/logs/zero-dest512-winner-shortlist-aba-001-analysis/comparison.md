# Same-source final512 fixed-tactic A/B/A

A1/A2 use the prior C1 auto choice; B uses the fresh512 auto choice, all on identical final512 source. Original primary100CUPTI/graph/coldL2 timing is unchanged. Same-shape split tuner caches persist inside each process; actual selections are retained. This is a tactic comparison, not a640-versus512 implementation A/B.

| Global tokens | Arm | Split ms | Mega ms | Actual fixed Mega choice |
| ---: | --- | ---: | ---: | --- |
| 32 | a1 | 0.200194 | 0.193265 | M256/N64,C2,F8,epi_warps |
| 32 | b | 0.201521 | 0.200241 | M128/N64,C2,F4,reuse_dispatch_warps |
| 32 | a2 | 0.201904 | 0.194114 | M256/N64,C2,F8,epi_warps |
| 128 | a1 | 0.222754 | 0.221409 | M256/N64,C2,F4,epi_warps |
| 128 | b | 0.234322 | 0.235409 | M256/N64,C2,F4,reuse_dispatch_warps |
| 128 | a2 | 0.234833 | 0.221617 | M256/N64,C2,F4,epi_warps |
| 4096 | a1 | 0.553027 | 0.542947 | M256/N128,C2,F4,reuse_dispatch_warps |
| 4096 | b | 0.543188 | 0.523764 | M256/N128,C2,F4,epi_warps |
| 4096 | a2 | 0.542404 | 0.541827 | M256/N128,C2,F4,reuse_dispatch_warps |

| Global tokens | B/A1 Mega change | B/A2 Mega change | A2/A1 Mega change | A2/A1 split change | Changed split ranks A1→B / A1→A2 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | +3.61% | +3.16% | +0.44% | +0.85% | 0 / 0 |
| 128 | +6.32% | +6.22% | +0.09% | +5.42% | 0 / 0 |
| 4096 | -3.53% | -3.33% | -0.21% | -1.92% | 0 / 0 |

All18 raw values,72 actual split selections and72 compiled rank/visit/resource records were independently reconstructed; complete source before/after, exact requested/resolved dictionaries, interpreter/compiler/decoder and actual REG128/512threads/two-group gates pass. Preserve these observations separately from complete full13 tables. No row minima, profiler timings or failed-arm substitutes are used.
