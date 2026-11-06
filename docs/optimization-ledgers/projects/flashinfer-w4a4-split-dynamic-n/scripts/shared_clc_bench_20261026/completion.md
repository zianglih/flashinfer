# Shared CLC comparison complete

Validated 195 cells / 78,000 raw public samples; 132 retention cells exclude tokens 1/2 and unchanged W4A16. Overall speedup 0.999551x (decode 0.999487x; prefill 0.999722x).

Raw tactics halve from720 to360; admitted tactics halve from640 to320 for every observed format/profile. Observed pre-warm AUTO context totals 4277.4s → 2833.4s (33.8% lower); this includes JIT/IO and shared CPU contention, not an isolated compiler benchmark.

| Model | Format | Decode GM | Prefill GM |
|---|---|---:|---:|
|kimi-k3|CuteDSL MXFP4x8|1.00241x|0.99746x|
|kimi-k3|CuteDSL MXFP8|1.00019x|1.00028x|
|kimi-k3|CuteDSL PER-TOKEN|1.00093x|1.00233x|
|kimi-k3|CuteDSL W4A4|0.99899x|1.00695x|
|v3|CuteDSL MXFP4x8|0.99653x|0.99496x|
|v3|CuteDSL MXFP8|1.00104x|1.01059x|
|v3|CuteDSL PER-TOKEN|0.99567x|1.00049x|
|v3|CuteDSL W4A4|0.99565x|0.99985x|
|v41-flash|CuteDSL MXFP4x8|0.99851x|0.99917x|
|v41-flash|CuteDSL MXFP8|1.00137x|1.00032x|
|v41-flash|CuteDSL PER-TOKEN|1.00079x|0.99402x|
|v41-flash|CuteDSL W4A4|1.00180x|0.99042x|

Stable losses worth noting: V3 per-token T4 0.97510x (pairs0.97196/0.97826), V4.1 MXFP4x8 T4 0.98309x (0.98575/0.98044), V3 W4A4 T16 0.98342x (0.98319/0.98366), V4.1 per-token T4096 0.98530x (0.98427/0.98632). These switch from mixed phase schedules to shared schedules.

The numerically worst K3 MXFP4x8 T16384 row is0.97508x, but its pair ratios disagree strongly (1.03292 vs0.92049), with about6% within-arm drift; both winners use static/static. Do not attribute that row to lost mixed scheduling. V4.1 W4A4 T16384 is0.98569x with static/static in both arms but different fresh AUTO geometry; distinguish search noise/geometry choice from shared-flag exclusion.

No publication or source retention decision was performed. Failed MXv1 diagnostic attempts contain no public samples and are explicitly excluded; the fixed observer differs only in optional input shape encoding. Native C++ artifacts were retained on persistent storage.

## Retained 2026-10-27

User explicitly selected the shared-flag policy for retention. Pushed `9334cb34fe9c81653dc4748632f44449e9aecd8d` on top of `9c9ed58a`; the original two-file benchmark patch is unchanged. The existing 13-test result is source-identical, and fresh scoped pre-commit and host-policy equivalence checks pass. Original GPU timing remains attributed to the measured `9b4721b0` pair. The completed review checkout was advanced to the retained commit, verified clean and removed. See `retention.json`.
