# TMEM scheduler startup: complete fixed-tactic screen

This screen is timing-neutral: control/candidate geomean **1.00054x overall, 1.00038x decode, 1.00070x prefill**. It does not establish an end-to-end speedup. The change removes the scheduler's TMEM readiness dependency while retaining full-warp CLC. One-CTA CLC gains an initialization join; worker warps retain the TMEM wait.

31/48 point estimates improve; 18/48 improve in both temporal comparisons and 7/48 regress in both. Median absolute opening-to-closing control drift is 0.069%, maximum 3.407%. The largest apparent regression, V4.1-Flash MXFP8 at 16K, changes sign between forward and reverse comparisons and has 3.407% control drift. Small ratios and that row should not be described as causal gains or losses.

Candidate patch `be8a12bb3090703aea918d3d0b72e7cd4cd0a678de97a25ab1ea5f83d3f36373` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. All 48 points pass source, frozen cache, six-field True/True tactics, routes, backend selectors, PDL, initial-quantization policy, and 100-raw-sample checks. The combined gate passes 64 CLC plus 16 static exact replays per source and 32 plus 8 core pairs, without spills or geometry/storage/pipeline/UMMA changes. CLC static SASS increases by 193 summed instructions (2–18/core), registers −4…+2; static kernels add 18 summed instructions, registers −2…0. No overall instruction count reduction is claimed.

C3 B300, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1; six workers on GPUs 0–5, one model/family per GPU. Tokens 32/128/4096/16384; V3 EP8, V4.1-Flash EP4, Kimi K3 EP8. The public DeepSeek benchmark runs standard/per-token NVFP4 and MXFP4x8/MXFP8 with PDL on, fused finalize off, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. NVFP4 includes initial activation quantization. No TRTLLM, W4A16 or native AUTO timing is repeated.

Each C–A–A–C series reuses the exact latest same-GPU/source/tactic closing control from the completed owner-v3 screen, then measures fresh candidate, candidate, control. No owner candidate timing is reused. Per-cell receipts preserve and validate the prior receipt, result hash and chronology. Native C++ compilation caches are retained; DSL caches are source-private.

| Model | Backend | Geomean C/A |
| --- | --- | ---: |
| v3 | CuteDSL W4A4 | 1.00109x |
| v3 | CuteDSL PER-TOKEN | 1.00003x |
| v3 | CuteDSL MXFP4x8 | 1.00192x |
| v3 | CuteDSL MXFP8 | 1.00496x |
| v41-flash | CuteDSL W4A4 | 0.99991x |
| v41-flash | CuteDSL PER-TOKEN | 0.99996x |
| v41-flash | CuteDSL MXFP4x8 | 1.00151x |
| v41-flash | CuteDSL MXFP8 | 0.99585x |
| kimi-k3 | CuteDSL W4A4 | 1.00058x |
| kimi-k3 | CuteDSL PER-TOKEN | 0.99992x |
| kimi-k3 | CuteDSL MXFP4x8 | 1.00185x |
| kimi-k3 | CuteDSL MXFP8 | 0.99894x |

All entries below are the raw per-arm medians in microseconds. C0 is reused; A1, A2 and C3 are fresh. C/A uses the mean of the two control medians divided by the mean of the two candidate medians. Forward is C0/A1, reverse C3/A2, and control drift is C3/C0−1.

