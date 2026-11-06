# Parallel optimization pass after7829fc00

User scope: continue all-dtype split CuTe DSL MoE optimization, referencing the
W4A16 split ledger and MegaMoE/CUTLASS/DeepGEMM. Preserve current API workflow,
per-token support and fused epilogue activation. Do not edit MegaMoE production.
Final PR body reports only the final retained version; experiment history stays
in this project. No old baseline reruns. Existing exact13-token native AUTO
benchmark, all three requested modes, fused finalize disabled, tokens1/2 excluded
from retention, unchanged10/100 cold-L2 CUDAgraph/CUPTI timing.

Frozen starting candidate: `7829fc00dc7121341cc40cd4190660507e006490`.
Existing C1 bare8xB200 devbox `fi-w4a4-dyn-n-1024`, namespaceziangli,
image `nvcr.io/nvidia/pytorch:26.05-py3`. Available GPUs permit parallel work;
no extra devbox has been requested. Shared native JIT epoch remains candidate.
Production checkout is frozen; each axis uses isolated module snapshots.

## Historical sources

- `../flashinfer-w4a16/w4a16_optimization_experiments.md`: retained one-item
  multi-wave FC1 CLC, activation EVICT_LAST/weight EVICT_FIRST and detailed
  stage/register experiments. Old results are source-specific hypotheses,
  not current evidence. FC2 CLC and N-major raster were previously rejected.
- `../flashinfer-w4a16/w4a16_warp_specialization_constraints.md`: warpgroup
  uniform setmaxnreg, actual launch pool and TMEM lane ownership constraints.
- Current FlashInfer SM100 MegaMoE source: scheduler, blockscaled pipeline,
  descriptor prefetch, epilogue and register policy reference only.
- CUTLASS and DeepGEMM register policy source audits are recorded by the
  register-budget experiment.

## Parallel axes

| Axis | GPUs | Durable artifact |
|---|---|---|
| CLC and raster scheduling |0,6|`scripts/scheduler_experiment/`|
| Stages, cache policies, descriptor prefetch and safe early PDL signal |1,4|`scripts/pipeline_cache_experiment/`|
| Register budget and warp specialization |2,5|`scripts/register_budget_experiment/`|
| FC1 arithmetic/loop simplification |3,7|`scripts/fc1_arithmetic_experiment/`|

## Decisions so far

- FC1 abs-max tree, xorsign abs-max, symmetric clamp and static slab unroll:
  paired exact checks pass, isolated phase changes below1%; not integrated.
- Static N-major traversal: native N256 A/B/A324.496/335.344/324.288us,
  paired bytes pass,3.38%slower; rejected.
- Initial producer96/epilogue256 register split: rejected before further timing.
  REG168 and288threads provide48384 registers, while requested redistribution
  exceeds that actual pool. The smoke was stopped and GPU process cleaned up.
  Follow-ups validate each emitted launch allocation before allowing inc.

Primary results from earlier checkpoints remain in their existing `evidence/`
folders. Those failed retention screens are not final retained performance.

## Subsequent diagnostic outcomes

- Register redistribution96/224 and128/192:270 paired exact cases pass,
  native changes neutral/slower across NVFP4/MXFP8/mixed; reject. Resource
  evidence finds no spills in the starting kernel. Archive and SHA are in
  `scripts/register_budget_experiment/README.md` and `evidence/register-budget-7829fc00/`.
- One completion barrier for operand-storage reuse:24 paired cases and native
  FC1/FC2 bytes pass, changes<0.4%; reject. See `scripts/single_completion_experiment/`.
- Invalid-output epilogue-omission bounds:FC1 323.713→300.017us, FC2
  178.608→90.4645us. These are diagnostic bounds only, not performance claims.
  They motivate the next FC1 wider-K mainloop and FC2 bulk R2S vectorization axes.
- CLC1 remains a candidate only for N256:large native FC1 ~3% better and
  active-cycle balance improves. N128 loses6–8% with either1/2metadata stages.
  Static metadata publication and wave permutation do not explain the gain.
- W4A16-style weight EVICT_FIRST regresses here; activation retention and TMA
  descriptor prefetch are neutral. Safe early PDL signal after dependency wait
  does not improve the full fixed-tactic chain. Detailed source-local records
  remain under `scripts/pipeline_cache_experiment/`.

- N192 two-CTA intermediate routing capacity passes18 raw exact cases and
  native final-output equality across N256/192/128, but full native latency
  regresses618.0→648.0us; reject the extra tactic.
- K128/two native MMA steps with6/8/10 stages is exact on native NVFP4 but
  slower than K256/four steps for both phases; reject.
- FC2 stage5 at oneCTA/N128 is a composition candidate: reverse checks give
  ~3–4% NVFP4 and~8–9% MXFP8/mixed phase gains with24all-format exact pairs.
- FC1 eight-stepK at twoCTA/N128 is a composition candidate, with repeated
  NVFP4 gains~3% and initial MXFP8/mixed gains. Other geometries remain unchanged.
- FC2 direct Ld16x256→STSM transpose is exact but unpadded shared rows cause
  severe bank conflicts. Padding row stride128→136 elements reduces measured
  shared-store conflicts and gives~2% NVFP4 N256/twoCTA and~4.7% N128/oneCTA;
  preserving two output stages matters. Broader/reverse evidence is ongoing.
- Next larger FC1 experiment: dual channel tiles per CTA group sharing B/SFB,
  analogous to the prior W4A16 NB2 direction, distinct from two-CTA MMA.

- SFB cp.async L2 prefetch64/128/256B hints and a no-hint inline-PTX control
  are exact but neutral/slower (FC1 323.505us control vs323.808–324.065us;
  FC2 180.689us vs180.7845–180.8645us); reject. Raw evidence is in
  `scripts/sf_cache_experiment/results/`.
- Completed pipeline-stage candidate passes48 all-format FC1,50 NVFP4
  tail/per-token and24 FC2 format/tail pairs. NCU finds zero local-load/store
  sectors for baseline and wider-K variant; the latter uses172928B SMEM
  vs144384B. Equivalent production integration patch is recorded locally.
- Padded STSM candidate completed98 paired exact cases and independent/reverse
  native timing. Archive hash and source hashes are in
  `evidence/bulk-r2s-7829fc00/summary.json`.
- Combined wider-K/stage5/padded-STSM full-chain diagnostic is running in an
  isolated package under `scripts/composed_stage_store_experiment/`.

## Retained incremental checkpoint285bae77

Pushed285bae770c688328f0da82660c307a5be7417375: FC1 M256/N128 wider K,
FC2 M128/N128 stage5 and padded STSM. Pre-commit passes. Combined native
fixed-tactic full-chain checks pass exact final bytes in all three modes.
These are incremental retained changes, not a claim of final baseline retention.

## Next combined screen candidates

- FC1 logical M512/N128: two physical M256 MMAs share B/SFB. Four operand
  stages for SF16, five for SF32. Keep M256 wider-K option because smaller
  token counts prefer it; AUTO gains two legal combinations,13 total, and
  tactic cache contract advances to v3. CLC remains unretained.
- FC2 bulk N256: overlapping accumulator windows0..255 and192..447 with
  SF storage448..495. Read overlap first and release ownership immediately
  after its TMEM-load fence, before conversion/store. Native NVFP4
 177.776→134.560us, MXFP8 253.985→199.536us, mixed242.576→186.224us;
 98 exact selected cases, seven small-token pairs, no spills/local instructions.
- One-CTA N16/32/64: eight native K steps/four stages, both phases. Native
  reverse/three-mode screens improve;48 FC1+24 FC2 all-format pairs pass.
  Initial test mismatch was a probe SF-allocation padding bug, corrected and
  preserved in logs. See scripts/small_n_widek_experiment/README.md.
- N192 NB2 FC1 gives281.872us vs N128 NB2 281.376us; no benefit justifies
  expanding tactics. Final-output equality passes. The N192 FC2 prototype used
  direct stores, so its full-chain timing is not a fair tuned N192 comparison;
  the FC1 result alone closes this axis without retaining geometry changes.
- iKET/NCU identifies producer imbalance, but redistribution is only~1.1%,
  weights-last neutral, and early SF completion commit regresses~0.9%; reject.
  Trace/profile artifacts and interpretations are in
  scripts/pipeline_cache_experiment/MAINLOOP_PROFILE.md.

## Combined13ca screen and follow-up directions (2026-10-25)

