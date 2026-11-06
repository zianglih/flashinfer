# Scatter4 r4 matched screen interpretation

Source `8d8af271` versus retained `b45b218b` only; the sole-announcer change is not composed into either screen arm. All 64 cells, 48 public processes and 25,600 CUPTI samples passed independent source/route/tactic/geometry checks. The archive has 1,024 verified manifest entries. Standard full-100-sample medians remain primary.

| Model | W4A4 | Per-token | MXFP4x8 | MXFP8 |
|---|---:|---:|---:|---:|
| v3 | +0.443% | +0.497% | +0.433% | -0.608% |
| v41-flash | +0.306% | +0.224% | +0.050% | +0.038% |
| kimi-k3 | -0.127% | -0.034% | -0.223% | -0.151% |
| nemo3-ultra | -0.173% | -0.118% | -0.348% | -0.132% |

Primary GM: overall +0.004%, decode +0.011%, prefill −0.002%. All 32 prefill cells used the bulk64 FC2 path; all 32 decode cells used bulk0. This is performance-neutral overall, with positive NV and negative MX tradeoffs.

Diagnostic prefill GM first25 +0.140%, last25 +0.088%, last50 +0.283%. Do not substitute these strata for the primary full medians.

V3 T16384 NV improvements are stable across both passes and time strata: W4A4 +1.314% (control/candidate spreads 0.032%/0.085%) and per-token +1.532% (0.072%/0.073%). Small repeatable costs include V3 MXFP4x8 T4096 −0.403% and V41F W4A4 T4096 −0.364%.

V3 MXFP8 T16384 has primary −2.351% with narrow pass-median spreads, but first25 is +0.730% and last50 −1.055%. Other 16K cells also change sign or magnitude by stratum. The established timing-band transition remains a limitation; do not claim an isolated source regression or gain from those medians.

Retention therefore depends on whether the reduced transaction count and final implementation quality justify a neutral performance tradeoff. The screen does not show a broad speedup. Bulk32 full-chain correctness is a separate gate owned by the epilogue agent, not established by these native winners.
