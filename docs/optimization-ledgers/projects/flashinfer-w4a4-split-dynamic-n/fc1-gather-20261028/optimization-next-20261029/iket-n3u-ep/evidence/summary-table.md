| Marker | Control mean ns | fb66 mean ns | Control count | fb66 count |
|---|---:|---:|---:|---:|
| startup_dependency_wait | 28.8 | 5.3 | 10 | 24 |
| producer_tma_empty | 209.7 | 349.3 | 1616 | 1616 |
| producer_weight_tma | 51.7 | 68.7 | 1616 | 1616 |
| producer_activation_empty | 218.4 | N/A | 1616 | 0 |
| producer_activation_tma | 44.7 | N/A | 1616 | 0 |
| producer_gather_empty | N/A | 174.0 | 0 | 6464 |
| producer_gather_issue | N/A | 114.7 | 0 | 6464 |
| producer_gather_relay_wait | N/A | 460.6 | 0 | 1616 |
| mma_acc_empty | 57.5 | 52.6 | 202 | 202 |
| mma_tma_ready | 72.9 | 80.3 | 1616 | 1616 |
| mma_gather_ready | N/A | 57.0 | 0 | 1616 |
| mma_sf_copy_issue | 44.6 | 52.5 | 1616 | 1616 |
| mma_umma0_issue | 51.2 | 66.6 | 1616 | 1616 |
| mma_release_issue | 17.8 | 40.7 | 1616 | 1616 |
| epi_acc_wait | 590.3 | 1982.7 | 808 | 808 |
| epi_body | 1641.7 | 2106.3 | 808 | 808 |
| scheduler_item | N/A | N/A | 0 | 0 |
