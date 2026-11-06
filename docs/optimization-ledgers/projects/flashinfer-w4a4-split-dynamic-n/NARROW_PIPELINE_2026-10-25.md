# Narrow allocation and operand pipeline experiments

User-requested follow-up to the TRTLLM comparison: try physical N16 allocation,
separate producer roles, and scale-factor publication outside the MMA hot path.
All candidates start at retained `98fd3566b5f945c100f48cddacf25deb2432cbc2` in
independent source copies with unstaged changes. Production and PR7290 remain
unchanged unless a candidate earns retention. No MegaMoE source changes.

## Independent candidates

| Candidate | Source copy | Initial distinction | Assigned GPU |
|---|---|---|---:|
| Physical N16 | `flashinfer-physical-n16-review` | Shrink B and accumulator/epilogue extent with four operand stages; distinct from rejected B16 plus five stages | 2 |
| Producer roles | `flashinfer-producer-roles-review` | Independent small-N weight A/SFA producer and completion ring, preserving activation/SF producer and MMA publication | 4 |
| SF publisher | `flashinfer-sf-publisher-review` | Separate shared-to-TMEM scale publication role and ring with explicit consumer lifetimes | 3 |

## Environment and protocol

The previous `fi-w4a4-pipeline-1025` devbox no longer exists. A replacement was
created using the managed `/usr/local/bin/h`. NVIDIA's live NGC catalog
and release matrix were checked on 2026-10-25; the latest CUDA13.2 PyTorch image
is still `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA13.2.1). Later listed releases
use CUDA13.3/13.4. The replacement is `fi-w4a4-narrow-1025`, C1,
namespace ziangli, eight B200 GPUs, bare, with size unspecified.

Sources: <https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-> and
<https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-09.html>.

Durable Weka sources and pinned dependencies survived and were verified before
timing. Existing results are preserved; old timings are not adjacent controls
in this new host/GPU/software epoch.

Initial screens use native `benchmarks/bench_moe_deepseek.py` inputs and captured
phase calls, per-tensor NVFP4, unfused CuTe finalize, H7168/I2048, top-k8,
256 total/32 local experts, simulated EP8/TP1. T32/T128 fixed N16 first;
10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per arm, adjacent ABA/BAB.
Record exact pre/post output bytes, source hashes, every sample and compiled
resources where useful. Preserve PDL. Full-chain results decide whether to
extend a phase improvement. Initial activation quantization is outside timing.

Reuse completed baseline, retained AUTO and native TRTLLM data. Fresh adjacent
controls are diagnostic measurements of the new candidates, not reruns of the
original campaign. Any promoted candidate must preserve affected dtype and
per-token behavior and use the existing full token grid; tokens1/2 are measured
but excluded from retention. A new environment cannot inherit a controlled
TRTLLM speedup claim from a different GPU epoch. Defer broad numerical and
sanitizer validation until a promising implementation is retained for review.

The replacement is ready on B200-92 (previous primary measurements used
B200-83). All eight GPUs were idle when assigned. The existing Weka environment
and clean `profile-98fd` source survived; alias restoration did not edit source.
CUDA13.2.78, PyTorch2.12.0a0+5aff3928d8.nv26.05, CuTeDSL4.7.1,
CUPTI Python13.4.0 and driver580.178.04 were verified.
Receipt: `evidence/narrow-pipeline-environment/environment.json`.

The publisher uses explicit `tcgen05.commit` completion before cross-warp SF
consumption. PTX9.2's pipelined-different-thread example is broader than the
newer clarification restricting the no-completion pattern to the same warp;
the stronger cross-warp completion protocol avoids relying on that ambiguity.

## Results

### Physical N16: closed, unretained

True B/C N16, unchanged four operand stages, generated-FP4 FC1 only in this
bounded prototype. Seven paired exact cases passed, followed by native FC1/SF,
FC2 and final-output equality before/after every timing arm. Twelve full-chain
arms contain 1,200 raw samples. GPU2 only; no new TRTLLM comparison implied.

| Tokens | ABA: control / candidate / control (us) | BAB: candidate / control / candidate (us) | Control/candidate geomean |
|---:|---|---|---:|
| 32 | 105.8720 / 106.4005 / 105.9045 | 106.2730 / 106.1125 / 106.3050 | 0.996584x |
| 128 | 143.4085 / 142.6885 / 143.5530 | 142.7050 / 143.4405 / 142.6730 | 1.005456x |

Shared memory fell 197,504 to 181,120 B and registers 64 to 50. Hardware TMEM
allocation remained 128 columns and occupancy one CTA/SM. The narrow epilogue
eliminated the FP32 transpose but increased static SASS instructions from 1,144
to 1,224, including 15 shuffles. The mixed sub-percent full-chain result does
not justify standalone retention or expanding its dtype gate. Preserve it for
possible composition with a separately useful pipeline change.

Evidence: `scripts/physical_n16_experiment/README.md`, source manifest, archive
receipt and all samples. Actual source remains two unstaged files in
`flashinfer-physical-n16-review`; production stays clean at `98fd3566b5`.

### Initial producer and publication variants: unretained

All entries below passed focused byte checks. Ratios compare geometric means of
three adjacent control/candidate arm medians; greater than one favors candidate.
Each variant has 36 full/FC1/FC2 arms, 100 samples per arm. Isolated phases are
diagnostic and are not additive. No broader numerical/sanitizer sweep followed
these negative gates.

| Variant | T32 full chain | T128 full chain | Interpretation |
|---|---:|---:|---|
| Dedicated weight warp, separate A/B rings | 0.981853x | 0.983633x | Added issue role and completion overhead did not pay back |
| Same producer roles, shared payload empty barrier | 0.982274x | 0.980920x | Removing one release did not explain/recover the loss |
| Separate SF publisher, canonical SFB | 0.992344x | 0.991810x | Correct publication, but joint payload readiness serializes it |
| Compact SFB broadcast + true C16 + publisher | 0.994396x | 0.995735x | Footprint/codegen improved; readiness dependency remained |

Producer evidence: `scripts/producer_roles_experiment/RESULTS.md` and archives
under `evidence/producer-roles-98fd-{initial,shared-empty}`. Root independently
recomputed all 7,200 sample medians and checked exact-output/input flags.
Publisher evidence: `scripts/sf_publisher_experiment/README.md` and
`scripts/compact_sf_broadcast_experiment/README.md`, with complete raw archives.

The compact broadcast packs pairs of K64 scale words into TMEM columns 0/2
within each 32x128b warpx4 atom. Four copies produce 16 SFB columns. True C16
ping-pong uses 32 columns, and two (32 SFA + 16 SFB) slots then fit 128 total.
Actual FC1 shared storage is 172,928 B, registers 46, local bytes zero, still
one CTA/SM. It emits 12 SF copies per K stage versus 16. This is a 2,048-byte
SFB source stage, not the 512-byte four-warp STTM layout in published TRT.
The four-warp STTM draft is preserved but unmeasured.

### Concurrent issue and independent SF readiness

The user explicitly reaffirmed concurrent warp issue as a preferred design
direction. The initial regressions do not reject that direction. Published TRT
N16 uses separate A, B, SFA and SFB loader roles, separate publication pipelines,
and role-specific register budgets. Its SF shared storage is released after
publication, independently of payload/MMA lifetime. Importing its full warp
topology or register caps without a measured mechanism is not justified.

A bounded NCU comparison of the frozen shared-empty FC2 variant at T128 found
essentially identical DRAM reads (248.301 versus 248.303 MB), but 11.64% more
executed warp instructions and 44.064 versus 44.960 us replay duration. The
MIO-throttle per-issued-instruction ratio fell 0.25 to 0.05; the denominator
also changed, so this alone is not causal evidence. The interpretation is to
reduce orchestration work while preserving concurrent issue. Report, source,
commands and raw metrics: `scripts/narrow_pipeline_profile/README.md` and
`evidence/narrow-pipeline-profile`.

The next isolated source assigns existing producer warps 0/1/2 to A/SFA/B,
keeping 288 threads. Three atomic arrival-plus-byte-expectations feed one full
barrier; each issuer announces only its own bytes before its transfer. A single
post-MMA empty release remains. Installed CuTe4.7.1 API semantics were checked.
Its native screen is exact and neutral: full-chain ratios 0.996535x at T32 and
0.999591x at T128; all 3,600 samples and source/input/output hashes verified.
It remains unretained as a standalone change. Threads and registers match the
control. Source: `flashinfer-producer-distributed-tma-review`; evidence:
`scripts/producer_roles_experiment/distributed_tma/RESULTS.md` and
`evidence/producer-roles-98fd-distributed-tma`.

The coordinated follow-up combines concurrent issue with compact SF. The first
publisher variants waited the joint A+SFA+B full barrier, so large payload
completion preceded cross-warp SF-copy completion on the MMA critical path.
The new design separates SFA readiness: payload A/B share one full barrier,
SFA has its own, SFB retains cp.async. Publisher waits scales only, while MMA
waits payload plus published scales. SF shared storage may release on copy
completion; payload and TMEM SF slots remain protected through MMA completion.
This coordinated source (`flashinfer-sf-readiness-review`, core `0f570a27…`)
passed seven paired exact cases and all 3,600 native samples, but remained
unretained: 0.994690x at T32 and 0.994124x at T128. It allocates 173,056 B SMEM,
320 threads, 50 registers, 128 TMEM columns, with no local memory. Complete
evidence is in `scripts/sf_readiness_experiment` and `evidence/sf-readiness-98fd`.

NCU T128 FC1 explains why fewer memory-copy instructions were insufficient:
executed warp instructions rose 6,575,874 to 7,639,172 (+16.17%), and branches
304,195 to 643,155. SF-copy instructions fell 215,040 to 161,280, global-to-shared
copies 430,080 to 215,040, and TMEM loads 26,880 to 7,680. TMA loads and MMA
counts were unchanged, as was approximately 497.3 MB of DRAM traffic. Replay
time was 77.472 versus 79.296 us; this is diagnostic, not primary timing.
These metrics motivate reducing orchestration, without assigning the extra
branches to a particular role absent PC-level evidence. Source guards and
initialized output/SF bytes passed. Report: `scripts/sf_readiness_profile/README.md`.

### Stage depth and warp reuse

A capacity-derived five-stage version fits 216,064 B SMEM and retains two TMEM
SF slots. Its source stages and all tails passed focused exact checks, but the
T32/T128 full-chain ratios against the **four-stage readiness control** were
0.989312x and 0.996202x. Do not multiply these across GPU epochs into a claimed
production speedup. The negative gate did not warrant a direct production
comparison. Source/evidence: `flashinfer-sf-readiness-stage5-review`,
`scripts/sf_readiness_stage5_experiment/README.md` and
`evidence/sf-readiness-stage5`.

The next bounded refinement reuses warp3 for compact SFB loading and SF
publication, returning to 288 threads. Warps0/1/2 issue A/SFA/B independently;
only warps1/3 wait the shared SF-source empty barrier. SFB has 32 cp.async
participants, initializes immutable odd-word padding once with a proxy fence
and warp synchronization, and rewrites/zero-fills even words each iteration.
This removes the extra publisher warp and the 128-thread SFB producer group.
Source `flashinfer-sf-warp-reuse-review` is frozen at core `2c4fee74…`. The first
core `0669a693…` failed compilation of the per-token fallback because a mixed
runtime/static branch still lowered a disabled publisher body. An explicit
inner static guard repaired it; the first source and failed logs are preserved.
Final smoke and timings used a fresh private cache and module identity.
Publication and source empty signals still use explicit completion. Four
operand stages and two TMEM SF slots stay fixed.

All seven saved-oracle cases and native pre/post byte checks passed. Full-chain
ratios were 0.987100x at T32 and 0.991679x at T128; FC1 ratios were 0.995391x
and 0.992238x. The candidate uses 173,056 B SMEM, 50 registers, zero local
bytes, 288 threads and 128 TMEM columns, still one CTA/SM. It is unretained.
Root independently recomputed all 3,600 sample medians and verified the archive
hash. Evidence: `scripts/sf_warp_reuse_experiment/README.md` and
`evidence/sf-warp-reuse-98fd`.

The final bounded follow-up is `flashinfer-sf-warp-localwait-review`, core
`7f0fdbc4…`. Warp3 commits and waits its own cp.async group on every lane,
performs the generic-to-async shared proxy fence, then synchronizes all lanes
before elected TCGEN CP publication. This replaces the producer-to-self
full-barrier handoff. Shared SF-source empty, SFA full, TMEM full/empty and
explicit TCGEN completion remain; four source stages, two SF slots and 288
threads are unchanged. The initial `dfcf99ba…` omitted the recurring proxy fence
and was preserved unmeasured. Independent review required the fence before any
GPU launch. The corrected source passed all seven saved-oracle cases and
native T32 phase/final exact checks. All 3,600 paired samples and pre/post byte
checks passed. Full-chain ratios were 0.988172x at T32 and 0.991785x at T128;
FC1 ratios were 0.997447x and 0.994682x. Resources remained 173,056 B SMEM,
50 registers, zero local bytes, 288 threads, 128 TMEM columns and one CTA/SM.
It is unretained. Root independently recomputed all sample medians and checked
the immutable archive hash. Evidence: `scripts/sf_warp_localwait_experiment` and
`evidence/sf-warp-localwait-98fd`.

Independent source/PC audit subsequently found a concrete remaining difference:
our N16 loader emits eight SFB cp.async/address/predicate sites per K512, while
published TRT N16 has four. Mapping `row = lane % 16`, `half = lane // 16`
halves per-lane copy sites without changing active words or bytes transferred.
Rows 16–31 remain zero and can be initialized once with the immutable odd words.
The full-word ownership/coverage proof is in
`scripts/compact_sfb_audit/loop_bookkeeping_receipt.json`. The isolated
`flashinfer-sf-warp-pairedrow-review` source (core `72ce0c11…`) screened this
mapping without combining a vectorized-startup change. It passed seven oracle
cases, native phase/final exact smoke, and all 36 timed arms / 3,600 samples.
Full-chain ratios were 0.987438x at T32 and 0.992111x at T128; FC1 ratios were
0.994272x and 0.995168x. Resources match localwait. It is unretained; no direct
comparison with the corrected aab kernel was warranted by the negative gate.
Root independently verified all medians, byte flags and archive SHA256
`2a0b1481dc4d3cccafce42ac3a63acc9a719de6e029d6955b725484a4ccb6667`.
Evidence: `scripts/sf_warp_pairedrow_experiment` and
`evidence/sf-warp-pairedrow-98fd`. SASS confirms eight-to-four LDGSTS sites,
but startup STS sites grow 34 to 50; total static instructions grow 1,583 to
1,591 excluding padding. No net executed-instruction reduction is claimed.
Independent CPU proof covers 5,904 persistent stage updates and 31,512 full-stage
byte comparisons; review manifest is
`scripts/compact_sfb_audit/pairedrow_review_manifest.json`.
This closes the bounded round with no retained
performance candidate. The other source-audited lead—hoisting runtime TMA-role
dispatch out of the persistent K loop—is left for a separate experiment.

