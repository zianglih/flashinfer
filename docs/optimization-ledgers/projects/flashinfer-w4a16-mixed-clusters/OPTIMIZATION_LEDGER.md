# Optimization ledger

## Baseline and protocol

Current-main baseline: `316faec37a4706a2ecc7d46265087f8190b40baa`.
Historical #6277 methodology is recorded in `BENCHMARK_PROTOCOL.md`; historical
latencies are reference material, not the new comparison baseline.

## Candidate 1: preferred 4 + fallback 2

Status: implementation in progress; GPU performance and numerical qualification
pending. No candidate has been promoted.

- New four-CTA geometry uses M256 two-CTA MMA pairs.
- Uniform two-CTA fast path and existing M128 variants remain available.
- Reuse generic FlashInfer mixed-CGA TMA/UMMA and fixed-group atomic work-ID
  helpers through the SM100 snapshot public API.
- Probe hardware cluster occupancy and use the existing Rubin whole-logical-tile
  launch-count calculation.
- Current controls: unchanged main AUTO16/all versus candidate AUTO12/mixed-only
  on T32/T4096 through one project wrapper; all performance uses native AUTO.
  The earlier exploratory AUTO28 policy and original fixed uniform2,
  uniform4 and mixed4+2 screening proposal was superseded by user direction on
  2026-10-24 before any fixed-tactic performance run.
- Keep compilation, cache preparation, input generation and tuning outside final
  timed samples. Record raw samples, selected tactics and source manifests.

## Resource setup

- Managed CLI path verified `/usr/local/bin/h`.
- Initial request outside an HAI checkout failed before creating resources.
- New independent HAI clone recovered a nonessential LFS checkout error with
  `GIT_LFS_SKIP_SMUDGE=1`; no shared source was modified.
- C2/ziangli had no free quota; only this task's queued request was deleted.
- C2/infra devbox ready: eight B300 GPUs, NGC 26.05 CUDA 13.2 image.

## Checks completed

- Historical capture parser replay reconstructed all 13 #6277 GLM5 medians
  from 1,300 raw samples.
- Host changes: scoped Ruff formatting/check and `git diff --check` passed.
- These are static/harness checks, not GPU validation.

## First GPU audit: unit-v1

- C2 B300, NGC 26.05, CuTe DSL 4.7.1, driver 595.91.07; container Torch retained.
- Source: baseline plus candidate SHA256 manifest in `evidence/sync-receipts/`.
- `25 passed, 51 warnings in 10.94s`: 13 host geometry/transition contracts
  and 12 GPU scheduler cases (static/atomic, preferred/fallback/mixed,
  group hints 1/5). Each GPU case replayed ragged, all-empty, and reversed counts.
- Production-sized mixed launch observed 33 physical four-CTA clusters and
  8 physical two-CTA clusters, totaling 148 CTAs. Forced fallback launches also
  passed exact FC1/FC2 tile ownership, row-prefix, and token-prefix assertions.
- Raw log: `evidence/remote/unit-v1/run.log`. This is scheduler validation, not full
  GEMM/transport numerical qualification or a performance result.
- Review fixes: normalize zero fallback capacity to uniform4 construction;
  explicitly clear fallback geometry in uniform AUTO candidates.

## User-directed iteration policy, 2026-10-24

- Prioritize short optimization feedback: GLM5 EP8 global tokens32,4096,
  100 untrimmed rank-MAX CUPTI samples per point, cold L2 and shared driver.
- Every performance arm uses AUTO; initial candidate expands the existing16
  candidates with12 valid M256 mixed candidates (AUTO28).
- Run a minimum one-case mixed compile/liveness smoke first. Defer rigorous
  numerical/sanitizer qualification until solid gains are retained; no new
  forced-fallback diagnostic or fixed-tactic performance screen at this stage.
- Run the full13-point AUTO comparison after retaining a candidate. Do not
  infer full-grid or statistically established gains from the short screen.

## Interrupted exploratory baseline: glm5-baseline-main-auto16-a1

- Pristine main `316faec37a4706a2ecc7d46265087f8190b40baa`, shared candidate
  driver SHA256 `90502a5eb9f8f402b3f8959b7065d319bc106d14de623c860a23610d3ac119d9`.
