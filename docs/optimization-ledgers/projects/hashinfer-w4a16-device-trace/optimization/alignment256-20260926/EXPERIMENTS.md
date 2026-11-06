# Native 256-bit global access campaign

## Scope and retention rule

The 2026-09-26 request supersedes previous preserve-16-byte and alignment-fallback proposals. Establish a hard 32-byte contract for tensors used by native 256-bit global copies. Reject invalid raw callers before compilation/launch; keep ordinary allocation and ownership. No upstream FlashInfer sync is authorized yet. Work remains in HashInfer PR13; artifacts remain outside the repository.

Baseline is exact current PR head `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`, package SHA256 `79ab6119a9019177beedaef1b396f9e601f56e2fe5aaad723709e6a98c713ddf`. A clean detached worktree is preserved in `before/`, with Git storage inside the effort's HashInfer clone. Candidate1 uses16 BF16 values/worker and native256 route loads/output stores, preserving ordered FP32 arithmetic. Retention requires fresh before/after end-to-end evidence, decode and EP8 guards, and selected-winner SASS. Instruction reduction is useful even with small timing gains; material regressions are not automatically accepted. Each retained follow-up becomes the next comparator.

The full source audit is `IMPLEMENTATION_AUDIT.md`. The measurement contract and frozen harness identities are `BENCHMARK.md` and `harness-cpu-checks.json`. Native H7168 EP4/EP8 results and uniform H6144 EP4 results are separate workloads. Historical true256 input staging was tested and rejected; previous wider combine workers did not establish native256 global loads.

## Resource recovery and environment

The prior `fi-w4a16-trace-0925` devbox was absent before this campaign; this task did not release it. Managed `/usr/local/bin/h` was verified. Its devbox command requires a HAI checkout as cwd, so the existing project-local `hai/` context was used without invoking its local CLI. Initial `ziangli` request queued with zero GPU quota; only that newly queued request was removed before retrying `infra`.

Replacement: C2/infra `fi-w4a16-align256-0926`, pod `devbox-fi-w4a16-align256-0926-0`, node `hu-pdx-38`, eight B300 SXM6 GPUs, compute10.3, driver590.48.01. Requested bare, no size override. Keep allocated after work. Live NGC/release-table check found26.05 remains newest PyTorch image providing CUDA13.2;26.06/07 use13.3 and26.08 uses13.4. Explicit image `nvcr.io/nvidia/pytorch:26.05-py3`.

`setup-runtime.sh` creates a system-site-packages venv preserving image Torch and pins the previous CuTe4.8/NVSHMEM/CUPTI environment. Runtime and compiler provenance will be recorded separately. Remote task root `/workspace/hashinfer-alignment256-20260926`; durable result root `/data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926`.

The first source-attestation attempt correctly rejected Mac tar metadata sidecars (`._*.py`) before any GPU benchmark. Removed only those transferred metadata files, then revalidated baseline bytes. Future archives disable Apple metadata. This setup failure is not a timing sample.

## Campaign1: combine payload256

Serial A1/B1/B2/A2 campaign, fresh source/rank caches, native SM103a on both sides. A1 nativeEP4 launched first with `--max-trials1`; remaining phases resume the same immutable campaign. No performance conclusion or retention decision yet.

Frozen payload trial commit `e5d91761f8c8a8ab78bf75428006327d1b35e864`, package SHA256 `c7f38c259459e692a54b29fb4fb41ca98b2d4c46c48c76d089f361ec81eeec4c`, in `payload-candidate/` local experiment branch. Not pushed or retained. Runtime CPU validation on the frozen candidate: **27 passed in1.65s**, with CUDA devices hidden. Actual runtime reports NVSHMEM3.6.5; pinned wheel version remains3.8.0. Source audit established native allocator512B alignment. A1 nativeEP4 is active; queued continuation waits for its verified success, runs one separate uniform128 candidate smoke, then finishes nativeEP8/uniform A1. Smoke timings are excluded from ABBA.

## First native256 smoke and spill investigation

