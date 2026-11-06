# Split CuTe DSL W4A16 dynamic-N results

Before `316faec37a4706a2ecc7d46265087f8190b40baa`; after `9ec90d0696752c72ff826c8880e58515ace84e60`.

NVIDIA B300 SXM6 AC on `hu-pdx-30`, GPU0; Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA runtime `13.2`, CuTe DSL `4.7.1`, CUPTI Python `13.4.0`.

H7168/I2048, 256 global experts, top-k 8, groups 8/top-groups 4, routed scaling 2.5; simulated EP8/TP1, 32 local experts, offset 0. BF16 activations/output and NVFP4 weights. Routing is timed; preparation, autotuning, compilation and inter-GPU communication are excluded.

Each cell is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups. Existing measurements are reused. With one paired repeat, speedup is Before/After; with two, sqrt((Before R1 × Before R2)/(After R1 × After R2)). No row minima, substitutions or pooling of samples. R2 is not required to report existing R1 evidence.

Token/retention policy: [merged #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), merged 2026-10-14T21:52:15Z. Exact grid: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Only T1/T2 are reported-only; T4 is included. Retention uses the 11 remaining points; decode uses T4–512 and prefill uses T4096/T8192/T16384. Existing T1024/T2048 remain supplemental and are outside this grid.

A missing required point makes that aggregate incomplete; its displayed speedup covers only the explicitly listed available points and cannot stand in for full retention evidence. No universal numeric acceptance threshold is established by #6277. Assess the full pointwise table, decode/prefill behavior and tactic changes. Small mixed gains and tactic selection alone do not establish a useful kernel improvement.

Retention additionally requires repeat consistency and review for fixed-tactic regressions. Normal AUTO evidence alone does not satisfy that check; any fixed-tactic diagnostics remain separate from these primary medians. This report does not automatically accept a candidate based on its aggregate ratio.

Repeat disagreement is 100 × (max(R1,R2)/min(R1,R2)−1). Opposite directions mean one repeat speeds up and the other slows down. One/two sweeps do not establish statistical significance or isolate a fixed-tactic kernel gain.

Validation: 2 complete arm sweeps, 3 source result files, 28 medians/cache hashes; expected commit/source hashes and matching workload/software/histogram summaries. Dtypes are source-derived. The separate environment record supplies GPU UUID, driver and container details.

## Unfused finalize (primary)

Paired repeats available: [1].

- **Full retention grid: 1.015547×**, 11/11 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]; 9 faster / 2 slower.
- **Decode: 1.006025×**, 8/8 points (complete); available tokens [4, 8, 16, 32, 64, 128, 256, 512]; 7 faster / 1 slower.
- **Prefill: 1.041383×**, 3/3 points (complete); available tokens [4096, 8192, 16384]; 2 faster / 1 slower.

| Tokens | Role | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | reported only | 34.2730 | — | 34.0160 | — | 1.007555× |
| 2 | reported only | 40.3840 | — | 39.7925 | — | 1.014865× |
| 4 | decode | 54.8640 | — | 54.4165 | — | 1.008224× |
| 8 | decode | 68.6730 | — | 69.7610 | — | 0.984404× |
| 16 | decode | 76.8970 | — | 76.2880 | — | 1.007983× |
| 32 | decode | 109.7130 | — | 109.1370 | — | 1.005278× |
| 64 | decode | 143.2010 | — | 141.9375 | — | 1.008902× |
| 128 | decode | 145.8900 | — | 144.1300 | — | 1.012211× |
| 256 | decode | 152.7530 | — | 151.4895 | — | 1.008341× |
| 512 | decode | 159.0090 | — | 156.9455 | — | 1.013148× |
| 1024 | supplemental | 174.8340 | — | — | — | — |
| 2048 | supplemental | 211.6820 | — | — | — | — |
| 4096 | prefill | 308.8670 | — | 295.1390 | — | 1.046514× |
| 8192 | prefill | 627.3330 | — | 573.9090 | — | 1.093088× |
| 16384 | prefill | 1183.9945 | — | 1199.2750 | — | 0.987259× |

## Source evidence

| Input | File SHA256 |
| :--- | :--- |
| baseline-unfused-r1 | `09fd7144500ff4dc5eeb1c7cf1ad3412ab48581f47c9531d3d1d1fb061d2570c` |
| baseline-unfused-r1-extra16384 | `61c161d2db6e7f50baebce51b3c2eec86f472a92f35fac5c8df6a25432732288` |
| candidate-unfused-r1 | `c8007c596409ecbb28b2607cd3c83cb308b516f6e5a1c9a1b1315e1c01ca8982` |

Full-precision native input documents (including separate appendices), derived rows, validation metadata and tactic-cache hashes are preserved in `RESULTS.raw.json`.
