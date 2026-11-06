# W4 tail-dequant affected scope

The internal predicate exists only when a final K stage leaves an entire transform warpgroup unused. All frozen W4 tactics use K256 and two transform warpgroups, so only remainders 1–128 enable it. The model dimensions are read from the committed benchmark AST, and the stage sizes come from every recorded winner, including the unchanged deterministic defaults.

| Model | Topology | FC1 K | FC2 K | Disposition |
|---|---|---:|---:|---|
| kimi-k3 | EP8 TP1 | 3584 | 3072 | Unchanged: reuse 13 cells |
| nemo3-ultra | EP8 TP1 | 2048 | 5120 | Unchanged: reuse 13 cells |
| v3 | EP8 TP1 | 7168 | 2048 | Unchanged: reuse 13 cells |
| v41-flash | EP4 TP1 | 5120 | 2304 | Unchanged: reuse 13 cells |
| kimi-k3 | EP1 TP8 | 3584 | 384 | FC2 only: measure 13 tokens |
| nemo3-ultra | EP1 TP8 | 2048 | 640 | FC2 only: measure 13 tokens |
| v3 | EP1 TP8 | 7168 | 256 | Unchanged: reuse 13 cells |
| v41-flash | EP1 TP4 | 5120 | 576 | FC2 only: measure 13 tokens |

The 468-cell full matrix has **39 affected W4 cells and 429 reusable cells**: 65 aligned W4 cells and all 364 swap cells. FC1 and the finalizer are unchanged for every cell. The completed 12-cell CAAC screen is reused; this extension runs only 27 remaining cells at tokens **1, 2, 8, 16, 32, 64, 256, 512, 8192**. Tokens 1 and 2 remain in raw output but are excluded from retention aggregates.

Qualification already establishes raw PTX/cubin/SASS equality for aligned split kernels in both layout modes and one/two CTA, for an all-live partial final stage, and for the shared MegaMoE helper's padded multistage contract. The unchanged active transform and constexpr folding support reuse; this is representative native identity evidence, not a claim of separately recompiling every reusable table cell. Source manifests and the 104-cell inventory bind the exact scope.

Timing remains four-phase C-A-A-C with 100 untrimmed native CUPTI cold-L2 CUDA-graph samples and 10 warmups per phase. The original choices/routes/cache entries are replayed without retuning. The two remaining recorded default choices are V41F TP4 and N3U TP8 at 8192; native resolution and resource joins remain mandatory. The old screen and its source/config/evidence are immutable.
