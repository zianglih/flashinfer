# Pre-wait expert-alpha reuse — rejected

The single frozen 56-cell C–A–A–C screen is **−0.215899% overall**, **−0.056295% decode**, and **−0.375248% prefill**, with **26 negative cells**. The parent rejected this candidate: several TP per-token losses are tight and substantial, and NVFP4 prefills also regress. Source-level brevity and representative instruction reduction do not justify retention against these measurements. No repeat, matrix expansion, selective replacement, or shape-specific rescue is planned.

- **Source:** measured control `c1ac8ce7341039db65195b99445fcdeb193cf226`; candidate swap SHA `2a6968117f2ab22bee751357667cc1dbb0edeb1f41f4a99c7112f588fc1310fd`. The change moves one existing expert-alpha load before the accumulator wait and reuses it. This is distinct from the earlier rejected post-wait alpha reuse. No production commit was made.
- **Native/exact gate:** 20 exact arm results / 30 native pairs (12 fresh calls, eight source/runtime-qualified controls), LOCAL0 and no representative occupancy/register loss. Four pilot GEMMs show actual alpha LDG motion before the wait. Preserve the W4A4 case14 FC1 +1 non-NOP exception. Gate `qualification-summary-combined.json` SHA `c04d8b71ece7f2dd6594b432ef399eec9a62a96553bb33d67da0be5907e3139a`.
- **Timing:** unchanged 23 jobs / 28 supported swap and per-token arms at T32/T16384; 100 strict CUPTI samples, 10 warmups, cold-L2 CUDA Graph replay; input quantization included. Same recorded choices/routes, no autotuning. Speedup is geometric mean of the two control phase medians divided by geometric mean of the two candidate medians, minus one.
- **Closure:** all 22,400 samples / 224 phase medians retained; both 13,245-file inventories and release ELF/Ninja byte checks pass. Runtime guards accepted all 448 native resource records with zero local memory. The measured 112 paired compilation sequences include 13 FC2 resource changes, including four register increases—qualification’s no-growth statement is representative, not a full-matrix guarantee. All actual changes are below.
- **Clock boundary:** 896 quartile windows, 58 exceptions and one missing window retained. The missing sample is V3 TP W4A4 T16384, second candidate phase, fourth quartile. Large EP MX moves have clock/repeat variation and are not labeled isolated causal regressions. All GPUs0/1/4/5 were checked idle and released; persistent caches are unchanged.

The tight TP per-token losses primarily extend FC2 after FC1: K3 T32 +3.808 µs, V3 T32 +2.504 µs, N3U T16384 +35.824 µs and V3 T16384 +44.801 µs, while their FC1 extensions improve slightly. K3 T16384 has both FC1 +12.425 µs and FC2 extension +11.824 µs. These are observed component differences, not proof of a particular scheduling or register-pressure cause.

Raw bundle: `../../evidence/alpha-prefetch-screen/1793397894372465000/`, archive SHA `3b9c4d9e3c8709314805f05bfbbd0338e52864eb886d0861f44a212f35539a83`. Config SHA `9054f1221dec38fbbaaa2c34e8b1298f4b9acd0dac1472e5931d3abced1c6182`. The report retains complete phase medians, raw samples, component timelines, clocks and resource records. Independent peer receipts are additive under `audits/`.

## Every negative cell

C/A spread is `(max phase median / min phase median − 1) × 100`. Clock flags count exceptions among 16 quartiles; missing observations are separate. These are descriptive repeat/telemetry checks, not confidence intervals. Component extensions account for overlap; do not sum overlapping kernel durations.