- Deliberately stopped via SIGINT after the user redirected the workflow.
  This is **PARTIAL EXPLORATORY ONLY**, not a complete13-point result.
  Original `run.json` remains `complete:false`, `exit_codes:[1]`.
- Completed600 samples across six points: T1=69.489us, T2=89.889us,
  T4=90.0325us, T8=111.313us, T16=128.257us, T32=139.5375us.
  All raw samples, including large first-sample transients, remain untrimmed.
- `partial.json` verifies unchanged baseline source and shared driver;
  `partial-raw-records.json` retains per-rank AUTO tactic receipts and samples.
  A requested full-grid comparison must not count this as complete.
- Stop receipts preserve process IDs, UTC time, exit code, empty GPU process
  list, eight idle GPUs and successful `.gpu.lock` reacquisition.
- `remote/baseline_short.sh` is prepared for a fresh T32/T4096 AUTO16 capture,
  reusing the baseline cache; launch only after the coordinating agent's smoke.

## Complete short baseline: glm5-baseline-main-auto16-short-a1

- Finished 2026-10-24 21:06:34 UTC; native source unchanged, shared driver
  unchanged, `complete:true`, `exit_codes:[0]`. Capture duration 4m41s includes
  untimed setup, weight preparation, compilation and AUTO selection.
- T32 median **146.9295us**: uniform2, M256/N32/K256, group512,
  `epi_warps`, two-CTA MMA, atomic scheduler.
- T4096 median **399.8430us**: uniform2, M256/N128/K256, group1024,
  `reuse_dispatch_warps`, two-CTA MMA, atomic scheduler.
- Each point contains100 untrimmed cold-L2 rank-MAX CUPTI samples and eight
  matching per-rank AUTO receipts. Raw logs and source/runtime manifests are in
  `evidence/remote/glm5-baseline-main-auto16-short-a1/`.
- An apparently quiet startup was ordinary compilation: a live quantization
  nvcc/ninja process followed by active CuTe compilation on all eight ranks.
  Nonblocking stack receipts are retained in the queue evidence. No prepared-init
  wrapper or measured-driver modification was needed.
- The partial full sweep's T32 selected group1024 and measured139.5375us.
  This source-identical selection variation limits conclusions from a single
  short screen; it is not pooled with the completed two-point capture.
- After capture, the project harness CLI was restricted to AUTO and comparison
  now rejects fixed-knob metadata. CPU checks verified both restrictions and
  reconstructed these medians. The native measured driver remained unchanged;
  the baseline retains its frozen original recipe.

## Preparation-cache control for the final comparison

- The first short AUTO pair retained the existing persistent knob-cache policy;
  baseline allocation began from compatible uniform entries and AUTO evaluated
  its full catalog. Do not alter this control mid-pair or silently apply it to
  candidate1-to-candidate2 iterations.
- Source audit found AUTO workspace preparation returns `None`, after which
  the W4A16 frontend can load persistent knobs before AUTO tuning. A newly cached
  mixed winner can be incompatible with pristine baseline allocation.
- For a fresh final matched pair, pass `FLASHINFER_MOE_EP_KNOB_CACHE=0` to both
  launcher environments and record it. Compiled-code caches remain enabled;
  native AUTO still runs and records its selected tactics. The harness already
  inherits this variable and includes it in provenance. New cache-disabled
  captures must not be pooled with the earlier policy.

## Candidate1 AUTO28 short result

- `glm5-candidate1-auto28-short-a1` completed both points with200 raw samples,
  exit0, unchanged source/driver and matching per-rank tactic receipts.
- CUPTI medians: T32=141.5850us (baseline146.9295us, 1.03775x),
  T4096=400.9310us (baseline399.8430us, 0.99729x).
- **Both AUTO winners remain original uniform2 tactics.** The T32 group hint
  differs between the short arms; the same-source partial baseline variation
  already covers this apparent gain. No mixed-cluster performance win is
  established, and candidate1 is not promoted on these results.
- Internal AUTO graph-event scores, separately from the CUPTI medians:
  T32 winner128.3us versus best mixed132.0us (M256/N32, epi_warps, group1024;
  group512 ties at printed precision), mixed2.884% slower. T4096 winner389.0us
  versus best mixed394.1us (M256/N128, reuse_dispatch_warps, group1024),
  mixed1.311% slower. All28 rankings are preserved in
  `evidence/candidate1-auto-rankings.json`; these are AUTO diagnostics, not
  standalone fixed-tactic performance runs.