- Production13ca1475 is pushed;56 capability/tactic checks and12 complete-chain
  byte-exact comparisons pass. Integration smoke archive SHA256:
  84cfce7f2a578e748548c600e6ddf820edf7c02b4dbc65708c06452882a460a2.
- Primary A1 completed39 points using the saved B1. Decode/prefill/overall:
  NVFP4 .994551/.918510/.973209; MXFP8 1.062953/1.035364/1.055357;
  mixed 1.074825/1.002396/1.054568. NVFP4 still fails retention, especially
 8K/16K. No A2/B2 or final PR speedup table. Full source/cache provenance and
  raw outputs are in evidence/combined-screen-13ca1475/.
- AUTO audit finds matching source/cache hashes and exact token buckets for
  all39 rows. Native tuning uses balanced approximate expert loads while
  actual seeded routing is imbalanced; do not change the established method.
- User requested early W4A16 cache retest, alternative activation loading,
  aligned LDG256, B300 FP4 K96, and avoidance of shape-specific/runtime policy.
  Older cache rejection was geometry-specific, not a universal result.
- Current N16/K8 weight EVICT_FIRST looks useful in sparse decode. Retest
  includes reverse full-chain controls and other formats before integration.
  NB2 prefill does not benefit from that A policy; B retention is separate.
- W4A16 regular TMA B follows explicit moe_permute payload materialization;
  current Gather4 avoids that stage. Direct vector-load prototype preserves
  the current payload workflow and is screened independently.
- Reopened N192 only for a new mechanism: resource-derived full double FC2
  accumulator banks fit in512 TMEM columns; previous N192 used one bank.
  Initial NV16K exact full chain: N12813ca556.897us, N192single586.737us,
  N192double549.314us, N128trailing565.937us. Control drift requires reverse
  checks; no primary claim. Scripts/n192_doublebank_experiment/ preserves code.
- Additional isolated logical M768/N128 prototype tests three physical M256
  channel tiles sharing B/SFB, three SMEM stages,448 TMEM columns. Production
  unchanged. Requires exact output and adjacent native screening before reuse.

C2 B300 devbox fi-w4a4-k96-1025 created in ziangli with8GPUs, --bare, no size
option, explicit nvcr.io/nvidia/pytorch:26.05-py3. Live NGC catalog and official
26.09 release matrix checked immediately before request:26.05 is newest CUDA13.2
release;26.06+ use CUDA13.3+. Actual8×B300 SXM6 AC, driver595.91.07,nvcc13.2.78.
Sources: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch and
https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-09.html
K96 supports FP4×FP4 only and needs SM103-specific SF/descriptor handling; no
claim for MXFP8/mixed or B200. Prototype work is separate from the B200 campaign.

## Retained source through1904964 and current profile-directed iteration

Local/pushed source is1904964d09db7f9a56d370d510ed03a0222e15c9. Remote C1/C2
candidate remains frozen13ca1475 for isolated module experiments. No new primary
A1 has been run and no final retention claim is made.

- df556949 makes channels/reduction/experts compile-time constants, already in
  the host cache key. Routes/token count remain dynamic.72 paired exact cases
  and adjacent native phase/chain probes pass; see scripts/static_shapes_experiment.
-2476de1 imports only common finalizer rounding from PR7196 head36740c36:
  first slot mul.rn.f32, ordered later fma.rn.f32, masked slots skipped,
  all-masked output+0. The finalizer file is byte-identical to that PR file.
-1904964 retains weight TMA EVICT_FIRST only for one-CTA/eight-K-step geometry.
 72 exact paired cases and33 bounded native timing rows are recorded in
  scripts/cache13_experiment. No token/channel dimension cutoff.
-1904964 also retains opt-in iKET markers. Disabled SASS is exactly identical
  after kernel-symbol normalization for FC1 NB2 and FC2 N128. Enabled traces
  preserve output/SF bytes. See scripts/iket13_experiment for raw PTX/SASS,
  compressed traces, instrumentation commands and analysis.

Matched NCU at16K, same GPU6 and saved AUTO geometry, explains why fewer tensor
operations did not produce a speedup. FC1 old/current replay223.040/293.952us,
 tensor active69.13/40.49%; current executes16.15% fewer tensor operations but
 read-path counters rise~15.85%. Count old cp.async payload in addition to TMA:
 old payload933.560MB+SF933.560MB+TMA1412.956MB, current payload0+SF933.560MB+
 TMA2866.282MB. DRAM bytes rise586.95→638.44MB. These instruction-path counters
 are not DRAM byte totals. FC2 old/current127.264/164.192us, tensor active
56.88/37.45%, LSU global requests31,368→1,289,444; old SF loading uses TMA.
At8K true saved AUTO, old/current FC1 is139.104/166.272us and FC2 is
88.544/96.128us. Source-specific canonical preparation and phase replay are
exact; sampled canonical final outputs also match across revisions.

The iKET sampled FC1 leader sees4.328us accumulator-empty wait per output tile,
approximately the4.334us epilogue body: one accumulator serializes the next MMA.
FC2 N128 already has two stages and only0.069us accumulator-empty wait. These
instrumented durations include overhead and are structural evidence only.

