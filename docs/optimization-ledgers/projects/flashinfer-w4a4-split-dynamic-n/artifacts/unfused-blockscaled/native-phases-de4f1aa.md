# Native NVFP4 actual-routing phase diagnostics, de4f1aa4

GPU0; diagnostic fixed tactics, no AUTO retention claim. Original native inputs and weight preparation; 10 warmups/100 cold-L2 graph CUPTI samples per isolated phase and full pipeline. Raw samples retained. Isolated phase medians need not sum to full pipeline due to cache residency and stream overlap.

|Tokens|Route N|Local routes|Max expert routes|Route tiles|Route us|Sort us|FC1 us|FC2 us|Combine us|Full us|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4096 | 16 | 3715 | 147 | 249 | 8.864 | 6.880 | 403.855 | 283.455 | 25.856 | 718.783 |
| 4096 | 32 | 3715 | 147 | 132 | 8.896 | 6.848 | 231.984 | 174.495 | 25.792 | 435.519 |
| 4096 | 64 | 3715 | 147 | 72 | 8.896 | 6.976 | 163.088 | 128.000 | 25.920 | 317.711 |
| 4096 | 128 | 3715 | 147 | 40 | 8.896 | 6.816 | 143.856 | 103.216 | 25.520 | 274.591 |
| 4096 | 256 | 3715 | 147 | 32 | 8.896 | 6.848 | 164.544 | 99.744 | 25.856 | 292.384 |
| 8192 | 16 | 8106 | 347 | 521 | 15.040 | 9.664 | 821.854 | 572.702 | 46.304 | 1451.052 |
| 8192 | 32 | 8106 | 347 | 270 | 15.008 | 9.632 | 447.007 | 341.407 | 46.336 | 847.134 |
| 8192 | 64 | 8106 | 347 | 140 | 15.008 | 9.632 | 283.776 | 231.487 | 46.303 | 574.751 |
| 8192 | 128 | 8106 | 347 | 77 | 14.976 | 9.632 | 244.335 | 182.592 | 46.336 | 486.223 |
| 8192 | 256 | 8106 | 347 | 45 | 15.008 | 9.472 | 252.368 | 163.151 | 46.304 | 476.911 |
| 16384 | 16 | 16280 | 733 | 1033 | 26.976 | 7.584 | 1604.093 | 1115.613 | 85.951 | 2825.177 |
| 16384 | 32 | 16280 | 733 | 525 | 26.944 | 7.680 | 845.374 | 669.902 | 85.936 | 1615.549 |
| 16384 | 64 | 16280 | 733 | 270 | 26.944 | 7.520 | 514.175 | 467.919 | 86.112 | 1083.870 |
| 16384 | 128 | 16280 | 733 | 142 | 26.944 | 7.712 | 428.047 | 380.815 | 85.791 | 900.782 |
| 16384 | 256 | 16280 | 733 | 77 | 26.976 | 7.776 | 433.119 | 361.727 | 86.096 | 908.750 |

Routing histograms match the original full AUTO screen for all three token counts. N256 route tiles at T4096/8192/16384:32/45/77, versus ideal equal counts at the nominal token totals:32/32/64. At T16K, N256 FC1+FC2=794.846us and isolated route+sort+combine=120.848us; full908.750us agrees with original AUTO915.070us.

The measured fixed-tactic minima are N128 at4096 (274.591us), N256 at8192 (476.911us), and N128 at16384 (900.782us). Original AUTO chose N256/N128/N256, so selection differences are modest (about6.1%,1.9%,0.9% versus diagnostic N256/N128/N256) and cannot explain the main prefill regression. Do not treat diagnostic minima as a replacement primary result.
