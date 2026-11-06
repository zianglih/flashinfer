# FC2 producer-drain PDL boundary

New independent unstaged copy `flashinfer-pdl-producer-drain-review`, corrected-aab base. Prepare and FC1 early all-thread signal remain identical to adcc; only FC2's signal moves to the existing warp-zero producer-loop exit before A drain. Every lane in warp zero performs conditional nonfused PDL GPU-release then signals, including idle CTAs and both cluster members. No election, token cutoff, extra warp or CTA barrier. Final CTA join and all waits remain.

A/AB drains use independent producer.clone() state, because producer_tail advances phase/index. A now drains in warp zero first, then all eligible producer warps drain AB. FC1's signal remains early; the shared drain order is safe for either phase. No cache-policy changes; all math/layout/stages/roles are unchanged.

Bounded gate: fresh aab combined control and candidate FC2 N16/N256 compiler resources/PTX/SASS; existing native T1 exact-only plus true zero-route FC2 sentinel check; T4/N16 and T16384/N256 exact then ABA/BAB full-chain and phase timing. Same10warmups/100cold-L2 CUDA-graph CUPTI samples, actual source modules/caches, routing/prep included and input quantization excluded. No original upstream baseline, AUTO or TRTLLM rerun. All previous sources/archives stay frozen.

`probe_native.py` measured/capture/oracle function ASTs match the existing all-thread harness. `probe_zero.py` adds only an exact-only zero-count copy to the captured native FC2 kwargs; it cannot time. Sourcehashes are in manifest.json. Compile-only objects are regenerated and are not asserted to be timing-process binaries.

## Bounded outcome

All exact/zero-route gates passed. Fullchain control/candidate T4=1.054678× andT16384=0.994681× (all three pairs retained); no stableprefill gain claimed. Complete raw evidence: `evidence/pdl-producer-drain-aab93f`. GPU2idle awaiting parentdirection.