The audit also corrected a static-SASS parser that omitted mixed-case TMEM
mnemonics. Warp3 has 1,135 control / 1,599 candidate instructions excluding
trailing padding; localwait has 1,135 / 1,583. Immutable raw archives are intact.
Some static growth is compiler loop unrolling, so these counts cannot explain
dynamic NCU growth by themselves. Exact epochs, PCs and counting rules:
`scripts/compact_sfb_audit/LOOP_BOOKKEEPING.md`.

### Proxy-ordering finding

PTX specifies ordinary non-bulk `cp.async` writes through the generic proxy and
TCGEN shared-memory reads through the async proxy. Completion plus warp/thread
synchronization does not replace the cross-proxy fence. See the official
[cp.async](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async)
and [TCGEN shared accesses](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-shared-memory-accesses)
sections. The warp3 prototype needs a recurring fence after its own group wait;
the startup fence only publishes the immutable odd padding.

Read-only audit found the same source-level gap in retained 98fd's one-CTA
non-TMA SFB path: it waits the cp.async mbarrier then issues TCGEN CP without a
proxy fence. Its two-CTA relay path already has that fence. The installed
CuTe4.7.1 wait chain and actual compiled control PTX contain no implicit proxy
fence; exact helper source/hashes are preserved in
`scripts/sf_readiness_profile/inherited-proxy-helper-source.json`.
This is a specification-based ordering finding, not an observed numerical
failure. Earlier byte checks do not establish that missing ordering is valid.
A separate minimal source copy, `flashinfer-sf-proxy-fence-review`, validated
the retained-kernel correction independently of the performance prototypes.
Its seven saved-oracle and 24 new paired format/PT/FC2 cases passed exactly,
as did all native pre/post byte checks across 3,600 samples. T32/T128 full-chain
cost was +0.675% / +0.579%, with unchanged compiled resources. Actual PTX proves
completion wait → proxy fence → TCGEN copy. Full data/commands are in
`scripts/sf_proxy_fence_experiment/README.md`; root independently verified the
archive hash, every sample median and output flags.

The exact four-line repair was committed and pushed as
`aab93f854054de834447bdd8985b8bbd653fb3c8`. Changed-file pre-commit passed.
The review copy stays unstaged. The PR body retains all original full-grid and
TRTLLM data explicitly attributed to 98fd, alongside this bounded correction
cost; no new full-grid or TRTLLM speedup is claimed for aab. Broad sanitizer
validation was not repeated for this correction. All performance prototypes
remain unretained and all running experiments keep their pinned 98fd controls.

Source identities, unstaged paths and project-local Git directories are recorded
by `scripts/narrow_pipeline_source_inventory.py` in
`evidence/narrow-pipeline-source-inventory.json`. No MegaMoE source was changed.
