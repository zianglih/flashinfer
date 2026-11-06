# Split W4A16 optimization experiments

This ledger records the follow-up to FlashInfer PRs #4048 and #5019. Source is the independent `flashinfer/` checkout in this project. Historical MegaMoE or split timings are context only; they are not fresh baselines for this effort.

## 001 — Compile-time top-k for fused finalize (retained, draft PR #5186)

- **Baseline:** upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`.
- **Candidate:** `candidates/topk_constexpr/source.patch`, SHA256 `8ad313cb2bab17b62fe584d2f7330193b580fbba73615dd3b38f2e12a4d1eef3`.
- **Motivation:** the MegaMoE compile-time/division audit suggests checking whether split kernels preserve values already known during compilation. Split's scale-table inner extent is top-k, but its wrapper currently represents that extent as a runtime Int64. The fused-finalize scale lookup and output scatter divide by this value.
- **Change:** declare the wrapper's `top_k` as `cutlass.Constexpr`, include it in the compiled-kernel cache key and omit it from the runtime invocation. Dynamic matrix dimensions and token count remain dynamic. No new configuration or autotune tactic is introduced.
- **Expected mechanism:** constant quotient/remainder lowering for the scale lookup and output scatter. Native inspection must establish the generated change; source inspection alone is not instruction-count evidence.
- **Control:** non-fused finalize passes top-k zero and omits the entire scale/finalize branch. Compare its GPU instructions/resources before and after, allowing the intentional host ABI difference.
- **Tests:** extend the existing six-geometry route-boundary test with top-k 2/3 and fused finalize false/true (24 cases), using the unchanged reference and tolerances. Supplement with existing W4A16 graph/EP tests as appropriate; no new test file.
- **Validation:** syntax, scoped pre-commit and independent cache/signature review passed. The subsequent GPU/native results are recorded below.

### Measurement protocol

Dedicated c2 B300 devbox `fi-w4a16-split-0913a`, node `hu-pdx-43`, explicit image `nvcr.io/nvidia/pytorch:26.05-py3`. System CUDA13.2.78, project CuTe DSL4.7.1, Torch2.12.0a0+5aff3928d8.nv26.5.50603568, CUPTI Python13.4.0/library13.4.58. See `remote-prep/README.md` and its raw setup logs for the exact environment and package boundaries.

The project helper `run_split_benchmark.py` calls the current upstream `bench_moe_deepseek._benchmark_single` with only the W4A16 arm selected. Use full auto tuning, H7168/I2048/E256/top-k8, simulated EP8 (32 local experts), fused finalize, routing included, ten warmups, 100 cold-L2 CUDA-graph CUPTI iterations and powers of two from 1 through 8192. It is a single-GPU local-compute benchmark, not distributed communication timing. `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `TRTLLM_ENABLE_PDL=1`, `CUDA_VISIBLE_DEVICES=0` are explicit.

Report all 14 rows. Retention summaries exclude 1/2/4. Compare complete same-node baseline and candidate runs; use the arithmetic ratio `before latency / after latency` for per-row speedup and its geometric mean over 8–8192. Normal timers provide medians, not saved raw per-iteration samples. Per-row autotune caches are saved after measurement for profiling without retuning.

Profile a representative completed row with Nsight Systems and Nsight Compute `--set full`. Preserve source and that row's selected tactic cache. Instrumented durations do not replace the unprofiled sweep. Native capture uses the actual split compile entry point with the installed toolchain, with no custom kernel options.

### Current status

The clean upstream baseline completed all 14 rows with exit0; `logs/baseline-ep8-fused.json` has SHA256 `0fdb419648d83b340566eef9d800c0958efd405a0a874f4bb35cad8a822f357d`. All per-row tactic cache hashes were checked locally. Driver wall time was524.261530 seconds, dominated by first-use compilation; the remaining13 rows completed about nine seconds after the first result.

