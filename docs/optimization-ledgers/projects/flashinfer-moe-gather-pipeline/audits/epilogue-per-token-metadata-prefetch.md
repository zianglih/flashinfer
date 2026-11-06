# FC2 per-token metadata before accumulator readiness

Bounded read-only audit at retained `c1ac8ce` / swap `482b636a`. Alpha candidate `2a696811` remains frozen and is now rejected after its 56-cell screen; no metadata prototype or GPU work was done.

**Real repeated work, but no minimal scalar-like proposal.** `_scatter_metadata` (`moe_swap_ab_kernel.py:1078–1126`) loads/rerounds one scale per 32-token group. `_run_bulk:1157–1167` and the nonbulk scatter branch of `run:1368–1378` call it after the outer accumulator wait (`:3338`), once for each channel-tile call (`:3372–3406`). Its row/scale result depends on route start/live rows, alpha and immutable scale/mapping buffers, not channel index or accumulators.

The exact c1ac-equivalent per-token case14 FC2 control captured in `experiments/alpha-prefetch/qualification-extra/fetched/evidence/per-token-14-Relu2-control/codegen/01-Sm100BlockScaledGroupedGemmKernel.{ptx,sass}` has M512/twoCTA, N128, two channel tiles, bulk64, 128 registers, LOCAL0 and occupancy1. PTX loads four routed Float32 scales from parameter14 plus `4*(route_start+lane+32*g)`, multiplies by alpha, then repeats the same four addresses for channel tile2. The native scale loads are:

| Group | First channel PC | Second channel PC |
|---|---|---|
|0|0x3d40|0x7b90|
|1|0x3c90|0x7b70|
|2|0x3d50|0x7b80|
|3|0x3d60|0x7ba0|

Both sets follow accumulator TRY at0x3990. SASS hash `8ddbfa6caa5358534b401d11f542ccd643db87740138c99baf8728d7fb1c963a`; PTX `ed71c87f738941e8127dfb996e56d7864650ed2feb76bb3be9e52794fd7b9c2f`. The same-route address algebra and duplicate native sites establish executed duplication when both channels and groups are live. They do **not** establish a sampled scale-load latency bottleneck or predict a net gain from longer liveness.

**Smallest conceptual interface:** compute the existing `(output_rows, output_scales)` once in the outer live-tile epilogue, before accumulator wait; pass those tensors into `run`, then pass scales into `_run_bulk`, removing the two internal `_scatter_metadata` calls. Existing scatter/per-token/fused-finalize compile-time conditions would select their use, with no new behavior flag or state machine. This still changes array-valued helper interfaces and extends up to8 scales/lane (plus up to8 rows for fused finalize) across the wait and all channel tiles. It also moves harmless loads onto inactive final channel CTAs unless their existing guard is carried outward. It is materially larger than alpha's one scalar/+1netline.

Startup PDL already waits for these epilogue readers (`:2755–2766`), including FC2 scales produced by the preceding quantizer. No wait may be deleted. Source safety of reading immutable metadata earlier does not prove favorable register allocation or issue order.

**FC1 is different:** its original-token or routed scale is multiplied into alpha before gated activation/Relu2 (`:864–883,958–968`); FC2 includes optional router weight and final-scale dtype rounding. Reusing `_scatter_metadata` for FC1 would change that contract without restructuring it. FC1 also has the overlapping-accumulator entry and dynamic 32-token traversal. Do not combine that larger interface change with this FC2-only question.

**History:** old `scripts/epilogue_experiment/README.md` preloads metadata before the inner slab loop, not before the outer accumulator wait; its phase diagnostics therefore do not measure this motion. `scripts/epilogue_hoist_20261027/PLAN.md` moves norm/alpha only. The bounded search found no matching tested pre-wait output-row/output-scale-array hoist. This is not classified as a historically measured rejection.

**Recommendation:** do not prototype now. Retain the concrete duplicate-load observation, but no current PC evidence establishes these scale dependencies as the limiting path. The just-completed alpha screen regresses overall and concentrates losses in TP per-token FC2 extension despite successful representative native motion/resource qualification; the full timing matrix also contains four FC2 register increases with unchanged occupancy/LOCAL0. That is evidence against assuming a broader pre-wait array lifetime helps, not a causal explanation of alpha's loss. A larger helper refactor/FC1 unification or a shape-specific rescue is not justified by static load count alone.
