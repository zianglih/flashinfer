# Canonical SFB multicast

Independent candidate on `2995bfda8338ca6ae623fbc2657d44e35e665627` in
`../../../flashinfer-mainloop-20261027`. One Blackwell core file changes;
all edits remain unstaged. No other backend or public/tuning policy changes.

The current wide-scale path issues an identical full SFB TMA load in both CTAs.
CTA0 instead issues one multicast request to both existing local buffers. This
removes one TMA request per canonical row block per K stage per CTA pair.
Both local scale buffers and their group-2 shared-to-TMEM copies remain necessary.
No DRAM-bandwidth or end-to-end speedup is claimed before measurement.

## Ownership and completion proof

- The launch cluster is exactly `(cta_group_size, 1, 1)`, with size one or two.
  The group-2 destination mask `0b11` therefore names exactly its CTA0/CTA1.
  Each CTA has the same SharedStorage layout and SFB stage offset.
- The existing group-2 UMMA empty release covers reads of **both** local SFB
  buffers. CTA0's existing producer acquisition precedes multicast and protects
  reuse of both destinations, even if CTA1's producer has not resumed yet.
  CTA1 no longer writes SFB itself. Weight/B writes occupy different storage.
- Group-2 multicast redirects each destination's completion to its even peer.
  Both full SFB byte contributions therefore still reach CTA0's full barrier;
  the original `2 * sfb_stage_bytes` expectation is unchanged. The consumer
  cannot start shared-to-TMEM copies before both destination copies complete.
- The request remains after the payload dependency wait. Startup prefetch
  continues to issue only A/SFA and leaves B/SFB bytes outstanding. No ancestor
  publication, startup stage, phase, tail or routing rule changes.
- Full canonical SF atoms are copied regardless of runtime MMA N. Short N and
  inactive channel-tail CTAs still receive the same scale bytes. The descriptor's
  separate K coordinate retains its existing short-K zero fill. The local buffers
  and raw source/descriptor coordinates are unchanged.
- One-CTA assembly construction is byte-identical. Narrow SF transport is not
  touched. The group-specific instruction/owner distinction expresses multicast
  destination ownership, not a model/dtype profitability threshold.

The [PTX copy specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-tensor)
defines destination replication and group-2 completion redirection.
[`SM100_TMA_2SM_LOAD_MULTICAST_3D`](../../../references/cutlass/include/cute/arch/copy_sm100_tma.hpp)
at CUTLASS `91843b71d90737e0a9b86f7d9df213cff5a3526f`, lines281–304,
uses the same cluster-space instruction, 16-bit mask and even-CTA barrier mapping.
That generic helper supports partitioned copies from both CTAs; our duplicated
full copy permits a single issuer. The older
[`SFB_COPY_AUDIT.md`](../../sfload_experiment/SFB_COPY_AUDIT.md) identified this
opportunity but did not implement or measure it.

## Instruction evidence and validation boundary

The source-bound retained structural capture
`scripts/simplicity_20261027/validation/structure-final/evidence/clc-gpu0/candidate/config1-fc1-pdl0.sass`
has two SFB `UTMALDG.3D.2CTA` sites at `0x1160/0x1170` (N256's two canonical
row blocks), executed by both CTA producers. The corresponding PTX emits plain
nonmulticast TMA, with no CTA0-only predicate. It is instruction evidence for
duplicate requests, not a current-source timing result; fresh captures must pin2995.

`verify_source.py` checks that the complete executable AST differs only in the
SFB helper and issuer admission, executes both helper constructions with scalar
stubs to prove one-CTA assembly/operands identical, and enumerates unchanged
local byte footprints and barrier accounting. It is not a GPU correctness test.

Required gate: exact changing-route replays for all four formats, both phases,
PDL on/off, static/CLC, one/two CTA; additionally wide per-token and mixed formats,
short K and inactive channel tails. Compare one-CTA encoded SASS, two-CTA TMA
instructions, stage/geometry/resource counts and spills. Timing follows only
after source and gate review, using unchanged saved public tactics and CAAC.

`probe_sfb_multicast.py --config-ids 0,1,2,3,4,5,6,7` supplements the unchanged
main gate with four formats × static/CLC at H384/M256/N128. Each case exercises
both phases and both PDL modes with balanced, skewed, empty and reactivated
routes: 32 core pairs and 64 source-paired replays. `probe-origin.json` pins the
base/new helper hashes and `probe_sfb_multicast.patch` records the bounded delta.
