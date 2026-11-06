# Independent FC2 scheduler native AUTO screen

A uses frozen final native selections from the retained implementation. B performs a fresh unrestricted native search, then replays its selected tactics. Both are measured in A–B–B–A order on the same GPU, 10 warmups / 100 cold-L2 CUPTI samples. NVFP4 includes input quantization. Per-token is omitted; W4A16 is an incidental unchanged control. No TRT rerun.

| Model | Backend | Tokens | A us | B us | A/B | Pair 1 | Pair 2 | B FC2 CLC |
|---|---|---:|---:|---:|---:|---:|---:|---|
| kimi-k3 | CuteDSL MXFP8 | 64 | 416.354 | 412.970 | 1.00819x | 1.00724x | 1.00915x | [True] |
| kimi-k3 | CuteDSL MXFP4x8 | 64 | 232.513 | 232.033 | 1.00207x | 1.00034x | 1.00380x | [True] |
| kimi-k3 | CuteDSL MXFP8 | 128 | 525.475 | 520.803 | 1.00897x | 1.00887x | 1.00907x | [True] |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 292.394 | 291.842 | 1.00189x | 1.00033x | 1.00346x | [True] |
| kimi-k3 | CuteDSL MXFP8 | 512 | 595.388 | 589.355 | 1.01024x | 1.01243x | 1.00804x | [True] |
| kimi-k3 | CuteDSL MXFP4x8 | 512 | 337.793 | 337.114 | 1.00201x | 1.00341x | 1.00062x | [False] |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 651.491 | 650.500 | 1.00152x | 1.00017x | 1.00288x | [False] |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 397.778 | 398.411 | 0.99841x | 0.99739x | 0.99944x | [False] |
| kimi-k3 | CuteDSL W4A4 | 64 | 241.201 | 239.521 | 1.00701x | 1.00809x | 1.00594x | [True] |
| kimi-k3 | CuteDSL W4A16 | 64 | 253.105 | 252.601 | 1.00200x | 1.00336x | 1.00063x | [] |
| kimi-k3 | CuteDSL W4A4 | 128 | 299.834 | 297.169 | 1.00897x | 1.00888x | 1.00905x | [True] |
| kimi-k3 | CuteDSL W4A16 | 128 | 317.074 | 316.618 | 1.00144x | 1.00217x | 1.00071x | [] |
| kimi-k3 | CuteDSL W4A4 | 512 | 343.370 | 338.770 | 1.01358x | 1.01552x | 1.01164x | [True] |
| kimi-k3 | CuteDSL W4A16 | 512 | 373.634 | 372.842 | 1.00212x | 1.00240x | 1.00184x | [] |
| kimi-k3 | CuteDSL W4A4 | 4096 | 386.530 | 386.938 | 0.99894x | 0.99905x | 0.99884x | [False] |
| kimi-k3 | CuteDSL W4A16 | 4096 | 616.707 | 631.227 | 0.97700x | 0.96256x | 0.99185x | [] |
| v3 | CuteDSL MXFP8 | 32 | 166.249 | 168.081 | 0.98910x | 0.98867x | 0.98953x | [True] |
| v3 | CuteDSL MXFP4x8 | 32 | 100.025 | 99.960 | 1.00065x | 1.00049x | 1.00080x | [True] |
| v3 | CuteDSL MXFP8 | 128 | 228.058 | 229.817 | 0.99234x | 0.99172x | 0.99296x | [True] |
| v3 | CuteDSL MXFP4x8 | 128 | 135.545 | 134.993 | 1.00409x | 1.00558x | 1.00260x | [True] |
| v3 | CuteDSL MXFP8 | 4096 | 305.042 | 305.362 | 0.99895x | 1.00037x | 0.99754x | [False] |
| v3 | CuteDSL MXFP4x8 | 4096 | 226.482 | 226.034 | 1.00198x | 1.00440x | 0.99957x | [False] |
| v3 | CuteDSL W4A4 | 32 | 102.056 | 101.233 | 1.00813x | 1.00885x | 1.00742x | [True] |
| v3 | CuteDSL W4A16 | 32 | 110.937 | 110.249 | 1.00624x | 1.00478x | 1.00770x | [] |
| v3 | CuteDSL W4A4 | 128 | 137.881 | 137.297 | 1.00425x | 1.00548x | 1.00302x | [True] |
| v3 | CuteDSL W4A16 | 128 | 148.161 | 148.857 | 0.99533x | 0.99613x | 0.99452x | [] |
| v3 | CuteDSL W4A4 | 4096 | 208.041 | 207.978 | 1.00031x | 1.00177x | 0.99885x | [False] |
| v3 | CuteDSL W4A16 | 4096 | 316.802 | 317.762 | 0.99698x | 0.99940x | 0.99455x | [] |
| v41-flash | CuteDSL MXFP8 | 64 | 356.459 | 352.635 | 1.01084x | 1.01139x | 1.01030x | [True] |
| v41-flash | CuteDSL MXFP4x8 | 64 | 198.578 | 196.370 | 1.01125x | 1.01406x | 1.00845x | [True] |
| v41-flash | CuteDSL MXFP8 | 128 | 468.179 | 463.709 | 1.00964x | 1.00816x | 1.01112x | [True] |
| v41-flash | CuteDSL MXFP4x8 | 128 | 259.378 | 255.426 | 1.01547x | 1.01750x | 1.01345x | [True] |
| v41-flash | CuteDSL MXFP8 | 4096 | 587.228 | 586.909 | 1.00054x | 1.00106x | 1.00003x | [True] |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 354.842 | 355.571 | 0.99795x | 0.99613x | 0.99977x | [False] |
| v41-flash | CuteDSL W4A4 | 64 | 206.074 | 204.274 | 1.00881x | 1.00823x | 1.00940x | [True] |
| v41-flash | CuteDSL W4A16 | 64 | 217.138 | 217.578 | 0.99798x | 0.99640x | 0.99956x | [] |
| v41-flash | CuteDSL W4A4 | 128 | 265.658 | 263.122 | 1.00964x | 1.00899x | 1.01029x | [True] |
| v41-flash | CuteDSL W4A16 | 128 | 280.234 | 280.435 | 0.99929x | 1.00040x | 0.99817x | [] |
| v41-flash | CuteDSL W4A4 | 4096 | 348.011 | 349.644 | 0.99533x | 0.99533x | 0.99533x | [False] |
| v41-flash | CuteDSL W4A16 | 4096 | 569.908 | 543.941 | 1.04774x | 1.07393x | 1.02145x | [] |
