Independently checked 16 measurements / 1600 raw samples.

| Case | C1 / A1 / A2 / C2 (ms) | C/A geometric ratio | Candidate latency change |
|---|---|---:|---:|
| v3-nvfp4 | 0.525443 / 0.525027 / 0.524242 / 0.525667 | 1.001755 | -0.175% |
| v3-mxfp | 0.770004 / 0.752212 / 0.779219 / 0.789969 | 1.018712 | -1.837% |
| kimi-k3-nvfp4 | 0.804322 / 0.823154 / 0.788884 / 0.814307 | 1.004297 | -0.428% |
| nemo3-ultra-nvfp4 | 0.581298 / 0.575571 / 0.579362 / 0.580994 | 1.006377 | -0.634% |

Ratio above 1 means lower candidate latency. Sources differ only in the kernel core; benchmark bytes, native tactics, actual dispatch, routes and runtime match across each bracket.

Drift across each bracket (second run / first run):
- v3-nvfp4: control +0.043%, candidate -0.149%; adjacent C/A ratios 1.000793 and 1.002718.
- v3-mxfp: control +2.593%, candidate +3.590%; adjacent C/A ratios 1.023652 and 1.013796.
- kimi-k3-nvfp4: control +1.241%, candidate -4.163%; adjacent C/A ratios 0.977122 and 1.032227.
- nemo3-ultra-nvfp4: control -0.052%, candidate +0.659%; adjacent C/A ratios 1.009950 and 1.002817.

These are bounded screening estimates, not statistical significance claims. Drift larger than the paired effect limits any claim of a repeatable gain.

Pending: none
