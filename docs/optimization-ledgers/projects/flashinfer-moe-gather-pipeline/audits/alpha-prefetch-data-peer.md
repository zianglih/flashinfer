# Alpha prefetch: independent data peer

Passed. Frozen receipt: `audits/alpha-prefetch-data-peer.json` (`5f8f317d634fffab2dff75d3805de81306240f2da2229adc288d57d9c5aaf783`). Replayed 23 complete CAAC jobs, 56 cells, 224 phase medians and all 22,400 raw CUPTI spans; verified source/config/tactic/route/cache bindings and 448 loaded resource records. Original raw evidence and all negative rows remain unchanged.

Geometric-mean speedup: **-0.215899%** overall, **-0.056295%** at 32 tokens, **-0.375248%** at 16,384 tokens. There are 26 negative cells, including 18 with both repeat spreads ≤0.5%; that threshold is descriptive, not a significance test. Several per-token losses have normal observed clocks and tight repeats, supporting rejection without further runs.

Clock replay preserves 58 exception quartiles and one missing observation among 896 quartiles. The missing NVML window is `tp-v3-w4a4`, 16,384 tokens, `2-candidate`, quartile 3 (zero-based). Its CUPTI samples are complete.

Resources were joined by actual ordered configuration, token, backend and FC stage. All 448 loaded functions have LOCAL0; actual occupancy and shared-memory allocations match across arms. Thirteen of 112 paired configurations change registers, all FC2: nine decrease and four increase below. The representative 30-pair qualification’s no-growth result does not extend to the full screen.

| Job | Tokens | FC | Registers C→A | Dynamic SMEM (B), both | Actual CTAs/SM, both |
|---|---:|---:|---:|---:|---:|
| ep-nemo3-ultra-per-token | 32 | 2 | 88→90 | 197632 | 1 |
| ep-v41-flash-per-token | 32 | 2 | 88→90 | 197632 | 1 |
| tp-nemo3-ultra-per-token | 32 | 2 | 92→94 | 226304 | 1 |
| tp-v41-flash-w4a4 | 32 | 2 | 71→72 | 226304 | 1 |

All negative cells follow. C and A list the two phase medians in microseconds; spreads are within-arm max/min differences. Clock flags summarize observed quartiles and do not replace missing observations.