- Audited short-pair comparison: `evidence/short-auto16-vs-candidate1-auto28.json`.
  Raw capture and queue receipts are under `evidence/remote/`.
- Candidate2 changes only the mixed kernel's repeated per-tile geometry work;
  measured kernel SHA256
  `87839cd3b1c4d68bbaf83c44a3f9838f0d1c3875764187cbe3f2b45f99388fb4`.
  Its AUTO28 T32/T4096 screen was launched after idle-GPU and driver/hash checks;
  no separate correctness matrix precedes this iteration.

## Superseding policy: baseline AUTO16/all versus optimized AUTO12/mixed-only

- User requires optimized AUTO to tune only the new mixed4+2 tactics. Product
  catalog remains28; a shared project-only `policy_driver.py` wrapper preserves
  baseline all16 and filters candidate to12 mixed tactics without changing native
  AUTO compilation, warmup, graph-event timing, ranking or winner selection.
- Wrapper SHA256
  `debc1f10711482235ecf152ffc5747a5fc4b1de2bf2275c9f9788bfeb7f048ef`.
  Both arms use unchanged native driver90502a5e… and knob-cache0. Source,
  wrapper, catalog policy/counts and per-rank winners are captured independently.
  The harness rejects any uniform winner under mixed-only policy.
- Candidate2's superseded AUTO28 sweep was stopped by scoped SIGINT after
  T32=143.201us/100samples; T4096 incomplete, exit1, `complete:false`.
  Its frozen source/patch remain. The authorized backend sync at21:21:35UTC
  occurred after the stop/idle receipt and before partial preservation at
  21:21:49UTC, so the post-stop source check is false; this is not evidence of
  an in-capture edit. Exclude this partial from the new policy comparison.
- `remote/policy_pair.sh` runs fresh baseline
  `glm5-baseline-main-auto16-all-short-a1`, then candidate
  `glm5-candidate2-auto12-mixed-only-short-a1` after clean exit and idle GPUs,
  holding `.gpu.lock` across both. No new correctness matrix is scheduled.

## Completed common-wrapper pair and candidate3r handoff

- Fresh baseline `glm5-baseline-main-auto16-all-short-a1` completed at
  21:29:58UTC; candidate2 `glm5-candidate2-auto12-mixed-only-short-a1`
  completed at21:35:18UTC. Both are `complete:true`, exit0, unchanged source,
  identical driver/wrapper/cache0, two token points with100 untrimmed samples
  each, and matching eight-rank tactic receipts. Baseline preserved16/16
  candidates; optimized selected12/28, all preferred4/fallback2.
- Cold-L2 rankMAX CUPTI medians (baseline / candidate2): T32
  **144.193 /154.482us**, speedup0.933397x; T4096
  **401.843 /408.675us**, speedup0.983283x. This mixed implementation is
  slower at both short-screen points and is not a retained gain.
- Both selected M256/K256. T32 selected N32/group1024/epi_warps in both arms;
  T4096 selected N128/reuse_dispatch_warps with baseline group1024 and mixed
  group512. Internal hot graph-event AUTO scores were128.3/390.3us baseline
  and130.2/394.9us mixed. Full rankings are diagnostic only, saved separately
  from reported cold-L2 performance.
- Comparison passed `harness/compare.py` and is saved as
  `evidence/short-auto16-all-vs-candidate2-auto12-mixed-only.json`.
  Rankings: `evidence/baseline-auto16-all-auto-rankings.json` and
  `evidence/candidate2-auto12-mixed-only-auto-rankings.json`. Raw captures and
  all three queues are under `evidence/remote/`. At21:35:33UTC no GPU
  processes remained, all eight GPUs were0%/0MiB, and `.gpu.lock` was available.
- `remote/candidate_mixed_only.sh` is the current serial candidate launcher:
  explicit mixed-only/cache0, frozen driver/wrapper hashes, idle-GPU checks,
  full-run lock and per-arm script/exit/UTC receipts. The older
  `remote/candidate.sh` is superseded and must not launch new iterations.
