# Separate two-cell ACCA diagnostic

Both jobs passed all four phases, source/cache postflight and raw CUPTI replay. These 800 samples stay separate from the original 39-cell CAAC screen. Same physical GPU per cell, immutable2b8/cbef sources, recorded choices/routes, release C++ libraries/Ninja descriptions, compiler flags and timing contract. No retuning, clock change, pooling, replacement or further repeats.

| Cell | Primary CAAC | Separate ACCA | C repeat spread | A repeat spread | ACCA clock exceptions |
|---|---:|---:|---:|---:|---:|
| nemo3-ultra TP8 T16384 | -0.891% | -0.966% | 2.555% | 0.105% | 11/16 |
| v41-flash TP4 T4096 | -2.368% | +1.445% | 3.537% | 0.092% | 3/16 |

V41F reverses sign because its second control is slower, with a lower-clock later trajectory. The original adverse observation remains preserved; this repeat does not establish a stable gain. N3U is nominally negative in both orders. Its two candidate medians lie between the controls in this repeat, whose clock trajectories vary; the repeated adverse sign still matters and is not erased by that variability. Both FC1 and FC2 durations/extensions rise for N3U in each block. The complete results do not isolate a clock-independent native-instruction cause.

All phase component medians are shown in execution order. Durations overlap under PDL; do not sum them. Separate component medians/extensions need not sum exactly to the E2E median.

| Cell | Phase | E2E µs | FC1 duration / extension µs | FC2 duration / extension µs | Combine duration / extension µs | Route-sort µs |
|---|---|---:|---:|---:|---:|---:|
| tp-nemo3-ultra-w4a16 T16384 | 0-candidate | 1963.144 | 831.492 / 831.060 | 827.379 / 817.923 | 321.457 / 299.073 | 13.072 |
| tp-nemo3-ultra-w4a16 T16384 | 1-control | 1969.898 | 830.260 / 829.748 | 831.988 / 824.660 | 325.185 / 299.249 | 13.120 |
| tp-nemo3-ultra-w4a16 T16384 | 2-control | 1920.825 | 807.220 / 806.708 | 807.348 / 799.123 | 320.993 / 297.394 | 12.816 |
| tp-nemo3-ultra-w4a16 T16384 | 3-candidate | 1965.211 | 830.837 / 830.341 | 828.517 / 819.269 | 323.457 / 299.314 | 13.087 |
| tp-v41-flash-w4a16 T4096 | 0-candidate | 555.682 | 300.322 / 299.473 | 198.401 / 185.425 | 70.209 / 61.329 | 9.473 |
| tp-v41-flash-w4a16 T4096 | 1-control | 553.746 | 299.393 / 298.625 | 198.112 / 185.441 | 71.040 / 61.408 | 9.376 |
| tp-v41-flash-w4a16 T4096 | 2-control | 573.331 | 310.786 / 309.793 | 201.169 / 188.784 | 70.624 / 62.049 | 10.032 |
| tp-v41-flash-w4a16 T4096 | 3-candidate | 555.170 | 300.610 / 299.778 | 199.008 / 185.665 | 72.048 / 61.552 | 9.376 |

Every quartile is preserved below; SM values are min/median MHz, reasons are the complete observed reason-key set. There are 14/32 exception windows and no missing NVML windows.

| Cell | Phase / quartile | E2E µs | SM min / median MHz | Reason keys |
|---|---|---:|---:|---|
| tp-nemo3-ultra-w4a16 T16384 | 0-candidate / 0 | 1688.552 | 2032 / 2032.0 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 0-candidate / 1 | 1873.352 | 2032 / 2032 | 0,4 |
| tp-nemo3-ultra-w4a16 T16384 | 0-candidate / 2 | 1994.154 | 2032 / 2032 | 4 |
| tp-nemo3-ultra-w4a16 T16384 | 0-candidate / 3 | 1972.201 | 1282 / 1282.0 | 4 |
| tp-nemo3-ultra-w4a16 T16384 | 1-control / 0 | 1715.560 | 2032 / 2032 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 1-control / 1 | 1960.201 | 2032 / 2032 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 1-control / 2 | 2014.473 | 1320 / 1320 | 0,4 |
| tp-nemo3-ultra-w4a16 T16384 | 1-control / 3 | 1973.002 | 1320 / 1320.0 | 4 |
| tp-nemo3-ultra-w4a16 T16384 | 2-control / 0 | 1705.512 | 1980 / 2006.0 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 2-control / 1 | 1816.490 | 1980 / 1980 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 2-control / 2 | 2016.266 | 1432 / 1980.0 | 0,4 |
| tp-nemo3-ultra-w4a16 T16384 | 2-control / 3 | 1978.794 | 1432 / 1432.0 | 4 |
| tp-nemo3-ultra-w4a16 T16384 | 3-candidate / 0 | 1698.474 | 2032 / 2032 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 3-candidate / 1 | 1950.283 | 2032 / 2032 | 0 |
| tp-nemo3-ultra-w4a16 T16384 | 3-candidate / 2 | 1989.259 | 1312 / 1312 | 0,4 |
| tp-nemo3-ultra-w4a16 T16384 | 3-candidate / 3 | 1969.867 | 1312 / 1312.0 | 4 |
| tp-v41-flash-w4a16 T4096 | 0-candidate / 0 | 552.483 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 0-candidate / 1 | 548.770 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 0-candidate / 2 | 560.515 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 0-candidate / 3 | 586.338 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 1-control / 0 | 552.161 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 1-control / 1 | 551.490 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 1-control / 2 | 569.666 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 1-control / 3 | 591.491 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 2-control / 0 | 553.186 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 2-control / 1 | 553.410 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 2-control / 2 | 582.914 | 1732 / 1882.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 2-control / 3 | 576.418 | 1732 / 1732 | 0 |
| tp-v41-flash-w4a16 T4096 | 3-candidate / 0 | 552.802 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 3-candidate / 1 | 552.899 | 2032 / 2032.0 | 0 |
| tp-v41-flash-w4a16 T4096 | 3-candidate / 2 | 583.427 | 2032 / 2032 | 0 |
| tp-v41-flash-w4a16 T4096 | 3-candidate / 3 | 589.955 | 1672 / 1672 | 0 |

[Full raw evidence](../../../evidence/w4-tail-cutoff-acca/1793394140932104000/data) · [replayed table](../../../evidence/w4-tail-cutoff-acca/1793394140932104000/report/table.md) · [resource joins](../../../evidence/w4-tail-cutoff-acca/1793394140932104000/report/resource-deltas.json) · [original primary results](../RESULTS.md).

Native driver resources remain unchanged for all four measured FC-stage configurations; 16 loaded function records have LOCAL0. This is not a timed-cubin identity claim. The initial launch-receipt formatting mismatch failed before GPU work and remains preserved in preflight-format-failure/.
