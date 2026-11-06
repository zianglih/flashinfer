# Integrated finalize timing variants

Same secondary B300 node and method: EP8, H7168/I2048/E256/K8, O3, four-tactic AUTO, 100 cold-L2 graph/CUPTI samples per row. Precomputed routing; the timed scope is the full public forward including input staging, collective compute and finalization. All candidate comparisons reuse identical A1 samples. Separated timing legs do not cancel temporal drift. All raw samples are retained.

| Tokens | External baseline µs | Dispatch WG µs | Two decode WGs µs | All five WGs µs | Two decode WGs + cleanup overlap µs | Four non-dispatch WGs + cleanup overlap µs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 89.169 | 94.353 | 78.689 | 77.761 | 73.985 | 81.616 |
| 2 | 92.272 | 96.817 | 95.105 | 100.465 | 87.521 | 100.098 |
| 4 | 119.937 | 115.250 | 116.961 | 110.193 | 114.433 | 113.393 |
| 8 | 129.441 | 136.225 | 136.497 | 134.273 | 131.569 | 135.713 |
| 16 | 155.313 | 150.418 | 144.209 | 139.553 | 145.713 | 144.898 |
| 32 | 180.114 | 176.897 | 177.218 | 183.425 | 175.186 | 177.202 |
| 64 | 206.322 | 193.938 | 203.746 | 201.730 | 201.506 | 201.265 |
| 128 | 199.105 | 202.114 | 198.786 | 202.866 | 203.137 | 203.874 |
| 256 | 202.497 | 205.826 | 205.314 | 204.994 | 206.258 | 203.970 |
| 512 | 213.762 | 217.026 | 213.091 | 214.147 | 208.482 | 208.194 |
| 1024 | 233.619 | 230.403 | 233.138 | 233.426 | 231.314 | 229.362 |
| 2048 | 313.219 | 322.163 | 320.244 | 311.667 | 310.803 | 310.611 |
| 4096 | 476.916 | 487.109 | 474.436 | 473.589 | 476.884 | 469.780 |
| 8192 | 781.334 | 834.281 | 817.673 | 776.840 | 804.311 | 775.304 |

All ratios below are baseline/candidate; greater than 1 favors the candidate.

| Tokens | Dispatch WG | Two decode WGs | All five WGs | Decode cleanup overlap | Four-WG cleanup overlap |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.945062× | 1.133183× | 1.146706× | 1.205239× | 1.092543× |
| 2 | 0.953061× | 0.970207× | 0.918454× | 1.054284× | 0.921821× |
| 4 | 1.040673× | 1.025444× | 1.088427× | 1.048098× | 1.057711× |
| 8 | 0.950200× | 0.948307× | 0.964017× | 0.983826× | 0.953781× |
| 16 | 1.032546× | 1.076996× | 1.112932× | 1.065883× | 1.071882× |
| 32 | 1.018183× | 1.016344× | 0.981949× | 1.028130× | 1.016436× |
| 64 | 1.063855× | 1.012643× | 1.022763× | 1.023903× | 1.025124× |
| 128 | 0.985115× | 1.001610× | 0.981463× | 0.980154× | 0.976611× |
| 256 | 0.983829× | 0.986280× | 0.987819× | 0.981766× | 0.992781× |
| 512 | 0.984960× | 1.003151× | 0.998202× | 1.025326× | 1.026744× |
| 1024 | 1.013956× | 1.002059× | 1.000825× | 1.009963× | 1.018558× |
| 2048 | 0.972238× | 0.978065× | 1.004980× | 1.007773× | 1.008398× |
| 4096 | 0.979074× | 1.005227× | 1.007025× | 1.000067× | 1.015191× |
| 8192 | 0.936536× | 0.955559× | 1.005785× | 0.971433× | 1.007778× |

| Variant | Tested commit | Geometric baseline/candidate, 8–8192 | Faster retained rows | Same baseline AUTO tactic |
| --- | --- | ---: | ---: | ---: |
| Dispatch WG | `5362e535` | 0.992158× | 4/11 | 13/14 |
| Two decode WGs | `f4aea692` | 0.998224× | 7/11 | 14/14 |
| All five WGs | `f5f4de65` | 1.005510× | 6/11 | 13/14 |
| Two decode WGs + cleanup overlap | `513b11d4` | 1.006765× | 7/11 | 13/14 |
| Four non-dispatch WGs + cleanup overlap | `14a9e720` | 1.009891× | 8/11 | 13/14 |

1/2/4 remain in the tables but are excluded from retention. Results remain small and mixed. All-five and both cleanup-overlap variants change the 2048 AUTO tactic from N128 epilogue return to N128 dispatch return; all their other baseline selections match. Dispatch differs at token 1 (N128 versus baseline N64); two-decode matches all baseline tactics.

Each candidate has 112 finite BF16 outputs bit exact against baseline, independently checked from complete raw archives. Later legs also match all 112 retained dispatch outputs. This benchmark output comparison is separate from full strict 60/sanitizer qualification. Source baseline is `68eb1fe`; all-five was measured at `f5f4de65` (PR head `62de7e6` has identical implementation/test/benchmark files and a corrected README ledger). Exact full source/archive/audit hashes are retained in `VARIANT_RESULTS.json`.

The four-WG candidate is slower than retained A1 at 8 tokens (135.7135 vs 129.441 µs; 0.953781×) and 128 (203.874 vs 199.105 µs; 0.976611×), as well as256. Its 8-token quarter medians 133.217/135.426/135.938/137.794 µs rise 3.436%; 128-token quarters 201.026/205.250/204.066/204.290 rise 1.624%. At 8192 its median 775.304 µs has MAD 19.3605 µs (2.497%) and quarters 762.216/761.415/800.360/815.657 µs (+7.011%), while the retained baseline rises 6.527%. These spreads, serial drift and changed AUTO selections preclude treating the sub-1% aggregate difference as a proven causal gain.

For decode-overlap at 8192, the median is 804.311 µs (0.971433× baseline/candidate), MAD 24.815 µs (3.085%), and quarters 775.943/777.926/815.975/830.343 µs (+7.011%). The same-source baseline refresh now passed full raw audit. Its separate A2/selected table is in `selected-four-wg-vs-baselines.md` (1.016513× over 8–8192); the tables above retain their original identical A1 control. See `selected-four-wg-timing-notes.md` for chronology and drift. No live closure, final source selection or full qualification is asserted by this timing rollup.

Full raw-audit tables: `independent-perf-ab1-audit`, `independent-perf-c1-audit`, `independent-all5-audit`, `independent-overlap-audit`, and `independent-nondispatch-overlap-audit` (`.json`/`.md`).
