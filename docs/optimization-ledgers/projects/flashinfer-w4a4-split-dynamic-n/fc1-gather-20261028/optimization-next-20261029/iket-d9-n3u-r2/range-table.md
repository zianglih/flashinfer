| Marker | Warps | Count | Mean ns | Median ns | P90 ns |
|---|---|---:|---:|---:|---:|
| producer_tma_empty | 0 | 816 | 496.9 | 384 | 1216 |
| producer_weight_tma | 0 | 816 | 81.5 | 64 | 192 |
| producer_gather_relay_wait | 1 | 816 | 563.6 | 128 | 1536 |
| producer_gather_empty | 8,9,10,11 | 3264 | 381.9 | 224 | 1088 |
| producer_gather_issue | 8,9,10,11 | 3264 | 189.6 | 160 | 384 |
| mma_acc_empty | 2 | 102 | 915.1 | 960 | 1184 |
| mma_tma_ready | 2 | 816 | 69.1 | 64 | 96 |
| mma_sf_copy_issue | 2 | 816 | 56.1 | 32 | 96 |
| mma_gather_ready | 2 | 816 | 61.8 | 32 | 96 |
| mma_sfb_copy_issue | 2 | 816 | 57.9 | 32 | 128 |
| mma_umma0_issue | 2 | 816 | 59.7 | 32 | 128 |
| mma_umma1_issue | 2 | 816 | 40.2 | 32 | 64 |
| mma_release_issue | 2 | 816 | 30.0 | 32 | 64 |
| epi_acc_wait | 4 | 102 | 2024.2 | 1856 | 2368 |
| epi_body | 4 | 102 | 3836.9 | 4032 | 4288 |
