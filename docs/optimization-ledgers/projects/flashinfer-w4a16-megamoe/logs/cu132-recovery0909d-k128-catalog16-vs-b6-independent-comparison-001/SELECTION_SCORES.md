# B6 versus initial16 K128/K256 selection scores

Secondary hot-graph GPU-event selection scores, MAX of per-rank medians, printed to0.1us; not primary cold-L2 CUPTI medians.

| Tokens | Initial K256 us | Initial K128 us | Initial gap | B6 K256 us | B6 K128 us | B6 gap | Gap change pp | Matched B6 K128 wins / ties (of8) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 66.6 | 68.8 | +3.303% | 66.7 | 70.1 | +5.097% | +1.794 | 0 / 0 |
| 2 | 85.0 | 91.3 | +7.412% | 83.1 | 90.9 | +9.386% | +1.975 | 0 / 0 |
| 4 | 94.9 | 103.4 | +8.957% | 94.1 | 103.4 | +9.883% | +0.926 | 0 / 0 |
| 8 | 111.7 | 125.9 | +12.713% | 112.6 | 126.2 | +12.078% | -0.634 | 0 / 0 |
| 16 | 126.0 | 144.6 | +14.762% | 126.0 | 145.0 | +15.079% | +0.317 | 0 / 0 |
| 32 | 152.6 | 178.9 | +17.235% | 152.7 | 175.4 | +14.866% | -2.369 | 0 / 0 |
| 64 | 175.8 | 210.0 | +19.454% | 175.4 | 201.8 | +15.051% | -4.403 | 0 / 0 |
| 128 | 180.0 | 214.3 | +19.056% | 181.2 | 208.5 | +15.066% | -3.989 | 0 / 0 |
| 256 | 181.4 | 218.2 | +20.287% | 182.7 | 211.5 | +15.764% | -4.523 | 0 / 0 |
| 512 | 188.0 | 225.9 | +20.160% | 187.6 | 216.3 | +15.299% | -4.861 | 0 / 0 |
| 1024 | 209.9 | 246.9 | +17.627% | 209.9 | 236.7 | +12.768% | -4.859 | 0 / 0 |
| 2048 | 298.0 | 326.6 | +9.597% | 295.7 | 308.4 | +4.295% | -5.302 | 0 / 0 |
| 4096 | 457.8 | 493.6 | +7.820% | 454.3 | 466.0 | +2.575% | -5.245 | 0 / 0 |

B6 has0 K128 winners. Across104 exact K-only B6 pairs, K128 has0 lower printed scores and0 printed ties. The104 matched before/after K128 and K256 score changes, all best-subset choices and complete source pins remain in [selection-scores.json](selection-scores.json).

Complete13×16 original printed scores; exact pair matching removes only tileK from the full dictionaries. Best-subset comparisons can choose different N/flags/returns. No original per-candidate replay arrays survive; printed ties cannot establish exact equality. Initial and B6 scores come from separate complete runs. Gap changes do not adjust primary latency or establish a fixed-tactic causal effect. No primary-latency prediction, row substitution or validator rerun.

[Primary whole-run comparisons](README.md)
