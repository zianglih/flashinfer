# Publication-owner bounded native AUTO screen

One C1 then A1 per model on the same GPU, with native AUTO; 27 medians per arm. Initial NV activation quantization included. W4A16 unchanged as a control. This is a bounded screen, not a retention campaign or TRT comparison.

| Model | Backend | Tokens | Control us | Candidate us | C/A | Same tactic |
|---|---|---:|---:|---:|---:|---|
| v3 | CuteDSL W4A4 | 4 | 47.841 | 47.232 | 1.012894 | True |
| v3 | CuteDSL PER-TOKEN | 4 | 51.697 | 51.088 | 1.011901 | True |
| v3 | CuteDSL W4A16 | 4 | 55.312 | 54.768 | 1.009933 | False |
| v3 | CuteDSL W4A4 | 128 | 137.778 | 137.377 | 1.002919 | True |
| v3 | CuteDSL PER-TOKEN | 128 | 145.122 | 144.721 | 1.002767 | True |
| v3 | CuteDSL W4A16 | 128 | 148.690 | 148.306 | 1.002589 | True |
| v3 | CuteDSL W4A4 | 4096 | 208.562 | 207.251 | 1.006331 | True |
| v3 | CuteDSL PER-TOKEN | 4096 | 296.420 | 296.659 | 0.999196 | True |
| v3 | CuteDSL W4A16 | 4096 | 319.493 | 320.419 | 0.997108 | True |
| v41-flash | CuteDSL W4A4 | 4 | 35.840 | 36.320 | 0.986784 | False |
| v41-flash | CuteDSL PER-TOKEN | 4 | 40.992 | 40.689 | 1.007459 | True |
| v41-flash | CuteDSL W4A16 | 4 | 41.473 | 41.504 | 0.999241 | True |
| v41-flash | CuteDSL W4A4 | 128 | 267.490 | 267.026 | 1.001738 | True |
| v41-flash | CuteDSL PER-TOKEN | 128 | 279.714 | 279.234 | 1.001719 | True |
| v41-flash | CuteDSL W4A16 | 128 | 280.578 | 279.650 | 1.003318 | True |
| v41-flash | CuteDSL W4A4 | 4096 | 354.131 | 353.875 | 1.000722 | True |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 454.483 | 452.083 | 1.005309 | False |
| v41-flash | CuteDSL W4A16 | 4096 | 568.212 | 564.982 | 1.005718 | True |
| kimi-k3 | CuteDSL W4A4 | 4 | 53.952 | 53.392 | 1.010479 | True |
| kimi-k3 | CuteDSL PER-TOKEN | 4 | 60.849 | 60.161 | 1.011436 | True |
| kimi-k3 | CuteDSL W4A16 | 4 | 60.561 | 60.417 | 1.002375 | True |
| kimi-k3 | CuteDSL W4A4 | 128 | 303.842 | 299.602 | 1.014152 | False |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 317.858 | 316.834 | 1.003234 | True |
| kimi-k3 | CuteDSL W4A16 | 128 | 317.634 | 317.747 | 0.999644 | True |
| kimi-k3 | CuteDSL W4A4 | 4096 | 392.307 | 391.043 | 1.003234 | True |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 562.293 | 558.628 | 1.006562 | True |
| kimi-k3 | CuteDSL W4A16 | 4096 | 638.069 | 634.741 | 1.005243 | True |

| Model | Backend | Decode C/A | Prefill C/A | All C/A |
|---|---|---:|---:|---:|
| v3 | CuteDSL W4A4 | 1.007894 | 1.006331 | 1.007373 |
| v3 | CuteDSL PER-TOKEN | 1.007324 | 0.999196 | 1.004607 |
| v3 | CuteDSL W4A16 | 1.006254 | 0.997108 | 1.003196 |
| v41-flash | CuteDSL W4A4 | 0.994233 | 1.000722 | 0.996391 |
| v41-flash | CuteDSL PER-TOKEN | 1.004585 | 1.005309 | 1.004826 |
| v41-flash | CuteDSL W4A16 | 1.001278 | 1.005718 | 1.002756 |
| kimi-k3 | CuteDSL W4A4 | 1.012314 | 1.003234 | 1.009278 |
| kimi-k3 | CuteDSL PER-TOKEN | 1.007326 | 1.006562 | 1.007071 |
| kimi-k3 | CuteDSL W4A16 | 1.001009 | 1.005243 | 1.002418 |
