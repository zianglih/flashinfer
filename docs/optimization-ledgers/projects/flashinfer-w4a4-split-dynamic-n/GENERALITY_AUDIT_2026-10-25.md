# Split CuTe DSL MoE generality audit

Baseline: `84f9a8e79ce2d5bf93243dfcc4b1fb117441f682`. Active changes are
unstaged in `flashinfer-generality-review`. This is a working audit, not a claim
that every item below has been fixed or retained.

## Scope and decision rules

Audit the SM100 split path from route preparation through FC1, FC2, and combine,
including host admission, autotune tactics, operand layouts, scale publication,
PDL, cache hints, and resource planning. Preserve the existing public API and
shared numerical contract. Do not change MegaMoE, Rubin, CUTLASS, or CAKE.

Keep format encodings and instruction/layout legality explicit. Do not mistake
those requirements for evidence that a performance policy must be conditional
on a dtype or tile. Resource policy should consume actual storage requirements
and hardware capacity. A new optimization should apply to every supported
configuration where its data dependencies permit it.

## Findings and experiments

| Area | Finding | Action / boundary |
|---|---|---|
| Host admission | M/N/cluster legality duplicated in the generic launcher and kernel; some rejection occurs after preparation launches. | Consolidate on core admission and reject before launch. CPU invalid-launch probes prepared. |
| Cache hints | Explicit policy strings silently become normal caching outside one-CTA K8 startup prefetch. Weight policy repeats that conjunction. | Test literal policy resolution and uniform streamed weight/scale versus retained activation priority across both FCs. |
| Activation TMA | N16 MMA uses a physical N32 allocation and copies all 32 activation rows. | Separate logical copy extent from unchanged physical storage, preserving K/stage strides and joint-barrier byte accounting. Validate the copy layout before device execution. |
| Preparation padding | N16-only extra SF initialization exists to cover the physical N32 copy. | Remove only after logical copy extent proves the extra atom is no longer read. |
| K staging | Host K4/K8 choices and FC1 overlap eligibility are an explicit M/N table with duplicated TMEM arithmetic. | Develop one compile-time resource planner; do not merely relocate the table. |
| Accumulator stages | N128 and logical-M512 branches proxy a TMEM capacity decision. | Derive stage count from accumulator/SF columns and the 512-column TMEM allocation limit, retaining required ownership semantics. |
| Two-CTA admission | Small N and logical M512 outside N128 are excluded. | Distinguish actual blockscaled instruction/SF layout limits from epilogue implementation gaps using installed CuTe 4.7.1 and device validation. |
| PDL startup prefetch | Static one-CTA scatter only; CLC and two-CTA exclusions encode scheduler/ownership gaps. | Extend only with correct first-tile ownership, barrier quorum, and routing publication; removing the guard alone is unsafe. |
| SF load path | TMA for complete canonical 128-row atoms; cp.async for tiles starting inside an atom. | This is a physical layout constraint, not a model-specific preference. Consider a different representation only with a complete producer/consumer design. |
| Epilogue slabs | 32/64-token bulk slabs correspond to supported TMEM/stmatrix mappings. | Keep instruction ownership constraints explicit; generalize dispatch from capacity and layout rather than problem dimensions. |
| Combine geometry | Fixed token thresholds and a five/six/seven divisor list are empirical launch policy. | Replace only with a measured general work/resource policy. Prior packed-FP32 and LDG256 substitutions were already tested and rejected; do not rerun unchanged experiments. |
| Dtype branches | FP4 packing, MXFP4-in-byte unpacking, SF encodings, and quantization have distinct instruction semantics. | Preserve necessary numerical/encoding specialization; eliminate duplicated policy, not the format contract. |

## Measurement and validation

The existing six published benchmark outputs remain valid for the current
implementation. A bounded causal screen uses tokens 4, 32, 128, 512, and 4096
for V3 EP8, V4.1-Flash EP4, and Kimi K3 EP8 on separate B300 GPUs. It uses the
public benchmark's native AUTO path, 10 warmups, 100 cold-L2 CUDA-graph CUPTI
samples, PDL, and unfused CuTe finalize. New final performance evidence uses
TRTLLM as the public comparison baseline; no old full before/after campaign is
repeated merely for formatting or cleanup.

