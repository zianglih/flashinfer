# Split W4A16 regular-TMA before/after

Before: `36740c36a32a6c6d1c7d8162823fe823912de741`. After: the same HEAD plus the archived unstaged patch. Host `hu-pdx-7`, NVIDIA B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Single-GPU simulated EP8, H7168/I2048, unfused finalize. Before R1/R2 are reused unchanged from the prior ABBA campaign at `/workspace/flashinfer-w4a16-regular-tma/experiments/regular-tma/history/gather4-split-v3`. Only after R1 then after R2 were newly measured. This follow-up is not a fresh ABBA campaign; baseline drift is not controlled by a new trailing before sweep. Each absolute latency is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups, with independent AUTO.

Primary paired speedup is sqrt((Before R1 × Before R2)/(After R1 × After R2)). T1/T2 are reported and excluded from retention; T4 is included. No minima or cross-arm sample pooling.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 | R2 | Paired | Repeat direction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1* | 33.664000 | 33.280000 | 33.056000 | 32.160000 | 1.018393× | 1.034826× | 1.026577× | both faster |
| 2* | 39.616500 | 40.256000 | 39.520000 | 38.560000 | 1.002442× | 1.043983× | 1.023002× | both faster |
| 4 | 54.400000 | 54.368000 | 53.600000 | 53.648500 | 1.014925× | 1.013411× | 1.014168× | both faster |
| 8 | 68.673000 | 68.000500 | 67.233000 | 67.856500 | 1.021418× | 1.002122× | 1.011724× | both faster |
| 16 | 76.961000 | 76.960500 | 75.457000 | 76.208500 | 1.019932× | 1.009868× | 1.014887× | both faster |
| 32 | 109.201000 | 110.241000 | 109.456000 | 109.473000 | 0.997670× | 1.007015× | 1.002332× | mixed or tied |
| 64 | 143.713500 | 145.761000 | 143.872500 | 143.888500 | 0.998895× | 1.013014× | 1.005929× | mixed or tied |
| 128 | 146.593500 | 146.753000 | 146.497000 | 145.857000 | 1.000659× | 1.006143× | 1.003397× | both faster |
| 256 | 154.753000 | 155.313000 | 153.585000 | 153.313000 | 1.007605× | 1.013045× | 1.010321× | both faster |
| 512 | 159.713000 | 159.713500 | 157.009000 | 157.121000 | 1.017222× | 1.016500× | 1.016861× | both faster |
| 4096 | 301.731000 | 300.482500 | 295.762000 | 295.634000 | 1.020182× | 1.016400× | 1.018289× | both faster |
| 8192 | 603.412500 | 594.613000 | 616.996500 | 595.925000 | 0.977984× | 0.997798× | 0.987841× | both slower |
| 16384 | 1235.834000 | 1202.218000 | 1189.161500 | 1201.290000 | 1.039248× | 1.000773× | 1.019829× | both faster |

*T1/T2 excluded from retention.*

| Aggregate | Rows | R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: |
| Overall | 11 | 1.010402× | 1.008717× | 1.009559× |
| Decode | 8 | 1.009749× | 1.010130× | 1.009940× |
| Prefill | 3 | 1.012145× | 1.004957× | 1.008545× |

## Complete tactic comparison

Token comparisons use each token's entire cache key/value record: both FC1/FC2 tactics, cluster, raster and cache policy. Cumulative comparisons include all nonmetadata entries saved at that row and may differ because of earlier rows. All complete records, full cache snapshots and verified hashes are retained in `RESULTS.json`; no selected tactic fields substitute for full equality.

| Tokens | Token R1 | Token R2 | Token before repeats | Token after repeats | Token all four | Cumulative R1 | Cumulative R2 |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | different | same | different | different | different | different | same |
| 2 | same | different | same | different | different | different | different |
| 4 | same | different | different | same | different | different | different |
| 8 | same | same | same | same | same | different | different |
| 16 | same | different | same | different | different | different | different |
| 32 | different | same | different | same | different | different | different |
| 64 | different | same | different | same | different | different | different |
| 128 | different | same | same | different | different | different | different |
| 256 | same | different | different | same | different | different | different |
| 512 | same | same | same | same | same | different | different |
| 4096 | same | same | same | same | same | different | different |
| 8192 | same | same | same | same | same | different | different |
| 16384 | same | same | same | same | same | different | different |

## Descriptive median of sweep medians

These values are the median of two sweep medians (their arithmetic mean for two values), not pooled sample medians. Their ratio is descriptive only; retention uses the primary geometric paired ratio above.

| Tokens | Before (µs) | After (µs) | Descriptive ratio |
| ---: | ---: | ---: | ---: |
| 1 | 33.472000 | 32.608000 | 1.026497× |
| 2 | 39.936250 | 39.040000 | 1.022957× |
| 4 | 54.384000 | 53.624250 | 1.014168× |
| 8 | 68.336750 | 67.544750 | 1.011726× |
| 16 | 76.960750 | 75.832750 | 1.014875× |
| 32 | 109.721000 | 109.464500 | 1.002343× |
| 64 | 144.737250 | 143.880500 | 1.005955× |
| 128 | 146.673250 | 146.177000 | 1.003395× |
| 256 | 155.033000 | 153.449000 | 1.010323× |
| 512 | 159.713250 | 157.065000 | 1.016861× |
| 4096 | 301.106750 | 295.698000 | 1.018291× |
| 8192 | 599.012750 | 606.460750 | 0.987719× |
| 16384 | 1219.026000 | 1195.225750 | 1.019913× |

## Evidence checks

Two newly measured candidate sweeps and two verified unchanged prior baseline sweeps; 52 positive native medians; identical routing histograms and host/runtime; matching GPU UUID/model/power limit; unchanged benchmark/timer source; stable source hashes and working-tree diffs within each arm; 52 verified per-row cache hashes and validated cache metadata (explicit audited relocation equivalence when reported below). Two repeats do not establish statistical significance. AUTO tactic changes prevent attributing every gain solely to the preparation kernel. This report does not make an automatic retention decision.

Changed production sources: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_prepare.py`.

Compiler cache fingerprints differ between historical and new environments. The explicit SHA-pinned audit reconstructs the exact historical fingerprint by changing only three generated entrypoint shebangs and their RECORD hash/size fields in memory. All raw metadata is preserved; every other metadata field must match. Audit SHA256: `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`.
