# Split CuTe DSL core generality audit

Work is local and unstaged in `flashinfer-generality-review`, based on pushed `84f9a8e79ce2d5bf93243dfcc4b1fb117441f682`. This note records implementation and validation boundaries, not a performance-retention decision. Parent campaign notes: [GENERALITY_AUDIT_2026-10-25.md](GENERALITY_AUDIT_2026-10-25.md).

## Physical allocation and logical B transfer

The 32-column minimum allocation is required by the current TMEM transpose epilogue. It does not require copying 32 activation rows when the routed-token tile is 16. The copy view now composes the logical row extent into the unchanged physical B layout, retaining its K/stage strides and swizzle. TMA transactions and expected byte counts use the logical copy extent. MMA, TMEM, SF atoms, epilogue ownership and stage counts remain unchanged.

Actual CuTe 4.7.1 evidence: 252 layout policies and 26,155,008 addresses match the original physical layout exactly; 18 B-copy-only kernels compile for group1 and existing wide group2. The combined copy source passed 68 existing tests and 96 public-chain changing-data/route replays against clean84f9. See [copy source](evidence/generality-copy-r1/source.json), [prefix proof](evidence/generality-core-r1/prove-b-prefix-r3/prefix-address-proof.json), and [PDL gate](evidence/generality-pdl-r1/gate-summary.json).

## General PDL prefetch

The old one-CTA/static/scatter-only prefetch admission was an implementation restriction. Startup now derives the first tile using the actual static or CLC initial-work mapping, then primes A and SFA through the existing group-aware operand pipeline. The regular loop skips only the primed slots of that exact first tile. Padded CLC initial work primes nothing; later cancelled live work acquires normally. Both CTAs retain the existing group-scaled TMA completion accounting. B and SFB loads remain after the dependency wait.

FC1 prepare and the intermediate per-token quantizer explicitly republish ready routing metadata before their first dependent-grid signal. Both host GEMM phases request prefetch when PDL is enabled. All no-work waits and teardown rendezvous remain.

Frozen PDL source `c205983c…` passed 68 tests and 96 exact chain replays. The compiler observer verified FC1 CLC, two-CTA FC2, both per-token phases and disabled prefetch when PDL is off (58 compiled instances). This is focused correctness evidence, not sanitizer coverage or a performance result. Parent owns investigation of per-token prefill timing regressions.

## Narrow two-CTA GEMM: actual missing dependency

The MMA instruction and SDK support M256 with N16/N32/N64. Eighteen B-copy-only kernels compiled, including N16's eight-row per-CTA copy into its unchanged 16-row physical allocation. The existing wide two-CTA kernel already executes runtime N16 for partial tiles. No new math or epilogue transformation is needed.

The missing dependency is scale publication. Narrow route tiles use 128 producer lanes for local `cp.async` SFB rather than canonical-atom TMA. Installed `PipelineCpAsyncUmma` commits these loads to each CTA's local barrier: the AsyncLoad commit path ignores the producer-mask destination. Waiting only on the leader's local completion cannot establish that the peer's full SFB replica is ready for group2 S2T.

The candidate adds a readiness barrier for each operand slot only when group2 uses this local SF path. Each MMA warp waits for local cp.async completion, issues the existing async-proxy fence, and one elected lane arrives on the leader's readiness barrier. The leader waits for both CTAs before S2T. The existing operand empty ring prevents reuse until UMMA completion, so no extra empty ring or per-stage producer join is needed. The readiness phase is the existing SF consumer phase.

The storage is eight bytes per operand stage before normal slab alignment. It enters both automatic K selection and final stage fitting. Initialization uses the standard cluster initialization fence/rendezvous. Existing group1 and TMA-SFB group2 specializations allocate no readiness storage and emit no join.

The isolated delta is [narrow-only.patch](evidence/generality-narrow-group2-r2/narrow-only.patch), based on the frozen resource planner. Full source patch is `7658b47302377b98a03ef0c61a4f34c539fc072ac7bd8d87f9e262ff790c6dfa`; core is `63ac0c87ddfd714e75cf11d1ea86800646158904130fa978d29b4ca97d2e7822`. Scoped precommit passes. No autotune tactics were added.

The initial transport failure and a subsequent observer lifetime error remain preserved. The observer now retains each graph's callable and its captured weights/workspace until replay finishes. An independent SDK review also identified that remote arrivals default to CTA scope. The corrected implementation explicitly uses cluster-release arrival and cluster-acquire wait for the peer scale handoff; this is a data-publication requirement, not merely a counter rendezvous.

