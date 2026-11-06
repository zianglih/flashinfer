# Corrected explicit-K native AUTO screen

R2 patch6379bed2 passed210 exact changing-data/route replays and21 host tests before this screen. Three models ran sequential NV/MX families on their originalGPU2/3/4, tokens4/32/128/512/4096, freshAUTO,10warmups/100cold-L2CUDAgraphCUPTI iterations. NV times its initial activation quantizer; MX does not. Controls are the already-recorded clean dea2 same-GPU sweeps. The older MX parser defect is explicitly bridged; no control was rerun.

All source/runtime/GPU/timer/route/arm-contract checks passed. Allsix families exited0, with no unsupported-tactic warnings. Current source remains unstaged; this candidate is not retained.

| Model | Backend | Decode GM (4/32/128/512) | T4096 |
|---|---|---:|---:|
| v3 | CuteDSL W4A4 | 0.997339× | 0.998009× |
| v3 | CuteDSL PER-TOKEN | 0.999012× | 1.000486× |
| v3 | CuteDSL MXFP8 | 1.001017× | 0.998381× |
| v3 | CuteDSL MXFP4x8 | 0.997039× | 0.997811× |
| v3 | CuteDSL W4A16 | 0.997533× | 1.003649× |
| v41-flash | CuteDSL W4A4 | 1.007016× | 1.017568× |
| v41-flash | CuteDSL PER-TOKEN | 1.000345× | 1.012826× |
| v41-flash | CuteDSL MXFP8 | 0.998036× | 1.010250× |
| v41-flash | CuteDSL MXFP4x8 | 0.997883× | 1.034199× |
| v41-flash | CuteDSL W4A16 | 0.999532× | 1.048343× |
| kimi-k3 | CuteDSL W4A4 | 0.998636× | 0.946822× |
| kimi-k3 | CuteDSL PER-TOKEN | 1.000726× | 0.962917× |
| kimi-k3 | CuteDSL MXFP8 | 0.999994× | 0.971737× |
| kimi-k3 | CuteDSL MXFP4x8 | 0.998696× | 0.965423× |
| kimi-k3 | CuteDSL W4A16 | 0.999032× | 0.950641× |

Ratios are control/candidate latency; values above1 favor the candidate. V4.1NV T4 improves2.10%; K3T4096 loses~3–5% across affected formats, repeating R1. W4A16 is unchanged source but its K3T4096 result drifts−4.94% with the same cached tactic, so a causal fixed-tactic scheduler comparison is necessary before attribution. V3NV T4 choosesN32/K8,4 and loses1.38%; V3mixedT512 choosesK4,8 and loses1.47%.

The combined source includes planner, broader geometry, generalized CLC and explicitK; no isolated-K claim follows. R2 exposed the formerly invalidN256K8 tactics but did not remove the K3prefill loss. Test agent received exactR2cachechoices for all-static vsall-CLC probes (K3T4096 allaffectedformats, V4.1T4NV), preserving source and K/geometry.

TRT ratios in comparison.json use the archived control TRT medians and are marked provisional cross-sweep comparisons. They are not refreshed current TRT tables.

CuTe-only processwalltime NV/MXseconds: V3236.9/252.7,V4.1241.2/278.2,K3251.1/250.7. This includes first-use compilation/nativeAUTO; no unique core-compilation count is recorded.180rawtactics yield160hardware-admitted chains, with compile-cache sharing across phase combinations.