Fresh A1 EP4 completed13rows/1300cold samples,4160hot tuner rank-samples,52winner binaries. Independent `payload-A1-ep4-audit-v2` passes, including4independent T128reference records and52finite/repeat records. Baselinecodegen all52exports: REG96/STACK0/LOCAL0/noLDL-STL; combine16LDG128+2STG128 per16BF16 output elements.

Candidate uniform128 smoke `payload-smoke-v3` passed all4ranks bit-exact/reference/source/binary checks. Source e5d9176, N64/G1024/epi, H6144EP4T128, nativeSM103a. Actual combine8LDG256+1STG256, but REG96/STACK40,10staticLDL-family sites and17STL-family sites. PTX has no explicitlocal accesses: assembler spills combine state/scores. No local-memory operations appear inside the repeated per-K MMA/TMA/transform work loop. See independent codegen and spill-analysis reports. The40Bframe is not evidence of per-K pipeline spilling. Smoke timing is excluded from performance retention.

Smokev1failed argument parsing before GPU because torchrun needed `--` before the worker's `--run`; v2blocked before launch on unresolvable node-hostname rendezvous with `--standalone`, then only its owned processes were stopped. v3uses explicit127.0.0.1/29914 and succeeds. Preservefailedlog artifacts; nofailedsamples enterABBA.

User asks to map spills to exact WGs and reclaim donated registers or restoreall96. For this fixture width16 has12288workers,148CTAs and18944workers/WG strip: onlytransformWG3 CTAs0–95 runactualcombine. This is deterministic source/mapping evidence, not an instruction-trace measurement. Common spillPCs do not mean onlythelowest-budgetrole spills. DetailedCFG/WG mapping pending.

Prepared independent fixed-tactic diagnostic variants: width8/alignment32 cd19503, lateprepare aafbbdb, compute-role rebalance3e96fc4, all-WG96restore47576e5, payload+score9afe37c, score-only/payload128adadbd6. Exact identities in diagnostic-sources.json. All remainlocal/unretained. `run-fixed-diagnostics.py` waits for the3A1baseline matrices then runs all8variants serially. These fixed-tactic diagnostics are explicitlyineligible for AUTO performance retention. Original frozen timingworker/driver are unchanged. GPU reducer-only480case harness isprepared, notrunyet. ScorecandidateCPU38tests pass; scopedhooks pass.

## Eight fixed-tactic register diagnostics

All8 fixed probes completed with four-rank reference/finite/repeat checks. Same H6144 uniform global128, N64/G1024/epilogue and native SM103a. Baseline and width8+alignment32 control have STACK0/LDL0/STL0. Payload16 initial: STACK40/LDL10/STL17; late preparation:24/4/9; retired WG1 rebalance:40/10/17; restore all WGs96 after return barrier:16/6/13; payload16+score256:40/10/17; payload8+score256:0/0/0. These are static native-code sites, not hardware counts or speedup results. Width8 control shows the new alignment contract alone does not cause spills. A late+all96 compound is being prepared to remove early state liveness while making the common tail's budget explicit before state creation.

Full first baseline pass is complete:30 workload rows,3000 cold rank-MAX samples,13760 hot rank samples,172 selected binary exports. `payload-A1-all-audit` passes. No candidate timing arm or final A2 has launched; B source can still be rebound with a journaled source change, preserving every measured A1 receipt.

Standalone actual payload reducer completed480 cases/60 compilations/60 graph cases under Compute Sanitizer memcheck with0 errors. Covers K1/2/3/4/7/8/9/16/17/32, H32/96/6144, weighted/unweighted, empty/partial/full output and allocation-base/aligned-interior views. All BF16 output bits, input immutability, output canaries and graph checks passed. Frozen source e5d9176; this qualifies its unchanged reducer method, not the full integrated register-retirement change or performance. Logs at `reducer-payload-memcheck-v1`.

## Spill-free compound and performance candidate freeze

