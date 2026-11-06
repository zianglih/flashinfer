# Row-ready staging retention

R1 is not promoted. Against the same hu59 d01/A1 control, decode T4–512 GM is 0.941059× (0/8 wins); all 13 medians are slower and all selected rank tactics are unchanged. The derived Q1/R1 decode GM is 0.965272×. The row-ready protocol is source-reviewed and bit exact in this sweep, but it does not demonstrate an end-to-end performance benefit. Reduced small-row copy concurrency and readiness overhead are plausible costs, not isolated causes.

| T | A1 µs | Q1 µs | R1 µs | A1/R1 | Q1/R1 | R1 MAD µs | R1 quarter medians µs |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 65.6805 | 71.0560 | 74.7210 | 0.879010 | 0.950951 | 0.8800 | 74.912/75.008/74.401/74.369 |
| 2 | 84.7690 | 87.3445 | 91.1365 | 0.930132 | 0.958392 | 0.8955 | 91.105/90.977/91.265/91.105 |
| 4 | 94.7040 | 98.3050 | 103.9360 | 0.911176 | 0.945822 | 1.1675 | 103.936/104.129/103.905/103.936 |
| 8 | 120.8970 | 115.8570 | 126.3215 | 0.957058 | 0.917160 | 1.0405 | 126.817/126.529/126.081/125.793 |
| 16 | 134.5290 | 139.6650 | 141.0895 | 0.953501 | 0.989904 | 0.6565 | 141.057/140.897/141.282/141.410 |
| 32 | 159.7930 | 164.3210 | 168.1450 | 0.950329 | 0.977258 | 0.9920 | 168.257/167.265/168.610/167.905 |
| 64 | 182.9625 | 188.6415 | 190.9135 | 0.958353 | 0.988099 | 0.7530 | 191.170/191.298/190.818/190.338 |
| 128 | 184.9770 | 195.9545 | 199.0255 | 0.929414 | 0.984570 | 0.9600 | 199.585/198.881/198.913/198.305 |
| 256 | 191.0255 | 196.3055 | 203.8740 | 0.936978 | 0.962877 | 0.7365 | 204.066/203.298/204.289/203.874 |
| 512 | 195.5375 | 201.0100 | 209.6500 | 0.932685 | 0.958788 | 1.5520 | 212.834/209.249/210.050/208.642 |
| 4096 | 464.0205 | 475.8130 | 486.1810 | 0.954419 | 0.978675 | 2.2555 | 487.750/486.501/485.861/485.221 |
| 8192 | 797.7025 | 813.3015 | 846.0560 | 0.942848 | 0.961286 | 24.3040 | 807.720/808.296/853.286/869.320 |
| 16384 | 1530.8020 | 1547.2475 | 1544.2040 | 0.991321 | 1.001971 | 81.4730 | 1434.603/1536.684/1653.325/1622.797 |

The complete original 167-member file inventory was verified, including all104 source files, immutable runtime and same-boot source/group/GPU closure. The unchanged raw-sample/finite/repeat/fixture validators passed, as did104 exact rank-output comparisons against A1 and the derived104 against Q1. Eight cached serialized outputs were reused only by exact SHA256. The original gzip remained remote; its byte hash was not independently verified locally. Serial comparisons retain possible drift.

Audit `decode13-benchmark-hu59-v2/independent-file-timing-audit.json` SHA256 `09cd4189c0ebd1b97b165c37d259452d9e874c278ca983f078deaf3780fe94ba`. Source `4cd6162b73b94da4be1c3ace76d07cac0d95f8d1`; original archive reference `5975d5efce18dc9f24452cf521bcef96d9a95d2f69fa71be88ea5a97f2a0d306`.
