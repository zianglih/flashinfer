# Gathered FC1 SF ownership: bounded feasibility

Read-only, 2026-10-30. Retained source `c1ac8ce7341039db65195b99445fcdeb193cf226`; swap kernel SHA `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. No source edit, compilation, GPU work, or new performance measurement.

**Recommendation: do not prototype the same-stage relay design.** It can reuse the existing barriers legally, but turns four parallel SF issuers into one serial issuer and removes SF stage run-ahead. Restoring that run-ahead needs another cursor/refill schedule. Splitting the four gather warps into SF/payload roles retains staging, but has a substantial payload-coordinate/register tradeoff rather than a demonstrated simple deletion. The exact current design was not found in the bounded history; this is a source-cost rejection, not a claim that it was already measured.

## What the new profile establishes

[The four-report diagnostic](../experiments/sf-coordinate-cache/ncu-diagnostic/RESULTS.md) binds the actual retained normal FC1 images and the rejected `15d6` composition. In N3U TP W4A4 T16K, SF coalescing reduced theoretical SF global sectors 57,671,680→14,417,920 and SF issue/completion MIO samples 1,601→3. It also introduced coordinate LDS→R2UR dependencies: 3,564 short-scoreboard samples at those R2UR sites, while every elected coordinate LDS.128 was conflict-free. EP has the same fourfold sector reduction and a different balance of waits.

This supports investigating ownership separately from the rejected coordinate cache. It does **not** establish a DRAM bandwidth problem, a removable completion wait, or a production PDL cause. The profiler serialized kernels; sampled stalls are not additive time fractions. The original 56-cell rejection remains unchanged.

## Existing contracts and the smallest relay variant

Source links below refer to [the retained kernel](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py).

- Lines 1616–1630 assign weight warp 0, activation/relay warp 1, MMA warp 2, scheduler warp 3, epilogue warps 4–7, and gather warps 8–11. Both the first warpgroup and gather warpgroup use the existing 128-register role budget (2787–2790, 3411–3413); the loaded function's 168-register attribute is a different quantity. There is no native evidence that the proposed relay's larger live offset set fits that budget.
- The gathered branch of activation warp (3020–3054) currently does only local completion wait, async shared proxy fence, one relay arrival per CTA, and consumer-state advance. It already executes the required PDL ancestor wait and startup publication (2757–2780).
- The gather group (3411–3582) caches payload coordinates and SF source offsets outside the K loop, waits the common operand-empty stage, issues SF and Gather4, and advances its producer state. SF is **full N in each CTA**, even for group-2 MMA; only payload rows are split.
- Local gather-full has `1 + min(N,128)` arrivals (2731–2743): one `arrive.expect_tx` for all payload bytes, plus completion from every participating SF thread. The separate cluster gather barrier still needs one relay per CTA. MMA releases operand storage after consuming all channel tiles (near 3290).

A same-stage relay implementation could retain its existing consumer state: wait operand-empty at the same index and `consumer.phase ^ 1`, issue that stage's SF copies, contribute per-thread `cp.async.mbarrier.arrive.noinc`, wait local gather-full at the current consumer phase, fence, relay, and advance once. The producer/consumer phase offset matters on first use and ring wrap. It would also retain `scheduled_valid` from `next_work` and reproduce the existing route/K predicates and zero fill. No new barrier is logically required.

The local expected-arrival count must match the **new participating SF threads**, not remain `min(N,128)`. A simple universal one-warp version can have all 32 lanes arrive once, including lanes with no issued copy, and use 33 expected arrivals including payload. Keeping the old sparse lane map with a smaller participation set requires deriving its union across virtual row groups; `min(N,32)` is not that derivation. One elected completion cannot stand for other lanes' cp.async operations. Payload expected bytes, cluster relay count, weight/SFA publication, and final CTA/TMEM join stay unchanged.

CLC metadata already counts warp 1 and all four gather warps (2698–2712). Keeping every role's `next_work`/release once per work tile needs no CLC count change. Empty work must still follow the existing startup publication and terminal join. The existing operand-empty wait protects SF reuse across stages and experts; the local completion wait alone does not.

**Progress cost:** after issuing stage `s` SF, this one relay warp blocks until stage `s` payload and SF both complete. It cannot issue SF for `s+1` while waiting, although payload and weights may fill the remaining operand stages. Thus at most one SF stage is in flight. Multiple-stage SF run-ahead needs a separate producer/refill position or a different owner, recreating schedule/state complexity rather than reusing the one consumer state for free.

## Issue and live-value estimates

Let `B=max(1,N/128)`, `W=tile_k/(4*sf_vec_size)` four-byte SF words per row per stage, and `G=min(W,4)` adjacent-word lanes in the previously tested coalesced mapping. Current modes give W=1/2 for MX8 or mixed MX4x8, W=2/4 for MX4, and W=4/8 for NVFP4, for existing K-steps 4/8.

These are source copy-site counts per stage, excluding address/predicate/completion instructions, not measured execution times. The relay columns preserve the existing conflict-free row permutation by iterating its four virtual warp groups; compacting narrow rows into fewer instructions changes the shared-bank grouping.

| Route N | B | Current sites per SF warp / all four | One relay warp | Two SF warps, each | One-relay cached Int64 offsets, current / coalesced |
|---:|---:|---:|---:|---:|---:|
|32|1|W / 4W|4W|2W|4 / 4G|
|64|1|W / 4W|4W|2W|4 / 4G|
|128|1|W / 4W|4W|2W|4 / 4G|
|256|2|2W / 8W|8W|4W|8 / 8G|

For the measured NVFP4 W=4 cases, EP N128 moves 4 sites per current warp to 16 in one relay; TP N256 moves 8 to 32. W=8 doubles those numbers. Coalescing adjacent words changes which rows/words lanes own but does not remove the four-byte copy sites. A one-relay N256/G4 cache has 32 Int64 offsets, or 64 32-bit register values before pointers, predicates, and pipeline state; the corresponding current-map cache has 8 Int64 offsets. Reconstructing addresses instead changes the arithmetic/lifetime tradeoff, not a proven free reduction.

N32 illustrates the compaction boundary: canonical four-byte row words occupy only eight distinct banks. The existing four warp owners each issue to eight distinct banks. Packing all 32 rows into one issue creates four distinct words per bank. Consequently `N/32*W` is an instruction-count lower bound for a compact mapping, not a bank-free equivalent of the retained map. The coalesced G-lane alternative deliberately has its own canonical shared-bank contention; it must not be described as unchanged transport.

## Alternative split inside the existing gather warpgroup

One SF + three payload warps, or two + two, lets the SF producer advance through the full ring independently while leaving the relay unchanged. Existing barriers suffice with corrected participating-thread arrivals, but this is a new role balance and mapping.

- **1+3:** payload tasks become `p + 3*t`. This does not inherently require runtime division by three; row-group division remains by a power of two. However, row groups are generally not divisible by three, so the same warp no longer owns the same row group in each K chunk. The current reused coordinate-index formula stops working. For N256/C1, the retained four-way partition caches 64 Int32 row coordinates per lane. A row-stable three-way mapping needs up to 88, plus remapping/reordered issue; a naive per-task K8 cache can reach 172. Those are logical live-value estimates, not predicted allocated registers or a spill proof.
- **2+2:** power-of-two mapping is simpler, but doubles payload-coordinate ownership: N256/C1 reaches 128 Int32 row coordinates per lane before any other state. Each SF warp issues `2BW` sites and holds up to `2BG` Int64 offsets. Removing its SF cache does not establish that the payload warp's enlarged coordinate set fits the unchanged 128-register role budget.

Neither split removes payload or SF work. It reduces issuers, changes source loops/role branches, and may shift the same pressure. The current evidence does not justify a general simple implementation, a quota change, or a shape exception.

## Uniform election is already optimized in the actual image

The retained TP [PTX](../experiments/sf-coordinate-cache/ncu-diagnostic/evidence/tp-control/loaded-codegen/56307/fc1.ptx) has a separate `elect.sync` scope around each of 16 Gather4 sites (near 4710–4900). Its exact [SASS](../experiments/sf-coordinate-cache/ncu-diagnostic/evidence/tp-control/loaded-codegen/56307/fc1.sass), gather role PCs `0xc830..0xe430`, has **one native ELECT**, 16 Gather4s, and eight SF LDGSTS sites. Widening source election scope therefore has no demonstrated election saving in this specialization.

That native region also has 17 `MOV.SPILL` uniform→general-register transfers and 17 `R2UR.FILL` reversals. For example `0xd7f0` saves UR54 into R8 and `0xe2e0` restores it. These are **not local-memory spills** (LOCAL0); the compiler already recognizes uniform values but has a uniform/general-register storage tradeoff. The existing [Gather4 helper](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py) lines 116–138 takes ordinary `r` coordinate operands. Warp-uniform values after shuffle do not guarantee persistent hardware UR allocation. There is no demonstrated source-only hint here that removes repeated R2UR without changing ownership/liveness. Removing SF might change allocation, but that is an unmeasured consequence, not a compiler-feasibility proof or an independent candidate.

## Historical and reference boundary

Both current and old `CLOSED_LEADS.md` were consulted. Exact frozen A/B in old `element-scale-ownership-20261029` still retain `sf_offsets` and `_copy_gather_sf` in the gather group (A near 3703–3772, B near 3700–3769). They split weight/SFA and regular FC2 producers, with refill cursors; their −3.826%/−3.690% results do not directly test this SF-only relay proposal.

The closest measured one-warp SF ownership is old [`sf_warp_reuse_experiment`](../../flashinfer-w4a4-split-dynamic-n/scripts/sf_warp_reuse_experiment/README.md): warp 3 loads compact SFB, waits SFA, and publishes both to two TMEM slots under an N16 generated-FP4 policy. It lost 1.2900%/0.8321% at T32/128 and grew 1,135→1,599 non-padding instructions. Its compact layout, independent source lifetime, and publication role differ. The extra-warp `sf_publisher_experiment` and 128-participant `producer_roles_experiment` are also related, not exact duplicates. No matching canonical full-N relay trial was found in this bounded history.

Reuse the existing [transport audit](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/sf-transport-audit/AUDIT.md): canonical SFB scatters adjacent four-byte K words 512 bytes apart. Rubin's four SF gather warps use 16-byte cp.async into linear SMEM and **another four transform warps** plus a separate transformed ring (Rubin source 2092–2347). Blackwell Mega receives canonical SF prepared and published by communication/refine work before its TMA-SFB loop. Neither is a drop-in precedent for one relay warp, unchanged canonical layout, and no new staging/state.

The SF request/MIO problem is measured, and ownership separation is a distinct hypothesis. Under the requested simplicity constraints, the same-stage relay loses useful overlap, the staged splits add coordinate pressure/mapping complexity, and broader election has already been optimized in the retained native image. No bounded source prototype is recommended from this audit.