`late-all96-candidate` commit1c6ba01ee64fdbfa68b365fa92a43bb77ae170fb, packageSHA098fb48f3a7026e91e8acebce6188dc0c23c5bd0b3e38ffae8fc228e11ecd9fb, combines the two complementary changes. All four uniform128 fixed-probe ranks pass exact reference/finite/repeat/source checks. Selected binary: REG96/STACK0/LOCAL0, no LDL/STL. Native256 route loads/output stores remain. Preparation follows common inc96, so early dummy state no longer crosses compute-role control flow and the reducer has a uniform96 budget. Existing144/80/64/96/96 compute policy remains; only the retired tail restores all96 using the existing return barrier. No extra barrier or copied implementation.

Main campaign B was rebound before any B trial launched, with a journaled immutable event preserving original/proposed manifests and verifying all three A1 receipts. The first rebind invocation named absent remote arms-remote.json and failed before reading/mutating the manifests; corrected to actual arms.json, then the transaction passed. Local mapping matches the new B. The unchanged full-forward driver resumed B1/B2/A2 against frozen1c6ba01. No timing conclusion yet.

## Original LDG128 controls and preserved timing failure

User additionally requests originalLDG128/16-byte contract with96register restoration. Prepared two controls directly fromcd7cc07:240ead0a94b4dd56eb712dc4ddc1f9f501e907c6 adds only the six register-tail lines; af145b603fe4f542a644693c9bd2ef78f725e3bb adds the late-preparation+all96 tail. Each changes only megamoe_kernel.py, with frontend/reducer/README/tests byte-identical to baseline. Fixed4rank native probes are running in `fixed-diagnostics-original128-v1`; original codegen/numerical diagnostics remain separate from retention timing.

First full candidate B1 aborted2026-09-26T04:29:18Z at nativeEP4 globalT16. Rank1's Python fatal stack identifies `hashinfer/testing/utils.py:516`, `cupti.finalize()`, after all8T16 tuning candidates had completed. T1/2/4/8 had winner exports. Torchrun terminated the other ranks after hostSIGSEGV; this is not a completed timing sweep and no partial sample enters the final comparison. No CUDAexecution error was reported before the hostcrash, but that does not prove its cause. Preserve entire failed attempt and perform one fresh-process retry via explicit journaled recovery with unchanged source/helpers and all3A1 receipts. `failed-B1-summary.tgz` preserves the first failure context.

## Prioritize LDG128 timing per user steering

Compound integration completed:14EP2 cases/rank and8EP4 cases/rank passed (60 cooperating-rank reports, no skips). These are existing uneven/empty/refill/geometry/tail, graph lifetime and epilogue contract tests. The source-bound driver stores exact collection/outcome receipts. Remaining detailed strict/sanitizer integration checks are deferred until timing indicates retention, per the user's explicit request to speed iterations.

The first recovery wrapper failed before metadata mutation because the remote read-only parsing dependency `optimization/summarize_benchmarks.py` was not yet transferred. After copying the unchanged dependency, the guarded recovery archived the original SIGSEGV attempt and preserved A1. Its new B1 retry began just as the user requested LDG128 benchmarking first. Root sent SIGTERM to only the verified owned torchrun process group43801 before timing progress, preserving that canceled attempt as a user-priority cancellation rather than another kernel/CUPTI failure. The256 campaign is now parked. Directly launched focused original128 study A1/C1/D1/D2/C2/A2, no correctness testing ahead of it. All original128 fixed diagnostics already passed and the baseline contracts/reducer remain exactcd7cc07 bytes.

## Hard retention gate: no spills for256

User explicitly requires eliminating all register spills to justify the256 contract. Treat no-spill native codegen as a hard retention condition, not merely an instruction-count preference or an acceptable small timing tradeoff. The1c6ba01 fixed uniform128 probe is already STACK0/LOCAL0/noLDL-STL across four ranks; broader relevant workload/tactic coverage remains pending. Do not promote based only on that single specialization. Inspect actual retained binaries across the benchmark matrix and compiled candidate catalog, identify any residual spilling WG/state and eliminate it; otherwise reject the256 contract. LDG128 focused timing retains priority.

