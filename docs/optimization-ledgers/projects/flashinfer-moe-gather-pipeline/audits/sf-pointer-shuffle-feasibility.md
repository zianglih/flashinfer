# SF source-pointer shuffle: read-only feasibility

The mapping is feasible without changing the original payload register coordinates, original SF route loads/division, shared allocation, or pipeline ordering. This is a prospective design, not compiled or measured evidence. Canonical c1ac swap SHA is `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`; the rejected coordinate-cache candidate `15d6eb18` remains untouched.

The existing locations are [`_copy_gather_sf`](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py#L95), [original SF offset setup and copy loop](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py#L3475), and the preserved [R1 coalesced mapping](../experiments/sf-lane-coalescing/r1-preserved/candidate-kernel.py.txt). The minimal private interface would add constexpr `sf_lanes` and `row_batch` to the existing copy primitive; no helper, public parameter, layout contract, or policy axis is needed.

## Exact mapping and address

Let `f(w,l)=8*w+32*(l>>3)+(l&7)`, `G=min(W,4)`, `W=tile_k/(4*sf_vec_size)`, `s=sf_block`, and `b=s%G`. For every supported G=1/2/4,

```
owner = l//G + (32//G)*b
f(w,owner) = f(w,l//G) + b*(128//G)
common_word = G*(s//G)
word = common_word + l%G
```

Keep the original `sf_offsets[row_block]` computation in every lane. Each lane forms its original full 64-bit source pointer using `common_word`, excluding `l%G`. Inside the existing side-effecting asm, shuffle both 32-bit halves from `owner`, reconstruct all 64 bits, and add `4*(l%G)` with 64-bit carry. This exactly selects R1's row offset and word, preserving the original signed-widening/stride semantics and four-byte alignment. Shuffling only the low half or using a low-half-only addition would be incorrect.

Use R1's destination, `row < mma_n` issue predicate and `(row < valid) & (channel < K)` load predicate, with the **actual** word/channel. Invalid original rows still initialize their offsets to zero. The source pointer for an invalid row/K word can therefore be formed, but `ignore_source` must still suppress its global read. SFB remains full-N in each CTA for group2; each pointer exchange stays within its own warp, independent of payload's CTA split.

The [CPU arithmetic check](sf_pointer_shuffle_feasibility.py) records [896 owner identities and 652,800 copy cases](sf-pointer-shuffle-feasibility.json), including 97,680 issued zero-fill cases and 184,320 low32 carry cases. It checks destinations and arrival counts too. This is algebra, not a compiler/runtime correctness gate.

## Convergence and publication

All 32 lanes must execute both pointer shuffles for every constexpr copy slot, including lanes whose copy is predicated off or which do not contribute the final arrival. Only `cp.async` is predicated. The current gather role, work-tile and K loops are warp-uniform; its conditional route loads reconverge before copying. Do not introduce an `if issue`, `if load`, or `if sf_row < route_tile` around the helper.

[PTX `shfl.sync`](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-shfl-sync) requires participating source lanes and matching member masks; inactive/nonmember source values are undefined. Existing FlashInfer [`shuffle_sync_idx_u32`](../flashinfer/flashinfer/comm/mnnvl_cutedsl/cute_dsl_primitives.py#L392) uses full-mask indexed shuffle in side-effecting asm to preserve participation across divergent consumers. This is a relevant instruction precedent, not evidence for this SF mapping.

R1's coalesced arrival predicate and count remain `copy_sf_row < route_tile` and `1+min(route_tile*G,128)`. Keep Gather4 expected bytes, no-increment SF completion, relay/proxy publication, operand waits and producer state unchanged. Startup dependency waits already precede these payload reads. No new shared storage or shared-memory barrier is required, but the two shuffle rendezvous are real per-copy costs.

## Cost and compiler boundary

With B=`sfb_row_blocks`, the prospective source adds `2*B*W` shuffle instructions per warp per K stage when G>1. G1 can emit the original asm unchanged.

| Scale format / K steps | W / G | SHFLs per warp/stage, B=1 / B=2 |
|---|---:|---:|
| SF32 / K4 | 1 / 1 | 0 / 0 |
| SF32 / K8 | 2 / 2 | 4 / 8 |
| SF16 / K4 | 4 / 4 | 8 / 16 |
| SF16 / K8 | 8 / 4 | 16 / 32 |

Lane/index arithmetic, the 64-bit post-shuffle add and any register moves are additional native costs to inspect. Persistent SF state returns from R1's `2*B*G` to baseline `2*B` register words, ideally four words fewer for the failed G2/B2 stress case. Payload register coordinates remain; no spill fix is guaranteed. Compared with `15d6`, this removes all coordinate-cache stores/LDS, planner bytes, the two added warp syncs, and duplicated SF route reads/divisions. N3U top_k22 makes the removed repeated division relevant source work, but it is not an established cause of the EP/TP split.

The common K-dependent channel makes the full pointer shuffle loop-dependent without a new volatile/forcing operation. Nevertheless ptxas could factor uniform address additions and retain shuffled offsets; the existing asm side effect does not guarantee compact liveness. A future native gate must check actual in-loop SHFL/address placement, offset/register liveness, LOCAL0 and preserved normal options, rather than assume R2's hoisting problem is solved.

R1's extra row/K predicates and G-way shared-bank grouping remain. Coalescing promises only the same ideal per-instruction request-sector reduction `R/ceil(R/G)` for R valid SF words, not fewer unique bytes or measured DRAM traffic. G1 has no coalescing benefit. Partial-K tails and duplicate/adjacent token rows can reduce the ideal benefit.

## Closed-history boundary

The prior [`sf-payload-linear-guard-typed`](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/sf-payload-linear-guard-typed/RESULTS.md) experiment reused SF-loaded token IDs for payload coordinates through an XOR ownership permutation, preserved bank-conflict-free SF stores, and was rejected after 23 exact tests and a negative eight-case screen. It did not exchange full source pointers inside the SF async-copy primitive or use the R1 coalesced SF ownership. R1/R2's cached G-way offsets and the later address-rematerialization/coordinate-SMEM attempts are also distinct.

The independent bounded check of both CLOSED_LEADS indices and directly relevant notes found no exact pointer-half-shuffle trial. Closest references in the old optimization directory are `sf-payload-ownership-audit/AUDIT.md:50–52` (raw row-ID shuffles into payload before K, explicitly none inside K), `sf-payload-deferred-offsets/GATE_RESULTS.md:3` (delayed Int64 offset formation), and `sf-transport-audit/AUDIT.md:82–93` (wider loads/scattered stores or data shuffles). This establishes a distinct untested composition within that checked set, not exhaustive historical absence.

Conclusion: a smaller source composition is plausible, with clear full-warp and 64-bit requirements. It remains an uncompiled design; the new SHFL-to-address-to-copy dependency, coalesced shared-store service, and possible compiler rehoisting must be assessed before any performance claim or broad qualification.
