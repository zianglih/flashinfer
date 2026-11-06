# N32 source audit: bounded authored epilogue extension required

No source edits, patch, CuTe constructor call or GPU work were performed for this audit. Active production source is parent's C1-overlay on6315; the N32 paths remain rejected. `static-geometry.json` checks only source-derived arithmetic and permutations.

## Established path and expected scope

Split W4A16's existing catalog includes routed N32 with M128 physicalC1/C2 and M256/C2 (`flashinfer/fused_moe/cute_dsl/tuner.py:971–1007`). It uses the same online packed-weight transform and derived epilogue tile (`blackwell/moe_w4a16_kernel.py:185–234`), unlike the Mega wrapper's fixed64-token epilogue. The mixed helper, K256 descriptor, two transform groups and two activation/accumulator stages are therefore good reuse points; this is not a reason to copy the split kernel's entire epilogue/finalization path into Mega.

At a fixed M, N32 halves the statically staged activation payload relative to N64. Formula-derived two-stage BF16-B storage is32768B for M128,16384B for M256. Raw packed-A/SF staging is unchanged. Runtime MMA already rounds valid tokens to16, so a valid≤32 expert tile does not automatically halve tensor-core arithmetic when moving from N64 to N32. Potential gains are reduced activation movement/SMEM, a single32-token epilogue half, smaller per-route metadata, and finer work-tile granularity. Experts with>32 routes require more work tiles and repeated weight decoding; smaller N may lose throughput. These are hypotheses, not measured gains.

Two N32 accumulator stages use64 TMEM columns. The existing capacity formula still chooses three decoded K256 stages (384 columns), leaving64 unused columns; N32 does not provide a fourth decoded stage. Expected logical ranges are acc[0..31],[32..63], decoded[64..191],[192..319],[320..447]. The allocator remains512 columns. No stage or register knob is needed.

## Concrete current blockers

All references below are under `flashinfer/moe_ep/kernel_src/cutedsl_megamoe` unless otherwise stated.

- Public/kernel geometry guards exclude N32: `shim/w4a16/frontend.py:73`, `kernel.py:89,145`, `epilogue.py:60`; dynamic helper whitelist also excludes it (`dynamic_mainloop.py:87`). Merely widening these guards is unsafe.
- Vendored base requires `cta_tile_n %64 ==0` and computes `subtile_cnt=N//64` (`src/moe_nvfp4_swapab/epilogue_refactor.py:1058,1080`). Bypassing that guard alone produces zero subtiles at N32.
- W4A16 FC1 performs two32-token TMEM halves unconditionally (`shim/w4a16/epilogue.py:340`). With N32 storage, half1 enters the next accumulator stage, or the decoded-A region at the final accumulator stage. The later output predicate does not protect those earlier loads/transposes.
- FC2 STG output-contract factory requires N%64 (`epilogue_refactor.py:2499`), its raw load reads four16-register quadrants over64 columns (`:593–677,2755`), and its reorder requires64 BF16 registers and performs a second transpose at column+32 (`:2780–2850`). The inherited FC2 helper therefore needs an N32-specific process pipeline, not only a smaller base tile.

## Smallest coherent specialization

Keep vendor originals immutable. Author a BF16-only32-token specialization in the W4A16 shim and retain existing FC2 return/routing/completion helpers.

1. Select `_EpilogueTokenTileSize=32` only for N32 before the base constructor runs; existing N64/N128 retain64. This lets base `cta_tile_n`, subtile count, stage pitch and loop division agree with actual32-token storage. The constructor's fake quantized-FC1 resources remain unused as today; actual constructor/layout checks must verify them.
2. W4A16 FC1 iterates `token_tile_size//32` halves and uses that token-tile stride. For N32, retain precisely the first existing `TmemTranspose16x32` sequence, including warp-local gate/up row composition, alpha/clamp placement, TMEM fences and valid-token/H-tail output predicates. No access to+32 columns occurs.
3. Add a W4A16 FC2 helper that reuses inherited `_make_output_router`, `__call__`, `run_subtile`, and `signal_fc2_done`, but supplies a BF1632-token process pipeline in its constructor. Its raw load uses the existing first top/bottom16×32 TMEM views, omitting only the second token-half. Reuse `fc2_f2fp` unchanged for the two16-register inputs.
4. Restrict the existing BF16 gather/scatter maps to one half: gather `((2,16),(16,1))`, scatter `((16,2),(2,1))`. Pack32 BF16 values into16 opaque32-bit values, call the existing `TmemTranspose16x32(Region.Top)` once, then scatter back. Preserve the generic STG store function and router. An authored BF16 output mapping uses the existing affine formula with N32: two256-bit stores per epilogue thread cover exactly32×128 output elements. No quantized, bulk-store or in-kernel reduction path is introduced.
5. Admit only selected established N32 geometry/cluster pairs; keep two decode groups,640threads, current register roles, K256 and preferred5 raw fitter. Runtime-N helper still emits K16 atoms with N16/N32 descriptor; the existing nonleader-B shift becomes−8 or0 and must remain in both FC1/FC2 for M256. Accumulator release and FC2 completion counts remain per feature CTA; routing scores stay after FC2.

`static_geometry.py` verifies the proposed BF16 output mapping covers every32×128 element once, gather/scatter index inverses, three decoded-stage ranges and96 valid-token/shift cases. It does not verify the hardware transpose register mapping, CuTe layouts/TMA descriptors, barrier execution or numerical precision. Those require real CPU construction and numerical/codegen gates before any catalog expansion.

A padded64-column accumulator workaround could avoid some out-of-range accesses but would retain unused epilogue work and introduce a logical/physical pitch distinction. It is not the clean extension proposed here.

## Priority and gates

N32 is more promising for the requested small routed-token workloads than M128/N128, but requires more implementation work. M128/N128/C2 is already accepted; its doubled activation allocation forces shallow raw staging at H7168 and can fail the minimum-ring fit at larger H. Parent deferred its catalog admission. Generic Mega `group_hint` values are a separate scheduling experiment: `shim/tuner.py:52–56` lists None/64/128/256/512, while the curated NVFP4/MXFP8/W4A16 sweeps use512 and flag4/8. Group_hint controls a greedy cumulative FC1 work-tile threshold (`src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:1104–1139`), not warp count or routed-N. No current W4A16 evidence justifies multiplying the catalog across that whole grid.

The existing tuner scores synchronized wall-clock launches per rank and reduces the maximum median (`shim/autotune.py:185–224`). A poor chosen candidate under host skew is a measurement issue, not evidence of a missing geometry; root's timing investigation remains separate.

Before an N32 timing claim: actual CUDA-hidden ctor/layout/fitter tests for M128/C1,C2 and M256/C2; exact FC2 store-contract mapping; EP1/EP2 public scale/routing/graph/clamp/tail/ring tests with route counts1,15,16,17,31,32,33,63,64,65,257; both return modes/flags4,8; codegen verification of32-column accumulator pitches,64-column decoded start, no second-half TMEM access and no new transform locals; finally same-source adjacent N64/N32/N64 controls at representative points before broader1–4096 measurements. Keep the catalog/default unchanged until those gates complete.
