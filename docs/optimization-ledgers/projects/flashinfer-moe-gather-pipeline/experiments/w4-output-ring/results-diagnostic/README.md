# Separate six-cell ACCA diagnostic

The original104-cell CAAC observation remains primary and unmodified. This opposite-order diagnostic does not replace or average into those results. C1/C2 and A1/A2 below mean first/second observation of each arm; actual chronological order here is A1,C1,C2,A2.

| Model | Tokens | GPU primary→repeat | Primary | Repeat | Repeat C1 µs | A1 µs | A2 µs | C2 µs | C spread | A spread |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 EP | 4096 | 2→2 | -1.703% | -1.457% | 543.107 | 544.466 | 557.187 | 542.418 | 0.127% | 2.336% |
| nemo3-ultra EP | 64 | 4→4 | -0.228% | +0.052% | 140.353 | 140.177 | 140.257 | 140.226 | 0.091% | 0.057% |
| v3 EP | 8192 | 6→6 | -2.982% | -0.249% | 544.915 | 543.987 | 542.132 | 538.515 | 1.188% | 0.342% |
| v41-flash EP | 16384 | 7→2 | -2.868% | +2.360% | 1564.553 | 1528.855 | 1525.961 | 1562.345 | 0.141% | 0.190% |
| v3 TP | 4096 | 6→4 | +0.324% | +0.444% | 482.198 | 480.292 | 479.221 | 481.572 | 0.130% | 0.224% |
| v41-flash TP | 32 | 7→6 | -0.250% | +0.047% | 153.089 | 152.929 | 153.025 | 153.009 | 0.052% | 0.063% |

All2400 samples,24 medians and48 loaded native resource records are retained. Resources/configurations agree across all12 cell-stage joins; no local-memory allocation. Seven clock-exception quartiles and no missing windows. Same source/tactics/routes/cache/timer contract as primary; three cases moved device according to the authorized GPU2/4/6 lane allocation, and every comparison remains paired on one GPU.

K3 EP4096 remains negative in both observations, with candidate phase spread7.625% primary and2.336% diagnostic. Its diagnostic FC1/FC2 extensions rise3.776/4.312µs; routing and combine also shift. These timing components are descriptive overlapping-kernel medians, not proof of an isolated arithmetic/index regression. The two small decode losses reverse sign. V41F EP16K reverses its large loss; V3 EP8K becomes a smaller loss. No additional repeat is proposed.

The standard shared report helper has a generic “CAAC” boundary label; the actual immutable configuration and all24 phase records explicitly use ACCA. This note records that presentation distinction without changing any raw receipt.
