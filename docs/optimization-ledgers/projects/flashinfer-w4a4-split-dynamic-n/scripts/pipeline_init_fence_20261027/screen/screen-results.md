# Complete fixed-tactic screen

Control/candidate geomean: **0.99918x overall, 1.00028x decode, 0.99808x prefill**. These are bounded diagnostic measurements, without native AUTO search or a retention decision.

30/48 point estimates improve, 18/48 improve in both temporal comparisons, and 14/48 regress in both. Median absolute control drift is 0.093%; maximum 3.737%.

Candidate `5112a25e2c70c5aec5cfdef0bbef02f1da22a08f2ad6b9240b0025c64a6753f6` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. All points pass source/cache/tactic/routing/selector and 100-raw-sample checks. The source gate passes 64 CLC plus 24 static exact replays per source across 32 plus 12 core pairs, without spills or geometry/storage/pipeline/UMMA changes. Summed static instruction delta is -240 for CLC and -55 for static. This is not a dynamic instruction total.

Fixed native all-CLC CAAC; same-GPU source-matched final TMEM-V2 control reused as opening control followed by fresh candidate/candidate/control, 10 warmups/100 cold-L2 CUPTI graph samples, input quantization included for NV. No native AUTO, TRTLLM, W4A16, or TMEM-V2 candidate timings.

Opening controls are copied with exact source, GPU UUID, receipt and result hashes; each is followed by fresh candidate/candidate/control. No previous candidate timing is reused.

| Model | Backend | Geomean C/A |
| --- | --- | ---: |
| v3 | CuteDSL W4A4 | 0.99940x |
| v3 | CuteDSL PER-TOKEN | 1.00022x |
| v3 | CuteDSL MXFP4x8 | 0.99787x |
| v3 | CuteDSL MXFP8 | 0.99189x |
| v41-flash | CuteDSL W4A4 | 1.00056x |
| v41-flash | CuteDSL PER-TOKEN | 1.00032x |
| v41-flash | CuteDSL MXFP4x8 | 1.00261x |
| v41-flash | CuteDSL MXFP8 | 0.99804x |
| kimi-k3 | CuteDSL W4A4 | 0.99974x |
| kimi-k3 | CuteDSL PER-TOKEN | 0.99988x |
| kimi-k3 | CuteDSL MXFP4x8 | 1.00204x |
| kimi-k3 | CuteDSL MXFP8 | 0.99766x |

All entries below are raw per-arm medians in microseconds. C0 is reused; A1, A2 and C3 are fresh. C/A is mean(C0,C3)/mean(A1,A2); forward is C0/A1, reverse C3/A2, and control drift is C3/C0−1.

