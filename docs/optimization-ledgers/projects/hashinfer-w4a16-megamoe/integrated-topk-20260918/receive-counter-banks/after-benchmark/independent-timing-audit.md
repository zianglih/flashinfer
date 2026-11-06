# Retained 7dc B1 versus receive-counter-bank b6fd D1

Same full public precomputed-routing forward on hu9/unchanged boot/environment; retained 7dc B1 versus fresh receive-counter-bank b6fd D1. All100 samples and112 finite bit-exact outputs checked. No routing selection or separate staging/reduction launch.

| Tokens | 7dc µs (MAD) | b6fd µs (MAD) | 7dc/b6fd | B1 Q1→Q4 µs | D1 Q1→Q4 µs | Same tactic |
|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 79.217 (0.960) | 73.137 (1.279) | 1.083132 | 76.705→79.521 | 71.072→73.696 | yes |
| 2 | 91.888 (1.729) | 92.337 (1.440) | 0.995137 | 88.193→93.377 | 88.256→92.705 | yes |
| 4 | 110.689 (1.600) | 104.721 (1.759) | 1.056994 | 107.553→111.041 | 99.361→106.081 | yes |
| 8 | 131.409 (2.320) | 126.129 (1.600) | 1.041862 | 127.169→132.449 | 123.617→126.561 | yes |
| 16 | 144.561 (1.487) | 141.089 (1.728) | 1.024612 | 141.473→145.378 | 136.673→141.249 | yes |
| 32 | 170.706 (3.680) | 164.529 (2.288) | 1.037540 | 167.522→172.001 | 160.097→165.698 | yes |
| 64 | 187.409 (1.536) | 188.018 (1.680) | 0.996764 | 186.049→188.065 | 184.930→189.410 | yes |
| 128 | 196.513 (1.584) | 194.113 (1.440) | 1.012361 | 193.826→197.633 | 190.210→195.649 | yes |
| 256 | 205.857 (2.464) | 190.817 (1.281) | 1.078822 | 205.442→204.513 | 187.777→191.553 | yes |
| 512 | 206.114 (1.712) | 200.130 (1.360) | 1.029898 | 202.882→206.561 | 197.154→200.770 | yes |
| 1024 | 228.082 (1.647) | 219.090 (2.511) | 1.041045 | 223.906→229.059 | 218.818→222.882 | yes |
| 2048 | 330.019 (2.607) | 309.827 (3.279) | 1.065172 | 322.211→331.458 | 306.370→310.658 | yes |
| 4096 | 471.426 (5.793) | 469.766 (3.136) | 1.003535 | 468.579→476.866 | 470.118→471.171 | yes |
| 8192 | 798.438 (25.168) | 805.173 (23.632) | 0.991634 | 771.110→821.158 | 776.262→824.133 | yes |

8–8192 geometric ratio: **1.029054×**; 9/11 faster, 14/14 matching tactics.

1/2/4 remain visible and are excluded only from the 8–8192 geometric aggregate. B1 was measured earlier, followed by profiling and qualification work; this comparison does not cancel temporal drift. MAD and ordered-quarter medians describe observed variation, not causal confidence. Frozen comparator external-finalize wording is historical.
