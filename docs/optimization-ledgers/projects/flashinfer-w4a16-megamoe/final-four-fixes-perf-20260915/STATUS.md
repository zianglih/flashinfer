# Four correctness fixes: measurement and conditional optimization

Current work: finish HashInfer Compute Sanitizer coverage, measure the upstream
four-fix performance cost, and reduce that cost if fresh measurements establish
a regression. Published branches retain the four fixes; the local paired
checkouts include the unpushed FC1 wait-deletion trial.

- Before: `7f1a093119f12b1f5b79d50bf6d0c951069224e5`.
- After: `a48e5706c2a7775b0b698aa8eccb4e124b02118c`.
- Both use the identical current benchmark with untimed weight PDL disabled.
  The source audit isolates the four kernel fixes in three owned files.
- The reviewed protocol is four complete Mega-only AUTO/O3 sweeps in A/B/B/A
  order, 1–8192 global tokens, EP8/B300/CUDA 13.2. Preserve every row, tactic,
  sample and output. Invalid baseline rows receive no clean speedup claim.
- Source and runtime CPU checks passed. Fresh ABBA measurements and full raw
  collection are complete:56 rows,5,600 samples,448 saved rank/token outputs,
  32 full tensor files. All checks pass, including independent raw-sample
  arithmetic and root rehash of98 files. See [the full result](RESULT.md).
  Aggregate8–8192 is1.001016x before/after, with same-tactic both-order
  regressions at4/32/128/512. The128 and512 rows are3.54%/4.78% slower.
  PR5019 contains this table and remains ready at a48; `publication-check.json`
  records exact readback. Candidate979 (paired Hash ec60097) removes only the
  early duplicate FC1 wait; it is local/unpushed. Ordinary O3 codegen at
  128/512 tokens preserves all 32 rank/token output checks and changes all
  16 kernel pairs: two interior NOPs disappear and some local scheduling changes,
  with identical total opcode counts. All 175 evidence files are collected and
  independently verified. This is not a speedup claim. The first full AUTO 1–8192 candidate sweep passed all output checks but
  was mixed: 128 tokens 1.0431x, 8–8192 aggregate 0.988955x versus reused
  a48 B1/B2. All raw evidence was collected. A repeat candidate sweep followed
  by a fresh corrected baseline sweep is running on the same node. See
  [the codegen result](fc1-wait-candidate/CODEGEN_RESULT.md).
  The former second devbox disappeared before staging. Its prior raw validation
  evidence was already collected. Replacement `hashinfer-perf-cu132-0916`
  (`c2/infra`, `hu-pdx-69`) is ready: pinned dependencies, both source trees,
  fresh boot/8-GPU identity, driver and compiler checks passed. The versioned
  configuration is under `replacement-node/runtime/`; original helper files
  remain archived unchanged. Real import/serialization preflight passed.
  Supervisor PID5482/start262234767 launched at epoch1789524112.6089;
  boot `7f67e9f6-5016-4598-8050-a93beafdb59f`. Exact identity and command:
  `replacement-node/runtime/box2-dispatch.json`.
- The original box continues the unfiltered EP4 racecheck. Current-source EP8
  guarded memcheck and racecheck remain planned after performance completes.
  Their preparation is in the sibling HashInfer project's
  `current-sanitizer-completion-20260915/`.

If any valid individual row shows a repeatable regression, distinguish changed
autotuner selection from same-tactic overhead before editing. Start with the
FC1 duplicate-wait candidate, then consider FC2 transpose batching or fence
scheduling only with evidence. See [the refreshed candidate analysis](OVERHEAD_CANDIDATES_A48.md).
Required ordering, corrected warp-row addressing, elected scheduler publication,
and deterministic FP32 combine remain correctness constraints.

Two separate alternatives remain unapplied: [paired FC2 transpose rounds](fc2-paired-transpose/README.md) and [earlier proxy-fence placement](proxy-fence-placement/README.md). Neither adds a public tuning knob or changes register allocation.

Additional local/unpushed non-kernel commits f3a3e714 (native) and 8b1539f (HashInfer) tighten CUDA-input validation; native also scopes NCU requirements to executable EP cases. Scoped checks and the full native validation file pass:40 passed,1 deep_gemm skip. GPU4 was visible only on the separate sanitizer node for package import and returned idle; this was host/API validation, not kernel numerical validation. Published branches and frozen runtime sources are unchanged. See [review followups](review-followups/README.md).