The corrected frozen source is `f793d812600ae9a54e633c351624946864fb5ccb00963aa4300e6a0ce80f9eea`; core is `02dfa398a7427e64e19ebb339685cfd36e0e5c734529a0ee63db3bcf971fe04d`. It includes planner deduplication and the quantizer startup pin `702f3e22…`. The GPU5 gate passed 288 static-scheduler exact comparisons plus 96 forced-CLC comparisons, including one-CTA control, either/both phases with group2, PDL on/off, changing inputs/routes, empty work, K tails and persistent SM2 work. The first static run stopped at the MX tactic registry after its 72 completed NV comparisons; those successful rows and a separate 216-case completion are explicitly bound in the [gate summary](evidence/generality-narrow-cluster-r1/gate-summary.json). Failed runs are not labeled complete.

All compiled narrow group2 artifacts emit cluster-release arrival and cluster-acquire wait; group1 emits neither new operation. Actual shared storage stays within the SDK budget. The CLC gate verifies effective group2 scheduling and prefetch in both phases, but does not instrument whether a particular live tile came from cancellation. These are focused exactness checks, not sanitizer coverage or performance evidence.

The validated M128/M256 geometries are now exposed uniformly for all five routed-token tile sizes, expanding 13 paired tactics to 22 while preserving every previous tactic and its relative order. The existing M512/N128 tactic remains. [Applied tactic receipt](evidence/generality-narrow-tactics-r1/applied.json) binds scoped precommit and the kernel gate. Retention and any further M512 expansion still require the separate workload campaign.

## M512 channel reuse and admission

The M512/N128 restriction was also an admission restriction: the existing two physical M256 instructions and epilogue channel loop already support narrower routed-token tiles. Admission now checks minimum accumulator plus canonical-scale TMEM against the SDK capacity. M512/N256 is rejected by that capacity calculation; M512/N16/N32/N64/N128 fit. No device method changed for this extension.

The frozen M512 FC1 source `ab28db37…` passed 216 static-scheduler and 72 forced-CLC exact comparisons against M128/M256 controls, including partial channel tiles, per-token quantization, empty work and PDL on/off. The actual M512 instances use K256, three or five operand stages, 256/512 TMEM columns and 205696–231296 shared-memory bytes. [Gate summary](evidence/generality-m512-narrow-r1/gate-summary.json) binds the raw comparisons, source and generated cluster-scope instructions.

The tuner generates all three channel tilings for FC1 without another N whitelist. Its existing actual-problem `can_implement` filter admits 28 of 30 generated pairs across all six dtype/SF contracts; the rejected pairs are M512/N256. [Host-only SDK audit](evidence/generality-m512-narrow-r1/admission-cpu.json) ran without initializing CUDA. All original tactic ordering remains. The combined source is [c36ce1f8…](evidence/generality-m512-combined-r1/source.json); only tactic generation differs from the M512 device-gate source.

FC1's remaining one-CTA CLC condition is a performance policy rather than a structural requirement: group2 and channel reuse share the tested initial-work mapping, group-aware completion protocol and scale-publication join. A separate `use_clc_scheduler=True` policy trial can retain the existing allocated-work capacity, explicit SM reservation and CUDA grid-Y guards. Scheduler metadata can affect the compile-time K/depth fit, so that trial must record the emitted choices. No such policy change is included in these gates.

The FC2 adapter had a separate unconditional M512 rejection. Source review found no missing scatter ownership mechanism: both MMA channel tiles finish before operand release, the epilogue visits both channel offsets, and bulk output drains and rendezvous before scratch reuse. The accumulator is released once after both channel tiles. Removing only that rejection passed 306 exact comparisons with identical output byte hashes, across 17 configurations and 136 compiled instances. The 34 M512 scatter instances cover N16/32/64/128, all three formats, per-token NV, PDL on/off, K384/K2304, partial 384 output channels and empty/persistent routes. Actual M512 shared storage is 205056–231296B, with 2–5 stages and 256/512 TMEM columns. [Gate summary](evidence/generality-m512-scatter-r1/gate-summary.json) binds the immutable source and artifacts; fused-finalize output is outside this gate.

Both phases now use the same channel-tile generator. It emits 45 paired candidates and the existing capacity filter admits 40 across all six operand/SF contracts. The 5 rejected N256 pairs involve M512 in either phase and exceed minimum TMEM capacity. Existing tactic ordering is preserved. [SDK admission census](evidence/generality-m512-scatter-r1/scatter-admission-cpu-r2.json) is host-only with CUDA uninitialized; the first observer attempt accidentally left GPUs visible and is preserved separately rather than counted as a CPU proof.

