# High-impact followups for the initial W4A16 MegaMoE

Read-only audit, 2026-09-07. The parent reports CUDA-event graph measurements
confirming the initial device slowdown, including approximately 4.3 ms once the
global batch activates nearly all experts. This document identifies source
mechanisms and experiment boundaries; it does not attribute measured time to a
mechanism without the pending profiler evidence.

All source paths below are relative to `flashinfer/`. No active source edits or
GPU operations were made for this audit.

## 1. Empty experts are skipped, but active experts execute a full M256

`flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:993-1024`
reads each expert's actual received count and creates
`ceil(actual_count / cluster_tile_m)` token blocks. A zero-count expert contributes
zero FC1 and FC2 tiles. The observed behavior is not caused by computing empty
experts merely because `static_expert_shape` is enabled.

However, the active kernel fixes token M to 256 and feature N to 256:
`.../shim/w4a16/frontend.py:34-36,69-75`. The scheduler clips valid token counts
for each CTA (`fc1_fc2_fuse_sched.py:1210-1252`), but the MMA loop unconditionally
issues the same tiled MMA for every K stage of a valid task
(`.../shim/w4a16/kernel.py:1025-1070`). It does not reduce MMA M according to the
valid token count.

For H7168/I2048/E256/EP8, once all 32 local experts are active and each receives
at most 256 routes, every rank executes the following fixed work:

| Quantity | Per rank |
| --- | ---: |
| FC1 feature tiles per expert | 16 |
| FC2 feature tiles per expert | 28 |
| Cluster tasks | 1,408 |
| BF16 MMA FLOPs, counting multiply and add separately | 721,554,505,728 |
| Packed weight payload read | 704,643,072 bytes |
| E4M3 scale payload read | 88,080,384 bytes |
| Decoded BF16 shared stores | 2,818,572,288 bytes |
| Logical BF16 activation TMA payload across feature tiles | 2,818,572,288 bytes |

These byte counts describe logical payload and repeated tile processing, not
measured DRAM traffic. Activations and scales can hit cache. The weight B
partition spans half the feature rows on each of the two CTAs, so the table does
not double-count a full weight tile per CTA.

The fixed active-expert work explains why a plateau can extend from global128
through global4096: the average received routes per expert rise from 4 to128,
but remain inside the same M256 tile. It does not by itself explain why each
tile is slow. Relative to a route8 swapped-operand GEMM, M256 may issue 32 times
as much token-axis arithmetic, so producer instruction fixes alone do not remove
the structural padding cost.

Do not skip a CTA solely because its local valid-token count is zero. CTA1 also
provides the second half of B feature rows for the two-CTA UMMA; those weights
are required for valid output rows on CTA0. Its pipeline arrivals and FC1
completion increments also remain required.

## 2. A bounded one-CTA M128/N256/K64 tactic

This is the next incremental geometry candidate, following the producer profile
and vectorized-store experiment. It preserves token-major BF16 computation and
the current packed-weight ABI.

**Expected work change:** below 128 received routes per active expert, it halves
the issued M dimension and halves padded activation-TMA payload. A one-CTA B
partition holds 256 feature rows instead of128, so each producer thread decodes
eight blocks rather than four per K64 stage. There are twice as many available
persistent clusters, but each work tile uses one CTA. Total weight/decode bytes
per expert token tile remain the same. This can be unfavorable at global4096,
where experts receiving more than128 routes require a second tile and reread
weights; select the tactic from measured small/large-batch results.

**Current blocker:** the vendored BF16 base rejects any cluster other than `(2,1)`
in `.../src/moe_bf16_glu/kernel_bf16_glu_fc12.py:228-243`. This is a validated
geometry restriction, not an instruction-set inability. Supporting the candidate
requires an authored W4A16 override of that validator plus a narrow host whitelist
for `(M,N,K)=(128,256,64)`, cluster `(1,1,1)`, `use_2cta_instrs=False`. Keep vendor
files unchanged and retain the existing two-CTA default. Normalize geometry
tuples when supplied through JSON benchmark knobs.

Source checks that make the candidate bounded, while not proving it correct:

- Per-CTA M remains128, satisfying the epilogue's current row layout. BF16
  `_create_tiled_mma` chooses the CTA group from `use_2cta_instrs`.
- `.../src/moe_bf16_glu/megamoe_kernel_bf16.py:217-220` derives
  `cluster_tile_tokens` from MMA M. Pool task capacities and readiness counters
  therefore use128 with the candidate. Token padding remains128.
- `.../src/moe_mxfp8_glu/epilogue_mxfp8.py:187-190` derives atom participation and
  per-CTA M from `use_2cta_instrs`. The W4A16 kernel's FC1 completion threshold,
  B producer count, accumulator consumer count, and TMEM allocation similarly
  use the atom count (`kernel.py:555-574,630-668,742-749`). They must all compile
  to one-CTA values; no hardcoded two-CTA count should be introduced.
- Activation TMA selection and multicast predicates already branch on cluster
  geometry and `use_2cta_instrs` (`kernel.py:370-371,778-805`). The single-CTA
  path has no multicast mask.
