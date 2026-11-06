# Warp-owned routed preparation experiment

Independent checkout: `../flashinfer-prepare-20261026`, detached at
`0def601d6603df828ea39679b41ccbce64f7f09e`. The only source edit is unstaged
`flashinfer/fused_moe/cute_dsl/blackwell/moe_prepare.py`. Canonical and review
checkouts are untouched. Root owns remote deployment, screening and retention.

Each 128-thread CTA now assigns one independent row to each of its four warps.
Payload vectors remain 256 bits and source scale-factor loads remain 32 bits.
The lane-strided copy iterations derive from payload and SF widths. CTA count
is the smaller of padded row capacity divided by rows per CTA and the existing
hardware thread-capacity ceiling. No model, dtype, token threshold, new API flag,
shared-memory buffer or barrier is added.

The hypothesis is less CTA scheduling and idle-thread work for short rows and
invalid routed padding. Wider rows require more sequential iterations per warp;
the experiment can therefore lose bandwidth despite reduced CTA overhead.
Existing native whole-chain timing across V3, V41 and K3 determines retention.
Phase timing alone cannot establish a useful backend improvement.

The row partition is `block * 4 + warp + iteration * grid * 4`. This partitions
every padded SF row exactly once. Each warp partitions a payload row into
complete 32-byte vectors and an SF row into complete four-byte scale groups.
Payload is still copied only for valid routes. Invalid rows retain untouched
payload and receive zero SF, including the final required 128-row atom. Existing
64-bit offsets, route limits, mapping and canonical SF addressing are unchanged.

The PDL wait, release fence and first-warp trigger are unchanged. They execute
before any row loop, including zero local work; no row divergence can skip a
required CTA trigger. Source AST comparison verifies the same PDL block.

Static index enumeration covers 91 row/grid combinations, 512 payload widths and
256 SF widths, including loop tails and duplicate-store detection. This is a
source/index proof only: GPU compilation, numerical checks, performance and
sanitizers have not run for this candidate. No repository tests were added.

`manifest.json` records the exact base, source and patch hashes.
`candidate.patch` is the reviewable unstaged diff; `precommit.log` contains scoped
hook output. GPU validation and timing results must identify this exact source.
