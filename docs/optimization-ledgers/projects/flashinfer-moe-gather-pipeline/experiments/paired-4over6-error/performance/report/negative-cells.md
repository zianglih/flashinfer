# Paired4over6 whole-chain screen

Current c1ac control vs sole5f232 helper change; all42 planned cells/16,800 CUPTI samples preserved. Two disjoint complete-job leaves, CAAC100/10 cold-L2; initial quantization included for both backends.

| Model | Topology | Backend | Tokens | C1us | A1us | A2us | C2us | Speedup | Cspread | Aspread | Clockexception/missing |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | 32 | 180.177 | 180.385 | 180.225 | 179.970 | -0.128% | 0.115% | 0.089% | 0/0 |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | 16384 | 1042.696 | 1050.137 | 1040.361 | 1033.801 | -0.670% | 0.860% | 0.940% | 2/0 |
| v3 | EP8 | CuteDSL PER-TOKEN | 4096 | 243.522 | 248.113 | 247.922 | 243.618 | -1.793% | 0.040% | 0.077% | 0/0 |
| v41-flash | EP4 | CuteDSL PER-TOKEN | 32 | 130.561 | 130.721 | 130.688 | 130.529 | -0.122% | 0.025% | 0.024% | 0/2 |
| v41-flash | EP4 | CuteDSL PER-TOKEN | 4096 | 398.610 | 402.082 | 402.051 | 399.172 | -0.790% | 0.141% | 0.008% | 0/0 |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 32 | 124.017 | 124.097 | 124.913 | 123.520 | -0.591% | 0.402% | 0.658% | 0/0 |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 4096 | 555.123 | 571.299 | 571.813 | 555.667 | -2.828% | 0.098% | 0.090% | 0/0 |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16384 | 1800.969 | 1870.314 | 1870.770 | 1801.930 | -3.694% | 0.053% | 0.024% | 0/0 |
| v3 | TP8 | CuteDSL PER-TOKEN | 4096 | 467.091 | 469.363 | 469.443 | 467.316 | -0.469% | 0.048% | 0.017% | 0/0 |
| v41-flash | TP4 | CuteDSL PER-TOKEN | 4096 | 534.820 | 542.147 | 541.956 | 534.982 | -1.319% | 0.030% | 0.035% | 0/0 |
| v41-flash | TP4 | CuteDSL PER-TOKEN | 16384 | 1276.905 | 1290.905 | 1290.297 | 1277.322 | -1.045% | 0.033% | 0.047% | 0/0 |
| nemo3-ultra | EP8 | TRTLLM PER-TOKEN | 4096 | 311.890 | 312.851 | 312.836 | 311.906 | -0.302% | 0.005% | 0.005% | 0/0 |
| nemo3-ultra | EP8 | TRTLLM PER-TOKEN | 16384 | 967.974 | 972.726 | 972.666 | 968.103 | -0.479% | 0.013% | 0.006% | 0/0 |
| v3 | EP8 | TRTLLM PER-TOKEN | 32 | 111.969 | 112.049 | 111.953 | 112.002 | -0.014% | 0.029% | 0.085% | 0/0 |
| v3 | EP8 | TRTLLM PER-TOKEN | 4096 | 269.986 | 273.090 | 272.770 | 269.666 | -1.137% | 0.119% | 0.117% | 0/0 |
| v41-flash | EP4 | TRTLLM PER-TOKEN | 32 | 138.849 | 139.680 | 139.377 | 138.832 | -0.493% | 0.012% | 0.218% | 0/0 |
| v41-flash | EP4 | TRTLLM PER-TOKEN | 4096 | 415.906 | 417.714 | 417.458 | 415.779 | -0.417% | 0.030% | 0.061% | 0/0 |
| nemo3-ultra | TP8 | TRTLLM PER-TOKEN | 4096 | 517.043 | 517.955 | 518.037 | 517.410 | -0.149% | 0.071% | 0.016% | 0/0 |
| nemo3-ultra | TP8 | TRTLLM PER-TOKEN | 16384 | 1663.369 | 1667.113 | 1668.176 | 1662.649 | -0.278% | 0.043% | 0.064% | 0/0 |
| v3 | TP8 | TRTLLM PER-TOKEN | 32 | 131.521 | 131.584 | 131.377 | 131.409 | -0.012% | 0.085% | 0.158% | 0/0 |
| v3 | TP8 | TRTLLM PER-TOKEN | 4096 | 475.235 | 477.923 | 478.291 | 475.203 | -0.604% | 0.007% | 0.077% | 0/0 |
| v41-flash | TP4 | TRTLLM PER-TOKEN | 32 | 150.913 | 150.961 | 150.769 | 150.721 | -0.032% | 0.127% | 0.127% | 0/0 |
| v41-flash | TP4 | TRTLLM PER-TOKEN | 4096 | 512.532 | 514.788 | 514.420 | 512.150 | -0.440% | 0.075% | 0.072% | 0/0 |