- Candidate3r combines try-acquire lookahead, overlap of fallback registration
  with metadata, and mixed group256 tactics. Its label is
  `glm5-candidate3r-auto18-mixed-only-short-a1`, launched21:36:43UTC/PID29528.
  Preflight verified kernel664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939
  and catalogfeea41a6bd666ff0b92c77cdd507645354d82589f577e32ba6677a8fe5ed168e.
  Product default catalog34 is filtered to18 mixed candidates. This combined
  screen cannot attribute performance to an individual constituent change.

## Candidate3r short result and T16384 endpoint

- `glm5-candidate3r-auto18-mixed-only-short-a1` completed both points,
  exit0/source unchanged; all eight ranks agree on preferred4/fallback2 winners.
  Cold-L2 CUPTI medians: T32=144.817us, T4096=405.6205us. Relative to fresh
  baseline144.193/401.843us, speedups are0.995691x/0.990687x. Relative to
  candidate2 mixed-only154.482/408.675us, speedups are1.066739x/1.007530x.
  The combined revision recovers the earlier T32 regression but establishes
  no gain over current-main in this short screen.
- N32/epi_warps/group512 wins T32; N128/reuse_dispatch_warps/group1024 wins
  T4096. Internal AUTO scores130.1/391.1us are selection diagnostics only.
  All three N32/epi group sizes tie at printed130.1us for T32. For T4096,
  N128/reuse groups1024/512/256 score391.1/395.1/400.3us, respectively.
- Audited results: `evidence/short-auto16-all-vs-candidate3r-auto18-mixed-only.json`,
  `evidence/short-candidate2-auto12-vs-candidate3r-auto18-mixed-only.json`, and
  `evidence/candidate3r-auto18-mixed-only-auto-rankings.json`. Raw capture and
  queue receipts are under `evidence/remote/`.
- After successful exit, empty GPU process list, eight idle GPUs and lock
  availability, the matched T16384 endpoint pair started21:41:11UTC/PID31444
  using `remote/endpoint_pair.sh`. It holds `.gpu.lock` across fresh baseline
  `glm5-baseline-main-auto16-all-t16384-a1` then candidate
  `glm5-candidate3r-auto18-mixed-only-t16384-a1`. The script verifies candidate3r
  kernel/catalog hashes plus the shared driver/wrapper and uses cache0 in both.
  This endpoint is an additional throughput screen, not the full final grid.

- Endpoint pair completed cleanly: baseline1228.877us versus candidate3r
  1244.425us (0.987506x, candidate1.27% slower),100 samples each. Both source
  manifests and shared driver/wrapper remain unchanged. Baseline winner is
  uniform2 N128/group512/reuse; candidate winner is mixed4+2
  N128/group256/reuse. Internal hot-AUTO scores1130.2/1141.3us are diagnostic.
  Audit: `evidence/t16384-auto16-all-vs-candidate3r-auto18-mixed-only.json`;
  full rankings are saved beside the short rankings. At21:51:01UTC all eight
  GPUs were0%/0MiB, no workers remained, and the GPU lock was available.
- None of the three candidate3r screened points establishes a gain over
  current-main. The compact untrimmed short-run quartiles and half-run medians
  are in `evidence/SHORT_COMPARISON_NOTE.md` and
  `evidence/short-current-policy-drift.json`; they do not establish repeatability.
- A diagnostic PC-sampling pair is prepared locally in `remote/profile_pair.py`
  using `harness/profile_ncu_policy.py` and `harness/audit_ncu_reports.py`.
  It is not a latency benchmark: baseline AUTO16/all then mixed AUTO18 atT4096,
  one requested sampling pass, actual replay count verified in each report,
  eight-rank AUTO receipts, source/resource provenance,1200s per-arm timeout
  and scoped TERM/KILL cleanup. No profile has been launched at this point.

## PC diagnostic attempt and support-JIT retry

- PC pair a1 started21:52:10UTC/PID36673. ncu_report import and eight-peer
  TCP communicator initialization succeeded. Before any report, baseline rank4
  host C++ compilation of `fp4_quantization_103/thop_fp4Quantize.o` aborted134
  with `malloc(): mismatching next->prev_size (unsorted)`. Peer NCCL failures
  followed. This is a support-build failure, not a mixed-kernel result; the
  logs do not establish which component caused the host allocator corruption.
- Only failed child process group36872 received SIGTERM at21:57:04UTC.
  Pair exited1, baseline remained incomplete, candidate never started, and no
  GPU/NCU workers remained. Failure logs/queues are preserved locally under
  `evidence/remote/profiles/` and `evidence/remote/queues/` with a1 labels.
