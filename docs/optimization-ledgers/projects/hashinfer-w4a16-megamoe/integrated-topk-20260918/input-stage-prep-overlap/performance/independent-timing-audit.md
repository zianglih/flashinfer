# Fresh selected7dc A1 → prep772 B1: independent audit

Same precomputed-routing public full forward, with staging and finalization integrated in both arms. Routing selection excluded; candidate changes staging-role and preparation overlap.

All 2,800 samples retained; 112 cross-arm rank/token outputs are finite BF16-bit exact.

| Tokens | Selected7dc µs (MAD) | Prep772 µs (MAD) | 7dc/772 | A1 Q1→Q4 µs | B1 Q1→Q4 µs | Same tactic |
|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 64.128 (0.928) | 66.128 (0.881) | 0.969756 | 64.128→64.225 | 65.920→66.528 | yes |
| 2 | 90.320 (1.088) | 88.992 (0.864) | 1.014928 | 90.592→89.440 | 88.577→89.088 | yes |
| 4 | 101.522 (0.816) | 102.833 (0.832) | 0.987246 | 101.505→101.249 | 102.849→102.913 | yes |
| 8 | 125.777 (0.880) | 125.762 (0.816) | 1.000127 | 125.762→126.209 | 126.081→125.665 | yes |
| 16 | 138.097 (0.880) | 140.417 (0.800) | 0.983474 | 137.793→138.177 | 140.385→140.193 | yes |
| 32 | 164.641 (0.768) | 167.601 (0.832) | 0.982339 | 164.865→164.513 | 167.969→167.361 | yes |
| 64 | 188.018 (0.559) | 189.905 (0.944) | 0.990063 | 188.130→187.905 | 189.857→189.121 | yes |
| 128 | 194.802 (0.720) | 195.138 (0.768) | 0.998278 | 195.393→194.817 | 195.234→194.850 | yes |
| 256 | 194.561 (1.216) | 196.576 (0.833) | 0.989750 | 194.434→197.025 | 197.056→196.289 | yes |
| 512 | 199.041 (0.784) | 199.457 (0.928) | 0.997917 | 199.682→199.074 | 199.585→199.137 | yes |
| 1024 | 221.122 (1.248) | 218.338 (0.944) | 1.012749 | 222.049→221.057 | 218.529→218.370 | yes |
| 2048 | 307.187 (1.584) | 302.307 (1.760) | 1.016143 | 307.683→307.778 | 302.978→302.723 | yes |
| 4096 | 470.117 (3.504) | 460.212 (4.064) | 1.021523 | 470.117→473.477 | 462.372→460.325 | yes |
| 8192 | 775.591 (13.584) | 776.886 (21.872) | 0.998334 | 769.575→816.711 | 758.216→808.777 | yes |

8–8192 geometric ratio: **0.999078×**; 4/11 faster. 14/14 tactics match.

All 100 samples retained. 1/2/4 excluded only from 8–8192 retention aggregate. Serial A1→B1 does not cancel temporal drift. Ordered quarters and MAD describe sample variation, not causal confidence. Frozen comparator external-finalize wording is historical and does not describe either integrated arm.

Recorded owned process groups absent and all eight GPUs idle after each arm and during archive creation. No fresh post-transfer closure is inferred.
