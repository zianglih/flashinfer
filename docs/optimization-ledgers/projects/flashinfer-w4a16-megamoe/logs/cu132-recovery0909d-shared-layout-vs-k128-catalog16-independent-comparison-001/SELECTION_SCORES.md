# K128 versus K256 selection scores

Secondary hot-graph GPU-event selection scores, MAX of per-rank medians, printed to0.1us; not primary cold-L2 CUPTI medians.

| Tokens | Best K256 us | Best K128 us | K128 gap us | Gap | Best K256 tactics | Best K128 tactics | Matched K128 wins / ties (of8) |
|---:|---:|---:|---:|---:|:---|:---|---:|
| 1 | 66.6 | 68.8 | +2.2 | +3.303% | N128/F4/epi, N64/F8/epi | N64/F4/epi | 0 / 0 |
| 2 | 85.0 | 91.3 | +6.3 | +7.412% | N64/F4/epi | N64/F4/epi | 0 / 0 |
| 4 | 94.9 | 103.4 | +8.5 | +8.957% | N64/F8/epi | N64/F8/epi | 0 / 0 |
| 8 | 111.7 | 125.9 | +14.2 | +12.713% | N64/F4/epi, N64/F8/epi | N64/F8/epi | 0 / 0 |
| 16 | 126.0 | 144.6 | +18.6 | +14.762% | N64/F4/epi | N64/F4/epi | 0 / 0 |
| 32 | 152.6 | 178.9 | +26.3 | +17.235% | N64/F8/epi | N64/F8/epi | 0 / 0 |
| 64 | 175.8 | 210.0 | +34.2 | +19.454% | N64/F8/epi | N64/F4/epi, N64/F8/epi | 0 / 0 |
| 128 | 180.0 | 214.3 | +34.3 | +19.056% | N64/F4/epi | N64/F8/epi | 0 / 0 |
| 256 | 181.4 | 218.2 | +36.8 | +20.287% | N64/F4/epi | N64/F8/epi | 0 / 0 |
| 512 | 188.0 | 225.9 | +37.9 | +20.160% | N64/F4/epi | N64/F4/epi | 0 / 0 |
| 1024 | 209.9 | 246.9 | +37.0 | +17.627% | N64/F8/epi | N64/F8/epi | 0 / 0 |
| 2048 | 298.0 | 326.6 | +28.6 | +9.597% | N128/F4/reuse | N128/F4/epi | 0 / 0 |
| 4096 | 457.8 | 493.6 | +35.8 | +7.820% | N128/F4/reuse | N128/F4/reuse | 0 / 0 |

All13 winners selected K256. Across104 exact K-only pairs, K128 has0 lower printed scores and0 printed ties. All dictionary pairs and exact saved-source pins are retained in [selection-scores.json](selection-scores.json).

Complete13×16 original printed scores; exact pair matching removes only tileK from the full dictionaries. Best-subset comparisons can choose different N/flags/returns. No original per-candidate replay arrays survive; printed ties cannot establish exact equality. No primary-latency prediction, row substitution or validator rerun.

[Primary whole-run comparison](README.md)