- The exact shared-cache build files were captured: quant103 now references
  baseline paths17 times, while fused-routing still references candidate paths
  19 times. Switching source roots changes absolute include/source commands
  under the same JIT output path and triggers rebuilds. The failed command,
  build.ninja copies and hashes are retained in the failed baseline queue.
- Authorized a2 retry started22:00:18UTC/PID39518. New
  `harness/prewarm_profile_support.py` calls exact SM103 quantization and
  default fused-routing `JitSpec.build_and_load()` outside NCU immediately
  before each source's profile; no kernel benchmark is run for this preparation.
  Compiler logs, build.ninja/.ninja_log and object/shared-library hashes are
  retained. Shared1200s arm budget covers prewarm plus profile; any prewarm
  failure stops the pair. No product source, native timer, AUTO policy,
  PC metric preset or NCU target-processes flag changed. Existing CUPTI
  measurements remain separate from this diagnostic setup.

## Candidate3r: combined established ordering changes and mixed group256

- Candidate2 mixed-only short pair completed with source/driver/wrapper stable:
  T32 154.482us versus baseline144.193us; T4096 408.675us versus401.843us.
  These are regressions of7.14% and1.70%; no mixed speedup is established.
  Complete audit: `evidence/short-auto16-all-vs-candidate2-auto12-mixed-only.json`.
- To prioritize iteration speed, candidate3r combines the independently reviewed
  B-TMA producer lookahead and fallback-registration-before-metadata-wait patches,
  then appends six mixed group256 choices following GenPhase group scaling.
  Individual experiment patches remain available for rollback. This screen tests
  their combined effect; it cannot attribute improvement to an individual change.
- Product catalog34 (51 with IKR opt-in); optimized benchmark filters to18 mixed
  choices. Baseline remains original AUTO16. All performance uses native AUTO,
  common wrapper/driver and knob-cache0. No fixed-tactic performance is measured.
- Applied after candidate2 clean exit/idle handoff21:35:33UTC; synced21:36:09UTC.
  Kernel SHA256 `664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939`;
  catalog SHA256 `feea41a6bd666ff0b92c77cdd507645354d82589f577e32ba6677a8fe5ed168e`.
  AST/py_compile, Ruff lint/format and diff checks passed locally.
- Run: `glm5-candidate3r-auto18-mixed-only-short-a1`, T32/T4096,100 untrimmed
  cold-L2 CUPTI samples/point. Native AUTO preparation is the compile/liveness
  gate; broader numerical and sanitizer qualification remains deferred.

## PC a2 completion and unchanged-source middle range

- PC a2 completed with both arms exit0 and unchanged source manifests. Baseline
  finished22:05:15.894UTC; candidate3r finished22:13:01.487UTC. Both support-JIT
  prewarms passed outside NCU. Each arm has eight reports, one matching action
  per rank, actual `profiler__replayer_passes=1`, and no report-integrity errors.
  Baseline AUTO16 selected uniform2 N128/group1024/reuse; mixed AUTO18 selected
  preferred4/fallback2 N128/group512/reuse. These are instrumented diagnostic
  captures and provide no latency comparison.
- At22:14:48UTC all eight GPUs had0MiB/0% utilization, no compute processes
  remained, and both locks were available. The pair queue preserves
  `idle-handoff.json`. Architecture owns CPU-only all-rank source/SASS analysis
  and full profile-tree retrieval; queue evidence is retrieved separately.
- Source remains candidate3r. Root authorized a fresh matched middle-range pair
  T128/T512 after the PC capture succeeded. `remote/middle_pair.sh` started
  22:15:11.769UTC/PID45376 under pair
  `glm5-auto16-all-vs-candidate3r-auto18-mixed-only-middle-a1`, baseline AUTO16/all
  followed by mixed AUTO18. Shared driver/wrapper, cache0,100 untrimmed cold-L2
  CUPTI samples and source guards are unchanged. Launcher SHA256
  `e7d1b38456b8b9beb642e8ce2930b63890c06da859c6d0a706a209efffbbe4f8`.
  No raw-weight lookahead or static-scheduler experiment is applied.

