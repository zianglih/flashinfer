# Split blockscaled MoE PDL startup audit

Source baseline: retained `24c48b9fd5d7c38fdcea213376602f97635c4ef9`.
Scope is the Blackwell split CuTe DSL chain, with the same V3 EP8 and
V41-Flash EP4 benchmark contract. This document records the audit and isolated
experiments; it is not a claim that every candidate is retained.

## Dependency boundaries

| Handoff / work | Dependency | Current behavior / opportunity |
|---|---|---|
| Routing → routed-input preparation | Route count, limits and mapping must be complete | `PrepareRouted.kernel` waits before reading metadata. |
| Preparation → FC1 initialization | Barrier initialization, TMEM allocation, tensor views and immutable descriptors do not read prepared payload | Common GEMM initialization already precedes the wait. Explicit descriptor prefetch is absent in retained24c; isolated experiment adds it. |
| Preparation → FC1 weights and SFA | Weights are independent of prepared activations, but expert selection uses routing metadata | Preparation currently triggers immediately after its wait without an explicit GPU release. Add an explicit routing-publication contract before permitting early FC1 metadata/weight reads. |
| FC1 → FC2 weights and SFA | Expert routing is complete; FC1 activations/SFB are still being produced | Retained24c publishes routing before the first FC1 trigger and fills `min(actual stages, static K tiles)` A/SFA stages before FC2 waits. No added buffers. |
| FC1 → FC2 B/SFB | FC1 must finish the payload/scale writes | Every B TMA and SFB TMA/cp.async stays after the dependency wait. Early descriptor prefetch does not access this data. |
| FC2 → combine | Metadata may be ready earlier; expanded output data requires FC2 completion | Retain the existing finalizer dependency wait before output loads. Cache hints do not supply memory ordering. |

The routing-publication contract uses a GPU release followed by the first PDL
trigger in the same memory synchronization domain. One designated warp must
perform both; a different warp must not trigger before that release. Default
standalone callers cannot assume arbitrary preceding producers publish routing.
Per-token quantization and localized/Rubin paths retain their existing contracts
unless a separate explicit producer pairing is implemented and verified.

## Existing overlap and remaining serialization

The common kernel constructs operand/accumulator pipelines, optional CLC
pipelines, SMEM tensors, TMEM allocation and static TMA partitions before its
global dependency wait. Host-created tensor maps are immutable launch
parameters. They can be prefetched without reading the activation tensor.
`moe_w4a16_kernel.py` already prefetches its descriptors before pipeline setup.

The common kernel then waits all threads. This holds back the CLC scheduler,
MMA-side setup and epilogue metadata work even when routing was explicitly
published. W4A16 instead runs its scheduler before the activation-producer wait.
For blockscaled kernels, the small-tile SFB cp.async path uses all four producer
warps: any role-specific wait must cover all 128 of those threads, not only the
warp issuing B TMA. Existing operand full barriers protect MMA; accumulator
barriers protect epilogue consumption. A separate direct compile-time behavior
knob can select this ordering once the metadata-publication contract is known.
The startup release/trigger in warp0 must still follow that warp's wait.

Both `PipelineTmaUmma.create` and `PipelineUmmaAsync.create` currently call
the local `custom_pipeline.pipeline_init_wait`, which emits an mbarrier
initialization fence, not the CTA/cluster wait emitted by the similarly named
CuTe SDK helper. Optional cp.async/CLC construction partly defers initialization
synchronization. A future isolated experiment could consolidate these fences
after all pipeline objects are initialized, preserving the existing two-CTA
arrival/wait and TMEM all-thread rendezvous. It must not introduce an additional
CTA barrier under the guise of consolidation. First inspect emitted code to
determine whether the compiler already merges the fences.

## FC1 initial work and scheduler correctness

The initial CLC work is known from launch coordinates. With the existing
identity raster/swizzle configuration, its flattened index is
`blockY * total_m_tiles + blockX / cta_group_size`; static scheduling instead
starts at normalized blockX. Early FC1 A/SFA prefetch can use that initial work
without consuming the scheduler queue or changing cancellation ownership.

An initial padded route must prefetch nothing. If CLC later cancels a live tile,
that different tile must acquire/load all stages normally. Initial stage reuse
must compare against the actual initial flattened tile, not just blockX.
Focused gates must cover padded initial work, zero local routes, cancellation
and multiple persistent work tiles. The scheduler itself can be moved ahead by
the separate role-specific wait experiment, without combining two mechanisms
in the first timing comparison.

## Issuer ownership and cache lifetime

Retained24c uses warp0 for A, SFA and B TMA; all four producer warps participate
in the small-tile SFB cp.async path. The full prefetch window makes concurrent
A and SFA issuing worth revisiting. The isolated two-issuer proposal reuses
warp1 for SFA and keeps warp0 for A/B. A two-arrival full barrier and separately
announced byte subtotals avoid a new per-stage rendezvous. Warp0 must include
the deferred B/SFB bytes, so early A/SFA completion cannot release MMA before
the dependency-protected activation load. Each issuer waits the same empty
phase and announces its subtotal exactly once per stage. Consumers, stage
count, storage and warp count remain unchanged.

The cache experiment streams weight scales at the same FIRST priority as
their payload, then independently tests LAST on FC2 activation TMA reads.
That LAST hint begins at FC2's first read; it does not protect FC1's stores
before that read and does not demote dead data. SFB remains normal. Broad
blanket LAST policies and the previously rejected output-store/combine policy
are not silently reintroduced. Native AUTO comparisons select retention.