## 2026-09-16: FC1 retention and FC2 trial

Fresh full C2→B3 sweeps passed all 28 timing rows/2800 samples/224 output checks. Same selected tactic in each paired row. The FC1 wait deletion gives 0.991751455 geometric B3/C2 speedup over 8–8192; the initial 128-token gain did not repeat. Fresh B3/C1 is 0.999147343. Historical t8 regression was baseline drift; no benefit supports promotion. Complete paired evidence (70 files/16 raw tensors) was independently rehashed locally. Preserve trial on archive/fc1-wait-trial-20260916 in both repositories and restore FC1 wait.

Replay only the independently tested host/API fixes onto the original corrected baselines: native 7717228f, Hash e0f6b4c. These commits are pushed; public 5019 remains ready and Hash2 remains draft. The 40 passed / 1 skipped native validation-file result was obtained on originalf3a3e714; its validation/test files are unchanged by replay, and no kernel-performance claim is attached.

Paired FC2 transpose waits now exist locally as native 71f94c12 / Hash f14a1b1, unpushed. Source/address/ordering reviews and scoped pre-commit pass. FC1's early wait is retained. Ordinary O3 codegen/all-four-tactic numerical/resource checks are next; no performance or sanitizer qualification is claimed yet. Original 224b EP4 unfiltered racecheck continues unchanged.

## FC1 preference update

After reviewing the full original and confirmation table, the user prefers a correct redundant source-wait removal even without a clear timing gain. Revisit after the isolated FC2 trial, add the short ordering comment, and qualify the final combined source. The current FC2 measurement retains the early FC1 wait; the previous no-promotion decision is deferred, not treated as final. Prepared patch: fc1-wait-candidate/reconsideration/candidate.patch.

## 2026-09-16: FC2 generated code and combined cleanup candidate

Native71f94c12 versus a48 passed all four fixed tactics at1024/8192:128 exact output/capture checks,64 executable comparisons, all normal exits. N64 epilogue/dispatch PTX load/store waits18/14→15/11 and SASS TMEM fences14→11. N128 epilogue/dispatch32/26→26/20 and26→20. All paired resources remain REG96/STACK0/LOCAL0/SHARED1024 with unchanged epi144 policy and no LDL/STL. Instruction slots include padding; no speedup is inferred. Full715-file/104,318,303-byte local collection and archive rehashed by root;64 full trial tensors remain remote with whole-file proof bound before/after collection. Full report: fc2-paired-transpose/codegen/RESULT.md; qualification7569b14d.

The user prefers keeping the correct redundant FC1 source-wait removal as a simplification, even without a clear timing benefit. Added the requested two-line ordering comment and reapplied in separate local native8da5ab77 / Hash1887e093 commits atop71f/f14. Scoped pre-commit passes and paired epilogues normalize exactly. These combined candidates remain unpushed. Isolated C3 timing remains frozen on71f against fresh a48 B3; combined strictEP4 will use1887 onBox1 GPUs4–7 while the existing224b race continues0–3. Long guarded runs wait for final performance selection and same-source ordinary qualification.

## FC2 timing and combined qualification

The isolated C3 sweep completed with all 14 timing rows, 1,400 samples and 112 exact/finite/repeat output checks. All selected tactics match B3. B3/C3 geometric speedup over 8–8192 is **1.006700735x**: seven rows improve, while 1024/2048/4096/8192 are 2.86%/1.10%/0.65%/1.12% slower. This is one candidate sweep against the preserved same-node B3 baseline, not statistical proof. Full rows: `fc2-paired-transpose/perf/terminal-table.md`. Terminal raw collection and independent closure are pending.

Retain paired FC2 for combined qualification because code generation demonstrably removes completion fences without changing resources, and the timing result is mixed but slightly positive overall. Authorized one full C4 sweep of native `8da5ab77` after C3 collection and closure, comparing every row with both B3 and C3. The removed FC1 early wait remains a source cleanup with no timing gain claimed.

