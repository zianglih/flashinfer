# FC1 index issue work after mixed V6

Read-only source assessment; no production change. Two independent patches are prepared against V6:

- `cache48-prefix.patch`: cache the first48 source rows for **every FC1 tactic**, retaining control80/epilogue176.
- `full-hoist-uniform128.patch`: cache up to96 rows, with FC1 control128/epilogue128. See `FULL_HOIST_PROPOSAL.md` for its legal warpgroup allocation and epilogue tradeoff.

Both patches apply cleanly and their source copies pass syntax and Ruff checks. They must be screened separately, not stacked.

## Why direct issuer loads are not the first bounded change

The current map load distributes four indices to each active lane with one128-bit vector-load instruction. Lanes perform division by constexpr top-k and tail selection in parallel. Mixed V6 then caches a32-row prefix with shuffles before the K loop. Every larger partition retains four indices per lane for its remaining groups.

[FlashMLA's elected issuer](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L395-L453) loads its own `int4` groups and retains them. Its four producer warps divide the rows; the matching configuration gives each issuer16 rows. Split W4A16 gives one existing producer warp up to96 rows for the measured two-CTA tactics and reuses those same indices across a long GEMM K reduction.

Direct-loading the existing32-row cached prefix would save32 setup shuffles per routed tile, with no reduction to the preferred mixed N128 K-loop shuffles because that path already has none. The alternative needs eight issuer128-bit vector-load instructions (or four256-bit loads) and serializes the32 index conversions and tail predicates in the issuer. The same distinct memory sectors may be cache-resident, but instruction and dependency costs still increase. No direct-load timing conclusion follows from FlashMLA alone.

Reloading each uncached group in the K loop replaces four shuffles with a vector global load, four index conversions, validity handling, and address work at every K tile. That loses the current once-per-route map reuse. Direct issuer loading becomes more attractive when the **complete** index set can remain resident, which is the separate full-hoist experiment; it is not a free substitute for the distributed registers at the present budget.

## Cache48 instruction hypothesis

The table counts source-row shuffles per K256 iteration from source topology, not measured SASS. Preferred and fallback entries refer to the mixed kernel, which already caches32; uniform cluster2 currently caches none for these widths.

| FC1 partition | Owned rows | V6 shuffles/K | Cache48 shuffles/K |
| --- | ---: | ---: | ---: |
| Mixed N128 preferred4 |32|0|0|
| Mixed N128 fallback2 |64|32|16|
| Mixed N192 preferred4 |48|16|0|
| Mixed N192 fallback2 |96|64|48|
| Uniform N128 cluster2 |64|64|16|
| Uniform N192 cluster2 |96|96|48|

For K7168,28 iterations multiply these reductions:448 fewer shuffles per routed tile for the affected mixed cases and1,344 fewer for the uniform cases. Up to48 one-time setup shuffles are added/retained instead. Actual compiler scheduling, uniform-register movement and spills remain decisive.

This adds16 cached indices relative to mixed V6's32-row prefix while retaining the80-register control target. Uniform tactics newly cache48 indices. If this spills, the proposal fails its intended instruction/memory benefit; do not infer feasibility merely from the source register tensor size. `R2UR` and `UMOV` may remain even after row shuffles move out of K.

## Decision screen

Capture uniform cluster2 N128/N192 first because AUTO may continue selecting those tactics; capture mixed N128/N192 as well to inspect runtime-mask overhead and preferred/fallback paths. Compare local-memory traffic and activation-loop `SHFL`, `R2UR`, `UMOV`, total instructions, then run the existing exact smoke and four-point timing screen for candidates with useful generated code. No new warp, synchronization protocol, map format, or arithmetic contract is proposed.