Before timing a layout/synchronization change, run focused numerical and graph
replay gates across formats, per-token NVFP4, PDL on/off, changing routes,
partial and empty work, and admitted CTA/tile configurations. Keep exact
source hashes, full-precision results, raw output, and tactic choices locally.
Broader sanitizer work remains deferred until a useful optimization is retained.

## First measured candidates

- `generality-cache-r1`: uniform weight/SFA `evict_first` and activation
  `evict_last`, plus admission consolidation. Existing 68-test gate passed.
  All three five-token native screens completed. Affected backend/model
  geometric means range from 1.0046x to 1.0199x versus the same-session current
  control; W4A4 is 1.0160x / 1.0135x / 1.0169x for V3 / V41 / K3. These are
  screening results, not final TRTLLM performance claims. V3 per-token T4096
  regresses to 0.9766x and remains a required final-grid check. Unchanged W4A16
  control means are 0.9995x / 1.0034x / 0.9996x.
- `generality-copy-r1`: cache policy plus logical B-copy extent. Existing
  68-test gate and 96 changing-input/routing graph replays passed, including
  byte equality against clean84f9 and PDL off/on. Installed-SDK proof checked
  26,155,008 addresses over 252 configurations and 18 descriptor compiles.
  Native five-token screens completed separately to isolate the copy change.
  Incremental affected-backend geometric means are 0.9994x–1.0045x: effectively
  neutral at this precision, with a small positive W4A4 result. Keep the
  resource/copy simplification as a candidate, without claiming a substantial
  isolated speedup. Unchanged W4A16 prefill AUTO variation reached 6.6%, so
  individual small timing differences are not reliable attribution evidence.
- General startup prefetch is implemented locally after the copy snapshot:
  exact initial CLC work is reused by scheduler and startup producer; one/two
  CTA producers retain existing group transaction accounting; all dependent
  activation/SF reads stay behind the wait. Preparation release-publishes
  routing, and the intervening per-token quantizer adds a GPU fence after its
  existing wait, dominating every trigger. Both FC call configs request
  prefetch directly from PDL, without geometry, fused, or per-token whitelists.
  Frozen c205983c passed 68 existing tests and 96 exact chain replays. Actual
  compilation covers FC1 CLC, two-CTA FC2, and both per-token phases. Standard
  NV/MX incremental screening is neutral to roughly +1%; per-token T4096
  regresses by 21 / 16 / 39 us on V3 / V41 / K3. Retention is pending an
  isolated synchronization experiment, not a per-token exception.

## Continuation and replacement environment, 2026-10-26

- Resource planner frozen a9ef37a8 passed the same 68 +96 gate. Its native
  screen was launched before the devbox disappeared; results need recovery
  from durable storage before any timing claim.
- Narrow two-CTA source7658 closes local SF publication with a per-slot
  cross-CTA readiness join. Descriptor/CPU/pre-commit checks pass; GPU gate
  has not run. The deduplicated planner preserves the join metadata fit.
- Quantizer source450fd2 moves the fence and dependent trigger to one issuing
  warp at each existing trigger site. Frozen8ac61640 contains exactly that
  one-file delta over validated PDLc205983c. This isolates publication cost
  without changing dtype or geometry policy. GPU validation is pending.
- The managed CLI confirmed fi-v41-gap-c2-1025 was absent. New C2/ziangli
  devbox fi-moe-general-c2-1026 requested with --bare, 8 B300 GPUs, explicit
  nvcr.io/nvidia/pytorch:26.05-py3. Fresh NGC catalog + release-note check
  confirms26.05 is the latest CUDA13.2 image (26.06 uses13.3;26.09 uses13.4).
  The default220CPU request could not fit; that pending request was deleted
  and replaced with64CPU,512Gi memory,100Gi disk, with no --size argument.
  New timing measurements require fresh environment/GPU identity evidence.

Primary PDL contract reviewed:
https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-griddepcontrol
A release fence before the first CTA trigger synchronizes with dependent-grid
start in the same memory synchronization domain; griddepcontrol.wait remains
necessary for payload consumption. The per-token publication experiment
retains this ordering and avoids redundant publisher warps.

### Recovered screening outcomes

The replacement is the same hu-pdx-150 host with all eight prior GPU UUIDs,
driver595.91.07, Torch/CuTe/CUDA/CUPTI versions, native cache and durable
sources. Environment recorded under evidence/generality-runtime-recovery-1026.
All completed NVFP4 rows and two V3 MXFP rows were recovered unchanged; only
uncompleted MXFP rows resumed. Full comparison is
evidence/generality-planner-screen-r1/comparison-recovered.json.

