| Marker | Control mean ns | R6 mean ns | Control count | R6 count |
|---|---:|---:|---:|---:|
| startup_dependency_wait | 32.0 | 29.3 | 10 | 24 |
| producer_tma_empty | 146.2 | 876.6 | 2072 | 2072 |
| producer_weight_tma | 23.6 | 38.5 | 2072 | 2072 |
| producer_activation_empty | 143.2 | N/A | 2072 | 0 |
| producer_activation_tma | 25.9 | N/A | 2072 | 0 |
| producer_gather_empty | N/A | 763.8 | 0 | 8288 |
| producer_gather_issue | N/A | 117.8 | 0 | 8288 |
| producer_gather_relay_wait | N/A | 108.2 | 0 | 2072 |
| mma_acc_empty | 59.7 | 38.9 | 74 | 74 |
| mma_tma_ready | 77.7 | 49.0 | 2072 | 2072 |
| mma_gather_ready | N/A | 805.3 | 0 | 2072 |
| mma_sf_copy_issue | 20.5 | 18.5 | 2072 | 2072 |
| mma_umma0_issue | 28.0 | 25.1 | 2072 | 2072 |
| mma_release_issue | 19.2 | 13.1 | 2072 | 2072 |
| epi_acc_wait | 3501.2 | 24761.6 | 296 | 296 |
| epi_body | 2877.4 | 2567.7 | 296 | 296 |
| scheduler_item | N/A | N/A | 0 | 0 |