Combined HashInfer `1887e093` strict EP4 is running on Box1 physical GPUs 4–7, separate from the original `224b` racecheck on GPUs 0–3. It covers all 30 EP4 cases, all four tactics, O2/O3 and eager/graph using strict BF16-bit reference and repeat checks. Once that exact source passes and the evidence is collected, its guarded EP4 run is authorized with fresh scoped idle/UUID/process/port checks. The original racecheck remains unchanged; an unrelated busy GPU must not be silently hidden if it affects that older harness's all-node idle closure.

The user clarified that the headline **BEFORE always means `7f1a0931`, before all four correctness fixes**. B3 (`a48e5706`) is only the corrected control for isolating an optimization. `LATEST_BEFORE_AFTER.md/json` now derives the original A1/A2 geometric latency versus latest completed C3: 0.997443x over 8–8192. All tactics match. Two earlier BEFORE sweeps versus a later candidate sweep retain a temporal-drift limitation. Refresh this same original-source comparison after C4; do not silently substitute B3 as BEFORE.

C3 collection is complete and independently rehashed locally: 56 files / 240,007,181 bytes, including eight full output tensor files. Archive SHA256 `80502aee4c3bf8ec93a1120aaf09a212b55879922b348e8422240cd6c6125968`; post-collection closure `c1d3450b9ee60c6fe122025efea29989727d05a531187e133a8d597b1b07b039` verifies the expected node, closed process groups and all eight GPUs idle. C4 staging is authorized and underway.

## Combined C4 result and retention

Combined native `8da5ab77` passed all 14 timing rows / 1,400 samples / 112 exact finite/repeat output checks. The complete archive has 58 files / 242,108,383 bytes, including eight full tensors; root independently verified all hashes, closure and table arithmetic. Archive SHA256 `0ba43cec7fd994bd4430e6fc18b3f48a0bb10d77b793f04a82b557f7a41c10af`. The requested original BEFORE versus combined AFTER and FC2-only versus combined AFTER table is `combined-candidate/perf/FINAL_COMPARISON.md/json`, also copied to `LATEST_BEFORE_AFTER.*`.

Over 8–8192 tokens, original BEFORE/C4 is **0.995549899x** and FC2-only C3/C4 is **0.998102277x**. Corrected a48 B3/C4 is 1.004790296x, retained only as an attribution control. All tactics match. Individual changes remain mixed, and the later single candidate sweeps do not cancel temporal drift. Retain both changes for final qualification under the user's preference for correct source simplification; no uniform gain or statistically established aggregate difference is claimed. The FC1 comment explains that the remaining R1 wait completes loads before scratch overwrite.

Combined Hash `1887e093` strict EP4 passed 30 cases / 480 configurations / 5,040 exact BF16-bit comparisons / 1,200 repeats. Its 191-file archive and scoped GPU/process closure were independently verified. The original race continues on GPUs 0–3. A guarded EP4 preflight failed before launching because it expected the strict-audit command without the runner's `-B`; a minimal helper-only successor corrects the prefix and tests the real collected summary. Guarded v2 launched at epoch1789536363.11, PID362485/start270678285, on GPUs 4–7, with source, tests and sanitizer options unchanged.

Box2 ownership transferred after C4 collection/idle closure to the native28 → strict EP8 sequence. A one-time final Split-only sweep is being prepared for the final PR table, to avoid combining old hu112 Split timings with hu69 Mega timings. It will not overlap validation or sanitizer GPU work.

## User decision: restore the FC1 early wait

The user rejected the FC1 removal because every 8–256 decode row regressed against FC2-only C3. Restore the early wait and add the requested explanation that only register work precedes `r1_store()`'s overwrite-protection wait, so the early wait is removable for correctness but retained for measured decode performance.

Selected local commits: native **`4d183b836bb8ceefea2fcd723f078b3a4935e6b6`**, Hash **`dbd3cead8837a251d7fcefc57a79b8d7cc87e5af`**. Exact Python ASTs match measured FC2-only 71f/f14; only comments differ. Paired epilogues normalize exactly, scoped pre-commit passes and both trees are clean. No kernel optimization is pushed yet. `fc1-wait-candidate/restored-wait/decision.json` supersedes the combined-retention decision.

