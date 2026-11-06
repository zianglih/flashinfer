# Independent CAAC audit

Primary: median of all100 CUPTI samples per process, geometric mean of C1/C2 medians divided by geometric mean of A1/A2 medians. First25/last25/last50 are diagnostics only; never substituted. Historical99f4 data supplies routes and native winners only.

| Model | Tokens | Backend | Speedup | C1/C2 spread | A1/A2 spread |
|---|---:|---|---:|---:|---:|
| kimi-k3 | 4 | CuteDSL MXFP4x8 | +0.391% | 0.062% | 0.158% |
| kimi-k3 | 4 | CuteDSL MXFP8 | +0.040% | 0.020% | 0.059% |
| kimi-k3 | 4 | CuteDSL PER-TOKEN | -0.138% | 0.170% | 0.560% |
| kimi-k3 | 4 | CuteDSL W4A4 | -0.091% | 0.091% | 0.029% |
| kimi-k3 | 64 | CuteDSL MXFP4x8 | +0.273% | 0.028% | 0.042% |
| kimi-k3 | 64 | CuteDSL MXFP8 | +0.154% | 0.027% | 0.070% |
| kimi-k3 | 64 | CuteDSL PER-TOKEN | -0.101% | 0.072% | 0.249% |
| kimi-k3 | 64 | CuteDSL W4A4 | +0.118% | 0.345% | 0.041% |
| kimi-k3 | 4096 | CuteDSL MXFP4x8 | +0.303% | 0.028% | 0.179% |
| kimi-k3 | 4096 | CuteDSL MXFP8 | +0.215% | 0.035% | 0.040% |
| kimi-k3 | 4096 | CuteDSL PER-TOKEN | +0.063% | 0.072% | 0.068% |
| kimi-k3 | 4096 | CuteDSL W4A4 | +0.040% | 0.004% | 0.058% |
| kimi-k3 | 16384 | CuteDSL MXFP4x8 | +1.242% | 0.070% | 6.150% |
| kimi-k3 | 16384 | CuteDSL MXFP8 | -2.044% | 0.833% | 1.598% |
| kimi-k3 | 16384 | CuteDSL PER-TOKEN | -1.008% | 0.122% | 1.394% |
| kimi-k3 | 16384 | CuteDSL W4A4 | +0.390% | 1.451% | 1.218% |
| nemo3-ultra | 4 | CuteDSL MXFP4x8 | +0.000% | 0.090% | 0.360% |
| nemo3-ultra | 4 | CuteDSL MXFP8 | +0.082% | 0.032% | 0.065% |
| nemo3-ultra | 4 | CuteDSL PER-TOKEN | +0.309% | 0.000% | 0.076% |
| nemo3-ultra | 4 | CuteDSL W4A4 | +0.067% | 0.090% | 0.044% |
| nemo3-ultra | 64 | CuteDSL MXFP4x8 | -0.496% | 0.000% | 0.038% |
| nemo3-ultra | 64 | CuteDSL MXFP8 | +0.196% | 0.029% | 0.096% |
| nemo3-ultra | 64 | CuteDSL PER-TOKEN | +0.225% | 0.104% | 0.022% |
| nemo3-ultra | 64 | CuteDSL W4A4 | +0.158% | 0.036% | 0.158% |
| nemo3-ultra | 4096 | CuteDSL MXFP4x8 | -0.405% | 0.317% | 0.045% |
| nemo3-ultra | 4096 | CuteDSL MXFP8 | -0.187% | 0.267% | 0.036% |
| nemo3-ultra | 4096 | CuteDSL PER-TOKEN | -0.197% | 0.426% | 0.020% |
| nemo3-ultra | 4096 | CuteDSL W4A4 | -0.234% | 0.234% | 0.292% |
| nemo3-ultra | 16384 | CuteDSL MXFP4x8 | -0.703% | 1.120% | 3.963% |
| nemo3-ultra | 16384 | CuteDSL MXFP8 | -2.915% | 0.761% | 2.094% |
| nemo3-ultra | 16384 | CuteDSL PER-TOKEN | +0.163% | 0.039% | 0.038% |
| nemo3-ultra | 16384 | CuteDSL W4A4 | +0.549% | 0.744% | 0.464% |
| v3 | 4 | CuteDSL MXFP4x8 | +0.035% | 0.311% | 0.313% |
| v3 | 4 | CuteDSL MXFP8 | -0.222% | 0.141% | 0.164% |
| v3 | 4 | CuteDSL PER-TOKEN | -0.189% | 0.157% | 0.220% |
| v3 | 4 | CuteDSL W4A4 | +0.220% | 0.342% | 0.034% |
| v3 | 64 | CuteDSL MXFP4x8 | +0.025% | 0.111% | 0.012% |
| v3 | 64 | CuteDSL MXFP8 | -0.025% | 0.080% | 0.014% |
| v3 | 64 | CuteDSL PER-TOKEN | -0.006% | 0.024% | 0.059% |
| v3 | 64 | CuteDSL W4A4 | +0.025% | 0.356% | 0.380% |
| v3 | 4096 | CuteDSL MXFP4x8 | -1.057% | 0.071% | 0.035% |
| v3 | 4096 | CuteDSL MXFP8 | -0.204% | 0.068% | 0.163% |
| v3 | 4096 | CuteDSL PER-TOKEN | -0.022% | 0.038% | 0.136% |
| v3 | 4096 | CuteDSL W4A4 | +0.039% | 0.209% | 0.023% |
| v3 | 16384 | CuteDSL MXFP4x8 | +3.525% | 1.949% | 2.187% |
| v3 | 16384 | CuteDSL MXFP8 | +1.359% | 3.045% | 3.314% |
| v3 | 16384 | CuteDSL PER-TOKEN | -0.407% | 0.079% | 0.178% |
| v3 | 16384 | CuteDSL W4A4 | -0.216% | 0.209% | 0.032% |
| v41-flash | 4 | CuteDSL MXFP4x8 | -0.257% | 0.048% | 0.001% |
| v41-flash | 4 | CuteDSL MXFP8 | +0.418% | 0.125% | 0.321% |
| v41-flash | 4 | CuteDSL PER-TOKEN | +0.040% | 0.249% | 0.332% |
| v41-flash | 4 | CuteDSL W4A4 | +0.248% | 0.047% | 0.092% |
| v41-flash | 64 | CuteDSL MXFP4x8 | +0.144% | 0.082% | 0.074% |
| v41-flash | 64 | CuteDSL MXFP8 | +0.235% | 0.037% | 0.050% |
| v41-flash | 64 | CuteDSL PER-TOKEN | +0.162% | 0.023% | 0.070% |
| v41-flash | 64 | CuteDSL W4A4 | +0.048% | 0.063% | 0.111% |
| v41-flash | 4096 | CuteDSL MXFP4x8 | -0.222% | 0.081% | 0.076% |
| v41-flash | 4096 | CuteDSL MXFP8 | +0.203% | 0.013% | 0.005% |
| v41-flash | 4096 | CuteDSL PER-TOKEN | +0.018% | 0.095% | 0.012% |
| v41-flash | 4096 | CuteDSL W4A4 | -0.018% | 0.027% | 0.000% |
| v41-flash | 16384 | CuteDSL MXFP4x8 | +0.420% | 1.074% | 1.684% |
| v41-flash | 16384 | CuteDSL MXFP8 | -1.938% | 2.988% | 1.087% |
| v41-flash | 16384 | CuteDSL PER-TOKEN | +0.056% | 0.147% | 0.235% |
| v41-flash | 16384 | CuteDSL W4A4 | -0.101% | 0.136% | 0.120% |

Verified 64 cells, 48 public-process records and 25600 raw CUPTI samples.

Two candidates run on separate GPUs of the same node. Static clocks/thermal and existing large-prefill bimodality can affect matched medians; source-paired CAAC does not prove causality for small differences. No new public autotuning traversal, external baseline run, or sanitizer.
