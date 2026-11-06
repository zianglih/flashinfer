# Deferred bulk-drain fixed screen

Complete: True. Control/candidate use identical retained native winners on GPU2. Ratio >1 favors deferred drain; identical native tactics, public full-chain timing, no AUTO search.

| Case | Control C1/C2 (ms) | Candidate A1/A2 (ms) | Control / Candidate |
|---|---:|---:|---:|
| decode-v3-cute-dsl-per-token | 0.143137 / 0.142977 | 0.143009 / 0.143136 | 0.999890× |
| decode-v41-flash-cute-dsl-w4a8 | 0.254418 / 0.254337 | 0.254321 / 0.254482 | 0.999904× |
| decode-kimi-k3-cute-dsl-mxfp8 | 0.520690 / 0.521186 | 0.520946 / 0.521218 | 0.999723× |
| decode-nemo3-ultra-cutedsl | 0.136640 / 0.136577 | 0.136672 / 0.136705 | 0.999417× |
| prefill-v3-cutedsl | 0.526017 / 0.525362 | 0.525362 / 0.525138 | 1.000837× |
| prefill-v3-cute-dsl-mxfp8 | 0.754612 / 0.770660 | 0.772115 / 0.766228 | 0.991455× |
| prefill-kimi-k3-cutedsl | 0.819732 / 0.818724 | 0.814052 / 0.797219 | 1.016927× |
| prefill-nemo3-ultra-cutedsl | 0.580323 / 0.584340 | 0.581906 / 0.583779 | 0.999118× |

Ratios are full-chain control/candidate with identical source-bound saved tactics and native timing. Interpret repeat drift alongside each paired effect. NV includes initial quantization; MX excludes it. Telemetry records process boundaries, not in-timer sampling.

Raw samples: 3200. Source/cache/route/dispatch checks passed for every completed row.
