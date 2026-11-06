# Retained TP pipeline profiles

Source: PR7290 retained `61c2c367`; remote Git metadata61249 plus byte-identical retained patch. Source348-file hashes and raw-report manifests are recorded in `results.json`. B300/CUDA13.2,20 graph replays, frozen public-API winners/routes, PDL enabled, unfused swap-AB MXFP4x8 at16384 tokens. These NSYS timings diagnose stage costs; CUPTI paired runs decide retention.

| Model | Graph (us) | Prepare extension | FC1 extension | FC2 extension | Combine extension |
|---|---:|---:|---:|---:|---:|
| tp-v3-mxfp | 1459.77 | 311.17 | 341.22 | 429.73 | 337.87 |
| tp-kimi-k3-mxfp | 1753.92 | 303.68 | 556.76 | 546.74 | 338.23 |

Extension is the newly covered timeline interval after accounting for prior kernel overlap, not an inferred dependency-DAG critical path. Medians of separate components need not sum exactly to the median graph span.

Preparation and combine together account for about44% of V3 and37% of K3 graph time. This supports auditing data movement alongside GEMM pipeline work. It does not by itself identify avoidable time or predict a speedup.
