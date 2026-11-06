# Rejected: independent raw-A / direct-B stage balancing

Frozen `cf78403f` on retained `ce4a7d8c`, 32 predeclared cells. No commit, no retuning, no shape gates or ad hoc repeats.

The geometric mean of the32 latency ratios is **−6.760%**: decode8 **+0.314%**, middle256 **−4.073%**, prefill4096/16384 **−11.376%**.23/32 rows are negative. The five unchanged N192 controls remain in every table and aggregate.

The proposed logical inventory model was insufficient for performance. It exchanged raw-weight lookahead for direct-B residency; notably A4/B4/D2→A2/B5/D2 leaves `min(B,A+D)` unchanged but cuts the raw-weight queue in half. FC1 durations grow strongly in the affected prefill cases, consistent with a weight/dequant supply starvation tradeoff. This is source/timeline inference, not an NCU stall-counter proof. Do not salvage this policy through model/dtype/tile gates.

At V41F EP/TP4K, FC1 duration grows205.39/225.59us and whole-chain performance drops34.48/33.68%. K3 TP4K growsFC1 by187.54us and drops23.56%. Those windows show2032MHz, clock-reason0 in both arms. At16K, FC2 often becomes faster while FC1 slows, so the general policy is not a universal pipeline improvement. Kernel durations overlap through PDL and must not be summed as E2E.

- Qualification:39 existing exact/graph tests passed;40 numerical kernels LOCAL0.20 native paired compile captures keepREG96/128 and LOCAL0, actual shared memory never grows, N192 binaries match exactly. See QUALIFICATION.md.
- Measurement: all12800 strictCUPTI samples,32 complete C–A–A–C job phases,32 guard receipts/200 loaded functions with LOCAL0; unchanged frozen tactics/routes/7observers, stock clocks, persistent caches, no sanitizer. Per-cell ratio uses arithmetic mean of each arm's two phase medians, matching prior W4 screens.
- Telemetry: all128 cell-phase windows have NVML data;97 windows stay2032MHz. Other windows include stock clock ramping and clock-reason4; no fixed-clock claim. Memory clock3996MHz throughout. Largest control/candidate phase spread4.58/2.22%. The unchanged V3 EP16K+2.11% row has2.50/2.22% spreads and is drift evidence, not an optimization gain.