The automatic planner is neutral on NVFP4 but MXFP4x8 T4096 loses8.3% /3.9%
/4.1% versus PDL for V3 /V41 /K3. Do not retain its policy unchanged.
The sole-warp quantizer8ac recovers4.3% /2.1% /3.9% at per-token T4096
versus all-thread publication, but V3 is still3.8% slower than copy-only.
Unchanged W4A16 K3 also drifted, so that model alone is not causal proof.
Startup publication702f3e moves the one publisher to the common post-wait
prologue and removes three branch-specific trigger sites; it is now gating.

Retain cache/admission +logical-Bcopy as the independently validated first
subset61aac0ac: 47insertions/60deletions in three production files, 68tests
+96exactreplays, all-format native screens. Later prefetch/planner/narrow
experiments remain in the separate unstaged review source.

### Retained subset and subsequent diagnosis

- Cache/admission +logical copy committed/pushed f9b8937302a66eb29e52f8901be68458e494444f; canonical tree clean and remote verified. Frozen source61aac0ac matches every retained source pin.
- Quantizer common-startup e669eb19 passed68+96 and nativeNVscreen. Relative to late one-warp signaling, T4 per-token improves4.4% /4.7% /2.7%; V3T4096 loses1.8%. Source702f3e remains the validated startup candidate.
- Single-CTA publication4937c8ad is a further isolated candidate: one CTA release-publishes already completed immutable ancestors, while every CTA still signals and dependent payload waits remain. Formal review and device gate pending.
- Narrow group2 had a diagnostic graph-lifetime bug: helper did not retain callable/workspaces. Correct keepalive fixes the mismatch; then independent review caught CTA-default barrier scopes. Corrected f793 uses explicit cluster release/acquire (verified generated PTX) and passes288 static exact comparisons acrossN16/32/64. Forced CLC coverage remains pending. No new tactics retained yet.
- Planner diagnosis: unchanged K3 geometry loses queuedK coverage896→768 (FC2K128×7→K256×3); V3 loses640→512 (FC2K128×5→K256×2). FC1/dedicated epilogue/protectedTMEM are unchanged for those selections. Fixed K4/K8 controls and generic capacity-ranking experiment are in progress.

### Capacity admission and causal publication diagnosis

- Cluster-scoped narrow M256 passes288 static +96 forced-CLC exact comparisons. Expanded M512 passes216 static exact comparisons across formats and narrow N, with partial channels/reduction, per-token, PDL off/on and empty routes. Narrow M512 forced-CLC is separately checking the initial-work/channel-tiles mapping.
- Frozen CTA0 publication1b7bf1c6 passes68 existing tests +96 byte-exact changing-input/route replays. Every CTA still triggers, but only CTA0 publishes already completed immutable ancestors. Formal PTX review confirms the release-before-first-trigger ordering in the same memory domain; dependent waits still protect produced payload.
- Isolated phase trace identifies the old all-thread fence as the per-token cost: deleting its one PTX fence makes the quantizer PTX byte-identical to copy-only. It emits MEMBAR.ALL.GPU +ERRBAR +CGAERRBAR +CCTL.IVALL, without changing registers/spills. Quantizer medians63.040/82.849/71.520/76.609us for copy/PDL/late/startup; FC1/FC2 remain nearly constant. Evidence: generality-per-token-prefill-profile-r1.
- Fixed-FC2 K4/K8 causal runs confirm the queued-depth regression: K4 recovers MXFP4x8 T4096 by5.36%/3.61%/3.85% for V3/V41/K3. Generic ranking maximizes staged K coverage, using larger K on ties; matched AUTO control/candidate is pending to catch NV decode tradeoffs.
- First source-private-cache performance launches failed before any token median: installed FileLock refuses symlink locks with O_NOFOLLOW. No performance evidence was produced. Repairing native lock sharing and testing actual lock contention before retry; kernel/source hashes remain unchanged.

### Remaining policy boundaries versus implementation constraints

