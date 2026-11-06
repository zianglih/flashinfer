# Complete fixed-tactic screen

Control/candidate geomean: **0.99971x overall, 1.00081x decode, 0.99862x prefill**. These are bounded diagnostic measurements, without native AUTO search or a retention decision.

27/48 point estimates improve, 16/48 improve in both temporal comparisons, and 11/48 regress in both. Median absolute control drift is 0.090%; maximum 3.160%.

Candidate `e1f42b2a92aeef3ce662e21c9729481ae2ebd50c3d50a72cdda38d3d121cfde9` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. All points pass source/cache/tactic/routing/selector and 100-raw-sample checks. The source gate passes 64 CLC plus 24 static exact replays per source across 32 plus 12 core pairs, without spills or geometry/storage/pipeline/UMMA changes. Summed static instruction delta is +209 for CLC and +60 for static. This is not a dynamic instruction total.

Fixed native all-CLC CAAC; same-GPU source-matched final TMEM-V1 control reused as opening control followed by fresh candidate/candidate/control, 10 warmups/100 cold-L2 CUPTI graph samples, input quantization included for NV. No native AUTO, TRTLLM, W4A16, or TMEM-V1 candidate timings.

Opening controls are copied with exact source, GPU UUID, receipt and result hashes; each is followed by fresh candidate/candidate/control. No previous candidate timing is reused.

| Model | Backend | Geomean C/A |
| --- | --- | ---: |
| v3 | CuteDSL W4A4 | 1.00050x |
| v3 | CuteDSL PER-TOKEN | 0.99885x |
| v3 | CuteDSL MXFP4x8 | 0.99801x |
| v3 | CuteDSL MXFP8 | 1.00422x |
| v41-flash | CuteDSL W4A4 | 0.99991x |
| v41-flash | CuteDSL PER-TOKEN | 1.00044x |
| v41-flash | CuteDSL MXFP4x8 | 1.00227x |
| v41-flash | CuteDSL MXFP8 | 0.99558x |
| kimi-k3 | CuteDSL W4A4 | 0.99979x |
| kimi-k3 | CuteDSL PER-TOKEN | 0.99983x |
| kimi-k3 | CuteDSL MXFP4x8 | 1.00150x |
| kimi-k3 | CuteDSL MXFP8 | 0.99570x |

All entries below are raw per-arm medians in microseconds. C0 is reused; A1, A2 and C3 are fresh. C/A is mean(C0,C3)/mean(A1,A2); forward is C0/A1, reverse C3/A2, and control drift is C3/C0−1.

