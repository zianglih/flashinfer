# Full13 raw-summary table

| Global tokens | Baseline median us | Candidate median us | Baseline/candidate | Baseline sample0 ms | Candidate sample0 ms |
|---:|---:|---:|---:|---:|---:|
| 1 | 71.105000 | 74.065000 | 0.960035 | 41.063923 | 56.300408 |
| 2 | 81.232500 | 90.128500 | 0.901296 | 36.692615 | 74.727444 |
| 4 | 95.473000 | 100.817000 | 0.946993 | 27.236236 | 26.890335 |
| 8 | 112.561500 | 110.960500 | 1.014429 | 22.803018 | 25.814731 |
| 16 | 128.545000 | 128.897000 | 0.997269 | 23.120913 | 83.503262 |
| 32 | 146.177000 | 148.688500 | 0.983109 | 32.887114 | 31.431644 |
| 64 | 165.873000 | 161.793500 | 1.025214 | 43.731900 | 41.637697 |
| 128 | 162.833500 | 171.649500 | 0.948640 | 22.356326 | 45.497813 |
| 256 | 166.514000 | 165.537500 | 1.005899 | 12.017075 | 54.522839 |
| 512 | 171.889000 | 169.889500 | 1.011769 | 62.926210 | 21.287768 |
| 4096 | 397.060000 | 401.427000 | 0.989121 | 103.928961 | 29.630227 |
| 8192 | 657.526000 | 659.895000 | 0.996410 | 39.996096 | 23.022847 |
| 16384 | 1241.288000 | 1242.922000 | 0.998685 | 35.030599 | 62.920035 |

All 100 samples per arm/point are retained in the exact [baseline raw records](runs/baseline-full13/raw-records.json) and [candidate raw records](runs/candidate3r-full13/raw-records.json). Sample 0 is shown explicitly and remains in every median. The full selected tactics are in [comparison.json](comparison.json). Ratios above 1 favor candidate; no significance claim is made.
