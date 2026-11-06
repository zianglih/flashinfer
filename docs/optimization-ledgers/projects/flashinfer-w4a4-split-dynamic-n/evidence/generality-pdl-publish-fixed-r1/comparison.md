# Publication-owner reversed fixed-tactic diagnostic

One A2 then C2 per model on the same GPU, both using exact saved A1 tactics without retuning; 27 medians per arm. Initial NV activation quantization included. W4A16 unchanged as a control. Separate fixed-tactic diagnostic, not a native AUTO retention campaign or TRT comparison.

| Model | Backend | Tokens | Control us | Candidate us | C/A | Same tactic |
|---|---|---:|---:|---:|---:|---|
| v3 | CuteDSL W4A4 | 4 | 47.872 | 47.104 | 1.016315 | True |
| v3 | CuteDSL PER-TOKEN | 4 | 51.776 | 50.977 | 1.015674 | True |
| v3 | CuteDSL W4A16 | 4 | 54.609 | 54.688 | 0.998546 | True |
| v3 | CuteDSL W4A4 | 128 | 137.713 | 137.186 | 1.003845 | True |
| v3 | CuteDSL PER-TOKEN | 128 | 144.993 | 144.769 | 1.001547 | True |
| v3 | CuteDSL W4A16 | 128 | 148.498 | 148.305 | 1.001301 | True |
| v3 | CuteDSL W4A4 | 4096 | 208.082 | 207.362 | 1.003472 | True |
| v3 | CuteDSL PER-TOKEN | 4096 | 296.483 | 296.099 | 1.001297 | True |
| v3 | CuteDSL W4A16 | 4096 | 321.892 | 321.972 | 0.999753 | True |
| v41-flash | CuteDSL W4A4 | 4 | 36.512 | 36.208 | 1.008396 | True |
| v41-flash | CuteDSL PER-TOKEN | 4 | 40.976 | 40.704 | 1.006670 | True |
| v41-flash | CuteDSL W4A16 | 4 | 41.520 | 41.488 | 1.000771 | True |
| v41-flash | CuteDSL W4A4 | 128 | 267.458 | 267.298 | 1.000597 | True |
| v41-flash | CuteDSL PER-TOKEN | 128 | 278.994 | 279.969 | 0.996516 | True |
| v41-flash | CuteDSL W4A16 | 128 | 279.377 | 279.763 | 0.998624 | True |
| v41-flash | CuteDSL W4A4 | 4096 | 353.651 | 353.603 | 1.000137 | True |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 451.731 | 452.612 | 0.998054 | True |
| v41-flash | CuteDSL W4A16 | 4096 | 572.148 | 562.756 | 1.016690 | True |
| kimi-k3 | CuteDSL W4A4 | 4 | 53.665 | 53.073 | 1.011145 | True |
| kimi-k3 | CuteDSL PER-TOKEN | 4 | 60.512 | 59.953 | 1.009332 | True |
| kimi-k3 | CuteDSL W4A16 | 4 | 60.145 | 60.096 | 1.000799 | True |
| kimi-k3 | CuteDSL W4A4 | 128 | 300.065 | 299.827 | 1.000797 | True |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 316.578 | 317.410 | 0.997380 | True |
| kimi-k3 | CuteDSL W4A16 | 128 | 317.762 | 316.322 | 1.004554 | True |
| kimi-k3 | CuteDSL W4A4 | 4096 | 391.875 | 394.259 | 0.993954 | True |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 557.508 | 560.964 | 0.993840 | True |
| kimi-k3 | CuteDSL W4A16 | 4096 | 650.564 | 630.869 | 1.031220 | True |

| Model | Backend | Decode C/A | Prefill C/A | All C/A |
|---|---|---:|---:|---:|
| v3 | CuteDSL W4A4 | 1.010061 | 1.003472 | 1.007860 |
| v3 | CuteDSL PER-TOKEN | 1.008586 | 1.001297 | 1.006150 |
| v3 | CuteDSL W4A16 | 0.999923 | 0.999753 | 0.999866 |
| v41-flash | CuteDSL W4A4 | 1.004489 | 1.000137 | 1.003036 |
| v41-flash | CuteDSL PER-TOKEN | 1.001580 | 0.998054 | 1.000403 |
| v41-flash | CuteDSL W4A16 | 0.999697 | 1.016690 | 1.005330 |
| kimi-k3 | CuteDSL W4A4 | 1.005958 | 0.993954 | 1.001941 |
| kimi-k3 | CuteDSL PER-TOKEN | 1.003339 | 0.993840 | 1.000162 |
| kimi-k3 | CuteDSL W4A16 | 1.002675 | 1.031220 | 1.012101 |
