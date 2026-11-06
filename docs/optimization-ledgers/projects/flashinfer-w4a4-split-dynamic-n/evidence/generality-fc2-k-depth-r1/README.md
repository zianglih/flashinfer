# FC2 K-depth diagnostic

Only the experiment observer overrides the core constructor's explicit `k_steps` for `scatter_output=True`; FC1 remains automatic. Source stays at the frozen planner patch `a9ef37a8`, with no narrow admission, new quantizer, or tactic expansion. The benchmark, public wrapper, inputs, timer, routing and selected tactics are unchanged.

Each model runs both MX formats on GPU7 in K8–K4–K4–K8 order at 4,096 tokens. This uses the native 10-warmup / 100-iteration cold-L2 CUDA-graph CUPTI method. Initial quantization is outside timing; fused finalization is disabled. Routes, source pins, cache choices and FC1 constructor settings are checked for every arm. Actual constructor and storage plans are recorded in each results file.

Speedups below are geometric means of the two direct K8/K4 repeat ratios (larger means K4 faster):

| Model | MXFP8 | MXFP4x8 |
|---|---:|---:|
| V3 EP8 | 1.023358x | 1.053588x |
| V4.1-Flash EP4 | 0.995137x | 1.036132x |
| Kimi K3 EP8 | 1.002136x | 1.038541x |

Both repeats agree in direction for all six points. These are fixed-tactic, whole-chain diagnostics, not an AUTO retention decision. The scalar K4/K8 controls alter the FC2 MMA tile and its derived operand ring together.

- V3 FC2 M256/N256: K256 x 2 slots -> K128 x 5, queued reduction 512 -> 640.
- V4.1 and K3 FC2 M256/N128: K256 x 3 -> K128 x 7, queued reduction 768 -> 896.
- FC1 resource plans and MMA geometry stay identical between arms.

`summary.json` contains full-precision raw medians and both direct repeat ratios. `raw/<model>/receipt.json` binds sources, commands, GPU UUID, clock/power/temperature snapshots, cache SHA and observed-result SHA; `fetch-receipt.json` pins the collected files. These runs contain no new output-correctness assertion.
