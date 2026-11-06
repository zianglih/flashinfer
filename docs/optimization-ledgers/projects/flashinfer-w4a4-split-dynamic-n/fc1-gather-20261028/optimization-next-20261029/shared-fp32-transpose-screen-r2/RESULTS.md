# Shared FP32 transpose R2: rejected

The 24-cell source-paired screen regressed **1.638% overall**, with decode **+0.152%**, prefill **−2.898%**, and **18 negative cells**. All 9,600 strict CUPTI samples, source/route/tactic bindings and 192 zero-local native runtime guards passed. Independent raw replay agrees. No rows or noisy phases were replaced.

The scratch/stage tradeoff is not the sole cause. The predeclared eight stage-loss cells average −0.574% E2E and −0.801% FC1; the 16 unchanged-stage cells average −2.166% E2E and −4.390% FC1. Tight unchanged-stage examples include N3U EP16K W4A4 (−8.609% E2E, −15.014% FC1), V41F TP16K W4A4 (−8.176%, −17.841%), and N3U TP16K per-token (−3.043%, −9.024%). These groups are descriptive, not an isolated causal test of stage count. Merely recovering stages with smaller scratch is not sufficient evidence for another version.

The mechanism moved the TMEM transpose to warp-private shared FP32 scratch (8,704 bytes for FC1), adding shared exchanges/synchronization and changing storage planning. Synthetic M512/K8 hot-MMA stores decreased, but local traffic moved into common roles and polling paths. Native timed cases were all zero-local; the broad native losses remain independent of the synthetic spill-site tradeoff.

- Control: retained b52, kernel d7c17adf; candidate f5b7124b. Only the swap kernel differs among 514 bound source files. FC2 source/planner remains unchanged but its duration can change under PDL overlap.
- Method: same-physical-GPU C-A-A-C, fixed native winners/routes, 100 strict CUPTI samples per phase, cold-L2 graph replay, NV input quantizer included. Arm estimates and per-FC estimates are geometric means of the two phase medians. Concurrent FC durations must not be summed to reconstruct E2E.
- Qualification: all 41 existing exact cases passed. Source-bound expected planner and two inherited synthetic resource exceptions are explicit in [qualification](../shared-fp32-transpose-b52-r2/QUALIFICATION.md); original failed guards are preserved. These exceptions are not admitted to performance runs.
- Stock clocks were unchanged. Observed quartile medians range 1,402–2,032 MHz with reasons0/4; one of384 short clock windows has no NVML sample. Maximum E2E phase spreads are8.799%/6.249%, chiefly noisy prefill; the tight losses above have both spreads below0.2%. No sanitizer or retune.
- GPUs4/5 were checked idle after all12 jobs; worker descendants and compute processes are absent in `idle-release.json`.

## Predeclared stage groups and all rows

| Group | Cells | Negative | E2E | FC1 | FC2 |
|---|---:|---:|---:|---:|---:|
| stage_loss | 8 | 5 | -0.574% | -0.801% | +0.119% |
| unchanged_stages | 16 | 13 | -2.166% | -4.390% | -1.347% |

| Job | Tokens | Stages | E2E | FC1 | FC2 | C/A E2E spread |
|---|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp | 16384 | 9→8 | -1.894% | -3.032% | -0.101% | 5.207/5.229% |
| ep-kimi-k3-per-token | 8 | 5→4 | +0.338% | +0.530% | +0.073% | 0.115/0.135% |
| ep-kimi-k3-per-token | 4096 | 4→3 | -0.140% | -0.497% | +0.202% | 0.000/0.089% |
| ep-kimi-k3-per-token | 16384 | 2→2 | -4.602% | -7.739% | -0.494% | 0.055/1.388% |
| ep-nemo3-ultra-mxfp | 8 | 10→10 | -0.194% | -0.023% | +0.221% | 0.320/0.205% |
| ep-nemo3-ultra-mxfp | 16384 | 3→3 | -0.331% | -1.776% | -0.251% | 3.073/1.450% |
| ep-nemo3-ultra-w4a4 | 8 | 5→4 | +1.099% | +0.830% | +1.319% | 0.099/0.070% |
| ep-nemo3-ultra-w4a4 | 16384 | 4→4 | -8.609% | -15.014% | -2.683% | 0.180/0.082% |
| ep-v3-mxfp | 8 | 5→5 | -0.018% | -0.027% | -0.635% | 0.145/0.037% |
| ep-v3-mxfp | 16384 | 5→5 | -2.926% | -2.387% | -2.168% | 8.799/6.249% |
| ep-v41-flash-mxfp | 8 | 11→11 | +0.144% | +0.139% | -0.772% | 0.193/0.032% |
| ep-v41-flash-mxfp | 16384 | 5→5 | -1.911% | -2.835% | -4.061% | 1.558/0.840% |
| tp-kimi-k3-mxfp | 8 | 10→10 | -0.281% | +0.091% | +0.000% | 0.101/0.060% |
| tp-kimi-k3-mxfp | 16384 | 9→8 | -3.440% | -3.132% | -4.818% | 4.406/1.021% |
| tp-nemo3-ultra-per-token | 8 | 5→4 | +0.503% | +1.447% | +0.171% | 0.351/0.101% |
| tp-nemo3-ultra-per-token | 16384 | 4→4 | -3.043% | -9.024% | -0.311% | 0.073/0.171% |
| tp-nemo3-ultra-w4a4 | 8 | 9→9 | +0.107% | +0.052% | -0.170% | 0.296/0.028% |
| tp-nemo3-ultra-w4a4 | 4096 | 2→2 | -4.056% | -10.769% | -2.392% | 0.208/0.012% |
| tp-v3-mxfp | 8 | 10→10 | -0.045% | +0.107% | -0.470% | 0.113/0.069% |
| tp-v3-mxfp | 16384 | 3→3 | +0.072% | +0.147% | -0.095% | 0.593/0.079% |
| tp-v3-w4a4 | 4096 | 4→3 | -0.217% | -0.650% | +4.256% | 0.112/0.074% |
| tp-v41-flash-w4a4 | 8 | 4→4 | -0.120% | -0.406% | -0.299% | 0.214/0.275% |
| tp-v41-flash-w4a4 | 4096 | 4→3 | -0.760% | -1.798% | +0.069% | 0.030/0.057% |
| tp-v41-flash-w4a4 | 16384 | 5→5 | -8.176% | -17.841% | -6.703% | 0.025/0.044% |

