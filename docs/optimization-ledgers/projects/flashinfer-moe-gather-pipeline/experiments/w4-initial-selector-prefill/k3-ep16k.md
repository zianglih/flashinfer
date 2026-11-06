# K3 EP8 / 16384: unresolved adverse row

All four complete phases are retained. Candidate E2E medians (2021.729, 2040.240 µs) exceed both control medians (1987.040, 2015.520 µs): −1.464026%. FC1 and FC2 mean-of-phase durations both grow, by14.024 and13.752 µs; their critical extensions grow14.048 and13.768 µs. This is not a clean FC1-only signature, but the repeat-spread threshold does not dismiss it.

Eleven of16 clock windows are exceptions. The current CUPTI quartile traces below show different time/clock trajectories. Sparse NVML clock observations must not be used to normalize away latency or to select favorable windows.

| Phase | Quartile | E2E µs | FC1 µs | FC2 µs | Combine µs | SM min/median/max MHz | Reasons |
|---|---:|---:|---:|---:|---:|---|---|
| 0-control | 1 | 1772.398 | 1163.976 | 527.300 | 114.625 | 1762/2032/2032 | 0 |
| 0-control | 2 | 2001.295 | 1345.131 | 569.221 | 122.080 | 1762/1762/1762 | 0 |
| 0-control | 3 | 2005.936 | 1346.922 | 571.749 | 118.561 | 1290/1762/1762 | 0,4 |
| 0-control | 4 | 1987.024 | 1331.754 | 566.916 | 117.281 | 1290/1290/1290 | 4 |
| 1-candidate | 1 | 1717.197 | 1130.761 | 509.092 | 114.145 | 2032/2032/2032 | 4 |
| 1-candidate | 2 | 2058.737 | 1371.755 | 591.685 | 124.289 | 1282/2032/2032 | 4 |
| 1-candidate | 3 | 2068.464 | 1380.555 | 594.917 | 125.954 | 1282/1282/1282 | 4 |
| 1-candidate | 4 | 2008.400 | 1344.875 | 576.645 | 120.097 | 1282/1282/1305 | 4 |
| 2-candidate | 1 | 1775.342 | 1161.993 | 526.212 | 114.817 | 1815/2032/2032 | 0 |
| 2-candidate | 2 | 2050.865 | 1369.771 | 589.349 | 126.753 | 1815/1815/1815 | 0,4 |
| 2-candidate | 3 | 2061.392 | 1377.194 | 592.740 | 128.801 | 1275/1815/1815 | 4 |
| 2-candidate | 4 | 2038.896 | 1362.250 | 588.100 | 130.401 | 1275/1275/1275 | 4 |
| 3-control | 1 | 1805.167 | 1193.514 | 526.756 | 112.512 | 2032/2032/2032 | 0 |
| 3-control | 2 | 2059.505 | 1381.931 | 586.820 | 124.321 | 2032/2032/2032 | 0 |
| 3-control | 3 | 2020.529 | 1358.027 | 574.181 | 120.065 | 1305/2032/2032 | 0 |
| 3-control | 4 | 2014.769 | 1352.427 | 576.677 | 122.305 | 1305/1305/1305 | 4 |

Recommended bounded diagnostic, if authorized: one A–C–C–A block on original GPU1 UUID `GPU-b17ed232-0a73-13f0-fd86-db7534da7ea2`, exact same822/02de source/cache/frozen tactic/route,100 samples and10 warmups per phase, stock clock policy, separate output. No whole-matrix repeat, no clock lock, no phase substitution. The present result remains adverse regardless of the later result.
