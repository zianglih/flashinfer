# Ternary absmax bounded performance screen

Frozen abd55f60 ternary absmax versus retained b139; only _absmax changes.

Decision pending the separately reported bounded N3U repeat. All predeclared cells are preserved; no retuning, clocks, or post-result source changes.

44/44 cells complete. Same-GPU C-A-A-C, 100 strict CUPTI samples/phase, cold L2 and frozen routes/tactics. Percent is control/candidate minus one; positive is faster.

| Job | Tokens | Backend | C1 us | A1 us | A2 us | C2 us | Speedup | C/A spread |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| ep-nemo3-ultra-w4a4 | 8 | CuteDSL W4A4 | 47.312 | 47.248 | 47.633 | 47.312 | -0.269% | 0.000% / 0.813% |
| ep-nemo3-ultra-w4a4 | 16384 | CuteDSL W4A4 | 588.963 | 588.179 | 587.315 | 589.396 | +0.244% | 0.073% / 0.147% |
| ep-nemo3-ultra-per-token | 16384 | CuteDSL PER-TOKEN | 913.945 | 912.632 | 912.808 | 913.320 | +0.100% | 0.068% / 0.019% |
| ep-kimi-k3-w4a4 | 8 | CuteDSL W4A4 | 78.561 | 78.561 | 78.561 | 78.608 | +0.030% | 0.060% / 0.001% |
| ep-kimi-k3-w4a4 | 16384 | CuteDSL W4A4 | 808.996 | 795.653 | 790.644 | 805.495 | +1.778% | 0.435% / 0.634% |
| ep-kimi-k3-per-token | 16384 | CuteDSL PER-TOKEN | 1018.534 | 1020.791 | 1025.686 | 1053.254 | +1.223% | 3.409% / 0.480% |
| ep-nemo3-ultra-mxfp | 8 | CuteDSL MXFP4x8 | 46.800 | 46.689 | 46.832 | 46.785 | +0.069% | 0.034% / 0.308% |
| ep-nemo3-ultra-mxfp | 8 | CuteDSL MXFP8 | 70.112 | 70.177 | 70.081 | 69.984 | -0.115% | 0.184% / 0.137% |
| ep-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | 744.774 | 764.662 | 779.318 | 744.038 | -3.569% | 0.099% / 1.917% |
| ep-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP8 | 837.238 | 871.479 | 831.671 | 848.151 | -1.018% | 1.303% / 4.786% |
| ep-v3-mxfp | 8 | CuteDSL MXFP4x8 | 56.352 | 56.256 | 56.145 | 56.273 | +0.200% | 0.142% / 0.199% |
| ep-v3-mxfp | 8 | CuteDSL MXFP8 | 89.073 | 89.024 | 89.024 | 88.977 | +0.001% | 0.108% / 0.000% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP4x8 | 656.772 | 676.516 | 638.467 | 679.444 | +1.643% | 3.452% / 5.959% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP8 | 721.156 | 709.011 | 722.581 | 728.372 | +1.256% | 1.001% / 1.914% |
| ep-kimi-k3-mxfp | 8 | CuteDSL MXFP4x8 | 76.385 | 76.145 | 76.224 | 76.081 | +0.063% | 0.400% / 0.104% |
| ep-kimi-k3-mxfp | 16384 | CuteDSL MXFP4x8 | 1030.569 | 1018.168 | 1026.409 | 1010.153 | -0.193% | 2.021% / 0.809% |
| ep-v41-flash-w4a4 | 8 | CuteDSL W4A4 | 44.608 | 44.480 | 44.656 | 44.640 | +0.126% | 0.072% / 0.396% |
| ep-v41-flash-w4a4 | 16384 | CuteDSL W4A4 | 610.004 | 602.899 | 602.851 | 605.028 | +0.769% | 0.822% / 0.008% |
| tp-v41-flash-w4a4 | 8 | CuteDSL W4A4 | 52.129 | 52.288 | 52.096 | 52.257 | +0.001% | 0.245% / 0.369% |
| tp-v41-flash-w4a4 | 16384 | CuteDSL W4A4 | 1040.010 | 1039.992 | 1040.026 | 1039.978 | -0.001% | 0.003% / 0.003% |
| tp-v41-flash-per-token | 16384 | CuteDSL PER-TOKEN | 1266.411 | 1266.299 | 1266.203 | 1266.346 | +0.010% | 0.005% / 0.008% |
| tp-v3-w4a4 | 8 | CuteDSL W4A4 | 49.873 | 50.016 | 50.016 | 49.937 | -0.223% | 0.128% / 0.001% |
| tp-v3-w4a4 | 16384 | CuteDSL W4A4 | 1093.207 | 1093.030 | 1092.903 | 1093.447 | +0.033% | 0.022% / 0.012% |
| tp-v3-per-token | 16384 | CuteDSL PER-TOKEN | 1392.280 | 1391.816 | 1392.009 | 1391.992 | +0.016% | 0.021% / 0.014% |
| ep-v41-flash-mxfp | 8 | CuteDSL MXFP4x8 | 49.248 | 49.217 | 49.217 | 49.104 | -0.083% | 0.293% / 0.000% |
| ep-v41-flash-mxfp | 8 | CuteDSL MXFP8 | 72.609 | 72.369 | 72.433 | 72.209 | +0.010% | 0.554% / 0.088% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP4x8 | 773.655 | 789.111 | 790.503 | 803.655 | -0.164% | 3.878% / 0.176% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP8 | 917.544 | 898.040 | 902.440 | 928.792 | +2.545% | 1.226% / 0.490% |
| tp-kimi-k3-mxfp | 8 | CuteDSL MXFP4x8 | 79.233 | 79.169 | 79.201 | 79.169 | +0.020% | 0.081% / 0.040% |
| tp-kimi-k3-mxfp | 16384 | CuteDSL MXFP4x8 | 1606.478 | 1604.637 | 1594.093 | 1597.071 | +0.151% | 0.589% / 0.661% |
| tp-nemo3-ultra-w4a4 | 8 | CuteDSL W4A4 | 59.201 | 59.120 | 59.281 | 59.232 | +0.027% | 0.052% / 0.271% |
| tp-nemo3-ultra-w4a4 | 16384 | CuteDSL W4A4 | 1182.407 | 1183.175 | 1183.207 | 1182.392 | -0.067% | 0.001% / 0.003% |
| ep-v3-w4a4 | 8 | CuteDSL W4A4 | 57.377 | 57.392 | 57.345 | 57.408 | +0.042% | 0.055% / 0.083% |
| ep-v3-w4a4 | 16384 | CuteDSL W4A4 | 516.804 | 517.844 | 516.740 | 517.284 | -0.048% | 0.093% / 0.214% |
| tp-kimi-k3-w4a4 | 8 | CuteDSL W4A4 | 76.992 | 76.832 | 76.960 | 76.641 | -0.104% | 0.458% / 0.167% |
| tp-kimi-k3-w4a4 | 16384 | CuteDSL W4A4 | 1406.776 | 1406.744 | 1398.024 | 1408.409 | +0.372% | 0.116% / 0.624% |
| tp-nemo3-ultra-mxfp | 8 | CuteDSL MXFP4x8 | 59.136 | 59.200 | 59.216 | 59.361 | +0.068% | 0.379% / 0.028% |
| tp-nemo3-ultra-mxfp | 8 | CuteDSL MXFP8 | 85.248 | 85.345 | 85.312 | 85.264 | -0.084% | 0.019% / 0.038% |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | 1240.807 | 1237.655 | 1252.040 | 1255.047 | +0.247% | 1.148% / 1.162% |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP8 | 1325.703 | 1331.416 | 1314.552 | 1327.912 | +0.291% | 0.167% / 1.283% |
| tp-v3-mxfp | 8 | CuteDSL MXFP4x8 | 50.032 | 50.160 | 50.096 | 50.113 | -0.111% | 0.161% / 0.127% |
| tp-v3-mxfp | 8 | CuteDSL MXFP8 | 70.561 | 70.529 | 70.673 | 70.496 | -0.103% | 0.092% / 0.204% |
| tp-v3-mxfp | 16384 | CuteDSL MXFP4x8 | 1233.403 | 1222.218 | 1232.091 | 1232.682 | +0.481% | 0.058% / 0.808% |
| tp-v3-mxfp | 16384 | CuteDSL MXFP8 | 1327.979 | 1327.436 | 1330.284 | 1332.188 | +0.092% | 0.317% / 0.215% |

Source and numerical qualification: `../swap-absmax-ternary-b139/QUALIFICATION.md`. Components, sample quartiles and clock timelines remain in each result analysis. Higher-spread cases are not used to claim causality.
