# Integrated finalize timing variants

Same secondary B300 node and method: EP8, H7168/I2048/E256/K8, O3, four-tactic AUTO, 100 cold-L2 graph/CUPTI samples per row. Precomputed routing; the timed scope is the full public forward including input staging, collective compute and finalization. All candidate comparisons reuse identical A1 samples. Separated timing legs do not cancel temporal drift. All raw samples are retained.

| Tokens | External baseline µs | Dispatch WG µs | Two decode WGs µs | All five WGs µs | Two decode WGs + cleanup overlap µs | Baseline / all-five | Baseline / decode-overlap |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 89.169 | 94.353 | 78.689 | 77.761 | 73.985 | 1.146706× | 1.205239× |
| 2 | 92.272 | 96.817 | 95.105 | 100.465 | 87.521 | 0.918454× | 1.054284× |
| 4 | 119.937 | 115.250 | 116.961 | 110.193 | 114.433 | 1.088427× | 1.048098× |
| 8 | 129.441 | 136.225 | 136.497 | 134.273 | 131.569 | 0.964017× | 0.983826× |
| 16 | 155.313 | 150.418 | 144.209 | 139.553 | 145.713 | 1.112932× | 1.065883× |
| 32 | 180.114 | 176.897 | 177.218 | 183.425 | 175.186 | 0.981949× | 1.028130× |
| 64 | 206.322 | 193.938 | 203.746 | 201.730 | 201.506 | 1.022763× | 1.023903× |
| 128 | 199.105 | 202.114 | 198.786 | 202.866 | 203.137 | 0.981463× | 0.980154× |
| 256 | 202.497 | 205.826 | 205.314 | 204.994 | 206.258 | 0.987819× | 0.981766× |
| 512 | 213.762 | 217.026 | 213.091 | 214.147 | 208.482 | 0.998202× | 1.025326× |
| 1024 | 233.619 | 230.403 | 233.138 | 233.426 | 231.314 | 1.000825× | 1.009963× |
| 2048 | 313.219 | 322.163 | 320.244 | 311.667 | 310.803 | 1.004980× | 1.007773× |
| 4096 | 476.916 | 487.109 | 474.436 | 473.589 | 476.884 | 1.007025× | 1.000067× |
| 8192 | 781.334 | 834.281 | 817.673 | 776.840 | 804.311 | 1.005785× | 0.971433× |

| Variant | Tested commit | Geometric baseline/candidate, 8–8192 | Faster retained rows | Same baseline AUTO tactic |
| --- | --- | ---: | ---: | ---: |
| Dispatch WG | `5362e535` | 0.992158× | 4/11 | 13/14 |
| Two decode WGs | `f4aea692` | 0.998224× | 7/11 | 14/14 |
| All five WGs | `f5f4de65` | 1.005510× | 6/11 | 13/14 |
| Two decode WGs + cleanup overlap | `513b11d4` | 1.006765× | 7/11 | 13/14 |

1/2/4 remain in the table but are excluded from retention. Results remain small and mixed. All-five and decode-overlap change the 2048 AUTO tactic from N128 epilogue return to N128 dispatch return; all their other baseline selections match. Dispatch differs at token 1 (N128 versus baseline N64); two-decode matches all baseline tactics.

Each candidate has 112 finite BF16 outputs bit exact against baseline, independently checked from complete raw archives. Later legs also match all112 retained dispatch outputs. This benchmark output comparison is separate from full strict60 qualification. Source baseline is `68eb1fe`; all-five was measured at `f5f4de65` (PR head `62de7e6` has identical implementation/test/benchmark files and a corrected README ledger). Exact full source/archive/audit hashes are retained in `VARIANT_RESULTS.json`.

For decode-overlap at 8192, the median is 804.311 µs (baseline/candidate 0.971433×), MAD24.815 µs (3.085%), and chronological quarter medians775.943/777.926/815.975/830.343 µs (+7.011%). The retained baseline also rises6.527% across quarters. Reused controls, drift and changed AUTO selections prevent a causal claim from the small aggregate differences. No fresh live closure or final qualification is asserted by this timing rollup.

Four-WG overlap remains in validation and is not included. Full tables and audit records: `independent-perf-ab1-audit`, `independent-perf-c1-audit`, `independent-all5-audit`, and `independent-overlap-audit` (`.json`/`.md`).
