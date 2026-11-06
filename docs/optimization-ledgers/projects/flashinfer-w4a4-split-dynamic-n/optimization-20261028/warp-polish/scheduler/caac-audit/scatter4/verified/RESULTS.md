# Independent CAAC audit

Primary: median of all100 CUPTI samples per process, geometric mean of C1/C2 medians divided by geometric mean of A1/A2 medians. First25/last25/last50 are diagnostics only; never substituted. Historical99f4 data supplies routes and native winners only.

| Model | Tokens | Backend | Speedup | C1/C2 spread | A1/A2 spread |
|---|---:|---|---:|---:|---:|
| kimi-k3 | 4 | CuteDSL MXFP4x8 | -0.123% | 0.123% | 0.125% |
| kimi-k3 | 4 | CuteDSL MXFP8 | +0.060% | 0.279% | 0.278% |
| kimi-k3 | 4 | CuteDSL PER-TOKEN | +0.251% | 0.002% | 0.391% |
| kimi-k3 | 4 | CuteDSL W4A4 | -0.182% | 0.214% | 0.031% |
| kimi-k3 | 64 | CuteDSL MXFP4x8 | +0.024% | 0.021% | 0.028% |
| kimi-k3 | 64 | CuteDSL MXFP8 | -0.021% | 0.058% | 0.000% |
| kimi-k3 | 64 | CuteDSL PER-TOKEN | +0.095% | 0.472% | 0.230% |
| kimi-k3 | 64 | CuteDSL W4A4 | -0.070% | 0.041% | 0.007% |
| kimi-k3 | 4096 | CuteDSL MXFP4x8 | -0.010% | 0.065% | 0.142% |
| kimi-k3 | 4096 | CuteDSL MXFP8 | +0.098% | 0.114% | 0.013% |
| kimi-k3 | 4096 | CuteDSL PER-TOKEN | -0.154% | 0.057% | 0.164% |
| kimi-k3 | 4096 | CuteDSL W4A4 | +0.010% | 0.200% | 0.029% |
| kimi-k3 | 16384 | CuteDSL MXFP4x8 | +2.670% | 0.696% | 2.180% |
| kimi-k3 | 16384 | CuteDSL MXFP8 | +0.594% | 0.389% | 3.962% |
| kimi-k3 | 16384 | CuteDSL PER-TOKEN | +0.615% | 0.329% | 0.984% |
| kimi-k3 | 16384 | CuteDSL W4A4 | -1.199% | 2.451% | 3.891% |
| nemo3-ultra | 4 | CuteDSL MXFP4x8 | -0.000% | 0.494% | 0.133% |
| nemo3-ultra | 4 | CuteDSL MXFP8 | +0.116% | 0.230% | 0.065% |
| nemo3-ultra | 4 | CuteDSL PER-TOKEN | -0.171% | 0.040% | 0.230% |
| nemo3-ultra | 4 | CuteDSL W4A4 | -0.086% | 0.172% | 0.175% |
| nemo3-ultra | 64 | CuteDSL MXFP4x8 | +0.007% | 0.101% | 0.063% |
| nemo3-ultra | 64 | CuteDSL MXFP8 | -0.103% | 0.030% | 0.104% |
| nemo3-ultra | 64 | CuteDSL PER-TOKEN | +0.029% | 0.068% | 0.218% |
| nemo3-ultra | 64 | CuteDSL W4A4 | +0.012% | 0.084% | 0.012% |
| nemo3-ultra | 4096 | CuteDSL MXFP4x8 | -0.559% | 0.104% | 0.013% |
| nemo3-ultra | 4096 | CuteDSL MXFP8 | +0.044% | 0.036% | 0.196% |
| nemo3-ultra | 4096 | CuteDSL PER-TOKEN | +0.010% | 0.000% | 0.130% |
| nemo3-ultra | 4096 | CuteDSL W4A4 | +0.092% | 0.177% | 0.184% |
| nemo3-ultra | 16384 | CuteDSL MXFP4x8 | +1.601% | 2.151% | 0.599% |
| nemo3-ultra | 16384 | CuteDSL MXFP8 | +0.548% | 2.306% | 4.114% |
| nemo3-ultra | 16384 | CuteDSL PER-TOKEN | -0.256% | 0.002% | 0.022% |
| nemo3-ultra | 16384 | CuteDSL W4A4 | -0.302% | 0.239% | 0.372% |
| v3 | 4 | CuteDSL MXFP4x8 | -0.189% | 0.105% | 0.206% |
| v3 | 4 | CuteDSL MXFP8 | +0.153% | 0.094% | 0.165% |
| v3 | 4 | CuteDSL PER-TOKEN | +0.173% | 0.253% | 0.032% |
| v3 | 4 | CuteDSL W4A4 | -0.018% | 0.000% | 0.171% |
| v3 | 64 | CuteDSL MXFP4x8 | +0.062% | 0.075% | 0.149% |
| v3 | 64 | CuteDSL MXFP8 | -0.070% | 0.037% | 0.161% |
| v3 | 64 | CuteDSL PER-TOKEN | +0.024% | 0.035% | 0.011% |
| v3 | 64 | CuteDSL W4A4 | -0.006% | 0.024% | 0.111% |
| v3 | 4096 | CuteDSL MXFP4x8 | -0.177% | 0.000% | 0.099% |
| v3 | 4096 | CuteDSL MXFP8 | +0.108% | 0.042% | 0.026% |
| v3 | 4096 | CuteDSL PER-TOKEN | +0.187% | 0.439% | 0.348% |
| v3 | 4096 | CuteDSL W4A4 | +0.201% | 0.008% | 0.132% |
| v3 | 16384 | CuteDSL MXFP4x8 | +0.109% | 0.717% | 2.921% |
| v3 | 16384 | CuteDSL MXFP8 | -0.182% | 0.058% | 1.947% |
| v3 | 16384 | CuteDSL PER-TOKEN | +0.667% | 0.071% | 0.095% |
| v3 | 16384 | CuteDSL W4A4 | +0.980% | 0.068% | 0.117% |
| v41-flash | 4 | CuteDSL MXFP4x8 | +0.092% | 0.046% | 0.322% |
| v41-flash | 4 | CuteDSL MXFP8 | -0.128% | 0.161% | 0.225% |
| v41-flash | 4 | CuteDSL PER-TOKEN | +0.125% | 0.000% | 0.251% |
| v41-flash | 4 | CuteDSL W4A4 | -0.046% | 0.091% | 0.090% |
| v41-flash | 64 | CuteDSL MXFP4x8 | +0.066% | 0.025% | 0.025% |
| v41-flash | 64 | CuteDSL MXFP8 | -0.030% | 0.087% | 0.046% |
| v41-flash | 64 | CuteDSL PER-TOKEN | +0.023% | 0.147% | 0.069% |
| v41-flash | 64 | CuteDSL W4A4 | +0.004% | 0.072% | 0.031% |
| v41-flash | 4096 | CuteDSL MXFP4x8 | -0.291% | 0.296% | 0.009% |
| v41-flash | 4096 | CuteDSL MXFP8 | -0.016% | 0.033% | 0.038% |
| v41-flash | 4096 | CuteDSL PER-TOKEN | -0.160% | 0.055% | 0.193% |
| v41-flash | 4096 | CuteDSL W4A4 | -0.089% | 0.334% | 0.283% |
| v41-flash | 16384 | CuteDSL MXFP4x8 | +0.618% | 0.583% | 0.450% |
| v41-flash | 16384 | CuteDSL MXFP8 | +3.032% | 0.132% | 3.987% |
| v41-flash | 16384 | CuteDSL PER-TOKEN | -0.110% | 0.023% | 0.691% |
| v41-flash | 16384 | CuteDSL W4A4 | -0.081% | 0.603% | 0.035% |

Verified 64 cells, 48 public-process records and 25600 raw CUPTI samples.

Two candidates run on separate GPUs of the same node. Static clocks/thermal and existing large-prefill bimodality can affect matched medians; source-paired CAAC does not prove causality for small differences. No new public autotuning traversal, external baseline run, or sanitizer.
