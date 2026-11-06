# Mixed K96 descriptor construction audit

Read-only source and existing generated-code audit; no source or GPU change.

Current emitter calls `make_umma_smem_desc` for each 96/64 instruction at
`moe_swap_ab_kernel.py:173–194`. Layout-derived SBO, SW128 mode, version and
base offset are invariant; the dynamic stage base and the compile-time native
start/next-segment offsets provide the variable address fields. All operand
starts and stage extents obey the 1024-byte SW128 period alignment.

Existing generated PTX demonstrates incomplete reuse, rather than merely a
source-level opportunity: `k-tail/k96-r2/evidence/gate/adversarial-r2/kernel-001.ptx`
lines842–851 builds the first K96 descriptors from prehoisted r30/r31 and one
stage-index value r221. Lines861–879 rebuild both second-K96 descriptors with
shifts/adds/ands even though start96 is in the same K256 segment and has the
same absolute-LBO address. In this pair, only the encoded current address
increases by3 (48bytes/16); the high word and next-segment field are unchanged.

The archived CUTLASS primary source already gives the intended pattern:
`scripts/sm103_k96_audit/sources/cutlass/mma_traits_sm100.hpp:334–340` updates
only the descriptor low32bits in DescriptorIterator. Lines4612–4625 reuse
current/next native descriptor values, set absolute-LBO mode, and copy the
next descriptor's start-address field into LBO.

A general implementation can reuse native stage descriptor fields and derive
native offsets from the existing partition layout. Do not use start/2 across
K256 boundaries: SW128 segment displacement depends on that layout. Preserve
relative-LBO mode for K64 instructions, and select the correct next segment
for every K96 instruction. A global uniform K96 stride would also violate
stage ownership. Actual SASS and resource measurements must qualify the
proposed reuse; this note does not claim that all emitted descriptor sites
have the demonstrated redundant sequence.

The associated SASS confirms twelve scalar construction sites for the second
pair at0x2040,0x20e0,0x20f0,0x2170,0x2190,0x21b0,0x2220,0x2240,0x2250,
0x2260,0x22b0,0x22c0. `descriptor-sass-sites.json` preserves the instructions.
This is one adversarial K192 specialization; wider frozen-winner captures are
still needed to determine the general dynamic cost and resource tradeoff.