The C4 tables, strict1887 EP4 pass and active1887 guarded EP4 are preserved as rejected-candidate evidence. Already running native8da28 will finish/collect; combined1887 strict EP8 was never launched. Remaining validation is redirected to selected4d/dbd, using unchanged test coverage and sanitizer options. Original224b long racecheck remains running. Headline selected performance reuses measured71f C3 explicitly, not fabricated new timing for the comment-only commit. Final Split preparation now targets selected4d with measured71f Mega as the same-node comparison.

## Selected native validation complete

Selected native `4d183b83` passed the unchanged 28 logical cases / 45 rank executions on hu-pdx-69: EP1 oracle 8 passed (133.50s), EP1 graph 3 passed (42.15s), EP2 routing/tails/graphs 17 passed per rank (139.70s each). Root rehashed all 25 raw artifacts and verified current hidden imports, launch source, source gate and terminal process/GPU closure. Historical selector catalog embedded in closure is distinct from the selected execution provenance. See `selected-candidate/native-tests/root-collection-review.json`.

Selected Hash `dbd3cea` strict EP8 launched on the same node after native collection and all-GPU idle closure (supervisor171898/start263643222; dispatch041e8395). Selected EP4 remains queued behind completion/collection of the rejected1887 guarded EP4 on the other node. No new timing or sanitizer pass is inferred.

## Selected EP8 strict pass and Box2 handoff

Selected Hash `dbd3cead` passed the EP8 half: all 30 cases, 480 tactic/O-level/eager-graph configurations, 5,040 finite BF16-bit comparisons including signed zero, and 1,200 repeat checks. All 195 raw files / 31,054,387 bytes and archive `8fd2417e9428274e9141b5320a2964d2d08cf12c2cff1a4a203ad4720ffe74ad` were rehashed by root. Snapshot: `hashinfer-w4a16-megamoe/selected-final-qualification-20260916/evidence-ep8/collected/20260916T061839Z-8281057a880e4fc7ba30c95d238f213f`. Closure `2ee05e35` verifies all eight GPUs idle and owned processes absent. This is EP8 only; selected full60 awaits EP4.

Rejected `1887e093` guarded EP4 completed all four cases with four zero-error memcheck summaries and exact 192 reference / 480 pair / 160 repeat checks. Root rehashed 835 files / 532,075,355 bytes; archive `4685581e` remains labeled rejected-candidate evidence. After its collection and scoped closure, selected `dbd3cead` strict EP4 launched on Box1 GPUs4–7. Original224b race0–3 remains unchanged and incomplete.

Box2 is reserved for the authorized final Split sweep, then selected guarded EP8 owned by o2. Both source trees remain unchanged/unpushed while qualification completes.

## Retained change published (2026-09-16 06:55 UTC)

Native `4d183b836bb8ceefea2fcd723f078b3a4935e6b6` is pushed to public PR5019, which remains ready. Hash `dbd3cead` plus README-only `1ba33fafd50b9920c22ffabacfd9288b16c013b0` are pushed to HashPR2, which remains draft. Both refreshed bodies were read back and verified; no reviewer comments were posted. Hash's ledger points to native4d; runtime validation stays frozen at dbd. GitHub CLI identity was restored/verified as zianglih.

Selected full60 union audit passed: two independently completed/collected EP4+EP8 runs, 960 configurations,10,080 finite BF16-bit comparisons including signed zero,2,400 repeats, all errors zero. Source/helper and scoped process/GPU closure are verified. The union preserves the separate raw runs rather than inventing a single driver execution. `hashinfer-w4a16-megamoe/selected-final-qualification-20260916/FULL60_UNION.json` SHA07929a39.

Final Split S1 at native4d is fully collected:14rows/1400samples/112 outputs,58files/239,213,702B, archivef50bf3a7, closured0f0ec4d. With measured71f C3 Mega, all11 retained8–8192 rows favor Mega; geometric Split/Mega1.099079653. The complete 1–8192 table replaces the historical hu112 table in PR5019. Original BEFORE remains7f1a0931; its geometric A1/A2 versusC3 comparison stays0.997442769. Sequential sweeps retain temporal-drift limitations. S1 took1293.75s including first-use Split compilation; setup is outside timing.

