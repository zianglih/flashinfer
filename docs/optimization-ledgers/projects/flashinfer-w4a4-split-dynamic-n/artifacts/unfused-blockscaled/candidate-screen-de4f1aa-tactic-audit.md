# de4 full-mode screen and tactic audit

Single-pair screening only. T1/T2 excluded; no retention claim. Baseline a65d5b09; candidate de4f1aa4. Same GPU1 and frozen v2 helper.

All 26 candidate cache hashes and full13 rows verified. Baseline/candidate methodology fields, source contract, histograms and chronology agree.

## mxfp8 (mxfp4 means mixed W4A8)

Baseline tactics below use (route-M, channel-N); candidate uses (channel-M128, route-N), so tile pairs must not be compared without swapping axes.

| Tokens | Before us | After us | Speedup | Baseline FC1 tile/cluster | Baseline FC2 tile/cluster | Candidate route N (both phases) |
|---:|---:|---:|---:|---|---|---:|
| 1 | 43.5200 | 41.4720 | 1.0494x | 128x128 / 1x1 | 128x256 / 1x1 | 16 |
| 2 | 55.5205 | 56.1280 | 0.9892x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 4 | 81.5840 | 84.6560 | 0.9637x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 8 | 110.2085 | 111.8880 | 0.9850x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 16 | 126.0480 | 128.4320 | 0.9814x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 32 | 182.9450 | 189.5845 | 0.9650x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 64 | 241.7600 | 251.6170 | 0.9608x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 128 | 250.2890 | 258.3530 | 0.9688x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 256 | 266.8810 | 273.7445 | 0.9749x | 128x128 / 1x1 | 128x128 / 1x2 | 32 |
| 512 | 268.4000 | 276.6245 | 0.9703x | 128x128 / 1x1 | 128x128 / 1x2 | 32 |
| 4096 | 359.6170 | 402.1445 | 0.8942x | 256x128 / 2x1 | 256x128 / 2x1 | 256 |
| 8192 | 536.5930 | 631.1370 | 0.8502x | 128x256 / 1x1 | 128x256 / 1x1 | 256 |
| 16384 | 857.8740 | 1138.7540 | 0.7533x | 128x256 / 1x1 | 128x256 / 1x2 | 256 |

Cache growth: one profile per token point through512; T4096 adds768/1024/1280/1536/1792/2048/2560/3072/3584/4096; T8192 and16384 each add their own profile (22 total). Same growth in both arms. Candidate N128 is selected at2048–3584, N256 at4096/8192/16384.

## mxfp4 (mxfp4 means mixed W4A8)

Baseline tactics below use (route-M, channel-N); candidate uses (channel-M128, route-N), so tile pairs must not be compared without swapping axes.

| Tokens | Before us | After us | Speedup | Baseline FC1 tile/cluster | Baseline FC2 tile/cluster | Candidate route N (both phases) |
|---:|---:|---:|---:|---|---|---:|
| 1 | 40.8960 | 33.3440 | 1.2265x | 128x256 / 1x1 | 128x128 / 1x2 | 16 |
| 2 | 51.2000 | 44.4800 | 1.1511x | 128x256 / 1x1 | 128x128 / 1x1 | 16 |
| 4 | 65.4400 | 66.4965 | 0.9841x | 128x128 / 1x1 | 128x192 / 1x1 | 16 |
| 8 | 85.7280 | 85.5845 | 1.0017x | 128x128 / 1x1 | 128x192 / 1x1 | 16 |
| 16 | 90.6410 | 94.6080 | 0.9581x | 128x128 / 1x1 | 128x128 / 1x1 | 32 |
| 32 | 133.8725 | 138.7040 | 0.9652x | 128x128 / 1x1 | 128x192 / 1x1 | 16 |
| 64 | 169.4725 | 182.5760 | 0.9282x | 128x128 / 1x1 | 128x128 / 1x1 | 32 |
| 128 | 177.8250 | 187.1840 | 0.9500x | 128x128 / 1x1 | 128x128 / 1x1 | 16 |
| 256 | 185.6490 | 196.2880 | 0.9458x | 128x128 / 1x1 | 128x192 / 1x1 | 32 |
| 512 | 188.3690 | 199.3445 | 0.9449x | 128x128 / 1x1 | 128x192 / 1x1 | 32 |
| 4096 | 303.2810 | 360.5925 | 0.8411x | 256x256 / 2x1 | 256x128 / 2x1 | 256 |
| 8192 | 461.1210 | 571.0090 | 0.8076x | 128x128 / 1x1 | 128x192 / 1x1 | 256 |
| 16384 | 776.0020 | 1075.0095 | 0.7219x | 128x256 / 1x1 | 128x256 / 1x1 | 256 |

Cache growth: one profile per token point through512; T4096 adds768/1024/1280/1536/1792/2048/2560/3072/3584/4096; T8192 and16384 each add their own profile (22 total). Same growth in both arms. Candidate N128 is selected at2048–3584, N256 at4096/8192/16384.

## Source implications

- Candidate catalogue has five coupled route tactics: N16/32/64/128/256, M128, cluster1. Both phases share route-N.
- N256 uses three FC1 pipeline stages and four FC2 stages; N128 uses four each; smaller N uses five. Stages are not independent AUTO dimensions.
- Candidate has a single accumulator pipeline stage. This serializes reuse of each accumulator through its epilogue; phase/overlap diagnostics can distinguish that cost from mainloop throughput.
- The old T4096 winner used two-CTA route-M256 clusters for both phases. Candidate only has one-CTA M128; lost parallelism is a plausible contributor, not established causality.
- Do not remove N256 based on this cache alone: it won AUTO at each prefill profile. First compare actual routed phase timing and mainloop/epilogue overlap.
