# FC2 CLC fixed-native screen results

Source `0def601d` plus one wrapper request; no kernel or tactic-list change. All 10 C–A–A–C screens (40 processes) passed source, cache-hit, routing, effective CLC/prefetch and raw-sample checks. Each number derives from the median of two full-precision 100-sample medians; paired ratios are shown separately. These are fixed-tactic diagnostic results, not native AUTO retention evidence.

| Screen | Tokens | Backend | Control us | FC2 CLC us | Ratio | Pair 1 / Pair 2 |
|---|---:|---|---:|---:|---:|---:|
| broad-k3-mx-prefill | 4096 | CuteDSL MXFP8 | 650.116750 | 653.044250 | 0.995517 | 0.995395 / 0.995640 |
| broad-k3-mx-prefill | 4096 | CuteDSL MXFP4x8 | 396.754750 | 410.298750 | 0.966990 | 0.966715 / 0.967265 |
| broad-k3-nv-prefill | 4096 | CuteDSL W4A4 | 388.626750 | 400.603000 | 0.970104 | 0.969769 / 0.970440 |
| broad-k3-nv-prefill | 4096 | CuteDSL PER-TOKEN | 557.235750 | 569.099500 | 0.979153 | 0.978700 / 0.979607 |
| broad-k3-nv-prefill | 4096 | CuteDSL W4A16 | 653.932000 | 648.843750 | 1.007842 | 0.943469 / 1.077505 |
| broad-k3-per-token-decode | 32 | CuteDSL PER-TOKEN | 187.649500 | 187.161000 | 1.002610 | 1.002909 / 1.002311 |
| broad-k3-per-token-decode | 128 | CuteDSL PER-TOKEN | 317.066000 | 314.537750 | 1.008038 | 1.006867 / 1.009209 |
| broad-v3-mx-prefill | 4096 | CuteDSL MXFP8 | 305.161500 | 305.066250 | 1.000312 | 1.000105 / 1.000520 |
| broad-v3-mx-prefill | 4096 | CuteDSL MXFP4x8 | 226.098000 | 230.177500 | 0.982277 | 0.982756 / 0.981797 |
| broad-v3-nv-prefill | 4096 | CuteDSL W4A4 | 207.586000 | 211.561500 | 0.981209 | 0.981698 / 0.980719 |
| broad-v3-nv-prefill | 4096 | CuteDSL PER-TOKEN | 297.618250 | 300.946000 | 0.988942 | 0.988945 / 0.988940 |
| broad-v3-nv-prefill | 4096 | CuteDSL W4A16 | 312.363000 | 312.714000 | 0.998878 | 0.998060 / 0.999696 |
| broad-v3-per-token-decode | 32 | CuteDSL PER-TOKEN | 106.624750 | 106.392000 | 1.002188 | 1.003923 / 1.000455 |
| broad-v3-per-token-decode | 128 | CuteDSL PER-TOKEN | 144.993250 | 145.001250 | 0.999945 | 0.997678 / 1.002209 |
| k3-mx | 32 | CuteDSL MXFP8 | 301.265500 | 299.569750 | 1.005661 | 1.006462 / 1.004859 |
| k3-mx | 32 | CuteDSL MXFP4x8 | 172.857000 | 171.777000 | 1.006287 | 1.006893 / 1.005681 |
| k3-mx | 64 | CuteDSL MXFP8 | 416.802250 | 413.162250 | 1.008810 | 1.008247 / 1.009373 |
| k3-mx | 64 | CuteDSL MXFP4x8 | 233.200750 | 231.953250 | 1.005378 | 1.005517 / 1.005239 |
| k3-mx | 128 | CuteDSL MXFP8 | 524.474500 | 520.139000 | 1.008335 | 1.007405 / 1.009267 |
| k3-mx | 128 | CuteDSL MXFP4x8 | 292.953250 | 291.489500 | 1.005022 | 1.004662 / 1.005382 |
| k3-mx | 512 | CuteDSL MXFP8 | 595.675000 | 590.004000 | 1.009612 | 1.008917 / 1.010308 |
| k3-mx | 512 | CuteDSL MXFP4x8 | 338.593750 | 348.706000 | 0.971001 | 0.970610 / 0.971392 |
| k3-nv-extension | 32 | CuteDSL W4A4 | 178.369000 | 177.409250 | 1.005410 | 1.006129 / 1.004691 |
| k3-nv-extension | 32 | CuteDSL W4A16 | 187.824750 | 187.665000 | 1.000851 | 1.000679 / 1.001023 |
| k3-nv-extension | 512 | CuteDSL W4A4 | 342.641500 | 338.794000 | 1.011356 | 1.011714 / 1.010999 |
| k3-nv-extension | 512 | CuteDSL W4A16 | 375.345750 | 374.553750 | 1.002115 | 1.001966 / 1.002263 |
| priority-k3-nv | 64 | CuteDSL W4A4 | 241.121000 | 239.584750 | 1.006412 | 1.006547 / 1.006278 |
| priority-k3-nv | 64 | CuteDSL W4A16 | 253.304750 | 252.953000 | 1.001391 | 1.001325 / 1.001456 |
| priority-k3-nv | 128 | CuteDSL W4A4 | 300.000750 | 296.953250 | 1.010263 | 1.010017 / 1.010508 |
| priority-k3-nv | 128 | CuteDSL W4A16 | 317.217750 | 316.553250 | 1.002099 | 1.002987 / 1.001213 |
| priority-v41-mx8 | 128 | CuteDSL MXFP8 | 468.873750 | 464.458000 | 1.009507 | 1.009647 / 1.009368 |

Unconditional FC2 CLC is rejected: decode gains are repeatable, but mixed T512 and most T4096 formats regress. This supports independent FC2 scheduler autotuning, with no shape-specific default policy. Unchanged K3 W4A16 T4096 is noisy and is not used to attribute a scheduler gain.
