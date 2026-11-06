# Integrated finalize timing variants

Same secondary B300 node and method: EP8, H7168/I2048/E256/K8, O3, four-tactic AUTO, 100 cold-L2 graph/CUPTI samples per row. All candidate comparisons reuse identical A1 samples. Separated timing legs do not cancel temporal drift. All raw samples are retained.

| Tokens | External baseline µs | Dispatch WG µs | Two decode WGs µs | All five WGs µs | Baseline / all-five |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 89.169 | 94.353 | 78.689 | 77.761 | 1.146706× |
| 2 | 92.272 | 96.817 | 95.105 | 100.465 | 0.918454× |
| 4 | 119.937 | 115.250 | 116.961 | 110.193 | 1.088427× |
| 8 | 129.441 | 136.225 | 136.497 | 134.273 | 0.964017× |
| 16 | 155.313 | 150.418 | 144.209 | 139.553 | 1.112932× |
| 32 | 180.114 | 176.897 | 177.218 | 183.425 | 0.981949× |
| 64 | 206.322 | 193.938 | 203.746 | 201.730 | 1.022763× |
| 128 | 199.105 | 202.114 | 198.786 | 202.866 | 0.981463× |
| 256 | 202.497 | 205.826 | 205.314 | 204.994 | 0.987819× |
| 512 | 213.762 | 217.026 | 213.091 | 214.147 | 0.998202× |
| 1024 | 233.619 | 230.403 | 233.138 | 233.426 | 1.000825× |
| 2048 | 313.219 | 322.163 | 320.244 | 311.667 | 1.004980× |
| 4096 | 476.916 | 487.109 | 474.436 | 473.589 | 1.007025× |
| 8192 | 781.334 | 834.281 | 817.673 | 776.840 | 1.005785× |

Geometric baseline/candidate speedup over 8–8192: **0.992158× dispatch; 0.998224× two decode WGs; 1.005510× all five WGs**. Results remain small and mixed. All-five changes the 2048 tactic from N128 epilogue return to N128 dispatch return; all other baseline/all-five selections match. 1/2/4 remain in the table but are excluded from retention.

Commits: baseline `68eb1fe`; dispatch `5362e53`; decode `f4aea69`; all-five measured `f5f4de65` (PR head `62de7e6` has identical implementation/test/benchmark files and a corrected README ledger). All three independent complete archive/raw audits pass. Every candidate has 112 finite BF16 outputs bit exact against baseline.

Two-decode-WG cleanup overlap completed with an owner-reported 1.006765×; full independent timing audit is pending. Four-WG overlap is in native validation. Neither result is folded into this audited table yet.