- Prefetch/cache policy is now independent of format, CTA group, scatter/fused mode and CLC in the experimental source. Metadata publication plus activation dependency waits are the controlling correctness contract.
- Narrow group2 SF readiness is a genuine cross-CTA dependency: local cp.async publication differs from canonical-atom TMA. Its extra per-slot barrier is conditional on that communication mechanism, with storage charged to the same capacity planner.
- Canonical SFB atom alignment still determines TMA versus local loads. Physical N remains at least32 for the existing epilogue transpose; logical B transfer extent no longer inherits that padding.
- M512 narrow FC1 passes216 static +72 forced-CLC exact comparisons. Tuner generates candidates uniformly and actual core TMEM capacity rejects M512/N256. FC2's old unconditionalM512 exclusion has no observed structural reason; admission-only gate is in progress.
- FC1's one-CTA CLC call-config whitelist has no remaining structural blocker after narrow cluster/initial-work gates. An isolated scheduling screen is still needed before broadening the production policy. Generic allocated-work, SM-budget and CUDA grid-Y checks remain valid scheduler resource guards.
- Narrow bulk-scatter selection is a separate measured performance/epilogue boundary; prior narrow-bulk regressions must be revisited before changing it. The64-column early accumulator release is an ownership constraint, not a hardware capacity limit.
- Public W4A8/W8A8 APIs deliberately requireBF16 output. Low-level mixed FC2 BF16-only admission appears broader than the hardware need, but changing it alone does not change public API support. No output-contract expansion is included in this optimization pass.

### Benchmark cache repair

Installed FileLock rejects symlink final components and unlinks locks on release. Common tmp-directory linking (regular lock-file final component) passes real cross-process contention and reacquisition. CuTe objects remain private; build locks may serialize across sources. Native headers/sources/outputs already resolve canonically, but a private generated-directory root changed the -I flag and forced repeated unchanged moe_utils builds. Whole-directory generated linking fixes this without modifying JIT code, public benchmark calls or GPU timing. Ancestor r2 was stopped with zero medians before restarting with repaired namespace; no data was discarded. Queued-K completed control arms are preserved across the candidate setup correction.

### Retained generalized PDL

Pushed dea2c065dc8e75ae26fe1ef8123e964db7b4eadb (parentf9b89373), source-equivalent to frozen1b7bf1c6. Canonical tree clean, remote verified, all86measured pins match and scoped precommit passes. Sixfiles64insertions/71deletions. Removes the one-CTA/static/scatter/nonfused weight-prefetch guard; both phases prefetch underPDL, with exact initial CLC mapping and immutable-ancestor publication.

Ancestor publication screen r3 completed all3models×5NVtokens with nativeAUTO on the same GPUs. Compared with retained copy-only: per-token T4 improves3.41%/2.96%/1.77%, T4096 speedups0.9995/1.0035/1.0052; W4A4 essentiallyneutral. K3W4A16T4096 control drift0.9333 means small K3prefill effects remain noise-sensitive. Same-tactic V3 and unaffected W4A4 support quantizer-cost recovery. Existing1b7 gate68+96 passes. Prior c205MX results are reused because the sole subsequent source difference is the per-token NVFP4 quantizer, absent from MX paths. Details in evidence/generality-retain-pdl.

Queued-K blanket ranking is NOT retained: matched V3nativeAUTO loses~4% per-tokenT4 (sameM128N16bothphases,K512x4→K256x9), while MXFP4x8T4096 improves5.87% (sameM256N256bothphases,FC2K256x2→K128x5). Exploring direct autotune K choices instead of a format/shape threshold. Expanded geometry/resource planner remains unstaged in the separate review copy.

### Review checkout follows retained commits

At the user's request, the independent `flashinfer-generality-review` checkout
now advances its HEAD/index after every retained push while preserving working
files. Reset from84f9 todea2 used `git reset --mixed`; all11992 tracked/untracked
working file hashes were identical before/after, and nothing was staged. The
remaining seven-file diff contains only the resource/tactic experiments and
associated existing-test expectation updates. Frozen remote evidence retains its
original source identity. Receipt: evidence/generality-review-base-dea2/receipt.json.
The reusable task-local helper is scripts/generality_audit/advance_review_base.py.

Clean dea2 final gate passed68 tests and96 byte-exact changing-data/route replays,
with all five expanded-PDL coverage checks and87 unchanged source pins. Evidence:
generality-retained-dea2-gate-r1. Fresh full13-token six-family/model public TRT
comparison tables are running onGPUs2/3/4 under generality-final-dea2-r1, with the
corrected source-private CuTe cache namespace. No historical table is relabeled.

### Internal K tuning and input-quantization timing

