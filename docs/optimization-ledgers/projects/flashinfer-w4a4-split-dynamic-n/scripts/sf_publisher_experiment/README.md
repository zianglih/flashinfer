# Separate TMEM SF publisher, retained98fd control

Actual independent source clone `flashinfer-sf-publisher-review`, one unstaged
core file. Initial static eligibility is oneCTA routeN16/32/64, both phases and
all existing dtypes. Other geometry retains its existing path. No arithmetic,
weight/preparation layout, publicAPI, per-token indexing or operand stages change.
The added warp is9 for overlapped320-thread kernels,5 for inline192-thread kernels.
Original producer0–3, epilogue4–7 and MMA8 (or inlineMMA4) stay assigned.

## Ownership and completion

The publisher waits existing A/AB full stages, acquires one of two independent
TMEM SF slots, then issues unchanged SFA/SFB S2T copies. It publishes completion
with tcgen05.commit. The MMA warp waits full completion and executes
`tcgen05.fence::after_thread_sync` before using those scales. After the last MMA
using the slot, another tcgen05.commit releases its empty barrier. The publisher
waits that completion and fences before overwriting. All roles advance the
same persistent tile/K sequence, with SF and operand ring states independent.
Original A/AB releases remain after MMA, so shared SF cannot be overwritten
before its copy completes. Existing terminal CTA barrier includes the new warp.

The two-slot ring reuses currently inactive oneCTA relay barrier storage; its
full and empty expected arrival counts are1. It cannot share that storage with
a later separately staged B-payload pipeline. Each SF slot consumes
sf_cols+sfb_cols. For NV K512/SF16/N16, accumulators occupy[0,64), SFslots
[64,128)/[128,192); allocation rounds to256 columns. SF32/mixed use the same
layout-derived formula. All SF regions remain disjoint from accumulator windows.

## Specification boundary

CUDA13.2.2 PTX§9.7.16.6.4.3 has a broad different-thread pipelined example:
https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-memory-consistency-model
The newer PTX9.4§9.7.18.6.2 explicitly treats different-warps as non-pipelined,
and§6.4.3 limits that example to threads in one warp:
https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-memory-consistency-model
Therefore this implementation uses actual CP completion before crossing warps,
not only an ordinary arrival and code-motion fence. The existing
PipelineUmmaAsync full side emits commit; its empty barrier is recast to
TCGen05Mma solely for the MMA completion arrival. No barrier is reinitialized.

Published TRT CopySfA/B rings in scripts/trtllm_gen_decode_audit/sources/src/
are architectural prior art, not binary/source identity for currentTRT cubins.
This differs from the closed442 synchronous register-SF global loader: global
SF transfers and shared layout remain unchanged; only S2T publication moves.

## Bounded gate

ReplacementC1 `fi-w4a4-narrow-1025`,GPU3 B200-92. Use new adjacent controls,
not old-node medians. Source `scripts/recovery442/env_candidate.sh`, private
CuTe cache; initial seven actual-source paired NV cases coverK64/384/1216,
per-token outputs, live17/33, repeated persistent work, zero routes. Then native
bench_moe_deepseek fixedN16, T32/128, ABA/BAB fullchain+FC1+FC2,10warmup100
cold-L2 CUDAgraphCUPTI samples, exact bytes before/after each arm. All output
allocations/captured intermediates are released before fullchain graph timing.
Broader correctness/sanitizers and primary AUTO remain deferred until a gain.

## Initial result: reject

Seven paired FC1 cases passed. Both native points passed exact FC1, FC2 and final
output checks before/after timing. All36 timing arms retain100samples each.
Full-chain control/publisher geomean ratios are0.992344 atT32 and0.991810 atT128
(0.77%/0.83%slower). FC1 ratios0.992924/0.999285; FC2 0.992211/0.991837.
This version is not retained. Raw archive:
`evidence/sf-publisher-98fd/raw.tar.gz`, SHA256
`efd0e1839dc23ac6e66822f7812ce136771778b751c0f306978aabaa0e719b64`.
No broader dtype/geometry tests or sanitizer work follows this negative gate.