## Completed original128 performance control

Focused A1/C1/D1/D2/C2/A2 campaign passed all six sweeps. The local source/artifact audit verifies 2,400 cold rank-MAX samples, 7,680 hot tuner rank samples, 96 winning native exports, 24 independent-reference rank records, and identical fixture/output hashes across all six sweeps. Each source/shape median pools 200 raw samples, without trimming. See `original128-focused-audit-v1.md/.json` and `original128-focused-v1/`.

| Global tokens | Original128 us | Restore96 tail us | Late preparation + restore96 us | Original / restore96 | Original / late+96 |
|---:|---:|---:|---:|---:|---:|
|128|282.738|286.691|291.027|0.986213|0.971520|
|4096|594.918|597.301|597.734|0.996010|0.995289|
|8192|1139.673|1151.675|1155.994|0.989579|0.985881|
|16384|2357.044|2380.516|2374.242|0.990140|0.992756|

No meaningful improvement; do not retain either original128 control. T128 is visibly noisy/order-sensitive, particularly D (2.94% repeat drift), so do not attribute its full pooled slowdown solely to the source change. The larger prefill rows likewise show no gain, and the source/codegen audit shows no executed instruction reduction. Scope is uniform EP4 H6144/I2048/E256/top8, not a completed native EP4/EP8 comparison. No additional detailed correctness run was inserted ahead of these timings.

After GPU idle was confirmed, the early wide-B1 user-priority cancellation was archived separately under `canceled-attempts/20260926T051120.843572Z-dbada56c`; event SHA256 `cee621638ce48332962bf674baffc4c7fbdf4f6e97f58f6ff77ba5743de3e6ae`. The earlier failure history and all three A1 receipts are unchanged. Full256 campaign resumed its three B1 groups with the unchanged frozen runner/source, wrapper PID59033. This remains an unretained experiment, with no-spill coverage and full ABBA comparison still pending.

## First256 EP4 screening and lower-cost spill-removal hypotheses

Fresh native EP4 B1 completed successfully. Its52 winner exports are REG96/STACK0/LOCAL0 with no SASS LDL/STL or PTX local memory. This is only the first A1/B1 screening pair. Native T1 increased68.257 to78.737us with the same N64/G512/epilogue tactic; the first and last sample quarters both show the increase. Prefill4K/8K/16K increased0.798119/1.459386/2.852805ms to0.806520/1.487629/2.883259ms. The first two prefill winners match;16K changes G1024 toG512. No causal attribution or retention decision follows from this first pair. Independent source/hash review is `B1_EP4_SCREENING_REVIEW.md`; partial-transfer evidence is preserved separately from the successful266-file compressed copy.

Prepared exactly two additional small source hypotheses, separate from frozen B:

- `late-no-prefetch-candidate`:679aa752f9292d5cbfe4f129c076e347089b58f2, package7917dadb41d479363acbf87c00e11b7f85fee27c14eacbc00dd8954b7c786e56. Parent is late-only aafbbdb; disables score prefetch using the existing scalar path. It trades2 vector128 score loads for8 scalar score loads atK8 to shorten score liveness, without tail register restoration.
- `late-participant96-candidate`:f8c97bb6eb9026ec6af87c825a5bd99c157a1d52, package1269688ad44e919c174f70e6febc88834ab48161fa2af1e1d82b5a647d325d81. Parent is1c6; moves inc96 into the existing four-WG combine branch. WG2 remains64 because it does not combine. Existing WG0 donation, barriers, state preparation, worker mapping and arithmetic are unchanged.

Both sources passed CPU/source checks and remote package verification. The participant archive contains a top-level folder, unlike the no-prefetch archive; an initial nested extraction failed source attestation before GPU use, then only that newly extracted nesting was corrected and exact attestation passed.

`run-tail-refinements.py`, wrapper71046, waits for all6 A1/B1 scopes and GPU idle, then runs the two existing fixed probes serially. Fixed-probe samples are diagnostic only and cannot establish native AUTO retention. Reject any hypothesis still spilling before wider timing. The published checkout and running benchmark source remain unchanged.

