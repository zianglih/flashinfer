# Fresh final PR comparison

Fresh ABBA on hu-pdx-38 / GPU-ae94371a-b05f-a1b5-d520-67157ffd295f; commit 316faec37a4706a2ecc7d46265087f8190b40baa versus 97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939. Whole split-MoE microseconds, independent AUTO, 10 warmups/100 cold-L2 CUDA-graph CUPTI samples per row. T1/T2 measured but excluded from aggregates.

| T | Before R1 | Before R2 | After R1 | After R2 | Paired speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 34.2720 | 34.0800 | 31.6160 | 31.1360 | 1.089268x |
| 2 | 39.7445 | 41.2965 | 36.8805 | 36.8160 | 1.099457x |
| 4 | 55.0730 | 56.8640 | 51.1050 | 51.2965 | 1.092981x |
| 8 | 69.7290 | 69.6165 | 66.6730 | 65.3760 | 1.055307x |
| 16 | 78.1450 | 77.7925 | 75.2965 | 75.3770 | 1.034934x |
| 32 | 110.6570 | 110.5770 | 108.4490 | 107.8410 | 1.022862x |
| 64 | 144.9930 | 145.5045 | 140.8170 | 142.1770 | 1.026525x |
| 128 | 147.9055 | 148.2570 | 144.3375 | 144.3690 | 1.025825x |
| 256 | 155.1680 | 156.0490 | 153.4570 | 152.8495 | 1.016029x |
| 512 | 160.8815 | 160.8970 | 156.5935 | 156.8975 | 1.026437x |
| 4096 | 312.2745 | 313.0420 | 290.4185 | 291.5550 | 1.074477x |
| 8192 | 595.8130 | 607.1090 | 573.8440 | 572.8210 | 1.049016x |
| 16384 | 1238.7945 | 1182.6020 | 1153.3055 | 1159.7695 | 1.046552x |

| Group | R1 | R2 | Paired |
| --- | ---: | ---: | ---: |
| overall | 1.041782x | 1.043352x | 1.042567x |
| decode | 1.034149x | 1.040561x | 1.037350x |
| prefill | 1.062416x | 1.050830x | 1.056607x |

Validated all 5,200 raw samples against reported row medians, all source snapshots against pinned Git commits, identical runtime/cache metadata, identical routing histograms, cache checksums, and the same GPU identity.