| Model | Backend | Tokens | C0 µs | A1 µs | A2 µs | C3 µs | C/A | Forward | Reverse | Control drift |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3 | CuteDSL W4A4 | 32 | 102.305 | 102.385 | 102.273 | 102.256 | 0.99953x | 0.99922x | 0.99983x | -0.048% |
| v3 | CuteDSL W4A4 | 128 | 138.305 | 138.049 | 138.304 | 138.545 | 1.00180x | 1.00185x | 1.00174x | +0.173% |
| v3 | CuteDSL W4A4 | 4096 | 211.345 | 210.962 | 211.041 | 211.361 | 1.00167x | 1.00182x | 1.00152x | +0.007% |
| v3 | CuteDSL W4A4 | 16384 | 562.259 | 561.411 | 561.620 | 562.323 | 1.00138x | 1.00151x | 1.00125x | +0.011% |
| v3 | CuteDSL PER-TOKEN | 32 | 106.433 | 106.577 | 106.081 | 106.209 | 0.99992x | 0.99864x | 1.00121x | -0.210% |
| v3 | CuteDSL PER-TOKEN | 128 | 142.881 | 142.625 | 142.576 | 142.817 | 1.00174x | 1.00179x | 1.00169x | -0.045% |
| v3 | CuteDSL PER-TOKEN | 4096 | 252.994 | 252.530 | 253.122 | 252.690 | 1.00006x | 1.00184x | 0.99829x | -0.120% |
| v3 | CuteDSL PER-TOKEN | 16384 | 683.524 | 684.580 | 684.804 | 683.684 | 0.99841x | 0.99846x | 0.99836x | +0.023% |
| v3 | CuteDSL MXFP8 | 32 | 165.297 | 165.377 | 165.409 | 165.105 | 0.99884x | 0.99952x | 0.99817x | -0.116% |
| v3 | CuteDSL MXFP4x8 | 32 | 100.705 | 100.417 | 100.450 | 100.656 | 1.00246x | 1.00287x | 1.00206x | -0.048% |
| v3 | CuteDSL MXFP8 | 128 | 230.017 | 230.257 | 230.001 | 230.306 | 1.00014x | 0.99896x | 1.00132x | +0.126% |
| v3 | CuteDSL MXFP4x8 | 128 | 135.617 | 135.585 | 135.617 | 135.794 | 1.00077x | 1.00024x | 1.00130x | +0.130% |
| v3 | CuteDSL MXFP8 | 4096 | 304.418 | 304.482 | 304.514 | 304.610 | 1.00005x | 0.99979x | 1.00032x | +0.063% |
| v3 | CuteDSL MXFP4x8 | 4096 | 228.386 | 228.530 | 228.498 | 228.706 | 1.00014x | 0.99937x | 1.00091x | +0.140% |
| v3 | CuteDSL MXFP8 | 16384 | 796.069 | 786.197 | 787.941 | 811.078 | 1.02097x | 1.01256x | 1.02936x | +1.885% |
| v3 | CuteDSL MXFP4x8 | 16384 | 714.708 | 712.260 | 716.020 | 719.749 | 1.00432x | 1.00344x | 1.00521x | +0.705% |
| v41-flash | CuteDSL W4A4 | 32 | 127.009 | 126.993 | 126.864 | 127.072 | 1.00088x | 1.00013x | 1.00164x | +0.050% |
| v41-flash | CuteDSL W4A4 | 128 | 263.057 | 263.633 | 263.329 | 263.344 | 0.99894x | 0.99782x | 1.00006x | +0.109% |
| v41-flash | CuteDSL W4A4 | 4096 | 351.969 | 351.666 | 351.633 | 351.889 | 1.00080x | 1.00086x | 1.00073x | -0.023% |
| v41-flash | CuteDSL W4A4 | 16384 | 636.851 | 638.355 | 636.114 | 636.355 | 0.99901x | 0.99764x | 1.00038x | -0.078% |
| v41-flash | CuteDSL PER-TOKEN | 32 | 132.497 | 132.512 | 132.353 | 132.464 | 1.00036x | 0.99989x | 1.00084x | -0.025% |
| v41-flash | CuteDSL PER-TOKEN | 128 | 271.329 | 271.681 | 271.329 | 271.377 | 0.99944x | 0.99870x | 1.00018x | +0.018% |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 407.122 | 406.866 | 406.802 | 406.851 | 1.00037x | 1.00063x | 1.00012x | -0.067% |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 808.052 | 808.259 | 808.659 | 808.291 | 0.99964x | 0.99974x | 0.99955x | +0.030% |
| v41-flash | CuteDSL MXFP8 | 32 | 213.730 | 213.602 | 213.489 | 213.489 | 1.00030x | 1.00060x | 1.00000x | -0.113% |
| v41-flash | CuteDSL MXFP4x8 | 32 | 122.673 | 122.881 | 122.880 | 122.832 | 0.99896x | 0.99831x | 0.99961x | +0.130% |
| v41-flash | CuteDSL MXFP8 | 128 | 462.514 | 462.466 | 462.579 | 462.324 | 0.99978x | 1.00010x | 0.99945x | -0.041% |
| v41-flash | CuteDSL MXFP4x8 | 128 | 255.330 | 255.265 | 255.202 | 255.282 | 1.00028x | 1.00025x | 1.00031x | -0.019% |
| v41-flash | CuteDSL MXFP8 | 4096 | 587.157 | 587.347 | 587.284 | 587.156 | 0.99973x | 0.99967x | 0.99978x | -0.000% |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 360.483 | 360.738 | 360.467 | 360.659 | 0.99991x | 0.99929x | 1.00053x | +0.049% |
| v41-flash | CuteDSL MXFP8 | 16384 | 999.735 | 995.462 | 1002.503 | 965.670 | 0.98370x | 1.00429x | 0.96326x | -3.407% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 875.717 | 857.893 | 876.678 | 870.854 | 1.00692x | 1.02078x | 0.99336x | -0.555% |
| kimi-k3 | CuteDSL W4A4 | 32 | 177.666 | 176.865 | 177.841 | 177.057 | 1.00005x | 1.00453x | 0.99559x | -0.343% |
| kimi-k3 | CuteDSL W4A4 | 128 | 297.346 | 297.538 | 297.202 | 297.426 | 1.00005x | 0.99936x | 1.00075x | +0.027% |
| kimi-k3 | CuteDSL W4A4 | 4096 | 414.835 | 415.203 | 414.163 | 414.947 | 1.00050x | 0.99911x | 1.00189x | +0.027% |
| kimi-k3 | CuteDSL W4A4 | 16384 | 897.510 | 897.783 | 897.319 | 900.694 | 1.00173x | 0.99970x | 1.00376x | +0.355% |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 181.985 | 182.146 | 182.177 | 182.209 | 0.99965x | 0.99912x | 1.00018x | +0.123% |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 306.306 | 307.185 | 306.306 | 306.626 | 0.99909x | 0.99714x | 1.00104x | +0.104% |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 478.579 | 476.580 | 478.980 | 478.148 | 1.00122x | 1.00420x | 0.99826x | -0.090% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1237.833 | 1236.793 | 1239.050 | 1237.305 | 0.99972x | 1.00084x | 0.99859x | -0.043% |
| kimi-k3 | CuteDSL MXFP8 | 32 | 299.426 | 299.106 | 298.979 | 299.442 | 1.00131x | 1.00107x | 1.00155x | +0.005% |
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 171.041 | 170.785 | 170.882 | 171.089 | 1.00136x | 1.00150x | 1.00121x | +0.028% |
| kimi-k3 | CuteDSL MXFP8 | 128 | 520.596 | 519.827 | 519.923 | 520.900 | 1.00168x | 1.00148x | 1.00188x | +0.058% |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 291.282 | 290.913 | 290.882 | 291.618 | 1.00190x | 1.00127x | 1.00253x | +0.115% |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 675.301 | 674.293 | 674.309 | 674.821 | 1.00113x | 1.00149x | 1.00076x | -0.071% |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 436.019 | 435.555 | 435.507 | 435.827 | 1.00090x | 1.00107x | 1.00073x | -0.044% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1333.594 | 1338.665 | 1331.785 | 1314.649 | 0.99168x | 0.99621x | 0.98713x | -1.421% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1262.281 | 1246.793 | 1248.938 | 1241.545 | 1.00324x | 1.01242x | 0.99408x | -1.643% |

Evidence: `results/full-screen-summary.json`, `results/gate-validation.json`, `results/collection.json`, and all nine cell receipts/raw outputs under `results/full-screen-20261027/`. Helper/source launch binding: `launch.json` and `helper-freeze.json`.

- Summary SHA256: `a4d18b2ef4baf195931f6f2c4d9ea2b372bad4594be4f18e631cbe88bda4fe49`
- Combined gate SHA256: `8c7455b2fb2d51a7d18dca62f1b1c6f083b572c06c1526404244bd8ccfc97119`
