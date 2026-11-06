# K3 EP8 T8192 sampled FC1 ranges

Mean ns per range, weighted across the two independently captured clusters. Counts are not equal work guarantees under CLC. Concurrent warp ranges overlap.

| Range | d35 mean ns | Current mean ns | d35 count | Current count |
|---|---:|---:|---:|---:|
| pdl_dependency_wait | 40.00 | 35.20 | 4 | 80 |
| scheduler_item | 2105.81 | 2011.37 | 1106 | 1202 |
| scheduler_clc_ready | 111.77 | 111.57 | 1102 | 1198 |
| weight_tma_empty | 801.40 | 848.72 | 2352 | 2296 |
| weight_tma_issue | 30.38 | 36.06 | 2352 | 2296 |
| activation_tma_empty | 783.37 | N/A | 2352 | 0 |
| activation_tma_issue | 37.78 | N/A | 2352 | 0 |
| gather_empty | N/A | 277.23 | 0 | 9184 |
| gather_issue | N/A | 567.98 | 0 | 9184 |
| transform_wait_raw_tma_ready | 26.99 | 26.51 | 18816 | 18368 |
| transform_wait_tmem_slot_free | 30.85 | 25.24 | 18816 | 18368 |
| transform_load_decode_nvfp4 | 318.18 | 309.41 | 18816 | 18368 |
| transform_store_commit_bf16 | 80.98 | 80.47 | 18816 | 18368 |
| mma_acc_empty | 2968.76 | 2990.05 | 84 | 82 |
| mma_a_ready | 327.07 | 240.45 | 1176 | 1148 |
| mma_b_ready | 40.19 | 174.58 | 1176 | 1148 |
| mma_issue | 157.17 | 161.09 | 1176 | 1148 |
| mma_release | 24.49 | 25.76 | 1176 | 1148 |
| epi_acc_wait | 10064.10 | 10791.46 | 672 | 656 |
| epi_body | 2736.76 | 2739.27 | 672 | 656 |

Trace aggregation: arithmetic mean of range duration, weighted by observed range count across clusters; no geometric aggregation. Range counts differ under CLC and overlapping warp durations are not summed into end-to-end latency.
