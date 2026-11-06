# Coalesced SF with warp-private payload coordinates

Active, unstaged composition on retained `c1ac8ce7` in
`flashinfer-sf-coordinate-cache-review`. No GPU work or performance claim yet.

The candidate restores the original R1 coalesced SF mapping, Int64 offsets and
unchanged `_copy_gather_sf` interface. Each gather warp writes its existing payload
row coordinates into its own 16-byte-aligned shared slice instead of broadcasting
them into a persistent register array. Only unique lanes write, including OOB
sentinels. A full-warp barrier publishes writes; a second barrier after the last K
issue joins readers before the next work tile overwrites the slice. Gather4 uses
register coordinate operands, so this cache has no asynchronous TMA read lifetime.

The current K-outer/row-inner task loop, election, TMA offsets, expected bytes and
all other pipelines remain unchanged. No row/K interchange, full-WG plane, address
rematerialization, quota change, public argument or tactic axis is added.

The cache requires `64*ceil(b_copy_rows/16)` bytes per CTA (64–1024), included in
both the actual shared struct and automatic K/stage/epilogue storage calculations.
The actual candidate planner preserves stage counts for all 364 recorded FC1
choices. The first wide N256/K8 one-CTA pilot adds 1024 bytes; compiled layout and
driver resources still need verification.

At that wide geometry the unchanged issue order reads 32 four-coordinate packets
per warp per K stage: 2 KiB of logical shared reads per CTA/stage. Native LDS.128
formation and placement are not assumed. This trades shared issue/dependency cost
for possible register relief; original native uniformization means 64 source row
IDs are not 64 guaranteed saved physical registers. Coalesced SF reduces ideal
full-stage request sectors, not unique byte addresses or proven DRAM traffic.

Only the original failing MXFP8 N256/K8/G2 stress pair is planned initially, using
the existing oracle/native helpers and `validation/templates/paired-native/run.py`.
No candidate launch with new local memory; no timing before the native decision.
The failed R1/R2/inline-address artifacts remain immutable in their own leaves.

Related ordering history is recorded in `audits/gather-coordinate-smem-peer.md`:
row-outer coordinate reuse was tested as part of a rejected dynamic-live-group
design, while retained linear issue removed 12/20 uniform branches. This candidate
preserves the retained traversal instead of combining that separate ordering change.


Fresh full qualification is complete: [QUALIFICATION_RESULTS.md](QUALIFICATION_RESULTS.md), 22 fresh calls / 33 native pairs, gate `914ce08b`. The current release cohort is explicitly `moe_utils046552b8`; [CACHE_RECOVERY.md](CACHE_RECOVERY.md) preserves the stopped attempt and cohort boundary. All eight GPUs were released for the separately owned authorized56-cell performance screen; no performance result is claimed here.
