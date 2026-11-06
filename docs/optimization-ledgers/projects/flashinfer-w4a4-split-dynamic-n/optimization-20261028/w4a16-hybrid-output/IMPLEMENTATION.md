# W4A16 hybrid output experiment

Status: source 01 passed the focused existing W4 tests and paired fused-finalize compatibility gate. Changes are unstaged in the separate `flashinfer-w4a16-hybrid-output-review` clone. This experiment starts from padded R2 and does not include the descriptor-bank implementation or source04 wait relocation.

## Scope

Only gated FC1 output changes: SwiGLU, SiTU, and GeGLU keep the existing activation arithmetic, TMEM loads, and row-folding layout. Complete token subtiles retain the existing TMA path; incomplete token subtiles write live rows directly to global memory. Existing ReLU² FC1 and unfused FC2 already use the same full-subtile/TMA versus partial-subtile/SIMT rule and are unchanged. Fused FC2 is unchanged.

## Coordinates

All references below are to `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` in source 01.

- Wrapper lines 855–858 define output `(m/output_m_factor, n, 1)` with M contiguous. Gated `output_m_factor=2`; `_setup_attributes` lines 398–407 likewise halves each CTA's output-M extent.
- Scheduler lines 1543–1551 and 1577–1585 construct the absolute CTA channel-tile coordinate, including each CTA's rank within a two-CTA MMA group. CLC publishes its already absolute `tile_coord_mnl[0]` at line 1511. Existing gated TMA selects that exact coordinate at line 2152.
- Gated identity partition lines 2059–2064 follows the existing TMEM ownership. Selecting the identity subtile at lines 2235–2237 retains its absolute N offset within the CTA tile.
- The same existing fold `local_m // 32 * 16 + local_m % 16` maps paired up/gate rows to output channels. Direct global output adds `work_tile.cta_coord_m * self.cta_tile_shape_mnk_c[0]` to that folded channel and adds `work_tile.coord_n` to the identity N coordinate. It does not divide the CTA coordinate again for two-CTA MMA.
- Tail predicates require identity N less than `distance_to_boundary`. The existing compile-time `m_cluster_aligned` policy controls the additional output-channel bound check, matching the nongated tail code.

## Synchronization and ring state

`full_subtile` uses the same runtime condition as the nongated path: `distance_to_boundary >= (subtile_index + 1) * epi_tile_n`. It is uniform across the CTA's epilogue warpgroup. Only full subtiles increment `num_prev_subtiles`, write a shared-memory stage, execute its async-proxy fence and two warpgroup barriers, and issue/commit/acquire a TMA store. Partial subtiles bypass all of those operations. The prior full store's acquire and trailing barrier already establish safe reuse before a later full store; an intervening tail does not touch shared output storage or advance the ring. Final `producer_tail()` remains unchanged, including the no-TMA case. Accumulator load fence/release remains unchanged and occurs after the last active TMEM subtile.

No new public arguments, model-shape policy, descriptor bank, or autotune tactics are introduced. The SIMT tail retains native TMEM register ownership and predicated element stores; no lane shuffle or forced vector reinterpretation is introduced.

## Validation boundary

AST parsing, `git diff --check`, and all applicable scoped pre-commit hooks passed. The frozen candidate then passed all 10 selected existing W4 tests (zero failures/errors/skips, 12.80s) and four paired fused-finalize cases against padded R2 (old/swap layouts × PDL off/on). FC1 matched exactly; final output also had observed max absolute difference0 in all four cases. Exact commands, environment, raw output and source-hash receipts are in `existing-gate-01/RESULT.md` and its adjacent logs. No source edits were made during validation.

The separate graph gate covers all gated activation families, one/two CTA, static/CLC scheduling, PDL, and below/at/above the actual epilogue subtile width, with poisoned candidate padding. Its detailed status is maintained in `VALIDATION.md`; performance remains a separate paired CUPTI result. The existing-test/fused-smoke selection itself uses full gated channel tiles and does not claim a partial output-channel predicate check. No sanitizer or reference-self-test was run.
