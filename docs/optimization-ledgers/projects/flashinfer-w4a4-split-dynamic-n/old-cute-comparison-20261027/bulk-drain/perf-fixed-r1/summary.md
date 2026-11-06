# Deferred bulk-drain fixed screen

Complete: True. Control/candidate use identical retained native winners on GPU2. Ratio >1 favors deferred drain; identical native tactics, public full-chain timing, no AUTO search.

| Case | Control C1/C2 (ms) | Candidate A1/A2 (ms) | Control / Candidate |
|---|---:|---:|---:|
| v3-nvfp4 | 0.525443 / 0.525667 | 0.525027 / 0.524242 | 1.001755× |
| v3-mxfp | 0.770004 / 0.789969 | 0.752212 / 0.779219 | 1.018712× |
| kimi-k3-nvfp4 | 0.804322 / 0.814307 | 0.823154 / 0.788884 | 1.004297× |
| nemo3-ultra-nvfp4 | 0.581298 / 0.580994 | 0.575571 / 0.579362 | 1.006377× |

Repeat/uncertainty: V3 NV is near-neutral; V3 MX control/candidate drift exceeds its paired effect; K3 adjacent comparisons disagree in direction. Nemo has two positive adjacent comparisons with a small paired effect. These data do not establish a universal stable speedup.

NV includes initial activation quantization; MX excludes it. Both sources use the same benchmark, routes, saved native tactic and native timing (10 warmups, 100 CUPTI cold-L2 samples per leg). Only the bulk-drain core differs. Bounded static-scheduler evidence; CLC/inline coverage remains a retention prerequisite if useful.

Raw samples: 1600. All listed source/cache/dispatch/runtime checks passed.