Selected guarded EP4 and EP8 are running. The original224b unfiltered EP4 race continues unchanged through its existing8h bound. A separately labeled full1/16384 selected-dbd EP8 race successor will run after same-source guardedEP8 pass/collection/closure, changing only the CPU analysis-worker setting to4. This uses the second node without changing the original run, preserves INFO/full/unlimited reports, ordinary O2/O3 and full strict reference, and is not a causally isolated worker-count comparison because kernel source also differs. No sanitizer-clean claim is made while pending.

## Selected guarded qualification published (2026-09-16 08:03 UTC)

Selected dbd guarded memcheck passed EP4 and EP8: eight cases, 128 eager/graph configurations, 384 reference checks, 960 output-pair checks and 320 repeat checks all finite BF16-bit exact, including signed zero. Every one of the 12 rank logs ends with zero errors. All five supervisor phases pass in each batch. Full raw/codegen collections and source/process/GPU closure are verified; EP4 root rehashes and EP8 independent local rehash/checker replay are retained. Archive SHA256 prefixes: EP4 `02fea0f5`, EP8 `5e2e7e3e`. Complete records and scope limits are in `hashinfer-w4a16-megamoe/sanitizer-guarded-selected-final-20260916/SELECTED_RESULTS.md`. EP8's first collection transport timeout is preserved; only the collection timeout changed for retry, with no GPU rerun or runtime change.

Both PR bodies now include the selected guarded passes; public5019 remains ready at4d, Hash2 remains draft at README-only1ba. Body readbacks/heads/statuses are verified in `guarded-publication.json` in each draft folder. Public GPU CI is pending maintainer authorization; pre-commit/API/docs checks passed. No reviewer reply was posted.

The new final-FC2-wait bot finding was independently reviewed and requires no change in the current call chain: PTX preserves same-thread true register dependencies, and existing final-valid/final-skipped waits precede every accumulator release. Disjoint scratch regions and next-round waits preserve memory anti-dependencies. Full source/spec/path audit: `fc2-paired-transpose/final-wait-review/ASSESSMENT.md`.

Selected dbd worker4 EP8 racecheck launched after guarded collection and fresh idle closure at epoch1789545689.5302, supervisor218829/start264392459; dispatchSHA3e58fd1b998ae58687ec3b210867323129e206c029dc8135044f24c7c8a3dc35. Four full-reference random/skewed 1/16384 cases, all tactics/O2/O3/eager/graphs, ordinary compilation and unlimited INFO reports remain unchanged. The checker remains strict; any INFO hazards will be retained as non-clean evidence rather than suppressed. Original224b EP4 continues independently to its unchanged outer deadline09:05:17 UTC. Neither race run is complete.


## CUDA13.0 refresh requested (2026-09-16)

User explicitly requested another CUDA13.0 devbox and current-fix Split/Mega PR table. Managed h request flashinfer-cu130-0916 uses explicit nvcr.io/nvidia/pytorch:25.11-py3 after live NGC/release checks; CUDA13.0.2 is provided by25.11, while25.12 moves to13.1. Eight B300, bare, no explicit size. First ziangli request had0/8GPUquota and was deleted before the infra retry; its local waiter was stopped. The infra earth request has quota but currently lacks a fitting physical node. Details/logs are in cu130-final-refresh-20260916/REQUEST.json. CurrentCUDA13.2 racechecks continue unchanged.

CPU preparation targets native4d with the prior cu130 stack preserved, native28/default-compiler plus six decoder cases, then same-fixture nonfused Split+Mega full1–8192 AUTO sweep with3 warmups/100 cold-L2 graph CUPTI samples. No refreshed CUDA13.0 results are claimed yet.


## CUDA13.0 setup qualified (2026-09-16 08:48 UTC)

