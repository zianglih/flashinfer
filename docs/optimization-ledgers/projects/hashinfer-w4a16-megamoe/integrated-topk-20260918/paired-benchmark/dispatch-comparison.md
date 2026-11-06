| Tokens | BEFORE µs | AFTER µs | BEFORE/AFTER | Same tactic |
| ---: | ---: | ---: | ---: | :---: |
| 1 | 89.169 | 94.353 | 0.945062× | no |
| 2 | 92.272 | 96.817 | 0.953061× | yes |
| 4 | 119.937 | 115.250 | 1.040673× | yes |
| 8 | 129.441 | 136.225 | 0.950200× | yes |
| 16 | 155.313 | 150.418 | 1.032546× | yes |
| 32 | 180.114 | 176.897 | 1.018183× | yes |
| 64 | 206.322 | 193.938 | 1.063855× | yes |
| 128 | 199.105 | 202.114 | 0.985115× | yes |
| 256 | 202.497 | 205.826 | 0.983829× | yes |
| 512 | 213.762 | 217.026 | 0.984960× | yes |
| 1024 | 233.619 | 230.403 | 1.013956× | yes |
| 2048 | 313.219 | 322.163 | 0.972238× | yes |
| 4096 | 476.916 | 487.109 | 0.979074× | yes |
| 8192 | 781.334 | 834.281 | 0.936536× | yes |

8–8192 geometric speedup: 0.992158×. All14 rows retained;1/2/4 excluded only from this aggregate.

One serial A/B pair does not cancel temporal drift. Use a full A2/B2 pair if regressions or small changes are ambiguous; never replace selected rows. MAD describes within-arm sample spread, not a causal confidence interval.
