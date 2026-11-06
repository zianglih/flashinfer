# FlashInfer NVFP4 W4A16 MegaMoE

## 2026-09-17 implementation cleanup

Current PR head: `fc676ce6`, following production cleanup `455183f5`. An audit against existing CuTe MegaMoE patterns removes 86 production lines: duplicate export bookkeeping, two forwarding wrappers, unused internal kernel arguments and duplicate aliases. The requested drop facade now adds 17 lines versus 53 before cleanup. No preexisting upstream code is deleted. A separate test commit avoids 348.05 MiB of unused expert-weight allocations per rank in the large routing fixture while retaining its seed and oracle.

Whole-PR scoped hooks pass. Local checks verify 105 exports, 34 lazy routes, 141 caller imports, 14 autotune control-flow cases, 12 exact CPU routing-input comparisons, and constructor-state equivalence. All 18 non-constructor kernel method bodies are AST-identical; public controls, schedules and fences remain unchanged. These are host/source checks with explicit CUDA/transport mocks, not native GPU validation. Published timing remains measured `1098a348`. [Full audit and evidence](pr-scope-cleanup-20260917/README.md).

## 2026-09-17 review follow-up and test scope cleanup

Current PR head: `45c1034b`, following host correctness commit `b4015a81`. Autotuning now uses the configured EP process group throughout, preserving six untimed graph replays and MAX of rank medians; rank-local errors abort instead of attempting unsafe score-and-continue recovery. The existing final-release hook invalidates only workspace-bound staging views while retaining compiled stagers. Combine-output validation checks CUDA BF16 metadata. The NVSHMEM requirement row includes this backend. The originally DeepGEMM-only validation file is restored exactly to upstream in its own commit, removing54 net lines while preserving six CuTe test files.

The proposed extra TMEM fence was rejected after PTX/dependency and emitted-code review: true same-thread register dependencies protect consumption, and existing waits protect accumulator release. No device fence, barrier, pipeline or launch/compiler/reducer/staging operation changed. Full-PR scoped hooks pass. Host checks:14 autotune/backend,9 staging lifetime,8 combine metadata; a real four-process Gloo subgroup[2,3] check passes while[0,1] stays outside tuning. CUDA work is mocked in these host checks; no fresh native subgroup, sanitizer or GPU timing claim. Measured1–8192 performance remains tied to `1098a348` below.

Five concise replies were posted to CodeRabbit findings with fixes or the PTX rationale; no human-reviewer reply was posted. The PR body retains the full three-way performance table and records the final host-only validation boundary. [Review evidence and receipts](review-followup-20260917/README.md). No GPU/devbox remains owned by this follow-up.

## 2026-09-17 alpha API, optional reduction and performance audit

PR5019 is pushed at `1098a348a1b2a4457cafba4e5263609451914043`. Separate commits tighten architecture documentation (`b546b4ee`), add optional in-kernel FC2 reduction (`576904a8`) and reuse the W4A4 alpha API (`1098a348`). Prepared weights are `(weight, scale)` pairs; `fc1_alpha`/`fc2_alpha` replace the bespoke global-scale fields and capability guard. Four shared production files return byte-for-byte to merged upstream. Default external FP32 weighted combine remains deterministic; opt-in IKR rounds weighted terms to BF16 and uses nondeterministic BF16 bulk reduction. The whole architecture-doc PR diff is five added lines.

Validation on B300/CUDA13.2: 58 host passes, one optional DeepGEMM skip; 30 single-GPU passes; 15 passes on each EP2 rank. Whole-PR scoped pre-commit and five benchmark host checks pass. All 14 token counts from 1 through 8192 were benchmarked with four native AUTO tactics and 100 cold-L2 CUPTI graph samples per row. Over8–8192, final performance is **0.999521×** versus same-node post-merge `4bc27889`, and **1.005964×** versus the saved pre-merge `4d183b83` on another B300 node. All 14 paired tactics,112 paired output hashes and three retained default-path CUBINs match. This supports consistent default-path performance; cross-node/temporal variation and capture scope remain explicit. Runtime alpha copies and IKR are not performance claims here.

