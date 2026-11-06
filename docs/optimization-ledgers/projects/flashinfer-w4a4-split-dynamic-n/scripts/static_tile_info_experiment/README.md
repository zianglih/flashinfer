# Static tile metadata queue experiment

Two independent unstaged source copies derived from frozen CLC R2, both based on retained fca8462. No production edits or publication.

- `flashinfer-static-tile-info-review`: FC1 static metadata queue depth1; FC2 disabled. Patch `72fc49fd2d04d7c42cd09d4f44ac2d56d97caba87cfcc33f37b430d9a04f54eb`.
- `flashinfer-static-tile-info-depth3-review`: only FC1 caller metadata depth changes to3. Patch `0a2df53f5be539ebc445d5cd61f209202e0873db41795b82f2139522474620a8`.
- Direct compile-time knobs: `use_tile_info_scheduler`, `num_tile_info_stages`. Static scheduler warp walks `block + n * grid`; fixed bounded persistent grid honors the explicit SM budget. No CLC grid, fetch response, or CLC barriers remain.
- Queue stores tile/expert/valid; existing consumer queue protocol is retained. An extra scheduler warp is appended without changing compute-role IDs. All three compute-role loop bodies, arithmetic/layout policy, PDL calls and next-work helper match frozen R2 after the direct knob rename (`static-ast-proof.json`).
- Gate:39 exact cases across NVFP4, MXFP8 and mixed; persistent padded work, zero live tiles, one/two CTA, and2-SM budget.360 actual operand/SharedStorage cases at depths1/3. All passed onGPU0 with unchanged source.
- Fixed screen:GPU0 V3EP8 /GPU1 V41EP4; T16,512,16384; all three affected formats, frozen baseline C1 token-wise tactics. Per format order C1,D1A1,D3A1,D3A2,D1A2,C2. Native benchmark10warmup/100replays,coldL2,CUPTI,no fused finalize. Explicit route and tactic assertions after each invocation; no retention claim until results.
- Static FC2 still has the R2 loop refactor. Comparing D1 with D3 isolates queue depth; comparisons with fca include this already-audited codegen difference.

The initial fixed screen launch rejected the NV backend selector before timing; the corrected `cutedsl` plan runs under remote tag `static-tile-info-r1-fixed-r2-{model}` and keeps the failed receipts intact. `cutedsl` also emits the unaffected W4A16 control arm.

All receipts, raw output, input caches and launch helpers are under `evidence/static-tile-info-r1`. The initial full-history clone failed on a missing historical object already present in the source clone; independent `--local --no-hardlinks` cloning succeeded, with no alternates or source mutation and exact HEAD/source hashes verified.

## Fixed screen outcome

36 native invocations completed; source/route/tactic/cache/observer assertions passed, plus all target runners logged3 config-file cache hits and no misses per invocation. Sources remain unchanged and unstaged. Raw archives and full-precision derived tables are retained under `fixed-v3/` and `fixed-v41/`.

No global retention recommendation: NVFP4 decode loses roughly0.2–0.7%, MXFP8 decode is near-flat/slower, mixed decode gains0.5–1.1%. V41 MXFP8 T16384 loses5.50%/3.52% in speedup terms at depths1/3 (both repetitions slower); depth3 nevertheless beats depth1 consistently by2.10%, a useful buffering-depth signal. Large-prefill variation also affects the unchanged W4A16 control; isolated prefill improvements are not a stable retention claim. This is a3-token fixed diagnostic screen, not the13-token AUTO methodology used for retention. No source retained or PR updated.