The optional K choice is internal. Two explicit public adapters preserve the
six existing generic/NV/MX FC signatures and defaults; private implementations
share all preparation/validation and receive the autotuner K pair. Public K
arguments are rejected. Frozen ccf84c54 has68 focused tests +96 exact replays
passing,21 existing CPU tactic/private-spy tests passing, and an additional210
K-pair/BF16-input replay gate running. Expanded geometry/CLC/K remains unstaged.

Per the user's refinement, benchmarks/bench_moe_deepseek.py keeps its existing
opt-in include_activation_quant behavior byte-for-byte. Our campaign now passes
--include-activation-quant for NVFP4 only. Initial standard/per-token quantization
is timed for both CuTe and TRT quantized-input arms; W4A16/BF16 still consume BF16.
MX remains prequantized. The before-FC1 chain includes top-k (V3), sort and
prepare; prepare republishes completed routing metadata before FC1 weight reads.
This does not assert direct quantizer/FC1 overlap. The opt-in smoke passed16
public configurations /48 finite changing-input graph replays onclean dea2.

Fresh retained-dea2 NV full13-token tables with the opt-in flag completed on
GPUs2/3/4 undergenerality-nv-input-dea2-r1. All source87pins unchanged. Earlier
quantization-excluded six tables remain immutable in generality-final-dea2-r1.
Their old CPU MX parser expected two ratio cells; an independent CPU-side audit
reparses the grouped column and verifies all78rows against native medians,
TFLOPS, ratios and winners without rerunning GPU work or rewriting raw receipts.
Evidence: generality-final-dea2-r1/parsed-table-audit.json.

### Explicit K overlap admission and publication follow-up

The ccf84 explicit-K replay reached72 exact outputs before exposing an FC2
policy gap: NV M256/N256 withK8 has96scale columns, so constructor capacity
analysis disables overlapping accumulators, but the bulk wrapper re-enabled
them and failed compilation. The correction preserves the derived eligibility
and uses the existing non-overlapping epilogue; it does not exclude a dtype or
geometry. R1 screens are diagnostic only because autotuning skips these invalid
tactics. Corrected r2 gates/performance will determine retention.

The input-inclusive retained-dea2 full13-token NV control is complete and all87
source pins are unchanged. W4A4/TRT speedup geomeans overT>=4 are1.06333 V3,
1.02844 V41 and1.01315 K3. All V3/V41 T>=4 rows exceed1; K3 still has decode
gaps. Per-token prefill remains slower than its TRT per-token counterpart where
supported. These are new input-inclusive numbers, not comparable as causal
changes against old input-excluded tables.

A read-only PDL ownership audit supports a small separate publication-fence
experiment: one physicalCTA publishes immutable ancestors for static grids;
CLC retains one publisher per executing cluster because cancellation may
remove a fixed physicalCTA0. All CTA signals and dependent payload waits stay
in place. Source/contract proof: evidence/generality-pdl-publication-audit-r1.
No blanket CTA0 rule or new election protocol is introduced.

R2 patch6379bed2 corrects overlap eligibility and removes duplicated scratch/K-fit
planning. CPU5400plans and1080admission decisions remain equivalent; exactly4
previously invalid NV N256K8 launch plans now use non-overlap,1004others unchanged.
All210 explicit-K public changing-input/route outputs are byte-exact, covering
PDL off/on, allfourKpairs, per-token, and one/twoCTA CLC. The150casebatch exited1
only after numerical completion because its helper wrongly required a one-CTA
CLC dispatch on too little work; immutable outputs/source/hash/coverage were
independently recomputed alongside the60casebatch. Source-bound combined proof:
evidence/generality-explicit-k-gate-r2/combined-replay.json.

R1 diagnostic K3 screen shows3–5% T4096losses, with unchanged W4A16controlstable.
No retention decision is based on that invalid-tactic r1 screen. R2 screens use
CuTe-only selectors to avoid redundant unchanged TRT compilation; final retained
full13token campaign will run default public comparison arms. If needed, isolate
CLC policy against identical planner/K choices before retaining the combineddiff.

The corrected r2NVscreen repeatsK3T4096 W4A4~0.947 andper-token~0.963
versus retained control. V41T4W4A4~1.021, V3mostlyneutral. UnchangedW4A16
K3T4096 also drifts~0.951 onr2, so fixed-tactic C–A–A–C static/CLC
diagnostics will bracket current drift; no direct performance-cause claim yet.