## Complete raw phase medians

| Job | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | E2E Δ | FC1 Δ | FC2 Δ | C/A spread |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp | 16384 | 1053.928 | 1021.000 | 1074.393 | 1001.768 | -1.894% | -3.032% | -0.101% | 5.207/5.229% |
| ep-kimi-k3-per-token | 8 | 83.169 | 82.881 | 82.993 | 83.265 | +0.338% | +0.530% | +0.073% | 0.115/0.135% |
| ep-kimi-k3-per-token | 4096 | 449.477 | 450.309 | 449.909 | 449.478 | -0.140% | -0.497% | +0.202% | 0.000/0.089% |
| ep-kimi-k3-per-token | 16384 | 1029.243 | 1071.772 | 1086.653 | 1029.804 | -4.602% | -7.739% | -0.494% | 0.055/1.388% |
| ep-nemo3-ultra-mxfp | 8 | 70.385 | 70.481 | 70.337 | 70.160 | -0.194% | -0.023% | +0.221% | 0.320/0.205% |
| ep-nemo3-ultra-mxfp | 16384 | 884.970 | 868.298 | 880.890 | 858.586 | -0.331% | -1.776% | -0.251% | 3.073/1.450% |
| ep-nemo3-ultra-w4a4 | 8 | 47.889 | 47.361 | 47.328 | 47.841 | +1.099% | +0.830% | +1.319% | 0.099/0.070% |
| ep-nemo3-ultra-w4a4 | 16384 | 588.758 | 644.535 | 645.063 | 589.815 | -8.609% | -15.014% | -2.683% | 0.180/0.082% |
| ep-v3-mxfp | 8 | 88.417 | 88.353 | 88.386 | 88.289 | -0.018% | -0.027% | -0.635% | 0.145/0.037% |
| ep-v3-mxfp | 16384 | 701.753 | 731.528 | 777.243 | 763.497 | -2.926% | -2.387% | -2.168% | 8.799/6.249% |
| ep-v41-flash-mxfp | 8 | 49.888 | 49.761 | 49.776 | 49.792 | +0.144% | +0.139% | -0.772% | 0.193/0.032% |
| ep-v41-flash-mxfp | 16384 | 818.762 | 824.825 | 831.754 | 806.201 | -1.911% | -2.835% | -4.061% | 1.558/0.840% |
| tp-kimi-k3-mxfp | 8 | 79.377 | 79.665 | 79.617 | 79.457 | -0.281% | +0.091% | +0.000% | 0.101/0.060% |
| tp-kimi-k3-mxfp | 16384 | 1551.789 | 1633.774 | 1650.462 | 1620.158 | -3.440% | -3.132% | -4.818% | 4.406/1.021% |
| tp-nemo3-ultra-per-token | 8 | 63.793 | 63.552 | 63.617 | 64.017 | +0.503% | +1.447% | +0.171% | 0.351/0.101% |
| tp-nemo3-ultra-per-token | 16384 | 1801.758 | 1859.215 | 1856.047 | 1800.448 | -3.043% | -9.024% | -0.311% | 0.073/0.171% |
| tp-nemo3-ultra-w4a4 | 8 | 59.504 | 59.537 | 59.520 | 59.680 | +0.107% | +0.052% | -0.170% | 0.296/0.028% |
| tp-nemo3-ultra-w4a4 | 4096 | 377.748 | 393.284 | 393.331 | 376.963 | -4.056% | -10.769% | -2.392% | 0.208/0.012% |
| tp-v3-mxfp | 8 | 71.184 | 71.152 | 71.201 | 71.104 | -0.045% | +0.107% | -0.470% | 0.113/0.069% |
| tp-v3-mxfp | 16384 | 1346.796 | 1342.379 | 1341.323 | 1338.859 | +0.072% | +0.147% | -0.095% | 0.593/0.079% |
| tp-v3-w4a4 | 4096 | 386.533 | 387.732 | 387.445 | 386.964 | -0.217% | -0.650% | +4.256% | 0.112/0.074% |
| tp-v41-flash-w4a4 | 8 | 52.481 | 52.560 | 52.416 | 52.369 | -0.120% | -0.406% | -0.299% | 0.214/0.275% |
| tp-v41-flash-w4a4 | 4096 | 420.803 | 423.971 | 424.211 | 420.931 | -0.760% | -1.798% | +0.069% | 0.030/0.057% |
| tp-v41-flash-w4a4 | 16384 | 1042.568 | 1135.289 | 1135.784 | 1042.824 | -8.176% | -17.841% | -6.703% | 0.025/0.044% |
