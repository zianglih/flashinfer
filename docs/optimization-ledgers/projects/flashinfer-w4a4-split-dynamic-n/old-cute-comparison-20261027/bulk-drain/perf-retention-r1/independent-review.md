Independently checked 32 measurements / 3200 raw samples.

| Case | C1 / A1 / A2 / C2 (ms) | C/A geometric ratio | Candidate latency change |
|---|---|---:|---:|
| decode-v3-cute-dsl-per-token | 0.143137 / 0.143009 / 0.143136 / 0.142977 | 0.999890 | +0.011% |
| decode-v41-flash-cute-dsl-w4a8 | 0.254418 / 0.254321 / 0.254482 / 0.254337 | 0.999904 | +0.010% |
| decode-kimi-k3-cute-dsl-mxfp8 | 0.520690 / 0.520946 / 0.521218 / 0.521186 | 0.999723 | +0.028% |
| decode-nemo3-ultra-cutedsl | 0.136640 / 0.136672 / 0.136705 / 0.136577 | 0.999417 | +0.058% |
| prefill-v3-cutedsl | 0.526017 / 0.525362 / 0.525138 / 0.525362 | 1.000837 | -0.084% |
| prefill-v3-cute-dsl-mxfp8 | 0.754612 / 0.772115 / 0.766228 / 0.770660 | 0.991455 | +0.862% |
| prefill-kimi-k3-cutedsl | 0.819732 / 0.814052 / 0.797219 / 0.818724 | 1.016927 | -1.665% |
| prefill-nemo3-ultra-cutedsl | 0.580323 / 0.581906 / 0.583779 / 0.584340 | 0.999118 | +0.088% |

Ratio above 1 means lower candidate latency. Sources differ only in the kernel core; benchmark bytes, native tactics, actual dispatch, routes and runtime match across each bracket.

Drift across each bracket (second run / first run):
- decode-v3-cute-dsl-per-token: control -0.112%, candidate +0.089%; adjacent C/A ratios 1.000895 and 0.998886.
- decode-v41-flash-cute-dsl-w4a8: control -0.032%, candidate +0.063%; adjacent C/A ratios 1.000377 and 0.999430.
- decode-kimi-k3-cute-dsl-mxfp8: control +0.095%, candidate +0.052%; adjacent C/A ratios 0.999508 and 0.999939.
- decode-nemo3-ultra-cutedsl: control -0.046%, candidate +0.024%; adjacent C/A ratios 0.999770 and 0.999064.
- prefill-v3-cutedsl: control -0.125%, candidate -0.043%; adjacent C/A ratios 1.001247 and 1.000427.
- prefill-v3-cute-dsl-mxfp8: control +2.127%, candidate -0.762%; adjacent C/A ratios 0.977330 and 1.005784.
- prefill-kimi-k3-cutedsl: control -0.123%, candidate -2.068%; adjacent C/A ratios 1.006978 and 1.026974.
- prefill-nemo3-ultra-cutedsl: control +0.692%, candidate +0.322%; adjacent C/A ratios 0.997279 and 1.000961.

These are bounded screening estimates, not statistical significance claims. Drift larger than the paired effect limits any claim of a repeatable gain.

Pending: none
