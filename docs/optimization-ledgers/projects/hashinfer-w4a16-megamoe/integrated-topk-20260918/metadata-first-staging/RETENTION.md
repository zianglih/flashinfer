# Retention: metadata-first staging P1

Unpromoted. The independently audited same-boot hu59 comparison against fresh d01/A1 has decode T4–512 geometric speedup **0.949920109×**, zero of eight decode wins. All 13 medians are slower with identical selected tactics on every rank. All104 rank/shape outputs are finite and bit-exact across arms; within-arm repeat checks and all raw100-sample checks pass.

| Tokens | d01 A1 (µs) | 3cd P1 (µs) | A1/P1 | A1 MAD (µs) | P1 MAD (µs) |
|---:|---:|---:|---:|---:|---:|
| 1 | 65.6805 | 75.8880 | 0.865493 | 0.7355 | 0.9280 |
| 2 | 84.7690 | 92.0965 | 0.920437 | 1.0235 | 0.7995 |
| 4 | 94.7040 | 103.0725 | 0.918810 | 0.6550 | 0.8315 |
| 8 | 120.8970 | 123.5205 | 0.978761 | 1.0080 | 0.8965 |
| 16 | 134.5290 | 142.3690 | 0.944932 | 0.9600 | 0.8320 |
| 32 | 159.7930 | 166.8495 | 0.957707 | 0.6880 | 0.9120 |
| 64 | 182.9625 | 191.0895 | 0.957470 | 0.7035 | 1.0720 |
| 128 | 184.9770 | 198.2255 | 0.933165 | 0.8320 | 0.9125 |
| 256 | 191.0255 | 200.1460 | 0.954431 | 0.7205 | 0.8805 |
| 512 | 195.5375 | 204.6900 | 0.955286 | 0.9915 | 0.8475 |
| 4096 | 464.0205 | 474.1160 | 0.978707 | 2.7530 | 3.2320 |
| 8192 | 797.7025 | 810.8860 | 0.983742 | 26.0970 | 22.3200 |
| 16384 | 1530.8020 | 1539.4850 | 0.994360 | 49.9690 | 94.1760 |

All13 cases are retained in the table; T1/T2 are visible but excluded from the decode aggregate, and prefill4096/8192/16384 remain separate guards. Same13/100/O3/AUTO4 and unchanged executed timing helpers, including the original cold-L2 method. This is a serial comparison, not a controlled measurement of overlap or a causal isolation of the extra payload barrier.

| Tokens | A1 quarter medians (µs) | P1 quarter medians (µs) |
|---:|---|---|
| 1 | 65.664, 65.793, 65.249, 65.824 | 76.512, 75.713, 75.489, 75.777 |
| 2 | 85.185, 85.089, 84.257, 84.096 | 92.161, 92.033, 92.225, 91.808 |
| 4 | 94.720, 94.849, 94.273, 94.849 | 103.104, 103.296, 102.721, 103.168 |
| 8 | 120.897, 120.897, 121.057, 120.673 | 123.617, 123.840, 123.329, 123.521 |
| 16 | 135.009, 134.529, 134.433, 134.401 | 142.369, 142.401, 142.049, 142.369 |
| 32 | 159.906, 160.161, 159.650, 159.297 | 166.625, 166.689, 166.786, 167.490 |
| 64 | 183.362, 182.626, 182.979, 182.947 | 191.201, 191.713, 191.073, 190.050 |
| 128 | 185.249, 185.537, 184.544, 184.673 | 198.433, 198.338, 197.921, 197.570 |
| 256 | 191.394, 190.594, 190.818, 191.201 | 200.417, 199.586, 199.298, 200.481 |
| 512 | 195.458, 194.817, 196.322, 195.490 | 205.090, 204.962, 204.130, 204.258 |
| 4096 | 463.235, 463.044, 464.388, 465.059 | 474.500, 473.668, 475.172, 473.764 |
| 8192 | 771.174, 769.638, 818.662, 833.830 | 777.894, 779.878, 824.838, 819.302 |
| 16384 | 1372.752, 1481.041, 1551.506, 1565.970 | 1386.030, 1506.185, 1650.379, 1614.698 |

Evidence: `decode13-benchmark-hu59/independent-file-timing-audit.json`. All165 original candidate sealed member files and the previously audited298-member control were rehashed. Compact transfer plus exact content-cache copies reconstruct full original member bytes. **Original gzip bytes were not locally verified**; their sealed hashes remain remote-provenance bindings. The old hu15 P1 package was prepared but never launched and supplies no timing evidence.

Q1 is a separate publication follow-up, not a promoted P1 result. The P1 table does not demonstrate whether early weight/decode release happened; diagnostic timestamps or actual generated-code observations are separately scoped.
