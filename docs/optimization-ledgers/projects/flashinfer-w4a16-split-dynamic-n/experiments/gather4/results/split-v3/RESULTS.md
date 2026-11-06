# Split W4A16 Gather4 before/after

Before: `36740c36a32a6c6d1c7d8162823fe823912de741`. After: the same HEAD plus the archived unstaged patch. Host `hu-pdx-7`, NVIDIA B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3`.

Single-GPU simulated EP8, H7168/I2048, unfused finalize. Before R1/R2 are reused unchanged from the prior ABBA campaign at `/workspace/flashinfer-w4a16-gather4/experiments/gather4/results/split-v1`. Only after R1 then after R2 were newly measured. This follow-up is not a fresh ABBA campaign; baseline drift is not controlled by a new trailing before sweep. Each absolute latency is a native median of 100 cold-L2 CUDA-graph CUPTI samples after 10 warmups, with independent AUTO.

Primary paired speedup is sqrt((Before R1 × Before R2)/(After R1 × After R2)). T1/T2 are reported and excluded from retention; T4 is included. No minima or cross-arm sample pooling.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | R1 | R2 | Paired | Repeat direction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1* | 33.664000 | 33.280000 | 29.504500 | 29.536500 | 1.140978× | 1.126741× | 1.133838× | both faster |
| 2* | 39.616500 | 40.256000 | 36.000000 | 35.712000 | 1.100458× | 1.127240× | 1.113769× | both faster |
| 4 | 54.400000 | 54.368000 | 51.296000 | 51.488500 | 1.060512× | 1.055925× | 1.058216× | both faster |
| 8 | 68.673000 | 68.000500 | 66.704500 | 66.720500 | 1.029511× | 1.019185× | 1.024335× | both faster |
| 16 | 76.961000 | 76.960500 | 72.449000 | 72.337000 | 1.062278× | 1.063916× | 1.063097× | both faster |
| 32 | 109.201000 | 110.241000 | 105.793500 | 106.512500 | 1.032209× | 1.035005× | 1.033606× | both faster |
| 64 | 143.713500 | 145.761000 | 139.409000 | 140.049500 | 1.030877× | 1.040782× | 1.035818× | both faster |
| 128 | 146.593500 | 146.753000 | 143.649000 | 143.329000 | 1.020498× | 1.023889× | 1.022192× | both faster |
| 256 | 154.753000 | 155.313000 | 152.096500 | 152.257000 | 1.017466× | 1.020071× | 1.018768× | both faster |
| 512 | 159.713000 | 159.713500 | 161.217000 | 160.609000 | 0.990671× | 0.994424× | 0.992546× | both slower |
| 4096 | 301.731000 | 300.482500 | 329.874500 | 329.346500 | 0.914684× | 0.912360× | 0.913521× | both slower |
| 8192 | 603.412500 | 594.613000 | 656.677000 | 634.517000 | 0.918888× | 0.937111× | 0.927955× | both slower |
| 16384 | 1235.834000 | 1202.218000 | 1215.546000 | 1205.370500 | 1.016690× | 0.997385× | 1.006991× | mixed or tied |

*T1/T2 excluded from retention.*

| Aggregate | Rows | R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: |
| Overall | 11 | 1.007426× | 1.008064× | 1.007745× |
| Decode | 8 | 1.030274× | 1.031440× | 1.030856× |
| Prefill | 3 | 0.948944× | 0.948287× | 0.948616× |

## Complete tactic comparison

Token comparisons use each token's entire cache key/value record: both FC1/FC2 tactics, cluster, raster and cache policy. Cumulative comparisons include all nonmetadata entries saved at that row and may differ because of earlier rows. All complete records, full cache snapshots and verified hashes are retained in `RESULTS.json`; no selected tactic fields substitute for full equality.

| Tokens | Token R1 | Token R2 | Token before repeats | Token after repeats | Token all four | Cumulative R1 | Cumulative R2 |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | different | different | different | same | different | different | different |
| 2 | different | same | same | different | different | different | different |
| 4 | different | different | different | same | different | different | different |
| 8 | different | different | same | same | different | different | different |
| 16 | same | same | same | same | same | different | different |
| 32 | same | same | different | different | different | different | different |
| 64 | different | different | different | different | different | different | different |
| 128 | different | different | same | same | different | different | different |
| 256 | different | same | different | same | different | different | different |
| 512 | different | different | same | different | different | different | different |
| 4096 | same | same | same | same | same | different | different |
| 8192 | same | same | same | same | same | different | different |
| 16384 | different | different | same | same | different | different | different |

## Descriptive median of sweep medians

These values are the median of two sweep medians (their arithmetic mean for two values), not pooled sample medians. Their ratio is descriptive only; retention uses the primary geometric paired ratio above.

| Tokens | Before (µs) | After (µs) | Descriptive ratio |
| ---: | ---: | ---: | ---: |
| 1 | 33.472000 | 29.520500 | 1.133856× |
| 2 | 39.936250 | 35.856000 | 1.113795× |
| 4 | 54.384000 | 51.392250 | 1.058214× |
| 8 | 68.336750 | 66.712500 | 1.024347× |
| 16 | 76.960750 | 72.393000 | 1.063097× |
| 32 | 109.721000 | 106.153000 | 1.033612× |
| 64 | 144.737250 | 139.729250 | 1.035841× |
| 128 | 146.673250 | 143.489000 | 1.022192× |
| 256 | 155.033000 | 152.176750 | 1.018769× |
| 512 | 159.713250 | 160.913000 | 0.992544× |
| 4096 | 301.106750 | 329.610500 | 0.913523× |
| 8192 | 599.012750 | 645.597000 | 0.927843× |
| 16384 | 1219.026000 | 1210.458250 | 1.007078× |

## Evidence checks

Two newly measured candidate sweeps and two verified unchanged prior baseline sweeps; 52 positive native medians; identical routing histograms and host/runtime; matching GPU UUID/model/power limit; unchanged benchmark/timer source; stable source hashes and working-tree diffs within each arm; 52 verified per-row cache hashes and matching cache metadata. Two repeats do not establish statistical significance. AUTO tactic changes prevent attributing every gain solely to Gather4. This report does not make an automatic retention decision.

Changed production sources: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`.
