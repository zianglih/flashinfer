# Dedicated TMA roles and a shared operand ring

Read-only review of retained `1e69d0a39`, installed CuTe DSL4.8.0, and the
project-local CUTLASS reference. No production source edits or GPU runs.
Installed pipeline sources are snapshotted beside this note; the remote read
helper only reads package files. Synthetic-routing audit/rejection is complete
in `../synthetic-routing/independent-audit/REVIEW.md`.

## Recommended initial role map

| Physical warp | Responsibility | Necessary dependencies |
|---|---|---|
|0|A weights plus SFA TMA; common operand-ring tail|Published route metadata; matching empty stage|
|1|B activation plus SFB TMA; FC1 startup publication|Ancestor payload dependency wait, then matching empty stage|
|2|SFA/SFB SMEM-to-TMEM copies, MMA, accumulator publication|One operand-full wait; accumulator-empty wait before first MMA|
|3|CLC fetch and tile metadata publication, or idle for static schedule|Published route metadata; metadata-empty and CLC response|
|4–7|Existing epilogue with local thread index `tidx-128`|Accumulator-full; existing partial-release and output-store fences|

Use256 physical threads for the dedicated design. Current public wrappers
already pass `overlap_epilogue=True` (`moe_swap_ab.py:253`); the internal inline
producer/epilogue path is not an autotune tactic. Do not create a new tactic
axis or retain a small-N producer-sharing branch merely to keep old scaffolding.

The current source uses9warps (10withCLC), with four possible producer warps,
MMA8 and CLC9; large-N TMA cases exclude idle producer warps1–3 from loops and
metadata consumers. The new map preserves physical epilogue warps4–7 exactly.
Software index subtraction does not change hardware TMEM lane ownership.
Keep the full four-warp epilogue and its128-thread barrier6.

## Shared full/empty ring is supported

Installed `pipeline/sm100.py:343` exposes
`producer_acquire(state, expected_tx=...)`. It waits on the local empty stage;
only the leader CTA calls `sync_object_full.arrive_and_expect_tx`. Installed
`helpers.py:458` elects one active lane per calling warp for that arrival.
The repository requires DSL>=4.8.0 (`requirements.txt:49`). Direct use of
`pipeline.PipelineTmaUmma` avoids changing the shared legacy custom class.

Construct one operand pipeline with producer group `Thread,2`, consumer group
`Thread,1`, `tx_count=0`, the existing cluster layout, and `defer_sync=True`.
Each producer owns a separate register pipeline state, but both enumerate the
same scheduled tile/K sequence and use the same number of stages:

- Warp0 acquires with `expected_tx = cta_group_size * local_weight_bytes`,
  then issues A and SFA copies for all channel tiles.
- Warp1 acquires with `expected_tx = cta_group_size * local_activation_bytes`,
  then issues B and every SFB copy.
- MMA leader waits once for full, copies scales to TMEM, issues all channel
  MMAs, and releases the common empty stage once after the last channel MMA.

For unchanged layouts, the current exact byte terms are:

```
local_weight_bytes = channel_tiles * (
    128 * tile_k * weight_dtype.width // 8 + sf_stage_bytes)
local_activation_bytes = (
    b_copy_rows * tile_k * activation_dtype.width // 8 + sfb_stage_bytes)
```

Recompute the SFB term from the new copy extent if the narrow-route TMA layout
changes. Use actual TMA transaction bytes, not mixed-weight expanded SMEM
allocation size or allocated-N padding that is not copied.

The two full arrivals are an AND quorum. One producer finishing its transfers
cannot release full before the other producer has both arrived and completed
its transactions. The producers need no mutual warp barrier and can run ahead
up to available ring capacity. They cannot overwrite an SMEM stage until the
single UMMA empty completion releases it. Separate full barriers/two MMA waits
are unnecessary when both operands share this ownership lifetime.