Current experiments follow established FlashInfer dense blockscaled GEMM and
CUTLASS persistent GEMM lifetimes: alternating partially overlapping accumulator
windows, reversed epilogue slab order, and early ownership release after every
protected TMEM read (including split MoE's transpose reads). FC1 NB2 and N256
share this mechanism. A one-CTA wide-N experiment separately tests dedicated
 epilogue warps and overlap, without changing external layout or adding tactics.
FC2 canonical-SFB TMA tests eliminating fragmented cp.async loads and their
redundant local/peer completion relay. Actual SF footprints are audited from
CuTe layouts before reducing reserved TMEM columns.

Closed/rejected axes:
- Direct LDG256 activation loading, even with prefetch, and cp.async128 are
  slower than Gather4 on NV16K. SASS confirms256-bit loads; no unjustified
  alignment/API restriction is retained. evidence/activation-loader-13ca1475.
- N192 full-double-acc FC2 improves16K but regresses8K; no extra AUTO tactic.
  scripts/n192_doublebank_experiment.
- FC1 logicalM768/N128 sharedB/SFB (NB3) is exact but neutral/slower. No tactic.
  scripts/nb3_experiment.
- FC2 N128 earlier release passes24 exact pairs and mildly improves NV but is
  not the main profiled bottleneck; deferred rather than composed.
  scripts/fc2_early_release_experiment.
- SM103 FP4 K96 wide-K and cross-stage prototypes are exact but slower on B300;
  NCU tensor activity decreases. Neither is integrated. Archive
  evidence/sm103-k96-13ca1475/raw.tar.gz SHA256
  b3fd4e1745903e4a847cfa62046ab3f2d7d7e5229555bfd12a4cbcbfdd7dfbfa.

Combine scope now includes vectorization, packed FP32 arithmetic and geometry.
An immutable PR7196 rounding reference is the baseline. First packed128/wide256
probes pass72 signed-zero/subnormal/masked/permuted/expanded/scale-type cases,
but have mixed performance; none is retained yet. Existing buffers and public
API workflow remain unchanged. scripts/finalize_vector_experiment.

## 442d2aa53: composed accumulator overlap, SFB TMA and combine geometry

Pushed and deployed to C1 as 442d2aa53f68b4640c3ab5118a76f1599ff60d34.
C2 remains frozen at 13ca1475 for prior SM103 experiments. Production changes:

- FC1 logical M512/N128 and physical M256/N256 alternate partially overlapping
  accumulator windows, following FlashInfer dense blockscaled/CUTLASS persistent
  GEMM lifetimes. Actual scale columns determine the protected interval. Reverse
  phase-zero slab order releases ownership only after protected accumulator AND
  TMEM transpose-scratch reads. No extra AUTO tactic or model-shape cutoff.
- FC2 route N>=128 loads canonical SFB through TMA, removing fragmented cp.async
  copies and the redundant local/peer completion relay. Existing public layout
  and preparation stay unchanged. N<128 retains its existing path. Explicitly
  typed constant K-block extent preserves the descriptor K axis at extent one;
  removing the type caused an illegal instruction on the MXFP8 K128 exact case.
- Expanded prefill combine chooses 5/6/7 vectors only when that geometry exactly
  divides H and existing four-vector geometry leaves a tail. Existing 16-byte
  alignment and PR7196 ordered FP32 FMA rounding remain unchanged. Aligned shapes
  retain the old geometry. LDG256 and packed arithmetic variants were rejected.

Changed-file pre-commit and commit hooks pass. Read-only accumulator/scale/phase
ownership review found no blockers. Composed snapshots match production AST
apart from imports: 72 paired phase cases and 15 native configurations pass final
byte equality. All raw samples and both three-arm orders are in
scripts/composed_pipeline_experiment; its README preserves full timing rows.
Mixed N256 at16K has substantial intra-run drift (candidate727→800us), so that
row is not a stable isolated speedup claim. Broad numerical/sanitizer checks are
still deferred in favor of performance iteration.

New native AUTO A1 screen completed without rerunning B1. Exact current capability,
tactic and architecture checks: 56 passed, four warnings. Native prewarm loaded
all three candidate extensions from the active cache without a rebuild or epoch
reset. Frozen preparation/timing helpers are unchanged; preflight exempts only
our explicitly authorized measured finalizer file from the old byte-identity
requirement and records its old/new hashes and complete diff.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 | 16K B1→A1 us |
|:---|---:|---:|---:|:---|
| NVFP4 | 1.057669 | 0.956047 | 1.028928 | 472.464→532.351 |
| MXFP8 | 1.094339 | 1.092435 | 1.093820 | 857.874→827.473 |
| MXFP4×MXFP8 | 1.149295 | 1.039251 | 1.118177 | 776.002→816.481 |

All39 rows and78 B1/A1 cache hashes verified, including exact AUTO buckets/history,
helper/environment/source/routing/timing receipts. Evidence:
evidence/combined-screen-442d2aa5. Archive96files,1,565,238bytes,
SHA256 6f4ffcf8bfd00449008b9e2d8cf133ec02d66f726f0825ceb1f447f6c95d48b4.
These are single-screen ratios; no A2/B2 or final ABBA retention claim. NV8K/16K
and mixed16K still trail original B1, so continue profile-directed optimization.
Next isolated axes: FC1 NB2 one-item CLC and FC2 six-warp role assignment.
Current production is frozen while these compile; root re-profiles442d with NCU
and iKET. Existing B1 data remains authoritative and untouched.

## Post442 profiles, rejected axes, and C1 recovery

Current442 NCU + iKET safely archived in scripts/iket442_experiment/results.
On B200 GPU4, NV16K FC1 NB2 NCU270.624us, tensor-active45.95%,80registers/thread;
FC2155.136us,38.45%,110registers. iKET leader accumulator-empty mean1.174us/tile
versus4.328us in13ca, epilogue4.266us versus4.334us. Instrumented waits support
intended overlap but are not additive uninstrumented performance estimates.
All current-profile output/SF bytes exact; full raw trace/report/CSV retained.

- CLC logicalM512 FC1 one-item/full-warp response:82 paired exact cases and54
  native arms exact. FC1 gains~1–2%, full-chain gain inconsistent by order/mode.
  Reject integration; scripts/clc_current_experiment has full raw archive.
- FC2 six-warp map (epi0–3/TMA4/MMA5):120 exact cases and36 native comparisons
  pass. Threads288→192, native registers110→106, static SASS1696→1616, no spills.
  No repeatable chain gain and some8K regressions: reject integration.
  evidence/fc2-roles-442d2aa5/raw.tar.gz SHA256
  2cd5a99209e90187b86d316aca2fae7763feb937560c6b31fe099acbc7b77fe3.

At08:56UTC Oct25, old fi-w4a4-dyn-n-1024 disappeared from c1/ziangli; root's
SF-commit probe terminated137. Its incomplete output was not archived and is
excluded from validation/performance claims. Wider-K prototype sources survived
locally;72 SF-layout cases and3072 ownership checks completed before loss, but
no exact kernel/timing run started. Main A1/39rows,composedresults,allprofiledata,
CLC andFC2role archives were already local. C2fi-w4a4-k96-1025 remains alive13ca.

Requested replacement fi-w4a4-pipeline-1025 c1/ziangli with--bare,8B200,no--size,
explicit nvcr.io/nvidia/pytorch:26.05-py3; ready after37.8s. LiveNGCcatalog and
26.09 release matrix rechecked immediately before request:26.05 remains newest
CUDA13.2,26.06+CUDA13.3+. Request frommanaged/usr/local/bin/h insharedHAIcheckout
becauseCLIrequiresHAIcontext; no sharedsource changes. Bootstrap is isolated in
newprojectdirectory andsource pinned442. DeviceUUIDs will be recorded; original
B1 remains preserved but must not silently pair with a replacementGPU as if it
were same-device retention evidence. No historicalbaseline rerun initiated.

Recovery inventory confirms replacement on B200-83 has exactly the same eight
index/GPU UUID/name/driver rows as the prior442 epoch. CUDA image/Torch match.
Thus hardware has not changed; source/environment/JIT cache epoch is being
restored and explicitly checked before further same-device comparisons. Agent
bootstrap uses verified task-owned WekaFS
/data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025 with the familiar
/workspace path as a symlink. Candidate/baseline have separate native JIT caches.
Future candidate probes source scripts/recovery442/env_candidate.sh; do not
silently default back to another cache. PR7290 body was updated and fetched back
exactly, with source442 and final-retention still pending, no intermediate table.

Recovery completed: exact noneditable package-freeze equality and source/UUID
receipts verified, native routing/FP4/MXFP8 prewarm serially passed, private
candidatecache ready. First pip attempt used Torch's display rather than wheel
version and failed before install; retry used archived wheel metadata. Existing
pip-check DALI packaging/missing PyPI runtime diagnostics are preserved, without
changing original environment. Root/agents released CuTe-only checks while
native prewarm completed, then native timing after all readiness markers.

Early local SF completion before Gather4 is rejected on C2 B300. All72 paired
cases and12 native arms exact. NV8K/16K phase and full-chain medians are neutral
or slightly worse in both three-arm orders. No broader dtype timing or primary
screen justified. Raw source/hashes, both GPU inventories, allsamples andlogs:
scripts/sfcommit442_experiment; archiveevidence/sfcommit-442d2aa5/raw.tar.gz SHA256
 a33f7f8a1074f2ee6f920457a5566e6e363b22dbfa03391b967dd571fb4a46c0.
Production remains442d. Next NVfocused native screens: widerK+protected96 onGPU7,
direct synchronousSF publication onGPU5. Neither has been integrated.

## Wider-K and N192 follow-up decisions

The replacement-environment wider-K run is complete and rejected. NVFP4 K512
with two operand stages and protected96 overlap passes72 SF-layout checks,
3072 ownership states,24 bounded paired exact cases and all18 native arms.
FC1 slows8.65% at8K and10.10% at16K for NB2/N128; N256 slows4.17%.
Full chains slow4.27%,4.99%,2.38%, respectively. No broader dtype matrix or
NCU run follows this clear loss. Source, every sample and resources are in
scripts/wide_k_overlap_experiment; raw archive SHA256
76df1613a0e60d4940874e515d028c3585ff69733e508735271ba17dc2052830.

CPU audit closes another N192 NB2 repeat as low priority. The earlier13ca
N192 probe already used this FC1 geometry. NV K256 needs448 TMEM columns and
208KiB operand shared memory at four stages. Overlap protects320 columns and
can release only after10/12 slabs, versus current N128's2/8. A revival must
also use ceil SFB row-block allocation, revise SF32 staging, and exclude N192
from FC2's aligned canonical-SFB TMA path. No new code or GPU run was needed;
see scripts/n192_doublebank_experiment/AUDIT_442.md.

Direct FC1 SF publication passes the bounded NV tail/per-token checks, but
initial native results trade a roughly2%16K full-chain gain for a2.3–2.6%8K
regression. No production integration or all-format expansion yet. An
immutable follow-up loads SF words before Gather4 and stores/publishes after
it, preserving the same current-stage storage and lifetime contract. A
separate prototype dedicates a new warp to A/SFA TMA issue with exact weighted
transaction counts on the existing operand full barrier. Both remain
diagnostic until adjacent native timings show a repeatable gain.

Both remaining axes are now closed without source integration:

- Direct SF publication and its LDG/Gather4/STS ordering variant retain the
  same8K regression. Split reverse16K candidate/control/candidate is
  516.913/529.617/516.289us, but8K is305.7445/299.025/305.969us. No
  token-specific branch is added. SASS has the intended LDG128 before four
  Gather4 instructions and STS afterward, but a dependent register move still
  stalls before Gather4; native80 registers and zero spills are unchanged.
  Final source/PTX/SASS/exact/native evidence archive includes full SASS and is
  7,454,876bytes, SHA256
  08b614740ecf264f7baf73fe807529d7127f246178689a63575c5087395c9ef7.
- Dedicated A/SFA TMA warp passes12 strict low-level and12 native exact arms,
  with independent barrier/phase/tail review. FC1 gains0.9–1.1% at16K, but
  full-chain gain reverses1.00970x to0.98725x;8K is neutral. Extra warp is
  unjustified. Source compatibility with DSL4.4 helper is verified; GPU
  execution remains4.7.1. All samples and source hashes are in
  scripts/dedicated_weight_tma_experiment, with artifact-manifest.json.

All experimental GPUs are released. Production stays442d2aa53, and the next
step is final A2/B2 using the unchanged savedB1 and442A1. Recovery orchestration
must explicitly verify cache relocation/build-target provenance and separate
arm caches; frozen timing helpers remain byte-identical. Root started baseline
native-module prewarm only onGPU0 with its private cache. This is neither a
timing run nor a repetition ofB1. Baseline prewarm completed successfully and
GPU0 is released. Both private caches now have routing, FP4 and MXFP8 native
modules ready; all six build.ninja files and the full baseline readiness log
are archived under scripts/recovery442/results/baseline-native-readiness.


## Final442 paired campaign and validation; regular-TMA experiment opened

Completed same-device B1→A1→A2→B2 using the unchanged saved B1 and442 A1,
then recovered-environment A2/B2. All156 medians, AUTO cache hashes, source,
software, hardware UUIDs, routing and timing receipts verified. Paired geometric
speedups (decode / prefill / overall): NVFP4 1.056020 / 0.957980 / 1.028327;
MXFP8 1.094150 / 1.092766 / 1.093772; MXFP4×MXFP8 1.151189 / 1.039069 /
1.119463. Token1/2 measured but excluded from all retention aggregates.
NV16K paired0.887188x remains a repeatable regression with about0.5% arm drift;
NV8K is0.9784x. Mixed4K baseline drift-7.69% and mixed16K repeat drift are
reported explicitly. No favorable-repeat selection. Complete39-row table,
all raw samples and verification: evidence/final-campaign-442-recovery.
Archive239files SHA256
30c2a25917a99ea566e2a47fdcaa8856ff33ccc6a49d677813f80e4ec46c37dd.

A prepare-time variable-shadowing error overwrote three B1 digest receipt
fields with GPU inventory text. The three raw B1 files still match immutable
original BASELINES pins; all other nine arm digests were correct. A separate
verification-only adapter checks the exact malformed metadata and all12 raw
hashes before correcting only those three fields in memory. Original malformed
receipt, frozen orchestrator, failure log and correction receipt are retained.
No measurements or raw result data were edited or repeated. Recovery establishes
source/toolchain/target equivalence, not original cubin byte identity.

Focused validation on unchanged442:95 existing tests passed, zero failures,
errors or skips;24 fused cases deselected. Compute Sanitizer2026.1.1.0 memcheck
passed3 reference+12 FC1+24 FC2 cases, racecheck passed12 FC1+24 FC2, with zero
errors/hazards/warnings and no unsupported instrumentation. Optional57 wrapper,
graph and EP cases remain deferred. Numerical archive SHA256
f5582d3968bb13a24b436d11dd90e2df0922b220432f1f1ab8b0ca1e68bd9f32;
sanitizer archive SHA256
6e94b9c7107c2681efc36fc2066ae204172f36666e446de4bdb2801b63ce9bd1.
Evidence and commands: evidence/final442-validation/README.md. PR7290 body now
contains only retained442 results and validation, fetched back and byte-verified
against pr-body.md; receipt pr-paired442-verified.json. Production remains clean442.

User explicitly requested the regular-TMA activation design used by split
W4A16. Immutable prototype scripts/fc1_regular_tma_experiment materializes routed
payload bytes and canonical SF bytes once, then uses regular B/SFB TMA while
preserving FC1 fused activation, accumulator overlap, runtime N and original-token
per-token scale indexing. Existing native moe_permute lacks SF copying, so a
small internal byte-copy preparation kernel is necessary for this experiment.
It writes only active padded rows, final canonical128-row SF padding, and the
bounded extra16 physical B rows needed by logicalN16; unused capacity remains
untouched. Allocations stay outside graphs, preparation runs inside every timed
full chain. Initial12 core NV exact cases and6 prep canary/padding cases passed;
broader core checks and native8K/16K forward/reverse gate are in progress.
No regular-TMA production integration or speedup claim yet.


## Regular-TMA initial gate and source-review workflow

Initial regular-TMA core passes48 exact comparisons across all six supported
operand/SF configurations; preparation passes6 canary/padding/zero-route cases.
The first native fixed N128/NB2 gate includes preparation and matches final
bytes in all12 arms, each with100 cold-L2 graph/CUPTI samples. It regresses:
NV8K ABA controls300.129/301.201us versus regular317.2005us (prep32.032us);
NV16K ABA controls524.1135/524.113us versus regular540.8655us (prep56.048us).
Reverse16K regular534.578/540.289us versus control526.225us. No retention
claim. Complete initial evidence: evidence/regular-tma-first-gate-442/raw.tar.gz,
SHA256 c65c27e9b8aa65882bda2145b5ec9e83344c079b940a03e3a2fc1f57f38dacda.

User requested all active experiment code as unstaged changes in separate
FlashInfer source copies for direct review. Created independent clones at
flashinfer-regular-tma (experiment/regular-tma) and
flashinfer-regular-tma-pipeline (experiment/regular-tma-pipeline), both based
on442 with private project-local .git directories and no staged changes.
Original flashinfer stays clean442. Initial3file source snapshot is frozen
under scripts/fc1_regular_tma_experiment/review_snapshots/initial; later
variants receive separate source hash manifests. Implementation now lives in
actual backend files, including per-invocation preparation allocation and a
real internal host call. Future GPU probes import those source checkouts;
previous runtime interception remains archived historical evidence only.

W4A16 structure audit found two concrete differences worth isolating: its native
permutation uses256 threads and cudaOccupancyMaxActiveBlocksPerMultiprocessor
rather than the prototype's128 threads/four blocks per SM; its GEMM has
independent weight and activation TMA pipelines. The first follow-up screens
4/8/16 producer blocks per SM and native payload-only permutation as an explicitly
incomplete diagnostic. The second variant reuses idle warp1 and inactive
ab_barriers for B/SFB, retaining warp0 for A/SFA with independent ring pacing,
unchanged operand stages, SMEM/TMEM layouts, dynamic N, arithmetic, CTA size,
and PDL placement. CPU/source review passes; GPU evidence remains pending.
W4A16 comparison and independent bounds/lifetime audit are in
scripts/fc1_regular_tma_experiment/W4A16_PIPELINE_COMPARISON.md and
INDEPENDENT_AUDIT.md. Old cache/prefetch/CLC failures are not being repeated.


## Regular-TMA resident-grid and native tactic gates

W4A16-style resident-grid sizing is a useful transfer. Actual preparation
resources are32 registers/thread, zero static SMEM/local bytes, and the CUDA
occupancy API permits16 active128-thread CTAs/SM. Grid4→8→16→16→8→4 prep-only
NV8K medians29.344/20.480/17.728/17.728/20.577/29.408us; NV16K
54.720/35.184/30.0805/30.049/35.296/54.6885us. Existing native payload-only
helper measures13.984/24.321us, but omits SF and padding and is not a candidate.
Actual-source captured prep passes30 replays across SF16/SF32,N16/32/64 and
changing active tile counts0→1→5→2→0, including canaries and physical padding.
Source prep SHA125d0f15910debc75ca1a128c6c59ad83db84558ef66fe338d362371955d4392.
A first phase callback captured a stale stream and failed on an empty graph;
no timings retained. Corrected callback obtains the current stream per launch.
An accidentally duplicated GPU4 native driver was stopped after crossed agent
messages; its incomplete results are preserved and excluded.

Authoritative full-chain diagnostics import actual source checkouts. Observers
are disabled and captured references released before graph capture, preserving
normal invocation-local scratch lifetimes. Each paired arm checks complete
input/weight/routing/final-output byte hashes. GPU5 runs ABBA thenBAAB, four
control and four candidate arms per token,100 cold-L2 graph/CUPTI samples each.

- N128 NB2:8K baseline299.777/299.713/299.809/299.601us versus regular
  302.657/303.1045/302.5445/302.7845us; geometric B/A0.98993448.
  16K baseline521.9695/521.2495/521.986/521.442us versus regular
  508.7695/508.4335/509.282/508.386us; B/A1.02544442. ArchiveSHA
  1f5509c3278161e6e9931d55c637822aec3e17b0a8c699e6a8fa9189e66fe664.
- N256 M256/group2 for both phases:8K baseline328.913/328.801/329.1055/
  328.705us versus regular289.6965/289.6325/289.457/289.633us; B/A1.13562055.
  16K baseline560.514/560.0175/560.5615/560.241us versus regular479.0735/
  478.9775/478.6735/479.089us; B/A1.16991240. ArchiveSHA
  7dd15e058e8fb7313724186f7338dde5db8469ddcc92354aa1e0a560bc607d6a.

Root independently verified both archives, all32 result digests, every100-sample
median and the four geometric ratios. These are fixed-tactic diagnostics, not
AUTO retention results. Grid16 remains unstaged in the review copy. Small-N
decode screening and the independent producer-ring variant are pending; no
primary baseline rerun or production promotion has occurred.


## Regular-TMA decode gate and pipeline closure

The N16 actual-source full-chain diagnostic (ABBA thenBAAB,100samples/arm)
passes complete input/routing/final byte equality for all16arms. T16 control
69.360/69.488/69.536/69.440us versus regular72.864/72.7845/72.736/72.768us,
geometric B/A0.95422137; T512 control156.208/155.9845/156.417/156.4165us
versus regular158.5765/158.672/158.592/158.7845us, B/A0.98487402. Root verified
all archive/result digests,100-sample medians and ratios. ArchiveSHA
48e267284072a64f72a7d16479777a6de12eee02cee7a744a0fc5f8c6cfe2b1a.
These are fixed-tactic diagnostics, not native AUTO retention evidence.

Closed the W4A16-style independent A/SFA and B/SFB producer-ring variant.
N256 regresses0.15–0.79% across both token counts/orders; N1288K regresses
both orders and16K changes sign.20paired exact cases and24native rows
(2400samples) pass. All three changes remain unstaged in the separate
flashinfer-regular-tma-pipeline clone. Evidence:
evidence/regular-tma-pipeline/RESULTS.md;79-file archiveSHA
3b8c0dfb4d66c306ee6fc02e2ebc5aabca1881bec0ab5b426f0f7dc0d9c6b881.

Actual-source MXFP8 and MXFP4xMXFP8 T4/N16 smokes each compare unchanged442
and regular-TMA inputs, weights, routing and final output exactly. FinalSHA
e98fa78d0a20934c146fba4ec0a62d71a8e24765b77c97b89857c1f45b67408e
and c122a2a6cefc97099cfd55131145631867e6929b3f2dea922eba9345b486ca77.
The9files are archived in scripts/fc1_regular_tma_experiment/results/
source-mx-integration-r1. GPU4/5/6/7 work released; all8GPUs verified idle.
The single-pipeline grid16 candidate now proceeds to an explicitly dirty-source
AUTO A1 screen with original B1 reused; no candidate promotion yet.


## Regular-TMA native AUTO A1 screen

Completed all39native AUTO rows using original GPU0 NV and GPU1 MX thenmixed,
unchanged13tokens/preparation/timing loop, original B1 reused. Explicit dirty
source manifest4a3b56e0150b4c76236f6d43d4c205d177c084ea3e286433449c092187aaa077
records442plus exactly3unstagedsourcefiles. Generated adapter full-module ASTs
equal originals after reversing declared provenance edits; original helpers
untouched. CPU preflight and postflight verify source/toolchain/GPU identities,
all original caches and exact environment exceptions. First CPU preflight rejected
Git patch abbreviation differences; full-index patch normalization fixed metadata
only before any timing. No data rerun. Archive: evidence/regular-tma-auto-grid16-A1.
Primary AUTO artifacts preserve39native medians, cache files and logs; they do not
persist individual100timer samples (fixed-tactic diagnostics do).

B1/A1 speedups, decode4..512 / prefill4K,8K,16K / all excluding1,2:
NVFP4 1.052735 /0.985046 /1.033826; MXFP8 1.086995 /1.073196 /1.083214;
mixed1.182668 /1.038259 /1.141401. Versus geometric mean of retained442A1/A2,
nonadjacent diagnostic ratios are NV0.996594 /1.030752 /1.005796,
MX0.993694 /0.980123 /0.989975, mixed1.029108 /0.991992 /1.018850.
These are not completed ABBA candidate retention results.

NV16K AUTO selectsN256/M256 instead of oldN128/M512FC1, improving
532.351/535.327us to486.639us, while originalB1 is472.4635us. NV8K staysN128
and is306.4955us. MX8K staysN128 and measures492.481us versus442478.288/466.721;
mixed16K staysN128 and measures823.6335us versus442816.481/780.353. Prior
mixed drift is material; do not attribute full geometric delta to preparation.
Keep regular-TMA experimental: no universal improvement proven, noA2/B2 yet,
no production commit/push or PRbodyperformancechange. Follow-ups isolate actual
MX16K preparation cost, coalesced SF tile preparation, and256bit payload copies.
Every in-progress source variant remains unstaged in its own independent clone.


## Regular-TMA256bit payload and closed SF transpose

Separate flashinfer-regular-tma-ldg256 copy changes only prep payload vectors
128→256bits and enforces32B pointer/row alignment; SF, grid and PDL unchanged.
SASS confirms LDG.E.ENL2.256/STG.E.ENL2.256,28–32regs,0SMEM/local and16active
128threadCTAs/SM.40graph byte/canary checks and3native-route pairs pass.
Prep-only ABA/BAB ratios control/new: NV8KN1281.0472, NV16KN2561.0455,
MX16KN2561.0525;18arms/1800samples preserved. ArchiveSHA
99a85b843e7908e8ce16804b2065447cf142ce213bcd97db5f055798165e94ab.

Full39rowAUTO A1 for the actual LDG256 source also completed, manifest
a01a877f14915a0b1aa442d71005fb62fc5a20beab852082cc6c4fb4530002cf,
original observer/timing unchanged. A failed oversized argv transfer wrote no
source or result; named files then transferred through a dedicated staging
directory and CPU preflight passed before timing. No benchmark retry.
B1/A1 decode/prefill/overall: NV1.054225/0.988353/1.035836;
MX1.094294/1.070204/1.087671; mixed1.192768/1.045759/1.150739.
Versus earlier regular grid16 A1 overall:1.001944/1.004115/1.008181.
MX8K latency492.481→503.057us also changes AUTO FC2M256/2CTA→M128/1CTA;
this is not a copy-width-only measurement. Other prefill tactics unchanged.
Allrawmedians/caches/logs/source in evidence/regular-tma-auto-ldg256-A1;
archiveSHAf8036cb7e803cf09562739f468e3512f76ae50fcdc401a552c5250e87805de9d.
NoA2/B2, productionpromotion or PRperformanceupdate.

Closed tiled-SF preparation:128row×32word tile with33word paddedSMEM pitch
passes72CPUcases and31unique graph checks, but is2.67–2.69x slowerNV8K,
1.83–1.85x slowerNV16K and3.12x slowerMX16K in bothorders. Each timingrow
passes its own byteoracle; fresh native moe_sort within-expert permutations
differ across processes, so this is not a fixed-permutation comparison.
Nofullchain/profiler/sanitizer follow-up justified. Copyremainsunstaged at
flashinfer-regular-tma-sf-tile.52-file archiveSHA
99a77b0d1e4a4bafbc5e4397a935d285ef59ed331ff58f9e935decdfd5f7b7e5.

Selected actualAUTO16K prep costs49.312us MXFP8N256 and47.088us mixedN128,
with independent byte references and canaries; evidence/regular-tma-selected-prep-442.
These GPU4phase costs cannot be directly subtracted from GPU1fullchain timings.
Next minimal W4A16 structural transfer is skipping invalid payload-row stores:
source audit finds no cross-N reduction; preserve physicalcapacity/SFwrites,
and prove arbitrary invalidFP8NaN/Inf bytes cannot affect validoutputs before
considering any retention. This remains an isolated experiment.


## Valid-route payload preparation and review candidate

W4A16 native preparation skips invalid payload rows. The corresponding isolated
blockscaled change preserves complete canonical SF padding, physical allocation
extents, descriptors, routing, PDL and all arithmetic. Invalid N columns remain
independent through MMA, activation and per-token quantization, then are masked
from outputs; zero SF bytes alone are not the safety argument. The physical
payload tail may remain uninitialized, so this does not claim initcheck coverage.

126 exact checks pass:90 changing-count/partial-tile preparation graph cases and
36 paired FC1/quantizer/FC2/combine cases across all six formats, including per-token
paths and poisoned invalid payload bytes. Prep-only ABA/BAB improves NV8K1.05383x,
NV16K1.06549x and MX16K1.10372x over LDG256;18arms/1800samples. Evidence:
evidence/prep-validcopy-442/, archiveSHA
b6471567e582140b85bba471fcce92aec0531b2ce4c156293c57a380db484b95.

All39 native AUTO validcopy A1 rows are complete, with unchanged original B1.
Decode/prefill/overall B1/A1: NV1.052042/0.995661/1.036356;
MX1.093515/1.118225/1.100199; mixed1.186884/1.047180/1.147032.
1/2 tokens remain measured and excluded from aggregates. Overall versus LDG256
is1.000502/1.011518/0.996779, a nonadjacent diagnostic. MX8K503.057→450.6565us
also changes AUTO from N128 to N256/two-CTA both phases; do not attribute the
full delta to the valid-row predicate. NV16K482.799us remains slower than
original B1472.4635 but faster than retained442532.351/535.327. Mixed16K825.2495
still regresses original B1776.002 and has material historical drift. No universal
win or final retention claim. Evidence: evidence/regular-tma-auto-validcopy-A1/;
60-file archiveSHAc87f88e262815895641244e03dfb5c5306486e19ef93492af1bc3cdfaed07317.
All234 cache hashes across B1/current/previous screens and442A1/A2 verified.

Read-only AUTO routing audit: existing tuner uses cold L2. Its balanced synthetic
max-load profile creates many more tiny tail tiles than native routed data at8K
(96 versus77 N128 tiles;64 versus45 N256 tiles). This can bias tactic preferences,
but both screens use the same profile, so it alone cannot explain a winner flip.
Winner-only caches contain no per-tactic margins. No tuning or benchmark policy
changes made. Artifacts: scripts/auto_routing_profile_audit/. Their relocation
left all15 frozen adapter files byte-identical.

New independent flashinfer-regular-tma-review keeps exactly3 unstaged files.
Removed10 statically false Gather4 branches,2 ternaries, the false attribute and
an unreferenced helper. Documentation/license/formatting updated. Full-module
ASTs match validcopy after precisely named constant pruning, helper removal and
docstring stripping; no live expression or operation reordering. Changed-file
precommit passes. This is a CPU proof, not a GPU/codegen identity claim. Manifest
9f174d224c41b18fd59f51deb360464f70654724ed1acf91d38aa1a55fe1e1f2 freezes11665
source hashes. Final paired campaign will use fresh cleanup-source A1/A2/B2,
immutable original B1, all13tokens and native AUTO. Retained442 and PRbody remain
unchanged until this campaign and validation support promotion.


## Retained98fd3566b: regular FC1 activation TMA

Completed fresh cleaned-source A1/A2/B2, original B1 reused and unchanged.
Full156 medians and156 AUTO-cache hashes verified, with global arm chronology,
source/toolchain/GPU/software/preparation pins. Paired decode/prefill/overall:
NV1.0514578/0.9959983/1.0360333; MX1.0954354/1.0945841/1.0952032;
mixed1.1875449/1.0594400/1.1511448. NV8K/16K remain0.983506/0.979423x.
MX16K B2/B1=1.113210 and mixed16K=1.106247 include baseline AUTO tactic changes;
do not attribute those changes entirely to new kernels. Every median and winner
is retained in evidence/regular-tma-final-review/. Raw archiveSHA
5794c0ecbb6897e39ec01e2294c4912376abf72afb5ec1edb0986fcae941838f.

B2 wrapper v1 stopped at a CPU symlink-path check before creating any B2 result
or starting GPU work. Preserved it and its log; v2 resolves only repository paths
and retains relative receipt paths, matching the frozen candidate verifier.
Actual A1/A2 were not rerun. The archive first attempt lacked an optional remote
CPU-proof directory; archive v2 includes the mandatory local proof separately.
Neither artifact correction changes source, timing helpers or recorded data.

Focused126 exact checks pass on the cleaned source. Post-performance validation:
95 existing tests,126 probe cases under memcheck,126 under racecheck, and three
existing references under memcheck; all processes exit0 with zero errors/hazards
and no sanitizer warnings/unsupported diagnostics. Initcheck not run; invalid
private payload remains uninitialized and masked from outputs. ArchiveSHA
3efcd8791ce8f24d4a98591d92393046f0da9b375904f93f42d0ac8930a3090d.

Retained commit98fd3566b5f945c100f48cddacf25deb2432cbc2 matches all three measured
kernel/host/prep file hashes exactly. A fourth file only updates three public
wrapper docstrings; independent full-module AST proof excludes executable changes.
All four changed files pass precommit; commit hooks also pass. The frozen review
copy and all older experimental clones remain unstaged. New user steering focuses
packedFP32 arithmetic and efficient vectorization in non-TMA paths; do not replace
workingTMA. Existing GEMM epilogue activation/scaling already uses f32x2. Input
prep payload uses verifiedLDG/STG256. New work audits combine conversion overhead
and SF source vector widths while retaining canonicalSFstores and public workflow.


## Closed: raw-pair packed FP32 combine

The independent `flashinfer-packed-combine-review/` copy remains unstaged.
This variant replaces BF16-pair expansion/conversion with Uint32 shift/mask,
packed RN FP32 multiply/FMA and BF16-pair conversion. It preserves existing
128-bit loads/stores,16-byte alignment, slot0 multiply then ordered valid-slot
FMAs, launch geometry and all regular-TMA source files. No LDG256 or TMA change.

All102 direct exact cases and post-timing native bytes pass. Actual native NVFP4
combine-only ABA/BAB at128/8192/16384 retains18arms/1800 cold-L2 CUDA-graph CUPTI
samples,10 warmups and100 samples per arm. Each process shares captured inputs
across its arms; separate ABA/BAB captures need not have identical permutations.
Raw medians in microseconds:

| Tokens | Control / variant / control | Variant / control / variant |
|---:|---:|---:|
|128|4.224 /4.208 /4.192|4.192 /4.192 /4.160|
|8192|44.864 /44.736 /44.816|44.7845 /44.8955 /44.800|
|16384|83.072 /82.912 /83.1355|82.976 /83.072 /82.960|

**Not retained:** prefill savings are only0.13–0.23%, below0.25µs. SASS confirms
scalar FP32 multiply/FMA56/392 become packed28/196, PRMT224 becomes0, while
128-bit loads/stores56/7 and80 registers stay unchanged, with no local memory
or spills. This is consistent with prior memory-bound evidence, not a new NCU
causal attribution. No whole-MoE timing or integration was performed.

[Final interpretation](scripts/packed_combine_review/README.md) and
[derived receipt](scripts/packed_combine_review/conclusion.json).
Control finalize SHA256
`0b043869056d7e1d8bd3a7c35d9ab33ebb632e65c410626cdebaf5d2784dd8cf`;
variant finalize SHA256
`99eb59d0045bcd09f43c8473bdee303368e914b71a514299460be8d9c44887ee`.
Archive `evidence/packed-combine-review/raw.tar.gz` SHA256
`233655f8bab74530623db553a21c151fbec6d14809828f298cb9a8f3000542f6`.

## Closed: regular-TMA preparation SF source vectorization

The independent `flashinfer-regular-tma-sf-vector-review/` copy remains unstaged.
Only SF source loading changes: a generic static policy selects complete Uint32
widths1/2/4/8 using estimated warp memory-instruction cost. Payload LDG/STG256,
canonical SF scatter/padding, workspace lifetime, per-token scales, PDL and
regular-TMA GEMMs remain unchanged. Wide cases explicitly require8/16/32-byte
SF alignment instead of the cleaned prep's4-byte allowance; this rejected
experiment does not promote that contract restriction.

CPU checks cover512 SF-block extents and exact destination partitioning. All107
GPU checks pass (75 preparation graph/byte/canary cases and32 alignment cases).
Whole prepared payload/SF allocations match control in each actual-routing
native case. Prep-only ABA then BAB uses10 warmups/100 cold-L2 CUDA-graph CUPTI
samples per arm,18arms/1800 samples retained. Ratios divide geometric means of
all three control and three vector medians:

| Case | Control medians, µs | Vector medians, µs | Control/vector |
|---|---|---|---:|
|NVFP4 8K, N128|15.968 /15.9675 /15.984|16.544 /16.5285 /16.544|0.965798×|
|NVFP4 16K, N256|29.616 /29.632 /29.744|30.816 /30.864 /30.800|0.962282×|
|MXFP8 16K, N256|42.528 /42.3845 /42.3685|43.248 /43.312 /43.1365|0.981376×|

**Rejected:** all three cases regress in both orders. Measured NV SF loads are
LDG128 plus four scattered32-bit stores; MX uses LDG64 plus two. A compile-only
width8 inspection confirms LDG256 plus eight stores; width8 bytes are covered by
the exact probe, but its inspection kernel was not launched/timed. Registers
remain30 for NV8K and32 for the other cases;16 resident128-thread CTAs/SM,
zero static SMEM/local bytes and no LDL/STL spills. Fewer active SF warps and
longer serial scatter chains are consistent with the slowdown; no NCU causal
claim. No primary campaign or whole-MoE timing was run.

[Final summary](evidence/prep-sf-vector-review/summary.md) and
[experiment contract](scripts/prep_sf_vector_experiment/README.md).
Control prep SHA256
`ec2c70b178f828b769ab7d63128996bed8535f23f099591e1a5c046392bc292c`;
variant prep SHA256
`19d29ab7dd421064c5de3d4d0858f8a9dd831cf07c91811fb6b32f0980ebe0f0`.
Archive `evidence/prep-sf-vector-review/raw.tar.gz` SHA256
`d3cbf935c61b3a44d8bcab2eec8ff97b268b40dead59bb6011716c7d5daa96d7`.


## Native TRTLLM reference and decode target

Completed two native non-distributed TRTLLM NVFP4 sweeps on original GPU0,
clean98fd, same image/software and13-token methodology. Reused completed CuTe
A1/A2 without rerunning existing data. Independently verified all52 medians,
52cache hashes and original CuTe record bytes. CuTe speedups vsTRTLLM are
decode0.9923095662, prefill1.1709543387, overall1.038136117;1/2 excluded.
These are later backend reference sweeps, not interleaved retention arms.
Native TRTLLM finalize/global-scale preparation and8192-token AUTO cap remain
unchanged; common input-routing histograms do not prove internal-route or
cross-backend numerical identity. Native setup/JIT is outside timing.

Evidence: evidence/trtllm-nvfp4-reference-98fd/; archiveSHA
5612b789e5980c1f593bf87737552ae482c83763ee2b037a5ce527713e0207f8.
PR7290 body updated and verified at unchanged98fd; bodySHA
ff7a265eb9a0b30ae3d80ee578c343454bdfdc3b5314e303eb7e129cc15e5227.
Only final retained performance is public; experiment details remain local.

User steering: NVFP4 target is stably faster than TRTLLM for decode. Inspect
matching current native cubins and published/unmerged Gen source PR2917
(head64ed071e23bf8d5d2d5af5c91577e5b8e036a1cf), without claiming older source
byte-identical to current8ee504... cubins. Current decode phase profiling and
source/cubin audit are independent of primary retention; no original baselines
are rerun. Six-warp FC1 prefill is bounded and lower priority.

## Closed: regular-TMA FC1 six-warp roles

Independent `flashinfer-fc1-tma-roles-review/` at98fd keeps one unstaged core delta.
Only FC1 with TMA SFB and overlapped epilogue uses192 threads: physical epilogue
warps0–3, TMA4, MMA5. FC2 and small-N/inline FC1 remain unchanged. Exact reverse
source/AST proof and all eight static role cases pass; MMA/TMEM ownership,
deallocation, pipeline transactions and PDL tail remain byte-identical.

Native FC1-wrapper (including unchanged routed preparation) ABA/BAB on GPU3
passes output/SF bytes before/after all12arms, retaining1200 cold-L2 graph/CUPTI
samples. NV8K/N128 control/compact geometric ratio0.998855; NV16K/N2561.001068.
No meaningful gain, so no MX extension, whole-chain timing or primary campaign.
Requested environment dumps did not yield PTX/CUBIN artifacts in these
processes; no emitted-resource claim. The actual-source copy remains unstaged.
[Raw medians and boundaries](scripts/fc1_tma_roles_experiment/README.md).
Archive `evidence/fc1-tma-roles-98fd/raw.tar.gz` SHA256
`cb0ec1e10dd23bdc9780530693562474f61a10403bf0dfafb57f0978374ad5e0`.

## Closed: descriptor-only one-CTA N8

Actual98fd source copy `flashinfer-dynamic-n8-review` changes only dynamic
MMA descriptor rounding: group1N8, group2unchangedN16. Allocation and
epilogue remain unchanged. GPU2 native fixedN16 ABA/BAB, tokens4/32/128/512,
whole-chain plusFC1/FC2:72exact arms,7200 cold-L2 graph/CUPTI samples.
Whole-chain control/variant ratios1.000004/1.000954/1.002535/0.999228.
No consistent gain; not retained, no primary rerun or broad validation.
Raw source/logs/samples and fullmedians: evidence/dynamic-n8-98fd/.
ArchiveSHA2f71ef964a9ae7010b503313e409171a576cd41e03094b83e4ec01d16c9b74e5.
Actual source remains unstaged. Narrow epilogue remains a separate opportunity.

## Closed: physical B16 and five stages

Separate `flashinfer-small-b-review` at98fd keeps accumulatorN32/epilogue
unchanged, but uses physicalB16 for routeN16 and five operand stages.
GPU2 native NV fixedN16 ABA/BAB, tokens32/128, full/FC1/FC2:36exactarms,
3600 cold-L2 graph/CUPTI samples. Whole-chain control/variant0.991981/0.992374;
FC1 0.986372/0.993628;FC2 0.969621/0.982291. Coupledchange rejected;
no claim B16alone is slower. No primary or broadvalidation rerun.
Actual source remains unstaged. Evidence: evidence/small-b-stage5-98fd/.
ArchiveSHAb43eb680d690f67c1c9efc4ce4e8bac872dfce3b03b656ef99d53fce42ea47e1.

## Closed: small-N K8/two-stage dual residency

Independent unstaged `flashinfer-small-n-occupancy-review/` at98fd uses2 operand
stages,2xSM persistent grid and minblocks2 for existingoneCTA K8 N16/32/64.
Initial stage2-only compile gate stopped at driveroccupancy1 despite99,200B
SMEM/128TMEMcols/64regs. Source/SASS establishes TMEM's initial virtual-resource
reservation128 equals the SMpool; supported early permit release emits
UVIRTCOUNT.DEALLOC.SMPOOL128 before mainloop. Actualnative NCU confirms1.88/1.93
mean residentCTAs and16.87/17.24activewarps forFC1/FC2, while initialdriver
occupancy still reports1. No cubinmetadata edits; allownership/free barriers remain.

Nativefixedtactic ABAB T32/T128×N16/N32 passes bothphase+fullfinalbytes,16arms,
1600cold-L2graph/CUPTI samples. Everyfullchain case loses1.56–3.49%. Reject; no
T4/T512/otherformat/primary extension. All8 rawcompilecubins/PTX/SASS, NCU,
failed admission logs and every sample are preserved; no broadvalidation.
[Full medians and resource distinction](scripts/small_n_occupancy_experiment/README.md).
ArchiveSHA `bc4e246772f73ca75b948fed11b32ccca7d815c06ebf69ee02f39f6f6a36f6ff`.
The subsequentK4/four-stage follow-up is independent and keeps this frozen.

## Closed: small-N K4/four-stage dual-residency follow-up

Independent unstaged `flashinfer-small-n-k4-occupancy-review/` preserves the
supported early TMEM permit release and2xSMgrid, uses K4/fourstages instead
ofK8/two, and explicitly retains EVICT_FIRST caching. OnlyNV T32/N16 gated:
99,200B SMEM,128TMEMcols,64/91compiledregs, zero local; phase/SF/fullfinal
bytes exact. Fullchain ABAB105.8245/110.1130/105.9680/110.1440µs yields
control/candidate0.961570 (3.997% slower),4arms/400samples. Close family, no
T128reverse/NCU/broadformats/primary campaign. [Raw result and scope](scripts/small_n_k4_occupancy_experiment/README.md).
ArchiveSHA `76e2645f4d262d66cd530c24f3725dbc8847f1501e43a96b32be6123b6af15b3`.

## Closed: small-N FC1 original linear SF

Independent unstaged `flashinfer-small-n-linear-sf-review/` at98fd keeps prepared
payload and regular B TMA; only FC1 N16/32/64 skips canonicalSF preparation and
uses existing cp.async to gather original linearSF through route mapping. The
mapping is hoisted before the K loop, original-token extent/per-token scales
preserved, and FC2/N>=128 unchanged. Initial5NV cases coverK64/384, per-token
off/on, invalid mapping, originalSF guards and zero routes, all byte-exact.

NativeT32/N16 ABA/BAB fullchain control105.4725/105.5205/105.4405µs versus
candidate105.8080/105.6805/105.6010µs gives0.997931 control/candidate
(0.207%slower). All6arms inputs/routing/finalbytes match;600cold-L2graph/CUPTI
samples retained. Reject without broader formats/primary rerun. Source remains
unstaged; naturally aligned input boundary and required4-byte pointer annotation
fix if revisited are explicit in [the experiment note](scripts/small_n_linear_sf_experiment/README.md).
ArchiveSHA `a6f287696aa829c51b4f28d8e2e5fb9433e5a88314f97bd0e84a8cfa24b22f6a`.

### Separate SF publisher, retained98fd, B200-92 GPU3 — rejected

- Actual unstaged `flashinfer-sf-publisher-review`; one added publisher warp,
  two disjoint TMEM SF slots and explicit CP/MMA completion barriers.
- Seven paired NVFP4 FC1 cases exact, including K64/384/1216, per-token BF16 and
  zero routes. Native N16 T32/T128 full-chain+both phases exact before/after;
  36arms,3600 cold-L2 graph/CUPTI samples retained.
- Full-chain control/candidate ratios0.992344/0.991810; FC1 0.992924/0.999285;
  FC2 0.992211/0.991837. Reject; no broad validation or production change.
- [Mechanism and boundaries](scripts/sf_publisher_experiment/README.md),
  [summary](evidence/sf-publisher-98fd/summary.json). Raw archive SHA256
  `efd0e1839dc23ac6e66822f7812ce136771778b751c0f306978aabaa0e719b64`.
- Current PTX clarifies inter-warp operations are non-pipelined; old13.2.2 wording
  was broader. Completion-based full/empty arrivals deliberately used. A compact
  SFB layout plus physicalN16 is a distinct authorized follow-up, not this result.

### Compact SFB broadcast + physicalN16 publisher,98fd — unretained schedule

- Fresh actual unstaged `flashinfer-compact-sf-broadcast-review`, NVFP4
  generated-FP4 gatedFC1N16 only. TrueB/C16 + twoSFslots + onepublisher320threads.
  Four packed512B SFBatoms broadcast128 TMEMlanes; MMA SFBstride2. Independent
  CPU lane/column proof, seven paired exact cases pass.
- Verified codegen:12CPwarpx4 perKstage(8SFA+4SFB), SFBstage2048B,
  SharedStorage172928B,46registers,0localmemory,128TMEMcolumns,1CTA/SM.
- T32/T128 full-chain control/candidate ratios0.994396/0.995735; FC1
  0.995544/1.000531; unchangedFC2 1.000760/0.999555.36arms/3600samples exact.
  No broadvalidation or primary rerun. Preserve all unstaged sourcecopies.
- This still waits jointA+SFA+B readiness beforepublishing; scalesourcesrelease
  afterMMA. Next coordinated design must decouple SFA readiness from payload,
  not infer that asynchronousSFpublication generally cannot help.
- [Mechanism/results](scripts/compact_sf_broadcast_experiment/README.md),
  [rawsummary](evidence/compact-sf-broadcast-98fd/summary.json), archive SHA256
  `d2694fea36e1e4aef365cd7f3034be5ad239c47ec05b8a513c6701bd3152e5c9`.
  Four-publisher512B STTM draft was preserved but never launched.

### Independent SF readiness + compact SFB + concurrent payload issue — unretained

- Fresh actual unstaged `flashinfer-sf-readiness-review`, core0f570a27. A/B
  independently announce32768/4096B to a two-arrival payload barrier; SFA4096B
  uses its own readiness barrier. Publisher waits only SFA/SFB and releases
  their shared source ring through CP completion, while MMA retains payload
  and TMEM SF until final use. Four source stages/two TMEM SF slots unchanged.
- Seven exact cases pass against the reused control oracle. Native T32/T128
  full-chain control/candidate0.994690/0.994124; FC1 0.995486/0.994513; unchanged
  FC2 1.000298/1.000002. All36 arms/3600 cold-L2 graph/CUPTI samples retained.
- Actual320threads/50regs/173056B SMEM/128TMEM, no local memory,1CTA/SM.
  No gain for this schedule; reducing publisher/producer coordination remains
  distinct from rejecting concurrent TMA or independently ready scales.
- [Design/results](scripts/sf_readiness_experiment/README.md),
  [complete summary](evidence/sf-readiness-98fd/summary.json). Archive SHA256
  `26d0edd6457485c99154c03934a361912b884f51257775759d0551bb213ac358`.
  No production changes, primary reruns or broad validation; source preserved.

### Readiness pipeline NCU diagnostic — coordination remains material

Actual-source FC1T128/N16 onB200-92GPU3, identical native input fingerprints
and initialized output/SF, exactbefore/after. Useful TMA/MMA counts unchanged;
DRAM497.378→497.325MB. CompactSF/physicalN16 reduces CP25%, LDGSTS50%, TMEM
loads26880→7680, yet total warp instructions rise16.17% and branch count
304195→643155. Barrier/wait ratios rise; long-scoreboard ratio slightly falls.
This supports reducing coordination work, not rejecting concurrent TMA or
attributing added branches to one role without PC-level evidence.
NCU replay77.472→79.296µs is diagnostic, not a benchmark median.
[Full metrics and source guards](scripts/sf_readiness_profile/README.md).
ArchiveSHA `8cd117f370e94ed35670be7eb2b53f0bf4023dd504fa22ddaafc34f1ef5a250a`.

### One-CTA SF proxy-ordering repair — correctness fix, measured small cost

- Actual unstaged `flashinfer-sf-proxy-fence-review`, four added lines only;
  core `7c0fe69f` versus retained `98fd3566`. The explicit async shared proxy
  fence follows non-bulk SF completion and precedes TCGEN shared reads. Existing
  group-two fencing and TMA SFB branches are unchanged. No observed numerical
  corruption is claimed; the installed CuTe wait has no implicit proxy fence.
- All 31 focused cases pass byte-exactly: seven reused NVFP4 oracle cases plus
  24 new paired cases covering six formats, FC1/FC2 and per-token/per-route
  scaling. Source/input guards and invalid rows remain intact.
- Same native fixed-N16 T32/T128 paired ABA/BAB methodology, 36 arms and 3600
  samples. Full-chain repair costs are +0.675% and +0.579%; FC1 +0.233%/-0.041%,
  FC2 +0.361%/+0.656%. This is an ordering repair, not an optimization gain.
- PTX proves full completion wait at1125 → proxy fence1131 → first TCGEN
  copy1150. Resources stay 64 registers, 197504 B dynamic SMEM, 288 threads,
  128 TMEM columns and zero local bytes. No primary campaign or broad
  sanitizer rerun; previous full-grid/TRTLLM results remain measured98fd data.
- [Exact scope, all medians and commands](scripts/sf_proxy_fence_experiment/README.md),
  [summary](evidence/sf-proxy-fence-98fd/summary.json),
  [codegen proof](evidence/sf-proxy-fence-98fd/ptx-ordering-proof.json).
  Raw archive SHA256
  `1fceb4bc6c19af9e8f92838e880ad8d7df957e9aae3ceaa80382ea360d8d7f52`.
  Parent owns promotion; no production edits or pushes by the experiment task.
