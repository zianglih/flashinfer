# Independent source and locality review

Frozen interleave source: `3b0114ea7b8099d759d9c62808d8752d2fa94fdda720f77024f4a6c4b8be64ac`, based on b52. No source or GPU changes were made by this review.

The actual helper/caller transformation has no semantic blocker. Each accumulator still receives the same ordered K widths, A/SFA channel, shared B/SFB, dynamic N and first-K accumulation predicate. `start` advances once after all channels. K96 stage descriptors retain separate A bases, the common B base and the same LBO/SW128 expressions; residual widths retain the old atom-K decomposition. Every descriptor is rebuilt from the base before adding that channel's scale selector, avoiding stale selector bits. Channel accumulators occupy disjoint allocated-N regions. Accumulator overlap protects the entire intersecting physical region before any new channel writes.

All 107 synchronization/PDL/metadata lifecycle calls have identical arguments and lexical order. Both SFA copies precede the gather wait, SFB publication precedes MMA, operand release follows every K/channel issue, and accumulator publication remains after the complete reduction. Only the two optional per-channel iKET ranges become one combined issue range. The 514-file source proof and all 130 reused baseline artifact hashes pass; the 26-capture plan covers one/two channels and CTAs, K32/K96 plus residual stages, CLC/static, four formats and native ReLU²/SiTU. Exact and timing remain separate qualification.

## Dynamic locality boundary

`peer_liveness_audit.py` checks actual loop backedges and local instruction predicates in the failing M512/N128, K512/stageK256 signature. Its two K stages are fully unrolled inside each work-tile iteration.

| Per MMA warp, per work tile, fast waits | Local loads | Local stores | Bytes per lane: loads + stores |
|---|---:|---:|---:|
| b52 control | 16 | 6 | 124 + 44 |
| Shared R2 | 16 | 0 | 64 + 0 |
| MMA interleave | 10 | 0 | 40 + 0 |

Control also has ten 64-bit descriptor stores once before its work loop. Shared R2 and interleave instead have fourteen/eight 32-bit descriptor stores there, plus three common startup stores. The local operations execute under role-wide branches, without elected-lane predicates.

The common-state reloads are **not only cold setup**. Per work tile, each CTA adds one weight-producer reload, two relay reloads, two per epilogue warp and two per gather warp. Across a two-CTA cluster, these are 38 additional warp load instructions; combined fastpath counts become control16 loads/6 stores, shared54/0 and interleave48/0. Both candidates also contain 15 retry-loop blocks that reload the shared barrier base on each iteration. Startup/tail behavior adds further work. Therefore MMA critical-path traffic shrinks while traffic elsewhere increases. Cache behavior, overlap and retry counts determine the latency tradeoff; lower stack size or total static site count alone is insufficient.

These formulas are bound to this exact cubin. Other K extents can produce a runtime K loop and a different allocation; no universal arbitrary-K traffic bound follows from this two-stage signature. The number of retry iterations is not statically bounded.

## Qualification recommendation

Preserve the original failed no-new-local-sites gate. Completing the predeclared compile-only diagnostics is justified: they cannot launch owned kernels and reveal whether the changed allocation affects native or previously spill-free cases. A future explicit qualification policy may permit numerical testing of the already-spilled stress cases only after recording their full role/loop traffic, provided every planned native and previously spill-free capture remains zero-local, quotas/geometry are unchanged, and REG/STACK bounds still hold. All cases must remain visible. This is a diagnostic gate decision, not backend shape eligibility or a retained performance conclusion.

Do not compose shared R2 with interleave based only on the smaller MMA descriptor traffic. Each first needs complete source/resource evidence and exact coverage; a composition needs its own matched captures, including the R2 stress case and stage-loss geometries.

## Separate source-level liveness opportunity

Current source retrieves `tmem_ptr` before warp specialization and keeps it for the final allocator free. SASS retains the pointer in UR4 from startup through free (`shared` PC0xee70; `interleave` PC0xf9e0). Weight, relay and gather roles otherwise never consume it. Retrieve it inside MMA and epilogue roles, then retrieve it again at allocator free, keeping every existing allocation/wait/barrier/release/free unchanged. CUTLASS `memory/tmem.py:522` implements retrieval as a load from the immutable allocation-result slot, without a wait or mutation. Rubin already scopes pointer retrieval to consumer roles.

This removes an unnecessary cross-role pointer lifetime; it does not directly eliminate the three observed shared-base/grid/count spills or guarantee compiler improvement. The parent has authorized a separate compile-only experiment. It is distinct from earlier rejected role-scoped allocation-wait changes, because rendezvous participation and timing remain unchanged.