Direct precedent: SM100 MegaMoE NVFP4 `kernel_fc12.py:1455` already uses two
independent TMA producer warps on one `PipelineTmaUmma`, producer count2,
aggregate bytes divided across the two arrivals, and one MMA wait/release.
The role-specific `expected_tx` version makes unequal payload accounting clear.

## One/two-CTA proof obligations

For oneCTA, both producer warps arrive on its local full barrier. For twoCTA,
both CTAs issue their local A/SFA/B/SFB loads, but only the leader CTA's two
producer warps add expected bytes/arrivals. The expected role bytes are doubled.
Existing A/SFA/B atoms use `CopyBulkTensorTileG2SOp(CtaGroup.TWO)`.
`_blockscaled_tma_sfb` explicitly clears the CTA-rank bit24 in its completion
barrier address, so both SFB copies contribute to the leader barrier.

Only the leader MMA waits on full and issues group2 S2T/MMA. Its existing UMMA
empty commit uses the group2 multicast mask to release both CTAs' local empty
stages. Follower producer warps wait their local empty stage; they must not wait
on their unused local full barrier. Producer count is2, not4 or64/128. Keep
both CTAs' TMA issuance even though only one contributes arrivals.

The full ring and empty ring retain identical persistent index/phase advances
across work tiles. Do not reset phase at tile boundaries. Do not skip an
arrival or copy on one role for a partially valid tile: valid-token instructionN
and TMA zero-fill handle payload tails. Padded/terminal CLC entries must be
filtered identically before either producer advances its stage state.

## Startup, PDL, scheduling and teardown

Keep the existing one-time barrier initialization fence, twoCTA cluster join,
and full-CTA TMEM allocation/retrieval join, updated to256threads. They order
barrier initialization by warp0 before any role uses shared barriers. Removing
the full-CTA allocation join requires a replacement initialization join; it is
not a free wait removal. Existing allocator warp0 and peer deallocation
handshake remain valid. An allocator-only/MMA+epilogue subset optimization can
be considered independently, as in Rubin/MegaMoE, after this design is gated.

Prepare waits for its ancestors, publishes routing with device release, then
launches dependents before copying payload/SF (`moe_swap_ab_prepare.py:97`).
Thus weights/scheduler may consume route metadata before GEMM's payload wait.
Warp0 can use one natural persistent weight loop and fill all free ring slots
without a special first-tile prefetch loop or startup-stage skip. Warp1 waits
for its predecessor before any B/SFB payload access. Preserve the wait on all
roles that otherwise read potentially dependent data in the first version;
move/widen the wait exemption only with a full data-flow proof.

For FC1, move the existing startup release+launch signal from warp0 to warp1,
after warp1's ancestor wait. Weightwarp0 no longer necessarily executed that
wait. Preserve `publishes_ancestors`: static grid owner versus each executing
CLC cluster's leader. Do not let an un-waited scheduler/weight warp publish the
FC2 ancestor chain at startup. For FC2 producer-exit publication, weightwarp0
may remain owner, but perform its dependency wait before device release and
signal. Waiting at role exit is also necessary for any scheduler that skipped
the startup dependency wait; preserve its existing end wait.

CLC metadata consumer count becomes `32*(2+1+4)=224` per CTA: two TMA warps,
one MMA warp and four epilogue warps. Scheduler3 is not a metadata consumer.
Both CTAs consume their locally published information; the CLC response ring
continues to expect `32*cta_group_size` scheduler consumers and16transaction
bytes. All active consumers must consume the terminal entry once. Keep
`next_work` release immediately after copying its three fields into registers,
so tile-buffer reuse does not wait for that tile's GEMM/epilogue completion.
No metadata pipeline is needed on the existing static scheduling branch.

One common operand `producer_tail` is sufficient: generic tail only waits all
empty stages, does not arrive on full or mutate the other role's state. After
matched state advances, the weight role can perform the drain; activation can
reach the final join. MMA accumulator tail and epilogue final TMEM-load/output
bulk-store waits remain necessary. Keep final full-CTA barrier1 at256threads
before warp0 relinquishes/frees TMEM, and the allocator's twoCTA peer handshake.
No role may return early, including invalid initial work or zero local tiles.