| Model | Backend | Tokens | C0 µs | A1 µs | A2 µs | C3 µs | C/A | Forward | Reverse | Control drift |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3 | CuteDSL W4A4 | 32 | 102.256 | 102.209 | 102.305 | 102.049 | 0.99898x | 1.00046x | 0.99750x | -0.202% |
| v3 | CuteDSL W4A4 | 128 | 138.545 | 138.113 | 138.065 | 138.656 | 1.00370x | 1.00312x | 1.00428x | +0.080% |
| v3 | CuteDSL W4A4 | 4096 | 211.361 | 211.137 | 211.216 | 210.593 | 0.99906x | 1.00106x | 0.99705x | -0.363% |
| v3 | CuteDSL W4A4 | 16384 | 562.323 | 561.939 | 561.923 | 561.842 | 1.00027x | 1.00068x | 0.99986x | -0.085% |
| v3 | CuteDSL PER-TOKEN | 32 | 106.209 | 106.369 | 106.337 | 106.369 | 0.99940x | 0.99850x | 1.00030x | +0.151% |
| v3 | CuteDSL PER-TOKEN | 128 | 142.817 | 142.753 | 143.024 | 143.072 | 1.00039x | 1.00045x | 1.00034x | +0.179% |
| v3 | CuteDSL PER-TOKEN | 4096 | 252.690 | 254.113 | 253.346 | 252.945 | 0.99640x | 0.99440x | 0.99842x | +0.101% |
| v3 | CuteDSL PER-TOKEN | 16384 | 683.684 | 684.148 | 684.005 | 683.364 | 0.99919x | 0.99932x | 0.99906x | -0.047% |
| v3 | CuteDSL MXFP8 | 32 | 165.105 | 165.425 | 165.089 | 165.457 | 1.00014x | 0.99807x | 1.00223x | +0.213% |
| v3 | CuteDSL MXFP4x8 | 32 | 100.656 | 100.368 | 100.384 | 100.368 | 1.00135x | 1.00287x | 0.99984x | -0.287% |
| v3 | CuteDSL MXFP8 | 128 | 230.306 | 230.401 | 229.922 | 230.338 | 1.00070x | 0.99959x | 1.00181x | +0.014% |
| v3 | CuteDSL MXFP4x8 | 128 | 135.794 | 135.537 | 135.569 | 135.745 | 1.00160x | 1.00189x | 1.00130x | -0.036% |
| v3 | CuteDSL MXFP8 | 4096 | 304.610 | 304.946 | 304.786 | 304.562 | 0.99908x | 0.99890x | 0.99926x | -0.016% |
| v3 | CuteDSL MXFP4x8 | 4096 | 228.706 | 228.913 | 228.721 | 228.641 | 0.99937x | 0.99909x | 0.99965x | -0.028% |
| v3 | CuteDSL MXFP8 | 16384 | 811.078 | 767.781 | 807.606 | 791.206 | 1.01707x | 1.05639x | 0.97969x | -2.450% |
| v3 | CuteDSL MXFP4x8 | 16384 | 719.749 | 739.717 | 719.013 | 724.069 | 0.98978x | 0.97301x | 1.00703x | +0.600% |
| v41-flash | CuteDSL W4A4 | 32 | 127.072 | 126.945 | 126.993 | 126.945 | 1.00031x | 1.00100x | 0.99962x | -0.100% |
| v41-flash | CuteDSL W4A4 | 128 | 263.344 | 263.217 | 263.281 | 262.945 | 0.99960x | 1.00048x | 0.99872x | -0.152% |
| v41-flash | CuteDSL W4A4 | 4096 | 351.889 | 352.034 | 352.018 | 352.450 | 1.00041x | 0.99959x | 1.00123x | +0.159% |
| v41-flash | CuteDSL W4A4 | 16384 | 636.355 | 636.179 | 636.803 | 635.747 | 0.99931x | 1.00028x | 0.99834x | -0.096% |
| v41-flash | CuteDSL PER-TOKEN | 32 | 132.464 | 132.192 | 132.257 | 132.481 | 1.00187x | 1.00206x | 1.00169x | +0.012% |
| v41-flash | CuteDSL PER-TOKEN | 128 | 271.377 | 271.313 | 271.394 | 271.585 | 1.00047x | 1.00024x | 1.00070x | +0.077% |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 406.851 | 407.138 | 406.914 | 406.721 | 0.99941x | 0.99929x | 0.99953x | -0.032% |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 808.291 | 808.820 | 807.956 | 808.515 | 1.00002x | 0.99935x | 1.00069x | +0.028% |
| v41-flash | CuteDSL MXFP8 | 32 | 213.489 | 213.233 | 213.393 | 213.746 | 1.00143x | 1.00120x | 1.00165x | +0.120% |
| v41-flash | CuteDSL MXFP4x8 | 32 | 122.832 | 122.849 | 122.737 | 122.785 | 1.00013x | 0.99987x | 1.00039x | -0.039% |
| v41-flash | CuteDSL MXFP8 | 128 | 462.324 | 462.082 | 462.659 | 462.323 | 0.99990x | 1.00052x | 0.99927x | -0.000% |
| v41-flash | CuteDSL MXFP4x8 | 128 | 255.282 | 255.202 | 255.313 | 255.394 | 1.00031x | 1.00031x | 1.00032x | +0.044% |
| v41-flash | CuteDSL MXFP8 | 4096 | 587.156 | 587.316 | 587.252 | 587.219 | 0.99984x | 0.99973x | 0.99994x | +0.011% |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 360.659 | 360.738 | 360.899 | 360.562 | 0.99942x | 0.99978x | 0.99907x | -0.027% |
| v41-flash | CuteDSL MXFP8 | 16384 | 965.670 | 1005.542 | 993.670 | 996.183 | 0.98131x | 0.96035x | 1.00253x | +3.160% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 870.854 | 857.685 | 871.221 | 874.021 | 1.00924x | 1.01535x | 1.00321x | +0.364% |
| kimi-k3 | CuteDSL W4A4 | 32 | 177.057 | 177.394 | 177.297 | 177.489 | 0.99959x | 0.99810x | 1.00108x | +0.244% |
| kimi-k3 | CuteDSL W4A4 | 128 | 297.426 | 297.298 | 297.618 | 297.714 | 1.00038x | 1.00043x | 1.00032x | +0.097% |
| kimi-k3 | CuteDSL W4A4 | 4096 | 414.947 | 415.203 | 415.235 | 414.819 | 0.99919x | 0.99938x | 0.99900x | -0.031% |
| kimi-k3 | CuteDSL W4A4 | 16384 | 900.694 | 899.399 | 900.583 | 899.303 | 1.00001x | 1.00144x | 0.99858x | -0.154% |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 182.209 | 181.970 | 182.162 | 182.002 | 1.00022x | 1.00132x | 0.99912x | -0.114% |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 306.626 | 306.307 | 306.515 | 306.642 | 1.00073x | 1.00104x | 1.00042x | +0.005% |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 478.148 | 478.228 | 478.884 | 477.843 | 0.99883x | 0.99983x | 0.99783x | -0.064% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1237.305 | 1237.979 | 1236.745 | 1236.330 | 0.99956x | 0.99946x | 0.99966x | -0.079% |
| kimi-k3 | CuteDSL MXFP8 | 32 | 299.442 | 298.994 | 299.265 | 300.115 | 1.00217x | 1.00150x | 1.00284x | +0.225% |
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 171.089 | 170.689 | 170.817 | 171.042 | 1.00183x | 1.00234x | 1.00131x | -0.028% |
| kimi-k3 | CuteDSL MXFP8 | 128 | 520.900 | 519.699 | 519.907 | 520.676 | 1.00189x | 1.00231x | 1.00148x | -0.043% |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 291.618 | 290.721 | 291.298 | 291.778 | 1.00237x | 1.00308x | 1.00165x | +0.055% |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 674.821 | 674.116 | 674.053 | 675.317 | 1.00146x | 1.00105x | 1.00187x | +0.073% |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 435.827 | 435.044 | 435.379 | 436.531 | 1.00222x | 1.00180x | 1.00265x | +0.162% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1314.649 | 1351.545 | 1361.418 | 1337.274 | 0.97750x | 0.97270x | 0.98227x | +1.721% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1241.545 | 1247.129 | 1253.624 | 1258.185 | 0.99959x | 0.99552x | 1.00364x | +1.340% |

Evidence: `results/full-screen-v2-summary.json`, `results/gate-v2-validation.json`, `results/collection.json`, and all cell receipts/raw outputs. Frozen source and helper bindings: `launch.json` and `helper-freeze.json`.

- Summary SHA256: `4274268be6e890cc1c9959424a516c5b26c47b49a4a9ba89e3f616c0db3a63d8`
- Combined gate SHA256: `35a68e525b1dbde60952c7d0e5033e29010de09fcf33b475c05cbb4fe2003a2f`
