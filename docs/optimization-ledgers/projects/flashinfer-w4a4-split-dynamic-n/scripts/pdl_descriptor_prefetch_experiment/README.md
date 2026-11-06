# Immutable TMA descriptor prefetch

The independent unstaged source copy is
`flashinfer-pdl-descriptor-prefetch-review`. It contains the retained24c bytes
plus eight kernel startup lines, represented as measured parent853 plus full
patch `50d44ac4085ac158b5d63767707054d6948895bc4797acccdba9f13ec66421e3`.
The source receipt pins all83 files. Production is unchanged.

Warp0 prefetches A/SFA/B tensor maps before pipeline setup and conditionally
prefetches SFB when that path uses TMA. These descriptors are immutable launch
parameters; the instructions do not read the dependent activation payload.
No stage counts, data ordering, scheduling, cache eviction hints or numerical
operations change. This mirrors the descriptor startup used by W4A16.

`build.py` creates the focused delta and runs scoped pre-commit. Existing
public-chain and codegen probes are copied byte-for-byte, then run by
`deploy_gate.py` and `deploy_codegen.py` on GPU3. They pass324 and27 exact
changing-data replays, respectively. The named narrow specialization emits
three descriptor prefetches before its dependency wait, verified in
`evidence/pdl-descriptor-prefetch-r1/descriptor-order-proof.json`. Wide TMA-SFB
is covered by the source branch and the N128 replay gate, not that named PTX.

`prepare_fixed.py` reuses the SFA experiment's immutable observer and fixed
N16 cache preparation. `launch_fixed.py` transfers the generated launcher in
hash-checked chunks. Both models run sequentially on GPU3, NV then MX, each
C1-A1-A2-C2 over4/32/128/512 tokens with native10/100 cold-L2 CUPTI timing.
No overlapping benchmark processes share that GPU. Raw artifacts are fetched
and audited with the existing `scripts/pdl_sfa_stream_experiment/{fetch_fixed,
summarize_fixed}.py --prefix pdl-descriptor-prefetch-r1-fixed` helpers.

Initial V41 fixed geomeans are NV1.000945, MX81.000377, mixed1.000874. T4
improves by0.20–0.27%; larger points are mostly within about0.1% of neutral.
This does not establish native AUTO retention. The V3 screen and any combined
candidate sweep must resolve whether the small benefit is worth retaining.
