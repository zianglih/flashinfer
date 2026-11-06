# Selected four-WG timing versus original and refreshed baseline

A1 and A2 are the same baseline68eb source; A2 ran after selected14. A2 is artifact label C1. Every100-sample row is retained. Separate A1/selected and A2/selected ratios are observations, not a drift-cancelled control or qualification. Selected source remains14a9e720; a README-only publication head is not a new timing run.

## Original A1 (before selected)

| Tokens | Baseline µs | Selected14 µs | Baseline/selected | Same AUTO tactic |
|---:|---:|---:|---:|:---:|
| 1 | 89.169 | 81.616 | 1.092543 | yes |
| 2 | 92.272 | 100.098 | 0.921821 | yes |
| 4 | 119.937 | 113.393 | 1.057711 | yes |
| 8 | 129.441 | 135.713 | 0.953781 | yes |
| 16 | 155.313 | 144.898 | 1.071882 | yes |
| 32 | 180.114 | 177.202 | 1.016436 | yes |
| 64 | 206.322 | 201.265 | 1.025124 | yes |
| 128 | 199.105 | 203.874 | 0.976611 | yes |
| 256 | 202.497 | 203.970 | 0.992781 | yes |
| 512 | 213.762 | 208.194 | 1.026744 | yes |
| 1024 | 233.619 | 229.362 | 1.018558 | yes |
| 2048 | 313.219 | 310.611 | 1.008398 | no |
| 4096 | 476.916 | 469.780 | 1.015191 | yes |
| 8192 | 781.334 | 775.304 | 1.007778 | yes |

## Fresh A2 (after selected)

| Tokens | Baseline µs | Selected14 µs | Baseline/selected | Same AUTO tactic |
|---:|---:|---:|---:|:---:|
| 1 | 74.096 | 81.616 | 0.907867 | yes |
| 2 | 101.313 | 100.098 | 1.012143 | yes |
| 4 | 115.633 | 113.393 | 1.019754 | yes |
| 8 | 133.057 | 135.713 | 0.980426 | yes |
| 16 | 147.793 | 144.898 | 1.019987 | yes |
| 32 | 181.921 | 177.202 | 1.026634 | yes |
| 64 | 206.066 | 201.265 | 1.023849 | yes |
| 128 | 208.194 | 203.874 | 1.021187 | yes |
| 256 | 206.499 | 203.970 | 1.012401 | yes |
| 512 | 210.738 | 208.194 | 1.012219 | yes |
| 1024 | 237.490 | 229.362 | 1.035440 | yes |
| 2048 | 316.226 | 310.611 | 1.018081 | yes |
| 4096 | 469.301 | 469.780 | 0.998981 | yes |
| 8192 | 801.416 | 775.304 | 1.033680 | yes |

Geometric ratios over 8–8192: A1/selected **1.009891×**, A2/selected **1.016513×**, A1/A2 **0.993485×**. All 112 outputs are finite BF16-bit exact in each comparison. All 100 samples per row are retained; 1/2/4 are excluded only from retention.

This artifact uses recorded closure only; no live GPU/process query.