- Middle pair completed: T128 baseline168.370us/candidate165.7295us
  (1.015933x); T512 baseline175.954us/candidate177.010us (0.994034x).
  Both arms pass source/driver/wrapper/runtime/raw-sample audits,100 samples per
  point. Baseline N32/group1024/epi wins both; mixed N32/epi uses group512 at128
  and group256 at512. Hot AUTO scores150.7/157.8us versus151.5/160.6us are
  diagnostic only. T128's small cold-sample gain is provisional in one ordered
  screen; the middle grid cannot establish full-grid or repeatable improvement.
  Audited JSON: `evidence/middle-auto16-all-vs-candidate3r-auto18-mixed-only.json`;
  full ranking files and `middle-current-policy-drift.json` are adjacent.
  At22:26:36UTC both arms were complete and source-stable, all8 GPUs idle0MiB,
  no compute apps and both locks available. Fresh final-grid measurements will
  not pool these exploratory samples.

- Post-middle host contracts ran under `.gpu.lock` with the frozen legacy capture
  helper/environment and a180s bound: `python3 -m pytest -q
  tests/moe_ep/test_w4a16_mixed_cluster_config.py
  tests/moe_ep/test_mega_workspace_knobs.py`. Result134 passed,3 warnings in10.73s,
  exit0 at22:27:52UTC, source/test hashes unchanged, no GPU apps. Raw log,
  command/environment, source-before/after and timeout receipts are preserved in
  `evidence/remote/tests/host-contracts-candidate3r-after-middle-a1/`.
- `remote/full_pair.sh` is prepared locally for a fresh independent13-point pair
  using the new per-source FlashInfer workspace policy in both arms. It requires
  the exact frozen candidate commit and clean candidate checkout, plus unchanged
  candidate3r kernel/catalog and shared driver/wrapper. No full-grid launch or
  new cache-helper sync has occurred; root owns pre-commit/commit and next handoff.

## Committed candidate freeze and fresh full grid

- Root committed candidate3r as `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`,
  parent `316faec37a4706a2ecc7d46265087f8190b40baa`. At22:30:15UTC remote
  `prepare_full.py` verified all14 hashes against `candidate3r-commit-freeze.json`,
  fetched that exact public-fork commit and used `git reset --mixed` to change
  HEAD/index while preserving every working-file byte. The candidate is fully
  clean; the baseline remains pinned316faec. Both GPU locks protected preparation.
- Exact helper transition and prior copies are preserved in
  `evidence/remote/setup/full13-freeze-a1/`: run.py SHA256
  `04139d1a2a776485c7bac62534723afb6f0b1ad9547efc2fdd9b161f978e5398`,
  compare.py `e9bb07254085e00ef383eb70f717f73fff603bd0ed56171d8156aee165f1d81a`,
  full_pair.sh `c529e9693f362f8afdbd23ae928e4fae269ee426ec13e1d0413960c68082d498`.
  Driver90502a5e and wrapperdebc1f10 remain unchanged.
- Full13 pair started22:30:41.838UTC/PID52338 under
  `glm5-auto16-all-vs-candidate3r-auto18-mixed-only-full13-a1`. Baseline AUTO16/all
  runs first, followed by committed candidate AUTO18/mixed-only. Both explicitly
  select `separate-flashinfer-workspace-v1`: source-specific FlashInfer workspaces
  with the other compiled caches shared. Persistent knob cache remains disabled;
  native timer/warmups/fixtures and100 untrimmed cold-L2 CUPTI samples are unchanged.
  These fresh full-grid samples are independent of the exploratory partial grids.
  No further source edits are permitted while the pair runs.

## Selected bounded static-mode follow-up; not yet applied

- Root selected one final GLM5 EP8 **T64/T128/T4096** hypothesis test after the
  full13 capture and explicit idle/lock handoff: fresh baseline AUTO16/all versus
  mixed-only AUTO36, preserving18 atomic choices and appending18 copies using
  the existing static mode. Product catalog52; IKR remains disabled. No kernel,
  arithmetic, tile, group or return-mode changes are part of this patch.
- Preserve the earlier PC-based condition in
  [AUTO52 preparation](experiments/AUTO52_MIXED_STATIC.md) as history: that
  condition was **not met**. This later selection is a bounded reuse-based test
  because source confirms removal of fallback registration, work-ID atomics and
  handoff broadcasts. Profiles did not establish those costs as a bottleneck.
  The earlier isolated T128 gain did not repeat in the ongoing full13 capture;
  the isolated T64 gain is provisional. Neither justifies default adoption.
