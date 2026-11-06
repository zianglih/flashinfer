# Duplicate terminal TMEM load wait: caller audit

Read-only source audit at aab93f, no GPU or implementation changes.
`Sm100BlockScaledMoeEpilogue` has one construction site in the shared Blackwell
blockscaled core and exactly two `run()` callsites in that core. Other repository
objects called `epilogue.run` are different classes and outside this proposal.

| Path | Caller | Existing completion/release |
|---|---|---|
| Inline producers also execute epilogue | core1212 inside channel loop | `utils.run` terminal wait, then core1229 wait after the channel loop; core1230 releases bank once. |
| Dedicated epilogue warps, ordinary path | core1302 inside channel loop | `utils.run` terminal wait, then core1321 wait after the channel loop; core1323 releases if not overlapping. |
| FC1 overlapping windows | core1269 calls `run_overlapping_fc1`, not `run` | Helper fences/releases at protected-read boundary, then reads remaining nonoverlapping slabs; core1321 retains final drain, no duplicate release. |
| FC2 bulk, ordinary accumulator | `run` → `_run_bulk_direction` | Internal store/proxy/barrier sequence and bulk-group shared-read drain stay; terminal `run` wait duplicates caller wait. |
| FC2 bulk, overlapping accumulator | Same entrypoint | Internal load fence precedes protected-region release; skipped overlap slab still fences/releases; no-live-channel CTA releases without reads. Caller wait remains. |
| Regular FC2 / fused finalize / ordinary gated activation | Branches in `run` | All converge on terminal wait and then the caller wait. Output math/store branches do not replace accumulator ownership. |

The minimal common simplification is **delete only the final
`fence_view_async_tmem_load()` in `utils.run`**, keeping both core waits and all
helper fences that precede an ownership release. Across multiple channel
tiles, the caller's single wait drains all loads before releasing the bank;
the channel fragments are disjoint. Physical-N16 only has one channel tile.
Do not remove both terminal waits, or infer the separate FC1-overlap entrypoint
has an equivalent final wait of its own.

For the new direct-N16 early-release branch, the explicit wait after its two
raw loads is already the last TMEM-load completion point. There are no later
TMEM accesses. The dedicated core can skip its late wait and late release only
under the identical static early-release flag. It must still advance the
consumer state once, and join the final CTA barrier. Other ordinary/bulk/overlap
paths keep their core drain unchanged. The inline path's fence need not change:
the initial eligible direct-N16 configuration uses dedicated epilogue warps.

No change is proposed to TMEM-store proxy fences, TCGEN async shared fencing,
bulk-store waits, named barriers or the final allocator join. Static source
inspection establishes the duplicated ownership boundary; emitted code should
confirm one wait remains before each ordinary release and exactly the early
wait remains for direct-N16. Existing matching-control adjacent PTX waits are
supporting evidence, not authorization to remove unrelated waits globally.


## Multiple channel tiles: final follow-up

Removing the helper terminal wait changes completion from per-channel to the
single caller drain after the channel loop. This is safe for the existing
scratch layout: `_blockscaled_transpose16x32` uses exactly32 rows ×32 columns
at the channel base plus token_start. Its bottom half uses a row+16 offset or
column+16 for a16-column destination; it never exceeds that32-column slab.
For N128, token_start0/32/64/96 covers channel0 columns[0,128), while channel1
starts at128 and covers[128,256). Their scratch regions do not alias.
Ordinary gated `run` calls `_run_token_group` with `release_acc=False`, so
there is no hidden per-channel ownership release depending on its terminal
wait. Bulk paths with early release keep their internal completion fences.

The retained NB2 geometry already takes the separate `run_overlapping_fc1`
entrypoint (`acc_cols==256` and SF footprint<=64), whose protected-read release
and core drain are unchanged. This fact is additional context, not a substitute
for the disjoint-scratch proof above. Runtime source remains untouched.