| Job / backend | Tokens | Speedup % | C medians µs | A medians µs | C / A spread % | Clock observation |
|---|---:|---:|---|---|---|---|
| ep-kimi-k3-mxfp / CuteDSL MXFP4x8 | 16384 | -0.138577 | 1082.3270, 1047.3195 | 1055.8630, 1076.5510 | 3.3426 / 1.9593 | 1537–2032 MHz / reasons 0 |
| ep-kimi-k3-per-token / CuteDSL PER-TOKEN | 32 | -0.057699 | 180.4340, 180.5450 | 180.4500, 180.7375 | 0.0615 / 0.1593 | 2032 MHz / reason 0 |
| ep-kimi-k3-w4a4 / CuteDSL W4A4 | 16384 | -0.055559 | 839.0470, 842.6150 | 836.3750, 846.2470 | 0.4252 / 1.1803 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 32 | -0.016642 | 100.6245, 100.6415 | 100.6575, 100.6420 | 0.0169 / 0.0154 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP8 | 32 | -0.156469 | 168.4975, 168.4180 | 168.6740, 168.7695 | 0.0472 / 0.0566 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 16384 | -3.968003 | 737.6400, 722.0075 | 777.1920, 743.0635 | 2.1651 / 4.5929 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-per-token / CuteDSL PER-TOKEN | 32 | -0.181565 | 109.8890, 110.0490 | 110.1770, 110.1610 | 0.1456 / 0.0145 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-per-token / CuteDSL PER-TOKEN | 16384 | -0.246548 | 951.9105, 951.4790 | 953.6390, 954.4550 | 0.0454 / 0.0856 | 2032 MHz / reason 0 |
| ep-nemo3-ultra-w4a4 / CuteDSL W4A4 | 16384 | -0.996850 | 558.4685, 558.5810 | 563.9405, 564.3565 | 0.0201 / 0.0738 | 2032–2032 MHz / reasons 0,4 |
| ep-v3-mxfp / CuteDSL MXFP8 | 32 | -0.058829 | 163.4895, 163.5045 | 163.6490, 163.5375 | 0.0092 / 0.0682 | 2032 MHz / reason 0 |
| ep-v3-mxfp / CuteDSL MXFP8 | 16384 | -6.267686 | 713.8130, 716.8700 | 780.5345, 746.1980 | 0.4283 / 4.6015 | 1972–2032 MHz / reasons 0 |
| ep-v3-w4a4 / CuteDSL W4A4 | 32 | -0.096313 | 99.5525, 99.6165 | 99.6800, 99.6810 | 0.0643 / 0.0010 | 2032 MHz / reason 0 |
| ep-v41-flash-mxfp / CuteDSL MXFP4x8 | 16384 | -0.579344 | 827.6225, 839.3670 | 844.0860, 832.6150 | 1.4191 / 1.3777 | 1987–2032 MHz / reasons 0,4 |
| ep-v41-flash-per-token / CuteDSL PER-TOKEN | 32 | -0.006323 | 130.3690, 130.3690 | 130.3370, 130.4175 | 0.0000 / 0.0618 | 2032 MHz / reason 0 |
| tp-kimi-k3-per-token / CuteDSL PER-TOKEN | 32 | -2.037073 | 178.1450, 178.1290 | 181.9055, 181.7770 | 0.0090 / 0.0707 | 2032 MHz / reason 0 |
| tp-kimi-k3-per-token / CuteDSL PER-TOKEN | 16384 | -1.250778 | 1947.4720, 1944.6560 | 1970.4485, 1970.9770 | 0.1448 / 0.0268 | 2032 MHz / reason 0 |
| tp-kimi-k3-w4a4 / CuteDSL W4A4 | 16384 | -0.912339 | 1414.4440, 1404.3640 | 1421.6915, 1423.0525 | 0.7178 / 0.0957 | 1965–2032 MHz / reasons 0,4 |
| tp-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 16384 | -0.315979 | 1194.8285, 1194.1415 | 1192.5410, 1204.0290 | 0.0575 / 0.9633 | 1785–2032 MHz / reasons 0,4 |
| tp-nemo3-ultra-per-token / CuteDSL PER-TOKEN | 16384 | -1.942232 | 1800.5090, 1799.8520 | 1835.2930, 1836.3805 | 0.0365 / 0.0593 | 2032 MHz / reason 0 |
| tp-nemo3-ultra-w4a4 / CuteDSL W4A4 | 16384 | -0.837001 | 1134.9375, 1136.0575 | 1144.7780, 1145.3855 | 0.0987 / 0.0531 | 2032 MHz / reason 0 |
| tp-v3-mxfp / CuteDSL MXFP4x8 | 16384 | -0.328523 | 1247.8505, 1246.8105 | 1250.2345, 1252.6500 | 0.0834 / 0.1932 | 1912–2032 MHz / reasons 0,4 |
| tp-v3-mxfp / CuteDSL MXFP8 | 16384 | -0.427849 | 1356.5880, 1354.6990 | 1366.0120, 1356.9395 | 0.1394 / 0.6686 | 1740–2032 MHz / reasons 0,4 |
| tp-v3-per-token / CuteDSL PER-TOKEN | 32 | -1.899226 | 116.1610, 116.0970 | 118.4010, 118.3535 | 0.0551 / 0.0401 | 2032 MHz / reason 0 |
| tp-v3-per-token / CuteDSL PER-TOKEN | 16384 | -2.995716 | 1395.8550, 1395.6950 | 1438.7680, 1438.9915 | 0.0115 / 0.0155 | 2032 MHz / reason 0 |
| tp-v3-w4a4 / CuteDSL W4A4 | 16384 | -0.233738 | 1092.8715, 1092.9190 | 1095.5440, 1095.3675 | 0.0043 / 0.0161 | 2032 MHz / reason 0; 1 window missing |
| tp-v41-flash-per-token / CuteDSL PER-TOKEN | 32 | -0.132282 | 144.9770, 144.9295 | 145.1530, 145.1375 | 0.0328 / 0.0107 | 2032 MHz / reason 0 |

Evidence: [raw campaign](../evidence/alpha-prefetch-screen/1793397894372465000/data/), [complete author report](../evidence/alpha-prefetch-screen/1793397894372465000/report/), [independent receipt](alpha-prefetch-data-peer.json), [replay helper](audit_alpha_prefetch_data.py). No GPU, source, timing-helper or original-evidence changes were made by this audit.