- Patch SHA256
  `51b5bd28ae22154753f8c0f1fca0931d326ccf6f300770ac539c872ab78c42c9`.
  Its two-file scope, base/proposed hashes, exact host validation commands,
  qualification boundaries and release-note wording are recorded in that note.
  Local read-only verification still finds a clean candidate3r checkout and
  matching frozen kernel/catalog/test hashes; `git apply --check` passes.
  The prepared AST-isolated catalog checks are not package-level pytest.
- The candidate3r full13 evidence stays immutable at commit3d047d3f. Freeze a
  distinct static-candidate source manifest/diff before measurement and do not
  pool its samples with full13 or earlier screens. Both new arms keep the same
  native AUTO driver/wrapper, inputs,100 untrimmed cold-L2 CUPTI samples,
  three explicit warmups, knob-cache0 and per-source-workspace-v1 cache policy.
  Record every rank's selected scheduler mode; an atomic AUTO36 winner does not
  support the static hypothesis. Doubling the catalog adds untimed preparation.
- Read-only source review found no new static-specific correctness defect:
  global preferred-grid coordinates preserve fallback channel halves, while
  the common FC1/FC2 decoder, readiness waits and padded-channel epilogue gates
  remain intact. Historical static scheduler tests include actual33x4+8x2
  placement, but do not qualify current full-kernel numerics or graph replay.
  Rigorous qualification remains deferred until retained gains. No live source
  edit, remote sync or GPU launch was performed for this decision record.

## Static experiment released after full13 idle handoff

- Rubin reported the full13 pair complete with both source audits/exit0 and
  pair exit0. At23:14:47UTC all8 GPUs were idle0MiB, no compute applications
  remained, both locks were available, and candidate3r was clean.
- Root then applied the exact static catalog/test patch, passed scoped
  pre-commit on both changed files and `git diff --check`, and committed
  `f14e4bae9379703fd5693d8ee993faae23e130d5`, direct parent3d047d3f, on
  `experiment/w4a16-mixed-static-auto36`. Freeze:
  [candidate4s-commit-freeze.json](evidence/candidate4s-commit-freeze.json).
  Independent local read-only verification confirmed clean status, parent,
  proposed catalog/test hashes and unchanged kernel hash664a74fd.
- Root authorized Rubin to sync/freeze and launch the bounded three-point pair.
  This entry records source release and authorization only, not completed
  package-level host tests, compilation or GPU results. Keep those receipts
  separate from candidate3r full13 and the prior134-pass host run. No further
  source changes are authorized during the new capture.

## Fresh full13 completion and upstream draft

- Both source-stable arms completed with 13 points and 100 untrimmed samples/point,
  baseline 316faec and candidate 3d047d3. Native comparison and independent raw/hash
  audits passed. Geometric-mean baseline/candidate: 0.9922122427 overall T4+,
  0.9912695321 decode and0.9947305229 prefill. T64's 1.025214x is the largest local
  gain; the earlier T128 improvement did not repeat. No broad retained benefit.
- `publication/final13-a1/` preserves all 2,600 samples and all rank winners; its
  SHA256SUMS hash is a5872cd9fdbccc2b2c0950aa26e05bb03fb5a1d47c60a77ce66562cfc0725c91.
  Published byte-identical as orphan evidence commit
  eb34175a2cc31befcc1e927db85c3628c5ae9e7f on
  `zianglih/flashinfer:w4a16-mixed-clusters-evidence-20261024`.
- Created upstream draft https://github.com/flashinfer-ai/flashinfer/pull/7202,
  head 3d047d3 / base main; read back exact body/head/draft status and attached to
  this task. Body reports 0.8% slower overall, no retained adoption claim, and
  deferred numerical/sanitizer qualification. Receipt: `evidence/pr7202-created.json`.
- Static AUTO36 trial remains separate; its source is not in the PR or primary
  evidence. No source/index/worktree bytes changed during evidence publication.

## Static AUTO36 source freeze and serial capture start

- The first remote bundle preparation stopped before checkout because the bundle
  advertises `HEAD`, not a branch ref. Its failed setup log is retained under
  `setup/candidate4s-freeze-a1`; no source bytes or GPU workload changed.
