# Current state: review fixes pushed; performance aligned

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


Primary is clean at pushed `8c975512665ec5de80d44cc54d1c8ed94a14f9f9`.
Draft PR: https://github.com/flashinfer-ai/flashinfer/pull/5019.
The new Final refresh is ready for root publication/readback. It uses measured
routing commit7d0434eb8/source5e9c and existing same-node split source3da,
without relabeling timing as a rerun at the cleanup head.

## Current retained code and validation

Route-pair reuse computes one direct-return pointer/validity for two adjacent
16-BF16 stores, preserving widened Int64 stride arithmetic, bounds and readiness.
Matched native C1/direct saves24 instructions and N64/direct saves16; reused-return
controls are byte-exact. Final metadata load count is unchanged. All5 native
fixtures retain96 registers,640 threads,zero stack/local bytes and the same
stages/shared memory. Focused source5e9c tests pass4 EP1,6 EP2 per rank and2 C1
routing calls per rank, with unchanged references/tolerances and closures.

The complete source5e9c AUTO14 passed14/112/56/1400 saved checks; result2ba8861d,
proof4d440f94, comparison70645aeb. Whole source3da repeat6060 is the control.
GM8–8192 latency is−0.295598%,7/11 lower; all choices unchanged, hot44 directions
21 lower/3 equal/20 higher. The changed selected-direct8–1024 group is−0.164361%
(5/8 lower); native-identical selected-reuse2048+ is−0.644723%(2/3 lower).
Retention is for reduced bookkeeping/cleaner reuse, not material latency gain.
Artifacts: `candidates/w4a16_fc2_route_pair_reuse/`.

Subsequent assignment-only kernel and required-alpha cleanup removes25 lines in
commit8c975512, frozen source680b17f0/manifest23d1f935. One N64/F4/direct capture
is exactly5392 instructions, PC/encoding/scheduling, arguments/descriptors and
resources versus5e9c. Native completion08ba20dd and independent review85d37005
pass; source/native/idle closure and commit hooks pass. No numerical or timing
replay at the cleanup head is claimed. Public omitted scales still become ones.
Artifacts: `candidates/w4a16_unused_kernel_fields/` and
`candidates/w4a16_required_epilogue_alpha/`.

## Orchestration audit complete

The source-only recheck confirms the existing early weight/decode overlap and
metadata/TMEM limits. No additional macro trial was selected. This does not
claim that broader pipeline redesigns are exhausted. Bootstrap input-staging
fusion is feasible but adds raw-input dtype, graph-cache and visibility plumbing
while preserving copy traffic; it remains a documented design option.
Read the notes under `candidates/w4a16_pipeline_orchestration_review/`:
`ORCHESTRATION_RECHECK_542224.md` (42dffdeb) and
`BOOTSTRAP_STAGING_FEASIBILITY.md` (3b28b44a).

## FC2 K256 readiness-mask experiment: closed, not retained

The requested early weight overlap already exists. Scheduler publication starts
after routing-count exchange, before remote payload pulls. Packed-weight loading
and both decoder WGs run independently of activation readiness. N64/N128 have
D3/D2 decoded TMEM rings; those buffers bound runahead. See
`candidates/w4a16_pipeline_orchestration_review/EARLY_WEIGHT_DECODE_AUDIT.md`.

A distinct implementation let FC2 consume ready K256 activation regions while
later FC1 feature regions finished. It used unique one-hot GPU-release ADDs,
cached acquire masks and existing batching/reset, with no extra barriers or
spills. Review caught and corrected an indirect metadata-prefetch regression:
the revised scheduler peek certified input/metadata readiness in both phases,
while FC2 independently checked K masks. Final patch 3d87ac89 was ported to the
primary before any run, five files and seven net added lines.

Frozen experimental source b65b / manifest 502c27a1 passed native4, five routing
calls per rank, three EP1 graph cases and two EP2 graph cases per rank. These
cover partial groups, bit31/word transitions, C1, immediate/batched publication,
empty/refill and replay. Native review d5d5e486; test completion 85f77912.
The functional implementation had no unresolved numerical or lowering failure.

Full public-F4 run `cu132-fc2-mask-f4-auto14-direct-001`, original 3477, passed
all 14 token counts 1–8192 with 100 cold-L2 CUPTI samples each in 429.973824 s.
Original/close-fetch 24955 passed; reader/comparator each passed once:
14 rows,112 selections/winners,56 hot scores,1400 primary samples.
Proof c1ac2eff, result 2096961d, comparison de261c26. Against the whole retained
F4 run, geometric latency over 8–8192 changed by -0.201994%, only 4/11 rows
lower. All selected tactics were unchanged; matched hot changes were small and
mixed. No compelling general gain was demonstrated, so the mask was removed.

[Complete before/after and matched hot tables](logs/cu132-fc2-mask-vs-retained-f4-auto14-comparison-001/README.md).
All five primary files were verified byte-exact before restoration. Full patch
0d095e6d and retention record are under
`candidates/w4a16_fc2_per_k_readiness/archived-after-auto14/`; all proposed files,
native/profile artifacts and logs are preserved. The independent sizes-only
cleanup was applied only after restoring the mask to clean 21fd.

The preceding exact-tail FP32 reduction is also closed and archived: -0.175331%
retention-range latency, 6/11 lower, not enough to justify 155 implementation
lines. Its complete artifacts remain under `candidates/w4a16_exact_tail_reduce/`.
Neither rejected candidate appears in the PR performance table or current code.

## Retained publication

Public four F4 candidates preserve N64/N128 × direct/reused return; manual F8 stays.
The new full14 table uses measured Mega5e9c/result2ba8861d and existing split3da/
result2cf158b0 on node59, image26.05, realEP8,100 cold-L2 CUPTI samples per row.
GM split/Mega is1.111309677× over8–8192 (10.016081% lower latency), all11 rows;
all14 raw rows favor Mega and remain visible. Table under
`candidates/w4a16_fc2_route_pair_reuse/FINAL_PUBLICATION_COMPARISON.md`.
Root owns final body publication/readback. Older source3da Mega6060 publication
and historical CUDA13.0 rows remain saved; no minima or cross-node substitution.

## Runtime and operating rules

Sole remote executor: iteration_prep. Devbox fi-w4a16-mega-0911c, c2,
namespace ziangli, node hu-pdx-59, eight B300 GPUs, image
nvcr.io/nvidia/pytorch:26.05-py3. CUDA13.2.78, driver590.48.01,
Torch2.12.0a0+5aff3928d8.nv26.05, CuTe DSL4.7.1/native compiler13.3.27,
CUPTI13.2.0, NSYS2026.2.1.210, NCU2026.1.1.0. Native inventory4143afa0;
environmentfaa253dc. Use managed /usr/local/bin/h directly after verifying
command -v h resolves there.
No CUDA13.0 work or new devbox request is needed.

Every performance decision uses one complete 1–8192 sweep with 100 CUPTI samples,
reporting 1/2/4 but excluding them from retention. Reuse the whole retained Mega
baseline; split only needs a publication refresh when its evidence changes.
Keep exactly two decode WGs and prefer five total. Closed CLC, custom transport,
share_operand_release, N256, K128 and one-decode-WG variants stay closed.
Favor substantial orchestration/overlap improvements and pure cleanup over tiny
instruction/lifetime changes. Port experiments to primary before GPU work.
Preserve artifacts; keep history in `w4a16_optimization_experiments.md`, with
only current design, validation boundaries and final tables in the draft PR.
