# K-major channel-interleaved MMA probe

The retained helper issues every K atom for channel zero, then repeats the K sequence for channel one. The candidate issues the two channel instructions beside each other for each K atom. This shortens the logical lifetime of the common B descriptor, without changing either accumulator's arithmetic order.

- Base: `b52e4e09649dc180fc7583a25ec35ff55f04654d`; candidate kernel SHA `3b0114ea7b8099d759d9c62808d8752d2fa94fdda720f77024f4a6c4b8be64ac`.
- The actual helper AST, after reversing tuple indexing and the two loops, exactly matches the retained helper. The caller tuple entries exactly match both original calls. The remaining module AST is unchanged except the combined optional MMA marker range.
- Each channel keeps its first-K initialization predicate, A descriptor and SFA address. B and SFB are shared. K96 descriptor/LBO arithmetic is unchanged, and the K position advances once after all channels consume the atom.
- Both SFA copies and SFB publication precede the combined issue helper. Operand release follows every channel/K instruction. The accumulator producer/consumer and overlap-release protocols are unchanged.
- The earlier CPU proof covers 18,432 K-order cases, 504 disjoint dynamic-N channel regions and 90 overlap intervals. These are static proofs, not numerical execution.

## Bounded qualification

`plan.json` selects 12 existing matrix signatures (22 FC1/FC2 captures), plus two existing native frozen winners (4 captures). The matrix covers all four formats, both channel counts, static and CLC scheduling, one/two CTA, K96 tails, and the two inherited M512/K8 MX spills. The native cases cover actual MXFP8 ReLU² and per-token SiTU winners.

Only the candidate compiles. Immutable b52-equivalent controls are reused from `control128-epilogue248-ce4`; subset receipts bind every original raw resource/PTX/CUBIN/SASS hash while renumbering only the capture index. The resource gate requires unchanged geometry and register quotas, and no growth in REG, STACK, LOCAL or LDL/STL site counts. The compile wrapper replaces FC1 callables with no-ops and intercepts FC2 before a callable can return. Ordinary setup/quantization may execute; owned MoE kernels cannot launch. No numerical or timing result is implied.

Inspect whole-kernel and role-local instructions, common-state local traffic, uniform-register transfers and uniform versus divergent branches. A smaller stack alone is insufficient: reject relocation/growth of common-state spills or increased local instruction sites. One-channel cases should largely compile identically; this is checked rather than assumed. The compiler may hoist descriptors despite source order, so the proposed liveness benefit remains unproven until actual code generation is examined.
