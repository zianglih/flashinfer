# Split W4A16 regular-TMA before/after

Before: `36740c36a32a6c6d1c7d8162823fe823912de741`. After: the same HEAD plus the archived unstaged patch. Host `hu-pdx-7`, NVIDIA B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Single-GPU simulated EP8, H7168/I2048, unfused finalize. Before R1/R2 are reused unchanged from the prior ABBA campaign at `/workspace/flashinfer-w4a16-regular-tma/experiments/regular-tma/history/gather4-split-v3`. Only after R1 then after R2 were newly measured. This follow-up is not a fresh ABBA campaign; baseline drift is not controlled by a new trailing before sweep. Each absolute latency is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups, with independent AUTO.

Primary paired speedup is sqrt((Before R1 × Before R2)/(After R1 × After R2)). T1/T2 are reported and excluded from retention; T4 is included. No minima or cross-arm sample pooling.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 | R2 | Paired | Repeat direction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1* | 33.664000 | 33.280000 | 30.752500 | 31.552000 | 1.094675× | 1.054767× | 1.074536× | both faster |
| 2* | 39.616500 | 40.256000 | 36.880000 | 36.624000 | 1.074200× | 1.099170× | 1.086613× | both faster |
| 4 | 54.400000 | 54.368000 | 51.296000 | 51.041000 | 1.060512× | 1.065183× | 1.062845× | both faster |
| 8 | 68.673000 | 68.000500 | 66.288500 | 66.849000 | 1.035972× | 1.017225× | 1.026556× | both faster |
| 16 | 76.961000 | 76.960500 | 75.505000 | 74.528000 | 1.019283× | 1.032639× | 1.025939× | both faster |
| 32 | 109.201000 | 110.241000 | 108.336500 | 107.617000 | 1.007980× | 1.024383× | 1.016148× | both faster |
| 64 | 143.713500 | 145.761000 | 141.633500 | 141.857000 | 1.014686× | 1.027521× | 1.021083× | both faster |
| 128 | 146.593500 | 146.753000 | 145.201500 | 144.512500 | 1.009587× | 1.015504× | 1.012541× | both faster |
| 256 | 154.753000 | 155.313000 | 152.897000 | 152.706000 | 1.012139× | 1.017072× | 1.014602× | both faster |
| 512 | 159.713000 | 159.713500 | 156.641000 | 156.577500 | 1.019612× | 1.020028× | 1.019820× | both faster |
| 4096 | 301.731000 | 300.482500 | 294.322000 | 294.242500 | 1.025173× | 1.021207× | 1.023188× | both faster |
| 8192 | 603.412500 | 594.613000 | 612.597000 | 586.677500 | 0.985007× | 1.013526× | 0.999165× | mixed or tied |
| 16384 | 1235.834000 | 1202.218000 | 1190.666000 | 1207.322500 | 1.037935× | 0.995772× | 1.016635× | mixed or tied |

*T1/T2 excluded from retention.*

| Aggregate | Rows | R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: |
| Overall | 11 | 1.020548× | 1.022607× | 1.021577× |
| Decode | 8 | 1.022339× | 1.027332× | 1.024833× |
| Prefill | 3 | 1.015786× | 1.010112× | 1.012945× |

## Complete tactic comparison

Token comparisons use each token's entire cache key/value record: both FC1/FC2 tactics, cluster, raster and cache policy. Cumulative comparisons include all nonmetadata entries saved at that row and may differ because of earlier rows. All complete records, full cache snapshots and verified hashes are retained in `RESULTS.json`; no selected tactic fields substitute for full equality.

| Tokens | Token R1 | Token R2 | Token before repeats | Token after repeats | Token all four | Cumulative R1 | Cumulative R2 |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | different | different | different | different | different | different | different |
| 2 | different | different | same | same | different | different | different |
| 4 | different | same | different | same | different | different | different |
| 8 | different | different | same | different | different | different | different |
| 16 | different | different | same | different | different | different | different |
| 32 | different | same | different | same | different | different | different |
| 64 | same | same | different | different | different | different | different |
| 128 | different | same | same | different | different | different | different |
| 256 | same | different | different | same | different | different | different |
| 512 | same | same | same | same | same | different | different |
| 4096 | same | same | same | same | same | different | different |
| 8192 | same | same | same | same | same | different | different |
| 16384 | same | different | same | different | different | different | different |

## Descriptive median of sweep medians

These values are the median of two sweep medians (their arithmetic mean for two values), not pooled sample medians. Their ratio is descriptive only; retention uses the primary geometric paired ratio above.

| Tokens | Before (µs) | After (µs) | Descriptive ratio |
| ---: | ---: | ---: | ---: |
| 1 | 33.472000 | 31.152250 | 1.074465× |
| 2 | 39.936250 | 36.752000 | 1.086642× |
| 4 | 54.384000 | 51.168500 | 1.062841× |
| 8 | 68.336750 | 66.568750 | 1.026559× |
| 16 | 76.960750 | 75.016500 | 1.025918× |
| 32 | 109.721000 | 107.976750 | 1.016154× |
| 64 | 144.737250 | 141.745250 | 1.021108× |
| 128 | 146.673250 | 144.857000 | 1.012538× |
| 256 | 155.033000 | 152.801500 | 1.014604× |
| 512 | 159.713250 | 156.609250 | 1.019820× |
| 4096 | 301.106750 | 294.282250 | 1.023190× |
| 8192 | 599.012750 | 599.637250 | 0.998959× |
| 16384 | 1219.026000 | 1198.994250 | 1.016707× |

## Evidence checks

Two newly measured candidate sweeps and two verified unchanged prior baseline sweeps; 52 positive native medians; identical routing histograms and host/runtime; matching GPU UUID/model/power limit; unchanged benchmark/timer source; stable source hashes and working-tree diffs within each arm; 52 verified per-row cache hashes and validated cache metadata (explicit audited relocation equivalence when reported below). Two repeats do not establish statistical significance. AUTO tactic changes prevent attributing every gain solely to the preparation kernel. This report does not make an automatic retention decision.

Changed production sources: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_prepare.py`.

Compiler cache fingerprints differ between historical and new environments. The explicit SHA-pinned audit reconstructs the exact historical fingerprint by changing only three generated entrypoint shebangs and their RECORD hash/size fields in memory. All raw metadata is preserved; every other metadata field must match. Audit SHA256: `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.