| Model | Backend | Tokens | C0 µs | A1 µs | A2 µs | C3 µs | C/A | Forward | Reverse | Control drift |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3 | CuteDSL W4A4 | 32 | 102.049 | 102.065 | 102.144 | 102.177 | 1.00008x | 0.99985x | 1.00032x | +0.125% |
| v3 | CuteDSL W4A4 | 128 | 138.656 | 138.432 | 138.353 | 138.352 | 1.00081x | 1.00162x | 1.00000x | -0.219% |
| v3 | CuteDSL W4A4 | 4096 | 210.593 | 211.425 | 211.505 | 211.345 | 0.99766x | 0.99606x | 0.99925x | +0.357% |
| v3 | CuteDSL W4A4 | 16384 | 561.842 | 562.595 | 562.467 | 562.179 | 0.99908x | 0.99866x | 0.99949x | +0.060% |
| v3 | CuteDSL PER-TOKEN | 32 | 106.369 | 106.400 | 106.560 | 106.528 | 0.99970x | 0.99970x | 0.99970x | +0.150% |
| v3 | CuteDSL PER-TOKEN | 128 | 143.072 | 142.913 | 142.800 | 142.784 | 1.00050x | 1.00112x | 0.99989x | -0.201% |
| v3 | CuteDSL PER-TOKEN | 4096 | 252.945 | 252.865 | 253.010 | 253.154 | 1.00044x | 1.00032x | 1.00057x | +0.082% |
| v3 | CuteDSL PER-TOKEN | 16384 | 683.364 | 683.428 | 683.445 | 683.828 | 1.00023x | 0.99991x | 1.00056x | +0.068% |
| v3 | CuteDSL MXFP8 | 32 | 165.457 | 165.265 | 165.441 | 165.281 | 1.00010x | 1.00116x | 0.99903x | -0.106% |
| v3 | CuteDSL MXFP4x8 | 32 | 100.368 | 100.545 | 100.673 | 100.417 | 0.99785x | 0.99824x | 0.99746x | +0.049% |
| v3 | CuteDSL MXFP8 | 128 | 230.338 | 230.017 | 229.745 | 230.081 | 1.00143x | 1.00139x | 1.00146x | -0.111% |
| v3 | CuteDSL MXFP4x8 | 128 | 135.745 | 135.457 | 135.425 | 135.617 | 1.00177x | 1.00213x | 1.00142x | -0.094% |
| v3 | CuteDSL MXFP8 | 4096 | 304.562 | 304.210 | 303.858 | 304.434 | 1.00153x | 1.00116x | 1.00190x | -0.042% |
| v3 | CuteDSL MXFP4x8 | 4096 | 228.641 | 228.225 | 228.258 | 228.465 | 1.00137x | 1.00182x | 1.00091x | -0.077% |
| v3 | CuteDSL MXFP8 | 16384 | 791.206 | 798.213 | 810.966 | 761.637 | 0.96499x | 0.99122x | 0.93917x | -3.737% |
| v3 | CuteDSL MXFP4x8 | 16384 | 724.069 | 748.101 | 721.589 | 731.701 | 0.99053x | 0.96788x | 1.01401x | +1.054% |
| v41-flash | CuteDSL W4A4 | 32 | 126.945 | 126.945 | 126.848 | 127.040 | 1.00076x | 1.00000x | 1.00152x | +0.076% |
| v41-flash | CuteDSL W4A4 | 128 | 262.945 | 263.185 | 263.121 | 263.314 | 0.99991x | 0.99909x | 1.00073x | +0.140% |
| v41-flash | CuteDSL W4A4 | 4096 | 352.450 | 351.746 | 352.355 | 351.794 | 1.00020x | 1.00200x | 0.99841x | -0.186% |
| v41-flash | CuteDSL W4A4 | 16384 | 635.747 | 636.308 | 635.683 | 638.003 | 1.00138x | 0.99912x | 1.00365x | +0.355% |
| v41-flash | CuteDSL PER-TOKEN | 32 | 132.481 | 132.353 | 132.353 | 132.305 | 1.00030x | 1.00096x | 0.99964x | -0.132% |
| v41-flash | CuteDSL PER-TOKEN | 128 | 271.585 | 271.120 | 271.233 | 271.330 | 1.00103x | 1.00171x | 1.00036x | -0.094% |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 406.721 | 406.386 | 406.658 | 406.690 | 1.00045x | 1.00083x | 1.00008x | -0.008% |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 808.515 | 809.075 | 808.100 | 807.812 | 0.99948x | 0.99931x | 0.99964x | -0.087% |
| v41-flash | CuteDSL MXFP8 | 32 | 213.746 | 213.377 | 213.441 | 213.313 | 1.00057x | 1.00173x | 0.99940x | -0.202% |
| v41-flash | CuteDSL MXFP4x8 | 32 | 122.785 | 122.720 | 122.689 | 122.672 | 1.00020x | 1.00053x | 0.99987x | -0.091% |
| v41-flash | CuteDSL MXFP8 | 128 | 462.323 | 462.755 | 462.963 | 462.867 | 0.99943x | 0.99907x | 0.99979x | +0.118% |
| v41-flash | CuteDSL MXFP4x8 | 128 | 255.394 | 255.362 | 255.298 | 255.522 | 1.00050x | 1.00013x | 1.00088x | +0.050% |
| v41-flash | CuteDSL MXFP8 | 4096 | 587.219 | 587.107 | 586.963 | 586.980 | 1.00011x | 1.00019x | 1.00003x | -0.041% |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 360.562 | 360.594 | 360.850 | 360.530 | 0.99951x | 0.99991x | 0.99911x | -0.009% |
| v41-flash | CuteDSL MXFP8 | 16384 | 996.183 | 1007.782 | 1006.198 | 1001.878 | 0.99210x | 0.98849x | 0.99571x | +0.572% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 874.021 | 866.726 | 865.189 | 875.701 | 1.01028x | 1.00842x | 1.01215x | +0.192% |
| kimi-k3 | CuteDSL W4A4 | 32 | 177.489 | 177.521 | 177.602 | 177.457 | 0.99950x | 0.99982x | 0.99919x | -0.018% |
| kimi-k3 | CuteDSL W4A4 | 128 | 297.714 | 296.994 | 297.346 | 297.506 | 1.00148x | 1.00243x | 1.00054x | -0.070% |
| kimi-k3 | CuteDSL W4A4 | 4096 | 414.819 | 415.059 | 415.091 | 414.803 | 0.99936x | 0.99942x | 0.99930x | -0.004% |
| kimi-k3 | CuteDSL W4A4 | 16384 | 899.303 | 900.151 | 900.487 | 898.807 | 0.99860x | 0.99906x | 0.99813x | -0.055% |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 182.002 | 182.305 | 182.370 | 182.194 | 0.99868x | 0.99833x | 0.99903x | +0.105% |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 306.642 | 307.202 | 307.347 | 306.467 | 0.99766x | 0.99818x | 0.99714x | -0.057% |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 477.843 | 476.532 | 476.292 | 478.132 | 1.00331x | 1.00275x | 1.00386x | +0.060% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1236.330 | 1237.531 | 1237.706 | 1238.634 | 0.99989x | 0.99903x | 1.00075x | +0.186% |
| kimi-k3 | CuteDSL MXFP8 | 32 | 300.115 | 299.554 | 299.346 | 299.922 | 1.00190x | 1.00187x | 1.00192x | -0.064% |
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 171.042 | 170.977 | 171.025 | 171.041 | 1.00024x | 1.00038x | 1.00009x | -0.000% |
| kimi-k3 | CuteDSL MXFP8 | 128 | 520.676 | 520.356 | 520.612 | 521.699 | 1.00135x | 1.00062x | 1.00209x | +0.197% |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 291.778 | 291.601 | 291.394 | 291.858 | 1.00110x | 1.00061x | 1.00159x | +0.027% |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 675.317 | 674.500 | 675.317 | 675.413 | 1.00068x | 1.00121x | 1.00014x | +0.014% |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 436.531 | 436.147 | 436.547 | 436.691 | 1.00061x | 1.00088x | 1.00033x | +0.037% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1337.274 | 1380.169 | 1333.785 | 1340.793 | 0.98678x | 0.96892x | 1.00525x | +0.263% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1258.185 | 1265.801 | 1262.697 | 1286.073 | 1.00623x | 0.99398x | 1.01851x | +2.217% |

Evidence: `results/full-screen-summary.json`, `results/gate-validation.json`, `results/collection.json`, and all cell receipts/raw outputs. Frozen source and helper bindings: `launch.json` and `helper-freeze.json`.

- Summary SHA256: `d192e13d9ccc30e6ff982ef0e92431c2ad4bad2227cc4c03462c7d498f4f7aff`
- Combined gate SHA256: `41ef205d56f091282fcc4723f7ee44a3abe0398b6b147827d9a88680ef61d312`