| Model | Topology | Mode | Tokens | C1 / A1 / A2 / C2 µs | Speedup | C/A spread | Clock flags; missing | FC1 extension Δ µs | FC2-after-FC1 Δ µs |
|---|---|---|---:|---|---:|---|---|---:|---:|
| kimi-k3 | EP | MXFP4x8 | 16384 | 1082.327 / 1055.863 / 1076.551 / 1047.320 | -0.138577% | 3.343% / 1.959% | 5; 0 | +0.863 | +0.849 |
| kimi-k3 | EP | PER-TOKEN | 32 | 180.434 / 180.450 / 180.738 / 180.545 | -0.057699% | 0.062% / 0.159% | 0; 0 | -0.008 | +0.072 |
| kimi-k3 | EP | W4A4 | 16384 | 839.047 / 836.375 / 846.247 / 842.615 | -0.055559% | 0.425% / 1.180% | 0; 0 | -0.192 | -0.392 |
| nemo3-ultra | EP | MXFP4x8 | 32 | 100.624 / 100.657 / 100.642 / 100.641 | -0.016642% | 0.017% / 0.015% | 0; 0 | +0.080 | -0.000 |
| nemo3-ultra | EP | MXFP8 | 32 | 168.498 / 168.674 / 168.769 / 168.418 | -0.156469% | 0.047% / 0.057% | 0; 0 | +0.120 | +0.032 |
| nemo3-ultra | EP | MXFP4x8 | 16384 | 737.640 / 777.192 / 743.063 / 722.008 | -3.968003% | 2.165% / 4.593% | 0; 0 | +12.632 | +14.608 |
| nemo3-ultra | EP | PER-TOKEN | 32 | 109.889 / 110.177 / 110.161 / 110.049 | -0.181565% | 0.146% / 0.015% | 0; 0 | -0.016 | +0.024 |
| nemo3-ultra | EP | PER-TOKEN | 16384 | 951.910 / 953.639 / 954.455 / 951.479 | -0.246548% | 0.045% / 0.086% | 0; 0 | +2.040 | +0.256 |
| nemo3-ultra | EP | W4A4 | 16384 | 558.468 / 563.940 / 564.357 / 558.581 | -0.996850% | 0.020% / 0.074% | 1; 0 | +5.480 | +0.336 |
| v3 | EP | MXFP8 | 32 | 163.490 / 163.649 / 163.537 / 163.505 | -0.058829% | 0.009% / 0.068% | 0; 0 | +0.056 | -0.024 |
| v3 | EP | MXFP8 | 16384 | 713.813 / 780.534 / 746.198 / 716.870 | -6.267686% | 0.428% / 4.602% | 1; 0 | +18.256 | +14.344 |
| v3 | EP | W4A4 | 32 | 99.553 / 99.680 / 99.681 / 99.617 | -0.096313% | 0.064% / 0.001% | 0; 0 | -0.008 | +0.056 |
| v41-flash | EP | MXFP4x8 | 16384 | 827.622 / 844.086 / 832.615 / 839.367 | -0.579344% | 1.419% / 1.378% | 4; 0 | +5.840 | +0.152 |
| v41-flash | EP | PER-TOKEN | 32 | 130.369 / 130.337 / 130.417 / 130.369 | -0.006323% | 0.000% / 0.062% | 0; 0 | -0.120 | +0.024 |
| kimi-k3 | TP | PER-TOKEN | 32 | 178.145 / 181.905 / 181.777 / 178.129 | -2.037073% | 0.009% / 0.071% | 0; 0 | -0.136 | +3.808 |
| kimi-k3 | TP | PER-TOKEN | 16384 | 1947.472 / 1970.448 / 1970.977 / 1944.656 | -1.250778% | 0.145% / 0.027% | 0; 0 | +12.425 | +11.824 |
| kimi-k3 | TP | W4A4 | 16384 | 1414.444 / 1421.691 / 1423.053 / 1404.364 | -0.912339% | 0.718% / 0.096% | 3; 0 | +2.024 | +9.072 |
| nemo3-ultra | TP | MXFP4x8 | 16384 | 1194.829 / 1192.541 / 1204.029 / 1194.142 | -0.315979% | 0.058% / 0.963% | 4; 0 | +1.832 | +0.544 |
| nemo3-ultra | TP | PER-TOKEN | 16384 | 1800.509 / 1835.293 / 1836.380 / 1799.852 | -1.942232% | 0.037% / 0.059% | 0; 0 | -0.272 | +35.824 |
| nemo3-ultra | TP | W4A4 | 16384 | 1134.938 / 1144.778 / 1145.385 / 1136.057 | -0.837001% | 0.099% / 0.053% | 0; 0 | +0.736 | +9.152 |
| v3 | TP | MXFP4x8 | 16384 | 1247.851 / 1250.235 / 1252.650 / 1246.811 | -0.328523% | 0.083% / 0.193% | 3; 0 | -1.361 | +5.887 |
| v3 | TP | MXFP8 | 16384 | 1356.588 / 1366.012 / 1356.939 / 1354.699 | -0.427849% | 0.139% / 0.669% | 6; 0 | -3.024 | +7.503 |
| v3 | TP | PER-TOKEN | 32 | 116.161 / 118.401 / 118.353 / 116.097 | -1.899226% | 0.055% / 0.040% | 0; 0 | -0.088 | +2.504 |
| v3 | TP | PER-TOKEN | 16384 | 1395.855 / 1438.768 / 1438.992 / 1395.695 | -2.995716% | 0.011% / 0.016% | 0; 0 | -1.632 | +44.801 |
| v3 | TP | W4A4 | 16384 | 1092.871 / 1095.544 / 1095.367 / 1092.919 | -0.233738% | 0.004% / 0.016% | 0; 1 | -0.368 | +2.816 |
| v41-flash | TP | PER-TOKEN | 32 | 144.977 / 145.153 / 145.137 / 144.930 | -0.132282% | 0.033% / 0.011% | 0; 0 | +0.160 | +0.048 |

