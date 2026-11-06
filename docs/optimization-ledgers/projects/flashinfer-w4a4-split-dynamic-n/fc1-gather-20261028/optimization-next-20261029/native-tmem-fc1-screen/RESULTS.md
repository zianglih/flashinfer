# Native-TMEM FC1 bounded performance screen

Frozen6a48 vs retained9037swap closure equivalent6be. Does not include later b139release policy.

Decision: reject the current general native epilogue. All predeclared cells are preserved; no retuning, clocks, or post-result source changes.

14/14 cells complete. Same-GPU C-A-A-C, 100 strict CUPTI samples/phase, cold L2 and frozen routes/tactics. Percent is control/candidate minus one; positive is faster.

| Job | Tokens | Backend | C1 us | A1 us | A2 us | C2 us | Speedup | C/A spread |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| ep-nemo3-ultra-w4a4 | 8 | CuteDSL W4A4 | 47.744 | 47.473 | 47.632 | 47.729 | +0.387% | 0.031% / 0.335% |
| ep-nemo3-ultra-w4a4 | 16384 | CuteDSL W4A4 | 585.383 | 697.207 | 696.871 | 585.031 | -16.044% | 0.060% / 0.048% |
| ep-nemo3-ultra-per-token | 16384 | CuteDSL PER-TOKEN | 916.775 | 1107.881 | 1107.848 | 915.591 | -17.302% | 0.129% / 0.003% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP4x8 | 635.816 | 650.504 | 672.744 | 656.151 | -2.362% | 3.198% / 3.419% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP8 | 744.489 | 717.513 | 708.264 | 701.625 | +1.384% | 6.109% / 1.306% |
| ep-v41-flash-w4a4 | 4096 | CuteDSL W4A4 | 340.338 | 340.467 | 340.339 | 340.211 | -0.038% | 0.037% / 0.038% |
| ep-v41-flash-per-token | 4096 | CuteDSL PER-TOKEN | 398.212 | 399.029 | 398.996 | 398.180 | -0.205% | 0.008% / 0.008% |
| ep-kimi-k3-mxfp | 8192 | CuteDSL MXFP4x8 | 584.807 | 612.039 | 606.519 | 585.159 | -3.987% | 0.060% / 0.910% |
| ep-kimi-k3-per-token | 8192 | CuteDSL PER-TOKEN | 622.389 | 668.950 | 669.030 | 622.437 | -6.962% | 0.008% / 0.012% |
| tp-v41-flash-w4a4 | 8 | CuteDSL W4A4 | 51.921 | 52.081 | 51.904 | 51.777 | -0.277% | 0.277% / 0.340% |
| tp-v41-flash-per-token | 8 | CuteDSL PER-TOKEN | 57.105 | 56.977 | 57.025 | 56.960 | +0.055% | 0.254% / 0.085% |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | 1219.674 | 1298.026 | 1301.258 | 1231.306 | -5.707% | 0.954% / 0.249% |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP8 | 1307.162 | 1350.458 | 1333.930 | 1276.699 | -3.750% | 2.386% / 1.239% |
| tp-kimi-k3-mxfp | 4096 | CuteDSL MXFP4x8 | 546.455 | 545.671 | 546.391 | 545.895 | +0.026% | 0.103% / 0.132% |

Source and numerical qualification: `../native-tmem-fc1-audit/QUALIFICATION.md`. Components, sample quartiles and clock timelines remain in each result analysis. Higher-spread cases are not used to claim causality. N3U EP16K W4A4 and per-token regressions have low repeat spread and primarily increase FC1 critical-path duration. The instruction/store-work explanation is consistent with SASS growth; individual operation costs have not been isolated.
