# Retained 7dc A1 versus async-retirement 0190 D1

Same full public precomputed-routing forward on hu7/unchanged boot/environment; retained 7dc A1 versus fresh async-retirement 0190 D1. All100 samples and112 finite bit-exact outputs checked. No routing selection or separate staging/reduction launch.

| Tokens | 7dc µs (MAD) | 0190 µs (MAD) | 7dc/0190 | A1 Q1→Q4 µs | D1 Q1→Q4 µs | Same tactic |
|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 64.128 (0.928) | 71.649 (0.737) | 0.895030 | 64.128→64.225 | 71.873→71.456 | yes |
| 2 | 90.320 (1.088) | 81.841 (0.736) | 1.103609 | 90.592→89.440 | 83.008→81.728 | yes |
| 4 | 101.522 (0.816) | 99.088 (0.625) | 1.024559 | 101.505→101.249 | 99.361→98.817 | yes |
| 8 | 125.777 (0.880) | 126.385 (0.913) | 0.995197 | 125.762→126.209 | 127.041→125.954 | yes |
| 16 | 138.097 (0.880) | 140.240 (0.816) | 0.984716 | 137.793→138.177 | 140.448→140.097 | yes |
| 32 | 164.641 (0.768) | 167.058 (1.008) | 0.985535 | 164.865→164.513 | 167.425→167.073 | yes |
| 64 | 188.018 (0.559) | 190.960 (1.089) | 0.984591 | 188.130→187.905 | 191.489→190.849 | yes |
| 128 | 194.802 (0.720) | 196.145 (1.024) | 0.993150 | 195.393→194.817 | 196.194→196.994 | yes |
| 256 | 194.561 (1.216) | 197.889 (0.912) | 0.983188 | 194.434→197.025 | 198.401→197.537 | yes |
| 512 | 199.041 (0.784) | 198.626 (0.945) | 1.002092 | 199.682→199.074 | 198.881→198.626 | yes |
| 1024 | 221.122 (1.248) | 222.594 (0.961) | 0.993385 | 222.049→221.057 | 222.466→222.753 | yes |
| 2048 | 307.187 (1.584) | 306.995 (1.728) | 1.000627 | 307.683→307.778 | 306.691→306.978 | yes |
| 4096 | 470.117 (3.504) | 464.325 (3.280) | 1.012475 | 470.117→473.477 | 465.701→463.621 | yes |
| 8192 | 775.591 (13.584) | 791.780 (16.848) | 0.979555 | 769.575→816.711 | 768.067→802.371 | yes |

8–8192 geometric ratio: **0.992183×**; 3/11 faster, 14/14 matching tactics.

1/2/4 remain visible and are excluded only from the 8–8192 geometric aggregate. A1 was measured earlier, followed by772 and qualification work; this comparison does not cancel temporal drift. MAD and ordered-quarter medians describe observed variation, not causal confidence. Frozen comparator external-finalize wording is historical.

| Tokens | 7dc A1 µs | c2b C1 µs | 0190 D1 µs | c2b/D1 | Same tactic C1/D1 |
|---:|---:|---:|---:|---:|:---:|
| 1 | 64.128 | 74.049 | 71.649 | 1.033490 | yes |
| 2 | 90.320 | 87.984 | 81.841 | 1.075066 | yes |
| 4 | 101.522 | 103.441 | 99.088 | 1.043926 | yes |
| 8 | 125.777 | 125.553 | 126.385 | 0.993421 | yes |
| 16 | 138.097 | 137.985 | 140.240 | 0.983920 | yes |
| 32 | 164.641 | 167.490 | 167.058 | 1.002586 | yes |
| 64 | 188.018 | 187.170 | 190.960 | 0.980150 | yes |
| 128 | 194.802 | 194.433 | 196.145 | 0.991269 | yes |
| 256 | 194.561 | 194.865 | 197.889 | 0.984724 | yes |
| 512 | 199.041 | 197.633 | 198.626 | 0.995001 | yes |
| 1024 | 221.122 | 218.738 | 222.594 | 0.982675 | yes |
| 2048 | 307.187 | 308.769 | 306.995 | 1.005780 | yes |
| 4096 | 470.117 | 466.882 | 464.325 | 1.005507 | yes |
| 8192 | 775.591 | 772.342 | 791.780 | 0.975451 | yes |

c2b/D1 geometric ratio: 0.9909025344144674

Derived from independently audited c2b C1 and current D1, both against identical retained hu7 7dc A1; serial measurements do not cancel drift.
