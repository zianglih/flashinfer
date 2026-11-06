# Row-outer exact and generated-code gate

All23 existing/reference exact cases passed.44 compiled kernels have zero LOCAL/STACK/LDL/STL;21 FC2 cubins are byte-identical to retained475 and the earlier K-outer loop. Shared-memory and pipeline capacities, register roles and tactics match.14 of23 FC1 cubins are byte-identical to the rejected K-outer candidate.

K8/N128 one-CTA code removes23 static instructions, four SHFL sites, four R2UR sites and one branch compared with K-outer. K4 broad tiles are predominantly unchanged. Static counts cover the entire kernel; they do not establish a runtime gain.

| Index | N | CTA | K tile | Type | Retained / K-outer / row-outer instructions | SHFL | R2UR | Branches |
|---:|---:|---:|---:|---|---|---|---|---|
| 0 | 128 | 1 | 512 | Float4E2M1FN | 1421/1227/1204 | 32/8/4 | 79/20/16 | 118/121/120 |
| 2 | 128 | 1 | 512 | Float4E2M1FN | 1538/1337/1314 | 32/8/4 | 77/18/14 | 119/122/121 |
| 4 | 128 | 2 | 128 | Float8E4M3FN | 1449/1444/1444 | 16/8/8 | 58/64/64 | 123/127/127 |
| 6 | 128 | 2 | 128 | Float8E4M3FN | 1449/1444/1444 | 16/8/8 | 58/64/64 | 123/127/127 |
| 8 | 16 | 1 | 256 | Float8E4M3FN | 1341/1410/1392 | 4/8/4 | 48/64/64 | 74/77/76 |
| 10 | 16 | 1 | 256 | Float4E2M1FN | 928/962/962 | 4/4/4 | 19/18/18 | 83/85/85 |
| 11 | 128 | 1 | 512 | Float4E2M1FN | 1089/900/877 | 32/8/4 | 77/20/16 | 65/68/67 |
| 12 | 16 | 2 | 256 | Float4E2M1FN | 1489/1532/1510 | 4/8/8 | 60/68/60 | 125/129/129 |
| 14 | 16 | 2 | 256 | Float4E2M1FN | 1469/1522/1500 | 4/8/8 | 51/64/56 | 126/130/130 |
| 16 | 16 | 2 | 128 | Float8E4M3FN | 1769/1859/1823 | 4/16/16 | 50/72/56 | 163/171/171 |
| 18 | 16 | 2 | 128 | Float8E4M3FN | 1769/1859/1823 | 4/16/16 | 50/72/56 | 163/171/171 |
| 20 | 16 | 2 | 512 | Float4E2M1FN | 1435/1460/1460 | 4/4/4 | 28/27/27 | 145/147/147 |
| 22 | 16 | 2 | 512 | Float4E2M1FN | 1450/1470/1470 | 4/4/4 | 36/35/35 | 146/148/148 |
| 24 | 16 | 2 | 256 | Float8E4M3FN | 1601/1651/1651 | 4/8/8 | 22/26/26 | 162/166/166 |
| 26 | 16 | 2 | 256 | Float8E4M3FN | 1601/1651/1651 | 4/8/8 | 22/26/26 | 162/166/166 |
| 28 | 256 | 1 | 256 | Float4E2M1FN | 5816/5380/5380 | 64/8/8 | 313/135/135 | 107/111/111 |
| 30 | 256 | 1 | 256 | Float4E2M1FN | 5954/5540/5540 | 64/8/8 | 277/110/110 | 107/111/111 |
| 32 | 256 | 1 | 128 | Float8E4M3FN | 5853/5802/5802 | 64/16/16 | 325/224/224 | 142/158/158 |
| 34 | 256 | 1 | 128 | Float8E4M3FN | 5853/5802/5802 | 64/16/16 | 325/224/224 | 142/158/158 |
| 36 | 128 | 2 | 256 | Float4E2M1FN | 5644/5645/5645 | 16/8/8 | 141/129/129 | 128/132/132 |
| 38 | 128 | 2 | 256 | Float4E2M1FN | 5820/5821/5821 | 16/8/8 | 139/127/127 | 128/132/132 |
| 40 | 128 | 2 | 128 | Float8E4M3FN | 6186/6227/6227 | 16/16/16 | 148/146/146 | 176/184/184 |
| 42 | 128 | 2 | 128 | Float8E4M3FN | 6186/6227/6227 | 16/16/16 | 148/146/146 | 176/184/184 |

Paired control and K-outer captures are reused from the completed preceding experiment. Source hashes match exactly; no control source or old evidence was changed. New147-file archive SHA `3c3f07b3cddde1d14f2e56e21a3b06e4d5e3df17cb966f03243722dbcf9e8093` (2,812,476 compressed bytes).

GPU codegen uses no-cache/keep-PTX/CUBIN and contributes no timing evidence. The subsequent small screen uses normal persistent caches and executable guards.
