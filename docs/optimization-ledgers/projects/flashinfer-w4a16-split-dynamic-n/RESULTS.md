# Split CuTe DSL W4A16 dynamic-N results

Before `316faec37a4706a2ecc7d46265087f8190b40baa`; after `9ec90d0696752c72ff826c8880e58515ace84e60`.

NVIDIA B300 SXM6 AC on `hu-pdx-30`, GPU0; Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA runtime `13.2`, CuTe DSL `4.7.1`, CUPTI Python `13.4.0`.

H7168/I2048, 256 global experts, top-k 8, groups 8/top-groups 4, routed scaling 2.5; simulated EP8/TP1, 32 local experts, offset 0. BF16 activations/output and NVFP4 weights. Routing is timed; preparation, autotuning, compilation and inter-GPU communication are excluded.

Each cell is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups. Existing measurements are reused. With one paired repeat, speedup is Before/After; with two, sqrt((Before R1 × Before R2)/(After R1 × After R2)). No row minima, substitutions or pooling of samples. R2 is not required to report existing R1 evidence.

Token/retention policy: [merged #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), merged 2026-10-14T21:52:15Z. Exact grid: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Only T1/T2 are reported-only; T4 is included. Retention uses the 11 remaining points; decode uses T4–512 and prefill uses T4096/T8192/T16384. Existing T1024/T2048 remain supplemental and are outside this grid.

Latest explicit user override: performance retention is UNFUSED ONLY. All measured fused medians and descriptive aggregates are preserved below for transparency; fused performance does not enter retention and requires no further tuning or diagnostic runs.

A missing required point makes that aggregate incomplete; its displayed speedup covers only the explicitly listed available points and cannot stand in for full retention evidence. No universal numeric acceptance threshold is established by #6277. Assess the full pointwise table, decode/prefill behavior and tactic changes. Small mixed gains and tactic selection alone do not establish a useful kernel improvement.

Retention additionally requires repeat consistency and review for fixed-tactic regressions. Normal AUTO evidence alone does not satisfy that check; any fixed-tactic diagnostics remain separate from these primary medians. This report does not automatically accept a candidate based on its aggregate ratio.

Repeat disagreement is 100 × (max(R1,R2)/min(R1,R2)−1). Opposite directions mean one repeat speeds up and the other slows down. One/two sweeps do not establish statistical significance or isolate a fixed-tactic kernel gain.

Validation: 8 complete arm sweeps, 9 source result files, 106 medians/cache hashes; expected commit/source hashes and matching workload/software/histogram summaries. Dtypes are source-derived. The separate environment record supplies GPU UUID, driver and container details.

## Unfused finalize (sole retention target)

Paired repeats available: [1, 2].

- **Full retention grid: 1.020415×**, 11/11 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]; 10 faster / 1 slower.
- **Decode: 1.008383×**, 8/8 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512]; 7 faster / 1 slower.
- **Prefill: 1.053206×**, 3/3 points (complete); available tokens [4096, 8192, 16384]; 3 faster / 0 slower.

| Tokens | Role | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | reported only | 34.2730 | 34.7520 | 34.0160 | 34.0485 | 1.014087× |
| 2 | reported only | 40.3840 | 40.0645 | 39.7925 | 39.6325 | 1.012880× |
| 4 | decode | 54.8640 | 54.9120 | 54.4165 | 53.5050 | 1.017220× |
| 8 | decode | 68.6730 | 69.2005 | 69.7610 | 68.7685 | 0.995283× |
| 16 | decode | 76.8970 | 76.8330 | 76.2880 | 75.7450 | 1.011168× |
| 32 | decode | 109.7130 | 109.9850 | 109.1370 | 108.9290 | 1.007484× |
| 64 | decode | 143.2010 | 143.6820 | 141.9375 | 142.0810 | 1.010084× |
| 128 | decode | 145.8900 | 145.7775 | 144.1300 | 144.6090 | 1.010144× |
| 256 | decode | 152.7530 | 152.4330 | 151.4895 | 151.6810 | 1.006648× |
| 512 | decode | 159.0090 | 157.9055 | 156.9455 | 157.0890 | 1.009165× |
| 1024 | supplemental | 174.8340 | — | — | — | — |
| 2048 | supplemental | 211.6820 | — | — | — | — |
| 4096 | prefill | 308.8670 | 309.3145 | 295.1390 | 294.5150 | 1.048380× |
| 8192 | prefill | 627.3330 | 620.1335 | 573.9090 | 573.5730 | 1.087116× |
| 16384 | prefill | 1183.9945 | 1226.3790 | 1199.2750 | 1152.2980 | 1.025051× |

Repeat disagreement for every row:

| Tokens | Before spread (%) | After spread (%) | R1 speedup | R2 speedup | Speedup spread (%) | Direction |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | 1.3976 | 0.0955 | 1.0076 | 1.0207 | 1.3008 | both faster |
| 2 | 0.7975 | 0.4037 | 1.0149 | 1.0109 | 0.3922 | both faster |
| 4 | 0.0875 | 1.7036 | 1.0082 | 1.0263 | 1.7926 | both faster |
| 8 | 0.7681 | 1.4432 | 0.9844 | 1.0063 | 2.2225 | disagree |
| 16 | 0.0833 | 0.7169 | 1.0080 | 1.0144 | 0.6331 | both faster |
| 32 | 0.2479 | 0.1910 | 1.0053 | 1.0097 | 0.4393 | both faster |
| 64 | 0.3359 | 0.1011 | 1.0089 | 1.0113 | 0.2346 | both faster |
| 128 | 0.0772 | 0.3323 | 1.0122 | 1.0081 | 0.4098 | both faster |
| 256 | 0.2099 | 0.1264 | 1.0083 | 1.0050 | 0.3366 | both faster |
| 512 | 0.6988 | 0.0914 | 1.0131 | 1.0052 | 0.7909 | both faster |
| 1024 | — | — | — | — | — | missing paired data |
| 2048 | — | — | — | — | — | missing paired data |
| 4096 | 0.1449 | 0.2119 | 1.0465 | 1.0503 | 0.3571 | both faster |
| 8192 | 1.1610 | 0.0586 | 1.0931 | 1.0812 | 1.1017 | both faster |
| 16384 | 3.5798 | 4.0768 | 0.9873 | 1.0643 | 7.8025 | disagree |

