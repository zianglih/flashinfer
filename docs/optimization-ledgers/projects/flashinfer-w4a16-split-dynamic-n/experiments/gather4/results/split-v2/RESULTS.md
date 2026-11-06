# Split W4A16 Gather4 before/after

Before: `36740c36a32a6c6d1c7d8162823fe823912de741`. After: the same HEAD plus the archived unstaged patch. Host `hu-pdx-7`, NVIDIA B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Single-GPU simulated EP8, H7168/I2048, unfused finalize. Before R1/R2 are reused unchanged from the prior ABBA campaign at `/workspace/flashinfer-w4a16-gather4/experiments/gather4/results/split-v1`. Only after R1 then after R2 were newly measured. This follow-up is not a fresh ABBA campaign; baseline drift is not controlled by a new trailing before sweep. Each absolute latency is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups, with independent AUTO.

Primary paired speedup is sqrt((Before R1 × Before R2)/(After R1 × After R2)). T1/T2 are reported and excluded from retention; T4 is included. No minima or cross-arm sample pooling.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 | R2 | Paired | Repeat direction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1* | 33.664000 | 33.280000 | 29.312000 | 29.344000 | 1.148472× | 1.134133× | 1.141280× | both faster |
| 2* | 39.616500 | 40.256000 | 35.664500 | 36.225000 | 1.110810× | 1.111277× | 1.111044× | both faster |
| 4 | 54.400000 | 54.368000 | 53.264500 | 53.840500 | 1.021318× | 1.009797× | 1.015541× | both faster |
| 8 | 68.673000 | 68.000500 | 66.800500 | 63.040000 | 1.028031× | 1.078688× | 1.053055× | both faster |
| 16 | 76.961000 | 76.960500 | 73.728500 | 72.432500 | 1.043843× | 1.062513× | 1.053137× | both faster |
| 32 | 109.201000 | 110.241000 | 106.561000 | 106.769000 | 1.024775× | 1.032519× | 1.028639× | both faster |
| 64 | 143.713500 | 145.761000 | 141.121000 | 142.017000 | 1.018371× | 1.026363× | 1.022359× | both faster |
| 128 | 146.593500 | 146.753000 | 143.856500 | 144.417000 | 1.019026× | 1.016175× | 1.017600× | both faster |
| 256 | 154.753000 | 155.313000 | 150.961000 | 150.721000 | 1.025119× | 1.030467× | 1.027790× | both faster |
| 512 | 159.713000 | 159.713500 | 155.777000 | 155.649000 | 1.025267× | 1.026113× | 1.025690× | both faster |
| 4096 | 301.731000 | 300.482500 | 331.362500 | 331.395000 | 0.910577× | 0.906720× | 0.908646× | both slower |
| 8192 | 603.412500 | 594.613000 | 624.645000 | 626.901000 | 0.966009× | 0.948496× | 0.957212× | both slower |
| 16384 | 1235.834000 | 1202.218000 | 1279.802000 | 1269.770500 | 0.965645× | 0.946799× | 0.956176× | both slower |

*T1/T2 excluded from retention.*

| Aggregate | Rows | R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: |
| Overall | 11 | 1.003617× | 1.006432× | 1.005023× |
| Decode | 8 | 1.025691× | 1.035101× | 1.030385× |
| Prefill | 3 | 0.947047× | 0.933804× | 0.940402× |

## Complete tactic comparison

Token comparisons use each token's entire cache key/value record: both FC1/FC2 tactics, cluster, raster and cache policy. Cumulative comparisons include all nonmetadata entries saved at that row and may differ because of earlier rows. All complete records, full cache snapshots and verified hashes are retained in `RESULTS.json`; no selected tactic fields substitute for full equality.

| Tokens | Token R1 | Token R2 | Token before repeats | Token after repeats | Token all four | Cumulative R1 | Cumulative R2 |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | different | same | different | same | different | different | same |
| 2 | same | different | same | different | different | different | different |
| 4 | different | different | different | same | different | different | different |
| 8 | different | different | same | same | different | different | different |
| 16 | different | same | same | different | different | different | different |
| 32 | different | same | different | same | different | different | different |
| 64 | different | different | different | different | different | different | different |
| 128 | different | same | same | different | different | different | different |
| 256 | same | different | different | same | different | different | different |
| 512 | same | same | same | same | same | different | different |
| 4096 | different | different | same | same | different | different | different |
| 8192 | same | same | same | same | same | different | different |
| 16384 | same | same | same | same | same | different | different |

## Descriptive median of sweep medians

These values are the median of two sweep medians (their arithmetic mean for two values), not pooled sample medians. Their ratio is descriptive only; retention uses the primary geometric paired ratio above.

| Tokens | Before (µs) | After (µs) | Descriptive ratio |
| ---: | ---: | ---: | ---: |
| 1 | 33.472000 | 29.328000 | 1.141298× |
| 2 | 39.936250 | 35.944750 | 1.111045× |
| 4 | 54.384000 | 53.552500 | 1.015527× |
| 8 | 68.336750 | 64.920250 | 1.052626× |
| 16 | 76.960750 | 73.080500 | 1.053096× |
| 32 | 109.721000 | 106.665000 | 1.028650× |
| 64 | 144.737250 | 141.569000 | 1.022380× |
| 128 | 146.673250 | 144.136750 | 1.017598× |
| 256 | 155.033000 | 150.841000 | 1.027791× |
| 512 | 159.713250 | 155.713000 | 1.025690× |
| 4096 | 301.106750 | 331.378750 | 0.908648× |
| 8192 | 599.012750 | 625.773000 | 0.957236× |
| 16384 | 1219.026000 | 1274.786250 | 0.956259× |

## Evidence checks

Two newly measured candidate sweeps and two verified unchanged prior baseline sweeps; 52 positive native medians; identical routing histograms and host/runtime; matching GPU UUID/model/power limit; unchanged benchmark/timer source; stable source hashes and working-tree diffs within each arm; 52 verified per-row cache hashes and matching cache metadata. Two repeats do not establish statistical significance. AUTO tactic changes prevent attributing every gain solely to Gather4. This report does not make an automatic retention decision.

Changed production sources: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`.
