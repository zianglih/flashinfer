# Native graph versus eager AUTO diagnostic

Same production source `1e69d0a39`, N3U EP8 T4096, balanced native routing, no new tactics. Explicit public graph-AUTO flag changes cache identity; native cold-L2 CUDA-event defaults remain intact (3 warmups, 10 samples; graph 100 us versus eager 5,000 us delay). These are **selected-winner comparisons**, not proof of an execution-policy effect or a kernel-source speedup. Fresh eager searches also selected the faster geometry (details below). Eager selections are reused from the verified retained native search; graph selections are fresh across all 20 generated buckets and 320 admitted tactics per bucket. All reported public times are fresh C–A–A–C 10/100 cold-L2 CUPTI graph timing with input quantization included.

| Backend | Eager-selected (us) | Graph-selected (us) | Speedup | Control drift | Graph drift | Same winner |
|---|---:|---:|---:|---:|---:|---|
| CuteDSL W4A4 | 233.857 | 219.369 | +6.60% | -0.18% | +0.01% | False |
| CuteDSL PER-TOKEN | 322.122 | 320.210 | +0.60% | -0.04% | +0.05% | False |

**Interpretation:** graph AUTO chose N128/two-CTA/static for both arms. A separate fresh eager search chose exactly the same per-token tactic, and another fresh eager W4A4 search chose the same geometry with FC1 K8 rather than K4. The large W4A4 difference versus the retained N256 eager winner therefore does not establish graph profiling as its cause. No benchmark or public default change is justified by these two comparisons alone.

Each cell retains 400 frozen public samples plus 100 diagnostic AUTO-pass samples. Exact cache keys/tactics and routing hashes were verified in every phase. Native graph profile failures/finite counts and all per-tactic event medians are retained in `analysis.json` and raw policy receipts. SGLang currently omits the public graph-AUTO flag, so this selection-policy result does not automatically apply to its serving wrapper.

## CuteDSL W4A4
Native graph profiles: 6400/6400 finite, 0 failed/nonfinite.
Eager winner: `[256, [[128, 256], [1, 1], false], [[256, 256], [2, 1], false], [4, 4], false]`
Graph winner: `[128, [[256, 128], [2, 1], false], [[256, 128], [2, 1], false], [4, 4], false]`

## CuteDSL PER-TOKEN
Native graph profiles: 6400/6400 finite, 0 failed/nonfinite.
Eager winner: `[128, [[128, 128], [1, 1], false], [[256, 128], [2, 1], false], [4, 4], false]`
Graph winner: `[128, [[256, 128], [2, 1], false], [[256, 128], [2, 1], false], [4, 4], false]`

## Legacy compatibility
Both non-swap W4A4 and per-token public graph-AUTO smoke tests passed 20 native buckets with 16 admitted tactics each: 320/320 finite profiles per backend, zero failures, and successful 100-sample CUPTI public calls. This establishes bounded compatibility, not broad performance retention. No W4A16 graph tuning was enabled.
