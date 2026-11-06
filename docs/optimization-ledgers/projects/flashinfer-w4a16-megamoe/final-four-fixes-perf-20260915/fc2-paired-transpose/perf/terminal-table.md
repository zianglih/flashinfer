| Tokens | a48 B3 ms | 71f94 C3 ms | B3/C3 | Same tactic |
|---:|---:|---:|---:|:---:|
| 1 | 0.07945700 | 0.08737700 | 0.909358 | True |
| 2 | 0.10396950 | 0.09656150 | 1.076718 | True |
| 4 | 0.12617750 | 0.12473700 | 1.011548 | True |
| 8 | 0.14438500 | 0.14137750 | 1.021273 | True |
| 16 | 0.15772900 | 0.14726500 | 1.071056 | True |
| 32 | 0.18310550 | 0.18256200 | 1.002977 | True |
| 64 | 0.20390600 | 0.20289800 | 1.004968 | True |
| 128 | 0.21297800 | 0.20886600 | 1.019687 | True |
| 256 | 0.21356950 | 0.21332950 | 1.001125 | True |
| 512 | 0.21878600 | 0.21619400 | 1.011989 | True |
| 1024 | 0.23224250 | 0.23888200 | 0.972206 | True |
| 2048 | 0.31369950 | 0.31713900 | 0.989155 | True |
| 4096 | 0.47000500 | 0.47304450 | 0.993575 | True |
| 8192 | 0.74405550 | 0.75240600 | 0.988902 | True |

8–8192 geometric B3/C3: 1.0067007345187864.
All 14 rows reported; only 1/2/4 excluded from aggregate. Ratio greater than 1 means faster candidate.
One candidate C3 sweep versus one preserved same-node fresh a48 B3 baseline. Full medians, samples and tactic changes remain visible; no causal or statistical-certainty claim from this single comparison.

| Tokens | B3 tactic | C3 tactic |
|---:|---|---|
| 1 | 256x64x256/epi | 256x64x256/epi |
| 2 | 256x64x256/epi | 256x64x256/epi |
| 4 | 256x64x256/epi | 256x64x256/epi |
| 8 | 256x64x256/epi | 256x64x256/epi |
| 16 | 256x64x256/epi | 256x64x256/epi |
| 32 | 256x64x256/epi | 256x64x256/epi |
| 64 | 256x64x256/epi | 256x64x256/epi |
| 128 | 256x64x256/epi | 256x64x256/epi |
| 256 | 256x64x256/epi | 256x64x256/epi |
| 512 | 256x64x256/epi | 256x64x256/epi |
| 1024 | 256x64x256/epi | 256x64x256/epi |
| 2048 | 256x128x256/dispatch | 256x128x256/dispatch |
| 4096 | 256x128x256/dispatch | 256x128x256/dispatch |
| 8192 | 256x128x256/dispatch | 256x128x256/dispatch |