## What to keep on MMA initially

Keep SFA/SFB S2T copies on MMA2 immediately after operand-full. Their TMEM
slots are reused across K steps, and same-thread tcgen05 ordering currently
orders the copies before MMA and their reuse after prior MMA. Moving them to
independent TMA warps requires new cross-thread publication plus explicit
TMEM slot lifetimes, defeating the initial minimum-barrier design. This is
also how the existing NVFP4 MegaMoE and Rubin finalizer work. Always-TMA SFB
can remove the current cp.async SF pipeline, cluster SF arrival join,
cluster-specific full wait, and SMEM async-proxy publication on the MMA path.
It does not justify removing accumulator-read fences or epilogue scratch joins.

W4A16 is a useful role/PDL precedent but its weight load/transform/MMA ownership
requires separate rings; copying that extra-ring topology into a no-transform
blockscaled kernel is unnecessary. Hopper's separate TMA/WGMMA/epilogue roles
are structurally informative but do not establish tcgen05 group2 semantics.
Rubin/MegaMoE retain explicit MMA/epilogue TMEM ownership and subset allocation
joins. No SM120 source was used.

## Known rejected work and validation boundary

Prior six-warp FC1/FC2 compaction was exact but performance neutral/slower;
producer-role loop factoring increased code/registers and was rejected. This
proposal differs: it assigns independent TMA ownership, removes the narrow-SF
cp.async publication chain, and preserves the physical epilogue warpgroup.
No speedup is asserted before new codegen and paired measurements.

The first gate should cover one/twoCTA, narrow/wideN, both channel-tile counts,
all four blockscaled formats, PDL off/on, static/CLC, zero/partial/multiple work
waves, and graph reactivation. Inspect expected-byte arrivals, single MMA full
wait/empty commit, unchanged S2T/MMA ordering, registers/spills and markers.
Broad sanitizer remains deferred by the user.

Primary hardware references (CUDA13.2.2 PTX9.2):
[TMEM lane restrictions](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-tensor-memory-ld-st-access-restrictions),
[mbarrier phase completion](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier),
[bulk tensor copy](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-tensor).

### Prepare integration update

Layout owner confirms private SF row padding with `P=ceil_div(N,128)*128`:
`physical_sf_row=(logical_row//N)*P+logical_row%N`. Payload rows remain compact.
The activation warp TMA loads `P/128` full atoms per stage into each CTA's local
SFB. Thus local SFB transaction bytes remain `P*tile_k/sf_vec_size`, exactly the
existing `sfb_stage_bytes`; group2 continues to duplicate full SF into both
CTAs. TMA row-block coordinates become `route_index*(P/128)+subblock`; K-block
coordinates stay separate to preserve zero-fill on K tails. This changes
private prepare/FC1 output scale addressing and buffer allocation, not the
shared operand-ring byte formula. Source/GPU integration is still pending.

### Integrated kernel review and MMA startup wait

The initial on-disk rewrite matches the proposed protocol: producer count2,
role-local transaction amounts,224 metadata consumers, persistent stage states,
one common operand tail, unchanged accumulator phase logic, startup signal on
activation1, and deferred waits on weight0/scheduler3 before exit/publication.
The existing public per-token intermediate quantizer and preallocated FC1 SF
buffer validation need integration with the new private layout; these were
reported to the layout owner before the source gate.

MMA2 can also defer its predecessor wait when early weight prefetch is enabled.
Before the shared full acquire, its work is descriptor/fragment construction,
state construction, local accumulator-empty acquisition, and reads of published
routing metadata. It does not read global payload, alpha, norm, or per-token
scales. The actual data chain is predecessor completion -> activation1 wait ->
B/SFB TMA -> operand-full completion/acquire -> S2T/MMA. Preserve the full wait
before every S2T issue and a final MMA dependency wait for follower/zero-work
paths. Keep the epilogue's initial wait because it reads global scaling data.
This recommendation changes placement, not removal, of the dependency wait.
