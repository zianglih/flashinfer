# Split W4A16 Gather4 before/after

Before: `36740c36a32a6c6d1c7d8162823fe823912de741`. After: the same HEAD plus the archived unstaged patch. Host `hu-pdx-7`, NVIDIA B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Single-GPU simulated EP8, H7168/I2048, unfused finalize. ABBA order: before R1, after R1, after R2, before R2. Each absolute latency is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups, with independent AUTO.

Primary paired speedup is sqrt((Before R1 × Before R2)/(After R1 × After R2)). T1/T2 are reported and excluded from retention; T4 is included. No minima or cross-arm sample pooling.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 | R2 | Paired | Repeat direction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1* | 33.664000 | 33.280000 | 29.568500 | 29.505000 | 1.138509× | 1.127944× | 1.133214× | both faster |
| 2* | 39.616500 | 40.256000 | 35.920500 | 35.936500 | 1.102894× | 1.120198× | 1.111512× | both faster |
| 4 | 54.400000 | 54.368000 | 52.864000 | 52.992000 | 1.029056× | 1.025966× | 1.027510× | both faster |
| 8 | 68.673000 | 68.000500 | 68.481000 | 68.576000 | 1.002804× | 0.991608× | 0.997190× | mixed or tied |
| 16 | 76.961000 | 76.960500 | 72.880500 | 72.832500 | 1.055989× | 1.056678× | 1.056333× | both faster |
| 32 | 109.201000 | 110.241000 | 106.641000 | 106.769000 | 1.024006× | 1.032519× | 1.028253× | both faster |
| 64 | 143.713500 | 145.761000 | 139.457000 | 139.601000 | 1.030522× | 1.044126× | 1.037302× | both faster |
| 128 | 146.593500 | 146.753000 | 142.561000 | 142.321500 | 1.028286× | 1.031137× | 1.029711× | both faster |
| 256 | 154.753000 | 155.313000 | 163.073000 | 163.105500 | 0.948980× | 0.952224× | 0.950601× | both slower |
| 512 | 159.713000 | 159.713500 | 201.634000 | 201.746000 | 0.792094× | 0.791656× | 0.791875× | both slower |
| 4096 | 301.731000 | 300.482500 | 646.196500 | 646.245000 | 0.466934× | 0.464967× | 0.465949× | both slower |
| 8192 | 603.412500 | 594.613000 | 1121.336500 | 1121.272000 | 0.538119× | 0.530302× | 0.534196× | both slower |
| 16384 | 1235.834000 | 1202.218000 | 2084.689000 | 2084.081500 | 0.592815× | 0.576857× | 0.584782× | both slower |

*T1/T2 excluded from retention.*

| Aggregate | Rows | R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: |
| Overall | 11 | 0.832090× | 0.829620× | 0.830854× |
| Decode | 8 | 0.985378× | 0.987035× | 0.986206× |
| Prefill | 3 | 0.530092× | 0.522001× | 0.526031× |

## Complete tactic comparison

Token comparisons use each token's entire cache key/value record: both FC1/FC2 tactics, cluster, raster and cache policy. Cumulative comparisons include all nonmetadata entries saved at that row and may differ because of earlier rows. All complete records, full cache snapshots and verified hashes are retained in `RESULTS.json`; no selected tactic fields substitute for full equality.

| Tokens | Token R1 | Token R2 | Token before repeats | Token after repeats | Token all four | Cumulative R1 | Cumulative R2 |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | different | different | different | same | different | different | different |
| 2 | different | different | same | same | different | different | different |
| 4 | different | different | different | same | different | different | different |
| 8 | different | different | same | same | different | different | different |
| 16 | different | different | same | same | different | different | different |
| 32 | different | same | different | same | different | different | different |
| 64 | different | different | different | same | different | different | different |
| 128 | different | different | same | same | different | different | different |
| 256 | different | different | different | same | different | different | different |
| 512 | same | same | same | same | same | different | different |
| 4096 | same | same | same | same | same | different | different |
| 8192 | same | same | same | same | same | different | different |
| 16384 | different | different | same | same | different | different | different |

## Descriptive median of sweep medians

These values are the median of two sweep medians (their arithmetic mean for two values), not pooled sample medians. Their ratio is descriptive only; retention uses the primary geometric paired ratio above.

| Tokens | Before (µs) | After (µs) | Descriptive ratio |
| ---: | ---: | ---: | ---: |
| 1 | 33.472000 | 29.536750 | 1.133232× |
| 2 | 39.936250 | 35.928500 | 1.111548× |
| 4 | 54.384000 | 52.928000 | 1.027509× |
| 8 | 68.336750 | 68.528500 | 0.997202× |
| 16 | 76.960750 | 72.856500 | 1.056333× |
| 32 | 109.721000 | 106.705000 | 1.028265× |
| 64 | 144.737250 | 139.529000 | 1.037327× |
| 128 | 146.673250 | 142.441250 | 1.029710× |
| 256 | 155.033000 | 163.089250 | 0.950602× |
| 512 | 159.713250 | 201.690000 | 0.791875× |
| 4096 | 301.106750 | 646.220750 | 0.465950× |
| 8192 | 599.012750 | 1121.304250 | 0.534211× |
| 16384 | 1219.026000 | 2084.385250 | 0.584837× |

## Evidence checks

Four successful complete sweeps; 52 positive native medians; identical routing histograms and host/runtime; matching GPU UUID/model/power limit; unchanged benchmark/timer source; stable source hashes and working-tree diffs within each arm; 52 verified per-row cache hashes and matching cache metadata. Two repeats do not establish statistical significance. AUTO tactic changes prevent attributing every gain solely to Gather4. This report does not make an automatic retention decision.

Changed production sources: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`.