## Experiment records

- Full-capacity A/SFA prefetch: retained24c; binding in
  `evidence/pdl-weight-prefetch-retained/receipt.json`.
- SFA-FIRST: both-model native AUTO decode and overall geomeans improve;
  `evidence/pdl-sfa-native-{v3,v41}-a2/paired.json`. Wide, unmodified prefill
  tactics show timing variation; report those observations without assigning
  a cache-policy cause.
- SFA-FIRST + B-LAST: retained as8b74 after all24 affected fixed-screen
  points and all six native AUTO decode groups improve in both repeats.
  Source binding: `evidence/pdl-cache-tier-retained/receipt.json`.
  Inactive M256/N256 two-CTA FC2 PTX/cubin/SASS/resources are byte-identical
  for all three formats: `evidence/pdl-inactive-wide-r1/comparison.json`.
- Full first-tile metadata reuse: passed gates but added three first-tile
  branches for mostly noisy gains; unretained. A much smaller live-count-only
  hoist is being measured.
- Descriptor prefetch: `flashinfer-pdl-descriptor-prefetch-review`, patch
  `50d44ac4085ac158b5d63767707054d6948895bc4797acccdba9f13ec66421e3`.
  Existing real-chain gate passes 324 exact replays; codegen gate passes 27.
  Named PTX places all three narrow-tile descriptor prefetches before the wait.
  Wide TMA-SFB also prefetches its descriptor via a compile-time branch.
  Fixed both-model full-chain screen completed on GPU3; tiny gains and
  repeatable small V3 MXFP8 losses leave this candidate unretained.
- Independent A/SFA issuer warps:135 exact replays and expected-byte proof
  pass, but V41 MXFP8/mixed fixed means regress0.65%/0.48%. Rejected;
  `evidence/pdl-weight-scale-producer-r1-fixed/summary-v41.json`.
- FC1 prefetch:216 exact chain replays,9 preparation-codegen replays and36
  corrected per-token replays pass. T4 improves across both models/formats;
  larger decode losses make FC1-only unretained. The initial per-token
  failure came from an observer dropping existing compile options; it is
  preserved separately, not attributed to production code. A separate
  `wait_for_activation_in_producers` candidate keeps all128 activation
  producer lanes waiting while scheduler and consumer setup can advance.
  That combined FC1 candidate also remains unretained: V41 mixed T32/128/512
  regress in both repeats. A fresh two-file FC2-only candidate on8b74 is
  also unretained after162 exact output checks and18 metadata follow-up
  replays. Its fixed paired means are V3 NV/MX8/mixed
  1.000149/1.000753/1.000886 and V41 1.001265/1.000028/0.999828.
  Only11/24 points improve in both repeats; V3 NV T512 and V41 mixed T32
  lose0.52% and0.33% respectively in both repeats. The added behavior does
  not earn its complexity; no native expansion is run. See
  `evidence/pdl-fc2-producer-wait-r1-fixed/summary.json`.
- Initialization fences: existing codegen does not merge all custom fences.
  The reviewed two-file `flashinfer-pipeline-fence-review` candidate defers
  the two custom fences and emits one after all initialization. It preserves
  the SDK TMEM fence, cluster sync and named barrier.45 exact replay checks
  and27 matched codegen/resource comparisons pass. The fixed both-model
  screen is neutral/slightly negative (five of six format/model means below1),
  so it remains unretained; `evidence/pipeline-fence-r1/final-screen-note.md`.
  `evidence/pipeline-fence-r1/design-review.md` records the ordering proof.

The benchmark's old MX component assembly is being replaced with the public
function/wrapper, using `quant_mode="w8a8"` for homogeneous MXFP8. Pipeline
policy belongs in the library. Frozen experiment receipts remain unchanged;
final timings require explicit input/tactic/launch equivalence and fresh
measurements through the public API.

All experimental sources remain unstaged in separate project-local checkouts.
Small gains can be retained when the full two-model sweep shows no credible
regression. Added synchronization or control flow must earn its cost; source
motion alone is not evidence of performance improvement.

## API cleanup retained: 2b7fb105

The public FC2 prefetch switch and FC1 routing-publication switch are removed. Blackwell FC1 now publishes routing whenever PDL is enabled; FC2 privately derives the existing prefetch admission from PDL, static one-CTA unfused output and absence of per-token scales. Custom PDL producers must provide ready metadata before early launch, or release-publish it before their first same-domain signal. Per-token conversion still excludes FC2 prefetch.

The shared launcher accepts explicit normal/evict_first/evict_last strings, rejects unknown values, and resolves the existing narrow-pipeline eligibility and hardware hints internally. Kernel-core bytes and effective FC2 hints are unchanged. FC1 publication changes37of156 prior native choices, so the new performance campaign measures clean2b7 rather than relabeling adf timings.

The existing epilogue and public beta propagation already supported MX SiTU; only two guards and documentation needed updating. Existing tests now include both MX formats, gate-only and gate+up SiTU, and one/twoCTA. Integrated focused68 passed; the frozen85source files are identical to clean2b7. Evidence: evidence/api-cleanup-focused-r1, evidence/api-cleanup-retained, evidence/api-cleanup-retained-2b7. Experiment copy flashinfer-api-cleanup-review remains unstaged. New native campaign: evidence/api-cleanup-final-r1; archived original controls remain untouched.
