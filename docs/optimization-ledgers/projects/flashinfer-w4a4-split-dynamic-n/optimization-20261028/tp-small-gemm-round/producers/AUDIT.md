# Small TP producer audit

Current source: `1054743780dda2919c1424124c1e3258248b8c19`.

The retained partial-K change already skips unused MMA atoms. Operand TMA still publishes a complete stage, including hardware zero-fill in the reduction tail. The shared full/empty ring has one byte announcer and separate independent weight/activation issuers. Its producer states span routing tiles; reducing ring depth to one tile's K count could remove useful next-tile overlap and is not a correctness-neutral simplification.

The existing TP profiles implicate a mix of work: K3 TP MXFP4x8 prepare and FC2 remained large after compact FC2. The stage interval overlap does not identify an operand barrier as redundant. Prior full-SFB multicast and prepare ownership experiments were rejected; this round does not repeat them.

## Candidate: normalize hardware rank to its compile-time group

The constructor permits logical channel tiles 128, 256, 512, yielding physical MMA M128 or M256 and a one/two-CTA group. The launch cluster is exactly `(cta_group_size, 1, 1)`. Thus `cluster_rank & (cta_group_size - 1)` equals the hardware rank for every admitted launch, and is identically zero for one CTA. This is a launch-geometry identity, with no model/dtype policy or new branch/tactic.

Current generated one-CTA config0 FC2 still has two `S2UR ..., SR_CgaCtaId` sites (one may belong to SDK internals). The kernel's rank reaches activation offset computation, metadata consumer quorum, MMA leadership and epilogue channel offsets. Expressing the known range may erase more than the rank read, including activation `valid` arithmetic whose result is multiplied by zero for one CTA. The bounded paired gate will establish the actual codegen effect, exact output and unchanged lifetime/resource geometry. No performance claim yet.

Frozen source/patch are in `source.json` and `candidate.patch`; scoped pre-commit passed. The current independent review copy is `flashinfer-tp-producer-review`, with only this kernel file unstaged.

## Qualification

Reuse the existing source-paired public-wrapper gate with four format cases: W4A4 one CTA, per-token W4A4 logical M512/two CTA, MXFP8 logical M512/two CTA, and MXFP4x8 two CTA. Each runs static/CLC, PDL off/on, live/empty/reactivated routing and cross-source storage-byte equality. It captures both FC1/FC2 PTX/cubin/SASS/resources. The clean control is the shared independently verified 105474 source; each role uses a private compiler CWD/workspace and retained native cache links. No sanitizer or timing is launched by this gate.

The source comparison also checks the unchanged launch cluster and group extent. Gate results are required before any performance screen.
