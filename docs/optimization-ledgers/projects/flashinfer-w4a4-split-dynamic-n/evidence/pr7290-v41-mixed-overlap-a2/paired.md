# v41-flash EP4 direct median comparison

Paired native medians, no incremental ratios, pooling, pointwise minima or rounding from displayed tables.

Tokens 1 and 2 are reported but excluded from every retention aggregate.

All token-wise ID/weight hashes, dtype/shape, full histograms and local partition metadata match.

Explicit precision-family scope: mxfp; other families excluded.

## mxfp/CuteDSL W4A8

| Tokens | C1 us | A1 us | A2 us | C2 us | R1 speedup | R2 speedup | Paired speedup | Direction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9.696000 | 9.696000 | 9.728000 | 9.696000 | 1.000000x | 0.996711x | 0.998354x | mixed/flat |
| 2 | 23.104000 | 23.360000 | 23.361000 | 23.136000 | 0.989041x | 0.990369x | 0.989705x | both slower |
| 4 | 39.504000 | 38.240000 | 38.112500 | 39.504500 | 1.033054x | 1.036523x | 1.034787x | both faster |
| 8 | 52.257000 | 49.648500 | 50.176000 | 52.288000 | 1.052539x | 1.042092x | 1.047303x | both faster |
| 16 | 70.800000 | 66.928000 | 66.736500 | 70.592000 | 1.057853x | 1.057772x | 1.057813x | both faster |
| 32 | 136.513000 | 130.017000 | 129.088500 | 136.672500 | 1.049963x | 1.058750x | 1.054347x | both faster |
| 64 | 218.273000 | 205.697000 | 205.681500 | 218.337500 | 1.061138x | 1.061532x | 1.061335x | both faster |
| 128 | 283.138000 | 268.625500 | 268.194000 | 283.442000 | 1.054025x | 1.056854x | 1.055439x | both faster |
| 256 | 323.297500 | 308.770000 | 308.626000 | 323.346000 | 1.047050x | 1.047695x | 1.047372x | both faster |
| 512 | 326.898500 | 311.554000 | 311.026000 | 327.138000 | 1.049251x | 1.051803x | 1.050526x | both faster |
| 4096 | 396.611000 | 371.746500 | 371.778500 | 396.835000 | 1.066886x | 1.067396x | 1.067141x | both faster |
| 8192 | 549.156500 | 506.979500 | 496.963000 | 549.171500 | 1.083193x | 1.105055x | 1.094069x | both faster |
| 16384 | 923.286000 | 843.125500 | 834.693000 | 936.502000 | 1.095075x | 1.121972x | 1.108442x | both faster |

| Group | R1 | R2 | Paired |
| --- | ---: | ---: | ---: |
| decode | 1.050579x | 1.051595x | 1.051087x |
| prefill | 1.081656x | 1.097903x | 1.089749x |
| overall | 1.058965x | 1.064027x | 1.061493x |
