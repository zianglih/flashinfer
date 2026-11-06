| Marker | Warps | Count | Mean ns | Median ns | P90 ns |
|---|---|---:|---:|---:|---:|
| producer_tma_empty | 0 | 816 | 500.6 | 384 | 1152 |
| producer_weight_tma | 0 | 816 | 87.1 | 64 | 192 |
| producer_gather_relay_wait | 1 | 816 | 604.9 | 192 | 1600 |
| producer_gather_empty | 8,9,10,11 | 3264 | 417.0 | 320 | 1152 |
| producer_gather_issue | 8,9,10,11 | 3264 | 163.0 | 128 | 320 |
| mma_acc_empty | 2 | 102 | 911.7 | 960 | 1120 |
| mma_tma_ready | 2 | 816 | 73.8 | 64 | 128 |
| mma_sf_copy_issue | 2 | 816 | 55.2 | 32 | 96 |
| mma_gather_ready | 2 | 816 | 71.1 | 32 | 160 |
| mma_sfb_copy_issue | 2 | 816 | 57.3 | 32 | 128 |
| mma_umma0_issue | 2 | 816 | 61.4 | 32 | 128 |
| mma_umma1_issue | 2 | 816 | 40.2 | 32 | 64 |
| mma_release_issue | 2 | 816 | 29.9 | 32 | 64 |
| epi_acc_wait | 4 | 102 | 1826.2 | 1664 | 2240 |
| epi_body | 4 | 102 | 4295.2 | 4448 | 4896 |
| epi_tmem_layout | 4 | 776 | 232.7 | 192 | 320 |