The new infra devbox is admitted on hu-pdx-112, boot2290feda-df27-4c66-8c27-dd44d27e3bf0. Fresh8-B300 identity and all-GPU idle checks passed. CPU-only setup completed20 steps; root independently verified all31 collected raw files, archive33643452, setup source4d/4896files and setup-process/GPU closure. ImageTorch2.10.0a0+b558c986e8.nv25.11 and systemCUDA13.0.2 remain unchanged. LoadedCuTe4.7.1 cu12 nativecompiler12.9 has SHA77f8826a and direct-BF16 decoder=false. Actual loaded libraries are NCCL2.28.8, NVSHMEM3.4.5 and CUPTI2025.3.1 (PythonCUPTI13.0.1); packageversions are recorded separately. Environmentproofa4fe60e4/nodeproof04e2ad68. Fullsetuprecords: cu130-final-refresh-20260916/setup-evidence.

Native28+six decoder qualification owns the node next. The sealed paired controller/observer/source/runtime identities and owned dispatch/closure gates have independent CPU reviews; no currentCUDA13.0 GPU pass or performance result exists yet. CurrentCUDA13.2 sources/performance and sanitizer bounds remain unchanged.


## CUDA13.0 instrumentation retry (2026-09-16 09:03 UTC)

Native001 stopped before pytest: the worker environment helper incorrectly required visible imports to leave Torch CUDA uninitialized. All27 failed-attempt raw files are preserved (gzipSHAef11fb7b); cleanup/independent closure05aea1ff reports no owned process/group and all8idle. No selected native test body ran, so this is not a numerical test result. Production source, tests, compiler settings and tolerances are unchanged.

A separate probe-v2 records before/after initialization while keeping hidden-host initialization forbidden and the stable compiler/library identity comparison AST unchanged. Actual visible/hidden traceb2a95577 passes; the observed first initializer is FlashInfer JIT workspace naming through CompilationContext/get_device_capability, superseding a preliminary KDA-import hypothesis. Originalsetup/probe/environment evidence is immutable. Reviewed native-tests-v2/native-002 is authorized after source/proof/idle handoff; the paired controller binds only its completed34/51 qualification and independently collected closure. Still no new CUDA13.0 GPU test or performance pass.


## Original EP4 racecheck reached its unchanged bound (2026-09-16 09:08 UTC)

The historical224b unfiltered EP4 run exhausted its29400s watchdog. Randomt1 completed; random16384 reached first public-forward setup with9 compiled/bound kernels perrank, but did not complete. Frozen postcheck failed. Full156files/257,520,900rawB are locally archived and independently rehashed, gzipSHA00ec939afa3833a4188493e9ab84d354641b5e2e4d5d63ad8d36daf11972468e. Snapshot: hashinfer-w4a16-megamoe/sanitizer-racecheck-scheduler-20260915/collected/20260916T090623Z-4192b7caadf84c44bc5d855ba29300ed. Strict failed/incomplete verdicts remain unchanged.

Immediate race cleanup still listed the four OWNED workers, not unrelated4–7 activity; later postcheck cleanup and independent closurecd7c8620 verify all18 recorded identities/groups absent, source100files/helpers unchanged and all8GPUs idle. Root verified complete manifest/archive and closure bindings. Currentdbd EP8worker4 race continues onBox2. This timeout neither establishes an owned-kernel race nor clears race-sanitizer qualification. Box1 retains apparently uncollected old anomaly tensors; no retirement before preserving useful artifacts.


## CUDA13.0 native tests passed; paired benchmark running (2026-09-16 09:36 UTC)

Current native4d passed34 logical cases/51 rank executions: original28/45 plus six decoder scale-mapping cases. All45 collected raw files and complete archive dc4e35da were independently rehashed; summary818974e1 and closure782bc7a2 verify source/compiler/environment identity and all8 GPUs idle before handoff. Original native001 probe failure remains preserved separately. See cu130-final-refresh-20260916/native-tests-v2/RESULT.json.

The paired full1–8192 Split/Mega sweep launched at09:15:32 UTC on hu-pdx-112 with the same4d source and CUDA13.0 stack, dispatch23cbe043/supervisor13189 start273072920. Full four-tactic Mega AUTO/O3, maxregs96, nonfused Split finalize,3 warmups/100 cold-L2 graph CUPTI samples, unchanged Split launch defaults, weight-quantization PDL disabled. Current runtime helpers/source are sealed; no GPU profiling runs concurrently on this node. First-use shared routing compilation progressed into Split token1 autotuning. There are not yet complete timing rows or publishable new CUDA13.0 results.


## Current CUDA13.0 refresh complete (2026-09-16 09:59 UTC)

