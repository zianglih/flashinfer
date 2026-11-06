# Independent CAAC audit

Primary: median of all100 CUPTI samples per process, geometric mean of C1/C2 medians divided by geometric mean of A1/A2 medians. First25/last25/last50 are diagnostics only; never substituted. Historical99f4 data supplies routes and native winners only.

| Model | Tokens | Backend | Speedup | C1/C2 spread | A1/A2 spread |
|---|---:|---|---:|---:|---:|
| kimi-k3 | 4 | CuteDSL MXFP4x8 | -0.171% | 0.000% | 0.032% |
| kimi-k3 | 4 | CuteDSL MXFP8 | +0.060% | 0.120% | 0.080% |
| kimi-k3 | 4 | CuteDSL PER-TOKEN | +0.111% | 0.306% | 0.082% |
| kimi-k3 | 4 | CuteDSL W4A4 | +0.168% | 0.062% | 0.275% |
| kimi-k3 | 64 | CuteDSL MXFP4x8 | +0.053% | 0.007% | 0.014% |
| kimi-k3 | 64 | CuteDSL MXFP8 | +0.002% | 0.093% | 0.035% |
| kimi-k3 | 64 | CuteDSL PER-TOKEN | +0.111% | 0.171% | 0.197% |
| kimi-k3 | 64 | CuteDSL W4A4 | +0.000% | 0.088% | 0.155% |
| kimi-k3 | 4096 | CuteDSL MXFP4x8 | -0.494% | 0.227% | 0.012% |
| kimi-k3 | 4096 | CuteDSL MXFP8 | +0.120% | 0.116% | 0.069% |
| kimi-k3 | 4096 | CuteDSL PER-TOKEN | +0.194% | 0.025% | 0.233% |
| kimi-k3 | 4096 | CuteDSL W4A4 | +0.133% | 0.121% | 0.137% |
| kimi-k3 | 16384 | CuteDSL MXFP4x8 | -1.545% | 8.869% | 1.630% |
| kimi-k3 | 16384 | CuteDSL MXFP8 | -4.188% | 0.591% | 1.773% |
| kimi-k3 | 16384 | CuteDSL PER-TOKEN | -0.264% | 0.047% | 1.987% |
| kimi-k3 | 16384 | CuteDSL W4A4 | -3.833% | 0.183% | 4.777% |
| nemo3-ultra | 4 | CuteDSL MXFP4x8 | +0.044% | 0.225% | 0.044% |
| nemo3-ultra | 4 | CuteDSL MXFP8 | +0.048% | 0.033% | 0.129% |
| nemo3-ultra | 4 | CuteDSL PER-TOKEN | -0.114% | 0.153% | 0.075% |
| nemo3-ultra | 4 | CuteDSL W4A4 | -0.042% | 0.266% | 0.175% |
| nemo3-ultra | 64 | CuteDSL MXFP4x8 | -0.051% | 0.025% | 0.101% |
| nemo3-ultra | 64 | CuteDSL MXFP8 | +0.107% | 0.163% | 0.037% |
| nemo3-ultra | 64 | CuteDSL PER-TOKEN | -0.006% | 0.103% | 0.046% |
| nemo3-ultra | 64 | CuteDSL W4A4 | -0.006% | 0.207% | 0.097% |
| nemo3-ultra | 4096 | CuteDSL MXFP4x8 | -0.084% | 0.097% | 0.317% |
| nemo3-ultra | 4096 | CuteDSL MXFP8 | +0.093% | 0.077% | 0.149% |
| nemo3-ultra | 4096 | CuteDSL PER-TOKEN | +0.241% | 0.060% | 0.533% |
| nemo3-ultra | 4096 | CuteDSL W4A4 | +0.324% | 0.162% | 0.162% |
| nemo3-ultra | 16384 | CuteDSL MXFP4x8 | +2.683% | 1.389% | 3.713% |
| nemo3-ultra | 16384 | CuteDSL MXFP8 | -4.472% | 2.925% | 0.108% |
| nemo3-ultra | 16384 | CuteDSL PER-TOKEN | -0.501% | 0.069% | 0.138% |
| nemo3-ultra | 16384 | CuteDSL W4A4 | -0.645% | 0.873% | 0.170% |
| v3 | 4 | CuteDSL MXFP4x8 | -0.017% | 0.034% | 0.069% |
| v3 | 4 | CuteDSL MXFP8 | +0.072% | 0.070% | 0.164% |
| v3 | 4 | CuteDSL PER-TOKEN | -0.016% | 0.158% | 0.001% |
| v3 | 4 | CuteDSL W4A4 | -0.017% | 0.137% | 0.103% |
| v3 | 64 | CuteDSL MXFP4x8 | +0.055% | 0.086% | 0.050% |
| v3 | 64 | CuteDSL MXFP8 | +0.026% | 0.007% | 0.073% |
| v3 | 64 | CuteDSL PER-TOKEN | -0.000% | 0.059% | 0.082% |
| v3 | 64 | CuteDSL W4A4 | -0.104% | 0.134% | 0.098% |
| v3 | 4096 | CuteDSL MXFP4x8 | -0.796% | 0.043% | 0.057% |
| v3 | 4096 | CuteDSL MXFP8 | -0.032% | 0.042% | 0.000% |
| v3 | 4096 | CuteDSL PER-TOKEN | +0.771% | 0.322% | 0.143% |
| v3 | 4096 | CuteDSL W4A4 | +0.255% | 0.069% | 0.008% |
| v3 | 16384 | CuteDSL MXFP4x8 | +1.159% | 0.627% | 1.974% |
| v3 | 16384 | CuteDSL MXFP8 | -2.716% | 2.774% | 3.406% |
| v3 | 16384 | CuteDSL PER-TOKEN | +2.139% | 0.061% | 0.138% |
| v3 | 16384 | CuteDSL W4A4 | +1.558% | 0.129% | 0.046% |
| v41-flash | 4 | CuteDSL MXFP4x8 | +0.116% | 0.185% | 0.046% |
| v41-flash | 4 | CuteDSL MXFP8 | -0.048% | 0.032% | 0.063% |
| v41-flash | 4 | CuteDSL PER-TOKEN | +0.083% | 0.251% | 0.082% |
| v41-flash | 4 | CuteDSL W4A4 | -0.295% | 0.091% | 0.045% |
| v41-flash | 64 | CuteDSL MXFP4x8 | -0.004% | 0.025% | 0.049% |
| v41-flash | 64 | CuteDSL MXFP8 | +0.030% | 0.050% | 0.009% |
| v41-flash | 64 | CuteDSL PER-TOKEN | +0.058% | 0.054% | 0.031% |
| v41-flash | 64 | CuteDSL W4A4 | +0.075% | 0.095% | 0.040% |
| v41-flash | 4096 | CuteDSL MXFP4x8 | -0.562% | 0.301% | 0.120% |
| v41-flash | 4096 | CuteDSL MXFP8 | -0.048% | 0.046% | 0.033% |
| v41-flash | 4096 | CuteDSL PER-TOKEN | +0.010% | 0.257% | 0.269% |
| v41-flash | 4096 | CuteDSL W4A4 | +0.107% | 0.265% | 0.087% |
| v41-flash | 16384 | CuteDSL MXFP4x8 | -3.592% | 5.533% | 0.077% |
| v41-flash | 16384 | CuteDSL MXFP8 | +1.614% | 1.231% | 2.639% |
| v41-flash | 16384 | CuteDSL PER-TOKEN | +1.000% | 0.264% | 0.032% |
| v41-flash | 16384 | CuteDSL W4A4 | +0.841% | 0.213% | 0.567% |

Verified 64 cells, 48 public-process records and 25600 raw CUPTI samples.

Two candidates run on separate GPUs of the same node. Static clocks/thermal and existing large-prefill bimodality can affect matched medians; source-paired CAAC does not prove causality for small differences. No new public autotuning traversal, external baseline run, or sanitizer.