| Model/topology | Tokens | Control us | Candidate us | Speedup | C/A spread | ΔFC1 us | ΔFC2 us | ΔFC2 exposed after FC1 us |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 8 | 84.033 | 84.537 | -0.596% | 0.535/0.057% | +0.088 | +0.696 | +0.520 |
| ep-kimi-k3-w4a16 | 256 | 348.324 | 368.564 | -5.492% | 0.037/0.165% | +1.352 | +18.945 | +19.192 |
| ep-kimi-k3-w4a16 | 4096 | 572.775 | 756.929 | -24.329% | 4.583/0.137% | +164.370 | +21.649 | +21.657 |
| ep-kimi-k3-w4a16 | 16384 | 1993.232 | 2186.066 | -8.821% | 0.455/0.181% | +231.459 | -35.496 | -35.320 |
| ep-nemo3-ultra-w4a16 | 8 | 51.241 | 50.881 | +0.708% | 0.220/0.250% | +0.024 | -0.112 | -0.376 |
| ep-nemo3-ultra-w4a16 | 256 | 153.906 | 166.490 | -7.559% | 0.062/0.010% | +0.032 | +12.232 | +12.233 |
| ep-nemo3-ultra-w4a16 † | 4096 | 395.589 | 395.508 | +0.020% | 0.284/0.576% | +0.264 | +0.504 | +0.495 |
| ep-nemo3-ultra-w4a16 | 16384 | 1555.155 | 1593.881 | -2.430% | 0.047/1.081% | +89.360 | -45.929 | -45.922 |
| ep-v3-w4a16 | 8 | 69.241 | 69.545 | -0.437% | 0.163/0.023% | -0.327 | +0.784 | +0.335 |
| ep-v3-w4a16 | 256 | 151.938 | 153.962 | -1.315% | 0.105/0.176% | +1.752 | +0.712 | +0.121 |
| ep-v3-w4a16 † | 4096 | 283.787 | 283.700 | +0.031% | 0.107/0.260% | -0.144 | -0.687 | -0.367 |
| ep-v3-w4a16 † | 16384 | 1133.365 | 1109.925 | +2.112% | 2.500/2.217% | -15.096 | -10.849 | -7.816 |
| ep-v41-flash-w4a16 | 8 | 51.313 | 50.624 | +1.361% | 0.124/0.000% | -0.944 | -4.536 | +0.048 |
| ep-v41-flash-w4a16 | 256 | 318.948 | 319.820 | -0.273% | 0.010/0.115% | +0.128 | +0.200 | +0.559 |
| ep-v41-flash-w4a16 | 4096 | 445.749 | 680.320 | -34.480% | 0.627/0.026% | +205.387 | +40.697 | +29.256 |
| ep-v41-flash-w4a16 | 16384 | 1520.666 | 1686.196 | -9.817% | 0.899/0.287% | +213.426 | -36.785 | -36.592 |
| tp-kimi-k3-w4a16 | 8 | 89.153 | 89.041 | +0.126% | 0.288/0.036% | -0.167 | -0.112 | +0.032 |
| tp-kimi-k3-w4a16 | 256 | 393.940 | 394.907 | -0.245% | 0.032/0.012% | +1.560 | -0.864 | -0.960 |
| tp-kimi-k3-w4a16 | 4096 | 701.534 | 917.744 | -23.559% | 0.034/0.065% | +187.537 | +33.769 | +30.728 |
| tp-kimi-k3-w4a16 | 16384 | 2441.300 | 2629.310 | -7.151% | 0.070/0.092% | +272.434 | -69.144 | -67.345 |
| tp-nemo3-ultra-w4a16 | 8 | 65.953 | 65.673 | +0.426% | 0.001/0.024% | -0.160 | -0.056 | -0.032 |
| tp-nemo3-ultra-w4a16 | 256 | 166.002 | 196.202 | -15.392% | 0.116/0.025% | +20.008 | +11.369 | +10.184 |
| tp-nemo3-ultra-w4a16 † | 4096 | 541.604 | 541.516 | +0.016% | 0.065/0.009% | +0.288 | +0.401 | +0.200 |
| tp-nemo3-ultra-w4a16 | 16384 | 1908.398 | 2053.392 | -7.061% | 0.262/0.428% | +116.586 | +37.488 | +36.945 |
| tp-v3-w4a16 | 8 | 57.528 | 56.880 | +1.139% | 0.083/0.169% | -0.656 | -0.808 | +0.056 |
| tp-v3-w4a16 | 256 | 169.210 | 171.025 | -1.062% | 0.180/0.056% | +1.777 | +0.441 | +0.176 |
| tp-v3-w4a16 † | 4096 | 476.204 | 476.540 | -0.071% | 0.037/0.111% | +0.344 | +0.529 | +0.097 |
| tp-v3-w4a16 | 16384 | 1724.870 | 1869.862 | -7.754% | 0.774/0.044% | +232.697 | -72.745 | -73.089 |
| tp-v41-flash-w4a16 | 8 | 63.920 | 64.048 | -0.200% | 0.051/0.151% | -0.039 | +0.048 | -0.032 |
| tp-v41-flash-w4a16 | 256 | 347.595 | 348.051 | -0.131% | 0.051/0.074% | +0.456 | +0.240 | +0.304 |
| tp-v41-flash-w4a16 | 4096 | 549.093 | 827.959 | -33.681% | 0.169/0.043% | +225.586 | +59.329 | +53.224 |
| tp-v41-flash-w4a16 | 16384 | 1874.856 | 2121.899 | -11.643% | 0.085/0.277% | +258.331 | -1.600 | -1.959 |

† N192 stage counts unchanged. Positive speedup means candidate faster; positive component deltas mean candidate slower.

Evidence: `screen-evidence/MANIFEST.json`, `perf-summary.json`, `screen.csv`, `component-summary.json`, `telemetry-summary.json`, source-bound `screen-preparation/plan.json`. Initial harness-only failures and all raw diagnostics remain in `gate-evidence`; neither required a kernel-source change.