A follow-up planner audit found that bulk-output eligibility was incorrectly treated as early accumulator release for M512/N128. Actual bulk overlap uses one channel tile and half the TMEM capacity in token columns. The predicate now matches that ownership window. An independent census of 1800 automatic and 3600 explicit-K policies changes only 6 newly admitted FC2 M512/N128 SF16 decisions; original tactics are unchanged. Automatic NV selects K512×2 instead of K256×4. [Census](evidence/generality-m512-bulk-plan-r1/cpu-census-independent.json) and [formatted-source bridge](evidence/generality-m512-bulk-plan-r1/format-bridge.json) bind this correction; its [source-specific 54-case gate](evidence/generality-m512-bulk-plan-r1/gate-summary.json) passes with equal output byte hashes and actual K512×2 / 223488B shared storage. The first attempt completed its comparisons but failed an inapplicable observer-only narrow-join assertion; the corrected rerun and failure are preserved separately. The complete 87-pin experimental source is [f4aaa68d…](evidence/generality-m512-bulk-plan-source-r1/source.json). Final performance integration remains held while the general K-policy experiment is resolved.

## Single-CTA publication audit

For an immutable routing ancestor, one CTA may perform the publication fence while all CTAs still issue their first startup trigger. The same issuing thread must wait for completed prerequisites, release at GPU scope, then trigger; CTA0 must execute this path even when its row is inactive. No earlier trigger may bypass its fence. Under the existing same-memory-domain contract, the [PTX grid dependency rule](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol) synchronizes that release with dependent-grid start, which requires every CTA to trigger or complete. The dependent wait still protects the current grid's payload. This reasoning supports the parent's isolated quantizer experiment; it does not justify early reads of the quantizer's own output or different memory domains.

## Resource planner review

The planner agent's automatic accumulator count uses the SDK TMEM capacity and actual scale footprint; the previous explicit policy is preserved across its 480-layout census. Automatic K selects a supported instruction grouping only when SMEM has room for the operand ring and epilogue scratch, preserving the current epilogue's 64-column early-release contract. That release extent is an implementation ownership constraint, not the hardware TMEM capacity. The new narrow readiness bytes are included in the same metadata helper.

No MegaMoE or Rubin production files were changed. Hardware instruction dtype formats and canonical SF atom alignment remain explicit. Generality of admission does not itself establish that a tactic should enter the autotuner; new geometry requires an exact gate and workload measurements first.

## Remaining output-path boundaries

The common epilogue separates operand formats from output conversion. Its direct scatter store converts FP32 accumulators to BF16, FP16 or FP32; the bulk path uses the existing 16-bit matrix-store instruction for BF16/FP16, while FP32 retains direct stores. The low-level finalize launcher allocates and validates all three output types. The mixed-input-only BF16 guard in the FC2 capability adapter is therefore not explained by MMA or scatter-store hardware. It remains unmodified and unvalidated for wider output types in this campaign.

There is a distinct public API contract: `fused_moe.py` explicitly restricts both W4A8 and W8A8 to BF16 output in the functional core and wrapper constructor. Removing only the low-level mixed guard would not extend that contract. Any later FP16/FP32 extension needs an explicit public-API decision, then tests of output rounding and combine behavior; this audit does not claim those configurations work merely because the conversion code is generic.

The `route_tile >= 128` admission for BF16/FP16 bulk scatter is a retained performance policy, not an MMA constraint. The current bulk implementation supports native 32/64-token slabs, so N32/N64 can be expressed without a new instruction; N16 also needs an explicit partial-slab loop rather than the current `tile_n // bulk_tokens` loop. Scratch feasibility is already derived from available SMEM, but feasibility alone does not establish a profitable store path.

Earlier B300 same-GPU, fixed-N16 C–A–A–C screens are preserved:

- [32-token bulk slab](evidence/fc2-narrow-bulk-r1-fixed/summary.md): whole-chain geomeans NV1.001166, MX8 1.000425, mixed1.000472; neutral overall.
- [Native16 bulk slab](evidence/fc2-narrow-bulk16-r1-fixed/summary.md): NV1.002440, MX8 1.001453, mixed1.000727. The timed N16 specialization was unaffected by a subsequently discovered metadata-offset bug at larger N. The corrected general slab passed81 byte comparisons; the buggy broader prototype was not retained.
- [Corrected bulk16 plus physical-N16 allocation](evidence/fc2-physical-n16-bulk-r1-fixed/summary.md): changing physical storage to fit a fifth NV operand stage lost overall NV performance (0.992761), with MX8 1.000942 and mixed1.000256. All99 exact comparisons and360 layout checks passed, but no source was retained.

Those experiments predate the current generalized PDL/planner. They justify keeping the bulk policy visible as a measured boundary, not asserting a permanent architecture limit. A future resource-based choice could enumerate legal slab sizes and their scratch cost, but a transaction-utilization cutoff would be a new heuristic without current evidence. No such cutoff or bulk-path change is added here.