Publication ownership refined source6cbb9c46 folds singleton-cluster ownership
at compile time. Its singletonCLC PDLon/offPTX matches retained bytes; group2
uses rank0 and static grids use original physical coordinates. Evidence binds
114broadreplays on35436 plus6delta replays on6cbb9; neither is relabeled as
a fullgateonanotherpatch. The isolated three-model input-inclusive NV C/A
screen uses GPUs5/6/7, with W4A16 control and no redundant TRT tuning.

### R3 generality / static scheduling / publication integration

The fixed-tactic C–A–A–C scheduler experiment on exact R2 source recovered K3
T4096 with static FC1: W4A4 1.057854, per-token 1.045925, MXFP8 1.031467,
MXFP4x8 1.070169 versus CLC. V41 T4 W4A4 was 0.990686. C1/C2 were stable;
all cache-only selections and captured buffer/TMEM plans matched. Register/SASS
equality was not captured. Keep one static FC1 default across geometries; retain
the supported CLC kernel knob without adding a shape whitelist or scheduler
search. Evidence: generality-clc-causal-r2/summary.json.

Isolated publication-fence reduction was also approved for integration: native
AUTO results and fixed-tactic A2–C2 are separate evidence, not one aggregate.
Fixed-tactic T4 W4A4/per-token gains were V3 +1.63/+1.57%, V41 +0.84/+0.67%,
K3 +1.11/+0.93%. Residual prefill losses were sub-percent; all selected tactics
and captured plans matched. Evidence: generality-pdl-publish-fixed-r1.

Combined R3 patch 04c682c66c87a6584890485ce052974b55df8f2d862c50bfd1ba2a2e02893809
passes 68 existing tests and 96 exact changing-data/route replays. All 32 captured
FC1 compilations are static; expanded PDL/per-token/two-CTA coverage is present.
The 87 source pins are unchanged before/after. The benchmark remains byte-identical
to dea2: include_activation_quant is opt-in; only this campaign's NV family enables
it. Native five-token screen is running before promotion. Existing exact-byte gate
will be bound through verified promotion; committing identical files is not a
reason to rerun the GPU gate. Evidence: generality-static-owner-gate-r3/promotion-inputs.json.

R3 full five-token screen completed all 75 CuTe rows with matching source, route,
recipe, timer, runtime and GPU checks. It is not retained. Static recovers K3
prefill, but repeatable middle-decode losses remain with unchanged geometry/K:
V41 MX8 T32/128/512 0.99059/0.98055/0.97169 and K3 MX8
0.98804/0.98605/0.96463 versus dea2. Same-tactic W4A16 controls are nearly
stable at the affected decode cells. Source-bound results:
generality-static-owner-screen-r3/comparison.json.

Proceed to R4: a flat internal FC1 scheduler boolean alongside geometry/K,
whole-chain native AUTO, no scheduler-specific shape heuristic or nested ranking
adapter. Public signatures remain unchanged. Legacy tactics request CLC by
default, preserving established one-CTA behavior while dropping the old CTA
whitelist; new tactics explicitly select static/CLC. Existing hardware launch
admission stays authoritative. Raw candidates increase 180 to 360, resource-
admitted candidates 160 to 320; distinct GEMM specialization upper bound rises
56 to 84 (FC1 doubles, FC2 unchanged). Actual compilation/tuning time and actual
benchmark routes determine whether this is worthwhile. Synthetic profiling uses
balanced approx-max routes and can differ from benchmark routes; no assumption
that the extra axis alone fixes selection.

Promotion-cache audit found no safe useful alias for compiled CuTe artifacts.
Installed raw cute.compile disables persistent caching for the main GEMMs and
exported quantizer keys include absolute resolved source paths. A different clean
checkout would miss those keys despite byte-identical files. Keep source-private
CuTe caches; retain existing safe native library/generated-root/regular-lock
sharing. Evidence: generality-promotion-cache-audit-r1/review.json.

R4 host/gate passes: 68 existing tests and 72 exact scheduler replays. All12
changing-data groups match across legacy/static/CLC and PDL off/on; six requested
and effective scheduler coverage flags pass, including one/two-CTA and per-token.
Public signatures unchanged; flat AUTO profiling will be observed separately.

