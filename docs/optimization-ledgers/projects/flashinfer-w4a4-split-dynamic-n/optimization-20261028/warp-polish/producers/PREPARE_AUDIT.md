# Prepare and shared-quantizer follow-up audit

Read-only at99f4 while the combined producer gate runs. No additional source
change is proposed from this audit.

`PrepareRouted.kernel` already has a compile-time PDL guard, one predecessor
wait before all dependent metadata/payload reads, and an early startup signal.
It uses no shared scratch or CTA barriers. Payload copies already use256-bit
loads/stores when the existing alignment contract permits; retained experiments
verified actual Blackwell LDG/STG256 instructions. W4A16 keeps its legacy
16-byte-view compatibility. No wider payload operation is available to replace
this path.

SF input is loaded into one or more register words before payload copying,
which exposes independent memory work rather than introducing synchronization.
The later stores transpose those words into the canonical private TMA atoms.
They are scattered by the required SF layout, so simply changing their width
to256bits would combine unrelated destination rows. Such vectorization needs a
new ownership/transpose design and should not be presented as a line-level
instruction cleanup. RouteN and topK are compile-time values; the repeated
quotients in source are strength-reduced rather than requiring runtime division
policy. The logical-row traversal already skips unused physical SF padding and
never reads poisoned invalid mapping slots.

The shared per-token quantizer's startup PDL is also compile-time guarded. Its
row-amax reduction requires cross-warp communication, and the existing
publication/reuse barriers protect that scratch. Its optional routed SF pitch
already maps logical rows directly into the same private TMA layout. Removing
those joins would need a new reduction ownership contract. The current polish
does not justify touching this shared quantizer or the unscaled W4A16 path.

Historical NCU/Nsys evidence under `optimization-20261027/DIAGNOSTICS.md` showed
prepare extending the prefill critical path, but those older timings do not
establish a fresh bottleneck after warp specialization. The previous regular
TMA preparation ledger already tested bounded hardware-derived grids and
retained256-bit copying. Avoid repeating those experiments without a new trace
showing a different limitation. Current producer-side SFB cache priority is the
small general fix: it keeps payload and scales at the same existing activation
priority without changing writer ownership, padding or synchronization.

## SF ownership follow-up

Fresh V3 MXFP4x8 T16384 NCU from the epilogue agent measured prepare at
44.256us: DRAM read81,400,832B/write120,860,416B,59.63% peak DRAM, L2 read
5,371,233 sectors with18.46% hit rate,7,013,344 warp instructions,32 registers,
128 threads and2368 CTAs. The bounded pass did not collect per-PC/store-sector
attribution. These counters establish a substantial prepare phase but do not
establish what fraction is caused by SF accesses.

For a fixed row, consecutive lanes store Uint32 words at512-byte intervals,
so32 active lanes touch32 sectors. Across a full128-row physical atom, mapping
`row = (lane % 4) * 32 + lane // 4` for a fixed SF block instead touches four
contiguous sectors. This illustrates the geometry, not an implemented design.
Route tiles below128 contain unused physical row quadrants, so the full
coalescing bound is unavailable without touching unused padding.

A unified two-dimensional ownership could give each row four payload lanes:
four32-byte operations still form a128-byte contiguous segment. More rows per
warp could reduce SF-store sectors, but each row then has many more sequential
payload iterations, source SF loads become less coalesced, and each warp must
manage several routing values. Any design must keep the no-scratch/no-barrier
benefit and preserve invalid-row/mapping handling.

Relevant prior trials are distinct:

- `prepare-warp-20261026` gave each warp one row, preserved the same scattered
  SF destination geometry, and lost up to3.7% decode in the general campaign.
- `scripts/prep_linear_sf_experiment` kept payload ownership and added a second
  destination-linear SF traversal. It passed36 byte checks but saved only
  0.043/0.075us for T32/T128 prepare, with register use30 to32. It repeated
  routing/index traversal and had no measured NCU traffic improvement.
- `optimization-20261027/prepare` tried separate payload/SF warp groups. Wider
  CTAs and a smaller grid erased issue overlap; N3U prepare regressed18.7%.
- Shared-memory SF transpose and wider SF source-vector variants also remain
  rejected in the local ledger.

Next discriminating evidence is per-PC STG sector/issue attribution, ideally
also source-load sectors, on the same current V3 prefill source. Do not infer an
SF bottleneck from aggregate DRAM or read-sector numbers. No new prepare source
changes or GPU work were launched for this assessment.