The separate all-candidate codegen helper was updated to stop after its eighth successful export and normal graph cleanup, avoiding unused winner recompiles. Exact helper SHA c3a7c05e5315a69d24ba65664eb039a3279fafc6cbfc4c7f8d1c55c68d600b2c; remote CPU plan passed after transferring its unchanged parser dependencies. No GPU catalog invocation yet.

## Full first-pass screening decision and successful tail probes

All three B1 scopes completed with172 spill-free winner exports and matching source/fixture/output closures. Independent table: `payload-full-B1-screening-v1.md/.json`. Native decode GM(T4–512) is1.003794x EP4 and1.001312x EP8; nativeEP4 prefills are slower1.05–1.94%. Uniform H6144 A1/B1 ratios at128/4K/8K/16K are0.977410/0.986170/1.000111/0.989800. The exact all96 compound is unpromising for the target; defer its full-catalog and B2/A2 expense while checking narrower hypotheses. These are screening results only, not a completed ABBA regression claim. The campaign remains a clean six-run prefix and its measured B source will not be replaced.

The two queued fixed tail probes both completed source-bound reference/repeat checks and show REG96/STACK0/LOCAL0. Artifacts: `fixed-tail-refinements-v1/` (55 evidence files); wrapper71046 exited successfully. No-prefetch removes spills without register restoration in this fixture; participant-only restoration also eliminates spills. Actual instruction/schedule audit is pending separately. The old strict reducer parser rejects interleaved scalar-score loads in the no-prefetch binary, so do not treat its parser failure as a kernel failure or weaken the frozen measurement worker. A separate audit will recognize the exact scalar-score plus vector-payload signature.

Prepare a fresh focused comparison of original128, wider payload with scalar scores, wider payload with participant-only restore, and native256 score loads with the original128 payload. All remain unretained and compare against originalcd7cc07. Use balanced A1/B1/C1/D1/D2/C2/B2/A2 order, unchanged public-forward timing worker, eight fresh AUTO candidates and200 pooled cold samples per source/shape. No detailed correctness sweep before these timings.

Fresh four-arm focused campaign launched on idle GPUs, wrapper77859, output `tail-variants-focused-v1`. Runner SHA2562fb1fcb0372ad858a6c503cddb699883c9718756554aa1fb0d3ae687aa62f3ac and manifestdacf0b7752e12c0b298822ac740bb43a495bcf1e7093f05bb8a6857d8934defc were verified remotely before launch. No source, timing worker or helper mutation during the campaign.

Independent fixed-tail audit now passes for both arms (`tail-refinement-independent-audit-v1.md/.json`). All8 rank exports have zero stack/local storage and no LDL/STL/PTX-local traffic;8 reference/repeat checks and source/tactic/fixture/output parity pass. The new external parser recognizes exactly8 scalar FP32 score loads on a separate base (offsets0..28) interleaved with8 vector256 route loads, followed by one vector256 store. Frozen helpers remain untouched. Per16 output elements, reducer-span plus score-load static instruction counts are baseline298, all96282, no-prefetch287, participant96282. The no-prefetch compiler hoists several scalar scores, but shortens their live ranges enough to avoid all spills in this fixture. These normalized static counts are not hardware instruction counters or speedup claims.

## Second resource recovery and fresh focused campaign

At roughly06:18UTC the old C2/infra pod was NotFound; live pod/StatefulSet/Workload/service inventory and managedh list confirmed its devbox was absent. This task did not release it. Shared storage preserved all five completed focused phases (A1/B1/C1/D1/D2) and the partial C2 receipt (passedfalse, noexitcode); B2/A2 never started. Preserve the original campaign unchanged as interrupted screening, with no completed before/after claim.