Baseline native captures succeeded after creating the output/cache directories and requesting PTX/cubin exports followed by standalone disassembly. The initial automatic SASS-export failure is preserved. Actual top-k divisions lower to `div.s32`, with two reciprocal/refinement sequences in SASS; the wrapper's Int64 annotation alone did not predict that narrowing. Fused top-k2 and3 produce identical baseline SASS. Non-fused control evidence is saved separately.

Baseline T128 Nsight Systems and NCU captures completed using the exact saved row cache without retuning. NCU `--set full` selected the observed FC2 launch (grid2×1×74, block512), completed40 console-reported application-replay passes in620.8757 seconds (the exported `profiler__replayer_passes` counter is44) and exported one kernel record with2470 identity/metric columns. Six CTC interconnect metrics were unavailable; the normal timing compilation had no imported line information, so source attribution uses the separate native captures. The NCU duration is not a benchmark latency. Artifacts are under `profiles/`.

The exact three-file candidate passed38 selected tests (24 route-boundary,2 simulated EP8 functional,12 CUDA-graph cases),28 deselected,1039 existing DSL deprecation warnings,36.82 seconds. Initial collection found pytest absent; installing pytest9.1.1/pluggy1.6 in the isolated venv resolved that setup issue without changing kernel/runtime packages. Test references and tolerances were unchanged.

Both fused native checks (top-k2 and3) reduce1640→1584 SASS instruction rows, remove both runtime divisions/reciprocal sequences, and preserve registers/stack/local/static-shared usage. Non-fused top-k0 is whole PTX/SASS byte-identical, including instruction encodings and scheduling. See `NATIVE_COMPARISON.md` for actual checked geometry and scope.

The first full A/B pair gives1.014026× speedup (−1.383239% latency GM over8–8192),11/11 rows lower. The full repeat gives1.015450× (−1.521506%),10/11 lower; T32 is+0.013393% in the repeat. Across both pairs, the per-row geometric ratios yield1.014738× overall (−1.452397% latency); no row minima were selected. The8192-token speedup is1.0503–1.0681× with identical tactics across all four sweeps. Smaller gains remain close to run/tuning variation; two runs are not a statistical-significance test. `FINAL_PERFORMANCE.md` retains all56 measured row medians in one table; original JSON/cache artifacts remain under `logs/`.

Candidate Nsight Systems and full-set NCU captures completed using its original measured T128 cache. NCU kernel replay took22.88685 seconds with40 reported replay passes, versus the baseline's620.8757-second application-replay capture. The first kernel-mode command rejected the leftover application-only flag before launch; the corrected command omitted it. That parse failure is preserved. The reports have identical checked FC2 launch/resource geometry and zero local accesses. Their replay modes differ, so profiler duration/counter changes are diagnostic and do not establish the measured speedup. Six CTC metrics and absent source import are documented limitations; separate native captures carry source attribution.