## Actual paired resource changes

All are FC2, with LOCAL0. Compilation index is the original returned-native sequence position, not an inferred token identity. Runtime resource/occupancy checks remain intact; peer cell/config joins are separate.

| Job | Compilation index | Changed native fields, control → candidate |
|---|---:|---|
| ep-kimi-k3-per-token | 3 | initial_regs: 105 → 103 |
| ep-kimi-k3-w4a4 | 3 | initial_regs: 82 → 80; max_threads: 640 → 768 |
| ep-nemo3-ultra-per-token | 1 | initial_regs: 88 → 90 |
| ep-v41-flash-per-token | 1 | initial_regs: 88 → 90 |
| tp-kimi-k3-mxfp | 1 | initial_regs: 80 → 79 |
| tp-kimi-k3-per-token | 1 | initial_regs: 108 → 106 |
| tp-kimi-k3-w4a4 | 1 | initial_regs: 88 → 87 |
| tp-nemo3-ultra-per-token | 1 | initial_regs: 92 → 94 |
| tp-nemo3-ultra-w4a4 | 1 | initial_regs: 76 → 74 |
| tp-v3-mxfp | 1 | initial_regs: 80 → 79 |
| tp-v3-mxfp | 3 | initial_regs: 80 → 79 |
| tp-v3-w4a4 | 1 | initial_regs: 88 → 86 |
| tp-v41-flash-w4a4 | 1 | initial_regs: 71 → 72 |

## Complete matrix

| Model | EP/TP | Mode | 32 | 16384 |
|---|---|---|---:|---:|
| kimi-k3 | EP8 | CuteDSL MXFP4x8 | +0.096% | -0.139% |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | -0.058% | +3.651% |
| kimi-k3 | EP8 | CuteDSL W4A4 | +0.069% | -0.056% |
| kimi-k3 | TP8 | CuteDSL MXFP4x8 | +0.086% | +0.151% |
| kimi-k3 | TP8 | CuteDSL PER-TOKEN | -2.037% | -1.251% |
| kimi-k3 | TP8 | CuteDSL W4A4 | +0.096% | -0.912% |
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | -0.017% | -3.968% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | -0.156% | +0.775% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | -0.182% | -0.247% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | +0.039% | -0.997% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | +0.097% | -0.316% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | +0.026% | +0.490% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | +0.059% | -1.942% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | +0.200% | -0.837% |
| v3 | EP8 | CuteDSL MXFP4x8 | +0.198% | +0.557% |
| v3 | EP8 | CuteDSL MXFP8 | -0.059% | -6.268% |
| v3 | EP8 | CuteDSL PER-TOKEN | +0.053% | +0.144% |
| v3 | EP8 | CuteDSL W4A4 | -0.096% | +1.207% |
| v3 | TP8 | CuteDSL MXFP4x8 | +0.874% | -0.329% |
| v3 | TP8 | CuteDSL MXFP8 | +0.182% | -0.428% |
| v3 | TP8 | CuteDSL PER-TOKEN | -1.899% | -2.996% |
| v3 | TP8 | CuteDSL W4A4 | +0.341% | -0.234% |
| v41-flash | EP4 | CuteDSL MXFP4x8 | +0.222% | -0.579% |
| v41-flash | EP4 | CuteDSL MXFP8 | +0.163% | +2.020% |
| v41-flash | EP4 | CuteDSL PER-TOKEN | -0.006% | +0.331% |
| v41-flash | EP4 | CuteDSL W4A4 | +0.217% | +2.065% |
| v41-flash | TP4 | CuteDSL PER-TOKEN | -0.132% | +0.044% |
| v41-flash | TP4 | CuteDSL W4A4 | +0.093% | +0.030% |