Before any R4 timing, cache audit found pre-R4 persisted v3 winners bypass the
new search: search_cache precedes profiling even inside autotune(True), no
source/commit hash exists in the key, and this runner has no validate_tactic.
R5 changes only the blockscaled runner marker to v4 (legacy parsing unchanged;
W4A16 unchanged). The other86pins match R4. First scheduler-AUTO timing runs on
R5; targeted gates also run there in parallel to avoid adding cache-only source
exceptions to final evidence validation. R4 gate remains labeled R4.

### R5 retained: 74388819

Retained/pushed 74388819899d0abfd1a12102f7cc108bda13c812 after 68 existing
tests and 72 byte-exact changing-data scheduler/PDL replays. The five-token
three-model native AUTO screen completed all 75 CuTe cells. Every affected
model/backend geometric mean was positive (1.001117–1.010934x); the worst
affected cell was K3 MXFP4x8 T32 at 0.994127x. V41/K3 mixed T4096 were
1.031084/1.034764x, but W4A16 prefill control drift prevents treating these small
prefill deltas as isolated mechanism proof. R5 recovers R3 middle-decode losses.
The expanded flat scheduler axis costs 1.64–1.85x combined NV+MX screen wall
time versus R3, including setup/compilation/profiling. Accepted as the simple
general solution without a model/geometry whitelist.

Measured parent dea2 + patch af2426e28bd67ac537adf7d31f979bd40aa22584fb600d5df849ee4677d12037
is byte-identical to clean retained source. Independent source review, screen
recomputation, promotion hashes and scoped precommit checks passed. Evidence:
- generality-retain-scheduler-r5/retention.json
- generality-scheduler-screen-r5/comparison.json and independent-review/full-review.json
- generality-scheduler-tests-r5/validation.json
- generality-scheduler-replay-r5/validation.json

The separate review checkout advanced from dea2 to 74388819 with all 11,992
working files unchanged; it is now clean. Receipt: generality-review-base-74388819.
Final clean-source full13 tables launched concurrently on C2 B300: NV GPUs2/3/4
and MX GPUs5/6/7, each in V3 EP8, V41-Flash EP4, Kimi K3 EP8 order. Tags:
generality-final-74388819-nv-r1 and generality-final-74388819-mx-r1.
The benchmark include_activation_quant option remains opt-in. This NV campaign
explicitly enables it; MX remains prequantized. Six source-pinned final tables
will replace old PR evidence. No correctness replay is repeated for identical
committed bytes. Source-private CuTe cache and native AUTO are preserved.

Final clean74388819 full13 campaign completed all six tables, each exit0 with
87 source hashes unchanged. Initial quantization is timed in NV only; no change
to the opt-in public benchmark default. Same-sweep standard W4A4/TRT NVFP4 GMs
(excluding1/2) are V3 1.066728, V41 1.039368, K3 1.012797. Decode4–512 GMs are
1.044845/1.029149/0.995638: K3 still trails slightly, worstT512 0.964820.
Matched MX4x8 GMs are1.051270/1.035143/1.036832; MX8 V3/V41 1.042849/1.006504,
K3 TRT MX8 is unsupported. Per-token vs TRT per-token decode wins in aggregate
(V3 1.063257,V41 1.029270), but prefill trails (.938977/.917358). These are
one-sweep status results, not universal or stable-win evidence.

Complete final evidence: generality-final-74388819-summary/comparison.json;
independent recomputation: generality-final-74388819-independent/review.json.
All377 native latency/TFLOPS entries,208 displayed ratios,39NVwinners,156saved
outer5/v4 choices and exact quantization/timer/source contracts checked.
Final plain observer records cached selections, not actual core forwarding.
Actual forwarding proof remains the separate byte-identical R5 five-token
screen (60affected calls); effective scheduling is established by72 replay
compilations. Publication validators bind these explicit scopes instead of
rerunning or inventing observer fields.

Published final PR body at2026-10-26T11:40:19Z and verified exact GitHub readback
under zianglih. Head74388819 and draft status unchanged. Body40196bytes,
SHA256680dabf995ca2e9f6e89e201daa4def8688ad73e0d0eb3880d7c8cfd4c7c4b6f,
opening13token speedup table plus six fresh raw outputs and concise68+72scope.
Publication receipt: evidence/generality-final-74388819-body/publication.json.
Canonical and review checkouts both clean at74388819. GPU2–7 benchmark jobs
finished and were released. Project README now points to this round.