## Fused finalize (reported only; excluded from retention)

Paired repeats available: [1, 2].

- **Descriptive 11-point grid (not a retention metric): 0.992009×**, 11/11 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]; 6 faster / 5 slower.
- **Decode: 1.004722×**, 8/8 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512]; 6 faster / 2 slower.
- **Prefill: 0.958889×**, 3/3 points (complete); available tokens [4096, 8192, 16384]; 0 faster / 3 slower.

| Tokens | Role | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | reported only | 36.8640 | 36.9600 | 37.3450 | 36.6720 | 0.997433× |
| 2 | reported only | 42.1600 | 42.0170 | 41.9365 | 42.6245 | 0.995490× |
| 4 | decode | 58.3845 | 58.4485 | 58.2245 | 58.2730 | 1.002880× |
| 8 | decode | 73.2970 | 73.4565 | 73.0890 | 74.1610 | 0.996654× |
| 16 | decode | 79.9685 | 82.8490 | 83.1530 | 79.8405 | 0.998970× |
| 32 | decode | 114.4970 | 114.4810 | 113.8570 | 113.7930 | 1.005834× |
| 64 | decode | 148.4495 | 148.2570 | 147.2490 | 147.2170 | 1.007608× |
| 128 | decode | 152.1620 | 152.0655 | 151.3775 | 151.4570 | 1.004600× |
| 256 | decode | 158.9775 | 158.7215 | 158.1935 | 157.7930 | 1.005420× |
| 512 | decode | 164.8970 | 164.7220 | 162.3695 | 162.0810 | 1.015930× |
| 4096 | prefill | 350.3870 | 350.7390 | 366.4835 | 366.5630 | 0.956455× |
| 8192 | prefill | 659.3340 | 667.2220 | 705.6710 | 685.8305 | 0.953407× |
| 16384 | prefill | 1301.8370 | 1295.7555 | 1329.9645 | 1356.7965 | 0.966857× |

Repeat disagreement for every row:

| Tokens | Before spread (%) | After spread (%) | R1 speedup | R2 speedup | Speedup spread (%) | Direction |
| ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | 0.2604 | 1.8352 | 0.9871 | 1.0079 | 2.1004 | disagree |
| 2 | 0.3403 | 1.6406 | 1.0053 | 0.9857 | 1.9865 | disagree |
| 4 | 0.1096 | 0.0833 | 1.0027 | 1.0030 | 0.0263 | both faster |
| 8 | 0.2176 | 1.4667 | 1.0028 | 0.9905 | 1.2464 | disagree |
| 16 | 3.6020 | 4.1489 | 0.9617 | 1.0377 | 7.9004 | disagree |
| 32 | 0.0140 | 0.0562 | 1.0056 | 1.0060 | 0.0423 | both faster |
| 64 | 0.1298 | 0.0217 | 1.0082 | 1.0071 | 0.1081 | both faster |
| 128 | 0.0635 | 0.0525 | 1.0052 | 1.0040 | 0.1160 | both faster |
| 256 | 0.1613 | 0.2538 | 1.0050 | 1.0059 | 0.0924 | both faster |
| 512 | 0.1062 | 0.1780 | 1.0156 | 1.0163 | 0.0717 | both faster |
| 4096 | 0.1005 | 0.0217 | 0.9561 | 0.9568 | 0.0788 | both slower |
| 8192 | 1.1964 | 2.8929 | 0.9343 | 0.9729 | 4.1239 | both slower |
| 16384 | 0.4693 | 2.0175 | 0.9789 | 0.9550 | 2.4963 | both slower |

## Source evidence

| Input | File SHA256 |
| :--- | :--- |
| baseline-unfused-r1 | `09fd7144500ff4dc5eeb1c7cf1ad3412ab48581f47c9531d3d1d1fb061d2570c` |
| baseline-unfused-r1-extra16384 | `61c161d2db6e7f50baebce51b3c2eec86f472a92f35fac5c8df6a25432732288` |
| candidate-unfused-r1 | `c8007c596409ecbb28b2607cd3c83cb308b516f6e5a1c9a1b1315e1c01ca8982` |
| baseline-unfused-r2 | `18498602225ffb078be530f3b8422bfaf86fb7558cad3b05585a2d18af26740f` |
| candidate-unfused-r2 | `f8f79f828aa0f5e434e3a576c3bff536dacfc997e9b6ad8afdef8df0f6899cee` |
| baseline-fused-r1 | `c99366fea852092fc1ae50a42ed1716ff4266012ef19d1199faabadc58ebf6e4` |
| candidate-fused-r1 | `02f675292356e291a90a4b1b92d531d8ce6a9b28593d76c79dbbe28d776ff37e` |
| baseline-fused-r2 | `b6905b43c0e564f17f8866d3579b581c20870c8c4241eec5024dacbc20816d40` |
| candidate-fused-r2 | `4d04522e01b36b918bbb87fad8790bab421e7d63850a2923a737f7df2193cadd` |

Full-precision native input documents (including separate appendices), derived rows, validation metadata and tactic-cache hashes are preserved in `RESULTS.raw.json`.