[Implementation and validation](ikr-support-20260917/README.md) · [full three-way performance table](ikr-support-20260917/benchmark/collected/results-001/historical-comparison.md) · [independent audit](ikr-support-20260917/benchmark/independent-results-audit.json). All artifacts are local. The owned devbox `fi-mega-ikr-0917` was released after collection; [receipt](ikr-support-20260917/gpu-setup/release-receipt.json). No HashInfer update or reviewer comment was made. Older entries below are historical snapshots.

## 2026-09-17 upstream/API refresh

PR5019 is at `4bc27889`: upstream merge `a22dfb73`, separate BF16 interface audit `0701a11a`, and mechanical `bf16_nvfp4` naming `4bc27889`. The public helper is now `preprocess_bf16_nvfp4_cutedsl_mega_weights`, the maintained package is `flashinfer.moe_ep.cute_dsl.megamoe.bf16_nvfp4`, and the cache uses `bf16_nvfp4`; the public config/backend name already matched this convention. Device kernels are unchanged. HashInfer synchronization is deferred. No new GPU/performance results are claimed. Details: [upstream merge/API audit](upstream-merge-audit-20260917/README.md).


## CUDA 13.0 table refreshed — 2026-09-14

[PR #5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) now includes a fresh complete 1–8192 CUDA13.0 table at unchanged head `7f1a093119f12b1f5b79d50bf6d0c951069224e5`. On eight B300 GPUs (C2/node87/image `nvcr.io/nvidia/pytorch:25.11-py3`), the actual DSL4.7.1 cu12/compiler12.9 fallback passes6 exact decoder,8 EP1 and6 EP2 cases per rank. Full autotune/CUPTI results verify2800 samples and112 collective Mega selections: GM8–8192 **1.1245×**, **11/11** rows faster; all14 rows retained. Source and native closure pass, with no code changes. The CUDA13.2 table is unchanged, and the PR remains ready for review. Devbox `fi-w4a16-cu130-0914` remains available in C2/infra. [Full evidence, raw table and commands](cu130-refresh-20260914/README.md).

## Final audit complete; ready for review — 2026-09-14

[PR #5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) is now ready for review at `7f1a093119f12b1f5b79d50bf6d0c951069224e5`, verified live. Final independent kernel/interface review and tests/benchmark/docs/evidence audit found no blocking issue. No code changed; performance tables remain intact. GitHub docs and pre-commit pass. Upstream GPU CI still requires authorization (its summary is red because execution was skipped); this is stated in the PR body. [Final audit evidence](final-review-20260914/README.md).

## Interface refactor and focused documentation — 2026-09-14

Current head: `7f1a093119f12b1f5b79d50bf6d0c951069224e5`. Interface fixes (`b83cbedb`) and the requested separate test/documentation cleanup (`2c451c73`) are followed by a documentation-only commit that removes the standalone W4A16 architecture walkthrough (net −79 lines). Shared sections retain only the global-scale and FP32 combine exceptions, plus BF16 input-copy behavior. Fresh CUDA 13.2/B300 validation at 2c passes 88 contract tests (one optional DeepGEMM skip), seven knob/capture cases and one positive graph test; five staging cases pass at byte-identical b83 staging source. Scoped hooks pass. The final doc edit does not change tested code. Kernel code, tactics/default values and the complete PR performance tables are unchanged; no performance rerun is claimed. See [full evidence and commands](interface-refactor-20260914/README.md).

## Focused test cleanup — 2026-09-14

Current head: `45fa27dd591f27d79d43423fe5af0fc389c9cfd4`, a test-only follow-up to the squashed/rebased implementation. The PR now changes seven test files (+834/−155), down from eight (+965/−178): 154 fewer changed lines. Core numerical oracles/tolerances and all production code are unchanged. Scope, retained coverage, checks and publication readback are in [test-cleanup-20260914](test-cleanup-20260914/README.md). Scoped hooks/syntax and independent review pass; GPU tests were not rerun. Historical performance tables are unchanged.


## History archived and rebased — 2026-09-14

Public [PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) now contains one commit, `9e36b1f8073a717288436ea087328a82a4f3e246`, on upstream `8c94f70f49fbe17adb5deae5b2b48ff467346863`. It remains draft and GitHub reports no merge conflicts. The complete original 58-commit history is preserved in [fork PR3](https://github.com/zianglih/flashinfer/pull/3), head `8c975512665ec5de80d44cc54d1c8ed94a14f9f9`.

All W4A16 compute/backend files remain byte-identical to the archive. Scoped hooks, syntax, independent rebase review and five benchmark host checks pass; ordinary host test collection was blocked by missing `tvm_ffi`. No GPU numerical tests or timing sweeps were rerun. Earlier results below remain tied to their recorded sources. Full preservation and validation records: [history-rewrite-20260914](history-rewrite-20260914/README.md).


Draft PR: https://github.com/flashinfer-ai/flashinfer/pull/5019
Latest pushed commit `d6f8502b7` fixes the curated W4A16 autotune catalog to
F4: four candidates remain, spanning N64/N128 and both token-return modes.
Explicit F8 remains supported. The completed1–8192 comparison favors F4 by
1.619% geometrically over8–8192, with the clearest wins at4096/8192.
[Full fixed-flag comparison](logs/cu132-fixed-f4-vs-f8-auto14-comparison-001/README.md).
One same-node split publication sweep is being prepared to refresh the PR's
final table using the completed F4 Mega data, without a Mega replay.

The N256 experiment was committed as `4db0979cf` and reverted separately as
`4733b0602` at the user's request. That revert restored the tree to
`a26dc8b88`; the later F4 catalogue simplification is described above. The experiment and all validation and
benchmark evidence are preserved locally and in commit history.

The refined N256 tactic narrowly won4096 hot autotuning (444.0 versus446.7us)
but did not win8192 (765.0 versus730.4us). The user judged that benefit too small.
Unchanged non-N256 native paths' timing variations are excluded from this
retention decision. Every future sweep covers1–8192 in one14-row run;
1/2/4 remain reporting-only for retention. No publication split or repeated sweep was run.
The PR Final performance table is unchanged.

[Current state and evidence](CURRENT_STATE.md).
[Development ledger](w4a16_optimization_experiments.md).
[Implementation cleanup](candidates/w4a16_implementation_cleanup/README.md).
[Pipeline comparison](candidates/w4a16_pipeline_orchestration_review/README.md).

## Historical development notes

The following evidence describes the preceding early raw-slot release,
commit `ceb619b21b02fb9d6235edd3eed10ea06627ba51` / source3b425:
Native2 direct, unchanged numerical8/32
both modes and full13/default8/AUTO100 passed. Over8–4096, latency GM is
**−0.424211% versus complete3efa**,6/10 lower, but **+1.532273% versus whole098c**,
4/10 lower. Results are marginal and mixed, with no new best; the published098c
whole-run table remains unchanged. Source/native/idle closure is0d54a5c7.
[Decision and complete tables](candidates/w4a16_raw_release_before_tmem_wait/execution/README.md).
The preceding empty FC1 bulk-group deletion remains retained as pure cleanup,
not a speedup; [its completed3efa sweep](candidates/w4a16_fc1_empty_bulk_drain/execution/README.md)
supplies the whole BEFORE without a rerun.

Previously published removal commit: `8d7718c9a6c76e5722e1cf201395b0df538b081e`.
CLC is removed in that separate commit (net1,093 lines), retaining static and
atomic-counter scheduling. Its parent16b7170fe preserves CLC for future use;
all local candidates, logs and profiles are retained. Removal validation passes:
135 host tests, identical default native instructions, eight EP2 rank tests and
32 compiled objects with zero local bytes. The PR remains draft and its complete
Final performance tables are unchanged.

The independent `flashinfer/` checkout uses `feat/w4a16-megamoe`. Earlier
retained changes include two-file raw-slot release, the five-line empty FC1
bulk-group cleanup and the separate CLC removal commit.
The tail-fence reorder passed native/numerical checks
but was rejected after a 2.02% latency increase versus the default (8–4096).
The preceding atomic-preclaim election trial passed native and
numerical checks but was rejected: full AUTO latency increased2.38% over8–4096
versus the latest whole default (3.85% versus the separate retained best).
The direct-FC2 barrier candidate was also rejected (+0.57% versus default).
Both complete before/after tables and source snapshots remain local. The retained
[full NCU reports](profiles/direct-epi-0910a-ncu-full-t1024-001/README.md) are now
downloaded and analyzed. Follow [CURRENT_STATE.md](CURRENT_STATE.md) for exact
source identities, complete tables and current native-validation status.
Future work focuses on unnecessary barriers and independent overlap in the
remaining five-WG/two-decoder kernel. No CLC trial remains active.
Maintained code lives at `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`.
Initial upstream is `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

The public MegaConfig/MoEEpLayer backend uses BF16 activations, packed NVFP4
weights, native per-expert E4M3 scale planes and separate FP32 global alphas. Two decode
warpgroups split each K tile and write BF16 directly into TMEM for MMA.
The raw weight/scale ring fits up to five stages. The activation ring prefers
three stages and falls back to two when shared memory requires it. The
accumulator ring has two stages; decoded TMEM has three at N64 and two at N128.
No BF16 weight materialization or round trip is used.

The default autotune catalog is one eight-dictionary Cartesian product:
M256/N64 or M256/N128 at K256 and physical cluster2, each with flag4/8 and
epi/reused-dispatch return, all explicitly selecting scheduler depth two.
Manual M128 and scheduler3 configurations remain supported; the untuned
scheduler default remains three. `knobs="auto"` tunes during collective eager
warmup. Explicit dictionaries bypass cache/default selection. None uses a
cache hit or the existing M256/N128 flag4/epi default.

## Earlier CUDA 13.2 results, 2026-09-10 UTC

Central source57e2 is fully closed: **139 host tests, five native comparisons
covering all11 exact roles,11 rank tests/41 numerical objects with compute
LOCAL0, and the complete default8/full13 AUTO100 run**. Numerical closure is
[b606e836](logs/cu132-recovery0909e-central-numerical-full-001-idle.json), with
[result3af0c730](candidates/w4a16_central_refactor/execution/numerical-result.json).
The default saved result0c19b3ee/proofd56db1c9 retains13 rows,104 compiled/winner
records,13×8 rankings and1,300 primary samples.

Against the complete owned098c default run, central latency GM over8–4096 is
**+1.437759%, with4/10 rows lower**. This is not a performance gain. Keep the
previous098c whole default best table. The
[full13 comparison](logs/cu132-recovery0909e-owned-default-vs-central-independent-comparison-001/README.md)
and [ledger completion](w4a16_optimization_experiments.md#entry-068--central-maintained-package-and-wrapper-cleanup)
preserve every row; no baseline validator or timing was rerun for this update.

Published5152a9e7 contains only scoped init export cleanup, with
[static identity proofdc703c5a](candidates/w4a16_init_cleanup/checks.json) and no
host/GPU/performance rerun. [PR readback](logs/pr5019-init-cleanup-after-body-edit-001.json)
confirms OPEN/draft/head5152 and body8183aead. The normal draft now records the
closed central result separately; both performance tables retain their26
numeric rows and the previous owned098c default measurement.

The CLC launch change is retained after the full unchanged13/CLC8/AUTO100 sweep:
**−0.910433% latency GM over8–4096,6/10 rows lower** versus the complete previous
CLC run. [Full before/after table](logs/cu132-recovery0910a-loop-vs-tight-rows-independent-comparison-002/README.md).
All nine native role comparisons are exact; unchanged11/41 numerics pass with
LOCAL0 in every role. The physical grid shrinks while workspace and software
fallback retain full skew capacity. CLC remains slower than default and outside
its public catalog; the final default performance table is unchanged.

[PR readback](logs/pr5019-tight-grid-after-body-edit-001.json) confirms draft/head16b
and bodybf1e7fa7 with the same complete Final performance section. The subsequently cancelled
[task-or-terminal trial](candidates/w4a16_configurable_clc/central_refactor_followups/task_or_terminal/README.md)
was installed on0910a as source85a1 and is preserved in its local frozen candidate; native validation passed with
40–48 fewer compute instructions, same resources and exact transport roles.
Its unchanged numerical cohort passed; the whole AUTO was cancelled after onlyT1/T2 on user direction, with no retention result.
It reuses the full tight002 BEFORE and corrected CLC helpers, with no extra
baseline/default/split run. Recovery preserves the same physical GPUs and pinned
stack in explicit26.05-py3; newly built caches retain their actual provenance.
The query/claim-overlap, skip-empty, metadata and payload-overlap proposals are
also archived. See [CURRENT_STATE.md](CURRENT_STATE.md) for current default work.

The completed loop11ea CLC8 reference remains **−0.376683% over8–4096,7/10 lower**
versus its preceding CLC run: [all13 rows](logs/cu132-recovery0909e-clc-before-vs-loop-independent-comparison-001/README.md).
CLC remains outside the public default catalog. Its delivered
[selected global-T128 NSYS report](profiles/clc-loop-0909e-nsys-t128-001/ep_w4a16_megamoe_t128.nsys-rep)
and [analysis](profiles/clc-loop-0909e-nsys-t128-001/README.md) are diagnostic,
not AUTO timing. See [CURRENT_STATE.md](CURRENT_STATE.md) for current pins.

The complete NCU `--set=full` capture is delivered for published056ce/sourceaf938:
[full-metrics index](profiles/current-best-056ce-0909e-full-ncu/README.md) and
[download archive](profiles/current-best-056ce-0909e-full-ncu.zip)
(47,467,778 bytes; SHA256 `9bf5498b71d42713044eaee5a4d2f5dc125397787cca7b768e66efbadf9c8bd2`).
It contains two unchanged NSYS traces, eight new full NCU reports, raw CSV exports
and source/tool metadata. All eight full reports have 2,472 metric names and
14 CLI-rendered sections; six C2C counters were unavailable. Replay duration and
throughput artifacts are retained as diagnostics, not AUTO latency evidence.
The earlier0909d full attempt was interrupted at pass37 without finalized reports.
The older PC-only bundle below remains an immutable historical archive.

K128 B6 is not promoted: its completed8–4096 latency GM is0.234344% lower
than initial16 but0.228269% higher than published shared layout (4/10 wins
each). All13 winners still useK256, with56.43% more subprocess wall than the
retained eight-candidate run. Numerical19/43 passed. Current-best profiles on
restored056ce/af938 are now downloaded: [index and exact metadata](profiles/current-best-056ce-0909d/README.md),
[all ten reports in one archive](profiles/current-best-056ce-0909d.zip)
(6,592,684 bytes; SHA256 `014fc2816f808d4eefd0ebbf772921402061c20ef4d1cb8639bf69da7ac290a2`).
The earlier bundle contains two EP8 NSYS traces and eight PC-only EP8 NCU rank reports, with
no driver/DSL caches. Instrumented eager profile times do not replace the
AUTO cold-L2 measurements. See
[entry061](w4a16_optimization_experiments.md#entry-061--k128-activation-preference-b6).

The completed initial K128/sixteen-tactic trial is not promoted: latency GM
is0.463700% higher over8–4096 (6/10 wins), all13 winners remain K256, and
benchmark subprocess time grows56.33%. Its18/42 numerical cases and one CPU
test passed. All104 exact K-only selection-score pairs favor K256. The whole
initial16 run remains experimental BEFORE for B6; shared-layout1a763 remains
the retained baseline. See [entry060 and the full table](w4a16_optimization_experiments.md#entry-060--k128-geometry-and-sixteen-tactic-catalog).
The published design and measurements below remain commit056ce.

Future performance retention decisions use **8–4096 tokens**: geometric means,
win counts and regression assessments exclude 1, 2 and 4 tokens. Continue
benchmarking and publishing all thirteen rows from 1–4096 tokens in the PR.
Correctness requirements apply across all tested sizes. The historical
thirteen-row comparisons below retain their original scope.

The shared W4A4/W4A16 prepared-weight interface is retained and published at
`056ce0d090d425ee09171e47f6faea61c76c9551`: gate16/up16 FC1 rows, K-major
FP4-x2 `[E,K/2,N]` transpose views and native E4M3 `[E,P]` scale planes, with
matching uint8 aliases. FP32 W4A16 expert alphas remain separate; the current PR
does not add a global-scale policy to other backends. Unquantized preparation flattens
through the existing 2D quantizer before restoring per-expert padding. The
fused BF16 input stager and FC1 final-scratch release remain in place.

This is an interface and maintenance improvement, **not an overall performance
win**. The complete shared-layout run has **0.173117% higher latency GM over
8–4096, with 5/10 wins**, versus the preceding complete staging run. All rows
from 64 through 1024 improve; regressions are T8 +9.290%, T16 +2.553%,
T32 +0.797%, T2048 +2.774% and T4096 +2.018%. The
[complete before/after table](logs/cu132-recovery0909d-staging-vs-shared-layout-independent-comparison-001/README.md)
retains all 13 rows, choices and samples. Six dictionaries change and seven
stay the same, including T8 and both large regressions; sequential AUTO timing
does not establish a fixed-tactic cause. Benchmark subprocess time is
596.187687s versus 599.645278s. The whole accepted comparison `1a763323` current
columns are the next trial's baseline; no rows are replaced or selected by minima.

Current validation passes **129 public host tests, 4 focused GPU tests and
18 rank-test calls / 48 compiled Mega objects**. Actual CUDA checks cover both
FP4/E4M3 and uint8 alias directions with changed backing pointers on one
compiled frontend, graph replay, and real BF16/FP32 preparation matching W4A4
bytes. N64/N128 EP2 both-return references and long-K cases supply 16/40;
manual M128/N64/C1 EP1 references supply 2/8. Matched native captures keep
96 registers and zero stack/local memory, with 36 fewer non-NOP instructions
per geometry. The full AUTO retains 104 winner/resource records, 13×8 rankings
and 1,300 primary samples; separate staging counts are 87 fused / 17 empty,
including all 80 retention observations fused. Detailed receipts are linked in
[entry 058](w4a16_optimization_experiments.md#entry-058--shared-nvfp4-prepared-weight-layout)
and [CURRENT_STATE.md](CURRENT_STATE.md).

[Publication and readback](logs/pr5019-shared-layout-publication-001.json)
confirm draft head `056ce` and exact canonical body `fd2fc607`. The
[source association](logs/pr5019-shared-layout-publication-source-association-001.json)
verifies all 1,575 measured source files against committed Git blobs, source
`af938`. The CUDA 13.0 table and reused CUDA 13.2 split column remain historical
and unchanged; the new shared layout has no CUDA 13.0 validation. Earlier
static-rounds, group256 and decoded-readiness trials remain rejected, with
complete results preserved in the ledger. ACC1 was rejected after its complete run: **+2.515221% latency GM over 8–4096,
1/10 wins**, with all 13 rows preserved in the
[full comparison](logs/cu132-recovery0909d-shared-layout-vs-single-acc-independent-comparison-001/README.md).
Its [saved numerical audit](logs/cu132-recovery0909d-single-acc-numerics-independent-001/README.md)
passes 13 rank tests / 40 objects (B3×36, manual B2×4), preserving the first
manual rendezvous failure and successful manual-only retry. Shared-layout1a763
remains the whole baseline. K128 is next on ACC2, with the original eight K256
entries plus eight K128 entries in one planned full catalog16 run; native,
numerical and catalog-reset checks are not yet claimed complete.

## Historical checkpoints

The records in this section describe their original source and environment;
"current" and "latest" within them refer to those earlier checkpoints.

- Latest completed local sweep: [graph-scored512 fixed/auto and all earlier whole-run comparisons](logs/cu132-graph-scoring-four-source-independent-001/FINDINGS.md). All seven cases above32 tokens beat their paired split control, but margins at64/512 are narrow; T1 and4096 still regress against the fresh C1 automatic run. It is a useful general trial baseline, without an unqualified overall-best claim or PR-table replacement. [First32 predecode native proof](candidates/w4a16_fc2_first_fragment_predecode_native_review_0d795/README.md) passes both matched N128/N64 pairs with no spills and actual math before the wait. The separate input-dispatch-on-epilogue proposal is now in numerical testing. [Complete EP8/EP1 profiler findings](profiles/zero-dest512-recovery0908b-ncu-standalone-002/FINDINGS.md) remain source-specific mechanism evidence.
- Current complete CUDA13.2 EP8 CUPTI auto16 run:
  `cu132-c1-catalog16-full13-002-auto`, exact six-file proposal now committed
  as195946. Global powers of two1–4096, H7168/I2048/E256/top8,
  graphs/coldL2/100iterations. T4096 split0.562021ms/Mega0.501842ms/1.120x;
  Mega trails split at1/32/64. The [complete current table](logs/cu132-c1-catalog16-full13-002-analysis/auto16-full13.md)
  preserves every actual winner. [Same-source fixed versus auto](logs/cu132-c1-catalog16-full13-002-analysis/fixed-versus-auto16-full13.md)
  improves12/13 Mega rows; T8 regresses1.37%. The audit verifies52raw rows,
  208split selections,208compiled records,104winner confirmations and all13
  sixteen-candidate rankings, with unchanged1572-file source inventories.
- C1 wins4/8/32/64, but online host-score margins over C2 are only0–3.6us.
  [Historical auto12 context](logs/cu132-c1-catalog16-full13-002-analysis/historical-auto12-context.md)
  exposes the T32 regression: Mega+8.01% while split+0.11%. That different-source,
  different-catalog comparison is a repeat hotspot, not an isolated C1 ablation.
  The extension preserves the original twelve choices and default; it does not
  establish uniform speedups or nonregression.
- CUDA13.0's current complete table remains the twelve-candidate6315 run
  `cu130-cross-stack-full13-001-auto`, T4096 split0.570468ms/Mega0.540133ms/1.056x.
  [Complete cross-stack evidence](logs/cross-stack-full13-001-analysis/comparison.json)
  retains both original6315 fixed/auto series. The fresh CUDA13.0 replacement has now passed C1 public EP1/EP2 and all16-tactic lifecycle gates and completed its [full13 fixed/auto comparison](logs/cross-stack-recovery0908b-c1-full13-001-analysis/comparison.md). This newer evidence remains separate from each displayed historical table.
- Historical second-box evidence: `fi-w4a16-mega-cu130-0908`, node`hu-pdx-119`, ran explicit
  `nvcr.io/nvidia/pytorch:25.11-py3`, nvcc13.0.88/imageTorch2.10.0a0+b558c986e8.nv25.11,
  isolated matching DSL4.7.1cu12/nativecompiler12.9 with real fallback gateFalse,
  loadedNVSHMEM3.4.5/NCCL2.28.8. CPU105,10EP1/10perEP2,6exact shareddecoder cases
  and all12 lifecycle pass; productionPTX proves fallback→TMEM and no transform
  locals. [Detailed environment](candidates/w4a16_cuda130/README.md).
  Cross-stack fixed timing remains slower and is under investigation; nearparity
  is not yet established. Existing CUPTI/event repeats do not remove the gap.
- Current C1 extension validation:121 public host tests; flag8 public suites
  pass10 EP1 and10 per EP2 rank, while deliberately explicit flag4 cases remain
  flag4. All sixteen candidate lifecycle oracles pass EP1/EP2, including all four
  C1 choices, an empty source rank, winner/cache agreement, a new None-layer cache
  hit, and stable/changed-input graph replay. H9472/I64/M257 proves raw4.
  [Independent validation audit](logs/c1-curated16-validation-independent-001.json)
  checks all five1572-file source inventories and actual compiled records.
  Changed-file pre-commit including mypy/Ruff passed; no tolerance changed.
  Earlier105-host/full-hook6315 evidence remains source-specific. Local results
  do not imply upstream GPU CI success; that workflow is permission-gated.
- Source-specific6315 N64 codegen has96 registers,640 threads and no local instructions.
  [Stage3 audit](profiles/n64-stage3-codegen-audit-002/ANALYSIS.md).
  Software nsys T256 verifies 16 fused launches/eight GPUs and 183808 dynamic SMEM bytes.
  [Current PC-only NCU audit](profiles/tmem-n64-stage3-current-ncu-pc-001/independent-audit/ANALYSIS.md)
  completes on all eight ranks with zero dropped samples.
  Focused repeats confirm 8.01%/3.63% lower Mega latency at 256/4096 versus
  adjacent fixed controls; 16 tokens is nearly tied.
  [Repeat evidence](logs/tmem-auto-selected-repeat-001/analysis/repeat-report.md).
- CUDA13.2 replacement `fi-w4a16-mega-0908b`, node `hu-pdx-88`, eight B300, driver 590.48.01,
  explicit `nvcr.io/nvidia/pytorch:26.05-py3`, rechecked 2026-09-08 as newest
  CUDA 13.2 image. nvcc 13.2.78, torch 2.12.0a0+5aff3928d8.nv26.05, DSL4.7.1,
  CUPTI13.2.0/runtime13.2.86, nsys2026.2.1, ncu2026.1.1. Bundled DSL
  compiler 13.3.27 is separate from system CUDA 13.2. Setup log is local.
- Earlier0907 devbox disappeared; unfetched stage3 timings were lost and are
  not evidence. Earlier fetched artifacts remain as historical controls.
  `remote.py` now validates remote execution and completion markers because
  managed h can return zero for a missing box. Use `/usr/local/bin/h` directly.
- K128 remains CPU-only and unapplied. C1's four curated choices are now
  retained after the completed functional/full13 gates above; older C2/C1/C2
  experiments remain historical. The general FC1 halfguard helper-v2 completed
  a separate full13 fixed/auto sweep; the [audited comparison](logs/cu132-halfguard-v2-full13-001-analysis/C1-COMPARISON.md)
  establishes no broad gain, so it remains unpromoted. Its source, codegen and
  numerical evidence belong to its own manifest. Branch-first constexpr v3 has
  also completed full13: the [complete comparison](logs/cu132-halfguard-v3-full13-001-analysis/PRIOR-COMPARISON.md)
  verifies identical fixed configurations and an epilogue-only source change;
  fixed T4–4096 changes -2.69% to +1.87% against C1, with no broad gain.
  The published C1 table remains unchanged. Isolated [512-thread adapters](candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512/README.md)
  preserve two decode groups and require actual initial REG128 before any new
  compiled Mega object can launch; their fresh-node public/lifecycle GPU admission is now complete; performance retention remains pending.

## Working records and remote execution

**Active experiment visibility (user instruction):** put implementation changes
in this project's `flashinfer/` checkout before experiments, and keep its Git diff
current as fixes are made so the user can inspect them. Leave unvalidated changes
uncommitted and unpushed. Candidate folders retain source-specific snapshots,
patches and evidence; they must not be the only place active code lives. Coordinate
file ownership before edits, and keep each running remote trial's source fixed.

The live [PR_BODY.md](PR_BODY.md) has one complete final13 timing table per environment and
is updated whenever the current best changes. Detailed experiment history is
local in [w4a16_optimization_experiments.md](w4a16_optimization_experiments.md)
and [PERFORMANCE_LEDGER.md](PERFORMANCE_LEDGER.md), with immutable raw artifacts.
Prior expanded PR bodies are preserved as `PR_BODY.pre-final-table-c7713ba1.md`
and `PR_BODY.pre-tmem-16aa85bd.md`. Upstream GPU CI was authorization-gated;
local results do not establish its status. Keep PR5019 draft.

`remote.py` uses the managed HAI CLI for commands and explicit source overlays.
Run managed HAI commands from this effort's `hai/` checkout when the CLI
requires a HAI working directory. The executable must still be
`/usr/local/bin/h`; using the checkout as cwd does not select its CLI or venv.
Verify `command -v h` resolves to `/usr/local/bin/h` before devbox operations.
Use `remote.py run '<command>'`, `remote.py sync <repository-relative-files>`,
or `remote.py get <remote-project-relative-file> <local-destination>`.
The active remote GPU source is `/workspace/flashinfer-w4a16-megamoe/flashinfer`.
An independent `host-validation` source copy supports CPU checks during GPU
benchmarks. Do not change the active GPU source during a benchmark/profile run.
Use explicit localhost torchrun rendezvous; `--standalone` advertises a node
hostname this container cannot resolve.

Read-only historical evidence:
`/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`
and sibling `logs/`.

Coordinate GPU ownership with the parent before any launch or active-source
overlay. CPU artifact reviews may run against `host-validation` concurrently.

## Numerical contract

Packed NVFP4 E2M1 times per-16 E4M3 scale decoded online to BF16, BF16 MMA
with FP32 accumulation, global weight alpha applied after accumulation, BF16
FC1 activation handoff, post-FC2 FP32 routing-weight application and BF16 output.
BF16 dispatch/combine. No activation or FC2-input quantization. Compare the
same packed weights, exact scales, routes and inputs to the existing W4A16
plus EP communication control, without relaxing numerical tolerance.
The split control rounds each rank's weighted partial to BF16 before rank
combine; Mega weights all per-route BF16 FC2 values in FP32 and converts once.
The isolated EP8 global8 diagnosis found all 458,752 per-route values bitwise
equal, but three final-tensor failures under the unchanged strict tolerance.
The optional cross-backend final `--refcheck` is therefore omitted from timing;
independent oracles and exact contract tests remain the correctness gate.

## Evidence rules

Keep scripts, logs, Nsight reports, experiment ledger and PR-body drafts here.
Record source SHA and candidate patch hash per run. Use full layer timing for
primary results; distinguish summed kernel durations from GPU span. Run ncu
on coordinated collectives rather than replaying a single participating rank
in isolation. Retain rejected experiment results and revert unhelpful changes.

The existing benchmark defines 1-4096 as global tokens. Preserve and label
that convention; EP8 low-token cells include zero-token ranks.
