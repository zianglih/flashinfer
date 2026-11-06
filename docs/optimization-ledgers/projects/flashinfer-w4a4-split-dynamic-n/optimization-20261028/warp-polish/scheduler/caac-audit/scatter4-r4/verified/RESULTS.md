# Independent CAAC audit

Primary: median of all100 CUPTI samples per process, geometric mean of C1/C2 medians divided by geometric mean of A1/A2 medians. First25/last25/last50 are diagnostics only; never substituted. Historical99f4 data supplies routes and native winners only.

| Model | Tokens | Backend | Speedup | C1/C2 spread | A1/A2 spread |
|---|---:|---|---:|---:|---:|
| kimi-k3 | 4 | CuteDSL MXFP4x8 | -0.171% | 0.061% | 0.031% |
| kimi-k3 | 4 | CuteDSL MXFP8 | +0.041% | 0.060% | 0.060% |
| kimi-k3 | 4 | CuteDSL PER-TOKEN | +0.085% | 0.139% | 0.307% |
| kimi-k3 | 4 | CuteDSL W4A4 | -0.076% | 0.060% | 0.031% |
| kimi-k3 | 64 | CuteDSL MXFP4x8 | +0.108% | 0.105% | 0.042% |
| kimi-k3 | 64 | CuteDSL MXFP8 | +0.070% | 0.113% | 0.012% |
| kimi-k3 | 64 | CuteDSL PER-TOKEN | +0.200% | 0.157% | 0.007% |
| kimi-k3 | 64 | CuteDSL W4A4 | -0.152% | 0.149% | 0.033% |
| kimi-k3 | 4096 | CuteDSL MXFP4x8 | -0.172% | 0.255% | 0.153% |
| kimi-k3 | 4096 | CuteDSL MXFP8 | -0.010% | 0.129% | 0.059% |
| kimi-k3 | 4096 | CuteDSL PER-TOKEN | +0.168% | 0.004% | 0.118% |
| kimi-k3 | 4096 | CuteDSL W4A4 | +0.025% | 0.142% | 0.075% |
| kimi-k3 | 16384 | CuteDSL MXFP4x8 | -0.656% | 2.179% | 0.279% |
| kimi-k3 | 16384 | CuteDSL MXFP8 | -0.704% | 0.081% | 3.416% |
| kimi-k3 | 16384 | CuteDSL PER-TOKEN | -0.585% | 1.171% | 0.075% |
| kimi-k3 | 16384 | CuteDSL W4A4 | -0.307% | 0.201% | 2.466% |
| nemo3-ultra | 4 | CuteDSL MXFP4x8 | -0.067% | 0.405% | 0.270% |
| nemo3-ultra | 4 | CuteDSL MXFP8 | -0.016% | 0.361% | 0.000% |
| nemo3-ultra | 4 | CuteDSL PER-TOKEN | -0.096% | 0.232% | 0.191% |
| nemo3-ultra | 4 | CuteDSL W4A4 | -0.151% | 0.088% | 0.042% |
| nemo3-ultra | 64 | CuteDSL MXFP4x8 | +0.019% | 0.064% | 0.051% |
| nemo3-ultra | 64 | CuteDSL MXFP8 | -0.092% | 0.015% | 0.170% |
| nemo3-ultra | 64 | CuteDSL PER-TOKEN | +0.063% | 0.057% | 0.023% |
| nemo3-ultra | 64 | CuteDSL W4A4 | +0.006% | 0.036% | 0.121% |
| nemo3-ultra | 4096 | CuteDSL MXFP4x8 | -0.045% | 0.058% | 0.006% |
| nemo3-ultra | 4096 | CuteDSL MXFP8 | +0.170% | 0.021% | 0.010% |
| nemo3-ultra | 4096 | CuteDSL PER-TOKEN | -0.256% | 0.603% | 0.000% |
| nemo3-ultra | 4096 | CuteDSL W4A4 | -0.217% | 0.037% | 0.206% |
| nemo3-ultra | 16384 | CuteDSL MXFP4x8 | -1.294% | 1.317% | 0.337% |
| nemo3-ultra | 16384 | CuteDSL MXFP8 | -0.589% | 0.290% | 3.230% |
| nemo3-ultra | 16384 | CuteDSL PER-TOKEN | -0.185% | 0.056% | 0.024% |
| nemo3-ultra | 16384 | CuteDSL W4A4 | -0.331% | 0.443% | 0.246% |
| v3 | 4 | CuteDSL MXFP4x8 | +0.259% | 0.209% | 0.174% |
| v3 | 4 | CuteDSL MXFP8 | -0.130% | 0.023% | 0.187% |
| v3 | 4 | CuteDSL PER-TOKEN | +0.014% | 0.063% | 0.286% |
| v3 | 4 | CuteDSL W4A4 | +0.289% | 0.409% | 0.240% |
| v3 | 64 | CuteDSL MXFP4x8 | -0.031% | 0.124% | 0.087% |
| v3 | 64 | CuteDSL MXFP8 | -0.025% | 0.051% | 0.014% |
| v3 | 64 | CuteDSL PER-TOKEN | -0.094% | 0.035% | 0.082% |
| v3 | 64 | CuteDSL W4A4 | -0.098% | 0.171% | 0.196% |
| v3 | 4096 | CuteDSL MXFP4x8 | -0.403% | 0.121% | 0.035% |
| v3 | 4096 | CuteDSL MXFP8 | +0.095% | 0.016% | 0.037% |
| v3 | 4096 | CuteDSL PER-TOKEN | +0.544% | 0.013% | 0.571% |
| v3 | 4096 | CuteDSL W4A4 | +0.271% | 0.116% | 0.178% |
| v3 | 16384 | CuteDSL MXFP4x8 | +1.922% | 3.062% | 0.130% |
| v3 | 16384 | CuteDSL MXFP8 | -2.351% | 0.025% | 0.066% |
| v3 | 16384 | CuteDSL PER-TOKEN | +1.532% | 0.072% | 0.073% |
| v3 | 16384 | CuteDSL W4A4 | +1.314% | 0.032% | 0.085% |
| v41-flash | 4 | CuteDSL MXFP4x8 | +0.115% | 0.275% | 0.140% |
| v41-flash | 4 | CuteDSL MXFP8 | -0.001% | 0.063% | 0.000% |
| v41-flash | 4 | CuteDSL PER-TOKEN | +0.126% | 0.168% | 0.335% |
| v41-flash | 4 | CuteDSL W4A4 | +0.159% | 0.272% | 0.046% |
| v41-flash | 64 | CuteDSL MXFP4x8 | -0.037% | 0.025% | 0.050% |
| v41-flash | 64 | CuteDSL MXFP8 | +0.009% | 0.064% | 0.046% |
| v41-flash | 64 | CuteDSL PER-TOKEN | +0.035% | 0.054% | 0.000% |
| v41-flash | 64 | CuteDSL W4A4 | -0.012% | 0.040% | 0.063% |
| v41-flash | 4096 | CuteDSL MXFP4x8 | -0.177% | 0.350% | 0.309% |
| v41-flash | 4096 | CuteDSL MXFP8 | +0.003% | 0.003% | 0.025% |
| v41-flash | 4096 | CuteDSL PER-TOKEN | -0.124% | 0.233% | 0.032% |
| v41-flash | 4096 | CuteDSL W4A4 | -0.364% | 0.100% | 0.100% |
| v41-flash | 16384 | CuteDSL MXFP4x8 | +0.298% | 1.963% | 1.283% |
| v41-flash | 16384 | CuteDSL MXFP8 | +0.141% | 2.497% | 0.663% |
| v41-flash | 16384 | CuteDSL PER-TOKEN | +0.860% | 0.216% | 0.381% |
| v41-flash | 16384 | CuteDSL W4A4 | +1.452% | 0.134% | 0.928% |

Verified 64 cells, 48 public-process records and 25600 raw CUPTI samples.

Two candidates run on separate GPUs of the same node. Static clocks/thermal and existing large-prefill bimodality can affect matched medians; source-paired CAAC does not prove causality for small differences. No new public autotuning traversal, external baseline run, or sanitizer.
