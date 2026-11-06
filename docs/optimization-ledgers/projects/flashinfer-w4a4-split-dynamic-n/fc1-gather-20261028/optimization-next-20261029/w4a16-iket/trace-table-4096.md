# K3 EP8 T4096 sampled FC1 ranges

Mean ns per range, weighted across the two independently captured clusters. Counts are not equal work guarantees under CLC. Concurrent warp ranges overlap.

| Range | d35 mean ns | Current mean ns | d35 count | Current count |
|---|---:|---:|---:|---:|
| pdl_dependency_wait | 40.00 | 31.20 | 4 | 80 |
| scheduler_item | 1911.62 | 2369.86 | 710 | 636 |
| scheduler_clc_ready | 238.19 | 238.73 | 706 | 632 |
| weight_tma_empty | 487.12 | 569.91 | 1848 | 1960 |
| weight_tma_issue | 40.29 | 34.56 | 1848 | 1960 |
| activation_tma_empty | 485.19 | N/A | 1848 | 0 |
| activation_tma_issue | 57.85 | N/A | 1848 | 0 |
| gather_empty | N/A | 150.86 | 0 | 7840 |
| gather_issue | N/A | 431.84 | 0 | 7840 |
| transform_wait_raw_tma_ready | 32.72 | 27.38 | 14784 | 15680 |
| transform_wait_tmem_slot_free | 27.68 | 25.36 | 14784 | 15680 |
| transform_load_decode_nvfp4 | 316.40 | 312.63 | 14784 | 15680 |
| transform_store_commit_bf16 | 85.81 | 83.09 | 14784 | 15680 |
| mma_acc_empty | 82.42 | 77.71 | 66 | 70 |
| mma_a_ready | 134.41 | 87.64 | 924 | 980 |
| mma_b_ready | 46.10 | 194.58 | 924 | 980 |
| mma_issue | 201.70 | 181.84 | 924 | 980 |
| mma_release | 34.60 | 27.79 | 924 | 980 |
| epi_acc_wait | 5579.27 | 6665.60 | 528 | 560 |
| epi_body | 3258.91 | 3018.74 | 528 | 560 |

Trace aggregation: arithmetic mean of range duration, weighted by observed range count across clusters; no geometric aggregation. Range counts differ under CLC and overlapping warp durations are not summed into end-to-end latency.