Outcome: retained and committed as `968380de3b82650c0ea3b691ca235a728baf8acc`, pushed to `zianglih:perf/w4a16-split-megamoe-learnings`, and published as draft [upstream PR #5186](https://github.com/flashinfer-ai/flashinfer/pull/5186). Readback verified OPEN/draft, exact commit, three files/+9/−5 and an exact PR-body match (SHA256 `16caaef3ad0439cdf8cc473fd3c3c37d61c9094c7c9f56848ec40a72dce1ed26`). GitHub returned gateway/empty-response errors during creation; head-filtered readback was used before retries and ultimately found the single created PR. Source remains clean locally; the dedicated remote box was left idle on exact candidate bytes.

Compiler provenance: system/runtime CUDA remains13.2 (nvcc/ptxas13.2.78), while the installed CuTe DSL4.7.1 extension contains a bundled compiler identified as13.3.27 and the emitted PTX carries that version. The matched comparison holds this stack fixed; it must not be described as using system ptxas13.2 for CuTe code generation.

## Follow-up candidates

See `HISTORICAL_TRANSFER_AUDIT.md` and `HOST_EPILOGUE_TRANSFER_AUDIT.md` for source pointers and prior rejected experiments. The remaining short list is full physical-cluster feature alignment specialization, raw/SF release between TMEM store issue and completion fence, and independently fitted raw/SF versus BF16 activation ring depths. These are hypotheses, not measured improvements. In particular, early raw release before TMEM store issue and corrected SF byte accounting were already tested in the prior split effort and must not be presented as novel trials.

## 002 — Full physical-cluster feature bounds (retained for simplification)

Immediate baseline is retained commit `968380de3b82650c0ea3b691ca235a728baf8acc`. Recheck `remote-prep/full-m-recheck-completion001.json` confirms the same hu-pdx-43 node, eight GPU UUIDs, exact committed source bytes, package freeze, DSL compiler library and unchanged benchmark driver. All GPUs were idle; no new box was requested. Reuse the completed `logs/candidate-topk-repeat-ep8-fused.json` control (SHA256 `0fa87eb84e88ee1d58a80e0c88e72ff99769a2c9783096048e3048d05d64cf2e`). A textual Git diff hash mismatch came only from index abbreviation length and was resolved by comparing actual committed file bytes.

Candidate patch `candidates/cluster_m_alignment/candidate.patch` (`2ff0789eea34cb974861471edacaee8be009e82c90c44f0c5368dfec0a8e6324`) specializes only the Boolean full physical-cluster M span. It removes per-feature predicates/clipping on fully covered clusters, preserving runtime matrix dimensions, route guards and partial/padded paths. See the candidate README and source-review JSON for the geometry proof, cache separation, exact pins and independent review. The existing padding test now checks aligned→padded→partial→aligned widths with both finalize modes and retains all W4A4 cases. Source/syntax/scoped pre-commit passed before release.

The sole executor is running the 42 selected numerical/graph/EP cases, followed by the unchanged complete 14-row sweep if tests pass. Native captures compare fused2 and ordinary0 at M256/M288 against the existing committed top-k captures; M was dynamic in those controls. Native helper adds only optional `--m` and preserves its default geometry. No instruction-count, performance or retention claim is made before those results complete.

## 003 — Raw release after TMEM store issue (not retained)

`candidates/raw_release_after_tmem_issue/` contains a small independent source patch and design review. It moves the raw/SF consumer release after register-to-TMEM store issue but before the completion fence, preserving the decoded readiness arrival after that fence and preserving the existing SMEM source order. No pipeline stage, hook or tuning knob is added. Both decoder WGs participate through the original raw pipeline consumer-group arrival count.

The historical split release-before-store trial was rejected; MegaMoE retained this narrower issue-to-completion separation with only mixed marginal latency evidence. The new split trial is not yet applied or tested. Actual K-major/TMEM native ordering, phase reuse across multiple ring wraps, numerical checks and a complete comparison against the immediate retained source are required. There is no existing wrapper-level SMEM fixture, so its preservation is a source-order observation, not a measured native claim.

### 002 outcome and publication

The initial 42-case run passed 40 and failed two during H288 input construction before W4A16 kernel execution. The existing flattened grouped-weight fixture lacks independent expert scale padding for non-128 widths. The minimal test-only correction drops H288, retaining H256→384→256 cache/padded-peer coverage in both finalize modes and all W4A4 controls. No kernel/helper/tolerance change was made. Corrected patch `candidate-corrected.patch` (`3d65dfdc`) and `test-correction.json` retain exact pins; original failure artifacts remain. Corrected tests passed42,28 deselected,1420 existing DSL warnings in45.18s.

All four native captures completed. Aligned fused top-k2 decreases1584→1568 SASS rows; ordinary0 decreases1664→1624. Both M288 fallback SASS files are byte-exact to the immediate top-k controls, including encoding/scheduling, with normalized PTX equivalence. All checked registers/stack/local/static-shared resources and parameter declarations remain unchanged. Native scope is C1/static/no activation/PDL-off; it does not establish native C2/CLC coverage or actual dynamic-SMEM allocation. Fused address setup also changes uniform versus per-thread constant loads, so the count reduction alone is not a latency diagnosis. Full evidence: `native/CANDIDATE002_FULL_M_REVIEW.md`.

Two complete normal-AUTO sweeps versus the reused immediate top-k repeat gave +0.326679% and −0.010460% latency GM8–8192; each has4/11 lower rows. T8192 changed+1.3784% in the first and+0.0075% in the repeat. T16's first-run difference coincides with a different unchanged FC1 tactic; no source-caused improvement/regression is inferred from that selection. Full tables/source/cache checks are in `candidates/cluster_m_alignment/BENCHMARK_COMPARISON.*` and `BENCHMARK_REPEAT_COMPARISON.*`. Native reduction is real, but an additional end-to-end speedup is not demonstrated. Retained under the user's preference for clean compile-time instruction reductions with neutral measured performance.

Committed and pushed as `b90b34744491c36d0039f44cba664191f7bb0eb0`. PR5186 remains draft and its title/body/final table were refreshed. The final table compares two saved upstream488ff controls with both complete current-source sweeps, reports all56 raw medians and gives1.014052667× /1.385792639% lower latency over8–8192. Historical top-k final artifacts were preserved under `candidates/topk_constexpr/`. This is source-pinned reuse on the same verified stack, not a claim that the four runs were newly interleaved.

### 003 execution started

Applied the reviewed two-line-net raw-release change over retainedb90b3474; active patch `candidate.patch` SHAac1c7c073c15a6b122e30abdddb0c2530c0ae46fe51bda7521f1dcf850e6eca4. Source-review.json pins kernele2da53cf, hostaa446d91 and test8dc842e6. Source syntax/scoped pre-commit passed. The unchanged42 selected GPU cases passed45.63s. Four additional project-local large-K calls reuse the existing test class's unchanged numerical oracle (H/I8192,T17,E2,top-k2,C1/C2×ordinary/fused); they exercise32 K256 iterations and route tails without adding an upstream fixture. Benchmark/native results are pending. Immediate performance control is the complete candidate002 repeatd3e5068e.

### 003 outcome

All42 selected GPU cases and4 large-K reference calls passed. Native proof in `native/CANDIDATE003_RAW_RELEASE_REVIEW.md` shows exactly three instruction slots reordered in each checked kernel: finalSTTM → raw arrival with wait mask0 → completion fence writing dependency2 → decoded arrival waitingmask0x4. The last raw LDS precedes this sequence, both decode WGs use the same loop, and all other instruction encodings/scheduling are byte-identical. Counts1568/1624 and checked resources remain unchanged. The intended overlap was compiled correctly.

Two full14 normal-AUTO sweeps versus the reused complete candidate002 repeat show +0.161942% and +0.322024% latency GM8–8192 (7/11 and6/11 lower). T16 uses a different autotune choice; other differences remain mostly small, but neither aggregate demonstrates a gain. Tables/cache/source checks are in the candidate directory. Do not infer that the intended overlap was absent: native evidence directly proves it.

Not retained: no demonstrated end-to-end improvement or instruction reduction justifies changing the published pipeline ordering. The exact patch, native proof, all numerical logs and both complete sweeps remain local for future reference. Restored the live local kernel to retainedb90b3474 before preparing the independent ring-depth trial. No raw-release commit was published, so PR5186 and its final table remain on the bounds/top-k implementation.

## 004 — Unequal raw/SF and activation ring depths (not retained)

Based on retainedb90b3474, after rejecting/restoring candidate003. `candidates/unequal_raw_b/source.patch` d4f45ab8 / activecandidate.patchdc895837 produces kernel7a2bf6ca; host/tests remain unchanged. Source-only layout/fitter/binding analysis and independent review passed, followed by scoped pre-commit on the live local candidate. The expanded layout helper calls exactly mirror installed DSL4.7.1's existing A/A-transform/B helper body. No public knob, tactic or device-loop algorithm is added.

Preserve the original paired fit and all B/decoded/ACC/C depths. Only fused finalize can spend unused conservative capacity on one extra raw/SF slot. The original BF16-width SF capacity charge and all1024-byte allocation alignment remain. The general residual rule changes M128/N16 raw7→8/B7, M128/N128 raw2→3/B2, and M256/N32 raw7→8/B7. The other27 mode/family rows are unchanged; full table/proof under the candidate directory. Static residuals are not measured dynamic-SMEM allocations.

Before mutation, the sole executor restored exact retainedb90 source and captured an actual fused2/M256/N16 native control; result0d205a8a under `native/baseline004-fused2-m256-tile-n16/`. The existing candidate002 fused2/M256/N64 native capture remains the ineligible control. Native helper adds only optional--tile-n, preserving default64; helper0798c673 and earlier versions are saved. No baseline benchmark was repeated: reuse the complete candidate002 normal-AUTO repeatd3e5068e.

Released42 existing selected tests plus6 project-local calls using the unchanged numerical oracle: allthree changed families, both finalize modes, H/I8192, E2/top-k2, route-tile+1 tokens,32 K256 iterations. This specifically covers unequal8/7 and3/2 wraparound; ordinary modes are controls. Full14 normal-AUTO100CUPTI sweep and two native captures follow passing numerics. Performance, actual allocation and retention remain pending.

### 004 outcome and finalization-mode priority

All42 selected tests and all6 large-K calls passed, including allthree changed fused families and ordinary controls. Native confirms unequal raw/B8/7, decoded3 and ACC2 in N16, correct independent wraps/tails, unchanged per-stage raw18432/B8192 transaction bytes and exact parameters. N16 increases1616→1632 instructions, with checked registers/stack/local unchanged. Ineligible N64 SASS is byte-exact to retainedb90 (normalized PTX exact). The implementation achieved the intended allocation/protocol, rather than silently falling back.

Two full14 fused-finalize sweeps versus reused immediate control show +0.069194% and −0.028030% latency GM8–8192 (5/11 and6/11 lower): no material end-to-end gain. NSYS actual selected T128 FC2 uses209984 dynamic shared bytes versus the prior191552: +18432 bytes, matching one physical raw/SF tile; grid2×1×74,512threads,128registers and no local memory remain. Full NCU diagnostics are finishing on the fixed candidate/cache.

Not retained: extra stage/storage/instructions and implementation bindings did not yield a useful measured gain. Exact patch, proofs, numerical/benchmark records and diagnostic profiles are preserved. Local source restored to retainedb90; remote source restoration follows the already-running NCU capture so that its source provenance stays exact. PR source/final fused table remain b90.

User steering: evaluate fused and non-fused finalize separately, with non-fused finalize the primary retention target for the RL precision use case. Existing fused measurements do not establish non-fused speedup. Next work establishes complete1–8192 non-fused upstream488ff versus retainedb90 comparisons under the identical GPU/compiler environment, preserving its FP32 accumulation/reference contract. No timing ratio will mix finalization modes.

## Non-fused primary baseline and deterministic combine contract

User priority: evaluate finalize modes separately; optimize non-fused first. Non-fused combine must remain deterministic with FP32 accumulation. TMA reduction/atomic BF16 combine is not permitted in this path. Current ordinary implementation writes alpha-scaled BF16 expert scratch, then the unchanged per-token `moe_unpermute` loops top-k in fixed order using private FP32 registers and casts once to BF16 output. It does not retain expert outputs in FP32.

Both whole 1–8192 non-fused source arms completed on hu-pdx-43 with normal autotune, ten warmups and 100 CUPTI iterations, source/cache/histogram/protocol checks passing. Upstream488 result `8840cdf9`, retainedb90 result `50fdb26f`; wall49.32/49.34s. Geometric speedup8–8192 is1.002697× (−0.268941% latency),6/11 lower; one run each and no significance claim. Full14 table and exact pins: `candidates/nonfused_baseline/BENCHMARK_COMPARISON.md/json`. This is the saved immediate non-fused baseline for future trials.

Candidate005 changes one existing epilogue branch condition to allow plain TMA stores for fully valid prefix subtiles in a route tail. This is a memory-copy optimization into unique scratch, not a combine operation. Both original store bodies and reducer remain unchanged. Held source/test patch417f1fb6 has passed local AST/syntax/lint checks; source review proves geometry and C-ring safety. Before/after repeated bitwise and native plain-store checks are pending before performance evaluation.

### 005 numerical/native and first performance result

Scoped pre-commit passed.6 forced N64/N128/N192 × top-k2/3 cases, tails33/65/97, each with3 repetitions atPDLoff/on:36launches perarm. All retained/candidate outputs match bitwise and unchanged reference checks pass; input tensor hashes/scalar arguments agree. Before result98e2dc4d, afterc5d26f27; allCPU bundles downloaded. Expanded existing suite:66passed,28deselected, no tolerance/oracle change.

Native005 proofc9ed61e7 confirms actual ordinary plain shared→global `cp.async.bulk.tensor`/`UTMASTG.2D`, no TMA reduce, correct per-subtile boundary, C-ring count/commit/wait/drain and last ACC release. OrdinaryC1N64 remains1624SASS instructions;REG128/STACK0/LOCAL0 and all23paramsunchanged. FusedN64 rawSASS whole-byte-identicalb90(1568).

First complete nonfused14row resultbba15abc:48.67s, versus retained50fdb control, latencyGM8–8192−0.003383% (neutral). Actual high-N rows1024/2048/4096/8192 all improve0.6–1.2%;2048/4096/8192 retain the same tactics,1024changesGEMM2M128→256. Small8rowregresses~2.8% despiteN16single-subtile semantics unchanged;16/512select different tactics. Full table/pins under005/BENCHMARK_COMPARISON.md/json. One repeat and ordinaryN16 nativeidentity requested to resolve this mixed result; no retention decision yet.

PR5186 body updated at retainedb90 to separate non-fused primary and fused full14tables; readbackexact, draft preserved. BodySHAe501ee922bbb320e018852657f2be86e1b8b4ee9359218889588f37dd08a21c0. Nocomments.

### 005 retained as88ff7db6

Second complete candidate sweep6122a952 had0.061598% higherGM latency8–8192 against saved50fdb;1024/2048/4096 repeated their gains, but8192was649.079µs vs firstcandidate626.438µs with unchangedtactic. Fresh fullcontrol/candidate pair d1070259→85329501 resolved the retention decision:182.1295→181.3775µs at1024;224.594→222.066 at2048;329.219→325.907 at4096;628.0225→625.494 at8192. Complete14table `BENCHMARK_REFRESH_COMPARISON` has1.003451× /−0.343890% latency8–8192,8/11lower. Neither rows nor controls were mixed. The8192variation is preserved and no stablegain is claimed there;1024–4096 gains reproduced across allthreecandidate sweeps.

OrdinaryN16 full rawSASS/resource identity confirmed againstb90; normalizedPTXexact. Addendum570cdf60. Thus lowN instructionchanges do not accountfor run/tacticvariation. Retained the clean single-condition change (no extra resource/instruction cost) plus existing-test tail product. Commit/push88ff7db6a558e8acbc0cd964275410cf94e5c22c. Full PR cumulative non-fused comparison uses saved upstream8840cdf9 vs latestwholecandidate85329501:1.005561× /0.553015% lowerlatency8–8192, with explicit noise limitation. Fused table reusesb90 sweeps becauseSwiGLU fusedcodeunchanged; no new fusedtiming claim.

Candidate006 applied locally over88ff for inspection: unroll_full ordinary epilogue hint, source6db190f3 and patchcbb4e1ce. Scopedprecommitpassed. Current-best005 non-fusedNSYS/fullNCU and additional ordinaryN128MMA256/C2 nativecontrol are requested before006nativevalidation. Extended nativehelperbd857f38adds explicit --mma-m/--cluster-m, retains previousdefaults and real maximumactiveclusterquery; prior0798helper savedasremote-prep/capture_split_topk-v3.py. Benchmarkdriverunchanged.

Current-best005 nonfused T2048 profiling completed/downloaded: `profiles/retained005-nonfused-t2048-nsys.nsys-rep` and `...-ncu.ncu-rep`; NCU fullreport15cf98bc,40kernel-replaypasses. Savedrowcache6f49aad6, no autotuning, exactsource88ff bytesbefore/after. ObservedFC2symbolunique atT2048, so NCUskip0/count1 (unlikeoldT128skip1). FC2 grid2×1×74,cluster2,512threads,128registers,222208dynamic+1024driver bytes andzerolocal-memorysectors. NSYS also captures unchanged per-tokenFP32 moeUnpermute with256threads and38registers. Firstfill kernel is coldL2flush, not outputfinalization. Six CTCmetrics unavailable; no importedsource innormalJIT, separate nativeexportsavailable. Profiling latency not usedforretention.

### 006 unroll outcome: not retained

Actual native expansion confirmed: N64/C1 ordinary1624→1824staticinstructions, N128/MMA256/C2 ordinary1736→2360; exactlyone last-load ACC fence/release, C-statejoins and finaldrains preserved. FusedN64 wholeSASSexact; no resource/parameter/spill growth. Nativeproofbb5b7e70. Sixbitwisecases/36launches remainexactbefore/repeats/PDL(result3af0b367),66selectedtestsPASS48.40s.

Full14resultd1f4bd9f versus retained005refresh85329501 shows−0.079706%GMlatency8–8192. ChangedN64/N128workloads:1024~unchanged,2048−0.35%,4096−0.24%,8192+0.17%; differences small/mixed. Addedstaticcodefootprint lacks a useful measuredgain. Notretained; sourcepatchcbb4e1c/active6db190f3, native/runtime/wholebenchmark artifacts retained. Localkernel restored005 then007 applied independently; no unrollhint enters007.

### 007 useful-subtile bound: active

Heldsource106b0770 appliedover88ff→ae6ef44c. General ordinarynongatedbound excludes allnewmath forsingle-subtileN8/N16/N32atcompiletime. ForlargerN, clampvalidroutes[1,N] beforeceildivision byconstant epiN. Publicrouting guaranteespositiveD; privateD0metadata otherwise skipsACC release, hence lowerclamp1 preserves progress. Existingloop/body/rounding/reducer stayunchanged; finalACC fence/release shifts tolast usefulTMEMload. Sourceproofandindependentreviewe1920c49, scopedprecommitPASS. Native sequencec1f36815 verifiesrestorationfrom006 andcapturesN64/N128C2/ordinaryN16/fusedN64 before runtimevalidation. PrivateD0 helpera4d8b3a isheldfor4probe+oraclecasesunderprocess timeout; no newupstreamtestfile.

### 007 validation and first sweep

The combined native review passed (`native/CANDIDATE007_USEFUL_SUBTILES_REVIEW.md`, SHA256 `a31a62abae59e9dd87aabedf67cf75a8385f3b4f5346816267396a33d18282e8`). Changed ordinary N64 and N128/C2 use the intended clamp/add/shift loop bound, add eight static SASS instructions, preserve parameters and REG128/STACK0/LOCAL0, and release ACC exactly once after the last executed TMEM load. Plain TMA stores, C-stage joins and the final drain remain intact. Fused N64 and ordinary N16 SASS are byte-exact to retained005. No output reduction was introduced.

Four private zero-route probes passed with unchanged sentinel output and progress, including PDL off/on; the original four numerical-oracle cases also passed. Six forced tail configurations passed 36 bitwise comparisons against original b90, repeats and PDL settings, all with zero difference. Existing selected tests passed 66, with 28 deselected, in 44.96 seconds. References and tolerances are unchanged. Exact result hashes and source/idle checks are bound by `remote-prep/candidate007-completion001.json` (`9dc7651899565ebd34de5dc4d97a093fae51c13055ee6d66aa431ad8b8966e97`).

First full non-fused sweep: `logs/candidate007-useful-subtiles-ep8-nonfused.json`, SHA256 `0673dacda369c4f6db2b7c31cb4440da4c324bbdb83003a85d34dd5c98d99e5c`; 42.17 seconds driver / 49.28 seconds outer. Against the complete retained005 refresh control `85329501`, geometric latency over 8–8192 is 0.104435% lower, with 6/11 rows lower. T1024/2048/4096/8192 improve by approximately 0.12%/0.18%/0.30%/0.58%. All 14 medians and source/cache/protocol verification are saved in `candidates/nonfused_skip_invalid_subtiles/BENCHMARK_COMPARISON.*`. These small differences do not establish significance.

A single complete 1–8192 confirmation sweep is authorized on unchanged007 to determine whether the larger-row gain repeats. Reuse the complete005 control; do not rerun fused mode, probe individual rows or select row minima. Retention is pending.

### 007 outcome: not retained

Confirmation result `logs/candidate007-useful-subtiles-repeat-ep8-nonfused.json`, SHA256 `60f8bd7539d7f311004b1be5d636816d45e8e2223ebdaa0cf61f6dc65f0a9b2d`, completed all 14 rows with normal AUTO and 100 CUPTI iterations; 42.11 seconds driver / 49.03 seconds outer. Source, all row-cache hashes and idle closure passed. Completion receipt: `remote-prep/candidate007-repeat-completion001.json`, SHA256 `bc39cf4593276ac7ebb95fdeeb58483fb8e4ac5ee8d6e36b146833f53df40fc6`.

Against the same complete005 refresh control, repeat geometric latency is 0.208398% higher over 8–8192, with 7/11 rows lower. T1024/4096 improve only 0.071%/0.133%, T2048 is 0.029% higher, and T8192 is 643.4625µs versus control625.494µs / first candidate621.862µs. Similar 8192 variance occurred on retained005; do not infer a proven source regression. The complete repeat comparison and its protocol/source checks are saved in `BENCHMARK_REPEAT_COMPARISON.*`.

The changed FC2 path is selected only at T1024/2048 (N64) and T4096/8192 (N128). Smaller rows use compile-time-excluded N8/N16/N32. In the first sweep, T2048 changes FC2 M128→256, while T1024/4096/8192 retain exact tactics. All rows remain in the full reports.

Decision: do not retain007. Native proof confirms the intended work reduction and correct progress, rather than an implementation fallback, but the repeated gains are too small/mixed to justify the additional dynamic bound calculation. No further repetitions are justified to chase this difference. The live local source was restored exactly to retained005, Git is clean, and remote restoration was requested separately. No trial007 commit or PR performance claim was published. The source, native exports, numerical logs, both full sweeps and proposal history remain preserved.

PR5186 readback remains OPEN/draft at `88ff7db6a558e8acbc0cd964275410cf94e5c22c`; its published body matches local `PR_BODY.md`, SHA256 `aefec6521320dcf0be8cb4e250903fc755f581ad3da9f9369a2214625fb4874b`. Its final tables therefore still describe retained005. The downloaded retained005 full NCU/NSYS profiles remain current for that source.

Remote restoration completed with exit0: only kernel `ae6ef44c`→`1fe29f6f` changed; host `aa446d91` and tests `102a3501` remained exact. All eight GPUs were idle with no compute processes. Receipt `logs/candidate007-restore001.json`, SHA256 `d22cf5a8f78e9e97a8a3fabe1df58b8b5ef9a7e514946a4b953e4ff2d0e94a0e`. No numerical or benchmark workload was rerun after the byte-exact restoration.

Independent repeat tactic review confirms all four affected rows exactly match their005 control tactic pairs. T8192 also matches the first007 tactic, so its variability is not a tactic switch. T1024/4096 repeat gains remain 0.070571%/0.132553%; T2048 is 0.028595% higher. The independent retention recommendation agrees with rejection and no further repeat.