- `.../src/src/token_comm.py:549-567` derives a bijective grid CTA id from cluster
  dimensions. The frontend doubles `max_active_clusters` for a one-CTA cluster,
  preserving the total resident CTA count and dispatch/tail partition.

Required gates: compilation/layout audit, EP1 and EP2 ring-wrap tests, a skewed
expert crossing128 routes, empty ranks, graph replay, and DSV3 per-route FC2
numerics. Test this first with the existing warp count and K64, preferably after
the scalar-store bottleneck is removed. A simultaneous register/stage redesign
would make failures and timing changes harder to attribute.

## 3. Existing scheduling knobs can test repeated phase-tail waits

The default `group_hint` is the number of persistent clusters (about74 for a
148-SM two-CTA launch). The scheduler accumulates complete experts until FC1 tile
count crosses that hint, then schedules FC2 for that group
(`fc1_fc2_fuse_sched.py:1103-1150`). Five active DSV3 experts produce80 FC1 tasks
and140 FC2 tasks. Under static stride74 (`:842-854`), many clusters can reach
FC2 while a few clusters still execute their second FC1 task, causing repeated
FC2-readiness waits at group boundaries.

After the frozen baseline, compare the already-supported `group_hint=512`
(32 experts x16 FC1 feature tiles) with the default, and compare static versus
atomic scheduling. An all-expert group reduces repeated partial-wave FC1 tails
but increases the time before FC2 and may affect intermediate/cache locality.
This is a hypothesis to discriminate with FC2 readiness-wait ranges, not an
explanation for the full twentyfold gap. No source patch is required.

## 4. K/N alternatives and their resource costs

The host currently rejects all but K64/N256. The BF16 base accepts K multiples
of the MMA instruction K and N in64/128/256. Narrowly exposing K128 and N128
therefore has less structural scope than reducing token M below128.

Using the existing stage fitter, current DSV3 BF16 epilogue staging, all256
expert-count scratch entries, and 232,448-byte SMEM capacity gives these static
estimates. Verify the actual compile log; they are not measured allocations.

| M/N/K and CTA group | A bytes/stage | B bytes/stage | A/B stages |
| --- | ---: | ---: | --- |
| 256/256/64, two CTA | 16,384 | 16,384 | 4 /4 |
| 256/256/128, two CTA | 32,768 | 32,768 | 2 /2 |
| 256/256/256, two CTA | 65,536 | 65,536 | 1 /1 |
| 128/256/64, one CTA | 16,384 | 32,768 | 2 /3 |
| 256/128/64, two CTA | 16,384 | 8,192 | 5 /6 |

K128 halves the number of per-task pipeline transactions, but also halves the
pipeline depth. K256 reduces it to a single A/B stage, so it should not be
assumed superior based on the earlier local W4A16 K256 kernel, whose transformed
weight storage is different. The full-decode-before-acquire candidate also
scales its live BF16 payload with K; do not combine these changes initially.

N128 doubles feature-task count and activation rereads, but can fill more SMs
for a single active expert and increases available stage depth. It is a plausible
tiny-batch tactic, not a universal throughput improvement. Start with N256 for
the all-expert plateau and compare N128 only where insufficient task parallelism
is visible.

## 5. If profiles still show a weight-producer bottleneck

The prepared vector-store, static-metadata, raw-preload, and full-predecode
patches are bounded probes. A larger staged producer should follow only after
those profiles:

1. Use warp6 for a coalesced packed-weight TMA load; move four decode warps to
   the complete warpgroup12-15. This produces a natural16-warp CTA but requires
   updating scheduler, communication, and tail participation and checking the
   register budget. Retain a separate raw-input readiness/release pipeline and
   the existing decoded-B-to-UMMA pipeline.
2. Decode from shared packed bytes into the correct BF16 B layout using the
   existing exact x16 helper, with vector shared stores. Do not materialize a
   whole expert weight matrix in BF16.
3. Treat E4M3 staging separately. At K64 each row contains only four scale
   bytes; at K128 it contains eight. A straightforward row-major TMA descriptor
   requires a sufficiently wide inner transfer, so copying the local kernel's
   scale TMA descriptor is not valid for the current linear scale ABI. Options
   include SIMT/cp.async scale staging, loading/reusing a wider K-span, or an
   explicitly coordinated preprocessing change to a tiled scale layout. Each
   has a different lifetime/layout contract.
4. Budget raw input stages explicitly. The current decoded BF16 operands already
   consume most shared memory. Adding an input pipeline without shrinking or
   refitting A/B stages can overrun the budget; K256 in particular has little
   room for both raw staging and a useful decoded pipeline.

Moving weights to operand A and using TMEM for transformed weights would recover
the mature local W4A16 small-route tactics. It also requires a swapped epilogue,
activation TMA mapping, scheduler coordinates, and communication tile contract.
It is the larger fallback architecture, deliberately deferred while the
incremental producer and one-CTA experiments are evaluated.
