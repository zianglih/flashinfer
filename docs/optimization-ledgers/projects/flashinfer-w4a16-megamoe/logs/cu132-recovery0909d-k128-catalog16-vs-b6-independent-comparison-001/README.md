# K128 B6 versus whole initial16 and published shared layout

B6 versus initial16, retention8–4096: **-0.234344% latency GM**, 4/10 wins. Full13 secondary: +1.987510% GM, 4/13 wins.

B6 versus retained published shared layout, retention8–4096: **+0.228269% latency GM**, 4/10 wins. Full13 secondary: +0.112228% GM, 5/13 wins. Counts1/2/4 remain excluded from both decisions.

| Tokens | Published shared ms | Initial16 ms | B6 ms | B6 vs initial16 | B6 vs published | Initial16 tactic | B6 tactic |
|---:|---:|---:|---:|---:|---:|:---|:---|
| 1 | 0.085088 | 0.072240 | 0.085409 | +18.230% | +0.377% | M256/N128/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 2 | 0.106128 | 0.092497 | 0.097809 | +5.743% | -7.839% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 4 | 0.121106 | 0.122769 | 0.129841 | +5.760% | +7.213% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 8 | 0.148705 | 0.147121 | 0.140193 | -4.709% | -5.724% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 16 | 0.160066 | 0.156210 | 0.150657 | -3.555% | -5.878% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 32 | 0.178001 | 0.184210 | 0.175362 | -4.803% | -1.483% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 64 | 0.202978 | 0.207058 | 0.208386 | +0.641% | +2.664% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 128 | 0.207521 | 0.206642 | 0.215538 | +4.305% | +3.863% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 256 | 0.207697 | 0.214050 | 0.215298 | +0.583% | +3.660% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 512 | 0.206354 | 0.212050 | 0.220643 | +4.052% | +6.925% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 1024 | 0.237858 | 0.236451 | 0.239442 | +1.265% | +0.666% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 2048 | 0.320691 | 0.315683 | 0.315315 | -0.117% | -1.676% | M256/N128/K256, C2, F4, reuse, S2 | M256/N128/K256, C2, F8, reuse, S2 |
| 4096 | 0.483602 | 0.481540 | 0.483813 | +0.472% | +0.044% | M256/N128/K256, C2, F4, reuse, S2 | M256/N128/K256, C2, F4, reuse, S2 |

Against initial16, 7 full rows retain their tactic: T2 +5.743%; T32 -4.803%; T128 +4.305%; T256 +0.583%; T512 +4.052%; T1024 +1.265%; T4096 +0.472%. Sequential whole-run timing is not a fixed-tactic causal experiment.

Benchmark subprocess B6 932.617467093s, initial16 932.001498857s, published 596.187686985s; current outer 936.030871167s and timer utility 5.994566776s are separate.

All13×100 primary samples reproduce the printed medians, with13×16 secondary hot rankings and104 choices/resources. Activation {'3': 104}; raw {'4': 16, '5': 88}; ACC {'2': 104}; decoded {'2': 16, '3': 88}; selected K {'256': 104}; scheduler {'2': 104}; local bytes {'0': 104}.

Separate BF16 staging observations remain87 fused/17 empty with all80 retention cases fused. Original reconstruction owns source/native validation; no native validator is rerun here. Current source b496 changes K128 activation preference from3 to6 and adds the public fallback parametrization. K256 remains B3, both K values retain ACC2 and the same sixteen-entry catalog. Actual19/43 numerical records are separate, with the original catalog CPU test inherited from c458.

The entire initial16 1da1 CURRENT columns supply the experimental B6 BEFORE, and the entire published1a763 CURRENT columns supply the retained comparison. No baseline reconstruction, row replacement, minima, drift correction or GPU/validator rerun.

[All rows and pins](comparison.json)

## Root decision

B6/catalog16 is not promoted: all13 winners still selectK256, and benchmark subprocess wall is56.43% higher than the published eight-entry run. The0.234344% ten-row improvement over initial16 does not make it a new retained best; published comparison remains+0.228269%. Preserve all whole runs and use exact published056ce/af938 for the requested current-best profiles. [Complete secondary K-score changes](SELECTION_SCORES.md).