Current native4d full paired1–8192 run passed on hu-pdx-112/8B300, image nvcr.io/nvidia/pytorch:25.11-py3, Torch2.10.0a0+b558c986e8.nv25.11, systemCUDA13.0.2/nvcc13.0.88, CuTe4.7.1 cu12 nativecompiler12.9 with fallback decoder. Loaded NCCL2.28.8/NVSHMEM3.4.5/CUPTI2025.3.1; PythonCUPTI13.0.1. EP8 H7168/I2048/E256/topk8, nonfused Split finalize, Mega AUTO4/O3/maxregs96,3warmups/100cold-L2 graph CUPTI samples with median per-sample rankMAX. Both variants share exact canonical weights/inputs/routes on this stack. Untimed weight quantization PDL is off; timed Split PDL/compiler defaults remain unchanged.

All28 rows/2800samples,14 collective selections (112 rank records),224 finite-bitwise-repeat outputs passed. Full raw tensor CPU verification covered234,866,688elements before completion. Collection preserves53files/475,092,299bytes, gzipSHA2ba0b8bf785174e0dda7bd16ad119320ab11533f00cc89f59c584652dcefc9b1. Independent root manifest/archive rehash, source/environment checks, pre/postprocess/GPU closure and independent sample arithmetic passed. No cross-backend bit equality or cross-stack CUDA-only attribution is claimed. Native34logical/51rank test pass is separate.

The original collector falsely rejected saved-versus-fresh report equality because JSON changes integer token keys to strings in mega.rows and mega.hot_autotune_candidates. Its immutable code and failure log remain preserved. A reviewed local-only verifier normalizes exactly those two14-key maps and the expected local log path; all other fields/values remain exact and all frozen checks pass. There was no GPU rerun, production/helper runtime edit, tolerance change or suppressed benchmark failure. Complete records: cu130-final-refresh-20260916/RESULT.json and paired/evidence/collected/20260916T094445Z-6689b8c0772b40e89eff91d6b18e933c.

| Global tokens | Split W4A16, non-fused finalize (ms) | W4A16 MegaMoE (ms) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 0.079264 | 0.096321 | 0.8229× |
| 2 | 0.126305 | 0.122289 | 1.0328× |
| 4 | 0.164065 | 0.133073 | 1.2329× |
| 8 | 0.197777 | 0.165490 | 1.1951× |
| 16 | 0.215938 | 0.188370 | 1.1464× |
| 32 | 0.242402 | 0.223457 | 1.0848× |
| 64 | 0.275730 | 0.257506 | 1.0708× |
| 128 | 0.290050 | 0.256610 | 1.1303× |
| 256 | 0.305844 | 0.255250 | 1.1982× |
| 512 | 0.291043 | 0.266163 | 1.0935× |
| 1024 | 0.299986 | 0.283971 | 1.0564× |
| 2048 | 0.366756 | 0.342787 | 1.0699× |
| 4096 | 0.563412 | 0.524693 | 1.0738× |
| 8192 | 0.980648 | 0.854342 | 1.1478× |

Over 8–8192 tokens: geometric mean speedup **1.1141×**; 11/11 rows faster.

All times are medians of 100 cold-L2 CUPTI samples, taking the maximum rank span per iteration; CUDA graphs enabled. The saved launch command must separately establish non-fused split finalization and environment provenance.


## CUDA13.0 table published; temporary node released

PR5019 readback matches the reviewed draft SHA1e5ab6456424bbf9de85dec1ff16976891d99f234929f5addd529a38b878f887 at 2026-09-16T10:01:38.771098+00:00; head remains4d183b83/ready. Both CUDA13.2 tables are preserved, and newCUDA13.0 table includes all14 rows/1.114128x geometric speedup over8–8192/all11retained rows faster. Native34/51 results, precise fallback stack and sanitizer limitations are included. No source commit or review comment was added.

Final independent retirement closure passed with original boot/source/runtime identities and all8GPUs idle. Managed h deleted only c2/infra flashinfer-cu130-0916 after complete local evidence preservation. Currentdbd EP8 race continues unchanged on its separate CUDA13.2 node; historical anomaly tensor preservation still owns Box1.
