# v41-flash EP4 direct median comparison

C1/A1 screening only; repeat pair A2/C2 is required before a retention decision.

Tokens 1 and 2 are reported but excluded from every retention aggregate.

All token-wise ID/weight hashes, dtype/shape, full histograms and local partition metadata match.

Explicit precision-family scope: mxfp; other families excluded.

## mxfp/CuteDSL W4A8

| Tokens | C1 us | A1 us | R1 speedup |
| --- | --- | --- | --- |
| 1 | 9.696000 | 9.696000 | 1.000000x |
| 2 | 23.104000 | 23.360000 | 0.989041x |
| 4 | 39.504000 | 38.240000 | 1.033054x |
| 8 | 52.257000 | 49.648500 | 1.052539x |
| 16 | 70.800000 | 66.928000 | 1.057853x |
| 32 | 136.513000 | 130.017000 | 1.049963x |
| 64 | 218.273000 | 205.697000 | 1.061138x |
| 128 | 283.138000 | 268.625500 | 1.054025x |
| 256 | 323.297500 | 308.770000 | 1.047050x |
| 512 | 326.898500 | 311.554000 | 1.049251x |
| 4096 | 396.611000 | 371.746500 | 1.066886x |
| 8192 | 549.156500 | 506.979500 | 1.083193x |
| 16384 | 923.286000 | 843.125500 | 1.095075x |

| Group | R1 |
| --- | ---: |
| decode | 1.050579x |
| prefill | 1.081656x |
| overall | 1.058965x |