Reverified `/usr/local/bin/h` and live NVIDIA NGC/release notes:26.05 remains newest CUDA13.2 PyTorch image (26.06/07 use13.3;26.08 uses13.4). Requested bare/no size underziangli first; quota had zero free GPUs, so removed only that new queued request and retriedinfra. Replacement `fi-w4a16-align256-r2-0926`, pod `devbox-fi-w4a16-align256-r2-0926-0`, nodehu-pdx-43, eight B300SXM6AC, driver590.48.01; explicit26.05-py3 image digest222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba. Keep allocated for iteration.

Runtime rebuilt from the unchanged pinned setup. `recovery-r2-runtime-bundle.tar.gz` SHA256403e8a69fc84a85a9684cb8cf13a4cab2d6beae2cf2c2ebda7a36525c69d1f8a contains492source/helper files, excluding Git metadata and caches. Frozen runner/worker/manifest hashes verified before source-boundCPU plan and GPU idle check. New `tail-variants-focused-r2-v1` launched2026-09-26T06:25:00.985513Z, wrapper1356, same eight-phase protocol from scratch. Old machine samples are excluded; no source changes or detailed correctness sweep before benchmarking. Source, runtime, command, GPU identities, and partial evidence transfers are retained beside this ledger.

The original pod-loss snapshot is now local: `tail-focused-pod-loss-v1/`,473hash-verified immediate files, including partial C2. ArchiveSHA45d6d938a3ad1022e3598c896113f87bb4e302131810b998cfadbf479afe30d6; transfer receipt and independent partial audit retained. All80completed winner exports are spill-free, but no matched final baseline exists, so all comparison outcomes remain screening only. Caches remain durable with metadata inventory.

The main HashInfer checkout was restored to clean publishedcd7cc07 after exact `git diff --exit-code e5d9176` verification of its four experimental files. This removes only the already-saved initial spilling candidate from the primary checkout; all experimental commits/worktrees/artifacts remain. No push or upstream change.

## Supplementary spill-artifact closure

Independent CPU-only `audit_spill_artifact_closure.py` (SHA2564e711c7a4a9159e91f2e6f5424ddb46e00a6ed3abd00127dcb8b026e2e3c5aa8) checks native STACK/LOCAL/LDL/STL plus qualified PTX local operations/declarations/address casts, shared-spill opt-in, reviewed internal leaf-call targets and actual ELF relocation entries. Ten parser/relocation tests pass. `supplementary-spill-closure-fixed13-v2` binds13sources×4rankexports:8sources/32exports pass, all5known spilling controls/20exports correctly fail. Audit execution passed; aggregate spill gate intentionallyfalse. Frozen collection/measurement helpers remain unchanged. These are fixed-probe results, not complete candidate-catalog qualification.

A retained candidate must separately inspect its final trace-enabled winner and representative SM100a compilation; perf-disabled SM103a receipts alone do not cover IKET or B200 target codegen. No B200 hardware runtime claim is intended.

Promotion source review found B/C entirely within three owned W4A16 runtime files and no bulk implementation copies. D score-only inherits unnecessary payload/output32 checks: if D alone qualifies, retain score32 validation/allocation/CuTe metadata and K8/K16native256 prefetch, restore original payload/output/workspace contract, remove misleading payload256 documentation/tests, and requalify the new source identity. No frozen source was edited.

## Final decision after complete R2 timing

Fresh R2 finished2026-09-26T06:59:58.470544Z with all8phases, exit0 and idle GPUs. Independent source/raw-sample/codegen/fixture audit PASS:3200cold samples,10240hotrank samples,128selected winner exports,32T128reference records,128finite/repeat checks; all128selected exports zero-spill. Every candidate/shape pooled ratio is below1. Reject all three refined256 variants and both standaloneLDG128 controls. Keep original contract and published PR13cd7cc07; no new trace or upstream sync. Final tables, drift/tactic analysis, qualification limits, preserved artifacts and exact resource are in [FINAL_DECISION.md](FINAL_DECISION.md). Full catalog/trace-enabled/SM100a/further strict correctness gates remain unrun because no candidate qualifies for retention. These are scoped negative-retention results, not proof about all256-bit implementations. Keep replacement devbox for iteration.