- Retry `setup/candidate4s-freeze-a2` verified the bundle SHA, exact advertised
  `f14e4bae... HEAD`, FETCH_HEAD, direct parent, two-file scope and all14 manifest
  hashes, then checked out the unpublished experiment detached and fully clean.
  The completed receipt and exact helper copies are local under
  `evidence/remote/setup/candidate4s-freeze-a2/`.
- The serial pair launched23:20:39.871UTC/PID68964 as
  `glm5-auto16-all-vs-candidate4s-auto36-mixed-only-static-screen-a1`; baseline
  native AUTO16/all began23:21:01.719UTC, followed automatically by candidate
  native mixed-only AUTO36 at T64/T128/T4096. Both retain per-source workspace
  policy, knob-cache0, driver90502a5e and wrapperdebc1f10,100 untrimmed cold-L2
  CUPTI samples and3 warmups. Both locks span the pair; each arm has a1800s
  wall timeout with20s TERM-to-KILL grace. Native rankings and explicit scheduler
  mode receipts must confirm16 atomic controls versus18 atomic+18 static choices.
  This is a new exploratory capture, separate from the committed full13 results.

## Static AUTO36 screen completed and rejected

- Both three-point arms completed with exit0, unchanged capture source and100
  untrimmed samples/point. Native ranking/mode audits confirmed16 atomic control
  tactics and18 atomic+18 static mixed tactics at every point. All8 ranks agreed
  on the selected **atomic** tactic at all3 points; static won no AUTO sweep.
- Matched baseline/candidate medians in microseconds: T64 159.601/162.7055
  (0.9809195x), T128 171.0255/171.2335 (0.9987853x), T4096 403.3325/400.4995
  (1.0070737x). Three-point geometric mean0.9955328x; this separate one-pair
  screen neither establishes a static benefit nor a retained general gain.
  Exact native comparison: `evidence/static-screen-auto16-all-vs-candidate4s-auto36-mixed-only.json`.
- At23:34:22.926UTC the final source audit matched clean f14 and all14 hashes,
  pair exit0, all8 GPUs idle0MiB and both locks available. Full raw runs, native
  rankings and scheduler-mode receipts are local under `evidence/remote/` and
  `evidence/remote/queues/`, using the static-screen-a1 labels.
- Root rejected the catalog expansion and explicitly authorized restoration.
  Under both locks, restored the remote checkout to exact public3d047d3 at
  23:34:57.943UTC, verified empty full porcelain status and the original14 hashes,
  and reconfirmed idle GPUs. Receipt: `evidence/candidate4s-remote-restoration.json`.
  Preserve f14 source manifests, bundle, failed/successful setup receipts and raw
  captures; no further GPU benchmarks or T64 confirmation were launched.

## Final publication and workspace state

- Published the independently audited rejected-trial extension as
  `623d698f45c2518243fdc11a849d2ed25e528b94` on
  `zianglih/flashinfer:w4a16-mixed-clusters-static-evidence-20261024`.
  All 600 new samples, full diagnostic AUTO rankings, hardware controls and
  local/remote restoration receipts are preserved. Original full13 data and
  aggregates remain byte-identical. Extension SHA256SUMS hash:
  `fa13b7e8a52dfdaa77de168b36055322a9660c7e3bb1d23e122dbb2f53954d0c`.
- PR7202 body now includes the separate rejected static experiment and runnable
  patch-based reproduction. Readback verified exact body, draft/open status and
  head `3d047d3f`; receipt `evidence/pr7202-final-readback.json`. Public body SHA256:
  `0022e6523377067c9d843706b63b72d0a5830714541ca3310a838289ba2f6a12`.
- Local source branch is `feat/w4a16-mixed-clusters`, clean at public3d047d3;
  local restoration receipt `evidence/restoration-local-after-static.json`.
  Both evidence pushes preserved source HEAD/index/worktree. The f14 experiment
  branch remains local for reference. All helper scripts/ledgers/raw data remain.
- Upstream pre-commit and Build Docs passed. GPU CI was skipped pending maintainer
  authorization; its summary failure is that gate, not a numerical/kernel failure.
  Full source-revision numerical and sanitizer validation remains deferred because
  no solid gain was retained. The C2 devbox is idle and available for follow-up.
