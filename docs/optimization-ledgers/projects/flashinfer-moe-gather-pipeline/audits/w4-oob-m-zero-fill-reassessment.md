# Defined-zero M-padding reassessment at 2b8

**Keep closed without a prototype.** The same defined-zero alternative was already reviewed at the current source in [w4-oob-m-zero-fill.md](w4-oob-m-zero-fill.md). That was a source-only closure, not a failed timing trial. This reassessment adds the full frozen-choice count and corrects the scope of the group-2 critical-path argument. No source, compiler, GPU, tactic, or PR change was made.

Retained HEAD is `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`, with a clean source checkout and W4 kernel SHA `5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d`. [The replayable audit](audit_w4_oob_m_zero_reassessment.py) verifies the prior five source hashes/layout evidence, all 104 frozen selections including ten recorded defaults, and all three shared-transform callers. Its [receipt](w4-oob-m-zero-fill-reassessment.json) contains all 208 FC-stage geometry records.

## Current affected choices

These counts describe the channel sweep of each valid routed work tile, not a fraction of E2E latency or a count of expert/token work tiles.

| Model/topology | FC1 physical logical-M extent | Tokens with a wholly padded CTA | Padding per channel sweep | MMA group |
|---|---:|---|---|---|
| V4.1 Flash TP4 | 1152 | 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384 | 1 of 10 M128 CTAs | Group 1 at T1/T4; group 2 otherwise |
| Nemotron3 Ultra TP8 | 640 | 4, 8, 16, 4096, 8192, 16384 | 1 of 6 M128 CTAs | Group 2 |
| All remaining model/topology choices | — | None | None | — |

All FC2 shapes are aligned. The eight FC1/FC2 M extents are K3 EP 6144/3584, K3 TP 768/3584, N3U EP 5120/2048, N3U TP 640/2048, V3 EP 4096/7168, V3 TP 512/7168, V4.1 Flash EP 4608/5120, and V4.1 Flash TP 1152/5120. Gated FC1 M includes both gate/up rows.

Thus 19 of 104 cells are affected; 17 remain after excluding T1/T2. Of those 17, **16 use group-2 MMA and one uses group-1 MMA** (V4.1 Flash TP T4). A two-CTA scheduling cluster does not necessarily imply group-2 MMA. The prior note's valid-peer argument must not be applied to that group-1 case.

## Existing information and minimum source cost

The split transform caller already has exact `mA_mkl.shape[0]` and the cached metadata `work_tile.cta_coord_m`. The predicate would be CTA-start M < logical M, using the existing physical `self.cta_tile_shape_mnk[0]`. This adds no global load, tensor metadata, public argument, or tuning axis. Both static and CLC callers use that coordinate. The existing `m_cluster_aligned` flag identifies the easy all-aligned specialization, but cannot identify which CTA in a misaligned cluster is wholly invalid.

The shared `_transform_tile` has neither M coordinate nor logical M; its stage-local fragments cannot recover them. The smallest legible handoff is **one private Boolean argument, forwarded at three call sites**: one split call and two Mega calls. Mega already has the CTA-local `work.tile_m_idx` and constexpr `intermediate_gateup`/`hidden` in its existing phase branches. Its divided logical-MMA index in `_weight_task` is unsuitable. The complementary [Mega handoff audit](w4-oob-m-mega-handoff.md) verifies this independently.

Keeping the live path's current raw-peek placement implies roughly **18–25 added nonblank lines**, plus indentation of the existing decode block: private argument/call expressions, a uniform zero-versus-decode branch, zero-fragment materialization, and a second copy of raw-state advance/next-peek handling. This is a source estimate, not an implemented diff or native resource prediction. The predicate may remain live across the K loop; branch, register and scheduling costs need emitted-code evidence before any stronger claim.

The existing K-tail predicate cannot absorb M validity. Its false branch skips TMEM stores and omits the next raw peek because it can occur only in the last K stage. Whole-M padding persists across K stages, and MMA still reads those rows. A correct zero path must preserve every live-K TMEM store, raw wait/release, decoded acquire/commit, cursor advance/phase and next raw query. Mega must also keep consuming its full padded K extent. No persistent initialization bit or skipped-arrival policy is justified.

For the public M128 geometry, both transform groups cover all M rows and divide K. Gate/up groups fit inside the CTA, and whole-invalid CTA starts are beyond the 128-row-padded SF extent; partial-M CTAs remain on the normal path. The saved 5,120-record layout proof supports that public geometry. It does not establish a generic private-M64 specialization.

## Cost and decision

At full stage K256, an invalid M128 CTA could avoid up to 16 KiB packed-weight SMEM reads, 2 KiB SF SMEM reads and 32,768 conversions. It still writes 64 KiB of defined BF16 zeros to TMEM. Every raw TMA issue/expected-byte operation, all pipeline publications, the same MMA operations, allocations and occupancy constraints remain. The skipped reads are from SMEM; TMA already handles the OOB region, so this is not a valid-weight DRAM-traffic reduction. Zero register materialization is not free.

For group 2, `PipelineAsyncUmma` counts `32 * 8 * 2 = 512` transform-thread arrivals. The valid CTA still performs its full load/decode before the shared MMA phase becomes ready. That makes a simple critical-path benefit doubtful, **not impossible or disproven**: arrival skew, scheduling or power effects would require evidence. For group 1 the count is 256; the valid-peer decoded-ready argument does not apply, but there is still no saved profile isolating the wholly padded CTA's transform as the delay. Aggregated wait/PC samples do not identify it.

Bounded searches of the original July W4 optimization ledger, the October gather ledger/CLOSED_LEADS, full-M transfer review, and current audits found no actual whole-M defined-zero trial. The known source-only closure is exact; partial-K group clipping, scheduler padded-ticket filtering and uninitialized-TMEM skipping are different mechanisms. The partial-K experiment's neutral result is context, not evidence against this alternative.

**Decision:** added private handoff/control work has no demonstrated exposed latency to remove, while the group-2 valid peer and all TMEM/MMA/publication work remain. Keep this lead closed rather than prototype it for instruction-count savings alone. Reopening would require a source-bound padded-versus-valid CTA arrival/critical-path signal, not another model-specific branch or shape gate.
