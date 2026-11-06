# First-hint reuse: bounded timing screen

All20 frozen phases pass source, native winner, route identity and100-sample CUPTI checks (2,000 samples). No AUTO search or new tactic was used. Speedup is geometric-mean control/candidate minus one.

| Model / backend | Tokens | C0 us | A1 us | A2 us | C3 us | Speedup | C drift | A drift |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| nemo3-ultra / CuteDSL MXFP4x8 | 4 | 39.3275 | 39.2000 | 39.2160 | 39.3600 | +0.346% | +0.083% | +0.041% |
| v3 / CuteDSL W4A4 | 4 | 47.1845 | 47.0400 | 46.9915 | 47.1205 | +0.291% | -0.136% | -0.103% |
| kimi-k3 / CuteDSL MXFP4x8 | 64 | 231.4095 | 231.3450 | 231.2810 | 231.3620 | +0.031% | -0.021% | -0.028% |
| nemo3-ultra / CuteDSL W4A4 | 4096 | 234.9775 | 235.7610 | 234.8810 | 234.8495 | -0.173% | -0.054% | -0.373% |
| nemo3-ultra / CuteDSL W4A4 | 16384 | 522.5310 | 522.5300 | 522.4020 | 522.8505 | +0.043% | +0.061% | -0.024% |

The two four-token cases show small consistent gains. K3 T64 and N3U T16384 are approximately neutral. N3U T4096 is −0.173% across the bracket but its candidate repeat shifts0.373%; it is inconclusive rather than a demonstrated sustained regression. A broader existing-tactic screen and reversed T4096 repeat would resolve retention. The source remains uncommitted and no PR numbers are replaced by these diagnostic cells.
