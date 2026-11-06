# Decode2WG C1 versus dispatch B1: table derivation

table_arithmetic_verified_C1_full_raw_audit_pending

| Tokens | A1 µs | Dispatch B1 µs | Decode C1 µs | A1/C1 | B1/C1 | Same B1/C1 tactic |
|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 89.169 | 94.353 | 78.689 | 1.133183 | 1.199056 | no |
| 2 | 92.272 | 96.817 | 95.105 | 0.970207 | 1.017991 | yes |
| 4 | 119.937 | 115.250 | 116.961 | 1.025444 | 0.985367 | yes |
| 8 | 129.441 | 136.225 | 136.497 | 0.948307 | 0.998007 | yes |
| 16 | 155.313 | 150.418 | 144.209 | 1.076996 | 1.043048 | yes |
| 32 | 180.114 | 176.897 | 177.218 | 1.016344 | 0.998194 | yes |
| 64 | 206.322 | 193.938 | 203.746 | 1.012643 | 0.951862 | yes |
| 128 | 199.105 | 202.114 | 198.786 | 1.001610 | 1.016744 | yes |
| 256 | 202.497 | 205.826 | 205.314 | 0.986280 | 1.002491 | yes |
| 512 | 213.762 | 217.026 | 213.091 | 1.003151 | 1.018469 | yes |
| 1024 | 233.619 | 230.403 | 233.138 | 1.002059 | 0.988267 | yes |
| 2048 | 313.219 | 322.163 | 320.244 | 0.978065 | 1.005994 | yes |
| 4096 | 476.916 | 487.109 | 474.436 | 1.005227 | 1.026712 | yes |
| 8192 | 781.334 | 834.281 | 817.673 | 0.955559 | 1.020312 | yes |

8–8192: A1/C1=0.998224×; B1/C1=1.006114×; decode faster in7/11 retained rows. B1/C1 tactics match13/14 rows, including all11 retained rows.

C1 is one later candidate-only sweep. A1 and B1 are reused from the earlier serial pair on the same node/environment. SharedA1 is exactly the same recorded baseline, so B1/C1 is a derived ratio of the actual medians, not an independent matched or drift-cancelling comparison. All14 rows shown;1/2/4 excluded only from retention aggregate. Timing covers precomputed-routing public full forward with integrated finalization inB1/C1; immutable generic external-finalize text is historical. This artifact verifies table arithmetic only; full C1 archive/raw validation is pending.
