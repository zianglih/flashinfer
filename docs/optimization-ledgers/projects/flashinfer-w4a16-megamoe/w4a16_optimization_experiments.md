# W4A16 MegaMoE experiment ledger

This effort extends FlashInfer #4048 to fused expert-parallel MegaMoE.
Draft upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/5019

## Controls and measurements

- Initial upstream `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.
- Initial implementation `34e3996`; host contract tests `74bda7f`.
- C2 devbox `fi-w4a16-mega-0907`, namespace ziangli, eight B300 SXM6 AC.
- Explicit image `nvcr.io/nvidia/pytorch:26.05-py3`; driver590.48.01;
  nvcc13.2.78; PyTorch2.12.0a0+5aff3928d8.nv26.05; DSL4.7.1;
  loaded NVSHMEM 3.6.5 (wheel metadata 3.7.2) / nvshmem4py 0.3.1; CUPTI13.2.0 / runtime13.2.86;
  nsys2026.2.1; ncu2026.1.1. The image was the newest CUDA13.2 NGC
  PyTorch release when provisioned. Pip initially selected newer prerelease
  dependencies; DSL/CUPTI were pinned before numerical/performance runs.
- Primary benchmark `benchmarks/bench_cute_dsl_moe_distributed.py`:
  DeepSeek-V3 H7168, I2048, E256, topk8, EP8, global tokens1..4096 powers2.
  Empty ranks at tiny batch sizes are part of the workload.
- Split W4A16 control and MegaMoE share exact packed bytes/scales, routes,
  activations, and FP32 post-FC2 routing. Split native FC1 is up/gate while
  Mega canonical pack is gate/up; packing swaps halves without requantizing.
- CUPTI measures the activity span per iteration, then MAX across ranks and
  median over iterations. Do not confuse this with summed kernel duration.
- Preserve raw results, source SHA plus candidate patch hash, profiling
  commands/reports and rejected candidates. Never loosen numerical tolerance.

## 000: Initial functional kernel (correctness passed)

Mirror BF16 non-swap MegaMoE scheduling/transport and replace TMA weight-B
loads with four online decode warps. Use BF16 UMMA with FP32 post-MMA global
alpha and separate post-FC2 FP32 top-k reduction. Initial tile256×256×64,
cluster2×1; source additions live in shim/w4a16, vendor src unchanged.

- Static initial check: Ruff and syntax compilation passed.
- Initial host tests: `logs/host-contract-001.log`, **37 passed**, including existing
  weight-pack tests. SourceNone+pretransformed, packed interleave, scale
  placement, and input validation covered.
- Full precommit initial snapshot: `logs/precommit-initial.log`; one new
  SchedStorage type annotation and one pinned-Ruff formatting fix required.
- Follow-up full precommit passed: `logs/precommit-followup.log` and
  `logs/precommit-api-guards.log`.
- Functional kernel `b5d2672`: EP1 **3 passed**, EP2 **3 passed per rank**.
  Complete raw logs: `logs/single_rank_006_final.log`,
  `logs/two_rank_002_all.log`. Includes exact scale/routing fixture, graph
  replay and changes to activations/routes, single/empty/refill rounds.
- Host public-helper guards and pool-key regression: **48 passed** in a
  separate CPU-only source snapshot, `logs/host-global-guards-pool-20260907.log`.
- Broader host regression: 77 passed, 7 skipped, and one existing test expected
  a visible CUDA device; CPU-only invocation instead raised no-GPU. Its unchanged
  test passed with CUDA visible, `logs/host-regression-visible-cuda.log`.
- Numerical compiler fixes: signedness at raw packed loads, R2S alignment,
  compact dynamic-token reducer metadata, skip zero-block reducer while
  retaining collective participation, and local-W4A16 SwiGLU association.
- EP8 baseline bring-up has passed exact prepared weight/layout parity,
  `logs/benchmark-weight-layout.log`, and is compiling first-use routing/EP
  dependencies. No timing result yet.
- Runtime actually loads base-image NVSHMEM3.6.5 although installed package
  metadata says3.7.2; report loaded runtime separately from wheel versions.

## 001: EP8 numerical diagnosis and host contracts

- First ten-iteration bringup at global 1: split 0.082945 ms, Mega 0.471267 ms.
  This was provisional; the 100-iteration baseline and synchronized control
  are recorded below. The global-8 strict final-output crosscheck failed
  3/57344 elements (max absolute error 0.03125, relative L2 0.0026392453).
  No tolerance was changed.
- `logs/diagnostic-global8/comparisons.json` and `outputs.pt`: all 458752
  captured per-route FC2 values are bitwise identical between split and Mega.
  Applying split's BF16 rank-local partial reduction to Mega's captured FC2
  values reproduces split's final output exactly. The different collective
  reduction boundary explains the crosscheck failure.
- Independent E2M1/E4M3 decode and TF32-disabled FP32 torch GEMM oracle:
  Mega's all-route reduction passes every element at 1e-2; both per-route FC2
  comparisons pass. Split's own rank-partial oracle has six near-boundary
  tolerance failures, retained in the raw JSON. Do not hide or relax them.
- Numerical tests through `ef182051`: five EP1 passes and five EP2 passes
  per rank, including H64/I64 and H192/I320 with 257 skew-routed tokens.
  Host cleanup suite: 56 passes. Existing host regression passes with CUDA
  visible after its CPU-only run encountered the expected no-GPU failure.
- `ef182051` removes the ignored new `fast_math` field and rejects invalid
  output or an unprepared positive-token CUDA graph capture. `sync=True`
  synchronizes after final reduction. Existing BF16 interfaces are unchanged;
  the compute kernel remains the source committed at `b5d2672`.
- Benchmark source freeze `15eb1c62` adds JSON knobs and targeted NCU metrics.
  Full 13-row CUPTI, synchronized event, and Nsight runs omit the optional
  cross-backend final-tensor check based on the independent numerical evidence.

Prepared candidates in `candidates/`: vectorized shared stores, static weight
metadata, packed preload before acquire, and full decode before acquire.
Each has independent provenance and an unchanged arithmetic baseline.
No candidate performance claim precedes GPU tests and profiling.

## Planned optimization loop

After single/multirank numerical tests and full sweep correctness pass:

1. Capture same-source split/Mega CUPTI baseline1..4096 and nsys timelines.
2. Use coordinated all-rank NCU on the actual Mega collective to attribute
   producer stalls, memory throughput, shared-memory pressure, occupancy,
   and tensor-core utilization. Isolated single-rank replay is invalid.
3. Explore dequant prefetch/overlap and warp scheduling with one mechanism
   per candidate. Prior split-kernel ledger already contains failed deeper
   lookahead variants; distinguish new Mega opportunities from repeats.
4. Retain changes only with matching numerics and repeatable end-to-end
   improvement, reporting decode and larger batches and any regressions.

## 002: Full initial baseline and synchronized control

- Frozen source `15eb1c62`: full 13-row, 100-iteration CUPTI sweep completed.
  `logs/baseline-cupti-001.log` and `.provenance.log` retain raw output and
  all 15 actual remote source hashes, verified against this committed source.
- Initial Mega spans 0.462948 to 4.357703 ms; split W4A16 spans 0.094273 to
  0.554579 ms. This is a substantial regression, not a performance claim.
- Synchronized CUDA-event graph timing at global 1/8/32/4096 confirms the
  device slowdown: Mega 0.466128/2.544000/3.630128/4.366880 ms, within about
  1% of CUPTI. Split event times are 0.074656/0.151520/0.194384/0.555024 ms.
  Evidence: `logs/baseline-events-001.log`. Host launch skew does not explain
  the Mega regression, so an additional aligned-CUPTI wrapper is unnecessary.
- Native CuTe DSL 4.7.1 binding reports its bundled compiler as CUDA 13.3;
  system toolkit remains the requested CUDA 13.2 (nvcc 13.2.78). Direct native
  query and binding source: `logs/cutedsl-bundled-compiler-version.txt`.
- Static audit finds no scheduling of empty experts. Every active expert's
  token count is rounded to a 256-token cluster tile for BF16 UMMA. At EP8,
  global 128+ activates most/all experts and padding can make device work
  nearly independent of the actual token count. This explains the plateau
  structurally but is not yet a measured bottleneck attribution.
- Nsight Systems and coordinated all-rank Nsight Compute are running before
  any candidate is applied. Candidate04 will also have a matched control
  preserving its unrolling and register buffer while moving acquire earlier.

## 003: Nsight attribution and first producer candidate

- Actual EP8 Nsight Systems captures at global 32 and 4096 show the fused
  kernel contributes 99.80% and 99.60% of summed GPU kernel time. This is
  summed-time attribution, not the primary end-to-end latency metric.
- Both shapes use 115 registers/thread, 480 threads/CTA, 74 two-CTA clusters,
  222592 dynamic shared bytes, and zero local memory per thread. Surviving
  4096 cubin resource dump confirms REG115, STACK0, LOCAL0. Shared dump
  filenames collided across ranks, so its rank identity is unproven; future
  dumps are separated by shape and rank.
- `summarize_sass.py` identifies 860 static instructions attributed to the
  baseline producer, including 752 at its scalar shared-store expressions
  and 32 STS.U16 instructions across FC1 and FC2. These are static counts,
  not executed totals. Packed weight loads already combine into LDG.E.64.
- Three coordinated NCU kernel-replay attempts (18 metrics, two shared-store
  metrics, one bank-conflict metric) fail at context-memory backup before
  collecting any counters. A real hardware-counter permission preflight
  passes. No failed run is counted as NCU performance evidence. Prepared
  TCP/full-application replay helper preserves real participation by all
  eight ranks and awaits a GPU slot.
- Baseline ring-wrap tests: six EP1 passes and six EP2 passes per rank,
  including H1024/I512/M257, `logs/baseline_ring_ep{1,2}.log`.
- Candidate01 mirrors the existing BF16 epilogue's aligned-register/CuTe
  128-bit R2S idiom on exact swizzled views. It passes all six EP1 and six
  EP2 tests per rank. First 100-iteration CUPTI Mega rows at global
  1/8/32/128/4096: 0.328674/1.657264/2.315403/2.743250/2.783182 ms.
  Initial baseline rows were 0.462948/2.542509/3.621276/4.323877/4.357703 ms.
  This is a preliminary 1.41–1.58x improvement; adjacent restoration and
  generated-store-width verification precede retention.
- Host knob-merge and ring-wrap followup committed as `eeb25500`; 63 host
  tests and full pre-commit pass. The active timing source still has the
  previous frontend plus only candidate01 in kernel.py, as recorded by
  actual source hashes.

## 004: Reference-led next phase

The user reiterated that optimizations must closely mirror efficient existing
MegaMoE and prior W4A16 code, including autotune configurations. Source mapping
is in `reference-kernel-audit-20260907.md`; reusable scheduling profiles are
AST-extracted into `candidates/reference_schedule_profiles.json`.

- The local W4A16 control uses output features on M, routed tokens on N,
  K256, and 23 paired FC1/FC2 tactic candidates. Its per-token winners are
  measured at runtime, not available as a static table. Historical baseline
  winner tuples were not persisted and must not be reconstructed as facts.
- Existing NVFP4 Mega has swapped operands and dynamic routed N rounded to
  16; its literal PTX helper is block-scaled FP4, so it cannot be copied as
  BF16 MMA without adaptation. An isolated fixed-N128 prototype is being
  prepared using established M256/N128/K256, cluster2x1 and the local W4A16
  staged packed-weight TMA/parallel-transform pipeline.
- Scheduling candidates retain current validated geometry and mirror the
  shared NVFP4/MXFP8 autotune base: group_hint512, atomic_counter,
  epi_flag_batch(2,4), flag_batch4/8, epi or reused-dispatch token-back.
  They preserve post-FC2 routing and do not enable activation quantization.
- Do not equate token domains: Mega default profiles key per-rank capacity;
  local split tuning sees gathered rows. The benchmark itself reports global
  tokens. A setup-only returned-tactic recorder is prepared for final runs.

## 005: Retained vector stores and successful coordinated NCU

Vector01 is committed and pushed as12b62378. Adjacent restored-baseline CUPTI
confirms1.44–1.58x improvement at global1/8/32/128/4096 with split control within
1.4%. Complete rows and existing reference-schedule results are retained in
`optimization_experiments.md`; all six EP1/six EP2 tests pass. The compound
existing group512/atomic/flag4/epi schedule improves8–4096 further but regresses
one token by14.7%, so no default changed. Current host suite has63 passes.

NCU TCP/application replay succeeds on all eight participating ranks, for both
vector01 and the adjacent restored scalar-store kernel at global32. Each rank
profiles one fused collective kernel with four requested metrics in one pass.
The working command is `run_ncu_tcp_application.sh <run-name> 32`; source hashes,
per-rank reports, CSV exports, PTX/SASS/cubins and provenance are retained under
`profiles/{vector01,baseline-restored}-ncu-tcp-app-t32-001/` and `logs/`.

The rank0..7 CUDA kernel durations under instrumentation range2.3–65.9ms for
vector01, substantially exceeding ordinary CUPTI on some ranks. This is
consistent with profiler-added collective waits; the exact cause of rank
skew is unproven. NCU durations/tensor percentages/LSU totals are not
production latency or occupancy evidence. Shared-store work counts
provide the structural A/B evidence; REG115 remains unchanged.

Raw counters (full kernel, same routes/weights/shape):

| Rank | Scalar bank conflicts | Vector bank conflicts | Scalar store wavefronts | Vector store wavefronts |
|---:|---:|---:|---:|---:|
| 0 | 115122231 | 1687503 | 151140475 | 19814419 |
| 1 | 101723107 | 1487843 | 133585895 | 17523687 |
| 2 | 97298898 | 1418975 | 127776534 | 16757795 |
| 3 | 84020796 | 1223143 | 110342976 | 14470891 |
| 4 | 79624590 | 1168942 | 104561618 | 13719666 |
| 5 | 79662502 | 1158878 | 104599530 | 13709602 |
| 6 | 79666618 | 1158968 | 104603646 | 13709692 |
| 7 | 84043692 | 1222429 | 110365872 | 14470177 |

Summed across ranks, shared-store bank conflicts fall68.508x and store
wavefronts fall7.626x. This agrees with static32STS.U16→4STS.128 producer
store sites, without interpreting counter ratios as end-to-end speedups.
The baseline was restored only remotely for this profiling control; source
returned to12b62378 afterward. GPU ownership then passed to the isolated
swapped-kernel correctness prototype.

## 006: TMEM requirement and reference-based correctness bring-up

The user explicitly requires decoded weight tiles in TMEM, consumed directly
inside GEMM as in the previous W4A16 kernel. The retained initial kernel used
online shared-memory tile decode, never a full BF16 matrix or global-memory
decoded-weight round-trip. The swapped prototype uses packed/scales TMA, the
existing W4A16 transform helpers, TMEM weight stages, and BF16 UMMA from TMEM.

The first compiled prototype exposed an FC1 epilogue error: a warp tried to
read paired gate/up rows outside its own32 TMEM datapaths. Dispatch was exact
and FC2 matched the oracle when given captured BF16 intermediates. The fix
reuses prior W4A16 producer-side row composition on both packed weights and
scales to pair gate16/up16 within each warp's TMEM band. No weight round-trip
or new shared-memory fragment exchange was added. EP1 H256/I256 numerical
rounds now pass unchanged tolerance (`logs/swap-ep1-numerical-006.log`).
Refactored current Mega epilogue, exact scale/routing, graphs, EP2, K tails and
production performance remain under validation.

Benchmark commit16aa85bd adds opt-in coordinated TCP/application NCU replay.
Its actual EP8 T32 four-counter run exits0 with eight reports; five host
plumbing checks and full pre-commit also pass. Artifacts are
`profiles/benchmark-ncu-application-001/` and same-named logs. Full metric-set
multipass application replay remains unvalidated.


## 007: Direct-TMEM fixed-N baseline and dynamic-N correctness

The current isolated TMEM candidate reuses the prior local W4A16 packed TMA,
scale layout, and transform helpers, with M256/N128/K256 and two stages each
for raw loads, transformed weights, BF16 activations, and FP32 accumulators.
Decoded BF16 weights occupy TMEM columns256–511; accumulators occupy0–255.
The production-shape PTX explicitly consumes the decoded TMEM pointer as MMA
operand A. No global decoded-weight buffer is created.

The current swapped Mega epilogue run loop, FC2 helper/router, and phase-aware
completion tracker are reused, with the BF16 FC1 helper substituted. Fixed-N
passes all six EP1 and six EP2 cases across recorded runs, preserving original
oracle tolerances, exact FP32 expert globals and routing, graph replay, K tails,
and ring wrap. Independent TMEM epilogue mapping/SwiGLU tests pass30 cases.
Extra H288/I448 multi-K tails pass EP1 and both EP2 ranks.

The first completed fixed-N paired sweep is
`logs/swap-tmem-fixedn-paired-002.log`, with source hashes and a frozen control
in `candidates/w4a16_swap/controls/fixed_n_timed_002`. Environment and benchmark
match earlier rows: EP8 B300, image26.05-py3/systemCUDA13.2, global token count,
3 warmups,100 CUPTI activity-span iterations, cold L2, CUDA graphs,
`--no-fused-finalize`; split and Mega share weights/routes/inputs. The optional
split-final-output refcheck is omitted after the separately documented
rank-partial BF16 rounding diagnosis. Independent oracle tests remain the
numerical gate. No profiler instrumentation is enabled in this timing run.

| Global tokens | Split W4A16 ms | TMEM fixed-N Mega ms | Split / Mega |
|---:|---:|---:|---:|
| 1 | 0.068002 | 0.111233 | 0.6113 |
| 8 | 0.161280 | 0.304322 | 0.5300 |
| 32 | 0.203074 | 0.411557 | 0.4934 |
| 128 | 0.235889 | 0.479267 | 0.4922 |
| 4096 | 0.551635 | 0.724197 | 0.7617 |

This is a substantial improvement over the historical tiled-SMEM vector
baseline, but still slower than the contemporaneous split control at all five
shapes. Historical-vs-current comparisons are not adjacent A/B measurements.
The first attempted fixed-N paired001 was stopped during split autotune setup
because it accidentally enabled the already-diagnosed strict final refcheck;
no performance or new mismatch is claimed from that attempt.

The fixed-N tactic files are empty: MoELayer selected CuteDslRunner, while the
recorder filtered only its inner CuteDslFusedMoEW4A16Runner. The recorder now
recognizes the wrapper and captures its actual returned tactic outside measured
intervals. A CPU mock verifies the selected object/tactic are unchanged and
steady-state calls are excluded; old winners cannot be reconstructed.

The next isolated candidate mirrors existing swapped Mega's align16 runtime-N
MMA policy and matching nonleader TMA-B shift in both FC1 and FC2, retaining
N128 allocation, scheduler pitch, and TMEM accumulator-stage stride. It passes
all six EP1 and six EP2 tests on both ranks, plus minimum H32/I64. Its timing
and fresh production-shape oracle checks are pending. Unapplied clamp,
reuse-dispatch, and native-SF host promotion patches are separately preserved.


## 008: Public TMEM promotion f952b398 and profiling follow-up

Commit f952b398 replaces the old SMEM decode/compute implementation in place.
Only the original public launch wrapper and FC2-alpha communication wrapper
remain; packed TMA, prior W4A16 conversion helpers, direct TMEM MMA, current
swapped scheduler/FC2 epilogue, and BF16 FC1 helper form the retained path.
Native SF preparation now occurs once in backend weight preparation. There is
no prototype installer, runtime scale cache, or full BF16 weight matrix.

The public suite now passes9 EP1 cases and9 cases on each EP2 rank. New cases
exercise batched atomic schedules in both epi/reused-dispatch return modes,
empty/refill, H288/I448/M257 tails, exact globals/routing, graph mutation, and
clamp1.5 against the unchanged independent oracle tolerance. Full precommit,
including mypy775 files, passes. GPU source hashes are in
`logs/tmem-public-validation-001.provenance.log`; one host-only type annotation
in weight validation was added afterward for mypy, without runtime change.
Raw outputs: `logs/tmem-public-ep1-001.log`, `tmem-public-ep2-001.log`,
`precommit-tmem-production.log`. The isolated host overlay passes71 tests;
its artifact-only extra tests are distinguished from actual repository tests.

The fixed/dynamic candidate comparison and all40 actual dynamic split tactic
selections are recorded in `candidates/w4a16_swap/COMPARISON.md`/comparison.json.
Dynamic Mega1/8/32/128/4096 = .114145/.302516/.409203/.469539/.712356 ms;
same-run split = .089297/.161008/.196082/.233681/.553395 ms. Dynamic-N timing
changes are small; no material gain is established. Split's one-token timing
varies31.32% between runs, and the missing fixed-run tactic cannot be inferred.
These timings precede public promotion and are not labeled final-head timings.

Fresh EP8 global8 production-shape oracle diagnostic retains exact weights and
routes: all458752 per-route BF16 FC2 values are bitwise identical to split,
Mega all-route final oracle0/57344 strict mismatches. The3 final Mega/split
mismatches and split's6 oracle mismatches are unchanged rank-partial rounding
behavior, fully preserved in `logs/diagnostic-swap-global8/comparisons.json`.
No instrumented diagnostic timing is used as performance evidence.

Nsight Systems at f952b398 completes T32/4096 on all8 devices with16 fused
launches per shape. The fused kernel accounts for98.829758%/98.554411% of
**named MoE-stage GPU time**, excluding benchmark NCCL barriers and L2 flush;
those harness activities remain present in the raw capture. Each launch uses
128 registers/thread,512 threads/CTA,grid(2,1,74),cluster(2,1,1),161152 bytes
dynamic SMEM,staticSharedMemory0 andlocalMemoryPerThread0. The non-graph,
instrumented averages643.195/1180.953us are not primary CUPTI latency.
Artifacts: `profiles/tmem-public-nsys-001/`, raw logs and source provenance.

A broader NCU stall-counter set in `tmem-public-ncu-stalls-001` requested
multiple application-replay passes. All8 ranks profiled pass1, then restarted
workers failed during second-pass NCCL initialization (stale peer socket
Connection refused); NCU consequently reports inconsistent kernel counts.
Root stopped that failed process tree and verified no GPU processes remained.
This is failed profiling evidence, not counters or a kernel/numerical failure.
A minimal replay-rendezvous fix is being investigated; the known single-pass
memory-counter set is being collected separately before scheduling sweeps.


Current one-pass NCU memory collection succeeded for T32/4096 on all8 ranks,
with16 reports under `profiles/tmem-public-ncu-memory-001/`. Complete base-unit
CSV exports, raw selected16-row table, hash manifest and analysis are local.
Shared-store wavefronts21,713–32,398 /39,929–52,377; only shared-store/whole-LSU/
elapsed-tensor metrics are measured. LSU counts correlate with profiler
runtime (r=.999989/.999880); no raw-fetch/transform-bottleneck claim follows.
NCU shared-memory configuration167936B includes161152 dynamic+1024 driver;
deeper raw stages may change the L1 carveout. Root started reference scheduling
sweep `tmem-reference-sweep-001` on frozen f952 source, five profiles over
1/8/32/128/4096,100CUPTI with actual split tactic recording. Ordinary timing
instrumentation is unset. Minimal application replay PrefixStore fix is local
only, CPU two-generation Gloo and fullprecommit pass; GPUvalidation pending.

Actual current public host suite atf952 also passes71tests in2.35s without an
overlay finder; log `tmem-public-host-001.log`/provenance. This matches the prior
overlay count because its12 constructor arms were committed into the tests.

## 009 — Reference schedules and coordinated PC replay

The completed f952 scheduling sweep is reproduced in
`TMEM_REFERENCE_SWEEP_001.md` and `logs/tmem-reference-sweep-001.comparison.json`.
All16 recorded source hashes match f952; all200 actual split tactics were
captured. All25 paired comparisons remain slower than split. Flag4-epi gives
0.110176/0.226114/0.298051/0.346707/0.649222ms at global1/8/32/128/4096.
The default gives0.106640/0.305458/0.401124/0.469076/0.715687ms. Every
nondefault schedule regresses at one token; no selector is established from
this five-profile sweep. Split-control variation is preserved in the report.

NCU `tmem-reference-ncu-pc-001` completed four replay passes on all8 ranks,
confirming the fresh PrefixStore resolves stale NCCL keys. Adaptive sampling
then requested a fifth worker only on rank0 after ranks1–7 had finished; the
collective could not restart. Root stopped exact owned process tree99535;
seven reports are partial evidence, not a complete successful capture.
The benchmark now bounds sampling to one pass in coordinated application
replay. Run002 completes T32 with all8 reports and advances to4096. Full
precommit including mypy passes (`precommit-ncu-replay-sampling.log` and source
JSON). This profiling-only change is pushed as c7713ba1; compute stays f952.

Raw3/raw5 and two-transform-group experiments remain unapplied. The latter
has passed independent source review of barrier counts, disjoint inherited
partitions and startup register redistribution, with no source-level blocker.
Its640-thread/96-register launch still requires fresh per-role codegen and
numerical validation; source budget arithmetic alone does not establish fit.

User publication guidance: keep the detailed optimization history in this
local ledger and effort artifacts. The upstream PR body should retain one
final13-row global-token1..4096 timing/speedup table, without full experiment
history. Intermediate bodies are archived locally; never relabel historical
runs as final source timings.

NCU002 has now completed both shapes and all16 reports with parent exit0.
Raw3 numerical validation passes9 EP1 in56.38s and9 per EP2 rank in81.77/81.78s.
Its exact source is captured in `logs/tmem-raw3-public-001.provenance.log`,
with raw test logs alongside. Production codegen and paired100-CUPTI
five-shape timing are running under `tmem-raw3-codegen-001` and
`tmem-raw3-paired-001`. Raw5 is deferred pending raw3/source-PC evidence.

## 010 — Confirmed raw3 control and deeper-ring trial

`RAW_DEPTH_COMPARISON_001.md` retains all20 raw timings,80 actual split tactic
records and matching source hashes for raw3 and adjacent restored raw2.
At global1/8/32/128/4096, raw3 Mega is .102480/.177778/.222241/.261378/.537045ms;
raw2 is .108608/.218801/.292419/.346786/.655702ms. Corresponding reductions
are5.64/18.75/24.00/24.63/18.10%; split-control max/min differences are
19.03/2.47/.71/.72/2.59%. The one-token result is noisy. Raw3's narrow1.0337x
T4096 win over same-run split needs repetition before a stable win claim.

Matched public codegen in `CODEGEN_COMPARISON.md` removes the earlier
fixed-N/default-schedule confound: raw2/raw3 retain REG128/STACK112/LOCAL0,
21 SASS local ops in the existing FC2 router sequence and96B explicit PTX
local depot. All256 decode instructions match after removing instruction PCs.
Static instruction counts6000/6016 differ outside those decode operations.
The hot F2FP has the same textual LDS.128 dependency85 instructions earlier.
This supports an upstream staging change, not an invented decode instruction
throughput improvement; SMEM carveout also changes with raw depth.

Raw5 passes9 EP1 in62.63s and9 per EP2 rank in77.45/78.36s. Production
codegen completes; five-shape paired100-CUPTI timing is running. This bounded
depth control follows the confirmed raw3 improvement, despite sparse sampled
raw-wait sleeps in baseline NCU. PC sampling does not establish that transient
raw readiness or TMA issue overlap can never limit performance.

The raw-depth production fitter is being prepared with actual allocation
order/layout/struct accounting. CuTe SM100 capacity232448 bytes already excludes
CUDA's1024-byte per-block reserve; do not subtract that reserve twice. Earlier
CPU experiment estimates including an extra1024 were conservative checks.

## 011 — Two-group register-pool failure and correction

The first raw5/two-group640-thread candidate emitted all8 cubins but hung
during production warmup. Root attached CUDA-GDB to worker123107 and captured
all CTA/thread PCs plus focused instruction disassembly. Epilogue warps were
looping at USETMAXREG.TRY_ALLOC.CTAPOOL176, transforms waited for a free TMEM
stage, and MMA waited for decoded inputs. Logs are
`logs/tmem-raw5-transform2-gdb-{001,002}.log`. Root stopped only the owned
process tree123039. No timing or successful liveness is claimed for001.

The prior source feasibility proof was wrong: unused SM registers are outside
the CTA's initial pool. Launch640*96 allocates61440, while proposed targets
176/80/64/96/96 require65536. The original artifact/review now links the
correction in `candidates/w4a16_swap_transform2_raw5/HANG_AUDIT.md`.
Separately, PTX requires every warp of a warpgroup to execute the same
setmaxnreg instruction; four per-control-warp sites are now hoisted into
one warpgroup-uniform80-register decrease. This inherited contract issue
will also be corrected on any retained one-group arm.

Corrected002 decreases both transform groups to80, balancing
128*(176+80+64+80+80)=61440. Fresh production warmup completes on all8 ranks.
`TRANSFORM2_CODEGEN_REVIEW_002.md` confirms actual REG96/640threads and the
correct four register sites. The existing40 PTXlocals/21 SASSlocals/96B
explicit router depot remain unchanged; no added transform or other local
traffic appears. EP1 passes9 in54.71s; EP2 passes9 per rank in81.52/81.86s.
Five-shape paired timing is running. The next one-group control will include
the same uniform control release so group-count comparisons remain meaningful.

Publication update: the single Final performance table is refreshed at each
new measured best. Raw5 five-shape values are published with exact source
overlay and pending-promotion caveats; remaining grid cells await a full13
run. Root will replace these on each new best without adding history tables.

## 012. Preferred-five fitter promotion and large-H diagnostic

The host stage fitter, existing flag4/epi default profile, and uniform control-warpgroup register decrease are integrated in the working tree. The fitter counts actual scheduler/control/transport/rawA/SF/B storage, tries raw5 down to raw2, keeps activation/decoded TMEM/accumulator stages at2, and rejects oversized shapes. CPU artifact validation covers552 layouts (140 expected rejections).

GPU run `tmem-fitted5-public-001` gives9 passes and1 failure in EP1 (76.96s); EP2 was not started after the failure. The new H9216/I64/M257 stress case has worst oracle overshoot193.0321 (|d|231.9987 vs unchanged tolerance38.9666). No tolerance adjustment or test removal has been made. `diagnose_h9216.py` compares exact inputs/weights at fitted4 and forcedraw2: every final output and every BF16 per-route FC2 value is bitwise equal. Both fail the same oracle cell. This rules out the newly fitted raw depth as the source of this observed difference; split/FC1 reference diagnosis remains in progress. Raw evidence is `logs/diagnostic-h9216-001.log`, its comparisons JSON, and remote outputs.pt.

Full13 CUPTI run `tmem-fitted5-paired-001` uses this same candidate while the new fixture failure is investigated. Measurements do not supersede numerical validation or authorize an unsupported correctness claim. Source provenance includes the exact kernel SHA and benchmark/source overlay hashes.

### Full13 result and PR publication

`tmem-fitted5-paired-001` completed all13 paired shapes,100CUPTI iterations. All16 recorded source hashes were checked against the frozen candidate/c7713ba1,104 actual split selections were checked (13 per rank). Raw/derived values and tactics are in `logs/tmem-fitted5-paired-001.final-table.json`. PR5019 Final performance was refreshed with this complete run and remains draft at c7713ba1. The pending H9216 numerical gate is explicit.

| Global tokens | Split ms | Mega ms | Split/Mega |
|---:|---:|---:|---:|
| 1 | 0.081200 | 0.100464 | 0.8082 |
| 2 | 0.101633 | 0.122385 | 0.8304 |
| 4 | 0.137296 | 0.138289 | 0.9928 |
| 8 | 0.156322 | 0.170849 | 0.9150 |
| 16 | 0.169010 | 0.183089 | 0.9231 |
| 32 | 0.202833 | 0.213249 | 0.9512 |
| 64 | 0.216993 | 0.238513 | 0.9098 |
| 128 | 0.233571 | 0.252625 | 0.9246 |
| 256 | 0.242513 | 0.254866 | 0.9515 |
| 512 | 0.238993 | 0.259026 | 0.9227 |
| 1024 | 0.260914 | 0.274498 | 0.9505 |
| 2048 | 0.350498 | 0.347442 | 1.0088 |
| 4096 | 0.554325 | 0.508981 | 1.0891 |

Mega remains slower at1–1024, near parity at2048, and1.0891x at4096 in this process run. Do not substitute earlier row minima. Onegroup constant raw5 and fitted5/uniform-control source differ; attribution of small-token variation awaits matching codegen and repeat comparisons. Corrected2group did not establish a consistent gain and remains an isolated artifact.


## 013. Two decode groups retained in fe4f8132

The prior section records the decision state before the matched full-grid run. The now-pushed draft head is `fe4f8132439df1b812f77279e7d033a5128f1ed4`: two same-K decode groups at 80 registers each, preferred-five raw fitter, uniform control register release and flag4/epilogue default. Existing geometry and decoded TMEM depth remain M256/N128/K256 and two stages. Full raw timing/tactic/source comparison: `FITTED_TRANSFORM_GROUP_COMPARISON_001.{md,json,csv}`. The complete thirteen-row current table is `logs/tmem-fitted5-transform2-paired-001.final-table.json` and PR_BODY.md; no repeat minima replace its rows.

The apparent T64 two-group regression in that full run did not reproduce in the bracketed 2/1/2 control. At T64, Mega medians were .232978/.237953/.234482 ms (split .211121/.210033/.211410); at T4096, .508210/.513075/.511861 ms (split .545139/.550773/.551924). Both two-group arms were faster at both shapes. All twelve raw results, 48 split tactic records and sixteen source hashes per run are preserved in `FITTED_TRANSFORM_GROUP_REPEAT_001.{md,json,csv}`. This supports retaining two groups without claiming confidence intervals or older-toolchain performance.

Current validation: ten EP1 passes in63.24s; ten per EP2 rank in89.71/89.76s; 79 host passes in2.25s; full pre-commit including mypy/Ruff passes. Exact tested manifests match fe4f8132 despite the pre-commit host log retaining prior Git HEAD c7713ba1. The H9216 failure is now attributed in `H9216_NUMERICAL_ATTRIBUTION.md`: correctly prepared split and Mega are bitwise equal at all FC1, per-route FC2 and final outputs in raw and normalized arms. Raw FC1 midpoint rounding is amplified by FC2; both fail the same unchanged final oracle. Only the new H9216 fixture normalizes FC1 globals by sqrt(H); original nine fixtures and tolerances remain unchanged. An earlier split diagnostic used the wrong gate layout and is explicitly marked invalid, with its artifacts preserved.

The current EP8/global8 independent diagnostic is `logs/diagnostic-fe4f8132-global8/comparisons.json`. Mega and split have bitwise-identical 458752 per-route FC2 values. Mega passes the independent all-route oracle; split's own rank-partial oracle has six near-boundary failures. Three final cross-backend cells fail because split rounds rank-local weighted partials to BF16 before rank combine. Optional benchmark final refcheck remains excluded; numerical tests and independent diagnostics retain their original tolerances.

Current two-group PC NCU reports all complete with one application replay per rank and zero dropped/overflow bytes, but rank2 contributes no useful compute samples. Resources are REG96/640 threads/216576 dynamic shared bytes. No new decode local-memory instructions appear; all21 local instructions remain in FC2 routing. Two-group E2M1 math-pipe and LDS MIO throttle counts are more visible; raw sample counts are not normalized across differing warp populations. Thus no claim of zero added issue-pipe contention is made. Detailed source-correlated analysis is being finalized under `profiles/tmem-fitted5-transform2-ncu-pc-001`.

The current two-group nsys run is partial (14 launches/seven devices at both shapes). Device2 has launch APIs and NVTX ranges but21 dropped incomplete CUPTI events. This is not a skipped rank. `FITTED_NSYS_CAPTURE_AUDIT_001.md` and its JSON retain the evidence. An effort-only finite-process-exit capture retry is running with capture-range-end=none; the strict16-launch/eight-device audit remains unchanged. Instrumented durations never enter the performance table.

## 014. Activation and cache-hint audit; descriptor-prefetch trial

`W4A16_ACTIVATION_AUDIT_001.md` confirms FC1 SwiGLU is already fused and generated as the retained packed FP32 sequence from PR4048, including packed alpha multiply and BF16 conversion. Reassociating to the other Mega helper changes rounding; its NVFP4 clamp helper also differs in NaN/limit assumptions. No speculative activation rewrite is retained.

`candidates/w4a16_cache_hints/README.md` confirms packed-weight TMA evict-first, BF16 activation TMA evict-last, default SF policy, token-pull evict-first and normal dispatch-pool stores. The prior W4A16 ledger rejected extra SF priority and FC1 output eviction hints. These are already established policies, not new gains in this run.

The only missing retained pattern found was startup prefetch of the six TMA descriptors. The isolated eight-line candidate is `candidates/w4a16_cache_hints/descriptor-prefetch.patch`; frozen measured kernel SHA256 is `1b827889d20de5c2d770d1f9b98ed0de79d78abc2d6b71cf043680ed6b2eeedc`. Production codegen completes. The first four-shape paired run `tmem-descriptor-prefetch-paired-001` gives split/Mega ms: T1 .080913/.109889, T8 .147281/.167810, T64 .220498/.233090, T4096 .551587/.512468. No win is established; an adjacent restored-fe4 control remains required. Current local source has the isolated candidate, while remote is restored to fe4 for the profiler retry. All raw outputs and tactics are preserved; no PR table promotion has occurred.

Next isolated geometry experiments are `candidates/w4a16_m128_n64/current2group/combined.patch` and then `candidates/w4a16_n64_transform3/transform3.patch`. CPU probes pass224 cases with64 expected oversized rejections each; neither has GPU evidence yet. The second mirrors the standalone fitter to consume otherwise-free TMEM columns for a third decoded-weight stage at N64. Group count, register targets and raw preferred depth are held constant.


Descriptor adjacent control `tmem-descriptor-control-paired-001` has split/Mega ms T1 .068736/.092033, T8 .151345/.160818, T64 .210402/.227314, T4096 .550629/.516021. Relative to this restored-fe4 control, prefetch regresses Mega T1/8/64 by19.40/4.35/2.54%, and improves4096 by0.69%. T1 split drift is large. No repeatable benefit justifies retention; candidate remains archived and is removed from active source. Codegen confirms six PTX tensormap prefetches/six SASS UTMACCTL.PF instructions, +24 whole-function instructions, unchanged REG96/640threads/STACK112/local footprint. Descriptor prefetch is not tensor-data prefetch.

The finite-exit nsys retry still has14/seven coverage at both shapes. All processes now report50/50 CUPTI buffers, but device2 alone drops163 incomplete timestamp events. Thus the first-Stop flush race does not fully explain this capture. External-stop control is running. Reports identify hardware CUDA tracing (Blackwell HES); installed cuda-sw tracing is a separate potential diagnostic, not an established fix. No kernel changes are made to work around profiler timestamp loss.


Software-trace nsys `tmem-fitted5-transform2-nsys-software-001` completes and passes the unchanged strict16-launch/eight-device gate at both32/4096. All named routing/staging/fused/reducer rows have16; no CUDA incomplete/drop timestamp diagnostics. Recorded resources96regs/640threads/216576dynamicSMEM match the exact fe4source. The generic NVTX warning is retained, not interpreted as complete processwide NVTX coverage. Artifacts: `logs/fitted-nsys-capture-software-diagnostic-001.json` and `profiles/tmem-fitted5-transform2-nsys-software-001`. Explicit externalstop001 failed with Nsight StopRequest after all8tails were ready; root released that exact session's tails, confirmed allPIDsgone, and preserved failure. Software trace is the first successful current two-group capture, not a kernel performance change.

N64 baseline source5ea9b59f is now applied locally and remotely. The first numerical launcher001 failed before kernel dispatch because the effort plugin read MoEEpLayer._workspace before lazy initialization. This is a harness error, not candidate numerical evidence. Original log is preserved; helper repair is underway. In parallel with CPU repair, root runs production M256N64 codegen/warmup as an independent liveness/assembly gate, with all instrumented timing discarded.


## 015. N64 geometry baseline and exact fallback-test correction

Both M256N64 and M128N64 compile/warmup on all8 B300 ranks. `profiles/n64-codegen-audit-001/ANALYSIS.md` preserves24 rank captures including fe4control. Both N64 variants have REG96/STACK0/no LDL or STL instructions, compared with N128's112-byte stack and21 FC2-router local instructions. M256/M128 static instruction counts5504/5344 versus5672 control are not throughput metrics. TMEM512 allocation,128 decoded-A base/stage columns, runtimeN descriptor, CTA-group and barrier counts match the intended geometry. Dynamic shared memory183808/216576 remains a fitter prediction until a profiler launch record verifies it.

Corrected numerical harness passes10 EP1 (57.87s) and10 each EP2 (85.31/85.31s) for M256N64 (`tmem-m256n64-public-002`), and10 EP1 (55.62s),10 each EP2 (85.43/85.18s) for M128N64 (`tmem-m128n64-public-001`). Every test/rank has observed public+compiled geometry and preserved tolerance. Original001 harness failure was before lazy workspace initialization, and is retained separately. Baseline source iskernel5ea9b59f with two decoded stages; these are not stage3 results.

M256N64 four-shape paired run is analyzed in `M256N64_TIMING_001.{md,json,csv}`. Split/Mega ms at1/8/64/4096: .069136/.091089, .152801/.159825, .212369/.216242, .544930/.567268. Against the restoredfe4 control, Mega changes -1.03/-0.62/-4.87/+9.93%, with split spread .58/.96/.93/1.05%. Small1/8 differences are near variation;64 improves,4096 regresses. All16sourcehashes and32actualtactics verified; onlykernel/epi/frontend changed. The source-start gap14m49s is disclosed. No universalN64 promotion; M128 and third-stage trials remain separate.

The realGPU defaultM256N128 H9216 single-case control (`logs/tmem-h9216-observed-control-001`) records raw5, decoded2, acc2 and passes in8.80s. This confirms the prior raw4 claim was incorrect; earlier raw-vs-forced2 labels did not establish the fitted depth. Exact frozen-fe4 CPU factory/prefix probe agrees: H9216=231936B/raw5; H9280 fits raw5 exactly; H9472 raw5would233984B and selectsraw4=215552B. The newfixture patch replaces only the normalizedH9216 row/id/comment with H9472,37 K256 tiles, keeping10 tests and originalnine/tolerances unchanged. Saved H9216 numerical parity diagnostics remain valid and preserved; current PR/README remove its unsupported raw4 claim.

Local source now has the isolated third-TMEM-stage patch, kernelSHA34bbdfba91e4743a7079d436c3181e3825ca771fe584f910c4ee1c37a4165152, plus H9472/host-geometry tests and optional nsys CLI flags. Remote remains baseline5ea9 during M128N64 timing. The nsys flags preserve previous defaults and are outside kernel timing behavior. Stage3 GPU validation/timing has not yet started.

## 016 — Curated autotune integration and C2 interruption (2026-09-08 UTC)

The user requires two decode warpgroups for all future tactics; no new one-versus-two comparisons. The interface mirrors existing Mega dictionaries/collective autotune/cache: three validated M/N pairs (M256/N128, M256/N64, M128/N64), K256, flag4/8 and epi/reused-dispatch return, twelve candidates. Raw and decoded stage counts remain derived; no arbitrary register/stage/group knobs.

The N64 three-decoded-stage candidate passed ten EP1 and ten per EP2 rank for each M256/N64 and M128/N64; raw logs and observed geometry records are local. Current public CPU validation passed90 tests and full pre-commit. Older numerical manifests used tracked-only enumeration and omitted untracked remote shim/test files: those manifests alone do not attest the complete source. Independent codegen/timing explicit hashes and observed geometry remain separate evidence. A v2 numerical provenance helper now requires explicit runtime/oracle/helper files and rejects source mutation/missing paths. Historical manifests are preserved unchanged.

The old devbox fi-w4a16-mega-0907 disappeared during the M128/N64 stage3 paired run (session exited137). M256/N64 stage3 codegen/timing and M128/N64 stage3 codegen had completed remotely, but none were fetched. No stage3 latency or codegen claims are made. Numerical and earlier baseline artifacts were already saved locally. Managed h returned exit0 for a missing box, so remote.py now requires remote execution/completion markers and status before accepting output, and validates base64 downloads. Local missing-box/success/failure checks pass.

Live NVIDIA release26.08 matrix rechecked:26.08 usesCUDA13.4.1,26.07 uses13.3.1,26.06 uses13.3.0,26.05 remains newestCUDA13.2. Replacement fi-w4a16-mega-0908 requested onC2, namespaceziangli, eightB300, --bare, explicitnvcr.io/nvidia/pytorch:26.05-py3, no size/queue override. Fresh same-node controls are required after recovery.
Source: https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html

### 016 validation and publication

Replacement C2 host hu-pdx-88 uses eight B300/driver590.48.01, nvcc13.2.78, torch runtime2.12.0a0+5aff3928d8.nv26.05 (distribution metadata2.12.0a0+5aff3928d8.nv26.5.50603568), DSL4.7.1, CUPTI Python13.2.0/runtime13.2.86, nsys2026.2.1 and ncu2026.1.1. Setup/environment log is saved as logs/recovery-install-0908.log. NVSHMEM reports loaded3.6.5.

Current M256/N128 public GPU suite passed10EP1 (171.59s, including first-use quantization JIT) and10eachEP2 (89.61/89.78s); v2 verifies1,571 source files/337 required paths plus3 helpers unchanged. H9472 observed raw4/decoded2/acc2/2WG640. Real all12 auto warmups passed the existing oracle on EP1 and EP2 (H256/I256/E4/top2,17source tokens onrank0 and0onEP2rank1), including flag8. Winner agreement, rank0 cache, fresh None-layer reuse, 3stable and1changed-input graph replay pass; allgraphs match eager exactly. Raw records/manifests saved under logs/auto-lifecycle-ep{1,2}-001.

Host first attempt had4new allocation-test fixture failures (EP bootstrap unbound); no runtime implementation failure. Binding one-rank BootstrapConfig fixes the fixture. Fresh exact public host105passed2.72s with1,570 source hashes; fullprecommit passes3,683 files includingmypy/Ruff, no hook/source changes. Evidence recovery-autotune-host-002 and precommit-w4a16-autotune-public-002.

Committed/pushed6315f94ceb279db53ec3149a7d81e19b332c8dd0, perf(moe): add curated W4A16 MegaMoE autotuning. All1,571 GPU lifecycle source hashes match the commit. DraftPR5019 body now documents the thin tuner andcurrentvalidation while explicitly retainingfe4's historical full13 table until newtimings complete. No comments posted.

Fresh full13 paired run tmem-auto-full13-001 is control thenauto in two processes through the existing extended benchmark,100CUPTIiterations and3warmups, graph/coldL2. The controls andactual returned104Mega winners are recorded separately from the capacity-keyed cache; T1/2/4/8 allsharecapacity1, so the final cache cannot reconstruct earlychoices. No rowmin promotion.

### 016 full-grid measurement and current PR table

Fresh replacement-node series `tmem-auto-full13-001` completed control then auto, exactly two processes. All 1,571 source files and four launch helpers remained unchanged and match 6315f94c. The audit validates all 52 original raw latency values, 208 actual split selections, 104 rank confirmations of 13 Mega winners, and all 156 online candidate scores. The first analysis parser expected one space after `us`; the existing tuner prints two. Widening this field separator to whitespace fixes the parser without changing raw evidence. Original launch and tests are unchanged.

#### Complete control and auto observations

Tested source `6315f94ceb279db53ec3149a7d81e19b332c8dd0`; same replacement node and source for both processes. B300 ×8, H7168/I2048/E256/top-k8; global tokens; BF16 activations/wire and NVFP4 weights. Three warmups,100 CUPTI iterations, CUDA graphs, cold L2, split `--no-fused-finalize`. Latency is median per-iteration maximum-rank GPU span, in ms. Online host-ranking scores are excluded.

Fixed control: M256/N128/K256, flag4, epi return; all arms use two decode groups. Ratios >1 favor auto. Each displayed latency is the original raw printed value.

| Global tokens | Split fixed-run | Fixed Mega | Split auto-run | Auto Mega | Split/auto | Fixed/auto | Actual auto choice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.084656 | 0.078992 | 0.077057 | 0.078384 | 0.983× | 1.008× | M128/N64, F4, epi |
| 2 | 0.099537 | 0.114193 | 0.108113 | 0.123761 | 0.874× | 0.923× | M256/N128, F4, reuse |
| 4 | 0.142113 | 0.139169 | 0.136913 | 0.132977 | 1.030× | 1.047× | M256/N128, F8, epi |
| 8 | 0.157409 | 0.156321 | 0.153633 | 0.158385 | 0.970× | 0.987× | M128/N64, F8, reuse |
| 16 | 0.182721 | 0.177345 | 0.180289 | 0.186434 | 0.967× | 0.951× | M256/N128, F4, reuse |
| 32 | 0.204289 | 0.204049 | 0.206737 | 0.208850 | 0.990× | 0.977× | M128/N64, F8, reuse |
| 64 | 0.209154 | 0.235665 | 0.224273 | 0.224417 | 0.999× | 1.050× | M128/N64, F8, epi |
| 128 | 0.235793 | 0.239442 | 0.220817 | 0.227986 | 0.969× | 1.050× | M256/N64, F8, epi |
| 256 | 0.230530 | 0.255202 | 0.243474 | 0.231026 | 1.054× | 1.105× | M256/N64, F4, epi |
| 512 | 0.238689 | 0.245569 | 0.241681 | 0.235009 | 1.028× | 1.045× | M256/N64, F8, epi |
| 1024 | 0.261329 | 0.268049 | 0.255842 | 0.252481 | 1.013× | 1.062× | M256/N64, F8, epi |
| 2048 | 0.338770 | 0.343922 | 0.350083 | 0.325554 | 1.075× | 1.056× | M256/N128, F4, reuse |
| 4096 | 0.552915 | 0.508131 | 0.538869 | 0.487970 | 1.104× | 1.041× | M256/N128, F4, reuse |

One process median per arm; repeat close/unstable points before promotion. Split control changes include fresh tactic selection, so they are context rather than confidence bounds. All52 raw values are shown above;208 original split selections and104 rank confirmations of13 Mega choices are retained in comparison.json. Capacity1 cache ends at T8; earlier choices come from their actual row records.

The current auto process is 1.022011x faster by equal-shape geometric mean than the fixed Mega process, with small-token regressions and moving split controls. At4096 auto is0.487970ms vs split0.538869ms (1.104307x); at256 auto0.231026 vs fixed0.255202 (9.47% reduction) and paired split0.243474 (1.053881x). PR5019 Final performance was updated to the entire current auto13 table, including losses, selectedtactics and isolated-cache reproduction. No row-wise minima. Draft/source6315 verified after publication.

Focused repeat plan selects16/256/4096:16 has a5.12% Mega regression while split decreases1.33% and keeps tactics;2 is moreconfounded by8.62% splitmovement and a changedrank1tactic. Repeat recorded explicit winners then fixed control to reverse the original process order. No fresh online choices in the repeat.

Current N64 software-nsys256 completes with source unchanged:16fused launches/eightdevices; routing, zeroing, fusedkernel and reducer each16. Actual resources640threads/96registers/183808dynamicSMEM,cluster2/grid2x1x74,localMemoryPerThread0. This verifies the former SMEMprediction, while SASS independently determines local instructions. Instrumented317.014us average is not benchmark latency. Current all8 PC-onlyNCU is inprogress.

### 016 recorded-winner repeats

#### Raw adjacent repeat evidence

Winner then fixed, two processes on frozen6315 source;100 CUPTI graph/cold-L2 samples per row. No new auto search and no substitution into the published full13 table. Positive change means the recorded winner is slower.

| Tokens | Fixed split ms | Fixed Mega ms | Winner split ms | Winner Mega ms | Winner change | Split change | Split tactic changes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 0.176081 | 0.178193 | 0.165906 | 0.178705 | +0.287% | -5.779% | [5, 6] |
| 256 | 0.242273 | 0.241473 | 0.240337 | 0.222130 | -8.010% | -0.799% | [0, 3] |
| 4096 | 0.543283 | 0.513394 | 0.559395 | 0.494771 | -3.627% | +2.966% | [] |

All12 raw values,48 original split selections and48 resolved Mega records are retained. Two decode groups are verified from the matched kernel's unconditional source assignment; this hook did not capture compiled group count. Split changes include fresh selections and are not confidence bounds. No row minimum or confidence interval is inferred.

Both processes completed with unchanged source and passed all plan, entrypoint, original source/helper, raw, actual split selection and resolved Mega config checks. The source fixes two decode warpgroups unconditionally; the repeat hook does not expose an extra internal tuning knob or pretend to measure the compiled group count. Source-attested groups are supported separately by same-source GPU codegen and profiling. No third repeat is warranted. The current table remains the full13 auto run, not these selected-row minima.

This comparison changes N geometry and decoded stage depth together. It does not isolate stage3 versus stage2 at identical N64; the old-box stage2 measurements cannot supply a same-node causal control. The third stage consumes otherwise unused allocated TMEM and passed numerical/codegen gates, but its individual latency contribution remains unmeasured.

### 016 retained next-step research, not shipped

The K128 artifact `candidates/w4a16_k128` changes only supported tile validation/derived host layouts. It keeps two groups,640threads and derives decoded depth4(N128)/6(N64). It passes224 real host CuTe layout cases, including68 expected SMEM rejections. It has no GPU numerical or timing evidence and does not expand the twelve-tactic production grid. At H7168 its predicted preferredraw5 dynamicSMEM is121344B(M256N64),137728B(M128N64/M256N128); smaller K doubles pipeline handovers.

The M128/N64 physicalcluster1 artifact `candidates/w4a16_m128n64_cluster1` changes three config guards and the launch cluster, keeping the device method AST identical. It passes88 CPU cases across raw5/4/3/2 with24 expected capacity rejections plus80 config checks. Installed C1 pipelines use local release with maskNone, not multicast bitmask1. At H7168 it predicts216576B/raw5/decoded3/twoaccumulators and640threads. No GPU gate or performance claim. Neither artifact is applied to active6315 source.

### 016 completed current N64 profile interpretation

Current all-eight-rank PC-only capture is fully audited in `profiles/tmem-n64-stage3-current-ncu-pc-001/independent-audit/ANALYSIS.md`, with the exact reviewed PC map, raw reports, source snapshots, rank CSV and unresolved PCs preserved. Every correlated metric conserves aggregate/instance/PC sums; zero sampler overflow and dropped bytes. Reported sampling aggregate passes2 and application replay passes1 are distinct. Total9,374,121 samples include1,482 unresolved samples, retained explicitly. Rank0 full5520instruction SASS has no LDL/STL anywhere; mapped sampled instructions agree across all8. Full unsampled disassembly scope is rank0, not an all-rank binary-equality claim.

Control-flow-reviewed sleep samples: scheduler work publication6,863,792; FC1acc7,458; free decodedTMEM295; free raw48; MMAactivation16; FC2acc13. Zero sampled raw-ready/MMAdecoded/freeacc sleep sites do not prove zero dependency stalls. Large rank skew and collective replay preclude production bottleneck or normalized contention claims. A source-line tag at free-accumulator stub0x14600 points misleadingly at decodedwait; caller/controlflow and barrier0xb0 identify the true accumulator-empty wait. No additional lookahead or stage-depth change is justified by these samples.

PR5019 body final publication verified against local PR_BODY.md at open draft6315; all13 raw values/ratios and shell reproduction blocks checked. Current upstream pre-commit/docs pass, Setup/matrix remain skipped by permission workflow and aggregateTestResultsSummary fails; no GPU CI pass claim. No reviewer comments/replies posted. Source checkout is clean; no running GPU experiment remains.

## 017. Physical-cluster experiment and genuine pre-13.2 validation (2026-09-08 UTC)

The user requests continued CUDA13.2 optimization plus a second C2/B300 CUDA13.0 box, a functional and performant pre13.2 decode path, and a complete1–4096 final table for that environment. Two decode warpgroups and the curated twelve-tactic interface remain fixed.

### 017a. M128/N64 physical C1: tested and rejected for promotion

Applied only `candidates/w4a16_m128n64_cluster1/cluster1.patch`:19 insertions/9 deletions in three shim files, no vendor/device-method AST or default/tuner changes. Source kernel e00942e45f690e22258bb7f649b1be87b5a1cad72d61286251f6885ed10da42b. C1 uses the existing one-CTA MMA/layout/local pipeline patterns and launches configured cluster1 rather than2. Geometry M128/N64/K256,640threads/two groups, raw5/decoded3/acc2 at H7168 remains identical to C2 control. No weight materialization is introduced.

Fresh C1 numerics pass10 EP1 (59.09s) and10 on each EP2 rank (82.24/81.70s). Independent audit checks all1,571 source hashes/337 required paths and7 helpers unchanged, plus16 compiled observations per rank:15 raw5 and1 raw4,512 TMEM columns,128 accumulator plus384 decoded. Public cases and tolerances are unchanged. Evidence: `logs/tmem-c1-numerics-001-c1-ep{1,2}` and `candidates/w4a16_m128n64_cluster1/c1-numerical-audit-001.json`.

`tmem-c1-controls-001` executes C2-before/C1/C2-after on the same patched source. EP8 DSV3, three warmups/100 CUPTI graph/cold-L2 iterations, flag4/epilogue return/group512/atomic/epi flags2,4, in-kernel reduction false. All30 raw values and120 actual split records are preserved and verified in `logs/tmem-c1-controls-001/audit/`. The runner's draft invalid `--no-refcheck` argument was removed and checked through the real argparse declarations before any GPU launch; no failed GPU run or tolerance relaxation resulted.

| Global tokens | C2-before Mega ms | C1 Mega ms | C2-after Mega ms | C1 vs before | C1 vs after | Split before ms | Split C1 ms | Split after ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|1|0.084609|0.076832|0.077585|-9.192%|-0.971%|0.076976|0.085137|0.084001|
|16|0.171809|0.187232|0.165249|+8.977%|+13.303%|0.177922|0.179874|0.178417|
|64|0.220322|0.225153|0.222529|+2.193%|+1.179%|0.221618|0.222369|0.220673|
|256|0.236818|0.250081|0.229778|+5.601%|+8.836%|0.229937|0.241698|0.236385|
|4096|0.568707|0.556596|0.567220|-2.130%|-1.873%|0.553237|0.553428|0.545654|

T1's apparent improvement is not robust against8.30% C2 drift. T16/256 regress against both endpoints; T64 also regresses. The narrow4096 gain over M128/N64/C2 is consistent across endpoints, but remains slower than the separately recorded current M256/N128/flag4/reused-dispatch winner0.494771ms. That prior winner is not a contemporaneous control, and does not establish an exact causal gap; it provides no reason to spend a full13 sweep or profiler session on this weaker geometry. No C1 tuner/default promotion. Both local and CUDA13.2 source restored to exact6315 kernel34bb; patch, helpers, numerical evidence and all timing artifacts remain archived. K128 remains unapplied.

### 017b. Second devbox and real compiler selection

Checked live NVIDIA26.08 release matrix immediately before requesting the box:25.11 is the newest PyTorch image with CUDA13.0.2.006 (25.12 uses13.1;26.05 remains newest13.2). Requested `fi-w4a16-mega-cu130-0908` onC2 with explicit `nvcr.io/nvidia/pytorch:25.11-py3`, `--bare`, no size override. The ziangli quota was occupied by the retained13.2 box; that failed request was cancelled/cleaned, then infra succeeded on hu-pdx-119,8B300. Both boxes are independent. Request logs `logs/request-cu130-0908-{ziangli,ziangli-cleanup,infra}.log`; image source https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html .

Observed system nvcc13.0.88 and image Torch2.10.0a0+b558c986e8.nv25.11/CUDA13.0. Source is a clean independent6315 clone. The shared PR4048 decoder selects conversion using native `cutlass.CUDA_VERSION`, not systemnvcc or Torch. Actual matching DSL4.6.2 and4.6.0 cu13 wheels both report compiler13.3 and would select direct BF16 conversion; these CPU-only probes are explicitly rejected as fallback coverage. Tagged documentation claiming a different compiler mapping is stale. DSL4.5.3/cu13 reports13.1 and imports current Mega, matching the historical PR4048 pairing, but is below current overall FlashInfer package floor.

Preferred arm: isolated matching DSL4.7.1 base/core/cu12-only packages, native compiler12.9, system/Torch CUDA13.0 unchanged. Its selected extension directory has only cu12; native path/hash/maps and exact venv Python/torchrun wrapper are recorded. Global cu13 distribution metadata remains visible via system-site-packages but its extension is outside the selected native directory and not loaded. No compiler-version spoofing, gate bypass, source fallback rewrite or dependency-floor lowering. This is real pre13.2 compilation, explicitly distinguished from system13.0. The highest-compatible sibling loader has no environment selector; `CUTE_DSL_LIBS` alone cannot force cu12 when cu13 is installed beside it. Evidence: `candidates/w4a16_cuda130/README.md`, `candidates/cuda13_cross_version/loader-audit/`, `logs/cu130-preflight-dsl471-cu12-002.json`.

Preferred arm passes105 public host tests and10 EP1 GPU cases (245.68s including first quantization build), with unchanged1,572-source/337-required provenance. EP2, exact decoder tests, all12 lifecycle, generated-code proof and full-grid performance remain in progress at this entry. No CUDA13.0 performance claim yet.

Fresh cross-stack full13 series use `candidates/cuda13_cross_version/common-source-6315.json`, source_id4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045. It transparently adds the now-tracked host autotune test omitted by the historical remote overlay's Git index; all original1,571 blobs and the added test are verified against6315, four existing helpers unchanged. Historical manifests remain untouched. CUDA13.2 remote retains fe4 GitHEAD plus exact6315 source overlay; syncing the committed test and adding only its intent-to-add index entry makes the existing inventory discover it. This is an inventory correction, not new runtime code or historical backfill.

### 017c. Completed genuine fallback gates and fresh measurements

Preferred4.7.1/compiler12.9 arm also passes10 EP2 tests per rank (86.46/86.12s), all6 existing exact weight/scale decode cases (5.48s, rtol=atol=0), and the real12-candidate EP1/EP2 lifecycle. Each lifecycle validates all12 candidate oracles, one collective winner/cache write, a fresh None-layer cache hit, three stable and one changed-input graph replay exactly against eager. EP2 rank1 has zero source tokens. Root independently verified every1,572-file numerical/lifecycle manifest against the common6315 source and current local files. Evidence prefixes `logs/cu130-dsl471-cu12-public-001`, `...-exact-decode-001`, `...-auto-lifecycle-ep{1,2}-001`.

All8 production-size EP8 codegen captures pass the required fallback PTX gate: FP16x2 E2M1/E4M3 conversion and multiply, scalar FP16-to-FP32 widening and packed FP32-to-BF16 conversion; no direct BF16 E2M1/E4M3 conversion. PTX8.8 targets sm_103a; decoded stores and TMEM-A CTA-group2 MMA remain. Every rank reports REG96/STACK112/LOCAL0 and21 SASS local instructions,6,288 whole-function instructions. STACK/local operations are not absence of local traffic; source-role attribution is independently reviewed before claiming no added decoder spills. Archive and extracted artifacts: `profiles/cu130-dsl471-cu12-codegen-001`; gate: `logs/cu130-fallback-ptx-gate-001.json`.

Actual CUDA13.0 NVSHMEM runtime prints3.4.5, while installed nvidia-nvshmem-cu13 distribution metadata is3.6.5. Earlier setup notes that called the loaded runtime3.6.5 were metadata-derived and are corrected here. CUDA13.2 loads3.6.5. Full-grid comparisons disclose system/Torch/compiler/NVSHMEM/node differences and cannot isolate compiler or decoder causality by themselves. No environment change is made during either active timing series.

Both fresh series are running as `cu132-cross-stack-full13-001` and `cu130-cross-stack-full13-001`, each fixed-Mega then auto, same common source and frozen helper pair. The driver initially compared Torch distribution metadata to torch.__version__; root caught that mismatch before launch and the helper now records/checks these separate identities. Eight CPU tests include the actual nv26.05 versus nv26.5.50603568 regression fixture. Runtime observation happens after original layer warmup and before the unchanged benchmark's three warmups/synchronize/barrier, outside graph/CUPTI calls. Per-row requested/resolved/compiled configurations and actual package/compiler/decoder sources are saved. No table promotion before complete audited output.

CUDA13.0 image profilers were NSYS2025.5.1 and NCU2025.3.1; NCU lacks coordinated application-replay communicator support. Standalone newer tools were extracted under the effort without replacing CUDA/Torch. Actual versions match the13.2 tools: NSYS2026.2.1.210 and NCU2026.1.1.0/build37634170. Official downloads: https://developer.nvidia.com/downloads/assets/tools/secure/nsight-systems/2026_2/nsight-systems-2026.2.1_2026.2.1.210-1_amd64.deb and https://developer.download.nvidia.com/compute/cuda/redist/nsight_compute/linux-x86_64/nsight_compute-linux-x86_64-2026.1.1.2-archive.tar.xz . Profiling remains separate from CUPTI production timings.

### 017d. Completed cross-stack full13, published current tables and launch-timing investigation

Both `cu132-cross-stack-full13-001` and `cu130-cross-stack-full13-001` completed fixed then auto with unchanged common source6315/source_id4a3716c6e6dc7f38ae84c182ffd7e06b083b4b606849031180f8939f340a8045. Each stack supplies52 raw rows,208 actual independently retuned split selections,208 actual compiled configurations and104 auto winner confirmations. Independent analyzer validation passes; raw values, source/runtime guards, full per-rank tactic records and host ranking tables are retained in `logs/cross-stack-full13-001-analysis/`. First-use native build time is outside timing.

PR5019 Final performance was updated and read back successfully on this continuation with one complete13-row auto table per environment, replacing the stale `tmem-auto-full13-001-auto` table. It remains draft, head6315, no comments. The current CUDA13.2 table regresses versus split at1/64/128/512; CUDA13.0 at2. CUDA13.2 4096 paired speedup1.1017x; CUDA13.0 1.0562x. The two complete auto arms improve over their corresponding fixed Mega profiles by equal-shape geometric means1.026867x and1.011383x. Independent split retuning and inter-run movement preclude interpreting every paired speedup change as a kernel gain.

|Global T|132 fixed Mega ms|130 fixed Mega ms|130 change|132 auto split ms|132 auto Mega ms|130 auto split ms|130 auto Mega ms|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|0.081361|0.102049|+25.43%|0.086368|0.093920|0.096929|0.090033|
|2|0.115489|0.137249|+18.84%|0.154849|0.120336|0.127185|0.147249|
|4|0.137888|0.155088|+12.47%|0.144561|0.119441|0.174866|0.153568|
|8|0.157201|0.176482|+12.27%|0.155057|0.149425|0.197649|0.180497|
|16|0.179360|0.195410|+8.95%|0.180561|0.162817|0.228770|0.205217|
|32|0.209953|0.234241|+11.57%|0.204321|0.192802|0.254387|0.237105|
|64|0.244817|0.269778|+10.20%|0.209361|0.240321|0.281202|0.255410|
|128|0.236946|0.266162|+12.33%|0.234129|0.238546|0.296946|0.260514|
|256|0.244721|0.272146|+11.21%|0.241922|0.238226|0.312978|0.265666|
|512|0.255009|0.279299|+9.53%|0.238370|0.243601|0.304370|0.271891|
|1024|0.263362|0.295700|+12.28%|0.259954|0.250818|0.321411|0.286915|
|2048|0.335665|0.351650|+4.76%|0.349027|0.335539|0.374499|0.351411|
|4096|0.510499|0.544453|+6.65%|0.551636|0.500723|0.570468|0.540133|

Fixed-Mega slowdown is approximately20–30us across most points,4.76–25.43% first-run relative gaps. At4096 the complete auto dictionaries match across stacks and CUDA13.0 is7.87% slower; fixed is6.65% slower. No CUDA13.0 near-parity claim yet. Actual loaded NVSHMEM/NCCL differ (130:3.4.5/2.28.8;132:3.6.5/2.30.4), as do Torch, system toolkit, native compiler and node. CPU-only NVSHMEM3.6.5 loader probe succeeded but no GPU library substitution is authorized for this frozen series; there are no NVSHMEM/NCCL device API calls in timed Mega codegen. Heap/mapping effects remain possible.

Four fresh fixed N128 NSYS captures (32/4096 on both stacks), all same2026.2.1 software tracer, pass16 fused/8GPU coverage,64 named stage kernels/32 staged copies per capture, matching640thread/96register/216576Bshared resources and no CUDA-loss diagnostics. Per-rank launch spreads reach1393us and make instrumented fused means unsuitable for explaining the20us CUPTIgraph gap. Complete independent audit: `profiles/cuda13-nsys-independent-audit/`. CUDA13.2 has full1572-source before/after manifests; CUDA13.0 has narrower contemporaneous10 source hashes + HEAD6315/tool evidence, not full per-profile manifests. Generic NVTX warnings are preserved.

Source audit found current CUPTI measurement locally flushes/synchronizes but adds no inter-rank barrier before each measured replay; existing event mode barriers before replay and rank-MAX-reduces after each event, outside the event interval. This may make rank readiness relevant for Mega's cross-rank waits. It is not a pure barrier-only control: graph setup, estimate iterations, instrumentation, aggregation pacing and event boundaries differ. `SYNC_DIAGNOSTIC.md` records exact boundaries. Fixed1/256/4096 CUPTI then cuda_event reruns are in progress on both boxes with100 iterations and completed same-stack compile caches. Diagnostic001 on both boxes failed import before GPU because the parser helper analyze_ep8_autotune.py was absent; uploaded the existing helper and retried002 without touching the frozen three support files. No failed measurements are promoted.

Latest user explicitly prioritizes useful curated tactic extensions even when aggregate gains are small, then individual>32 hotspots. This changes the earlier017a retention threshold: reconsider C1 as a fourth M128/N64 geometry, not a default or arbitrary knob. Previous C1 flag4 numerical/5point timing evidence remains valid; flag8 and true16-candidate lifecycle are untested and must pass before promotion. Both decode warpgroups remain fixed. After CUDA13.0 investigation, continue CUDA13.2 general optimization and64/128/512 hotspot work, with full1–4096 timing as retention evidence and selective detailed NSYS/NCU.

### 017e. Exact cross-stack input identity and separate timer repeats

Both untimed input-factory audits pass unchanged common-source/native guards. `logs/cross-stack-input-identity-comparison-001.json` confirms all792 logical tensors have identical bytes, dtype, shape and layout across8virtualranks/13global token counts: raw/canonical/split/Mega-prepared weights, activations, local/global routing logits, routing bias, selected IDs and scores. This is deterministic factory reconstruction, not a capture during measured timing; scope is the recorded shapes/seeds. CUDA13.2 `cu132-input-identity-001` and CUDA13.0 `cu130-input-identity-001` preserve all per-rank SHA256 records.

Both `cu{130,132}-sync-diagnostic-002` runs completed fixed1/256/4096 CUPTI then existing cuda_event,100iterations each. Each arm records24 compiled and24 split selections with full before/after source guards. Every value below is its raw printed ms.

|T|132 CUPTI split|132 CUPTI Mega|130 CUPTI split|130 CUPTI Mega|132 event split|132 event Mega|130 event split|130 event Mega|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|1|0.087153|0.093697|0.097792|0.105761|0.075008|0.095024|0.084400|0.101424|
|256|0.242369|0.247969|0.302353|0.269937|0.237888|0.252800|0.304416|0.278672|
|4096|0.550836|0.516787|0.568132|0.544068|0.551120|0.519408|0.585584|0.542448|

The event protocol does not eliminate the cross-stack Mega gap:130slower4.44% at4096 and10.23% at256; CUPTI repeatedgap5.28%/8.86% respectively. Protocol differences and independent setup remain; no barrier-only causal claim. The first-run gap is not attributed to kernel decode until a same-node compiler control. Integration is preparing matchingDSL4.7.1cu13 native13.3direct versus preferredcu12native12.9fallback on the unchanged CUDA13.0 image/node, preserving Torch/NVSHMEM/NCCL/libcudart and both isolated environments. CPU identity hashes show shared package/runtime bytes match apart from expected native distribution and interpreter entrypoint metadata.

### 018. Curated C1 extension and general epilogue/role-layout directions

Latest user requests retaining useful curated tactics beyond this one workload, general-purpose hotspot fixes, full65536-register/independent decode-overlap investigation, and high-quality compile-time specialization rather than unnecessary runtime dispatch. Meaningful directions should be refined based on generated code before judging a weak initial prototype. Two decode warpgroups remain fixed.

Applied the6-file C1 catalog extension locally and only on CUDA13.2: same exact previously tested C1 admission/launch implementation plus four M128/N64/C1 flag4/8 epi/reuse choices, yielding16. The first12 choices and cache-miss default remain unchanged. KernelSHAe00942e45f690e22258bb7f649b1be87b5a1cad72d61286251f6885ed10da42b; candidate manifest is `candidates/w4a16_c1_curated16/manifest.json`; fullsource_id250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b. Current source is not yet committed/pushed.

Host121 tests pass2.89s; changed-file precommit includingmypy/Ruff passes. CUDA13.2 public C1 suite with flag8 injection passes10EP1/10eachEP2 rank in56.30/78.81/78.65s. The injection preserves deliberately explicitflag4 fixtures. Actual per-rank16 configs split8 flag8-default/8 explicitflag4, epi12/reuse4. All16 candidate lifecycle oracles passEP1/EP2 (including allfour C1 combos); EP2 rank1 has empty input, both ranks participate; one tune/cache winner, fresh None-layer hit, three bit-exact stable and one changed-input graph replay. H9472 raw4 and otherraw5 configs observed; C1 decoded3/acc2,640threads/twoWG fixed. Independent audit `logs/c1-curated16-validation-independent-001.json` checks allfive1572-source manifest sets and unchanged-after/helper hashes.

Full13 fixedCONTROL+auto16 benchmark retry `cu132-c1-catalog16-full13-002` is running with fresh DSL/driver/knob caches, completed same-stack native caches reused only after exact six-source-change and native-stack proof. Original benchmark/observer/frozen12 helpers stay unchanged. Launch001 failed in CPU dryplan beforeGPU: Python3.12 eagerly evaluated a return annotation but the AST validation namespace omittedstr, while localPython3.14 lazy annotations masked it. Addedstr and a negative-control annotation-evaluation regression test;17CPU helper tests pass. No production code/timing change from the retry, failed001 preserved separately. No C1 performance/promotion claim before complete output.

Queued general epilogue change: only process the second32-token FC1 half when its actual routed count requires it. Fixedhalf index is constexpr; v2 firsthalf is unconditional beneath the existing outer64-subtile predicate, and only secondhalf has a runtime valid-count check. Existing halfbody is unchanged in a cute.jit helper, avoiding a known plain-Python transpose-object dynamic-scope lowering hazard. All194 staticvalid-count/bounds cases preserve valid output coverage and disjointhalf scratch ranges. Outer accumulator releases, named barriers and completion counters stay untouched. Artifacts: `candidates/w4a16_fc1_half_guard/v2/`; uncompiled/unmeasured at this entry.

Another separate source-supported candidate removes the empty FC1 bulk-store commit/drain inherited from quantized Mega, since W4A16 FC1 uses ordinary BF16STG/TMEMtransposes; preserve the real dispatch bulk drain, named barrier and release atomic. Not applied.

Register audit: current initial640threads×96=61440 register pool; dynamic caps epi176, memory/MMA/sched80, dispatch64, decode80+80 exactly redistribute that pool. Installed NCU CPU model forSM103 reports65536regs,256-register allocation granularity perwarp, four-warp allocation granularity;97–104nominal initial registers perthread require66560 and cannotfit. SETMAXNREG cannot borrow unallocatedSM registers outside the CTA pool. A full64K direction is a512-thread role layout: reuse inputdispatchWG as seconddecodeWG after inputpull, then optionallyreuse it for outputpush after transformtail;176/80/128/128. Source feasibility/risk map in progress, not an implemented or timed claim. Samepool rebalance and exactSASSrole register-demand audits remain distinct alternatives.

### 019. Completed C1 auto16 sweep and retention (195946)

The prior018 entry is historical: `cu132-c1-catalog16-full13-002` has now completed, and the exact six-file proposal is committed/pushed as `1959462045f502e367055bd56ec407188dc316fd`. Full source identity is `250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b`; the original common6315 source identity is4a3716c6. CUDA13.0 remains on6315/twelve candidates. Do not transfer C1 validation or timings to that stack.

Independent analysis in `logs/cu132-c1-catalog16-full13-002-analysis/` validates all52 raw latency rows,208 actual split tactics,208 compiled records,104 returned auto choices and13 complete rankings of16 candidates. All eight ranks agree at each global shape. Before/after1572-file inventories match the proposal; completed native caches were reused only after explicit six-change/native-identity validation, while DSL/driver/knob caches were fresh. The final ten-entry capacity cache is not the thirteen-shape history; original row records preserve all choices. Online host ranking and final100-iteration CUPTI activity spans remain distinct measurements. All13 returned winners match the minimum printed host score; T64 has a printed tie, so unrounded ordering is not inferred.

The same-source fixed-Mega then auto16 comparison makes auto faster in12/13 shapes; the sole regression is T8,0.154481→0.156593ms (+1.37%), with split+5.11%. At64/128/256/512/1024, Mega changes are−6.54/−6.69/−7.07/−7.03/−8.28%. At4096 fixed0.513715→auto0.501842ms (−2.31%); paired auto split0.562021ms gives1.120x. The complete auto table still loses to split at1/32/64. Split independently retunes and moves between processes; those movements are context, not error bars. Full52 raw values and the thirteen actual choices are appended to PERFORMANCE_LEDGER.md and retained in the immutable analysis files.

C1 is selected at4/8/32/64, covering each of the four new flag4/8 × epi/reuse combinations once. Its printed online margin over the best C2 is only3.6/2.2/0.9/0.0us respectively. These small host margins do not establish stable C1 superiority in CUPTI. The remaining shape winners are M256/N64/C2 at1/2/16/128/256/512/1024 and M256/N128/C2/F4/reuse at2048/4096; M128/N64/C2 has no winners in this run. All16 candidates and count distributions remain in historical-auto12-context.json/.md.

The historical6315 auto12 comparison is mixed and is not a pure catalog-size or C1 ablation. At32, current Mega0.208241ms versus historical0.192802ms is+8.01%, while paired split moves only+0.11%; this is the clearest repeat hotspot. T8/T16 regress4.80%/3.18%, T64/T128 improve5.60%/6.15%, and T4096 changes+0.22%. Six source files/catalog and elapsed time differ; neither this context nor one full sweep establishes statistical nonregression. `historical-auto12-context.json` preserves original raw rows, all six source changes, both manifest hashes,55 evidence hashes and actual selections without row substitution.

Retention follows the user's updated preference for useful curated extensions: keep the validated C1 tactic alongside the unchanged twelve choices and unchanged default after all121 host tests, public flag8/explicitflag4 tests, all16 lifecycle checks and complete full13 measurement. This is not a universal speedup claim. Parent is publishing the entire current CUDA13.2 auto table, including its losses, while preserving the complete older CUDA13.0 table. No helper timing boundary or tolerance changed. The local analyzer initially compared parsed tuple-valued knobs with JSON lists; normalizing through JSON fixes that representation-only audit failure. Original scores/order/winners match, and malformed scores/knobs remain rejected. A later parent analyzer invocation refused to overwrite the existing analysis directory; no evidence was corrupted.

Next candidate is the general constexpr FC1 halfguard helper-v2, independently source-attested and evaluated against the unguarded C1 baseline. The baseline C1N64/F4/epi production-size T128 codegen capture `profiles/c1-n64-f4-epi-codegen-001` completed with its own full before/after manifest; candidate numerics/codegen are separate and pending at this entry. Its instrumented event value is not performance evidence.

### 019b. Halfguard-v2 generated-code gate, before timing

Halfguard-v2 source a1963c4e01c37b320b041d78f291116419c17e780f6b64c127a3202a8ab316b0 differs from published195946/C1source250553 in epilogue bytes only (33b596→6315df). Full before/after1572-file fingerprints and57 emitted artifact hashes pass for each codegen capture. No benchmark or original helper changes. Both captures run global128/H7168/I2048/E256/top8/EP8 at explicitflag4/epilogue return; event values are instrumented codegen-only and excluded from performance.

The strict matched C1M128/N64 A/B retains REG96/STACK0/LOCAL0,640threads and5320 static SASS instructions, without PTX local allocations, LDL/STL or device calls. Independent all8-rank PTX normalization finds precisely the extra valid<33 predicate/branch; after consequent predicate/block renumbering and source-location directives are accounted for, the remaining emitted PTX is identical. Actual SASS tests valid>=33 at0x9260, branches on false at0x9280 to0x9ae0, and skips the full half1 work region through0x9ad0. Accumulator release is after the join at0x9af0. This is compiled constexpr specialization with a necessary runtime valid-count guard, not a runtime half-dispatch helper. Baseline/candidate captures: `profiles/c1-n64-f4-epi-codegen-001`, `profiles/halfguard-v2-n64-f4-epi-codegen-001`.

CandidateM256/N128/C2 structure has equivalent subtile*64+32>=valid guard, seven skipped TMEM loads andthree TMEM transpose stores plus activation/conversion/global output. No barrier/atomic/reduction/call is inside that skipped region; the loop/finalTMEMfence/accumulator release are after its join. All8rank code is identical within this capture, with5672instructions,REG96/STACK112/LOCAL0 andthe existing96-byte PTX depot/21FC2router local instructions. Generic inlined source labels are resolved through surrounding pointer/valid-array offsets and vendorrouter loads, not attributed to transform spills. Strict195946N128 control is pending, so this is structural evidence rather than exact N128 A/B. `profiles/halfguard-v2-n128-f4-epi-codegen-001/independent-audit/` preserves excerpts and per-role local sites.

Existing public fixtures do not deliberately cover all routed31/32/33,63/64/65,95/96/97,127/128 boundaries. The frozen effort-only `candidates/w4a16_fc1_half_guard/v2/check_boundary_outputs.py` (SHA427fdea415fbde6f8f870cf42dfab78d35bf80270c5e0d1fd68f61566cdf8f5f) reuses existing public weights/inputs/layer/term-band oracle, adds no protocol copy, and covers48cases perrank atH288/I448/clamp1.5: twelve counts includingzero ×C1N64/C2N128 ×epi/reuse. Rank0 routes toexperts0/2; EP2rank1 has empty source but participates in expert compute. It records actual routed counts, derived CTAcounts, exactweight/input hashes andcompiled geometry/stages/contracts, and later demands bitwise BF16 candidate output equality against savedcontrol. N64 counts above64 are multiple CTA tiles, not a single valid>64. Empty experts schedule no FC1 tiles; their empty-output checks alone do not trace the outerguard. CPUsyntax/Ruff/fourplans passed; GPUexact-output gate is pending. Root will use EP2, which exercises both source/empty-rank roles; separate fullpublic/lifecycle EP1 coverage remains.

### 019c. Unapplied branch-first half-count refinement

Parent requested refining the full-tile scheduling path while v2's full13 is running, not abandoning the general halfguard direction if its first implementation regresses. Isolated v3 branches once on actual routed count before any subtile body: full invokes a private JIT helper with constexpr half_count2, partial invokes1. The helper preserves the original contiguous two-half constexpr loop and setup; this gives the compiler an opportunity to schedule across both full halves again. No new public knob, runtime half dispatch or synchronization change. Activev2 and frozen measurement/codegen helpers are untouched.

Artifacts `candidates/w4a16_fc1_half_guard/v3/`: sourceSHA4c04933c87eca37407d9eadb05482b49214383eeac117719ce7b2fd25234761a, patchSHA91471a279f11b865a21ba6e2fbf7b5cd8e421841e1594fd22323680fc496b96c, combined six-filemanifestSHAe9c2607024932f808aa6a7642cc8d5876c0f83c70200c7b6f77e53fd98677780, prospective source_id20011ffd100b1139b84eed469bb460650043947a8078417a3fc6e7dd2ebe078d. Original module AST restores exactly after undoing only the wrapper/helper specialization;194N64/N128 valid-count checks, independent CPUreview, Ruff,3.12grammar and read-only index apply-check pass. The existing frozen runner accepts the declaration.

Actual generated-code validation remains required: compiler common-prefix hoisting or tail merging could reconstruct v2's half0-then-guard schedule despite the source shape. Three static half bodies could enlarge text even though runtime executes at most two. Inspect actual full-path instruction interleaving, branch placement, registers/local sites and text size before benchmarking. No v3 GPU compilation, numerical/exact-output test or timing has happened at this entry; keep all v2 evidence and compare with exact195946 controls. The frozen v2 boundary helper has fixed source IDs and must not be spoofed forv3.


### 019d. Completed halfguard v2 full13: no promotion

`cu132-halfguard-v2-full13-001` completed both fixed CONTROL and automatic16 arms. The unchanged analyzer validates all 52 raw rows, 208 actual split choices, 208 actual compiled configurations, 104 returned automatic choices and 13 complete rankings of 16 candidates. Every before/after source/helper fingerprint agrees. Source ID `a1963c4e01c37b320b041d78f291116419c17e780f6b64c127a3202a8ab316b0` is distinct from published C1 `250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b`; their 1,572-file inventories differ only in the epilogue, from `33b5967cd477c9b775e059945d7b2234e2ee9e98b822f55c4effcba346ede795` to `6315df2722314502cfc17d7db586ed77a2505075f3763acdacff314bbef075b3`. All 337 required paths, image/node, runtime/compiler metadata, catalog and frozen helper hashes match. All 104 fixed actual configurations, compiled geometries and decoder gates match exactly across the two complete sweeps.

The raw v2 sweep is retained below. Timing remains 100-iteration CUPTI, three warmups, CUDA graph, cold L2, median of per-iteration maximum-rank GPU activity spans, EP8/H7168/I2048/E256/K8/global tokens. Online autotuning uses the existing host timing path; it is not the CUPTI measurement. Split is independently retuned in each process. No selected minima or other runs replace these rows.

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.080321 | 0.097936 | 0.097457 | 0.102640 | +4.80% | +21.33% | [1, 4, 5] |
| 2 | 0.117072 | 0.114913 | 0.116353 | 0.111473 | -2.99% | -0.61% | [1, 4, 5] |
| 4 | 0.128673 | 0.136545 | 0.137825 | 0.116625 | -14.59% | +7.11% | [1, 4, 5] |
| 8 | 0.161329 | 0.156033 | 0.162593 | 0.168450 | +7.96% | +0.78% | [1, 4, 5] |
| 16 | 0.171552 | 0.179233 | 0.178177 | 0.176801 | -1.36% | +3.86% | [3] |
| 32 | 0.205809 | 0.203856 | 0.206738 | 0.209570 | +2.80% | +0.45% | [0, 2, 3, 6, 7] |
| 64 | 0.220577 | 0.236337 | 0.224658 | 0.230178 | -2.61% | +1.85% | [0, 1, 3, 4, 7] |
| 128 | 0.235586 | 0.239282 | 0.224433 | 0.234642 | -1.94% | -4.73% | [5] |
| 256 | 0.246210 | 0.246289 | 0.245058 | 0.235025 | -4.57% | -0.47% | [0, 1, 4, 5, 6] |
| 512 | 0.240049 | 0.254833 | 0.238961 | 0.235105 | -7.74% | -0.45% | [1, 2, 3, 4, 6, 7] |
| 1024 | 0.263425 | 0.264689 | 0.260721 | 0.249202 | -5.85% | -1.03% | [1, 2, 3, 4] |
| 2048 | 0.350050 | 0.352753 | 0.344435 | 0.339139 | -3.86% | -1.60% | [0, 4, 6] |
| 4096 | 0.560867 | 0.512723 | 0.551669 | 0.498100 | -2.85% | -1.64% | [] |


The fixed C1-to-v2 series improves at T1/T2 by 7.80%/5.48%, but small-token split baselines move substantially in those processes. T4 through T4096 fixed changes span -3.06% to +2.12%; T4096 is 0.513715 to 0.512723 ms (-0.19%). No broad gain or clear full-tile regression is established by this single sequential pair. Global T4096 does not imply that every expert tile is full, and no branch-frequency data was collected.

Nine of 13 automatic choices change. Historical auto regressions at T1 (+30.17%, split +27.70%), T8 (+7.57%, split +0.08%) and T16 (+5.24%, split -0.42%) therefore combine the implementation change with different selected tactics and process conditions. Exact same automatic choices at T256/T512/T1024/T4096 move +2.08%/+0.12%/+0.25%/-0.75%. The v2 automatic process is itself slower than its fixed control at T1 (+4.80%), T8 (+7.96%) and T32 (+2.80%). C1 is selected only at T128; many online margins are below 1 us, including a displayed tie at T256. The returned winners match complete rankings and agree across all ranks. Selection uses unrounded rank-max measurements; stdout is rounded to 0.1 us, so that printed tie is not inconsistent.

Detailed cross-run tables, exact per-rank split tactic deltas, raw records and source hashes: `logs/cu132-halfguard-v2-full13-001-analysis/{comparison.json,c1-versus-v2.json,C1-COMPARISON.md,auto16-full13.md}`. Reproduction: `python3 logs/cu132-halfguard-v2-full13-001-analysis/compare_c1.py`; it reruns both frozen analyzers before deriving the comparison. Parent explicitly keeps v2 unpromoted and the published C1 table unchanged. The general halfguard direction continues as the separate branch-first constexpr v3 quality refinement; v2 codegen and all functional evidence remain preserved.


### 019e. Completed v2 numerical/lifecycle audit and strict N128 control

Independent audit of all six public/lifecycle captures is saved at `logs/halfguard-v2-validation-audit-001/`. All six have the exact a1963 full1,572-source inventory,337 required paths and frozen helper hashes. There are60 passed public calls across EP1 and both EP2 ranks,96 actual compiled events, and48 lifecycle candidate-oracle records covering the full16 catalog in EP1/EP2, flags4/8, epi/reuse, derived stages and fixed2WG. Cache reuse, three stable graph replays, changed-input graph/eager parity and the EP2 empty source rank pass. Tolerances are unchanged.

One observation gap is retained explicitly: C1-flag8 EP2 rank1 has16 compiled events but15 public_config events. Two different compiled workspaces are labeled layer2 in the reuse-dispatch reference-schedule case. The frozen observer stores id(frontend) keys without retaining the objects; ID reuse is plausible but not proven. The audit preserves both events, validates every actual compiled geometry and reports `passed_tests_with_observer_gap`; it does not invent the missing config or silently deduplicate. Future isolated512 observer copies will retain object references and reject duplicate labels. Historical helpers remain untouched.

Strict C1 N128 codegen control `profiles/c1-n128-f4-epi-codegen-001` now matches the prior v2 N128 capture's command, geometry, runtime/compiler identity and native cache origin; all57 artifact hashes and full before/after source maps pass. Both eight-rank captures have REG96/STACK112/LOCAL0,640 threads,5672 static instructions and the same21 inherited FC2-router local instructions. Whole executable PTX is equal after removing exactly the added add32/setp/branch and normalizing virtual-register/block labels; v2 adds one virtual b32 and one predicate. The SASS sequences differ in scheduling, so no timing gain is inferred. Complete audit and reproduced normalized text: `profiles/c1-n128-f4-epi-codegen-001/independent-audit/`. The earlier N128 context-only limitation is now closed by this same-geometry control.


### 019f. v3 actual branch-first codegen quality gate

Both `profiles/halfguard-v3-{n64,n128}-f4-epi-codegen-001` captures pass all57 artifact hashes,1,572-source/337-required before/after maps, same runtime/compiler/helpers/cache-origin identities against their exact C1 controls, and all8 rank resource checks. Only epilogue4c04933c differs, source20011. Each capture has separate full (14 TMEM loads/6 transpose stores) and partial (7/3) bodies, no FC1 helper call, no CTA barrier/atomic/accumulator arrival inside either body, and common reconvergence before final accumulator release. Whole-kernel compiler guardrail trap calls remain outside this region.

N64 achieves the requested scheduling quality: routed-count branch0x89e0 is before firstload0x8a60; full half1 load0x91d0 and exponential0x9260 precede half0 outputstore0x9730. v2 had serialized that half1 work after half0's store. N64 keeps REG96/STACK0/LOCAL0, no locals; text grows5320→5464 instructions (+144/+2.71%). N128 also branches before the first half but preserves its existing serial half schedule; its exact C1 baseline was already serial. N128 keeps REG96/STACK112/LOCAL0 and the same21 inherited FC2-router local operations,5672→5816 instructions (+144/+2.54%). The extra partial-half copy is a code-size tradeoff, not a runtime loop or helper dispatch.

Detailed independent audits and annotated excerpts are under each capture's `independent-audit/`. These codegen measurements are not performance timings. Parent has completed exact EP2 boundary outputs and is running the separate unchanged full13 fixed/auto sweep; retain or reject only on the combined numerical and measured performance evidence. No published table changes at this entry.


### 019g. Completed v3 full13: no broad improvement established

`cu132-halfguard-v3-full13-001` completed both original fixed CONTROL and automatic16 arms. The unchanged analyzer and independent C1/v2 comparator pass all52 raw values,208 split selections,208 actual compiled records,104 returned winners and13 complete sixteen-candidate rankings. Source20011 has exactly the epilogue4c04933c difference from C1 and v2, with the same1,572/337 source inventory, image/node, runtime/compiler identity, frozen helpers and candidate catalog. All104 fixed actual configurations, compiled geometry and capability records are identical across all three sweeps. Detailed reproducible evidence: `logs/cu132-halfguard-v3-full13-001-analysis/{comparison.json,prior-versus-v3.json,PRIOR-COMPARISON.md,compare_prior.py}`.

Timing remains the unchanged100-iteration CUPTI graph/cold-L2 EP8 benchmark at H7168/I2048/E256/top8/global tokens. These are sequential unrepeated full sweeps. The complete v3 raw table follows; no selected minima or prior rows are substituted.

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.085568 | 0.092145 | 0.083840 | 0.101680 | +10.35% | -2.02% | [3] |
| 2 | 0.118465 | 0.111601 | 0.117970 | 0.107665 | -3.53% | -0.42% | [3] |
| 4 | 0.166594 | 0.136433 | 0.145345 | 0.133856 | -1.89% | -12.75% | [3] |
| 8 | 0.165986 | 0.154817 | 0.151185 | 0.159088 | +2.76% | -8.92% | [3] |
| 16 | 0.179201 | 0.179890 | 0.178913 | 0.162946 | -9.42% | -0.16% | [] |
| 32 | 0.202977 | 0.211441 | 0.201953 | 0.202034 | -4.45% | -0.50% | [0, 2, 4, 6, 7] |
| 64 | 0.220785 | 0.236961 | 0.223393 | 0.224898 | -5.09% | +1.18% | [0, 6] |
| 128 | 0.234289 | 0.236801 | 0.233665 | 0.215729 | -8.90% | -0.27% | [5, 6] |
| 256 | 0.242466 | 0.248449 | 0.239730 | 0.230882 | -7.07% | -1.13% | [2] |
| 512 | 0.241009 | 0.245777 | 0.241393 | 0.236433 | -3.80% | +0.16% | [1, 2, 3, 4, 7] |
| 1024 | 0.261682 | 0.266865 | 0.260497 | 0.251922 | -5.60% | -0.45% | [0, 4, 7] |
| 2048 | 0.342082 | 0.343491 | 0.346691 | 0.339025 | -1.30% | +1.35% | [3, 5, 6] |
| 4096 | 0.544420 | 0.512019 | 0.531141 | 0.503459 | -1.67% | -2.44% | [2] |

Against C1, fixed T4–4096 ranges from-2.69% to+1.87%, with4096 only-0.33%. FixedT1/T2 improve13.25%/8.20%, while their split baselines move+19.14%/+29.51%; those process changes do not identify a halfguard mechanism. Seven automatic choices change and none choosesC1. Same-choice automatic T16/T128 improve3.01%/3.64%, but T256/T512/T2048/T4096 move+0.28%/+0.68%/+1.21%/+0.32%. Automatic T1 andT4 regress28.96%/13.56% against C1 with changed tactics; split moves+9.85%/+13.64%. Within v3, auto regresses10.35% atT1 and2.76% atT8 relative to its own fixed process. Split retuning and movement are recorded as context, not an error bar.

Against v2, fixed4096 changes-0.14% and automatic4096+1.08%. The generated-code quality improvement (N64 full-half scheduling restored with constexpr1/2 bodies) therefore does not establish a broad latency improvement. No captured branch-frequency data identifies any row as a pure full-tile control. Keep v3 experimental and the complete publishedC1 table unchanged; root restored C1 for subsequent paired-timer and independent512 admission work.

### 019h. Isolated512 admission adapters and no-Mega-call resource probe

Artifacts are under `candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512/`, with exact zero-destination proposal declaration `zero-dest-manifest-001.json` SHA5cae04237169fe75e24d8918e351b4ed7c1968f0bf0317fc8ca6be6ae425ddd4. This declares prospective sourcee2d88e6a564638efe464d5a586a2b0284e66cb0b14bb4b77c7743593a09a29e3: exactly the six C1 source/test changes plus newcommunication.py relative to common6315,1,573 inventoried files and338 required paths. All other native C++/benchmark/helper identities remain unchanged. This is an unexecuted declaration, not source/GPU performance evidence.

Every new compiled object must satisfy actual CUDA function REG128/512threads/two decode groups before first Mega invocation. The gate binds to installed DSL4.7.1 jit_executor.py SHA06c91ba84b7a1b43b93e0f2de97e872426104ba1773f904c58845d5ae74870ea and uses `.to(None)` then `cuFuncGetAttribute`, never invoking the compiled function. Query errors and rejected counts enter one all-rank success consensus. Successful metadata/executor references live only on the current `_CompiledMega`; cached checks perform no driver/collective work. Numerical and benchmark observers all share this gate. The resource-probe mode uses real fixed public setup, compiles and inspects one object/rank, then exits via a dedicated sentinel before returning to the frontend launch site. Its real-GPU execution is pending root scheduling.

This supersedes019e's tentative suggestion to retain all frontend references: the implemented public observer attaches monotonic IDs to objects and retains only integer sets. No external strong-reference map or pytest undo closure retains destroyed workspaces; CPU weakref tests verify collection and identity-safe rejection. Original public tolerances, all16 lifecycle candidate oracles/cache/graph checks and the full13 CUPTI benchmark/timer are reused. Native caches are reused only from their completed same-stack owner after seven-source-change validation; DSL/driver/knob caches are fresh.

CPU checks comprise6 benchmark admission tests,6 resource-gate tests and9 numerical/probe tests, plus12 synthetic driver plans, Ruff andPython3.12 grammar checks. Synthetic observations are explicitly not GPU evidence. The actual current C1 source rejects512 admission. Aggregate evidence `adapters-cpu-validation-001.json` SHA3b50cbf8f9d7b3023b9c2e7199652c894c4039dd2944ff925534c79879780f8f freezes helper hashes; README contains exact commands. No production/frozen helper edits or GPU calls were made during adapter preparation.


### 019i. Completed paired T128 scorer diagnostic and queued five-shape check

`paired-tuner-metric-baseline128-002` completed exit0, with source/helpers unchanged and no timeout. Launch001 failed before workers/GPU because `--standalone` advertised the unresolvable pod hostname; the original helpers and failure are archived. Retry002 changes only explicit localhost rendezvous (127.0.0.1:29676). Frozen worker85d3e18b compares uint8 views for bitwise output equality, preserving signedzero. Source remains exact publishedC1/250553,1,572 files/337 required paths; native caches come from completed common6315 with the exact six-file C1/native-stack proof.

Independent analysis validates384 rank/visit records,7,680 raw samples,48 visits perrank, all three forward/reverse/forward passes and scorer-order reversal. Every local ten-sample median and maximum across eight ranks recomputes exactly; rank0 gathered samples match every originating rank, all global winners agree across eight ranks, input/weight/routing bytes and addresses agree before/after, all output finite/bitwise gates pass, every graph-reset count isone before next candidate invalidation, and no tactic cache is written. Actual CUDA13.2/Torch/DSL4.7.1/compiler13.3/direct-decoder identity and mapped NVSHMEM3.6.5/NCCL2.30.4/native-library hashes match. Output bytes were not saved for independent rehash; successful output/reset checks are source-attested recorded gates.

Scorer values are hot prestaged fullforward including reducer, deliberately separate from public cold-L2 CUPTI timing. Both scores use MAX of local medians; host eager includes synchronous wrapper overhead and graph events use the existing one-forward graph utility. Global eager winners are candidate4/6/4 across the three passes; graph winners4/6/6. Candidate4=M256/N64/C2/F4/epi and6=F8. Eager first/second margins2.801/1.945/0.823us; graph0.608/0.416/0.288us. Non-tied candidate-pair ordering disagrees13/120,15/120,23/119. These are rank-local preference differences and scorer differences, not divergent collective decisions.

Candidate6 is tenth in pass2 eager ranking but first in graph ranking. Its host scores306.863–316.653us span3.19%, while graph191.600–191.648us spans0.025%. This supports a broader scorer experiment, but the tiny graph winner margins (0.15–0.32%) do not establish anF4/F8 policy or performance gain. No reason for the host variation is proven by this diagnostic. Full16-candidate/three-pass values, rank-local orders and margins,7,680 raw samples, hashes and interpretation are in `logs/paired-tuner-metric-baseline128-002-analysis/{analysis.json,raw-samples.csv,FINDINGS.md,analyze-frozen.py}`.

A fresh sibling `candidates/w4a16_tuner_metric_experiment_five_shapes/` is CPU-ready for128/512/1/4096/64;64 directly addresses the published post32 slowdown. Only the token tuple changes; worker, timers, static gate and launcher are byte-identical to completed002. Wrapper `candidates/w4a16_tuner_metric_analysis/run_baseline_five_shapes_003.py` SHA9894c8136a877a9df376fb369402d49bb7a08f56d410f51b32b1b28789a370b2 freezes original/copied helpers, saved C1/native inputs, and uses fresh DSL/driver caches. Local dryplan explicitly rejects the active512 overlay for execution; exact C1 must be restored when root schedules it after512 work. Source-copy manifest SHA f64b5ecdc09402331359ea3f92d51839569151285af59818cd0fd7674f5d6c40; CPU proof1a74e24c19d0b5f17bba7092cb5c9e8da83263e8e99494e732466f83263c3c42. No new GPU run or production/timing policy change at this entry.

### 019j. CUDA13.0 native scalar conversion tail rejected by ABA

The compact nativeF2F.BF16.F16 scalar alternative preserves the direct13.2 branch and native FP16 decode/multiply AST. Independent exactness audit rechecks all65,536 saved output bit patterns, including512 canonicalNaNs; native12.9 probe remains72 SASS instructions, with registers24→27. The104-instruction integer packed-bit form is a separate rejected probe. Neither small code size nor exactness is a performance claim.

`cu130-scalar-tail-aba-001` completed all three arms on the same CUDA13.0 image/runtime node (devbox fi-w4a16-mega-cu130-0908). Original fixed CONTROL, EP8, global1/256/4096,100CUPTI,threewarmups,graph,coldL2,two decode groups. Shared decoder B changes both split and Mega. All18 raw values,72 split selections and72 actual compiled records pass independent reconstruction and source/native checks; A2 restores exact6315/common4a3716. B's only source difference is decoder735beaa0/sourcea0e08551.

| Global T | A1 split ms | B split ms | A2 split ms | A1 Mega ms | B Mega ms | A2 Mega ms |
|---:|---:|---:|---:|---:|---:|---:|
|1|0.086929|0.105201|0.106881|0.112449|0.130721|0.107297|
|256|0.310961|0.493972|0.300291|0.274786|0.417843|0.275859|
|4096|0.568085|0.670246|0.572595|0.539011|0.716805|0.539686|

Mega B regresses against both controls by16.25–21.83% at1,51.47–52.06% at256,and32.82–32.99% at4096. Corresponding A-control spreads4.80/0.39/0.13% are not confidence intervals. Split retunes: A1→A2 changes3/0/2 ranks and each A→B changes7/8/2 ranks; B is a changed split implementation, not an invariant split baseline. Reject the scalar tail on this bracket; no instruction-level cause is established. Durable independent audit `logs/cu130-scalar-tail-aba-001/performance-audit/audit.json` SHA95711e6497bc86d759c351c4f4ed1ec5a3248d48e8f613a448eb26ea410141ec preserves all original records; environment/source restoration is separately audited. Published full13 tables remain untouched.

### 019k. Resource probe001 failure and exact CUDA-dialect repair

The first real512 probe rejected both ranks before Mega launch: `inspect.getfile(type(compiled.compiled))` did not point to the base JIT executor implementation assumed in019h. Read-only installed-source inspection established that CuTe uses a CUDA-dialect library representation; its executor lacks the base-class `exec_context.kernel_functions` route. This was an artifact admission error, not a numerical or performance failure of512. Original helper/tests/CPU evidence are preserved under `provenance512/failed-runtime-probe001/`; original run logs remain unchanged.

Repaired helper5911294a44c546c1bddd5e35692a420515b32c610e4bf658ed5b38fde7ae53c6 binds the exact inherited `CudaDialectJitCompiledFunction.library` property and installed cuda_jit_executor.py SHA1589949f04c39184dc3ef9287720b029bb4f8e1161fb8e20a416977cb6bf6583. It resolves CUlibrary→CUkernel→current-contextCUfunction, explicitly loads that function, and queries the same actual register/resource attributes. It does not call or separately pin `.to()`, infer frommaxrregcount, retain another executor, or add retry/fallback paths. All property/import/lookup/load/query errors still enter one prelaunch all-rank success consensus. Actual runtimeclass and propertyowner are recorded. Source/API proof is in `profiles/cuda132-jit-method-owner-001/`.

Twenty-four CPU tests pass including inherited-property vs subclass-file resolution, override rejection, CUDA lookup/function/load failures, same-object cache behavior and no compiled-callable invocation. One artifact test's assumption that current source must differ from512 was replaced with explicit saved-C1 negative control because root had now applied512; this does not weaken admission. Updated proof `adapters-cpu-validation-002.json` SHAbc5e276bb978cc622a0fe814b5712e486e73c0264cf81c2ac4ff0e7130da35b5. Root reviewed/uploaded and froze the repaired folder for probe002 and subsequent gates. Do not treat019h's CPU-only base-executor success as runtime validation.

The original seven-path benchmarkoverlay deliberately retains an upstream shim-contract expectation of640threads at test_w4a16_shim_contract.py:416. If512 is retained, update that assertion in a kernel-identical test-only followup and rerun full host checks; do not change current benchmarksource during its gates/timing. PublicGPU tests and220constructor trials are separate coverage, not proof that this stale upstream host assertion passes512.


### 019l. Replacement CUDA13.2 node and fresh C1 cache ownership

The CUDA13.2 devbox disappeared during the first public512 suite; root's owned process exited137 and the interrupted public logs were not fetched. No public pass is claimed for that capture. Previously completed pairedT128, repaired resourceprobe002 and codegen artifacts had been fetched and remain separate evidence. Replacement `fi-w4a16-mega-0908b` again reports hostnamehu-pdx-88 but has empty `/workspace`; hostname reuse does not establish GPU UUID/cache continuity. The five-shape scorer wrapper is saved but paused because its old native-cache owner paths were lost.

Root restored clean public C1 commit1959462045f502e367055bd56ec407188dc316fd and launched a fresh full13 fixed/auto run `cu132-recovery0908b-c1-full13-001` after pinned setup/native gates. Its results are pending at this entry. The unchanged `run_stack_benchmark.py` creates allfour native/DSL/driver caches fresh and reuses the original benchmark,100CUPTI,graph,coldL2,threewarmups and separate split retuning. There is no inherited completed-cache claim. Pure source manifest `candidates/cuda132_recovery_0908b/performance/c1-source-manifest.json` SHAec28e53b333b8a715df95d2d7db574f25b195502cb47a719ee349d4778ee2951 records exactsource250553/1572files/337required and four frozen helpers. Independent CPU replay confirms its unchanged compiled validator accepts all208 historical C1 fixed/auto records,104winners and13complete16-candidate rankings, while rejecting synthetic512 geometry. This is compatibility checking of old records, not new performance evidence.

Prospective `provenance512_c1/` preserves frozen `provenance512/` and rebases only the source admission: C1frontend/kernel changes plus newcommunication.py,250553→same e2d88,1572→1573 and337→338. Manifest SHA39d595c9b2a97d7f953d0e3f72ef2e16b377c29e2783b3b740bf808a16b48e99 pins a distinct C1schema/owner and rejects the oldseven-path declaration. Resource gate5911294, numerical/probe/compiled/public observers and validationdriver are byte-identical. Lifecycle changes only helper-inventory paths; benchmark changes self-paths and the source-boundary declaration/schema. Twenty-five CPU tests,Python3.12 grammar and Ruff pass; proof21fd971c9ea3eb06242a79f4849927cf17fefe8b8d4a0d7400932a9446dfb0b5. Independent helper closure/admission review found no new runtime/cache compatibility blocker.

The replacement512 launch must wait for the fresh C1owner's completed fullresults, preserve allfour cache directories for loader validation while reusing only the native two, and obtain its own new512source preflight. Fresh actualREG128/512/two-group resource admission precedes public/lifecycle work. Sequential driver `run_public_validation_recovery0908b_001.py` SHAd5c7fda56a0c7a06b4d2af321e91edec3c8ab7b2f405bfde85c86adba88a3830 uses new names, defaults to dryplan, checkpoints each passed capture and printsREADY_TO_FETCH paths for prompt local preservation. All GPU and retained-performance gates remain pending on the replacement. No production or historical frozen helper changed for this preparation.


### 019m. Queued replacement five-shape scorer with exact same-source owner

New sibling `candidates/w4a16_tuner_metric_experiment_five_shapes_recovery0908b/` changes only the protocol's declared token tuple to64/128/512/1/4096; worker85d3e18b, timers057fe6e0, staticgate45b7d2d2 and launcher0a5173d7 remain byte-identical to completed002. It preserves all16candidates,48F/R/Fvisits perrank/shape,raw10samples/scorer,1,920rankvisits/38,400samples, hot prestaged fullwrapper+reducer scope, MAX-of-local-medians aggregation, alternating scorerorder, exact same-candidate outputs and graph-reset-before-workspace-release. No publicCSV/CUPTI table substitution occurs. Completed002 and the earlier queuedfive sibling stay untouched.

Outer wrapper188d31304105ba35cd28566c6a687964e191f6bf703f177be508a68f8444a346 uses futurecompleted `logs/cu132-recovery0908b-c1-full13-001/stack-manifest.json` and requires allfour source-snapshot fields to equal currentC1/250553 exactly. No oldsix-path cache exception remains. Only newowner nativeTorch/FlashInfer caches are reused; DSL/driver/outputpaths are fresh. An explicit actualfresh EP8worker librarymap is required; no oldnode map/preflight/owner default is accepted. DefaultCPUplan reports owner/map pending; execution requires completion, exactsource/interpreter/compiler/helper gates. This stays queued after512 work and requires restoringC1 before scheduling.

New `analyze_recovery0908b.py` SHA5de528eea29ff15d63228d48bdf0406b626d2b8e0720a976ca95a3768a07d619 requires exacttokenorder, mandatorywrapper status/digests, completedfreshowner, zerochangedpaths andexplicitall8native maps. Original pervisit configuration/output/lifetime checks and scoring math remain AST-identical. SixteenCPUtests,Python3.12grammar, staticparser/graphreset checks andRuff pass; proofc9824ace4ad47207acff3ae32686585f035964ead9726d3b43985cda5d1faff9. Twenty-four staticuploadhelper/input checksums pass; actualowner/results/libraryfiles are futureinputs. No GPU/remote action or production/frozen helper edit in this preparation.


### 019n. Completed replacement C1 full13 baseline

The fresh fixed/control and auto16 sweep completed and passed independent source, raw-log, tactic, compiled-record, final-cache and library-map checks. All52 raw values/208 split selections/208 compiled records/104 actual winners are retained.

Auto reduces Mega latency against its same-source fixed CONTROL by6–10% at4/16/32/128/256/512/1024 and5.10% at4096. T1 regresses8.21% while split shifts+11.94%; T2 is effectively unchanged. T64 regresses2.04% while split shifts−6.15%, reinforcing its inclusion in the queued paired-scorer diagnostic. These are two-process observations, not confidence intervals.

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.075681 | 0.081633 | 0.084720 | 0.088336 | +8.21% | +11.94% | [1, 3] |
| 2 | 0.101712 | 0.118193 | 0.101584 | 0.118321 | +0.11% | -0.13% | [1, 3] |
| 4 | 0.137649 | 0.137361 | 0.145120 | 0.129025 | -6.07% | +5.43% | [1, 3] |
| 8 | 0.160449 | 0.161793 | 0.151409 | 0.157473 | -2.67% | -5.63% | [1, 3] |
| 16 | 0.179874 | 0.181265 | 0.182240 | 0.165105 | -8.92% | +1.32% | [2, 3] |
| 32 | 0.204978 | 0.210705 | 0.204113 | 0.188978 | -10.31% | -0.42% | [0, 2, 7] |
| 64 | 0.222801 | 0.235954 | 0.209105 | 0.240770 | +2.04% | -6.15% | [0, 3, 4, 7] |
| 128 | 0.234961 | 0.242594 | 0.235698 | 0.220081 | -9.28% | +0.31% | [0, 1, 5, 6] |
| 256 | 0.241905 | 0.250626 | 0.232258 | 0.227921 | -9.06% | -3.99% | [0, 1, 6, 7] |
| 512 | 0.241041 | 0.251922 | 0.236818 | 0.228514 | -9.29% | -1.75% | [1, 3, 5, 6, 7] |
| 1024 | 0.262401 | 0.268962 | 0.260738 | 0.251970 | -6.32% | -0.63% | [1, 3, 4, 5, 6, 7] |
| 2048 | 0.355106 | 0.336435 | 0.351186 | 0.335859 | -0.17% | -1.10% | [0, 1, 3, 5] |
| 4096 | 0.555268 | 0.522484 | 0.550483 | 0.495827 | -5.10% | -0.86% | [] |

Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.084720 | 0.088336 | 0.959x | M128/N64, C1, F8, reuse |
| 2 | 0.101584 | 0.118321 | 0.859x | M256/N64, C2, F8, reuse |
| 4 | 0.145120 | 0.129025 | 1.125x | M128/N64, C1, F8, reuse |
| 8 | 0.151409 | 0.157473 | 0.961x | M128/N64, C2, F4, epi |
| 16 | 0.182240 | 0.165105 | 1.104x | M128/N64, C2, F8, epi |
| 32 | 0.204113 | 0.188978 | 1.080x | M256/N64, C2, F8, epi |
| 64 | 0.209105 | 0.240770 | 0.868x | M256/N64, C2, F4, epi |
| 128 | 0.235698 | 0.220081 | 1.071x | M256/N64, C2, F4, epi |
| 256 | 0.232258 | 0.227921 | 1.019x | M128/N64, C2, F4, epi |
| 512 | 0.236818 | 0.228514 | 1.036x | M256/N64, C2, F8, epi |
| 1024 | 0.260738 | 0.251970 | 1.035x | M256/N64, C2, F8, epi |
| 2048 | 0.351186 | 0.335859 | 1.046x | M256/N128, C2, F8, reuse |
| 4096 | 0.550483 | 0.495827 | 1.110x | M256/N128, C2, F4, reuse |

Durable independent evidence: `logs/cu132-recovery0908b-c1-full13-001-analysis/` includes all52 raw CSVvalues, actual selections/compiledrecords and fresh libraryattestation. Owner `logs/cu132-recovery0908b-c1-full13-001/stack-manifest.json` is now complete withbothdeclaredarms. Source250553/C1/195946,1572files/337required. Rootreporteddriverexit0; source/helper guards and perarm recordchecks pass. Onlinehost scores remainseparate fromCUPTI. NoPRbody change or512 performanceclaim. Fresh512resource/publicvalidation is a separate subsequent run.

### 019o — fresh-node final512 public and lifecycle admission completed

Root's `zero-dest512-recovery0908b-public-sequence-driver-001.log` completed all10 captures with exit0. Each READY_TO_FETCH capture was preserved locally before later work, along with its plan/driver log; `logs/zero-dest512-recovery0908b-public-fetch-progress.json` records all10 result hashes. The earlier reclaimed-node incomplete public attempt remains incomplete and is not counted here.

- Exact source `e2d88e6a564638efe464d5a586a2b0284e66cb0b14bb4b77c7743593a09a29e3`, 1,573 source files/338 required paths, with complete identical before/after snapshots. Source IDs were independently recomputed from saved source/helper maps; no comparison to a later active checkout substitutes for these snapshots.
- Eight public captures cover M256/N128/C2, M128/N64/C1, M256/N64/C2, M128/N64/C2 at both EP1 and EP2. All120 rank-test calls and360 setup/call/teardown phases pass. All192 `(test, layer)` config/compiled pairs associate exactly; layer counters are intentionally local to each test. Actual function queries report REG128, 512 threads, two transform groups and65,536 initial CTA registers for every object. Local bytes are112 for36 N128 epilogue-return objects and0 for the remaining156; this is actual queried local storage, not a throughput diagnosis.
- EP1/EP2 lifecycle captures each exercise the complete distinct16-candidate catalog, including allfour C1 combinations:48 candidate/rank oracle checks in total. Every candidate receives the actual resource gate. EP2 rank1 has zero local tokens and records the empty-output contract while rank0 checks numerical output. One tuner call, rank-consistent winner, a distinct cached layer with the same winner/output, three exact stable graph replays and one changed-input graph/eager/oracle replay pass. These tensor comparisons are successful assertions from the frozen lifecycle helper; the independent JSON audit does not reconstruct unsaved tensor bytes.
- Public audit: `logs/zero-dest512-recovery0908b-public-all8-independent-audit-001.json`, SHA `a15ca1ab7a4434e56cf3915e53f5314e0118268fa3643423f00bea9c058d0923`. Lifecycle audit: `logs/zero-dest512-recovery0908b-lifecycle-independent-audit-001.json`, SHA `16068fd2e7452c70af0ddc58f9faa83f9b3c2b70df09db10bfc1bc653ae39e28`.

The separate primary full13 fixed→auto sweep `cu132-recovery0908b-zero-dest512-full13-001` is now running on the unchanged source. No performance or PR-promotion conclusion follows from these correctness/resource gates. The stale upstream host assertion expecting640 threads remains intentionally unchanged in this candidate overlay and must be updated with separate host validation if512 is retained.

Prospective preload and static-FC2 adapters were staged as18 new files, with18 exact shared-file matches skipped and all36 hashes verified; no existing remote path was overwritten. `logs/prospective512-preload-static-upload-001.json` preserves that operation. Their source deltas remain isolated and unapplied: preload source `d899a347…`, static-FC2 source `6765c231…`. Each sibling's `RUN_PLAN.md` supplies the later full13 command and matching source/preflight/resource/public/lifecycle prerequisites. They have no runtime or timing claim from this preparation.

### 019p — complete fresh512 fixed/auto sweep; ranking-sensitive regressions remain

The existing independent analyzer passes all52 raw latencies,208 actual split selections,208 actual compiled/resource records,104 actual rank auto winners,13 complete16-candidate host rankings, full source-before/after and exact completed C1 native-cache ownership. Sourcee2d88,1,573files/338required; no CUPTI fallback. All208 objects have actualREG128/512threads/two decode groups/pool65,536. Queried local-byte distribution (REG,local bytes): {(128, 112): 128, (128, 0): 80}.

The complete auto sweep is not a broad improvement over the fresh C1 auto sweep. T32/T128/T4096 are +6.83/+7.10/+6.94%, while T1 is−12.08% and T64−3.88%. Actual automatic choice changes at[1, 2, 4, 8, 32, 64, 128, 512, 1024, 2048, 4096]; onlyT16/T256 retain the same choice. No C1 single-CTA tactic wins this512 auto run, though allfour were included and passed the independent lifecycle gates.

The fixed CONTROL comparison provides a different boundary: T1+13.43%, T8−5.01%, T256−7.32%, T4096+0.81%. At4096 the automatic512 run selects the same epilogue-return CONTROL at.530227ms, versus its fixed process.526691ms. Fresh C1 auto chose reuse-dispatch at.495827ms; fresh C1 fixed epilogue-return was.522484ms. These observations motivate measuring exact returned configurations before assigning the approximately7% automatic regression to role sharing. They do not prove its cause.

The bounded next comparison shortlist is32/128/4096, each with the saved prior-C1 and current512 dictionary. New online winning margins over runner-up are only1.5/2.0/6.3us (printed host scores, not GPU intervals); the prior choices rank5/3/3. `../cu132-recovery0908b-c1-vs-zero-dest512-full13-001/online-shortlist-context.json` preserves those exact dictionaries/scores. Reuse the primary CUPTI timer and current source; keep each complete measured arm separate, and do not substitute row minima into this full13 table.

Independent reports: this folder's `comparison.json` SHAd6142dc952c70f6b77c9b8ca3884c6ae9dad7ae661dc89ae9928729a09228c1d; full cross-run comparison SHAbbc963f29a092eb6f06cc0596980e8e8db128dbe2133b678aa9398bcdd057a46. Original logs/provenance/tactics and both raw13 tables remain durable. This artifact does not promote source or modify the PR.

Complete primary raw fixed/auto rows and actual returned choices:

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.071072 | 0.092592 | 0.078176 | 0.077664 | -16.12% | +10.00% | [1, 3] |
| 2 | 0.100160 | 0.114081 | 0.116369 | 0.118432 | +3.81% | +16.18% | [1, 3] |
| 4 | 0.136753 | 0.136817 | 0.144065 | 0.134784 | -1.49% | +5.35% | [1, 3] |
| 8 | 0.162481 | 0.153680 | 0.151361 | 0.159585 | +3.84% | -6.84% | [1, 3] |
| 16 | 0.179600 | 0.177713 | 0.177281 | 0.159649 | -10.16% | -1.29% | [4] |
| 32 | 0.193681 | 0.206721 | 0.193873 | 0.201889 | -2.34% | +0.10% | [2, 4, 7] |
| 64 | 0.224113 | 0.238049 | 0.220497 | 0.231425 | -2.78% | -1.61% | [7] |
| 128 | 0.233298 | 0.241522 | 0.235025 | 0.235713 | -2.41% | +0.74% | [2, 6] |
| 256 | 0.243202 | 0.232289 | 0.242386 | 0.224977 | -3.15% | -0.34% | [5] |
| 512 | 0.240208 | 0.258113 | 0.238370 | 0.233921 | -9.37% | -0.77% | [1, 2, 4, 5] |
| 1024 | 0.262769 | 0.268786 | 0.261297 | 0.252225 | -6.16% | -0.56% | [0, 2, 7] |
| 2048 | 0.350914 | 0.338337 | 0.349379 | 0.341714 | +1.00% | -0.44% | [0, 2, 3, 6] |
| 4096 | 0.552515 | 0.526691 | 0.551171 | 0.530227 | +0.67% | -0.24% | [] |

Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.078176 | 0.077664 | 1.007x | M128/N64, C2, F8, epi |
| 2 | 0.116369 | 0.118432 | 0.983x | M256/N128, C2, F8, reuse |
| 4 | 0.144065 | 0.134784 | 1.069x | M256/N128, C2, F4, reuse |
| 8 | 0.151361 | 0.159585 | 0.948x | M256/N128, C2, F8, epi |
| 16 | 0.177281 | 0.159649 | 1.110x | M128/N64, C2, F8, epi |
| 32 | 0.193873 | 0.201889 | 0.960x | M128/N64, C2, F4, reuse |
| 64 | 0.220497 | 0.231425 | 0.953x | M128/N64, C2, F8, epi |
| 128 | 0.235025 | 0.235713 | 0.997x | M256/N64, C2, F4, reuse |
| 256 | 0.242386 | 0.224977 | 1.077x | M128/N64, C2, F4, epi |
| 512 | 0.238370 | 0.233921 | 1.019x | M256/N64, C2, F4, epi |
| 1024 | 0.261297 | 0.252225 | 1.036x | M256/N64, C2, F4, epi |
| 2048 | 0.349379 | 0.341714 | 1.022x | M256/N128, C2, F4, epi |
| 4096 | 0.551171 | 0.530227 | 1.040x | M256/N128, C2, F4, epi |

### 019q — final512 profiling complete; same-source tactic shortlist admitted

The complete EP8 software Nsight Systems evidence is [profiles/zero-dest512-recovery0908b-nsys-001/independent-audit-001.json](profiles/zero-dest512-recovery0908b-nsys-001/independent-audit-001.json): 16 actual source/resource worker records and 32 Mega actions, exactly two per device on all eight GPUs at each global32/4096 shape. Source e2d88, actual REG128/512threads/two decode groups. No GPU action is missing. Incomplete worker NVTX warnings remain preserved; 98.07%/97.13% aggregate fused-kernel shares are instrumentation context, not production latency. NSYS's zero local-memory field does not override the CUDA function query's112 bytes.

The actual EP1 H7168/I2048/E256/T4096 production resource probe passed before profiling. Initial NCU001 failed before application startup because a one-participant TCP communicator was requested. The isolated standalone002 adapter removes exactly the six communicator/lockstep flags while retaining application replay, original worker/lifecycle, source and actualREG128 admission. The [completed NCU findings](profiles/zero-dest512-recovery0908b-ncu-standalone-002/FINDINGS.md), [independent audit](profiles/zero-dest512-recovery0908b-ncu-standalone-002/independent-audit-001.json) and raw PC samples preserve two device0 actions, 152544/152909 total samples, exact conservation and15 embedded project source hashes matching e2d88. Source/SASS shows the existing21 FC2 router local accesses. Hot sampled barrier/control sites include raw-weight readiness, free decoded stages and FC1 accumulator readiness. Long-scoreboard samples on predicate-dependent branches do not establish HBM starvation; role denominators and EP1's256 local experts differ from EP8. Few source-tagged MMA free-accumulator samples limit any EP1 prediction for earlier FC2 release. Full EP8 measurements remain the retention gate.

The explicit next tactic comparison is [candidates/w4a16_512_winner_shortlist/README.md](candidates/w4a16_512_winner_shortlist/README.md): three unchanged original primary benchmark processes,32/128/4096, each with repeated T,T,T rows and exact A1(old C1 winner)/B(new512 winner)/A2(old C1 winner) dictionaries. Original100CUPTI/graph/coldL2 timing and row methods remain unchanged; only setup dictionary and recorder namespace are assigned. Same-shape split tuner cache persists and actual returned choices are recorded. Seven CPU checks pass locally and under actual remote Python3.12; native dry plan verifies all1573 source/338 required hashes and the completed fresh C1 native-cache owner. Eight new files were exclusively staged after all15 existing dependency hashes matched; no source/helper overwrite. Launch session78611 is recorded in logs/zero-dest512-winner-shortlist-launch-001.json. At this entry's creation it is running; no partial result is a performance claim or replacement for the complete full13 table.

### 019r — complete same-source512 tactic A/B/A;32/128 scorer misses,4096 new choice wins

All three primary benchmark processes completed with exit0 under source e2d88; the exact capture worker process scan was empty before GPU ownership returned to root. The original100CUPTI/3warmup/CUDAgraph/coldL2 row methods and timer stayed unchanged. One process per global32/128/4096 executed repeated T,T,T rows with explicit fixed old-choice/new-choice/old-choice setup dictionaries. Per-visit namespaces prevent collapsed records or cache-overridden Mega choices. The split tuner cache was deliberately left intact inside each process; all eight actual split choices are identical across visits at each shape. This is same-source tactic evidence, not a640-versus512 implementation A/B.

The independent replay of saved evidence validates all18 raw values,72 actual split selections,72 compiled rank/visit records, source-before/after1573/338, plan/helper digests and actual REG128/512threads/two-group admission. Complete JSON SHA `d6fadf3fb383a37851d0b3db009b8e3fab0a2aaaa62d650f416d10d9f7e0cf8b`; report [logs/zero-dest512-winner-shortlist-aba-001-analysis/comparison.md](logs/zero-dest512-winner-shortlist-aba-001-analysis/comparison.md). The initial native fp4-quantization/moe-utils rebuild was untimed and its generated build.ninja files matched their prelaunch cache inventory exactly; current nvcc argv/build files are preserved in logs/zero-dest512-winner-shortlist-build-cache-comparison-001.json. The build cause is not established. Subsequent processes reused the same verified native caches.

| Global tokens | Arm | Split ms | Mega ms | Actual fixed Mega choice |
| ---: | --- | ---: | ---: | --- |
| 32 | a1 | 0.200194 | 0.193265 | M256/N64,C2,F8,epi_warps |
| 32 | b | 0.201521 | 0.200241 | M128/N64,C2,F4,reuse_dispatch_warps |
| 32 | a2 | 0.201904 | 0.194114 | M256/N64,C2,F8,epi_warps |
| 128 | a1 | 0.222754 | 0.221409 | M256/N64,C2,F4,epi_warps |
| 128 | b | 0.234322 | 0.235409 | M256/N64,C2,F4,reuse_dispatch_warps |
| 128 | a2 | 0.234833 | 0.221617 | M256/N64,C2,F4,epi_warps |
| 4096 | a1 | 0.553027 | 0.542947 | M256/N128,C2,F4,reuse_dispatch_warps |
| 4096 | b | 0.543188 | 0.523764 | M256/N128,C2,F4,epi_warps |
| 4096 | a2 | 0.542404 | 0.541827 | M256/N128,C2,F4,reuse_dispatch_warps |

| Global tokens | B/A1 Mega change | B/A2 Mega change | A2/A1 Mega change | A2/A1 split change | Changed split ranks A1→B / A1→A2 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | +3.61% | +3.16% | +0.44% | +0.85% | 0 / 0 |
| 128 | +6.32% | +6.22% | +0.09% | +5.42% | 0 / 0 |
| 4096 | -3.53% | -3.33% | -0.21% | -1.92% | 0 / 0 |

All18 raw values,72 actual split selections and72 compiled rank/visit/resource records were independently reconstructed; complete source before/after, exact requested/resolved dictionaries, interpreter/compiler/decoder and actual REG128/512threads/two-group gates pass. Preserve these observations separately from complete full13 tables. No row minima, profiler timings or failed-arm substitutes are used.

At32 and128, the prior C1 automatic choice is consistently faster on the new512 implementation than the fresh512 automatic choice. The narrow online host-score margins previously recorded did not predict these primary CUPTI results; the prepared five-shape host-versus-GPU scorer diagnostic is warranted. At4096, the new epilogue-return choice beats the prior reuse-dispatch choice in both brackets. Therefore the large-token difference from historical640-source auto cannot be explained simply by selecting the old dictionary on512. It remains a source/performance boundary requiring further work; profiler/control-flow hypotheses are separate from this measured result.

A1/A2 Mega movement is under0.45% at every sampled shape, while same-tactic split movement reaches5.42% at128 and−1.92% at4096. Split variation is disclosed, not used as an error bar. The complete full13 automatic tables are unchanged; no result here is substituted into them and no kernel/source promotion follows. Source e2d88 remains frozen for the upcoming512 five-shape diagnostic; the strict combined static-FC2/post-reorder-release candidate is independently prepared for later validation.

### 019s — complete fresh C1 cross-stack owner and catalog16 timing evidence

The completed fresh C1 CUDA13.0 and13.2 runs both validate exact source250553/195946, identical original benchmark helpers and18 printed provenance hashes per arm. Each has52 raw values,208 actual split selections,208 compiled records,104 automatic winner confirmations and13 complete16-choice rankings. The [complete comparison](logs/cross-stack-recovery0908b-c1-full13-001-analysis/comparison.md), [all104 raw values](logs/cross-stack-recovery0908b-c1-full13-001-analysis/raw-latencies.csv) and [source/runtime/tactic records](logs/cross-stack-recovery0908b-c1-full13-001-analysis/comparison.json) remain separate from512 results. JSON SHA875dca738d6aad1555d321d0e51147c167f2daaf3be4fbb4b4df6a22c33c59ee. The earlier fixed-only comparison remains preserved at logs/cross-stack-recovery0908b-c1-fixed-control-001-analysis.

Whole-auto CUDA13.0 is slower in all13 rows: T1+27.12%,T32+25.72%,T512+19.02%,T4096+10.29%. Actual automatic choices differ in9/13rows; no physical-cluster1 tactic wins on13.0. CUDA13.0 auto versus its own fixed Mega regresses at1(+6.49%),8(+.94%),32(+1.89%),4096(+.91%) and improves elsewhere. Fixed configurations/stages/workspaces match across stacks, with4096fixed gap+3.72%;81/104fixed split choices and79/104auto split choices differ. These observed comparisons are not statistical confidence bounds or compiler-only causal evidence.

Both use DSL4.7.1, but the13.0 image25.11 preserves Torch2.10/nativecu12compiler12.9/fallbackdecode/NVSHMEM3.4.5/NCCL2.28.8 onhu-pdx-119;13.2 image26.05 preserves Torch2.12/nativecu13compiler13.3/directdecode/NVSHMEM3.6.5/NCCL2.30.4 onhu-pdx-88. Fresh13.0 control and auto live-library captures are verified and equal;13.2's fresh live map comes from auto only, not its fixed process. The separate132 preflight pointer audit established Python CUPTI wheel bindings; a two-library process map alone would not establish them. Input shapes match; this audit does not newly remeasure cross-stack input bytes. Earlier source-attested byte evidence remains historical context.

Integration's logs/cu130-recovery0908b-c1-owner-admission-002.json confirms complete native owner results, exact source/helpers/runtime, cache existence and no GPU/compiler/worker at15:01:48UTC. Initial001 postprocessing compared tuples to JSON lists; its log/helper are preserved, and002 only normalized serialization. Allpublic10 cases and all16-tactic cache/graph lifecycles had passed onEP1/EP2 before timing. That finished C1 owner now anchors the separately scheduled exact three-path512 fallback experiment; no combined-FC2 source or512 performance result is credited here. No PR table was changed by this CPU audit.

### 019t. Primary/scorer boundary audit and completed T64/T128 partial rankings

The read-only boundary review is saved at `candidates/w4a16_tuner_metric_analysis/timing_boundary_001/REVIEW.md` with exact source hashes. The primary CUPTI closure includes routing, public output ownership/staging, Mega and the external reducer; the paired scorer uses staged fixed inputs and Mega plus reducer. Cache policy, replay pacing and distributed aggregation also differ. Changing graph `cold_l2_cache` alone is insufficient with a zero-argument closure: that utility disables argument rotation. A prospective private scorer hook can retain the existing candidate/cache lifecycle, but must state its staged boundary and clean up each graph before candidate workspace replacement. No timing/helper/production changes were made by this audit.

While the five-shape run remained active, completed T64 and T128 folders were fetched only after all eight ranks recorded 48 successful visits for each shape. Independent partial reconstruction is in `logs/paired-tuner-metric-512-five-shapes-recovery0908b-001-partial64-128-analysis/` (JSON SHA `c8d7f87cd341b1bdee6adbc1735dc898c516813122ecda711f0897e860f867ad`). It validates 768 rank-visits and 15,360 raw samples, exact MAX of local medians, recorded winners, actual REG128/512-thread/two-group admission, native mappings, unchanged per-shape input hashes and successful emitted output/graph gates. It does not claim the whole run or post-run source check completed.

Across all six passes, the graph top two are M256/N64/C2 with epilogue-warps return, flag4/8. The flag margins are too small to establish a consistent preference; T64 reverse pass rounds both to187.936us but has a raw difference of only0.00000745us, a near-tie. Same-geometry reuse return is3.51–4.81% slower at64 and4.30–5.30% at128 under this hot staged metric. Graph pairwise ordering changes only4–9 of119–120 comparable pairs across passes, whereas eager/graph disagreement is15–38 pairs. Eager winners change64:6/8/0 and128:10/4/6. Full13 primary tables and shortlist measurements remain separate; no row substitutions or PR edits.


### 019u. Complete five-shape512 scorer diagnostic and static FC2 trial launch

`paired-tuner-metric-512-five-shapes-recovery0908b-001` completed with driver exit0 and unchanged before/after source, helpers and inputs. Full independent analyzer passes all1,573 source files/338 required paths,40 rank/shape groups,1,920 visits and38,400 raw samples; exact three-path C1 native-owner admission, actual REG128/512threads/twoWGs, all loaded native maps, per-shape input bytes/addresses, emitted exact-output gates and graph reset checks pass. Complete raw scores, all15 pass winners and ranking disagreements are preserved in `logs/paired-tuner-metric-512-five-shapes-recovery0908b-001/analysis-independent-512-001/`; analysis SHA2e129052703317550b033990522ad6790af3b657ea3cf1b4a8749169c01e8ba5. The outer native-cache plan records TORCH_EXTENSIONS_DIR; the original child environment filter omits it, as the analyzer explicitly discloses.

Graph winners by pass are64:[4,6,4],128:[4,6,4],512:[4,4,4],1:[12,8,6],4096:[0,0,0] in the unchanged16-candidate catalog. Candidates4/6 are M256/N64/C2 epilogue return F4/F8; candidate0 is M256/N128/C2/F4 epilogue return. The one-token graph margins are only.032-.080us with varying geometry, so no stable choice is established there. At4096 the graph winning margins are7.328/7.616/8.624us and both scorers select candidate0 in all passes. At512 graph selects candidate4 in all passes while eager selects6. This supports a general private graph-event scorer trial; it does not promote a timing policy or replace any cold-L2 full13 row. Hot staged scope, queued replay pacing and MAX-of-rank-medians remain distinct from the primary full-forward CUPTI metric. The prepared graph-owner candidate is source-only and remains unapplied.

After complete diagnostic fetch/audit and an empty worker/compiler scan, parent installed exactly the static FC2 unroll plus safe last-scratch-read release: epilogue33b596→604935, sourcee2d88→28a58c2d9406a246a9e0319935f24340b17a00abe8723fde9b62ddf1a6f84fe0. Local transition evidence is `logs/cu132-recovery0908b-static-fc2-release-local-install-001.json`; remote sync changed only that epilogue. Fresh preflight16 verifies system/TorchCUDA13.2, DSL4.7.1/native13.3 actualbb367, directdecode and exact interpreter/torchrun. All ten strict validation dry plans passed before the serial numerical driver launched at15:26UTC (root session32754), with fresh actual-function resource checks before each first Mega launch. Numerical results are pending at this entry; no full13 gain or PR promotion is claimed. Performance agent may run the four sealed FC1 codegen captures during this numerical-only window, with empty CUDA visibility and no GPU invocation; all native compilers must exit before performance timing. CUDA13.0 retains exacte2d88 for its independent validation/full13 series.

### 019v. FC1 final scratch-read release sealed compile gate

The prospective cohort `profiles/cu132-recovery0908b-fc1-safe-release-compileonly-001` was staged new-only (22 frozen inputs plus2 evidence files), then compiled only after root installed exact safe-FC2 source28a and opened the CPU compilation window. All4 declared captures completed sequentially and were promptly fetched. Source/native/artifact before/after gates passed:1573 inventoried/338 required/3684 all production files,22 inputs, DSL4.7.1 native13.3 `bb367e30…bba`. No compiled callable, numerical test, GPU launch or benchmark was run by this cohort. Window closure and exact driver hashes are in `logs/cu132-recovery0908b-fc1-safe-release-completion-001.json`.

The N128 control/candidate are5776/6000 SASS,92416/96000 text bytes (+224/+3.88%). N64 is5448 instructions/87168 bytes in both. All4 retainREG128/STACK0/no local operations/MMA16/DEC80–INC176. Transform opcode counts are unchanged. N128 duplicates the previously shared FC1 body into two static specializations; N64 removes the preceding-body case entirely. Source-correlated PTX/SASS confirms final scratch-read→wait→arrival→register permutation/BF16 pack/store, with the early arm bypassing the normal release and no subsequent TMEM read. N128≤64 and zero-token paths retain normal release. FC2 source is AST-identical, but global recompilation shifts some source-tagged FC2 private instructions, so whole-FC2 machine-code equality is not claimed.

Detailed resources, CFG evidence and retained limitations are under the cohort's `analysis/`. Code quality allows a later public/lifecycle numerical gate; the N128 static-size cost and end-to-end effect require measurement. No promotion or PR table edit followed from this compile-only result.


### 019w. Static FC2 numerical gate complete; graph scorer staged; input-role overlap proposal

Exact source28a completed all eight public geometry/EP suites and both all16-tactic lifecycles before its full13 launch. Independent reconstructions in `logs/cu132-recovery0908b-static-fc2-release-public-independent-001/` and `logs/cu132-recovery0908b-static-fc2-release-lifecycle-independent-001/` validate120 rank-test calls,192 public and48 lifecycle compiled records, all numerical/cache/graph assertions and unchanged source. Every observed object reports actualREG128,512threads,two decode groups,65,536 initial registers and0 local bytes. The control-to-candidate change is static FC2 iteration plus release after the last accumulator scratch read; this resource observation alone is not a speedup claim.

Root launched `cu132-recovery0908b-static-fc2-release-full13-001` at15:49:50UTC using the completed C1 native owner and fresh DSL/driver/knob caches. The original fixedCONTROL→auto16,100CUPTI,13-shape benchmark is unchanged. Its initial split setup rebuilt native moe_utils, with actual nvcc/ptxas observed before timing. The rebuild cause is unestablished; cache reuse does not imply no compilation. Experimental CPU compilers had exited before launch. At16:05UTC fixed split had reached2048; complete results remain pending, and no table or PR code has been promoted.

The graph-scoring production candidate and strict five-path sibling are frozen at `candidates/w4a16_tuner_graph_scoring/` and `candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512_c1_static_fc2_release_graph_scoring/`. Parent reviewed the private full-wrapper graph ownership, collective capture-ready agreement, existing event sampler and cleanup before workspace replacement. Forty-six adapter and10 private scorer CPU tests pass. Source28a→0d795 changes only autotune.py; public APIs,16 dict tactics, other-precision timing and cache lookup remain unchanged. New cache score provenance is explicit. Runtime staging created18 files and verified18 preexisting exact files without overwriting; all36 hashes are recorded in `logs/cu132-recovery0908b-graph-scoring-runtime-upload-001.json`. The scorer remains unapplied. New runtime gates will exercise EP1/2 lifecycle plus actual peer capture-error/no-replay cleanup before a fresh full13; unchanged28a kernel public evidence is inherited only with the exact four kernel hashes.

The source audit `candidates/w4a16_input_dispatch_epilogue_audit/README.md` establishes a further overlap opportunity: input counts reach the scheduler before payload pulls finish, yet current decodeWG0 waits for those pulls. Moving input onto the epilogueWG can expose earlier two-WG weight decode within existing metadata/accumulator ring limits. This is a source-proven possible overlap, not a measured gain. All current512-thread pipeline counts remain, and input must run after TMEM rendezvous at128 registers before epilogue INC176. Reused-dispatch output needs an explicit one-time scratch handoff even for compute-idle CTAs; producer-tail/sentinel alone is insufficient. The selected bounded prototype preserves the exact input mbarrier phase in each fully drained existing pull-buffer head, then uses private named barrier11/256 participants before output reads it. That handoff is constexpr absent for epilogue return. It needs no new public knob, global read, shared allocation or phase scalar live through decode/epilogue. The separate candidate is being prepared for generated-code review; installed source and active benchmark remain frozen.


### 019x. Complete static FC2 fixed sweep and empty-drain runtime adapter

The completed CUDA 13.2 source28a fixed arm passed independent reconstruction through the original helpers:26 raw values,104 split tactics and104 actual compiled observations. Source-before/after, all1573/338 inventory entries, current imported source/native, completed fresh C1 cache owner, original CUPTI command and actual rank resources match. Separate target auto output is excluded. All104 source28a observations retain REG128/512 threads/two transform groups/pool65536 and report zero local bytes; all104 e2d fixed observations had112 local bytes. Earlier C1 compiled observations did not query actual resources. This does not attribute timing changes to local memory.

The report [complete fixed comparison](logs/cu132-recovery0908b-static-fc2-release-fixed-independent-001/README.md) preserves all78 raw values and312 split/compiled observations across C1,e2d and28a. JSON SHA `492fd8c7e869ceb9f3ba848c21d62356de4fd04742bdcf669239917ea67ae940`. Each original arm was independently revalidated. Fixed actual configs and split input shapes match at every rank; split retunes differ17/104 against e2d and33/104 against C1. Recorded image/node/native versions match; source28a differs from e2d only in the epilogue, combining static FC2 specialization and post-reorder release. Sequential unbracketed sweeps cannot isolate those two source changes from each other or temporal effects.

| Tokens | C1 split | C1 Mega | Base512 split | Base512 Mega | Static512 split | Static512 Mega | Mega vs base512 | Split vs base512 | Changed split ranks | Mega vs C1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 0.075681 | 0.081633 | 0.071072 | 0.092592 | 0.084256 | 0.091920 | -0.73% | +18.55% | [] | +12.60% |
| 2 | 0.101712 | 0.118193 | 0.100160 | 0.114081 | 0.116752 | 0.117217 | +2.75% | +16.57% | [] | -0.83% |
| 4 | 0.137649 | 0.137361 | 0.136753 | 0.136817 | 0.127202 | 0.130529 | -4.60% | -6.98% | [] | -4.97% |
| 8 | 0.160449 | 0.161793 | 0.162481 | 0.153680 | 0.147921 | 0.151761 | -1.25% | -8.96% | [] | -6.20% |
| 16 | 0.179874 | 0.181265 | 0.179600 | 0.177713 | 0.179538 | 0.174418 | -1.85% | -0.03% | [4] | -3.78% |
| 32 | 0.204978 | 0.210705 | 0.193681 | 0.206721 | 0.203538 | 0.199553 | -3.47% | +5.09% | [0, 6] | -5.29% |
| 64 | 0.222801 | 0.235954 | 0.224113 | 0.238049 | 0.222674 | 0.230210 | -3.29% | -0.64% | [0, 6] | -2.43% |
| 128 | 0.234961 | 0.242594 | 0.233298 | 0.241522 | 0.233505 | 0.240289 | -0.51% | +0.09% | [2, 6] | -0.95% |
| 256 | 0.241905 | 0.250626 | 0.243202 | 0.232289 | 0.243922 | 0.238305 | +2.59% | +0.30% | [5] | -4.92% |
| 512 | 0.241041 | 0.251922 | 0.240208 | 0.258113 | 0.239042 | 0.246434 | -4.52% | -0.49% | [3, 4, 5, 6] | -2.18% |
| 1024 | 0.262401 | 0.268962 | 0.262769 | 0.268786 | 0.261122 | 0.267985 | -0.30% | -0.63% | [0, 6] | -0.36% |
| 2048 | 0.355106 | 0.336435 | 0.350914 | 0.338337 | 0.351475 | 0.342035 | +1.09% | +0.16% | [0, 2, 5] | +1.66% |
| 4096 | 0.555268 | 0.522484 | 0.552515 | 0.526691 | 0.552262 | 0.531972 | +1.00% | -0.05% | [] | +1.82% |

Against e2d,28a is faster at9/13 points and slower at4/13: T32/64/512 change−3.47%/−3.29%/−4.52%; T256/4096 change+2.59%/+1.00%. The paired split changes+0.30%/−0.05% at256/4096, while tiny-token split movement ranges−8.96% to+18.55%. These are contextual controls, not statistical error bounds or normalization factors. Auto and any retention decision remain separate.

The isolated [empty-drain adapter](candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512_c1_static_fc2_release_empty_bulk_drain/README.md) is frozen and unstaged. Exact e9a725 source admission differs from28a only at epilogue b1d82a1d. All37 independent CPU tests pass;28 upload hashes and23 handoff entries match; five core resource/numerical/observer helpers are byte-identical and remaining runtime changes are exact declared literals. Source28a rejects this adapter. Independent review SHA `8040e4eba05f4b7ebfe7a44a56ef5a31eaa644f6865904c2fd2ecd44b3e6a030`. It still requires new installed-source preflight and actual per-object resource/numerical/lifecycle validation. Prior private N128/N64 codegen removed eight instructions each with zero locals and preserved waits/publication, but establishes no runtime or latency result for e9a725. No source or PR edit follows from this entry.

### 019y. Graph scorer lifecycle passed; full13 and two overlap candidates queued

On 2026-09-08, applied only the previously reviewed `autotune.py` GPU-event graph scorer to static-FC2 source28a. Current observed source is `0d795ec767c1a588e4982d6972ef12dcf5b10683f55141310adab96efb6e1e86`; kernel, communication, epilogue, shared W4A16 transform/decoder, public tests and all original measurement helpers remain identical to28a. Exact one-file transition is recorded in `logs/cu132-recovery0908b-static-fc2-release-graph-scoring-local-install-001.json`.

All three new runtime jobs passed: auto16 lifecycle EP1 and EP2, then actual private graph-sampler ownership / peer-capture-error / same-workspace recovery EP2. The independent audit (`logs/cu132-recovery0908b-static-fc2-release-graph-scoring-numerics-independent-001/audit.json`, SHA `9901fd441a5866341e4285f7438e4fcdcf409b236f683772f27f7b8704a30079`) reexecuted source/native/resource validators: 48 catalog objects, 32 nonempty candidate oracles plus16 empty contracts, one tuning call per rank, agreed cached winners, nine stable and three changed-input serving replays. Every object used actual REG128,512threads,two transform groups,65,536registers,local0. The separate sampler observed six completed graph resets, zero replay/timer entries after the injected peer capture failure, and successful numerical recovery. This is safe host capture-error evidence, not device-fault recovery. The exact28a original public suite is inherited only through the verified one-file host-only delta:120public cases/192compiled objects,109 saved evidence hashes rechecked.

Started `cu132-recovery0908b-static-fc2-release-graph-scoring-full13-001`: original fixed CONTROL then independent auto16, all powers of two1–4096,EP8/H7168/I2048/E256/top8,100CUPTI/three warmups/coldL2/single-forward graph, split no-fused-finalize, median per-iteration rank-MAX full GPU span. Fresh DSL/driver/knob caches; completed C1 native owner reused. Primary PATH keeps `/usr/bin` before `/usr/local/bin`, preserving the prior primary's Ninja selection. Read-only evidence shows the installed Ninja1.11.1 and1.13.0 builds disagree about freshness for the same recipe; this does not by itself establish historical rebuild causality. No experimental compiler is allowed alongside primary timing. No current-best claim or PR update is made from the pending run.

Prepared/staged two separate overlap directions without production installation. Input dispatch on epilogue warps passed all eight geometry/return matched native pairs with REG128/512/STACK0/local0, unchanged16MMA and DEC80/INC176; native per-warp phase handoff and compile-time absence in epilogue-return are verified. The new runtime adapter targets `21ee720f…` on the graph scorer, passed53CPU tests and independent checks, and stages32runtime files (18created/19existing-exact with five extras). It still requires fresh resource probe, eight public jobs, two lifecycle jobs and sampler before full13. Its input code has no numerical/performance result yet.

The first-FC2-32-value predecode candidate remains an isolated private constexpr specialization of the existing shared transform, with default-False AST recovery. A four-capture current-owner cohort is staged (`candidates/w4a16_fc2_first_fragment_predecode_compile_0d795`, handoff SHA `914b757a47e81e9d61c808b9a2e6ea33a17177e6d9319edc9e492804ad141851`); no native compilation has run. Its decisive gate requires all32 fully scaled BF16 values before the decoded-stage blocking wait, preserved through slow paths, with every TMEM store after acquisition, no duplicate decode/new local spills/MMA cloning. Packed-load motion alone will not qualify. Compile only after the primary window closes, then refine any codegen-quality failure before judging the direction's performance.

### 019z. Complete graph scorer full13: useful general trial baseline, no unqualified overall best

Completed `cu132-recovery0908b-static-fc2-release-graph-scoring-full13-001` with exit0; source `0d795ec767c1a588e4982d6972ef12dcf5b10683f55141310adab96efb6e1e86` and all original measurement helpers remained unchanged. Independent four-source analysis: `logs/cu132-graph-scoring-four-source-independent-001/` (`comparison.json` SHA `251dbe1d6217a11370ba092f5fa72679f9a188a63ac90d8073f3f370b1d8deb3`).

All four strict analyzers pass in separate CPU processes:208 raw values,832 split records,832 compiled records,416 returned rank choices and52 full16-candidate rankings. The new graph sweep contributes52/208/208/104/13. Its208 selected objects all attest REG128,512threads,two decode groups,pool65536,local0. Ten cache capacities retain the correct last winner, while all13 actual row choices are preserved.

The graph source differs from28a only at autotune.py. All104 fixed-control config/compiled/gate records match exactly; separate fixed-process Mega movement spans−4.01%..+4.80%, and paired split movement−13.17%..+13.51%. This is context, not a scorer-induced kernel change or a correction factor for auto.

Graph auto is lower at11/13 points versus its fixed arm. T1 is4.35% slower andT4096 is0.62% slower. T2048 andT4096 use exactly the same observed config/compiled/gate as fixed on every rank; their−1.75%/+0.62% changes cannot be credited to a changed tactic.

Versus complete host-scored28a auto, graph auto improves8/13 rows and changes10 choices. T8/T16/T64 improve7.40%/6.08%/7.84%, useful selection evidence. It regressesT1 by14.85% andT2 by11.48%; T256 is1.73% slower with the same selected configuration, andT4096 is0.71% slower with the same selected configuration. Small differences and repeated same configurations need context, not a new-best label.

Versus base512 e2d auto, graph auto improves9/13, butT1 is22.97% slower. Versus freshC1 auto it improves6/13, whileT1 is8.11% slower andT4096 is7.03% slower. At4096, C1 selected the same M256/N128/C2/F4 geometry with reused-dispatch return; graph selects epilogue return on the later512-thread/static-FC2 implementation. This is not an isolated scorer or return-mode comparison across those sources.

The complete graph table beats its own paired split at12/13 shapes, including all seven shapes above32. T64 is only1.0102x andT512 only1.0060x; split independently retunes and those narrow margins do not establish repeatable nonregression. T1 remains below split at0.8449x.

All13 graph selections use epi_warps. Most printed first/second score gaps are below1%; T1 andT8 are equal at the displayed0.1us precision, which does not prove exact ties. T4096 has a1.82% printed graph-score gap. Host wall-clock scores and hot graph GPU-event scores remain distinct from unchanged cold-L2 CUPTI final latency; no score ratio is interpreted as a kernel speedup.

Continue graph scoring as a meaningful general trial baseline, as directed by the parent. These observations do not justify an unqualified new overall-best claim or replacing the PR table. Preserve the full table; no minimum across rows/sources or workload weighting is invented. New CUDA13.0 recovery targets0d, while CUDA13.2 first32 predecode CPU capture and the separate input trial continue independently.

| T | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Auto split/Mega | Auto vs fixed | Actual auto choice |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.085153 | 0.091520 | 0.080688 | 0.095504 | 0.8449x | +4.35% | M128/N64, C1, F8, epi |
| 2 | 0.101377 | 0.115585 | 0.116752 | 0.114497 | 1.0197x | -0.94% | M128/N64, C1, F8, epi |
| 4 | 0.144385 | 0.136800 | 0.138161 | 0.126609 | 1.0912x | -7.45% | M128/N64, C1, F4, epi |
| 8 | 0.163041 | 0.152129 | 0.160992 | 0.147153 | 1.0940x | -3.27% | M256/N64, C2, F8, epi |
| 16 | 0.166977 | 0.178113 | 0.177841 | 0.156673 | 1.1351x | -12.04% | M256/N64, C2, F4, epi |
| 32 | 0.205441 | 0.203266 | 0.200866 | 0.193250 | 1.0394x | -4.93% | M256/N64, C2, F8, epi |
| 64 | 0.209682 | 0.232882 | 0.220977 | 0.218738 | 1.0102x | -6.07% | M256/N64, C2, F8, epi |
| 128 | 0.239042 | 0.237410 | 0.231955 | 0.225282 | 1.0296x | -5.11% | M256/N64, C2, F4, epi |
| 256 | 0.245042 | 0.246849 | 0.244785 | 0.229217 | 1.0679x | -7.14% | M256/N64, C2, F8, epi |
| 512 | 0.239554 | 0.250626 | 0.237201 | 0.235794 | 1.0060x | -5.92% | M256/N64, C2, F4, epi |
| 1024 | 0.260274 | 0.257250 | 0.259714 | 0.250225 | 1.0379x | -2.73% | M256/N64, C2, F4, epi |
| 2048 | 0.351874 | 0.344578 | 0.348210 | 0.338531 | 1.0286x | -1.75% | M256/N128, C2, F4, epi |
| 4096 | 0.557699 | 0.527445 | 0.549221 | 0.530692 | 1.0349x | +0.62% | M256/N128, C2, F4, epi |

The full comparison and raw208 rows are retained in `FINDINGS.md`, `comparison.md`, `comparison.json` and `raw-latencies.csv`; online host scores and GPU-event scores keep their original metadata. No PR write was performed.

### 020. First32 predecode native overlap passes; input-dispatch runtime trial installed

The four current-owner sealed captures completed on CUDA13.2/native13.3 while GPUs were hidden, after the graph full13 timing window ended. Frozen cohort `candidates/w4a16_fc2_first_fragment_predecode_compile_0d795` kept source0d and all3684 production files plus29 cohort inputs unchanged; every arm used the original compile helper `268ac3a…` and native `bb367…`, one actual cute.compile and zero device allocations/collectives/Mega invocations. Final native review: `candidates/w4a16_fc2_first_fragment_predecode_native_review_0d795/README.md`; handoff SHA `fe60fab66680f517b0002690565eaa165cf6efcb9c3c7630fa677b243b395ef8`,111 hashed evidence files. Fresh post-window proof at17:33:13UTC, `logs/cu132-fc2-first32-predecode-cohort-post-idle-001.json`, SHA `c7142b7dc3665c4f0fc3bb679a2d27a24f603a0b0d36de87e70ecc1eadfe8bca`.

| Geometry, return | Control SASS instructions | Candidate SASS instructions | Registers / threads | Stack / local | MMA / broadcasts |
| --- | ---: | ---: | --- | --- | --- |
| M256/N128/C2, epi | 5776 | 5784 |128 /512 |0 /0 |16 /4 |
| M256/N64/C2, epi | 5448 | 5456 |128 /512 |0 /0 |16 /4 |

Both candidates perform all16 FP4 pair conversions, two E4M3 conversions and16 BF16 pair scaling operations before the decoded-stage acquire branch. Every scaled pair survives the exact blocking slow path and reaches the first two STTM.x8 stores in original order. N128: final scale0xc710, acquire branch0xc720/TRYWAIT0xc750, first store0xc970. N64: final scale0xc630, acquire branch0xc640/TRYWAIT0xc670, first stores0xc890/0xcaa0. These are these captures' own PCs, not carried-forward profiler PCs. The wait uses R12/R13 after their scale duties; the live payload occupies other registers. Root independently checked the N128 slow path and payload/store handoff.

Both phases retain their per-K four packed LDS.128, two SF LDS,64 FP4 pair conversions,eight SF conversions,64 pair scale operations and eight STTM.x8. Normalized branch topology is unchanged (634 entries N128,586 N64), as are FC1 opcode histograms; register assignments differ, so FC1 is not claimed byte-identical. No LDL/STL or extra MMA exists. The +8 instructions are payload moves for the second store packet with minor arithmetic redistribution, not duplicate decode or a new runtime branch. Keep this small cost visible in the later benchmark; it does not negate the demonstrated independent work. Runtime/numerical/performance and actual fallback codegen remain untested for this candidate. Its original28a→707da declaration is unchanged; on graph0d its prospective runtime source isf65112e5… .

After the entire CPU window closed, installed the separate input-dispatch-on-epilogue proposal on local and132 source: **21ee720fa10f71e1e7950320d13326b113f6134bff734f69e716758a7a355eea**. Only kernel.py `0b038129…` and communication.py `a2fb6365…` changed from0d. No first32/shared-transform, FC1-release, empty-drain, test or documentation patch was applied. Install audit: `logs/cu132-input-dispatch-graph-local-install-001.json`; two-file sync completed. Fresh real preflight and all12 strict dry plans pass, including exact source/native/16-catalog admission. Started original resource→eight public geometry/EP jobs→two all16 lifecycle jobs→private sampler sequence, prefix `cu132-recovery0908b-input-dispatch-graph-scoring`, driver log `logs/cu132-recovery0908b-input-dispatch-graph-scoring-validation-sequence-001.log`. It stops on first failure. No input-candidate numerical/performance success is inferred from preflight or native codegen.

Resumed the separate CUDA13.0 recovery against frozen0d, independently of the ongoing132 trial. Reverified live image selection `nvcr.io/nvidia/pytorch:25.11-py3`; ziangli pending resources were cancelled/deleted after quota rejection, and a single `c2/infra` request `fi-w4a16-mega-cu130-0908c` has quota reserved but awaits physical placement. No duplicate hell request, source upload or native/GPU validation has occurred. The recovery bundle freezes its own exact0d five-file overlay, so it does not copy current21ee source; pinned image Torch/native12.9 gateFalse setup and fresh-cache admission remain explicit. See `candidates/cuda130_recovery_0908c/checkpoint.json`. This queue wait does not pause CUDA13.2 optimization.


### 021 — complete input-dispatch sweep and CUDA13.2-only direction

User explicitly discontinued CUDA13.0 due to preemption and compilation cost, and clarified that using most registers does not require mirroring split W4A16's four-WG layout. The completed130replacement setup/preflight is preserved as setup-only; no new GPU numerical/performance result followed. Integration confirmed no owned workers, fetched artifacts and deleted only fi-w4a16-mega-cu130-0908c. Release evidence: logs/cu130-recovery0908c-user-release-001.log. No further130work is scheduled. Two decode WGs remain the existing requirement; no one-versus-two comparison or runtime register/WG knobs are added.

Input source21ee completed all12 numerical jobs, independently audited at logs/cu132-recovery0908b-input-dispatch-graph-scoring-independent-001/audit.json (SHA30d0ead42555cfdceeed68922508c6f3888539a6d8c087339a7b949060ba019f):120 public rank-tests/192 objects,48 all-catalog candidates,9 stable+3 changed serving-graph replays, graph-sampler peer capture-error/reset/recovery. All250 original prelaunch records are REG128/512/twoWG/pool65536;244 local0 and6 local8. The six are two small M256N64C2 epi fixtures (H192/I320/T257/F8 and H288/I448/T257/F4, E4/top2), each EP1rank0 and bothEP2ranks. Exact matching28a records had local0. All recorded stage/workspace/config fields match; recovered driver caches contain no Mega binary, so no native role attribution follows from allocation metadata. A fresh sealed exact-fixture cohort is separately recorded under candidates/w4a16_input_dispatch_small_local_compile_21ee.

Primary cu132-recovery0908b-input-dispatch-graph-scoring-full13-001 completed both fixed and auto arms, root process41229 exit0 at18:30:40UTC. All eight result/log/provenance/tactic paths were fetched. Fresh18:31:28UTC process/GPU queries were empty before the next CPU-only capture window. Exact source21ee/nativebb367 and the existing completed freshC1 native-cache owner are preserved; primary PATH selects system Ninja. The original EP8 H7168/I2048/E256/top8,100CUPTI,three-warmup,cold-L2 single-forward-graph,median per-iteration rank-MAX GPU activity span remains unchanged, with independent same-source split retuning and no-fused-finalize.

| T | Fixed split | Fixed Mega | Auto split | Auto Mega | Auto/fixed change | Split/auto | Actual auto choice | Local bytes by rank count (auto) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 0.086528 | 0.085984 | 0.096737 | 0.094225 | +9.58% | 1.0267x | M128/N64,C1,F8,epi_warps | {'0': 8} |
| 2 | 0.116336 | 0.121680 | 0.117169 | 0.111344 | -8.49% | 1.0523x | M128/N64,C1,F4,epi_warps | {'0': 8} |
| 4 | 0.127409 | 0.130609 | 0.142337 | 0.133202 | +1.99% | 1.0686x | M256/N128,C2,F4,epi_warps | {'0': 8} |
| 8 | 0.162673 | 0.158337 | 0.160370 | 0.155234 | -1.96% | 1.0331x | M256/N64,C2,F4,epi_warps | {'0': 8} |
| 16 | 0.168081 | 0.178048 | 0.166241 | 0.162274 | -8.86% | 1.0244x | M256/N64,C2,F8,epi_warps | {'0': 8} |
| 32 | 0.205329 | 0.205377 | 0.201986 | 0.186289 | -9.29% | 1.0843x | M256/N64,C2,F8,epi_warps | {'0': 8} |
| 64 | 0.225650 | 0.234193 | 0.223538 | 0.209170 | -10.68% | 1.0687x | M256/N64,C2,F4,epi_warps | {'0': 8} |
| 128 | 0.237970 | 0.239042 | 0.222754 | 0.225154 | -5.81% | 0.9893x | M256/N64,C2,F4,epi_warps | {'0': 8} |
| 256 | 0.244195 | 0.239185 | 0.243681 | 0.229953 | -3.86% | 1.0597x | M256/N64,C2,F8,epi_warps | {'0': 8} |
| 512 | 0.241201 | 0.247985 | 0.239665 | 0.233249 | -5.94% | 1.0275x | M256/N64,C2,F4,epi_warps | {'0': 8} |
| 1024 | 0.251426 | 0.263041 | 0.260497 | 0.252705 | -3.93% | 1.0308x | M256/N64,C2,F8,epi_warps | {'0': 8} |
| 2048 | 0.354882 | 0.353153 | 0.355825 | 0.339650 | -3.82% | 1.0476x | M256/N128,C2,F4,epi_warps | {'0': 8} |
| 4096 | 0.554083 | 0.510994 | 0.551635 | 0.509155 | -0.36% | 1.0834x | M256/N128,C2,F4,epi_warps | {'0': 8} |

The complete two-source comparison is logs/cu132-input-dispatch-vs-graph-independent-001/comparison.json (SHAcdc798f68e80b8239d47c7fa57e3cbe43af87c1fa2f2ec9f7317b0461288283f) and comparison.md/raw-latencies.csv. Its strict analyzers retain104 total raw values,416 split records,416 selected compiled records,208 returned rank choices and26 complete rankings. The candidate's selected208 records are all local0. Integration additionally reconciles all1872 original prelaunch records (104 fixed+1768 auto); all have REG128/512/twoWG/pool65536/local0. These are canonical benchmark objects, distinct from the six small public local8 objects.

Against graph0d, input auto improves7/13 and fixed improves6/13 (fixedT16 effectively unchanged). Auto4096 .509155 versus .530692 is−4.06%; fixed4096 .510994 versus .527445 is−3.12%. Auto32/64 improve3.60/4.37%; auto4/8/16 regress5.21/5.49/3.57%. Auto128 Mega .225154 versus .225282 is effectively flat (−.06%), while paired split falls3.97%, putting the candidate ratio at.9893x. Do not call that a measured4% Mega regression, subtract split drift as normalization, or mix per-row minima. The source change remains a meaningful candidate with mixed full-grid evidence; no unqualified overall-best or PR table promotion follows.

The next separate first32 predecode runtime trial targetsf651 on graph0d, not input21ee. Its installer is prepared dry-only at logs/install-first32-on-graph-after-input-001.py (SHAbd99695b69bcc5a43874e3d9a8a2b18ecb66c69aaed9c326be752a281ea92c89), exactly changing kernel/shared transform and restoring graph0d communication; existing shared native-quality evidence and fresh all-tactic numerical gates remain required. The modern five-WG alternative is a separate unapplied artifact: publishedC1 geometry/roles/caps plus exact staticFC2 and graph scorer, no invented dispatch policy. It uses the existing640*96=61440 register pool (~94%) rather than an infeasible640*100 request. Native/codegen and new runtime gates remain pending for that combined source.


### 021a. Small-fixture native allocation attribution; tail-scope cohort preserved unrun

Completed all four exact small-fixture sealed CPU captures after the input full13 timing window, under production source21ee and native13.3 compiler SHA `bb367e30bb24541faa974ed05ff201171f61c5b18b01df9e46a406bdde5edbba` / DSL4.7.1. Each arm made one actual cute.compile call with CUDA hidden and zero device allocations, collectives or compiled-kernel invocations. Control private sources are graph0d; candidate private sources are input21ee. The original small-fixture helper is `50a320ffc07d656ebccfef1ac5c0974046e2ec406e0bd937e25dc2445ad1f939`, with exact E4/top2/T257 and CPU DLPack/workspace descriptor equivalence checked. This is native code-quality evidence, not numerical or performance timing.

| Fixture, EP1/rank0, M256/N64/K256/C2, epi return | Control → candidate SASS | REG / threads both | Native STACK | Native LOCAL | LDL/STL count |
| --- | ---: | --- | --- | --- | --- |
| H192/I320/T257/E4/top2/flag8 | 4488 → 4600 |128 /512 |0 →8 B |0 →0 B |0 →2 |
| H288/I448/T257/E4/top2/flag4 | 4552 →4680 |128 /512 |0 →8 B |0 →0 B |0 →2 |

Both retain raw5/decoded3/acc2, sixteen static MMA instructions, four R2UR.BROADCAST instructions, DEC80/INC176 and no named barrier11. Native static shared allocation is1024B in all four; that is separate from launch dynamic shared memory. Exact source, descriptors, configuration and every opcode delta are saved.

Both candidates' only local payload is one32-bit shared-storage base in an8-byte stack allocation. Entry S2UR/UMOV/ULEA constructs `0x400 + (CTA cluster bits <<24)` in UR4, copied toR4 at0xa0 and saved by `STL [R1],R4` at0xf0 before role dispatch. The only reload is `LDL R3,[R1]` at0x11bf0 forH192 or0x120a0 forH288. It feeds the two-CTA **TMEM deallocation** slow wait on `[base+0x170]`, whose initialization maps to TmemAllocator construction at frozen kernel1167 and whose fast wait maps to tmem.free at1060. The slow backedge repeats the reload; its success edge rejoins immediately after the original fast wait. UR4 is unchanged through that wait path. The control uses `MOV R3,UR4` at the corresponding slow-wait entry. The inherited scheduler187 annotation on the LDL alone is misleading; exact def/use, barrier address/init, adjacent source and native CFG resolve its role.

There are no local loads/stores in either weight-decode body in these captures. The slot is not FC1/FC2 output, routing metadata or decoded weight payload. Dynamic slow-wait iteration count and cost were not measured. These exact EP1 native captures explain the same observed allocation size in the matching small public cases; the earlier EP2 objects were not recompiled here. Review and machine-checkable proof: `candidates/w4a16_input_dispatch_small_local_native_review_21ee/{README.md,first-pair-audit.json,remaining-pair-audit.json,allocator-slot-proof.json}`, handoff `8f6beda0a8e52f466e6315073119a867c7c889539cff8589f50f70c208ff9746` seals110 preserved files. Both complete archives and all runner/provenance logs were fetched before releasing the CPU window: firstpair archive SHA `4fcbec0704be7782de513ab824ee04af8e11aa62a8bfc9d9ff8e113e5be9d26c`, remaining archive SHA `15dc7deef5c1c3d00cbaeb24a3f6167f503128a04d7861028093a09f11d045c6`. Both postflight proofs preserve all3684 production files and28 cohort inputs and have no surviving compiler/cohort children; no GPU query was used by this audit.

Prepared a separate general **tail-scope** refinement, with no active-source edit: move only the unchanged system fence, allocation-permit relinquish and TMEM free from the private input/epilogue method to the caller's existing `warp <4` arm. This restores the control's cleanup scope while keeping input/epilogue state private, preserving exact ordering before the common communication tail. No new predicate, pointer arithmetic, barrier, broadcast, register knob or shape selector is added. Reversing the three-statement relocation gives whole-module AST identity; unittest, Ruff, formatting and isolated git-apply check pass. The compiler may still produce the same or worse code; no improvement is claimed. Artifact `candidates/w4a16_input_dispatch_tail_scope`, handoff `901fbc5b1ddc794cef20112e5f48efc08866062295d46fc9faa704f26c4eefaf`, patch `9ab68382360e6ac6de5341e91a31c91d36b01108440263b47a96dd99e966ce0b`, proposed kernel `74eafd23f811bca3fb57f25dec3c9a0434e30e7e02407049162cb90ab4ad387e`.

The new matched refinement cohort is frozen at `candidates/w4a16_input_dispatch_tail_scope_compile_21ee`, handoff `0790fe6089db5b06d5315cb7c0e899cbb1cb8cfbcdf9f863ea4a990111a8399e` (26inputs plus handoff). Both arms preserve helper50a320; current input0b038/comma2fb is control, and only kernel74eafd differs for candidate (logical source1e7be18d…). Ten CPU tests pass, including process-group cleanup after an exited leader, exact native/source gates, missing/corrupt postflight rejection, and exact fixtures. Remaining-pair admission requires complete hashed success/source/native records, not a result.json alone. The old fixture0→8 observation stays immutable and explicitly labeled historical rather than misreported as the new arm result.

New-only staging completed27files, all3684 production hashes unchanged, no native imports/compiles/GPU, audit `logs/cu132-input-tail-scope-cohort-stage-001.json` SHA `d7e702fd4d84210933d3a1f875e5467b02c573697993532f01f6e6987df8d532`. The parent subsequently stopped the pending tail launch after two HAI checks reported devbox0908b had disappeared. **No tail-refinement native capture ever started.** All local artifacts remain intact; no remote retry or provisioning was performed by this subtask. Parent owns CUDA13.2 replacement. The staged0790 cohort requires source21ee/shared4a870/nativebb367 exactly and must not be reused unchanged against a replacement0d/f651 owner: prepare a fresh owner declaration and private shared-decoder admission before any future compile. H192 remains the bounded first refinement gate; H288 only follows an actual code-quality improvement and renewed authorization. First32 runtime work takes priority over an expanded refinement matrix.


### 022. CUDA 13.2 replacement baseline admission and native-cache preservation

CUDA13.0 is discontinued by explicit user direction; its owned box was released and no new130 tests/timing ran. Replacement132 `fi-w4a16-mega-0908c` is on c2/ziangli/hu-pdx-133, eight B300, driver590.48.01, explicit `nvcr.io/nvidia/pytorch:26.05-py3`, bare/no size argument. Live NGC/release matrix was rechecked immediately before the request. The source installed remotely is frozen graph0d, while local source remains input21ee. The first request from the effort root failed because managed h requires the HAI checkout cwd; the second managed request from effort/hai completed. Original setup001 installed the pinned environment but invoked preflight with its default13.0 expectation. It failed honestly, was preserved, and only the invocation was corrected to explicit13.2 in verification002. No reinstall or gate relaxation followed. Accepted preflight002 SHA7547965f102ad3ffacdafbc4ccb0beed1b2f6b30fc5185a5ba564a9eac81d9fb; setup completion SHA52f51d708d8e97cfd30fab8149f7a12e8fe7da1beb1ee88c040b197bc2832830. Source1573/338, native13.3/direct bb367, image/runtime bytes, CUPTI binding and NSYS/NCU are verified. Old lost-node cache paths are never admitted as existing.

Fresh-owner adapter `candidates/cuda132_recovery_0908c/performance` passed35 CPU tests, Ruff and independent review. Its193-entry handoff is ab67f40f7a3a8fe9fd7a58c67d2d64e1f2361a83b0a5667e3bdbc2dad586bc89; 194 staged entries (184new/10exact skips) were checked. Exact old public120rank-tests/192compiled objects are inherited through161 hashed evidence files, unchanged device/shared/vendor sources and matched native/image/driver; they were not rerun on the new node. Four fresh jobs then ran serially: resourceEP2, all16-tactic lifecycleEP1, lifecycleEP2, real graph-samplerEP2. All four completed exit0 and all evidence was fetched. Independent audit `logs/cu132-recovery0908c-graph-numerics-independent-001` reconstructs all source/native/helper/input/result hashes and the native-cache chain.

All58 original prelaunch resource records are REG128/512threads/two decode WGs/pool65536/local0. The lifecycle jobs check48 candidate records (32 nonempty numerical oracles and16 empty-rank contracts), nine stable and three changed-input serving-graph replays, cached second-layer selection, and collective winner agreement. The sampler checks both ranks' capture/replay/reset, peer capture failure with zero replay/timer entry on both ranks, and same-workspace recovery. Final owner: `logs/cu132-recovery0908c-graph-graph-sampler-ep2-001/validation-manifest.json`. The first resource job owns four fresh caches; subsequent validation jobs reuse only its native C++ roots through the immediately previous successful job, while DSL/driver caches are fresh per job. Full13 will own a separate fresh native generation.

After all four jobs and fresh idle/source proof, the reviewed stdlib-only helper `candidates/native_cache_backup_0908/backup.py` archived exactly that final owner's two declared native roots. Eight focused CPU tests cover binary/empty-root/PAX nanosecond metadata and failure/mutation/redirect/writer rejection. Root independently reviewed the helper and checked all actual fetched artifact hashes, archive member bytes, modes and nanosecond mtimes, exact owner and final native inventory. Snapshot `native-cache-backups/cu132-recovery0908c-validation-001` contains12files/7,717,163B; manifest SHAee8d0e2c4e6858076b134941e820570001bbb9dac54dbf45afba4db73e0303e2; archive SHAcdad071de107517ab196d4ec4eb905c8540dcf9ae4aed44f5e39df1708f7a4cd. Record: `logs/cu132-recovery0908c-validation-native-backup-independent-001.json`. This is preservation only, with no restore/load compatibility claim. External dependency timestamps, toolchain/ABI, actual paths, Ninja freshness and native loading still require verification before reuse. The resolved image digest remains unknown; the explicit image tag is recorded.

The optional modern-five-WG N64-only native pair is separately frozen against real owner0d, using unchanged private ce2/ec94 packages and sealed helper7eb9. It follows backup and precedes primary timing; no fresh N64 result is claimed by this entry. The pending primaryfull13 retains the original100CUPTI/3warmup/graph/coldL2/median-per-iteration-rank-MAX metric and complete fixedCONTROL plusauto16 1–4096 grid. First32f651 follows as an exact two-path successor with eleven fresh public/lifecycle/sampler jobs, not as an input21ee overlay. No PR body or commit was promoted during recovery.

A separate unapplied host-only trial is prepared at `candidates/w4a16_cold_graph_scoring`: enable the existing CUDA-event helper's cold_l2_cache flag, update the docstring and use a distinct autotune_graph_events_cold_l2 cache provenance label. AST comparison proves exactly those three constant changes, with no control-flow/signature/catalog change. The explicit buffer flush occurs before every measured start event; this is distinct from the older zero-argument graph-buffer timing helper, which had no explicit tensor inputs to rotate. It is a cache-condition experiment, not evidence of hardware eviction or performance improvement. Fresh lifecycle/sampler and complete primaryfull13 remain required. Baseline and first32 execution take priority.


### 022a. Fresh graph0d full13 baseline on hu-pdx-133

Completed cu132-recovery0908c-graph-full13-001, both original fixed CONTROL and auto16 arms, with exit0 on exact source0d/nativebb367. All four performance caches were freshly created, separately from validation. Strict saved analysis at logs/cu132-recovery0908c-graph-full13-001-analysis verifies52 raw values,208 split selections,208 selected compiled records,104 returned choices,13 full16-candidate rankings and10 final capacity-cache entries. Every selected object is actualREG128/512/twoWG/pool65536/local0. Comparison JSON SHA f29d77f48e26b8f68705972bf5db9543fe7f39c8b8a9c3e94e9577e5a057332e. Original primary EP8/H7168/I2048/E256/top8/100CUPTI/3warmup/coldL2/one-forward graph/median per-iteration rank-MAX activity span and independently retuned split no-fused-finalize remain unchanged.

Auto beats its fixed arm at12/13 shapes;T4 is0.35% higher. All13 actual winners use epi_warps. T4096's returned dictionary exactly equals fixedCONTROL, so its0.36% movement is context variation rather than a tactic gain. T2 andT1024 are below paired split (0.9919x and0.9953x);T64 is near parity at1.0022x. The complete table is a same-node starting point for first32, not a new overall-best selection across historical sources. No PR table or code was promoted.

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.083072 | 0.094865 | 0.077264 | 0.072000 | -24.10% | -6.99% | [3, 4, 6] |
| 2 | 0.116464 | 0.112352 | 0.097249 | 0.098048 | -12.73% | -16.50% | [3, 4, 6] |
| 4 | 0.145297 | 0.128816 | 0.144737 | 0.129265 | +0.35% | -0.39% | [3, 4, 6] |
| 8 | 0.162609 | 0.158017 | 0.163521 | 0.141969 | -10.16% | +0.56% | [3, 4, 6] |
| 16 | 0.171553 | 0.170049 | 0.175505 | 0.159056 | -6.46% | +2.30% | [6] |
| 32 | 0.205457 | 0.203218 | 0.208482 | 0.195649 | -3.72% | +1.47% | [0, 1, 3, 5] |
| 64 | 0.220402 | 0.226849 | 0.223218 | 0.222721 | -1.82% | +1.28% | [3, 4, 7] |
| 128 | 0.237378 | 0.234353 | 0.233537 | 0.226402 | -3.39% | -1.62% | [1, 3, 5, 6, 7] |
| 256 | 0.243361 | 0.242593 | 0.246465 | 0.227042 | -6.41% | +1.28% | [0, 1, 5] |
| 512 | 0.242594 | 0.249826 | 0.236882 | 0.229618 | -8.09% | -2.35% | [1, 2, 4, 7] |
| 1024 | 0.262818 | 0.269169 | 0.259410 | 0.260641 | -3.17% | -1.30% | [0, 1, 4] |
| 2048 | 0.348546 | 0.343330 | 0.348690 | 0.339170 | -1.21% | +0.04% | [3, 4, 6] |
| 4096 | 0.551779 | 0.532003 | 0.553700 | 0.530068 | -0.36% | +0.35% | [] |

The exact source/config fixed comparison with the earlier lost-node0d run is saved separately in logs/cu132-recovery0908c-fixed-repeat-context-001. Its Mega differences range from−5.84% to+4.63%, with independent split retuning. No causal kernel improvement or native-binary identity is inferred across nodes.

Native performance backup v1 failed honestly before output creation because an internal generated TRT-LLM directory symlink resolved under the same declared cache root. The original helper and failed log remain unchanged. The separately reviewed v2 preserves one SYMTYPE member and contemporaneous link/target metadata, archives regular payload only through plain paths, and preserves exact legacy owner file inventory. It rejects cross-root/external/file/dangling links;13CPU tests plus independent mutation/integrity checks pass. At this entry's writing v2 archive is running; no completed snapshot or restore claim follows yet.

Backup v2 subsequently completed/fetched with exit0 and independent artifact verification: native-cache-backups/cu132-recovery0908c-performance-v2-001; manifest04edab2ec91d377151f7db78248b61b53c655abe1db695cfe74df1b458b821df; archive594903239a7eb7d43a6942e3d102b41194a34bea9d35f953bc1024ea3fc4834b. Exact76 regular files/49,758,296B,24directories and one internal directory link; all artifact/member bytes, modes and nanosecond mtimes verified without extraction. Independent receipt62c8e3f3c59b68352af8b339a4a5fd81836ebcc041a85414dd3420877d5d190d. Source/native cache/toolchain were unchanged; no restore/load claim. All backup PTYs closed before source transition.

Both exact installers then completed: local21ee→f651 restores graph communication and patches kernel/shared; remote0d→f651 patches only kernel/shared. Target f65112e5d2ed3ca5f0db8c65b909e2483994453453921f265ee3ba82250e88e3; untouched sources/helpers fully match the frozen declaration. Fresh actual CUDA13.2 preflight exited0 with SHA6ac92fd6dd2b9cd827e9ef0adfeda8fcd3bbbc256bf150951815147952583c53 and nativebb367/directTrue. Eleven fresh numerical jobs launched under performance-owned PTY66337 using separately reviewed launcher e82ebb76…, sixCPUtests. This is running work, not a candidate numerical or timing result. Full13 remains gated on all eleven completed jobs.


### 023. First32 numerical gates complete; primary CUDA13.2 performance trial running

The exact f651 first-fragment candidate completed all eleven fresh numerical jobs on hu-pdx-133. Numerical launcher66337 exited0 with every ordered READY marker and real remote exit marker; all folders and final summary were fetched. Independent final audit logs/cu132-recovery0908c-first32-numerics-independent-001/audit-final.json SHAe2d77071e570599146bf28a414312fe187fd77ea3a64ccb9517ea078dc7b0ad6. Summary SHA1546a653330195e559f707ac8033047da6f12774b8a09e6bc19e8215f7fa8b2c. No candidate public proof is inherited and no tolerance was relaxed.

All120 public rank-tests and192 config-paired objects passed across four geometry/cluster pairs at EP1/EP2. The two lifecycle jobs cover48 candidate records (32 numerical oracles and16 empty-output contracts), collective winners, second-layer cache reuse, nine stable and three changed-input graph replays. Final sampler EP2 passes valid capture/replay/reset, peer rank1 capture failure with zero replay/timer entry on both ranks, and recovery on the same workspace. All248 actual prelaunch records report REG128/512threads/two decode WGs/65536registerpool/local0, with loaded shared c89 class/MRO and unchanged c36 decoder identities verified before cached launch. This is source-specific numerical/resource evidence; the earlier native four-capture overlap proof remains separately labeled.

The exact baseline-final→all11 jobs native chain validates. Root additionally compared baseline graph0d full13 native-cache-after.json with the final first32 sampler inventory: byte-identical SHAc7978da4f7cb050b7468f221c5e2cb33caac811597213dfaf083178de5be45e8, zero Torch-extension files and76 FlashInfer files, no changes/additions/removals. If first32 full13 preserves this inventory too, the existing modern5WG graph0d native-owner admission remains usable; no speculative successor exception or inventory relabeling is needed.

Root reviewed original full13 launcher31671cb431325a431f2d23f77ed96c704f89cd0f845646c7c7d4e307a902e3e9 and approved the actual summary. Original dry plan and fresh source/native/idle checks passed. Primary cu132-recovery0908c-first32-full13-001 launched under performance-owned PTY94848, preserving the complete fixedCONTROL thenauto16, global1–4096,100CUPTI/3warmup/coldL2/one-forward-graph/median-per-iteration-rank-MAX metric and same-source independently retuned split no-fused-finalize. No benchmark result or PR promotion is claimed at this entry. No competing native/GPU work is scheduled.

Prepared local first32_analysis/analyze_full13.py reuses original raw/tactic/resource/scorer/numerical validators, with exact current-owner saved-chain handling and isolated baseline analysis; its tenCPU tests and replay of the real completed eleven-job chain pass. It still requires actual completed full13 artifacts. Root's compare_first32.py reuses frozen prior comparison math to preserve all104 raw fixed/auto values across0d/f651, per-row source changes, split retuning, actual choices and local resources. No row minima or baseline-drift subtraction is used.

A separate saved-sample audit at candidates/w4a16_rank_aggregation_audit reconciles1,920rankvisits/19,200graph samples from the earlier e2d88 five-shape diagnostic. Reaggregating MAX of rank medians into median of per-iteration rank maxima changes only2/15 winners (T1pass2 andT64pass1), with alternative first/second margins0.016us and0.032us. T128/512/4096 choices remain unchanged in all three passes. These are historical hot queued graph samples, not current0d/f651 or cold CUPTI; no better policy or source change is inferred. Kernel/layout and the prepared cold-cache scorer trials retain priority.

User further reaffirmed exactly two weight-dequantization WGs for every trial, with no one-WG variants, and explicitly prefers the cleaner total-five-WG layout if performance is comparable. Its dedicated input dispatch stays separate from both decode groups. Total-four-WG register utilization alone is not a retention argument; the modern640x96=61440 (~94%) allocation is acceptable. The active first32 sweep will finish unchanged for complete evidence, after which modern5WG is the preferred base unless the full1–4096 results show a significant regression. No per-shape role policy or new public register/WG knob is added.


### 024. Complete first32 comparison; prefer modern five-WG next

First32 is numerically valid but this complete sweep does not establish a broad performance gain over the fresh graph0d baseline. Keep it as a separate measured candidate. Proceed with the user's preferred five-total-warpgroups layout with dedicated input dispatch when comparable; both layouts retain exactly two weight-dequantization warpgroups. Register-pool occupancy alone is not a retention reason.

The complete fixed and auto tables are in [README.md](README.md), all104 literal raw values in [raw-latencies.csv](raw-latencies.csv), and exact per-rank configurations, compiled/resource observations and split tactic changes in [comparison.json](comparison.json). The candidate's thirteen returned configurations are also preserved in `../cu132-recovery0908c-first32-full13-001-analysis/auto16-full13.md`. No row is replaced with another run's minimum.

- The fixed CONTROL uses identical dictionaries at all13 points. First32 improves4/13 and regresses9/13. The largest improvement is1.83% at512; the largest regression is6.01% at2. At4096 the change is+0.05% (.532003→.532260ms), effectively close in this unbracketed comparison.
- Auto improves6/13 and regresses7/13. Seven returned configurations change across the two sources. T1/T2/T8 regress18.24%/8.94%/12.26%;1024/2048/4096 improve4.31%/1.43%/1.40%. T8 has the same returned configuration in both auto runs, but this one pass does not distinguish source behavior from timing context.
- Within first32, auto is faster than fixed at12/13; T8 is1.42% slower. At4096 its selected config, compiled metadata and resource gate are exactly the fixed CONTROL, so .522644 auto versus .532260 fixed is measured context variation, not a tactic benefit.
- First32 auto beats its same-run split at every point above32, but64 and512 are only1.0014x and1.0075x. It trails split at1,8 and32. Split independently retunes:32 rank-level tactics change between source control arms and51 between source auto arms. Split timing movement is retained explicitly; no drift subtraction or statistical uncertainty estimate is asserted.

Both complete same-node runs use the same original EP8 benchmark, global token powers of two1–4096,100 CUPTI iterations, three warmups, CUDA graphs, cold L2, and median of per-iteration maximum-rank GPU activity spans. The source-identical graph scorer is separate: its hot prestaged graph GPU-event rankings are selection evidence, not these final CUPTI timings. Full source comparison admits exactly the Mega kernel and shared W4A16 transform module; default-False shared-path source preservation is recorded, while split is still measured and retuned against that changed shared module.

The strict analyzer passed52 raw values,208 split selections,208 measured compiled objects,104 actual auto rank choices, thirteen sixteen-candidate rankings, and final capacity-cache choices/scores for first32. Both sources together reconstruct104 raw values,416 split records,416 compiled records,208 auto choices and26 rankings. All candidate measured resources have REG128,512 threads, two decode groups and zero local bytes, with exact shared-MRO/decoder hashes. Numerical closure independently passed all120 public rank cases,48 catalog candidate records, nine stable plus three changed-input serving replays and the two-rank sampler capture-error/recovery test; all248 numerical resource objects pass.

The final run exited0 and fresh source/native/worker/GPU quiescence was verified at21:07:45.75UTC. Native roots equal the completed graph0d owner. The saved baseline inventory SHA is c7978da4f7cb050b7468f221c5e2cb33caac811597213dfaf083178de5be45e8; final candidate is94b60815fa0d0eba0a87c7adf0322bb898743d2ac43a1eb43860c3d488f63715. Both contain76 entries. Only `flashinfer_jit.log` grew143601→188737bytes; all75 other entries retain identical paths, sizes and hashes. See `../cu132-recovery0908c-first32-final-native-inventory-001.json`. The final inventory was freshly captured by the original completed driver; no additional remote operation occurred after the execution window was released.

These are complete, unbracketed source trials on one recovered node, not statistical significance or an arithmetic-only causal isolation. No PR body, production source, or frozen helper was changed by the analysis.


The complete literal timing tables follow; choices and raw samples remain in the linked original artifacts.



| T | Graph split | Graph Mega | First32 split | First32 Mega | First32 split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.083072 | 0.094865 | 0.096465 | 0.095169 | 1.0136x | +0.32% | +16.12% |
| 2 | 0.116464 | 0.112352 | 0.101312 | 0.119105 | 0.8506x | +6.01% | -13.01% |
| 4 | 0.145297 | 0.128816 | 0.136001 | 0.133024 | 1.0224x | +3.27% | -6.40% |
| 8 | 0.162609 | 0.158017 | 0.156097 | 0.157153 | 0.9933x | -0.55% | -4.00% |
| 16 | 0.171553 | 0.170049 | 0.180273 | 0.170352 | 1.0582x | +0.18% | +5.08% |
| 32 | 0.205457 | 0.203218 | 0.203649 | 0.211106 | 0.9647x | +3.88% | -0.88% |
| 64 | 0.220402 | 0.226849 | 0.221889 | 0.230546 | 0.9625x | +1.63% | +0.67% |
| 128 | 0.237378 | 0.234353 | 0.236369 | 0.241746 | 0.9778x | +3.15% | -0.43% |
| 256 | 0.243361 | 0.242593 | 0.233361 | 0.242146 | 0.9637x | -0.18% | -4.11% |
| 512 | 0.242594 | 0.249826 | 0.240177 | 0.245266 | 0.9793x | -1.83% | -1.00% |
| 1024 | 0.262818 | 0.269169 | 0.240706 | 0.266914 | 0.9018x | -0.84% | -8.41% |
| 2048 | 0.348546 | 0.343330 | 0.351795 | 0.343570 | 1.0239x | +0.07% | +0.93% |
| 4096 | 0.551779 | 0.532003 | 0.533683 | 0.532260 | 1.0027x | +0.05% | -3.28% |

Auto: all13 rows, ms.

| T | Graph split | Graph Mega | First32 split | First32 Mega | First32 split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.077264 | 0.072000 | 0.083489 | 0.085136 | 0.9807x | +18.24% | +8.06% |
| 2 | 0.097249 | 0.098048 | 0.116513 | 0.106817 | 1.0908x | +8.94% | +19.81% |
| 4 | 0.144737 | 0.129265 | 0.136752 | 0.129808 | 1.0535x | +0.42% | -5.52% |
| 8 | 0.163521 | 0.141969 | 0.156400 | 0.159378 | 0.9813x | +12.26% | -4.35% |
| 16 | 0.175505 | 0.159056 | 0.176946 | 0.164529 | 1.0755x | +3.44% | +0.82% |
| 32 | 0.208482 | 0.195649 | 0.189377 | 0.194673 | 0.9728x | -0.50% | -9.16% |
| 64 | 0.223218 | 0.222721 | 0.221473 | 0.221154 | 1.0014x | -0.70% | -0.78% |
| 128 | 0.233537 | 0.226402 | 0.230690 | 0.226322 | 1.0193x | -0.04% | -1.22% |
| 256 | 0.246465 | 0.227042 | 0.239058 | 0.230162 | 1.0387x | +1.37% | -3.01% |
| 512 | 0.236882 | 0.229618 | 0.238930 | 0.237154 | 1.0075x | +3.28% | +0.86% |
| 1024 | 0.259410 | 0.260641 | 0.262786 | 0.249410 | 1.0536x | -4.31% | +1.30% |
| 2048 | 0.348690 | 0.339170 | 0.356627 | 0.334307 | 1.0668x | -1.43% | +2.28% |
| 4096 | 0.553700 | 0.530068 | 0.548133 | 0.522644 | 1.0488x | -1.40% | -1.01% |

Full choices, resource observations and tactic changes are in comparison.json; all104 literal raw values are in raw-latencies.csv.

The accepted f651→ec94 source installer remains separate from native-owner admission. Because full13 appended the JIT log, original modern5WG admission must stay frozen and fail closed; the successor will explicitly admit completed first32 and inventory94b60815. All75 non-log native files and roots remain unchanged. Source installation, fresh12 numerical jobs and actual host tests precede pushing the staticFC2+graph scorer to draft5019. No first32 or cold-scorer promotion is implied.


### 025. Modern five-WG source installed; host checks pass; fresh numerical sequence started

Exact accepted f651→ec94 installation completed locally and on hu-pdx-133, restoring published195946 kernel/frontend/dedicated dispatch and original shared4a transform while retaining staticFC2 epi604935 and graph scorer6d. Only autotune.py and w4a16/epilogue.py differ from publishedHEAD; no shared decoder/transform, frontend, communication or role-layout patch remains. Both installers preserve allfour originalf651 files and full before/after inventories; fetched remote receipts are separate from local receipts. Fresh native preflight SHA3660b1dd87e0baead40f0c4326794bb0fdcf877dbd0ba0b21414ec5f83d35d0d records actual CUDA13.2/native13.3 directbb367 and Mega e009.

Actual Torch/pytest CPU validation:125 passed,2warnings in2.30s at logs/cu132-recovery0908c-modern5wg-host-001.log (SHA49a78ddf79b1726cd7dad7f74a5a234ec3a846aaf773602b25d285d03ebe10bc). Three public host files ran alongside four proposed graph-ownership cases loaded from the effort candidate path, outside the frozen repository. Those four cases mock CUDA boundaries, while the later realEP2 sampler remains separate. All source bytes stayedec94. Changed-runtime-file pre-commit passed mypy/Ruff/formatting/standard hooks with no edits; receipt41afbc0771868d60a8c6afefd607e095dbe5210e91221e2e5536a6b15205a1ae. Two independent source reviews found no correctness blocker; stale comments/docs/newtest cleanup is frozen separately and unapplied.

Original modern34-file staging002 completed. The separate successor modern5wg_after_first32 (handoff91388c915bd2f4f151bfb8a46cdf6c037516fcdd3db5af0687ac6ec7629ffdc8) admits complete first32 manifest932bdf5e/results6c6eba94/finalnative94b60815 through the unchanged savedfirst32 analyzer. Original640resource/public/lifecycle/sampler/timer payloads remain untouched. First remote dry failed before GPU work because a frozen first32 handoff CPU log was missing; staging10 unchanged historical closure files resolved it. No analyzer, tolerance or evidence gate changed. Dry002 SHA3b84507880ec9f6a466ce616649561be79249fecc23963593e8fafb159325a89 passed complete saved owner/native/liveidle admission.

Performance-owned launcher41ed2380 started original12-job sequence underPTY66919, marker MODERN5WG_VALIDATION_0f3382703f4a4981ad03647a6adcb582. Initial EP2 resource probe completed21:33:05UTC: both actualcompiledobjects REG96/640/two decodeWG/61440pool/local0, no Mega launch. Eight public geometry jobs, lifecycleEP1/2 and actualsamplerEP2 follow. This entry does not claim their success or any modern timing. Full13 and the two-file draftPR push remain gated on numericalcompletion.

Queued first16 prefix remains source-only a9b149c2, handoffa657e016; native-plan9dbab9cb has exactlyfour matched N128/N64 captures using unchanged640 helper7eb93095. The future selected-utils→selected-shared bootstrap is necessary because the decoder wrapper admits16values/8packedbytes/1SFbyte; no arithmetic rewrite. Native gates must show actual first16 before wait/remaining16 after, unchangedload/store/MMAcounts and no newlocals. No compile cohort or GPU work has run. Root compare_modern5wg.py c4f9d9d3 reuses prior complete-table math and exact0d→ec94 source/resource transition, not a claim of results.


Modern sequence subsequently completed all12jobs with original66919exit0 and allorderedmarkers, summary5fd1e7332c6ea68c2f8c1dd1266111cb875da9197fc454a83556070c187fe281. Final independent audita604cb0a16613342af056a0c2bdd4b60d2b27305f0ae6e647541fe9ca1130e5d validates120publicranktests,48catalogrecords,9stable+3changedgraphreplays andactualEP2samplerfailure/recovery. All250actualobjects REG96/640/twoWG/61440/local0; finalnativeinventory exact94b6. Runtime semantic commitbd2fa61c82caed9b5237aea00db5ce00436beb41 was created/pushed to draft5019, with actualcommit hooks passing and fullsourceec94 unchanged. Onlyautotune.py/epilogue.py differ from195946. Commitproof logs/modern5wg-semantic-commit-proof-001.json; newgraphhosttest remains validated from its externalcandidatepath pending later cleanupcommit.

Authorized original full13 launcherd7285ea30a3bd1155ac9421c89f41a5ebcb0d54f5c8ee6d2c8bcd3ea085869f1 started underperformancePTY66515, marker MODERN5WG_FULL13_2f59fb1c08c84100bb2ef9711c2129e8. Freshsource/native/summary/idle/dry gates passed; originalfixedCONTROL thenauto16/all13/100CUPTI metric. Fiveinitialownerartifacts fetched83078; nativebefore remains94b6. No full13 result or newbest is claimed at this entry. PRbody draft preserves all26 older performance rows byte-identically and explicitlylabels their older195946/6315 sources while newec94 timing proceeds.

PR5019 body was reviewed, updated and read-back verified on draftheadbd2fa61c. Publicationreceipt logs/pr5019-modern5wg-publication-001.json; bodySHAd4c534034ba8647b1cf79b145ba45ad0af50512c69c36ee1165f72fec0b6b924. It includes all12 literal publicpytest resultlines, bothlifecyclePASS andsamplerPASS, actual125hostscope and250prelaunchresourceobservations. All26 older performance rows remain byte-identical, with explicit older195946/6315commitlabels and currentfull13pending. Review corrected stale130cluster1-not-rerun wording without claiming new130validation of this epilogue/scorer. No PRcomment or draftstatechange.


### 026. Complete modern five-WG fixed/auto result; semantic changes pushed

Original full13 process66515 completed with both UUID markers and real exit0. Complete fetch30318 closed; fresh source/native/GPU-idle check at2026-09-08T22:24:06.351507UTC passed on hu-pdx-133. Execution receipt5ea68738fd4e1bd785c2b6a71101ccb00c35474eda28b7c13d0f9228d83a3b13; idlef556b811b84d14186e5e8043cd3240f4bd08999c25e6b038c8772206835e0fa1. Local committedbd2fa and remote195946 overlay are exact ec94 source; no source mutation occurred during timing. The exact final native inventory isfc0821a90c2e78636305d359dca2ad3b081094f0b9357aa901f6d79d259be98c. It supersedes preceding94b6 for future native-window admission; do not relabel the old inventory.

Strict saved modern analysis b15e3fa0e37ff60382e39eb2e4050ca522b7bf83241ea9c2cf3e7b79025efb85 and independent rerun agree. All52 literal raw rows,208 actual split configurations,208 actual compiled records,104 returned rank winners,13 complete sixteen-tactic rankings and all twelve numerical predecessors reconcile. Every timed production object is REG96/640/two dequant WGs/61440/zero local bytes. Primary protocol remains EP8,H7168/I2048/E256/top8,100CUPTI,three warmups,coldL2,one-forward graphs,split no-fused-finalize and median(per-iteration rank-MAX GPU activity span).

The modern auto arm is faster than its fixed CONTROL at all thirteen points, fixed/auto geometric mean1.0660x. Auto4096 is0.496995ms,1.1211x paired split;128 is1.0344x. T1,T2 and2048 are below split;2048 is 0.9994x, a0.208us difference. This is one complete run, no row minima or drift subtraction.

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.080656 | 0.094928 | 0.086481 | 0.087441 | -7.89% | +7.22% | [1, 4, 7] |
| 2 | 0.116624 | 0.112033 | 0.102448 | 0.108656 | -3.01% | -12.16% | [1, 4, 7] |
| 4 | 0.127505 | 0.135777 | 0.143441 | 0.121488 | -10.52% | +12.50% | [1, 4, 7] |
| 8 | 0.162385 | 0.158593 | 0.156209 | 0.150577 | -5.05% | -3.80% | [1, 4, 7] |
| 16 | 0.180945 | 0.173153 | 0.175761 | 0.162480 | -6.16% | -2.86% | [4] |
| 32 | 0.204002 | 0.213362 | 0.203105 | 0.192385 | -9.83% | -0.44% | [0, 1, 2, 7] |
| 64 | 0.240978 | 0.232706 | 0.222610 | 0.220529 | -5.23% | -7.62% | [0, 1, 3, 4, 6, 7] |
| 128 | 0.231969 | 0.245058 | 0.234050 | 0.226257 | -7.67% | +0.90% | [1, 2, 3, 6] |
| 256 | 0.233153 | 0.251074 | 0.243185 | 0.226338 | -9.85% | +4.30% | [0, 5] |
| 512 | 0.238689 | 0.255154 | 0.238049 | 0.236770 | -7.21% | -0.27% | [0, 2, 3, 4, 5, 6, 7] |
| 1024 | 0.250433 | 0.265618 | 0.260722 | 0.258385 | -2.72% | +4.11% | [2, 5, 7] |
| 2048 | 0.351634 | 0.344834 | 0.336658 | 0.336866 | -2.31% | -4.26% | [1, 2, 4, 5] |
| 4096 | 0.554212 | 0.509651 | 0.557189 | 0.496995 | -2.48% | +0.54% | [] |


# Complete modern5wg comparison

Complete same-node source trials; same original benchmark and graph scorer. Modern5WG restores the dedicated input-dispatch role and uses REG96/640/61440 rather than REG128/512/65536. The shared split kernel, static FC2 and graph scorer are identical; split still retunes independently. This is a whole-layout comparison, not an isolated epilogue/scorer ablation. No row minima, drift subtraction, statistical uncertainty estimate or automatic retention decision.

control: all13 rows, ms.

| T | Graph split | Graph Mega | Modern5WG split | Modern5WG Mega | Modern5WG split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.083072 | 0.094865 | 0.080656 | 0.094928 | 0.8497x | +0.07% | -2.91% |
| 2 | 0.116464 | 0.112352 | 0.116624 | 0.112033 | 1.0410x | -0.28% | +0.14% |
| 4 | 0.145297 | 0.128816 | 0.127505 | 0.135777 | 0.9391x | +5.40% | -12.25% |
| 8 | 0.162609 | 0.158017 | 0.162385 | 0.158593 | 1.0239x | +0.36% | -0.14% |
| 16 | 0.171553 | 0.170049 | 0.180945 | 0.173153 | 1.0450x | +1.83% | +5.47% |
| 32 | 0.205457 | 0.203218 | 0.204002 | 0.213362 | 0.9561x | +4.99% | -0.71% |
| 64 | 0.220402 | 0.226849 | 0.240978 | 0.232706 | 1.0355x | +2.58% | +9.34% |
| 128 | 0.237378 | 0.234353 | 0.231969 | 0.245058 | 0.9466x | +4.57% | -2.28% |
| 256 | 0.243361 | 0.242593 | 0.233153 | 0.251074 | 0.9286x | +3.50% | -4.19% |
| 512 | 0.242594 | 0.249826 | 0.238689 | 0.255154 | 0.9355x | +2.13% | -1.61% |
| 1024 | 0.262818 | 0.269169 | 0.250433 | 0.265618 | 0.9428x | -1.32% | -4.71% |
| 2048 | 0.348546 | 0.343330 | 0.351634 | 0.344834 | 1.0197x | +0.44% | +0.89% |
| 4096 | 0.551779 | 0.532003 | 0.554212 | 0.509651 | 1.0874x | -4.20% | +0.44% |

auto: all13 rows, ms.

| T | Graph split | Graph Mega | Modern5WG split | Modern5WG Mega | Modern5WG split/Mega | Mega change | Split change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.077264 | 0.072000 | 0.086481 | 0.087441 | 0.9890x | +21.45% | +11.93% |
| 2 | 0.097249 | 0.098048 | 0.102448 | 0.108656 | 0.9429x | +10.82% | +5.35% |
| 4 | 0.144737 | 0.129265 | 0.143441 | 0.121488 | 1.1807x | -6.02% | -0.90% |
| 8 | 0.163521 | 0.141969 | 0.156209 | 0.150577 | 1.0374x | +6.06% | -4.47% |
| 16 | 0.175505 | 0.159056 | 0.175761 | 0.162480 | 1.0817x | +2.15% | +0.15% |
| 32 | 0.208482 | 0.195649 | 0.203105 | 0.192385 | 1.0557x | -1.67% | -2.58% |
| 64 | 0.223218 | 0.222721 | 0.222610 | 0.220529 | 1.0094x | -0.98% | -0.27% |
| 128 | 0.233537 | 0.226402 | 0.234050 | 0.226257 | 1.0344x | -0.06% | +0.22% |
| 256 | 0.246465 | 0.227042 | 0.243185 | 0.226338 | 1.0744x | -0.31% | -1.33% |
| 512 | 0.236882 | 0.229618 | 0.238049 | 0.236770 | 1.0054x | +3.11% | +0.49% |
| 1024 | 0.259410 | 0.260641 | 0.260722 | 0.258385 | 1.0090x | -0.87% | +0.51% |
| 2048 | 0.348690 | 0.339170 | 0.336658 | 0.336866 | 0.9994x | -0.68% | -3.45% |
| 4096 | 0.553700 | 0.530068 | 0.557189 | 0.496995 | 1.1211x | -6.24% | +0.63% |

Full choices, resource observations and tactic changes are in comparison.json; all104 literal raw values are in raw-latencies.csv.


Decision: retain the preferred dedicated-dispatch five-WG source as the working baseline. The whole-layout comparison improves8/13 auto rows versus same-node graph0d and materially improves4096; fixed improves3/13, and small auto1/2/8 regress21.45/10.82/6.06 percent. This is not an isolated static-epilogue or scorer ablation and not a uniform gain over four WGs. Independent split retuning and movement are preserved explicitly. Current-head Final performance draft is being prepared; earlier live table remains unchanged until the exact new body is reviewed/published.

First16 prefix a9b149 remains uninstalled. Loader original19e3 was preserved after review found analyzer progress on stdout would break JSON parsing. Narrow v2 handoff6fe7c71079f0aebada041d207b52e27af09775410746114260f34021ab85c275 redirects only owner-validation progress to stderr; six CPU tests pass, all original source/package bytes and five tests preserved. New outer pair runner1d7120946614705c3dfda842cff10c21b83da489c3c98e2abb39741b8f54d1ef uses unchanged640 helper, fixedN128 control/candidate first,600s inner/900s outer timeout, actualzero-GPU/REG96 checks, and explicit owned-PGID live-descendant exit proof. Source-only independent review002 passes. No native capture has run at this entry.

Separate register-budget audit found no decoder spills in saved modern binaries: epilogue physical maxima R111/R107, decodeR58, not minimum register proofs. Fixed epi144/control80/dispatch64/decode96+96 candidate d1794ee9 preserves61440 and eliminates decoder donation from epilogue acquisition. Exact two executable AST edits removeDEC80 from decode and changeINC176→144; omission of no-opDEC96 mirrors CUTLASS equality handling and split's unchanged decode allocation. It remains uncompiled and lower priority than first16, not a public tuning knob or combined trial.


Current-head PR Finalperformance was published/read-back verified on draftbd2fa, bodySHA7a59e222414b48d3e5083edee765355742ac532329b3401c7e2669cf441f1989, receiptlogs/pr5019-modern-full13-publication-001.json. The CUDA130table remains byte-identical. No comments.

First16 staging0019a402/effed completed587verified/57newfiles, production unchanged. OriginalN128attempt001PTY58523 returned1; fetch93062closed. Control stopped after10.23s in DSL AST import: unchangedhelper7eb9 recreates the private package object after loaderpreload, so cachedchildmodules remain in sys.modules but dynamic_mainloop is absent fromthe newparent attributes. No codegen/result.json; candidate never ran. Actual ownerbefore/afteridenticalec94/nativefc082, allownedPGID97562membersgone, noGPUapps/nativeworkers. This is a harness module-identity failure, not a kernel or performance rejection. Preserveattempt001; narrow v3 commonhelperparentreuse is being prepared forbotharms with allsealed/noGPU/resourcechecks unchanged and freshattempt002 output.

User steering: do not investigate2048specifically. Focus general-purposeCUDA13.2 techniques; first16dequant overlap, fixedsamepoolregisterallocation and generalhot/coldgraphscoring remain aligned. No shape-specializeddispatch or single-row optimization.


Narrow first16 v3 helper fix frozen79594a24572f5bfe418749095ea2dd440c8ce5ec45c4e524d6c9b122430ce05e: commonhelper50dbe687ffe8b6938fca6038b119124276c59c10ed9b7c9a9d3006d335f24742 reuses alreadyattested privateparent and checksitsfourchildidentities/files. Whole-helper AST differsonlypackageinitialization; loaderdiffersonlyexplicithelperSHA. All12 sourcepayloads/two manifestsunchanged. EightCPUtests/Ruffpass; independentperformance reviewb35f566f passes. Old7eb9plan andfailed001preserved.

Root successor execution_v2 changesonlyv3pins/path/fresh002names; reversingthose literals reproducespreviousreviewedrunner/stagerASTs. Runner8a586e1867fa7623b00d16dab1ed8d08192880930372eb18475839e3835bae3b; stager9ee92f2b3b3690ed445cc5553cedd68966cf2d4d24d58582ff8ca26a70f04695. Stage002PTY16689exit0:591verifiedfiles/28new, exactec94sourceunchanged. NativeN128pair002startedrootPTY34623 withCUDAhidden andsamecomplete modern/nativefc082 owner. No result claimedatthisentry.


### 027. First16 native schedule verified; installed candidate enters numerical validation

Both fresh matched native pairs completed: profiles/first16-modern-ec94-m256n128c2-002 and m256n64c2-002, control/candidate each. Original processes34623/18078 exited0, complete fetches closed, all owned PGIDs gone and before/after source ec94/native fc082 unchanged. Closure cd6899ea2564c104bff93b7fb8459ffaa460a891ca13322fbcfacd1cf803d47b. Combined quality receipt fb05254aeefe87513d285b899aefaa640c294746fc802c0c130bc3e8b9ab9649; audit a02eaf9666126ed605a3dc51193272486474fc86661c48eec8d08c1ec4b1a702. All four REG96/640/STACK0/LOCAL0, unchanged dynamic caps DEC80/DEC80/INC176/DEC64 and exactly two decode WGs. N128 instructions5856→5864; N64 5528→5536. Packed/SF load, conversion, scale, TMEM store, MMA and barrier counts are unchanged. First16 scales before decoded-stage acquire, survives the slow wait, and stores directly from contiguous registers. Second16 remains packed across the wait and scales after the first store. Two packed-word moves replace no BF16 packet gather; extra mask/address instructions remain an eight-instruction cost. FC1 differs only by uniform-register renaming. Raw release/decoded commit and TMEM store completion ordering are preserved. This is native evidence, not numerical or performance evidence.

The ec94→a9 three-file installer a0b39218 completed locally and remotely after preserving and verifying all three original files before any write. Candidate source is a9b149c2a0dae801b2bb709c3c5b0bf13b0908418e3708262a5512551f373bee; shared transform b473a1e0, decoder85808c54, Mega2d53b2c3. Both receipts include full before/after source inventories; remote evidence is separately fetched under logs/cu132-recovery0908c-first16-remote-install-evidence-001. Fresh actual preflight82d31fc453cdfb9ee25a7876782d402b0613058e10f5f410feceda03537f43f3 verifies CUDA13.2/native13.3/direct bb367 and the candidate imports. Published HEADbd2fa/PR body remains the previously validated ec94 result.

Runtime adapter85323ac9b4dc8a33ef6e315308bc8fbaa61e7cb17950d7133eb90d920c1fa097 retains the original12-job commands and full13 loop. Its additional shared-transform provenance observer verifies actual loaded helper/decoder bytes and inherited transform method ownership inside existing resource consensus. Staging776files/38new completed before source install; frozen helpers and predecessor evidence remain exact. Actual host validation passed125 tests,2warnings,2.56s with Torch, GPU hidden and entirely private CPU/JIT/pytest caches; receipt28243e280345b8d9cd761d0354736380e117e6e6aec65b0af2be8824dfe08d76. Same three public host files plus four externally loaded graph ownership cases; source before/after a9 unchanged.

Performance owns numerical process89923, marker FIRST16_VALIDATION_ab24296bda1043dc85dede9ceb7b5e92, original launcher23b2ba35. Resource EP2 and public M256/N128 C2 EP1/EP2 have passed; remaining jobs run sequentially with independent review. This entry does not claim completion or timing. Full13 remains held until all12 plus host admission passes. User steering remains general-purpose CUDA13.2 optimization, no2048-specific work. Separate cold-scoring and fixed epi144/decode96 preparations remain uninstalled; their ec94/nativefc082 admissions must not be reused against currenta9 without an explicit correct successor.


### 028. Separate FC1 alpha load overlap candidate, source only

Read-only source and saved-native audit found a small existing-pattern mismatch: the private W4A16 FC1 epilogue issues its immutable per-expert alpha load after accumulator readiness, while immutable vendor FC1, retained PR4048 split FC1, and current W4A16 FC2 issue it before the wait. On fresh modern N128/N64 controls, actual alpha LDG is at9330/94c0 after TRYWAIT9300/9400 and their slow-path branches. Merely moving pointer arithmetic would not meet the intended overlap; the actual scalar load must move in the native candidate.

Isolated candidate candidates/w4a16_fc1_alpha_before_acc_wait, handoff dd85378265dabc9968a595dbd153f62830d244e8be8408486549a6a41d178c39, patch ee5e460a, changes only one assignment's position. Epilogue604935b5 becomes1131c7e804126d1306d77248dde53f3f5c4b2ea58d7c7254e88217665e65b569. Both agent and independent root AST checks recover the entire original module after moving statement1 back to3. No new operations, buffers, broadcasts, branches, arithmetic associations, hints, stage or role changes are introduced. Ruff and formatting pass. Valid scheduler metadata precedes this method; the alpha input is not MMA-produced data. The same valid/empty tiles perform the same alpha read, with one FP32 scalar potentially live longer across the accumulator wait. The diagnostic FC1 range still begins after the wait; complete-forward timing scope is unchanged.

This differs from the earlier rejected split GEMM2 scheduler-staged alpha experiment, which added shared storage/handshake/read. It remains a small latency-hiding hypothesis: existing accumulator TMEM loads may already overlap much alpha latency. Native code must show actual early LDG, preserved fast/slow-path value, no duplicate load or new locals/CFG/MMA changes, and identical publication ordering. No new harness, native compilation, GPU test, production edit or performance claim. Its one-file dependency is shared by ec94 and first16a9, but no future full-source/native admission is asserted before the running first16 trial finishes.


### 029. Separate scale operand narrowing candidate, source only

The first16 native delta was traced further. Five extra LOP3 AND0xffff instructions correspond to SF byte widening: seven u16-to-u32 temporaries versus two in control. Two extra LEA replace two IMAD one-for-one; one ULEA recomputes the decoded barrier base across acquire/commit; two instructions move packed words. No obvious alternative half-view expression eliminates these costs. The first16 source remains frozen during validation.

A separate shared-utility simplification is saved at candidates/w4a16_scale_operand_u16, handoff6184079aac4788003c70469604883e0eed1fe4633dfe686011a76a507ca3c7c0, patch61602f230d78555c3343eda87636493994587d768e310573b2b3bdd00a5cf978. Utils85808c54 becomes3579088892bcf72027318e039270d5eba7337ab2a19e24291e2b18162ab88368. Preserve the public Uint32 scale argument, pass Uint16(scale) with assembly constraint h, and unpack the same low byte with mov.b16 in both branches. Low8(trunc16(x)) equals low8(x), including shifted words with nonzero upper bits. All conversion/multiply/repack instructions and other helper definitions remain exact. Root independently reversed the five affected lines and recovered the full original file byte for byte.

Local CUTLASS uses the exact mov.b16 {b,_} / =r,h byte-conversion pattern; existing FlashInfer E4M3 helpers use Uint16/h too. The official [NVIDIA inline PTX constraints](https://docs.nvidia.com/cuda/inline-ptx-assembly/index.html) confirm h is 16-bit. This establishes type support, not instruction savings. Static checks pass; no production edit, compilation, numerical test, timing or full-owner admission occurred. Native code must establish whether SF masks disappear without replacement cost, resource regression or changed ordering. Split and Mega both use the helper and require relevant compatibility validation. This candidate remains separate from alpha reordering, register rebalancing and cold scoring.


First16 numerical sequence completed: original89923 exited0, all twelve READY markers and actual remote EXIT=0, no progress errors; all fetches closed. Final summary ea4c43b453a0df37ce01d86e11357794786af4c8e190bda86d135d119663089c, launcher exit c727f7ba866a2a402e2b5bf027e8d5f8bf0e195279dd53520acb691856db27fa. Independent final audit3189025bfb4e2ca893f890e866d13cf9eadf1ceff9862a6f2b1d3adbee3f899b passes all120 public rank-tests/192 public objects,48 lifecycle records (32 nonempty oracles plus16 empty contracts),9 stable plus3 changed-input graph replays, and real EP2 sampler peer-failure/reset/recovery. All250 actual prelaunch observations have REG96/640/two decode WGs/61440/local0 and exact shared-transform/MRO/decoder identity. Actual host125 result28243e28 also passes. Source remainsa9, actual preflight82d31, final native inventory unchangedfc082.

Root approved original full13 launcher c9d79dd32052c6f8e0ad5c5cd8a4bcd6e821b4840ec73f92015348b5819eec42 with that exact completed summary. The planned fresh live idle/source/native and dry-run checks precede execution. Performance retains the exclusive remote/source/native/GPU window. This entry does not claim a timing result or source retention. Sealed saved analyzer handoff596dd7e4fd49da06e53b9b0e4acb687e648f8a4c63b2a68e0408246e01c9ed12 retains original complete raw/config/choice/ranking validators and requires the host125 proof; paired comparator handles all104 raw values across ec94 and a9 with unchanged metric and explicit changed shared split source. No PR table change before a retained result.


First16 full13 started under performance-owned PTY73372, marker FIRST16_FULL13_46ea6557508a4fc1a3b4c4115cc0bc28. Fresh live source/native/summary/host/idle admission passes before the original dry plan and fixed CONTROL→auto16 execution. Candidate remains exacta9. No timing result is claimed yet; no competing profile, native compile or source change runs during primary timing.


### 030. Complete first16 full13; publication unchanged; private UInt16/h native trial begins

Recorded 2026-09-09T00:18:45.088973+00:00. The first16 a9 trial has completed both original primary benchmark arms and all prior numerical/host gates. It is **not promoted**. Published draftPR5019 remains commit `bd2fa61c82caed9b5237aea00db5ce00436beb41`, runtime ec94, with the unchanged current-head performance body SHA `7a59e222414b48d3e5083edee765355742ac532329b3401c7e2669cf441f1989` and unchanged historical CUDA13.0 table. This entry is local evidence/checkpoint work only; no production, harness, memory, PR or remote change is made by its author.

**Execution and exact owner.** Original full13 PTY73372, marker `FIRST16_FULL13_46ea6557508a4fc1a3b4c4115cc0bc28`, exited0. Final ten-path fetch41738, postflight80275 and idle fetch40427 exited0. The complete run is [cu132-recovery0908c-first16-full13-001](logs/cu132-recovery0908c-first16-full13-001/stack-manifest.json), source `a9b149c2a0dae801b2bb709c3c5b0bf13b0908418e3708262a5512551f373bee`. Manifest SHA `0f7305b5c32b0ca8eb420f0132f928846e4544e7ba3bbcca3e60c9d172c9a059`, results SHA `9fe07941a18556743020df386da1ff26cd44ffdfe54efa5c143a1b5a07b4efeb`, final native inventory SHA `079f6f7a3fa1569c4b4ca45d3769165f7be7d4f2ad1991eafaca06ff39cf3a8f`. The source is the exact ec94 three-file successor: shared transform b473a1e0, decoder utility85808c54 and private Mega2d53b2c3. Graph scorer6d7, five warpgroups, dedicated dispatch, exactly two decode groups, REG96/640/pool61440 and vendor bytes stay unchanged.

**Validation and saved proof.** The original twelve-job summary `ea4c43b453a0df37ce01d86e11357794786af4c8e190bda86d135d119663089c` and independent numerical audit `3189025bfb4e2ca893f890e866d13cf9eadf1ceff9862a6f2b1d3adbee3f899b` retain all120 public rank-tests/192 objects,48 lifecycle candidate records (32 nonempty oracles and16 empty contracts),9 stable+3 changed-input graph replays, sampler peer-capture failure/reset/recovery, and all250 original prelaunch observations. Every resource observation is REG96/640/two decode groups/61440/local0 with exact shared-transform/decoder/MRO proof. Actual host125 passed, two warnings,2.56s with hidden GPU visibility/private caches; result SHA `28243e280345b8d9cd761d0354736380e117e6e6aec65b0af2be8824dfe08d76`. These are actual first16 outcomes, not inherited new-source numerical claims.

The [canonical strict report](logs/cu132-recovery0908c-first16-full13-001-analysis/comparison.json) SHA `faa1bd1e0be30e6643c52c83c58ca804920acb7a0a581ff3dc39cd0fbd4866ec` is byte-identical to the [independent original-analyzer rerun](logs/cu132-recovery0908c-first16-full13-independent-001/comparison.json). Analyzer handoff596dd7e4 verifies 52 literal raw values,208 split selections,208 compiled records,104 actual returned auto choices,13 complete16-candidate rankings,10 final capacity entries, source/helper/native identity, host125 and completed ec94→all12 first16→full13 native-cache lineage. All208 production compiled objects have local0 and the original exact resource/shared-MRO contract. The10 capacity buckets do not replace the104 actual returned choices; T1/2/4/8 share the capacity1 cache bucket.

**Original timing scope.** Same hu-pdx-133, eight B300 SM103, `nvcr.io/nvidia/pytorch:26.05-py3`, systemCUDA13.2.78, driver590.48.01, image Torch2.12.0a0+5aff3928d8.nv26.05, DSL4.7.1/native13.3.27 direct bb367. Workload H7168/I2048/E256/top8/EP8, global tokens1–4096, three warmups and100 cold-L2 CUPTI one-forward-graph samples. Metric is median of per-iteration rank-MAX full-forward GPU activity span; split disables fused finalize and retunes independently. Fixed CONTROL uses M256/N128/K256/C2/F4/epi, group512/atomic/epi flags2,4; auto searches the unchanged16 candidates. The hot private graph-event tuning score is distinct from primary CUPTI. No tolerance, timer, control, catalog or resource gate was weakened.

**All26 paired raw timing rows.** Each split and Mega value below retains the original six-decimal millisecond text (52 raw values total). Ratios are derived; choices are the actual returned winners, with the full dictionaries and all-rank equality in the strict report. `epi` means epilogue return; `reuse` means reused-dispatch return. Other fixed fields remain as stated above.

| Arm | Global tokens | Split ms | Mega ms | Split / Mega | Actual choice |
| --- | ---: | ---: | ---: | ---: | --- |
| control | 1 | 0.067456 | 0.093536 | 0.7212x | M256/N128, C2, F4, epi |
| control | 2 | 0.098817 | 0.119937 | 0.8239x | M256/N128, C2, F4, epi |
| control | 4 | 0.144337 | 0.138449 | 1.0425x | M256/N128, C2, F4, epi |
| control | 8 | 0.162321 | 0.156881 | 1.0347x | M256/N128, C2, F4, epi |
| control | 16 | 0.168049 | 0.176033 | 0.9546x | M256/N128, C2, F4, epi |
| control | 32 | 0.204354 | 0.216049 | 0.9459x | M256/N128, C2, F4, epi |
| control | 64 | 0.223073 | 0.225313 | 0.9901x | M256/N128, C2, F4, epi |
| control | 128 | 0.228897 | 0.245489 | 0.9324x | M256/N128, C2, F4, epi |
| control | 256 | 0.244737 | 0.247858 | 0.9874x | M256/N128, C2, F4, epi |
| control | 512 | 0.243073 | 0.253298 | 0.9596x | M256/N128, C2, F4, epi |
| control | 1024 | 0.260674 | 0.263025 | 0.9911x | M256/N128, C2, F4, epi |
| control | 2048 | 0.336674 | 0.344162 | 0.9782x | M256/N128, C2, F4, epi |
| control | 4096 | 0.553940 | 0.514547 | 1.0766x | M256/N128, C2, F4, epi |
| auto | 1 | 0.083600 | 0.088673 | 0.9428x | M256/N64, C2, F8, epi |
| auto | 2 | 0.098657 | 0.105440 | 0.9357x | M128/N64, C2, F8, epi |
| auto | 4 | 0.128321 | 0.128577 | 0.9980x | M128/N64, C1, F4, epi |
| auto | 8 | 0.162913 | 0.150145 | 1.0850x | M256/N64, C2, F4, epi |
| auto | 16 | 0.179377 | 0.163554 | 1.0967x | M256/N64, C2, F8, epi |
| auto | 32 | 0.200369 | 0.197809 | 1.0129x | M256/N64, C2, F8, epi |
| auto | 64 | 0.209921 | 0.221089 | 0.9495x | M256/N64, C2, F4, epi |
| auto | 128 | 0.234161 | 0.217345 | 1.0774x | M256/N64, C2, F4, epi |
| auto | 256 | 0.238337 | 0.230946 | 1.0320x | M256/N64, C2, F4, epi |
| auto | 512 | 0.236978 | 0.238594 | 0.9932x | M256/N64, C2, F8, epi |
| auto | 1024 | 0.269010 | 0.250353 | 1.0745x | M256/N64, C2, F4, epi |
| auto | 2048 | 0.345907 | 0.334706 | 1.0335x | M256/N128, C2, F8, reuse |
| auto | 4096 | 0.548244 | 0.498308 | 1.1002x | M256/N128, C2, F4, reuse |

**Complete ec94→a9 comparison.** Both arms and every original value are preserved in [comparison.json](logs/cu132-recovery0908c-modern5wg-vs-first16-full13-001-analysis/comparison.json), [two whole-grid tables](logs/cu132-recovery0908c-modern5wg-vs-first16-full13-001-analysis/README.md) and [all104 raw values](logs/cu132-recovery0908c-modern5wg-vs-first16-full13-001-analysis/raw-latencies.csv). Independent reconstruction at [independent-verification.json](logs/cu132-recovery0908c-modern5wg-vs-first16-full13-independent-001/independent-verification.json), SHA `41e771f15cd2de50ac2a377c3761bb2c30fcf66abf6dfdfb48dddb41f704a521`, agrees on every comparison payload, both tables and complete CSV. Across the two sources this retains104 raw values,416 split records,416 compiled records,208 actual returned choices and26 rankings; all416 objects have local0.

Fixed Mega is faster in7/13 rows and slower in6/13; geometric mean a9/ec94 latency is1.002937057456751 (+0.2937%). Auto is faster in5/13 and slower in8/13; geometric mean is1.0020778016064247 (+0.2078%). Fixed actual dictionaries match on all104 rank-shape pairs. Nine returned auto choices change; identical auto dictionaries occur at T16/32/128/4096. Split tactic selections change on40 fixed and35 auto rank-shape pairs. No cross-source row has identical full config/compiled/gate metadata because the shared implementation differs. This does not show a broad speedup or isolate first-fragment overlap: shared split transform/utility bytes changed and split retunes; separate sequential arms do not establish uncertainty or remove context effects. Keep all regressions, no row minima or drift subtraction, and no 2048-specific optimization. **No promotion decision is made; ec94 remains the published baseline.**

**Current completed native ownership and release.** Compared with modern's final fc082 inventory, only `flashinfer_jit.log` changes,233,873→279,009 bytes; all75 other entries remain equal. The log stays included in the exact native snapshot and is not excluded from ownership. The actual [idle proof](logs/cu132-recovery0908c-first16-full13-idle-001.json), SHA `d90b7d8fa9a2c0ea6b8ab19378d375c0b758f9ec83d151a72c8eff490aedaf54`, records 2026-09-09T00:02:38.383924Z with exact a9/helper source, no GPU/compiler workers and live native inventory079f. [Window release](logs/cu132-recovery0908c-first16-full13-window-release-001.json), SHA `45f0625b990a893e81631bb87592b1a1966df7af6ae7e0f68a155e2063112996`, records00:03:36.651626Z, all owned sessions closed, and returns exclusive scheduling to root. Older ec94/fc082-only adapters cannot silently admit this current owner.

**Private UInt16/h trial, pending native result.** Root staged the exact reviewed successor. [Staging receipt](logs/cu132-recovery0908c-scale-u16-native-stage-001.json) SHA `9e4e26d0fbea3176817ab7590d0aa8c6ef854fc8bff8bd09fa72eac1b52fb849` verifies824 files,44 created/780 exact existing/no concurrent skips, production source before=after a9, and zero native imports/compiles/GPU operations during staging. The extra file over the reviewed823-file local plan is the completed first16 strict report. Stager8bf9262b, outer runnerf989a7fc and bootstrap handoff21486808 bind the actual completed first16 manifest/results/native079f with three explicit required SHA arguments, sealed analyzer596dd7e4, selected utility/shared/private-Mega identities and unchanged compile helper50dbe. The source-only stager review is [stager-review.json](candidates/w4a16_scale_operand_u16_compatibility_review/stager-review.json), SHA `4d668cc1c1505d460d2550122ec2f473f9c2af453e2ae80b5a7760b14a132a32`.

At this checkpoint root reports private N128 control/candidate native pair PTY19931 running, using utility858→357 in isolated packages and production a9 untouched. Root owns every remote/source/GPU operation. This entry claims no native code-quality result, compile completion, numerical outcome or speedup for UInt16/h. N64 and the minimal runtime successor remain contingent on actual quality review. The bounded compatibility plan is the existing14-case split W4A16 class and Mega reference schedules at EP1/EP2, both returns and N128/N64 observers; forced64/all-code bitwise decode coverage remains an explicit gap. No CUDA13.0 work, broad unchanged catalog/lifecycle rerun, new public knob or combined alpha/register/cold-scorer experiment is authorized by this record.


Entry030 follow-up from root: both private UInt16/h native pairs are now reported complete. N128 is admitted as a changed-schedule trial; N64 exited0 and fetch44547 is running, with actual N64 quality review still pending. No instruction-count, numerical or performance result is inferred here. Root retains every remote/source operation. The minimal runtime successor is being prepared separately at `candidates/cuda132_recovery_0908c/scale_operand_u16`, prospective one-file source `20ae8493dc0374efb67c6695fda4bb8f424b6be868bd27101fb2312238b1ad4f`, source manifest SHA `0f738de118681c6d2c358d7f57f49e6b27ae4fd38e8234dadb620b974fc24764`; independent review waits for its freeze. It is not installed or executed by this checkpoint.


### 031. UInt16/h native review complete; one-file runtime installed; five focused jobs authorized

Recorded 2026-09-09T00:39:15.783071+00:00. Root accepted the completed N128 and N64 private native pairs for a numerical/full13 trial, explicitly allowing the changed generated schedule. The published draft remains `bd2fa61c82caed9b5237aea00db5ce00436beb41` / ec94, with its existing PR body and performance table unchanged. Neither first16 a9 nor the new UInt16/h source is promoted. Integration edits only this ledger and `CURRENT_STATE.md`; frozen artifacts, production, harnesses, memory and PR files are untouched by this documentation update.

**Completed native evidence.** The [native review](candidates/w4a16_scale_operand_u16_native_review_a9/README.md) and [receipt](candidates/w4a16_scale_operand_u16_native_review_a9/receipt.json), SHA `a3c3ac3483e7d09ea1bc94f82ccfe2d76fcb7f163582062903dfb3ce8e9b8e65`, cover both completed control/candidate pairs: `profiles/scale-u16-first16-a9-m256n128c2-001` and `profiles/scale-u16-first16-a9-m256n64c2-001`. Root's [independent four-capture check](logs/cu132-scale-u16-native-four-capture-check-001.json), SHA `21e3f1bf1ea8f74ebf8f7f9f893ad3001b45ba9e966fedaea84f186a0b25e368`, agrees. Each arm has one real sealed compilation, zero compiled launches/device allocations/collective initializations, a successful owned-process exit, and unchanged source/native identity before/after. Actual native remains bb367 with common helper50dbe, five warpgroups, exactly two decode groups, initial REG96, 640 threads and pool61440; dynamic caps remain control80/decode80/epilogue176/dispatch64.

| Pair | Control static instructions | Candidate static instructions | FC1 body | FC2 body | Both-arm resources |
| --- | ---: | ---: | --- | --- | --- |
| M256/N128/C2 | 5864 | 5856 | 223 → 223 | 233 → 227 | REG96, 640 threads, STACK0, LOCAL0 |
| M256/N64/C2 | 5536 | 5528 | 223 → 223 | 233 → 227 | REG96, 640 threads, STACK0, LOCAL0 |

These body counts span raw-ready wait through the last of eight STTM.x8 stores and are static counts, not cycles. Both geometries remove eight instructions overall. The u16→u32 PTX conversions drop 7→0, but native masking remains: FC2 replaces seven 0xffff masks with seven 0xff masks and changes scale replication. Packed/SF loads, conversions, HMUL2/HFMA2, TMEM stores and MMA counts remain unchanged; there are no added LDL/STL sites or MMA copies. The source low8(trunc16(x)) contract and selected utility/shared/private-Mega identities are preserved.

**Changed schedule is explicit.** In both candidates the first sixteen BF16 values are fully scaled before decoded-stage acquire and survive its slow path. The second x16 decode now precedes the first TMEM store, unlike control; three x16 payloads are completed before that store, versus one in control. The first payload therefore spans 92 intervening static instruction slots instead of 47. Those are source-correlated intervals, not latency or full simultaneous-liveness measurements. No TMEM store precedes acquire, and final store fence → raw release → decoded publication remains correct. The native review accepts this as a changed-schedule trial; fewer static instructions do not demonstrate throughput improvement or preserve the prior first-store interleaving.

**Frozen minimal runtime.** Adapter [scale_operand_u16](candidates/cuda132_recovery_0908c/scale_operand_u16/README.md), handoff SHA `ec42f9d917829c68ade23096b6659aba590bf971de21f1a3281b6f42e303f503`, upload SHA `525e5cfb3a09491c1e69486c5b785f87b8a1121eb8bad941e4ff133ec1a7396a`, passed bounded independent review. The handoff has 26 entries, the upload map has 25 entries, and the saved/helper dependency map has 985 entries. That map includes all 774 historical analyzer dependencies, all 12 first16 analyzer handoff files, and all 964 actual completed-owner evidence entries. The five unchanged payloads (resource gate, geometry observer, compiled capture, graph scoring and preflight) remain byte-identical to first16; the shared observer changes only the decoder SHA. The actual compiled validator and original primary fixed→auto phase loop are AST-identical. Six focused CPU checks are saved as synthetic fixture/admission checks, not candidate GPU results. Installer SHA `1d2d588ce2157a68c97d250f9a9919e6adf357bda811eff2d41533702720f08d` retains the original strict backup-before-write body.

**Actual runtime staging and installation.** [Runtime staging receipt](logs/cu132-recovery0908c-scale-u16-runtime-stage-001.json), SHA `be5811709863710cd856beb8c3b671af391171a3b5b8bf224cbbad511b0ce92c`, verifies 1,013 files: 34 created, 979 exact existing and no concurrent skips. This is separate from entry030's 824-file private native staging. The production source remained a9 throughout staging, with zero native imports, compilations, GPU operations or production writes in that step.

Root then applied exactly one file locally and remotely: decoder utility `85808c54a149721ba37071794e79c8ea0d19bfbf6817e485e7ec00d64ebf8104` → `3579088892bcf72027318e039270d5eba7337ab2a19e24291e2b18162ab88368`. Full source transitions from completed `a9b149c2a0dae801b2bb709c3c5b0bf13b0908418e3708262a5512551f373bee` to candidate `20ae8493dc0374efb67c6695fda4bb8f424b6be868bd27101fb2312238b1ad4f`; all other 1,571 source files, 337 required paths and four source helpers are unchanged. Source manifest SHA is `0f738de118681c6d2c358d7f57f49e6b27ae4fd38e8234dadb620b974fc24764`. Public Uint32 ABI, decode arithmetic, shared transform b473, private Mega2d53, static epilogue604935, graph scorer6d7, vendor source and native C++ dependencies remain unchanged from a9.

The [local installation result](logs/cu132-recovery0908c-scale-u16-from-first16-install-001/result.json), SHA `ed802a2d0e5473ae8cc40335674555d4cf2800e7865dbca40650cd2bcb2d1a19`, is kept separately from the [remote installation result](logs/cu132-scale-u16-remote-install-evidence-001/logs/cu132-recovery0908c-scale-u16-from-first16-install-001/result.json), SHA `c6f8677541b2bf837718b257f6f778e4d4a957145385cef2fd188da75bca37f1`. Both report installed status, exact full before/after source inventories and a verified old-utility backup before mutation. Integration independently read both receipts and checked each saved backup against the old858 hash; these are not remote operations by integration.

**Fresh actual preflight and ownership.** [Preflight001](logs/cu132-recovery0908c-scale-u16-preflight-001.json), SHA `d62856191c25fc6009658b06475b52733c35ec6d027bbc14fc3bc76fd4720bb0`, confirms system CUDA13.2, image Torch2.12.0a0+5aff3928d8.nv26.05, DSL4.7.1/native13.3/directTrue, actual native extension bb367, decoder357 and unchanged private Mega2d53. The accepted container/node remain `nvcr.io/nvidia/pytorch:26.05-py3` on hu-pdx-133, eight B300, driver590.48.01. This is actual new-source import/native admission, not numerical validation.

The immediate completed native owner is still first16 full13: manifest `0f7305b5c32b0ca8eb420f0132f928846e4544e7ba3bbcca3e60c9d172c9a059`, results `9fe07941a18556743020df386da1ff26cd44ffdfe54efa5c143a1b5a07b4efeb`, final native inventory `079f6f7a3fa1569c4b4ca45d3769165f7be7d4f2ad1991eafaca06ff39cf3a8f`. The first job must match that complete inventory including JIT-log bytes. Later jobs require the immediately preceding completed native snapshot and fresh DSL/driver caches; full13 must follow the completed five-job chain with fresh knob/tactic outputs. No restored or missing-cache owner is invented.

**Window and pending validation.** Performance now owns the exclusive GPU/native/source window and is authorized to launch five existing-fixture jobs: the 14-case split W4A16 class on one GPU, then the Mega reference schedule at M256/N128/C2 and M256/N64/C2, each EP1 and EP2 with both return modes. Expected Mega coverage is 12 rank-tests and 48 compiled objects, each subject to the unchanged actual REG96/640/two-decode/pool61440 gate and nested shared/MRO identity. At this checkpoint no launch message has arrived and no numerical job is claimed complete. No new host, lifecycle, catalog or sampler rerun is added; explicit forced64 and all-code bitwise decoder coverage remain outside this subset. Original full13 fixed CONTROL→auto16 across all 13 token counts, 100 cold-L2 CUPTI samples, unchanged tolerances and timer, is held until all five actual jobs and source/native checks pass. Root and performance coordinate the window; integration remains local and read-only outside these two documentation files.

**Separate source-only register rebalance.** [w4a16_first16_epi144_decode96](candidates/w4a16_first16_epi144_decode96/README.md), handoff `258b31a1c5371b543d5e6456a785148662fdf96a6ac2689a6a14618421f0bf1e`, is an independent uninstalled proposal. It starts from private Mega kernel2d53 shared by a9 and20ae and proposes kernel `87b5881ea9b890a25af0c0bb38ae0a9e37cc2b0c9b32726eb3d4cc1d0d5f48c2`. Exactly two executable edits remove decode decrease80 and change epilogue increase176→144. Both decode groups retain initial96, control remains80, dedicated dispatch64, and five WGs / two decode WGs / 640 threads / pool61440 stay fixed. Control donates 2,048 registers and dispatch donates 4,096, exactly covering the epilogue's 6,144-register increase; this removes a possible decode-donation dependency at startup, not a steady-state pipeline wait. The proposal has source/AST/patch checks and saved register-index observations only. Register maxima R111/R107 do not prove minimum liveness or a spill-free lower cap. It declares no owner, native harness, compile, installation, numerical result or timing, and is not combined into the active UInt16/h trial. Cold scoring and FC1 alpha relocation remain separate. No promotion, PR change, CUDA13.0 restart or shape-specific optimization follows from this entry.


Entry031 launch update: performance reports the numerical launcher active under PTY58036, marker `SCALE_U16_VALIDATION_3eedd0f9cced42fab9d876ec3b6f047a`, with exact source20ae, preflight d62856191c25fc6009658b06475b52733c35ec6d027bbc14fc3bc76fd4720bb0 and frozen runtime ec42. Live source/native/idle and dry-plan checks run before split14, followed by the four reference jobs. No case or job completion is claimed at this update. Performance owns execution and prompt completed-folder fetches; full13 remains held until numerical completion review.


Entry031 numerical completion and primary launch: original PTY58036 exited0 with all five ordered READY paths, no progress errors, and the actual `SCALE_U16_VALIDATION_3eedd0f9cced42fab9d876ec3b6f047a_EXIT=0` marker. Final fetch89823 closed. Summary SHA `5fb982bcde92d8c094c3567f1df0b83a94d276c8a35fc544960af387d5843fcd`; launcher receipt SHA `af6cc96349997ad47b14d0f72d778f9fc309f7c526df3e577ae9b600fe4a45e4`. [Independent final audit](logs/cu132-recovery0908c-scale-u16-numerics-independent-001/audit-final.json), SHA `280faa17fbe907ffae72889c8d7f9327b28f5dd0b9cbabcfba17774d683b55fd`, passes all 14 split calls, 42 setup/call/teardown reports, 28 before/after loaded shared-b473/utils357 aliases, 12 Mega rank-tests and 48 actual REG96/640/two-decode/pool61440 resource records, all local0 with the nested MRO proof. Exact source20ae, runtime ec42, preflight d628, complete helper/provenance maps and immediate native ownership are retained; all five native-after snapshots remain079f. The local audit uses exact AST-sliced saved split validators to avoid importing pytest; an initial local/remote path-mapping assertion was corrected with its failed log preserved. No GPU test was rerun, no frozen helper was changed, and no fresh host125/lifecycle/catalog/sampler or exhaustive-bit proof is implied. Root independently verified the final audit and all 1,071 evidence hashes.

Root authorized the original held full13 launcher521e5 using that exact completed summary. Performance reports actual PTY95530 active, marker `SCALE_U16_FULL13_28cb8d0e37424d169326fe429b37764c`, after successful live source/native/idle guards and dry plan. Fixed CONTROL is running; its first T1 split row was emitted, and initial metadata fetch7628 exited0. This update claims neither a complete arm nor final performance result. The sequence remains original fixed CONTROL then auto16, all 13 token counts and 100 cold-L2 CUPTI samples. Performance owns exclusive runtime/fetch, integration remains local, production source20ae stays frozen, and published draft bd2fa/ec94 remains unchanged without promotion.

The prospective saved-result reader is frozen separately at `candidates/cuda132_recovery_0908c/scale_operand_u16_analysis`, handoff `4228bebba61bfa2cbdf92461aa682b0423b3f70b1709587ceea4959b50872c57`, reader SHA `6e26d98b5abf39e9f820f904332e6479f3571de111ae03676e23875cc0abfd60`. Five CPU checks and an actual saved five-job numerical read passed; independent implementation review is pending. No complete20ae full13 evidence exists at this checkpoint, and no repeated numerical execution is needed for that review.


Entry031 interruption and review update, recorded 2026-09-09T01:04:55Z. The scale-u16 full13 run is **incomplete**. [Failure receipt](logs/cu132-recovery0908c-scale-u16-full13-interruption-001.json), SHA `075b0e5adb7262db47dc42f268513590e9ad6dd461fcfa63e9818f3a4cab9363`, records original remote child exit137, local wrapper exit1, and no completion marker for PTY95530 / `SCALE_U16_FULL13_28cb8d0e37424d169326fe429b37764c`. [Launcher receipt](logs/cu132-recovery0908c-scale-u16-full13-001.launcher-exit.json), SHA `6ed4beac43247e8c54e424a8171315379c32f3c2056b7f40af33c73cd805bec8`, explicitly has success=false and completed_full13=false. Zero complete performance arms were fetched. The last read-only status reported 17 fixed raw rows and 64 compiled records for tokens1–128, without a benchmark traceback; only three literal raw strings survive in the separate partial-observations record. These observations do not constitute a completed timing arm, comparison table, resource census or performance result.

Bounded checks at 00:57:23–24Z show the named devbox absent from SSH lookup and an empty explicit c2/ziangli devbox inventory. [Checks receipt](logs/cu132-recovery0908c-scale-u16-full13-interruption-001-checks.json), SHA `7757823cc2dcbecd8aeed49cdb84e442eb90e71ae58056263ef09a53f554b0ae`, retains both original command outputs. No lifecycle/reclamation event was obtained; the cause is unknown, and exit137 alone does not establish OOM or reclamation. All performance-owned local sessions and absence checks are closed. No post-run GPU-idle, source or native-after state is available, and no new20ae completed native owner exists. Integration verified the failure receipt's thirteen evidence hashes locally without a remote/native operation.

The initial full13 manifest SHA `8c2bf586d60cfa811ac04a4598867370909796c16e1d91ec891f5734bbaecf4f`, native-before079f, dry plan SHA `4c6ba60a408f63bd2d04f12ecf78a96c8db1553c99b5655d0928ef8ba618049e` and prelaunch idle SHA `e7481862ff0dea853785e2ae10270e343225436c13574bee03ef8b8ab24ebc4c` remain saved. All five numerical jobs, summary5fb982bc, final independent audit280faa17 and their original successful launcher receipt remain complete and valid. Earlier completed ec94 and first16 tables, exact source/native records, and archived evidence remain intact. The unavailable node's cache directories cannot be assumed present or reused on a replacement solely from historical snapshots. Local production remains20ae, while the last verified remote20ae installation is historical evidence. Published bd2fa/ec94 and the PR body remain unchanged; neither a9 nor20ae is promoted.

The bounded saved-reader review is complete. All seven files in frozen handoff4228bebb match, and six original helper functions plus the entire completed fixed/auto validation and comparison body have ASTs identical to the first16 analyzer. Exact20ae/d628/ec42 admission, saved first16 owner079f, immediate five-job native lineage, pure split AST validators, original640 shared/MRO resource checks, actual104 returned choices, thirteen rankings and ten capacity buckets are retained. Historical host125 and twelve-job lifecycle/public evidence are correctly labeled as predecessor evidence only. Two narrow corrections were sent to root/design without editing the frozen reader: require the final numerical sequence/launcher success, exit0, exact five paths and actual completion markers; and describe the hot scorer as the staged W4A16 wrapper plus reducer, excluding public staging/routing preparation. The original primary cold-L2 CUPTI metric and math are unchanged. No complete20ae full13 reader pass is claimed.

Root is requesting a replacement0909a box and performance is preparing a narrow recovery adapter. Integration's next scope is source-only independent review when that adapter is frozen; it owns no provisioning, remote, native or GPU action. Recovery must establish its actual environment/source/cache admission and keep this failed attempt separate. No CUDA13.0 restart, source promotion, PR edit or shape-specific investigation follows from this interruption.


### 032. Optional sample logger published; calibration pending; replacement setup begins

Recorded 2026-09-09T01:33:48Z. The user requested faster experiment iteration by reducing samples per point while always retaining the complete 1–4096 token grid. Root committed and pushed only the optional benchmark logger as `50ff0abf962d79877eb2fe4b6d32a7763915e8e7`. [Saved public PR read](logs/pr5019-after-timing-logger-push-001.json) confirms that head and draft=true; push98605 exited0. The three experimental shared-kernel, utility and private-Mega files remain unchanged and uncommitted. No first16 or UInt16/h kernel proposal was promoted. Retained performance remains the earlier complete bd2fa/ec94 measurement; the historical CUDA13.0 table remains unchanged.

**Optional logging and exact source.** The isolated [logger artifact](candidates/w4a16_benchmark_timing_samples_0909/README.md), handoff `24bec9a87a0cd53ca4c721218899611359ff4dcab54a68ccd84ce34aea04a095`, proposes only `benchmarks/bench_cute_dsl_moe_distributed.py`, before SHA `b4e845f3b43805e8056be2ac32dc87c452bed8211bfe612f74b04feb65681a09` and committed after SHA `0f7765463d06e93a8998cfcf6f79b7a793e182c9018d3eb3e9649d38436b5454`. Patch SHA `0d7a69b9a37399571232e25ad6cbf2c60c15f59ae7474ff6935e68f7cf2bd5ff`. `--log-timing-samples` defaults off; `--iters` defaults to 100; the default 13 token counts and both existing timers remain unchanged. Rank zero prints the existing ordered post-rank-MAX sample array in milliseconds, token count, existing profile label, warmup/requested/actual count, graph/cold-L2 settings, timer and a scoped host wall interval. It prints only after measurement; the original median remains the result. No additional GPU synchronization, collective, kernel or replay is introduced, and profiler paths return before logging.

The CUPTI wall interval brackets the unchanged `bench_gpu_time` call, including its internal graph preparation, estimate runs, flushes, activity processing and rank reduction. It excludes prior case compilation/autotuning, external warmup, import and JSON output; it is not pure 100-sample execution time. The event interval covers its existing optional graph capture and sampling loop. Both wall values are rank-zero host elapsed time, not a new distributed maximum. Four [artifact-only CPU checks](candidates/w4a16_benchmark_timing_samples_0909/cpu-checks.log) pass with mocked device boundaries, including disabled/default equivalence, both timers with graph on/off, rank-one silence, profiler equivalence and exact timed-call/reduction ASTs. An independent source review confirms CUPTI indexwise MAX and the event path's original all-reduce MAX. Ruff and formatting pass. Root reports all applicable changed-benchmark pre-commit hooks passed during commit; mypy skipped this benchmark path. There is no standalone hook log, fresh GPU logging proof or sample array yet.

Because the benchmark participates in the full inventory, modern ec94 plus this exact logger has source `38870d4bf87aefb77deb3d9a63b09bf1cde4d99e077b7e71ad5a0d8bfe3bf296`. The active UInt16/h20ae plus logger has source `e3590c2f766a4e1c635e45d49471579394190e38acdb8fdabeef2dafb8963321`, independently recomputed and verified by root's [active-source receipt](logs/timing-logger-active-source-001.json), SHA `3c504f641c71fe89e2216fe8cbe56edf36f0d2abb02faec5effcc21540a26750`. Both retain 1,572 source files/337 required paths. No adapter may silently admit the modified benchmark under ec94 or20ae's old full-source ID. These identifiers describe source, not a new numerical or timing outcome.

**Calibration scope.** Root's stdlib [sample analyzer](candidates/w4a16_benchmark_iteration_budget/analyze_samples.py) accepts one complete 13-point split/Mega arm, rejects missing/duplicate points, and compares predetermined first 20/30/50 medians plus every contiguous window to each case's 100-sample median. It preserves signed prefix deviations and absolute rolling-window p95/max deviations; windows overlap and are not confidence intervals. A complete source fixed/auto pair would provide 52 case arrays, each with 100 samples. The logger fields and calculation direction passed bounded source review. Actual sample arrays are unavailable from older runs because their benchmark retained only medians. Neither 30 nor 50 samples is calibrated yet; shorter-run execution and between-run drift are not established by within-run subsampling. No row minima or point-specific sample policy is proposed. The cheap additional per-case metric is a separately proposed host interval around the existing benchmark-function call; subtracting timer wall would yield setup/warmup/teardown residual, not a compiler-only or autotuning-only attribution. It was not added in this commit.

**Unpublished PR-body update.** Integration updated only the local `PR_BODY.md` and `PR_BODY-current-modern-full13.md` drafts to describe default off/default 100 logging, all four named CPU results with the complete saved output, applicable hook results and pending GPU logging. Both drafts have SHA `0d166747e2fb87f40c89b5149d9603ee305d0bf3ddb63301fee6f025bcf9672d` for root's later publication. The autotune description now names the staged W4A16 wrapper plus reducer and excludes public input staging/routing preparation; primary public full-forward CUPTI scope is unchanged. The entire Final performance section remains byte-identical with SHA `a45392899d71ef959481f87ca7bab337ce88a705248340a4abc4962906f5d471`, including raw 13-point tables, choices, regressions and retained bd2fa/6315 provenance. CUDA13.0 reproduction details and template content are preserved. Integration made no GitHub write.

**Completed source-only FC1 proposal.** [FC1 first-x16 predecode](candidates/w4a16_fc1_first16_predecode_20ae/README.md), handoff `ef94e29841f26a9afbf21c5b4f7b158c7b037a00f5ea2a14e9687c795364b2c0`, is prepared against pre-logger20ae and remains unapplied. It proposes shared kernel b473→eb7a13a9 and private Mega2d53→a1e1cb65, with utility357 unchanged. FC1 keeps fragment128 while copying only its first packed32 chunk and decoding the first x16 block before decoded-stage acquire. The remaining first-fragment chunks follow acquire; no TMEM store moves before it, and raw-state probe/release/publication ordering is retained. FC2 true/32 and default shared behavior are constexpr-AST equivalent. Twelve logical operation cases across 32/64/128 extents and four fragment counts pass source proofs. These checks do not execute CuTe layouts, compile native code, validate numerics or show a speedup. Five warpgroups, two decode groups, caps, stage fitting and public catalog are unchanged. Alpha-before-wait, register rebalancing and cold scoring remain separate proposals.

**Preserved analyzer correction.** New [scale-u16 saved readerV2](candidates/cuda132_recovery_0908c/scale_operand_u16_analysis_v2/README.md), handoff `b67ed0614ab7f409407e7c8b8f433d54a8bc5b9df338df5e80a93e72cc446784`, preserves the original 4228 draft and adds the exact final numerical audit 280faa17, launcher af6cc963 and unchanged-source exit-state a9841a51 receipts. It checks all five successful paths, actual marker pair, no progress errors and the final audit's original evidence. Scorer wording now distinguishes staged wrapper/reducer from public staging/routing preparation. All five handoff file hashes match; six saved CPU checks pass. This addresses summary-before-final-validation admission without rerunning numerical jobs. It still cannot pass a complete 20ae timing report, because that run was interrupted before any complete arm was fetched. Existing five-job numerical evidence and failure 075b0e5a remain valid historical records; no lost native cache is assumed available.

**Replacement status.** Root's managed bare/default-size `fi-w4a16-mega-0909a` request became READY after 25.4 minutes, on hu-pdx-115 with eight B300 and driver590.48.01, using explicit `nvcr.io/nvidia/pytorch:26.05-py3`. Root owns provisioning, source and remote setup. The independently reviewed [setup handoff](candidates/cuda132_recovery_0909a/handoff.json), SHA `214b35105076afd2e98f630cfe1cf1206ee8191a84ee0fec1722f5499420eaaf`, stages only 17 handoff files, the handoff and five consumed dependencies. [Stage receipt](candidates/cuda132_recovery_0909a/stage-receipt.json), SHA `014aac4b99980a36d5bf6094479f6fbef097f6ed0a4220680adf0a05109490ea`, records 23 verified files and 23 exclusive creates with checkout absent. No historical benchmark/cache-owner tree is staged. The old transport was backed up before root retargeted it.

The first bootstrap redirection failed before executing the script because logs/ was absent; root corrected the directory, bootstrap PTY19174 exited0, and setup PTY16746 is now running with bootstrap/source-installed fetch4317 underway. Actual completed source/image/packages/preflight receipts remain pending. Bootstrap restores C1 commit 195946 plus the exact two-file ec94 overlay first; logger 38870 will require explicit source admission afterward. Existing package/image/CUPTI checks, 13.2 preflight flag and system PATH are preserved. Performance is preparing fresh-owner runtime admission with optional phase/iteration arguments while retaining full-grid timing; no old 079f owner or completed source-only setup is treated as a fresh performance result. Integration remains local-only. No CUDA13.0 restart or experimental-kernel promotion occurs.


Entry032 completion update at 2026-09-09T01:39:00Z. Root published the reviewed body through process 70346, exit0. [Publication receipt](logs/pr5019-timing-logger-publication-001.json), SHA `9e142b34316f2a8ed53660643ddd770625f9f3b19522c966cd68c873c41dab4c`, confirms head 50ff, draft=true, body `0d166747e2fb87f40c89b5149d9603ee305d0bf3ddb63301fee6f025bcf9672d` and unchanged Final performance. Both local drafts match. This is a benchmark-observability/documentation publication, not a new performance result or promotion of the three experimental kernel files.

Replacement setup is now completed and fetched: bootstrap 19174, setup 16746 and final fetch 57776 all exited0. [Completion receipt](candidates/cuda132_recovery_0909a/completion.json), SHA `305d117b89b6c411e8385427de827ce3bd011a8e682655ec4c2cb18015fccb9b`, binds 21 saved artifacts on hu-pdx-115, eight B300, driver590.48.01 and explicit 26.05-py3. Actual source remains exact ec94, with 1,572 sources/337 required paths; original image-before and image-after records are byte-identical. Accepted preflight SHA `441b19e96da22d7757d9ba7e33000d714bd5c1961d1bc3842cd6ded7f7e48ab0` and environment SHA `5b2c4ccf31b024f32f458f1f438c59ae9b423f341c5fd21163f4750c6c94d5dc` verify `/usr/bin/python3`, `/usr/local/bin/torchrun`, image Torch2.12.0a0+5aff3928d8.nv26.05/CUDA13.2, DSL4.7.1/native13.3 bb367 and direct BF16 decoding, 16 candidates, eight visible GPUs and original profiler versions. Actual CUPTI timestamp/dispatch-pointer ownership passes; the separately mapped toolkit CUPTI remains recorded, so the all-process-maps-wheel-only field stays false by design. Setup did not restore native caches, compile Mega, initialize communicators or run tests/benchmarks. The failed first redirection is retained separately and was not a source/setup assertion failure.

Root released remote ownership to performance for logger installation with full source 38870 admission, four fresh baseline validation jobs and the complete fixed/auto 1–4096 sweeps at 100 samples. At this update those runtime steps are authorized and pending; no replacement numerical, cache-owner, sample-array or timing result is claimed. Old 20ae's five completed numerical jobs remain valid historical evidence, and its interrupted full13 remains incomplete. Integration performed only local read/hash/documentation work and has no remote/native/GPU ownership.

Entry032 runtime-admission update at 2026-09-09T01:50:36Z. Performance's logger installation/preflight PTY52013 and fetch15255 completed with exit0. Installation receipt `049f311f6647ff1ee85b3bd63a7111aa6924d9aaedf963d86ec207c184693adb` records exact ec94→38870 through the benchmark-only delta and preserved old benchmark bytes. Actual new preflight `e8d11bd7f00bd52bd4cc3e5ebc61c43cfbe94e7140fe554777285a8645f27275` is admitted by approved receipt `c3b8d90ad6f6cda62d65f6feb8a8fdb2744be42b12bc5f6de928ae4e4e640608`, which binds the successful remote markers/exit and 13 saved evidence hashes. Integration verified those saved inputs locally, including the original setup/native identity and unchanged new-versus-historical environment.

The bounded independent runtime review passes against `candidates/cuda132_recovery_0909a/performance/runtime-files.json`, SHA `4480a6493e2e1f8238c27c4e6ace8bb015896e9b527000899cd6663bda16bb06`, with all 136 consumed files matching. The sole review fix requires actual socket hostname to equal the attested replacement setup before sequence/job/full13 cache admission; final variant SHA is `50b1f1fa5f8c12fd2c59349a266655cb0baf80f5781b571a80a6e1298d50c01e`, full13 driver SHA `ce8f350ee3d80dc929b1e232426d2c7e2c1a243e9e94b87f422df7b7f4fb5a72`. All 94 consumed historical public evidence files revalidate: eight suites, 120 rank-tests and 192 REG96/640/two-decode/pool61440/local0 objects, explicitly inherited across the benchmark-only change. Six actual640 payloads are byte-identical; lifecycle changes only helper paths. The validation sequence creates fresh caches and follows each completed native predecessor; performance creates a separate four-cache root with no old-node owner. Original full-grid timing calls, rank-MAX reduction, actual choices and resource checks remain, with optional arrays checked against all printed medians. Default both/100 remains confirmation; closed reduced/selected-phase screening and cache checkpoints do not imply an unrun arm or publication eligibility. Four fresh GPU validation jobs and the full13 sample calibration are still pending at this checkpoint. No remote, native, GPU, production or frozen-artifact action was performed by integration.

Entry032 four-gate completion at 2026-09-09T02:04:07Z. The original validation launcher PTY3657 exited0 with both execution markers and all four exact completed paths; final fetch66161 closed. Summary `8f6758a434a9c2ec510ca13fcd95434756c26e2220d13e8f510d02fe79d56988` and launcher receipt `3be5ac5ce0da999c2aa7a68bf759c67a5eff6577581786c0aacbffc4aef42786` are saved. The concise independent [four-gate audit](logs/cu132-recovery0909a-modern5wg-four-gates-independent-001.json), SHA `65fd1e2c9f0ee48d4b308ff955e424a93a3b5b39135064a9228325d5419ab5ab`, reuses only the existing pure output validators and checks all 58 summary files, source/helper/preflight identity, result exits, ordered saved native inventories and final launcher/exit-state receipts. All 58 actual objects satisfy REG96/640/two-decode/pool61440 and have local0: two resource probes, 54 lifecycle objects including six winner/cache observations, and two graph-sampler objects. The lifecycle retains 32 nonempty and 16 empty-output candidate oracles, 9 stable and 3 changed-input graph replays. Sampler checks include 32 replays, 6 resets, 8 samples, exact peer-only capture failure propagation and subsequent recovery. The first native inventory is empty; all four after snapshots equal `99f79428ba97e9f72e780ddf71e4089d23b80a9d7fff63783f96e5da2e4ad1a6`. This is fresh resource/lifecycle/sampler proof; eight public suites remain explicitly inherited.

Under root's existing authorization, performance launched the original full13 runner as PTY91228 on source38870, with both fixed CONTROL and auto16 across all 13 points at 100 samples. Live admission/dry checks passed and initial stack/native-before metadata is fetched. Performance owns the exclusive GPU/runtime window and all fetches. No complete arm or calibrated 20/30/50-sample screening budget is claimed yet; integration will apply the existing saved-sample analyzer after a complete arm is available. Published kernel/table provenance and experimental source status remain unchanged.

Entry032 fixed sample calibration at 2026-09-09T02:21:18Z. Fixed CONTROL completed and fetch11911 closed; actual control SHA `044e3cf54400cd44d1ae27c9e4152dfb1f47e2a3f88ac5ce6ad2e354806ce0c3`, execution receipt `2b690cb8e1e7897126e09cd44f756d332b2f281655f25ad037ded54653ec754f`. Integration applied the existing iteration-budget analyzer without changing it: [all-point diagnostics](logs/cu132-recovery0909a-modern5wg-control-sample-budget-001.json), SHA `1995c4103758ee5024af0ad276a4981f208735a96dd6b40800cafa5217eb500d`, and [concise findings](logs/cu132-recovery0909a-modern5wg-control-sample-budget-001.md), SHA `58fbc46e29760271ed40223e24ace4928b46343f6742301e6cc9d1a5e4563976`. The [independent fixed sample/raw check](logs/cu132-recovery0909a-modern5wg-control-samples-independent-001.json), SHA `26cdd6c80c4471de2ee0d4d3deacc09ea866992573228e7dc3af8887aa027494`, reparses all 26 raw rows, 104 split records, 104 actual compiled records and 26 arrays of 100 post-rank-MAX samples. All resources have local0 and the original contract; array medians agree with the printed six-decimal values within rounding (maximum approximately 0.0000005 ms). Exact source and per-arm provenance pass. Auto is still running; no complete both-arm owner or comparison is inferred.

Actual subprocess wall is 899.790608815 seconds, including this new node's first-use native build. The 26 rank-zero timing-utility intervals sum to 11.815638530 seconds (split5.889442645, Mega5.926195885), 1.313% of that phase wall; each interval is about 0.414–0.505 seconds. Utility wall includes graph preparation, estimate calls, flushing, processing and reduction. The 887.974970285-second residual is not labeled compile time, and the whole phase is not a warmed iteration-time measurement. Worst absolute first20/30/50 median deviations across the 26 points are 7.031%/7.173%/5.441%; worst point rolling-window p95 deviations are 7.670%/7.031%/5.346%. Mega-only first-prefix maxima are 3.203%/2.677%/1.299%. The full point diagnostics and raw arrays remain saved, with no row selection.

Root's decision is to retain 100 samples for ordinary full-grid fixed screening. Reducing count is a weak speed lever in this measured arm and sacrifices useful median stability; no additional 20/30/50 actual-run trial or repeated fixed calibration is needed. Fifty is less sensitive here but does not establish sub-percent reliability across the whole paired grid. These dependent within-run windows are not confidence intervals, the 100-sample reference is not ground truth, and no shorter-run or between-run speed/stability claim follows. The full 1–4096 grid, primary timer, publication tables and 100-sample default remain unchanged.

Entry032 complete baseline at 2026-09-09T02:38:56Z. Original PTY91228 exited0 with the complete marker; final canonical fetch59987 closed. Postflight41559 passed source 38870/native/GPU-worker-idle checks. The completed owner is `logs/cu132-recovery0909a-modern5wg-full13-001`: manifest `df96338af84e474f4902ceef7a8a25d11618da29ddbe58263a29f4ee97bb4631`, results `e7fa3be5636eae92ef418f49949209bf62378e7512c4d810c0a6f61793b79aec`, native-after `c53b29471147f64715fe273b473c7e95f3e9aee4e4d536e9bf73528a3b4b1831`. The existing clean-process saved reader initially failed only because its generic wrapper constant differed from the original controller; performance restored the exact baseline wrapper assignment before the unchanged provenance validator. Both failed local attempt001 receipts remain saved. Independent attempt002 passes all completed phases and exact source/native/idle bindings; proof SHA `3bf905882339c0bc4cb97711f68a930c2c7b91f0beaef48fb09a93c19216404d`.

The [complete independent report](logs/cu132-recovery0909a-modern5wg-full13-independent-001/comparison.json), SHA `f10edfaf8e26f0dab5f93f09a13ade307277b3c422c1f341dd530da5f2da3eb0`, preserves all 52 raw rows, 208 split records, 208 actual compiled records, 104 returned choices, 13 complete 16-candidate rankings, 10 final cache capacities and 52 arrays of 100 post-rank-MAX samples. All 208 actual production resources have local0 with the REG96/640/two-decode/pool61440 contract. It reuses the original comparison math and table writer; [current auto table](logs/cu132-recovery0909a-modern5wg-full13-independent-001/auto16-full13.md), [fixed/auto table](logs/cu132-recovery0909a-modern5wg-full13-independent-001/fixed-versus-auto16-full13.md) and [all52 raw rows](logs/cu132-recovery0909a-modern5wg-full13-independent-001/raw-latencies.csv) are complete. Auto Mega is faster than fixed CONTROL at 13/13 points, with geometric mean auto/fixed latency 0.930334 (−6.967%). Auto is faster than its paired split at 12/13 points, geometric mean split/Mega 1.059677x; only T1 is below parity (split 0.079473/Mega 0.090274). T4096 is split 0.573590/Mega 0.507012. Split tactics change on 35/104 rank-shape pairs and all 13 actual auto choices differ CONTROL; this is not an isolated selected-tactic speedup or a source improvement. Published tables remain unchanged.

The [existing analyzer's auto diagnostics](logs/cu132-recovery0909a-modern5wg-auto-sample-budget-001.json), SHA `eaa9ee0ba4c3503b9f979b9ba5bb88d292d65b5b17aeb3cebd73c52dac717f52`, confirm 11.783223428 seconds of timer utility wall versus 932.118753394 seconds of subprocess wall (1.264%). Both arms total 23.598861958/1831.909362209 seconds (1.288%). Auto first 20/30/50 worst prefix deviations are 8.445%/7.621%/6.185% across all 26 points; Mega-only maxima are 3.579%/2.519%/0.879%. The retain 100 decision stands, without a new reduced-count trial. Auto's residual includes unpartitioned setup/tuning/runtime work; neither it nor the fresh-build fixed residual is labeled compile-only or warmed fixed iteration time. Exact hot staged-scorer versus cold public full-forward CUPTI scope remains explicit.

The next e359 runtime code has passed bounded source review: exact three-file delta from 38870, original five split/reference jobs, actual shared/MRO resource admission, direct completed same-node native cache reuse, fresh DSL/driver outputs and unchanged primary 100-sample phase loop. Its actual baseline declaration now binds the completed owner above. Candidate source installation/preflight and five numerical results remain separate pending admissions; no candidate result, source promotion or PR-table change is inferred from this baseline completion. Performance retains all remote/GPU work; integration used local saved artifacts only.

Entry032 e359 focused-validation completion at 2026-09-09T02:56:18Z. Performance installed the exact three-file 38870→e359 delta on the recovered node after the baseline closed, preserving the old shared kernel, decoder utility and private Mega file before mutation. Install receipt `5b4dc3f4a79a7fa7799ae4ff4a225060843e647c0c3d4a6a725e5796dc4ee0ef` and actual preflight `e5693b9a9568bc509656605e29f65f8f1b823e565777f2aa4ebf2a1eed5cb3f7` are saved. Approved receipt `9aa6998090108c93f738abdf9120500afe9741ead61bc746587a260636fcc79e` and runtime map `ac8d15dab2a76176aaf970254137a2d8bfb19447e470274177093523bd583671` bind 42 consumed files/inputs. Candidate source is `e3590c2f766a4e1c635e45d49471579394190e38acdb8fdabeef2dafb8963321`; original logger, scorer, native C++ inputs, image/native identity and public resource contract remain unchanged. The earlier rejected fetch metadata-name typo is preserved; its corrected fetch succeeded without altering numerical evidence.

All five original jobs completed under PTY95630 with true exit0; final fetch64747 closed. [Summary](logs/cu132-recovery0909a-scale-u16-validation-sequence-001/summary.json) SHA `813aa43c015546faefe0e02cd4827af40f667cf9e473b5557c790e84a8a66e0e`, launcher exit SHA `41fbdb82382e117467b2ee42f3196b1f3edf37b947dade234b50e34a4b94b6b0` and exact marker pair establish completed execution. The [independent final audit](logs/cu132-recovery0909a-scale-u16-numerics-independent-final-001.json), SHA `9907f06a5a96765e6a33f18914999a1db1daf6865e5c56a58a8db1c057d1916f`, uses only the original pure split validators (AST-sliced to omit pytest import), unchanged reference/output/resource validators and saved source/native/exit checks. It verifies 14 split call tests, 42 passing setup/call/teardown reports, 28 loaded shared b473/decoder357 alias observations, 12 Mega reference rank-tests and 48 actual REG96/640/two-decode/pool61440/local0 objects with nested shared/MRO proof. All five before/after native snapshots equal completed baseline `c53b29471147f64715fe273b473c7e95f3e9aee4e4d536e9bf73528a3b4b1831`; source/preflight/helpers and immediate predecessor hashes remain exact. No GPU tests were rerun by integration, and no live cache assertion is inferred from local files.

Root allowed the original CONTROL100 continuation after original five-job checks while independent saved verification closed in parallel. That independent audit is now PASS with no discrepancy. Performance launched reviewed PTY42257 for `cu132-recovery0909a-scale-u16-control13-001`, initially in fresh owner/admission checks; the actual benchmark-start marker and candidate timing remain pending at this checkpoint. The screen keeps all 13 global token counts and 100 cold-L2 CUPTI samples, with actual retained same-node native roots and fresh DSL/driver/output paths. No promotion, PR edit, reduced-sample trial, fresh host/lifecycle/catalog rerun or CUDA13.0 work follows from these focused numerical results.

Entry032 completed e359 control screen at 2026-09-09T03:11:29Z. Original PTY42257 exited 0 with the complete CONTROL marker; fetch53365 closed. The [control-only owner](logs/cu132-recovery0909a-scale-u16-control13-001/stack-manifest.json) has manifest SHA `645c8c36a41f4fa0f9726ab23dd84346f7990e075a792f235f0d336108fc9913`, results SHA `aa96ff4196aabcfa7e11812dd7d6f4d927e409650805ec8ef9f8b8eb1263efd2`, and final native inventory `60c59c2481647d7b35f9b0426bf337307c67f1f5c2e5d04c2b9c769dc306cb9c`. [Idle receipt](logs/cu132-recovery0909a-scale-u16-control13-idle-001.json), SHA `30fe1583865bf98a72aa57917134021d3245e24e0785bc403cad3d8cbaade8b4`, binds the exact completed source, manifest/results, live native roots/inventory and no GPU/native workers on hu-pdx-115. [Closure receipt](logs/cu132-recovery0909a-scale-u16-control13-closure-001.json), SHA `1105f69fe5ba39c6b4a8c9f3349128d2ab0e131249d58cdf874125e3aef16e8b`, records successful execution, fetch and idle closure. This is a completed control-only checkpoint; auto was not executed.

The [independent saved audit](logs/cu132-recovery0909a-scale-u16-control13-independent-001.json), SHA `5b86da9a2e1771151050eb74b8691abfaa478b450cc97e0985cfac7a67b05e10`, passes original source/native/provenance, raw/result, sample-array and candidate nested shared/MRO resource checks. It reuses the exact original validators in a clean process with the actual candidate capture wrapper explicitly bound; no reusable framework, native import, remote operation or numerical rerun was added. All 26 candidate raw rows, 104 split records, 104 compiled objects and 26 arrays of 100 post-rank-MAX samples are complete. Native-before equals the final focused numerical predecessor, and the actual control final inventory is retained without excluding JIT-log changes.

Independent arithmetic reconstruction matches the [complete paired report](logs/cu132-recovery0909a-scale-u16-control13-comparison-001/comparison.json), SHA `4394405135500c1fc72933ba45a1b71479058f16fa4d3ba4bcb0c4ec30cbf513`, and its [all-13 raw table](logs/cu132-recovery0909a-scale-u16-control13-comparison-001/README.md). Across both fixed arms, all 52 raw rows, 208 split records, 208 compiled records and 52 sample arrays are preserved. Mega candidate/baseline geometric mean latency is 1.0001437794785062 (+0.0143779%), with 9 points faster and 4 slower. All 104 actual CONTROL configs and requested dictionaries agree. Split candidate/baseline geometric mean is 0.996100240674693, with 49/104 split tactic selections changed. All 208 paired resources are REG96 / 640 threads / two decode groups / pool61440 / local0. The shared decoder also changes and split tactics retune, so this is not a pure Mega-only attribution; no row minima or isolated UInt16/h speedup is claimed.

Candidate subprocess wall is 315.129061668 seconds, including 11.702198875 seconds of timing-utility wall. Baseline fixed wall was 899.790608815 seconds with 11.815638530 seconds in that utility and a first-use native build. Their different cache/setup histories prevent interpreting the phase-wall reduction as kernel acceleration or a controlled warmed-iteration comparison. The 100-sample/full-grid decision remains unchanged.

Root's decision is to skip candidate auto, keep e359 experimental and leave published bd2fa/ec94 kernel provenance, logger commit50ff and PR performance tables unchanged. The completed 645c/aa96/60c/30fe checkpoint may admit the next same-node private native trial without pretending auto completed. Root released the FC1 compile-only window to performance, which is preparing the private source package and loader/pair against this actual owner. No FC1 native execution or quality result is recorded yet. Integration changed only this ledger and `CURRENT_STATE.md`; source, frozen helpers, PR files and memory remain untouched.

Entry032 FC1 native completion and focused numerical plan at 2026-09-09T03:27:16Z. Both private matched pairs are complete on the e359 control-only owner: `profiles/fc1-first16-e359-m256n128c2-001` and `profiles/fc1-first16-e359-m256n64c2-001`. Root accepted the original native gates and the [combined native review](candidates/w4a16_fc1_first16_native_review_e359/COMBINED.md), [receipt](candidates/w4a16_fc1_first16_native_review_e359/combined-receipt.json) SHA `98badd3dbbccd6cdb064f65c8aad376cde3e94bddf9594974150f96847da775a`. Both pairs preserve source/native60c before/after, report successful owned-process completion, and leave no recorded GPU/native workers. These compile-only results execute no GPU kernel and are not numerical or performance evidence. Integration reads the accepted receipt rather than repeating the native review.

| Geometry | Whole static instructions, control → candidate | FC1 region | FC2 region | Actual resources |
| --- | ---: | ---: | ---: | --- |
| M256/N128/C2 | 5856 →5864 | 223 →234 | 227 →227 | REG96 /640 threads /STACK0 /LOCAL0 |
| M256/N64/C2 | 5528 →5536 | 223 →234 | 227 →227 | REG96 /640 threads /STACK0 /LOCAL0 |

The +11 FC1 /+8 whole-kernel instruction cost is explicit. Both geometries retain four packed LDS.128 loads, two scale LDS loads, 64 E2M1 conversions, eight E4M3 conversions, 32 BF16 multiplies, 32 BF16 fused operations and eight STTM.x8 stores. Whole-kernel MMA/broadcast counts, two decode groups and the register redistribution remain unchanged. The first16 packet is scaled before decoded-stage acquire and survives the blocking slow path; remaining packed reads precede raw advance/probe, with no TMEM store before acquisition. Final stores, fence, raw release and decoded publication preserve ownership order. Seven added moves come from packed-load definitions, not BF16 output gathers; extra scale permutation/mask/packing work is real. FC2 matches after its documented uniform-register and branch-label normalization. Native code quality permits the experiment but predicts no speedup.

The [numerical coverage recommendation](candidates/w4a16_fc1_first16_numerical_coverage_e359/README.md), SHA `22f20fd6d5ff3a373105f81afa2eb671157583adcebce2fcfed09e90f303dbf2`, compares the exact two-file proposal/native payloads to retained split and Mega tests. The existing reference cases already cover changing token counts, empty/refill workspaces, H288/I448 tails, both return modes and exact graph replay. The new FC1 path additionally needs M128/C1 and M128/C2 layouts plus the retained H64/I64 padding, H1024/I512 multi-K/phase and H9472/I64 long raw-ring cases. Root/performance accepted seven jobs using unchanged definitions: split14; M256/N128/C2 and M256/N64/C2 EP1 reference pairs; then EP2 for those two and M128/N64/C1+C2, each with both references and the three exact geometry cases. Expected counts are 14 split call tests /42 phase reports and 44 Mega call rank-tests /104 objects. No host125, all16 lifecycle, sampler or unrelated dense rerun is added. M128 EP1 and explicit true-fragment64 remain outside this focused matrix. The two native cohorts both instantiate FC1 fragment128; route64, H64 and N64 labels do not prove the per-thread fragment extent.

Integration supplied only the new pure `candidates/cuda132_recovery_0909a/fc1_first16/reference_subset.py`, SHA `e9b62c5ea3c25a391c9afdc7363efe1a6a1462b44d5db1fec19d8108ea4dd2e8`, to performance's runtime adaptation. Its copied geometry validator has the original AST except its private name; the reference body differs only at the private filtered-row input boundary. Exact EP1 two-case /EP2 five-case identities, setup/call/teardown success, original layer counts, shapes, knobs and actual resource checks remain. [CPU proof](logs/cu132-recovery0909a-fc1-reference-subset-cpu-001.json) and [complete output](logs/cu132-recovery0909a-fc1-reference-subset-cpu-001.log) cover six saved historical public-job fixtures, seven negative cases and two AST checks; resource calls are explicitly mocked. Ruff passes. Those fixtures are selector/admission checks, not candidate GPU results. Performance owns other runtime files, actual installation/preflight, execution and fetch; numerical validation and the complete fixed sweep remain pending here. Production/PR files remain unchanged by integration.

The [current640 profiler refresh](candidates/w4a16_modern640_profile_refresh/README.md), SHA `d79cb38895bd3dccccf425314cde933785ed01eb47a21d135de2f598166e7008`, is queued after the next admitted numerical checks and complete fixed sweep. It reuses successful NSYS EP8 global32/4096 and NCU EP1 T4096 paths with current source/native ownership and actual REG96/640/two-decode/pool61440/local0 gates, preserving input staging, reducer scope, finite cleanup and source correlation. It does not require auto merely to establish a completed owner. Old 512-thread reports remain historical; EP1's expert/row distribution differs from EP8, and profiler durations do not replace CUPTI performance. No current640 capture or profiler result is claimed. Published kernel bd2fa/ec94, logger50ff and PR tables remain unchanged.

Entry032 transition notice: root reports FC1 runtime staging69496 completed and f377 installation PTY16236 active under performance's ownership. The compile-only captures above kept e359 unchanged; this later installation is a separate authorized source transition. Completed installation/preflight and new-source numerical/performance results remain pending. Integration is ready for saved completed-log review without blocking original validated GPU progression, and makes no further runtime edits.


Entry032 FC1 seven-job completion at 2026-09-09T03:48:02Z. Performance completed the exact two-file e359→f377 installation, preserving shared b473 and private Mega2d53 before replacing them with eb7a/a1e1. Actual source is `f3776369a6399b5c8860504af96fc09041ff1fc2fb1dfaf00bbe06d3fcd142e2`; decoder357, logger, scorer, native inputs and public resource contract remain unchanged. Actual preflight `b68c7359395fd8bb2c463cf45fe6e9191c937de64e25861ffdfc0ed3fbcdf01e`, approved receipt `ac7bf96c01eef75a571784521c868cee4f5336f92f1f06981df09472f11fa72b` and 40-file runtime map `8b420aaffa5f5d2c76d59a94112dd77dd7ec9573f922e98c1c352a4dd79db7af` bind that execution.

All seven original jobs completed under PTY16293 with true exit0; final fetch6429 closed. [Summary](logs/cu132-recovery0909a-fc1-first16-validation-sequence-001/summary.json) SHA `a24f21f5434c50117217b64553a5885d31da51a0ff0c87766487c3c8930a679d` and launcher receipt `37a2244d73aa76aaf5646a55f51562db0d984d22ee41cc38748da5811777b56c` retain exact seven paths, no progress errors and the actual completion markers. The [independent final audit](logs/cu132-recovery0909a-fc1-first16-numerics-independent-final-001.json), SHA `05ac01f4829965fe0d6ce7eb5df3707b5a4db03715ddf7ce26291290e963cc1b`, verifies 14 split calls, 42 setup/call/teardown reports, 28 loaded shared-eb7a/decoder357 alias observations, 44 Mega rank-tests and 104 actual REG96/640/two-decode/pool61440/local0 resource records with the original nested shared/MRO checks. It covers both M256 reference modes at EP1 and all four geometry families at EP2 with the accepted partial-tile, phase-reuse and long raw-ring fixtures. All source/helper/command/preflight maps and native predecessor links match; every saved native-before/after inventory equals60c. The frozen plan.scope sentence still says five jobs, while its executable list, commands, schema and actual outputs prove seven. This wording defect is preserved and disclosed; it does not require a rerun. True per-thread fragment64 remains unobserved; no exhaustive decoder-bit or new host/lifecycle/catalog/sampler coverage is claimed.

Under root's standing authorization, performance started the original CONTROL100 launcher PTY44426 for `cu132-recovery0909a-fc1-first16-control13-001` while the independent reread completed. Its saved launch binds the exact successful summary, source f377, all13 global token counts and 100 original cold-L2 CUPTI samples. The independent audit reports no material discrepancy. Timing is active and no complete arm, final native owner or speedup is inferred yet. Integration performs no remote/native/GPU operation or production/frozen-file edit. Published bd2fa/ec94 kernel, logger50ff and PR tables remain unchanged.


Entry032 completed FC1 CONTROL100 at 2026-09-09T03:59:31Z. Original PTY44426 exited0; complete fetch48736, source/native/idle14438 and canonical idle fetch42093 all closed0. The completed control-only owner is [manifest](logs/cu132-recovery0909a-fc1-first16-control13-001/stack-manifest.json) SHA `336fb3b8f0105c60a4c06ccab95b4508b4b6ea61cf28609eae4a83c0478fa951`, results `8e7326ff20f0006df7095b6475b2e9593d8b181c869b2145a3cfa2b1269ef343`, final native inventory `90f5d0a265ce4ba7f21a0d83122df327d1bd50a4cc1ee19b068e1c7c3ef667f5` and [idle receipt](logs/cu132-recovery0909a-fc1-first16-control13-idle-001.json) SHA `f57c1c26fbe8b79b91a795878a9ce92a60fa4a3ae4679b1e686217c743fa0d11`. Its saved source is exact f377 on hu-pdx-115. Native-before equals the final seven-job60c snapshot; final native differs only in `flashinfer_jit.log`, 158,136→180,704 bytes, with all75 other entries unchanged. The log remains included in ownership.

The [independent saved audit](logs/cu132-recovery0909a-fc1-first16-control13-independent-001.json), SHA `53f38839a73e2bae92e51fad3ac8f99cc39a02c0df87158d1182512f7693addd`, checks 217 consumed evidence hashes and original source/runtime/preflight, raw/tactic/sample/provenance, exact candidate nested shared/MRO resource and closed source/native/launcher/idle contracts. It preserves all26 candidate raw rows, 104 split records, 104 actual compiled objects and 26 arrays of100 post-rank-MAX samples. The three-source [comparison](logs/cu132-recovery0909a-fc1-first16-control13-comparison-001/comparison.json), SHA `3c4bb63e000baa86601a1bf185f7dc77dfa365fa445d7d65eaf4d520322053e2`, and [complete thirteen-row table](logs/cu132-recovery0909a-fc1-first16-control13-comparison-001/README.md) match independently reparsed logs and tactics: 78 raw rows, 312 split records, 312 compiled records and78 timing arrays. Every resource is REG96/640/two-decode/pool61440/local0. Two local one-off marker-parser attempts are recorded in `logs/cu132-recovery0909a-fc1-first16-control13-independent-attempts-001.log`; the final extra cross-source check uses the original raw JSON decoder to handle concatenated rank output. Candidate original validators had already passed, and no runtime, source, tolerance or test was changed.

| FC1 compared with | Mega latency ratio, candidate/baseline geometric mean | Points with lower Mega latency | Equal CONTROL configs / requested knobs | Changed split rank-shape tactics | Split latency ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retained38870 | 1.0046953213 (+0.469532%) | 6/13 | 104/104 | 45/104 | 0.9962525966 |
| Intermediate e359 | 1.0045508875 (+0.455089%) | 5/13 | 104/104 | 30/104 | 1.0001529524 |

Candidate subprocess wall is318.880318050 seconds, of which the timing utility accounts for11.869729078 seconds. The corresponding e359 values are315.129061668 /11.702198875, and retained38870 values899.790608815 /11.815638530. Retained includes its first native build; these process-wall differences are not a measured kernel speedup or controlled warmed-iteration comparison. Shared split source changes and split tactics retune, while separate unbracketed runs do not isolate a mechanism. No row minimum or drift adjustment is used. Root's decision is to skip candidate auto, retain f377 as experimental and leave published bd2fa/ec94 kernel, logger50ff and all PR performance tables unchanged. This actual control-only owner can admit performance's separate packed-SF native trial without implying auto completed; no packed-SF result is claimed by this entry.

The profiler preparation is separately frozen at [handoff074e740e](candidates/w4a16_modern640_profile_refresh/handoff.json), full SHA `074e740e50fcbcd6087d975c95d8c8876b999cc322f1c43d6ef5f50b1456b399`. It binds seven files and exact original helper/resource origins; eight original standalone NCU mocked tests and seven original function AST comparisons pass. Root and the bounded independent reader found no blocker. NSYS keeps exact-script EP8 substitution; only standalone EP1 NCU removes the original six peer/lockstep options. Local0 rejection stays inside original _query before unchanged consensus, with cached function identity and first-warmup metadata retained. No actual binding, upload, native import, GPU or profile capture was made. Scheduling must supply actual completed f377 owner/native/idle receipts and immediate profiler cache continuity; preparation does not synthesize them. Integration edited only this ledger/current state and its separate local audit/preparation artifacts.


### 033. Current five-warpgroup NSYS capture: complete actions, large launch skew

**Completed scope.** `profiles/fc1-modern640-recovery0909a-nsys-001` captured ordinary EP8 global32 and4096 on exact f377 /hu-pdx-115 /eight B300 SM103 GPUs /NSYS2026.2.1.210. Original PTY93807 and fetch57067 exited0; saved outer exit reports137.482170340 seconds, unchanged source, empty before/after GPU/native worker checks and exited owned process groups. The scheduling binding is912a6f4f, and parent resource receipt5967ed90 passes. All76 native entry objects remain identical to the completed CONTROL owner90f, including `flashinfer_jit.log`; profile serialization369d is sorted JSON with a different byte hash, not a changed inventory or an excluded log.

**Independent completeness.** [Receipt](profiles/fc1-modern640-recovery0909a-nsys-independent-001/receipt.json), SHA `0af81d6ac0c5f869529a9547a1e64a81a40dbf36704360d4409214c1cc44f901`, verifies92 consumed source/binding/helper/owner/capture hashes. Both SQLite integrity checks pass. Each capture contains all8 device/PID mappings with2 actual Mega actions perdevice,16 routing kernels,16 input-ID copy kernels,16 reducers and32 correlated memcpy actions. All32 expected NVTX stage ranges are present. Sixteen worker function observations pass the unchanged actual REG96/640/two-decode/pool61440/local0 and nested shared/MRO checks; the parent retains exact-script substitution for its two original launches. [Details](profiles/fc1-modern640-recovery0909a-nsys-independent-001/details.json) preserve every correlated kernel, memory action, GPU identity, diagnostic and32 rank/iteration records. Integration used only local SQLite/stdlib and saved pure resource validators; no profiler/native/GPU work was rerun.

| Global tokens | Routing mean µs | Input-ID copy kernel mean µs | Fused Mega mean µs | Reducer mean µs | Mega share of summed kernel time | Two memcpy actions mean µs/rank/iteration |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 3.546 | 1.800 | 430.749 | 2.492 | 98.213% | 3.306 |
| 4096 | 4.130 | 3.170 | 804.663 | 9.794 | 97.920% | 6.072 |

Shares sum GPU kernel durations across ranks/actions; they exclude memory copies and host/launch gaps. Copy sizes match the existing public hidden-state/top-k weight staging; top-k IDs use the elementwise copy kernel. Reducer arithmetic is a small external part of this trace (0.568% /1.192%). Internal routing/dispatch/decode/MMA/epilogue work remains fused and cannot be separated from these ranges. [Concise findings](profiles/fc1-modern640-recovery0909a-nsys-independent-001/README.md) retain full definitions and the source mapping.

**Skew and limits.** T32 Mega start spreads are693.007/274.131µs for the two iterations; finish spreads are0.472/0.314µs. T4096 start spreads are842.296/582.012µs; finish spreads are1.253/1.384µs. Early arrivals running longer and finishing nearly together are consistent with inter-rank rendezvous contributing to apparent kernel duration, but do not prove a specific stalled role. Mean input-ID-copy-end→Mega-start gaps are382.227/410.900µs. These instrumented host/launch effects must not be subtracted from primary latency or treated as intrinsic kernel cost. General in-kernel work still needs role-correlated NCU/SASS evidence; external reducer arithmetic has limited absolute scope in this trace.

All8 workers in each capture report potentially missing NVTX events, despite the independently complete expected stage/action counts. Other CUDA/NVTX-start warnings map to auxiliary PIDs. No severity3 or reported CUDA loss/overflow diagnostic is present; that is not a universal no-loss assertion. These are two instrumented eager actions perGPU with profiler CUPTI, separate from100-sample CUDA-graph CUPTI performance. Old4WG captures remain historical context only. No performance promotion or PR-table update follows. Root/performance proceed with the separately bound NCU production probe from the actual current inventory; this entry does not claim a completed NCU capture.


### 034. Current five-warpgroup NCU capture: complete actions and conserved samples

**Completed scope.** `profiles/fc1-modern640-recovery0909a-ncu-001` is the ordinary EP1 T4096 fixed f377 capture on hu-pdx-115, using NCU 2026.1.1. Original PTY80542, report export and fetch37835 complete successfully; the saved outer record reports exit0 in 39.627167618 seconds. Parent717ef98f and worker2bddfd0b pass. Source before/after is exact f377 across all 1,572 files; native before/after retains all 76 entry objects, including the JIT log, equal to completed CONTROL owner90f. Sorted profile snapshot369d remains a distinct serialization hash. Idle checks are empty and the owned process group has no remaining live or zombie members. Actual bindingd7b40780 preserves the original standalone communicator adaptation and exact-script replacement.

**Independent result.** [Saved audit receipt](profiles/fc1-modern640-recovery0909a-ncu-independent-001/receipt.json), SHA `8e0bad56c0b215e4c1d75f8c5856bf724178607a6b5ee2138675e9fbb4d16ef3`, checks 95 consumed hashes. The original actual resource/MRO validator passes REG96 / 640 threads / two decode groups / pool61440 / local0 with shared eb7a and loaded decoder357 identity. The [report](profiles/fc1-modern640-recovery0909a-ncu-001/ep_w4a16_megamoe_t4096.rank0.ncu-rep), SHA `85ca8700a3aca4672ae4d96341ae124583059d03f61e160fbd3eee538dd161c6`, contains exactly two matching Mega actions on device0, each with REG96 / block640 / 216,576 dynamic shared-memory bytes. Local0 is separately established by the saved prelaunch query, not a selected report metric.

| Action | Sampled PCs | All samples | Not-issued samples | Unresolved PCs / samples | Long scoreboard, all samples | Barrier, all samples |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 2,295 | 142,571 | 65,892 | 26 / 254 | 68,346 (47.938%) | 25,795 (18.093%) |
| 1 | 2,353 | 141,572 | 65,069 | 25 / 225 | 67,518 (47.692%) | 25,542 (18.042%) |

All 35 correlated metrics per action reconcile PC sums to instance sums and report aggregates; the all-sample reason totals independently equal each sample count. Not-issued data remains a separate population: its long-scoreboard counts are 42,638 / 42,166 (64.709% / 64.802%), and barrier counts are 11,769 / 11,494 (17.861% / 17.664%). Both actions report zero dropped bytes and buffer overflow, 32 MiB buffers, interval7 / 4,096 cycles, replay passes1 and PC aggregated passes2. These last two metrics are recorded separately, without inferring two full application replays. [Full findings](profiles/fc1-modern640-recovery0909a-ncu-independent-001/README.md) retain the definitions and exact export hashes.

**Attribution limits.** Thirteen embedded source texts match f377, including private and shared kernels, but the decoder utility is not embedded. Worker MRO proves its loaded357 identity separately. First-action SASS export14301fd8 has 5,000 rows at offsets0x0–0x13870 inside the requested0x18000 scan. Every supplied sampled SASS instruction from both actions matches that export. The 26 / 25 unresolved PCs have empty SASS/source and lie outside the emitted instruction range; all sampled offsets span −0x280 through0x13c20. Their 479 of284,143 samples (0.168577%) stay in every total and the [unresolved/conservation artifact](profiles/fc1-modern640-recovery0909a-ncu-independent-001/unresolved-and-conservation.json). Matching sampled SASS does not prove unsampled-code identity across actions.

The prospective local reader stopped on its unsupported embedded-utils requirement and also contained an overbroad nonempty-SASS expectation. Its unchanged source and [failed log](profiles/fc1-modern640-recovery0909a-ncu-001/export-read-check-001.log) are preserved. These are reader assumptions absent from the original capture gates; the final independent audit explicitly records the actual coverage instead of converting the mismatch into a kernel failure or requesting another GPU run. No original runtime, profiler payload, tolerance, source or gate changed.

Long-scoreboard/barrier fractions describe sampled states, not elapsed stall time, memory latency, tensor utilization or a limiting role. Optimized source-range wait labels cannot alone distinguish FC1, FC2, dispatch or epilogue; the separate SASS interpretation stays with root/design. EP1 has4,096 local rows /256 local experts, while primary EP8 at global4096 has512 rows /32 experts per rank. No primary latency, old four-warpgroup speedup, performance promotion or PR-table update follows. Integration performed only local saved JSON and original pure resource validation, then updated this ledger/current state. Remote/GPU/source ownership remains with root/performance.


### 035. Packed-SF: complete numerics and mixed CONTROL100 result, not retained

**Numerical evidence.** The frozen `candidates/cuda132_recovery_0909a/fc1_packed_sf` runtime3335eb75 binds exact source `049c9661f561520150af4887619049faf1699c854423fc84957bc214633df351`, actual preflight5f41ed46 and approved receiptd6379e2b. Its one-file shared transform change is eb7a → 2d89; private Mega a1e1, decoder357, logger and graph scorer stay fixed. Original PTY88813 exits0 and complete fetch21133 closes. Summary `c616147264ef5ba311da2e62f60630bfdbe0bd3a5de6c46562b47734105a74dd` and launcheraef73d42 retain all seven exact commands and completion markers.

The [independent seven-job audit](logs/cu132-recovery0909a-fc1-packed-sf-numerics-independent-final-001.json), SHA `16ab451e09b961a2c27158f883e23732c8994ee2ae44f28f06ed717f33a0e54f`, reuses original pure split/reference/output/resource validators. All14 split calls,42 setup/call/teardown reports,28 loaded decoder/x16 alias observations,44 Mega rank-tests and104 actual REG96 /640 /two-decode /pool61440 /local0 records pass. Exact source/helper/command/preflight maps, before/after inventories, six predecessor links and successful final sequence/launcher are verified. All81 summary evidence files are checked; its94-file evidence map also binds the previously validated owner and immediate NCU profile. Numerical native90f and profile369d have distinct byte hashes but identical76-entry objects including the JIT log. The saved audit does not compare049c to today's live source or rerun GPU work.

**Complete fixed sweep.** Original CONTROL PTY51082 and fetch34548 exit0; source/native/idle32886 and canonical idle fetch62247 close. Completed owner is manifest `11181cd86d7bf17ad3662c46fd8563595a37e4f5bee5f5073fecab8c094c5951`, results `cbb56d038e8c506da5c1d1cae1adffd71dbd59155f2ee37de65451b68a62a1fc`, final native `1967f9ec27d7eea363d2b665a184e7f3805ea0159772d7c0dd2df76baea27081` and idle `57603a7be7f779bc7698ec867704fe08b9d5855ac218707e734c0f7c278db2ce`. Only `flashinfer_jit.log` grows180,704 →203,272 bytes; all75 other entries and roots remain unchanged. The final native delta was independently reconstructed and equals the saved closure; the log is retained, not excluded.

[Independent CONTROL/four-source audit](logs/cu132-recovery0909a-fc1-packed-sf-control13-independent-001.json), SHA `77705b0214b07a9b7c81985eb7e5a7760f8e2521b609d8f80e382eef071c22eb`, checks368 consumed hashes. Candidate26 raw values,104 split choices,104 compiled objects and26 arrays of100 samples match the original result/provenance/timing validators with the actual candidate wrapper bound. Four complete fixed sources preserve104 raw rows,416 split/compiled records and104 arrays of100 samples; every resource is local0. The [full thirteen-row paired table](logs/cu132-recovery0909a-fc1-packed-sf-control13-comparison-001/README.md) and [comparison](logs/cu132-recovery0909a-fc1-packed-sf-control13-comparison-001/comparison.json), SHA `ca5043d1e502987d5ec2f471fd7d209292eff8af8590f8374b76df610600fc86`, match independently reparsed logs, actual returned configs, split selections and all arithmetic.

| Comparison reference | Mega candidate/reference geometric mean | Lower Mega points | Equal CONTROL configs / requested knobs | Changed split rank-shape choices | Split ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retained38870 | 0.9940678266 | 5/13 | 104/104 | 45/104 | 0.9827395263 |
| e359 | 0.9939249206 | 6/13 | 104/104 | 30/104 | 0.9865869781 |
| f377 | 0.9894221715 | 7/13 | 104/104 | 20/104 | 0.9864361003 |

Candidate wall is313.150887323 seconds, with11.596354981 seconds in the timing utility. These complete unbracketed rows use no minima or drift correction; shared split source and independently retuned split tactics prevent pure Mega attribution. The average improves slightly while eight retained-reference points regress, including visible midrange regressions. Root therefore skips auto, rejects promotion and restores exact retained38870. Published bd2fa/ec94 kernels, logger50ff and PR tables remain unchanged. Local and remote restore receipts preserve all three experimental files, and the actual postflight binds source38870 separately from the completed049c native owner1967.

One local saved-audit adaptation initially expected the prior closure's scalar exitcode fields. The current closure embeds the exact original launcher instead. Its [attempt note](logs/cu132-recovery0909a-fc1-packed-sf-control13-independent-attempts-001.log) is preserved; final validation checks that embedded launcher against the separately validated successful receipt and original counts. This was a local schema adaptation, not a runtime failure or gate relaxation. No frozen artifact, source, remote operation or GPU work changed during the independent audit.

### 036. Independent alpha trial on retained source: six numerical jobs complete

After the rejected decode stack is restored, alpha moves one FC1 alpha assignment in the private epilogue,604935 →1131. Source is `487b626009ba6420057b4ef3eef45c14b473719af2b72bd42c96f5a2e33a0e53` atop retained38870, with original shared4a870 /utilsc36 /Mega e009. Root accepted the sole design agent's N128 and N64 private native quality reviews; integration does not repeat or convert that compile-only result into GPU correctness. Actual remote install at05:37:21Z has a passed one-file receipt. Preflightdbf83705 and runtime42d20358 bind this separate source; completed packed-SF owner11181/cbb56/native1967 and the successful38870 restore remain explicit, distinct records.

Original six-job PTY19498 and final fetch27678 close successfully. [Summary](logs/cu132-recovery0909a-fc1-alpha-validation-sequence-001/summary.json), SHA `bd3004350ba8c8451c196a99154087e4210c1a6947f9b3bbc68e51dfdda4ae79`, and true launcher65f8103a retain the six existing M256 N128/N64 EP1 reference jobs plus four EP2 reference/geometry suites. The [independent final reread](logs/cu132-recovery0909a-fc1-alpha-numerics-independent-final-001.json), SHA `715ad562a8e32c00525f5cd6cc0a2771ef1a92aef95f796238c84689550ee49f`, runs the original six pure saved-output validators and checks70 summary files /113 consumed hashes, exact commands, source/preflight/provenance, prior-result links, six final cache snapshots and actual sequence/launcher closure. All44 rank-tests and104 REG96 /640 /two-decode /pool61440 /local0 resources pass. All76 native objects remain exact1967. Public fixtures use4 experts; no fresh split, host, lifecycle, sampler or exhaustive decoder test is claimed.

Original CONTROL100 PTY7094 is active over all13 token counts under performance ownership. The independent numerical audit ran alongside it and found no material discrepancy; no GPU hold or second approval was added. Alpha complete performance, auto, retention and publication remain pending at this checkpoint.

The artifact-only [PR logging paragraph replacement](PR_LOGGING_PARAGRAPH-completed-0909a.md) corrects the stale GPU-logging-pending sentence without editing either PR body or its tables. Completed retained38870 fixed/auto logging has52 arrays of100 post-rank-MAX samples across all13 token counts, with raw-median agreement. Actual utility walls are11.815638530 /11.783223428 seconds, within899.790608815 /932.118753394 seconds of process wall; fixed includes first-use native building. The later warm packed-SF sweep's313.150887323 /11.596354981 seconds illustrates the small timing-utility share, not a controlled process-wall speedup. Offline20/30/50 prefix/window diagnostics remain diagnostics rather than reduced-count GPU trials. Keep100 samples for every complete1–4096 sweep. Root owns final paragraph review/publication; retained performance tables and their older unlogged provenance remain unchanged.


Entry036 alpha CONTROL completion at2026-09-09T06:00:14Z. Original7094 and all report/fetch/idle operations have closed. [Canonical paired comparison](logs/cu132-recovery0909a-fc1-alpha-control13-comparison-001/comparison.json), SHA `e23c50157063bf19afca94755f34d20f1484724daae45c5310ae1b1076142cee`, and its complete thirteen-row README retain only alpha487b versus the retained38870 reference. [Independent saved audit](logs/cu132-recovery0909a-fc1-alpha-control13-independent-001.json), SHA `f145ad6369f1d37aa8aaba23596237076174bdb4448563a4f42bfff0b9cbc927`, reuses the original alpha candidate checker once, then independently reparses all52 paired raw rows,208 split choices,208 compiled objects and52 arrays of100 samples. All resources are REG96 /640 /two-decode /pool61440 /local0. The sole source delta is the private epilogue assignment; shared split code is identical, although32 of104 split tactic selections change. All104 actual CONTROL configs and requested knobs agree.

Mega alpha/retained geometric mean latency is0.9850415303912334, with9 of13 points faster. The full table preserves the T8 regression:0.156386 →0.170658 ms (+9.1261366%). Split geometric mean is1.0037218162066839. Candidate process wall is313.248735208 seconds, with11.598952181 seconds in the timing utility. These unbracketed fixed data are promising but mixed, without row minima, drift correction or a claim of isolated causal speedup. Root authorized complete AUTO100 for this simple epilogue-only trial; performance is preparing the completed-CONTROL-to-AUTO admission. No completed auto or promotion is claimed.

Saved owner manifest83467c37, result a6cee094, native `61934f26acbcd73c165f0a5aae6a6ed346ce3ef0822019f09bad9e990223742c` and idle `07e8105fb029879282d3881220769530cc3d3539535a01dd34679d1dca07fdbf` retain successful original launcher, exact source/helpers and the final numerical-to-CONTROL native transition. Performance's closure3c4fafda records only JIT-log growth203,272 →225,840 bytes with all76 entries retained. The independent saved audit completed alongside authorized follow-up preparation, without remote/GPU work or another scheduling gate. PR files, retained tables and publication remain unchanged.


Entry036 logging-only publication: root published and verified the completed-logging correction on draft PR5019. [Publication receipt](logs/pr5019-completed-logging-publication-001.json), SHA `a422521e7a1c08bc04e7a39eaacff42be833dc1dd7999bda5304822dd7d22970`, records unchanged draft status/head50ff, no comments and byte-identical Final performance suffix. Both `PR_BODY.md` and `PR_BODY-current-modern-full13.md` now hash to `4034261b997600dccfba42c746c54f3556e15825588fc2b882d35c16d3554c44`. Root used the local replacement paragraph with hu-pdx-115 and the explicit image added, and omitted its warm rejected-trial timing sentence to keep development history out of the PR. Complete retained38870 logging and the100-sample decision replace the stale pending claim; no performance table or kernel promotion changes. Integration verified only the local receipt and updated documentation, with no repeated GitHub read or write.


Entry036 AUTO execution update. Performance-owned original PTY26095 has passed the actual source/native/idle check and original dry plan, and started `cu132-recovery0909a-fc1-alpha-auto13-001-auto`. Marker is `FC1_ALPHA_AUTO13_31572614958d44418e2e2f279b8fa5a8`. Frozen AUTO runtime `91f5bed72089b2825b9d3ca09ad921ffc9011382a28400b9411c40a198ef4d41`, driver27f77842 and checkpointcd558012 bind source487b and completed same-source CONTROL native61934. The six numerical jobs remain historical native1967 evidence; AUTO reuses the actual later CONTROL cache. All thirteen tokens and 100 samples are retained. The prepared local comparator explicitly selects retained38870 AUTO from the same node and will preserve every previous/new Mega value, actual returned tactic and paired split value. The retained saved-reader preparation check passes; alpha AUTO is still pending. No fixed-for-auto substitution, row minimum, new GPU work by integration, promotion or PR table update follows from this preparation.


Entry036 complete AUTO and retention. Original PTY26095 closes with its true UUID exit0; canonical fetch1718 and final source/native/idle capture55593 close. [Complete same-node AUTO comparison](logs/cu132-recovery0909a-fc1-alpha-auto13-comparison-001/comparison.json), SHA `fe20574e34b621a95c8b29b231c28371824168c0621b6d7296c1cc9fa8681b48`, and [full before/after table](logs/cu132-recovery0909a-fc1-alpha-auto13-comparison-001/README.md), SHA7129b4cf, explicitly compare retained38870 AUTO against alpha487b AUTO. The actual AUTO successor's original source/preflight/resource/MRO/CUPTI/raw/tactic/winner/ranking/cache validators pass in a clean local process. The retained sealed original reader separately validates its completed pair, then only its AUTO rows enter the comparison. [Independent arithmetic and final closure receipt](logs/cu132-recovery0909a-fc1-alpha-auto13-independent-001.json), SHA `3a298b42006629414a822113c928008fa2abd51e03c46518394c8058ec764dde`, rechecks 217 consumed hashes, direct original raw rows against all thirteen table entries, actual returned tactics, original exit and final saved idle/native closure. Counts are 52 paired raw rows, 208 split selections, 208 compiled records, 208 actual AUTO confirmations, 26 complete sixteen-candidate rankings and 52 arrays of 100 samples; every compiled resource has zero locals.

Alpha/previous AUTO geometric-mean Mega latency is `0.9869305524120456`, or 1.307% lower and 1.0132425200× speedup, with nine of thirteen points faster. All four regressions remain explicit: T1 +2.533%, T16 +1.191%, T32 +0.910%, T128 +0.838%. T4096 changes 0.507012 → 0.499749 ms; T8 changes 0.154546 → 0.142002 ms. Five of thirteen actual tactics agree (40/104 compiled configs), and 49 split selections change. The new alpha paired split/Mega wins ten of thirteen; T1/T32/T128 remain below parity at 0.920312× / 0.978089× / 0.995883×. Alpha's separately completed AUTO is faster than its CONTROL at twelve points, with 1.0728× geometric-mean improvement and T32 +1.722% slower. These are complete unbracketed observations, not drift-adjusted values or fixed-tactic causal isolation. No fixed baseline is substituted for previous AUTO.

Current completed AUTO owner is manifest `09de5fa65a4fcc3b0cf7ae9f61dad64a92d1be000af11d44bb7e03b08d22ec2a`, results `7dccf063d22b1053e5e28dcd54eb43824246764df56ba3bcaa951b0cef257f48`, native `cba7683dc8a11b34a5e56fef8fbdeb4cfd0e6e3b77253e9eadea22d6202869fd`, idle `345f833607cc7cc9684ff91e5614e1c995b05deb439afe43a1498267e158b98c` and closure `1eedb285706d3c774eb535f605a0f1e4e2a2826861b4d23a23e69362fcfa20b7`. AUTO native-before equals completed CONTROL61934 exactly. All 76 native entries remain; only the included JIT log grows 225,840 → 248,408 bytes. Actual AUTO process wall is 937.047762301 seconds, with 11.758914737 seconds in the timer utility. Keep all thirteen points and 100 samples.

Root retains alpha per the user's preference after reading the complete before/after table. Exact one-assignment commit `2e8dc30df5efaf7dd1b7bf1771e72711c033d383` has scoped pre-commit PASS including mypy/Ruff/format. Root owns push and publication; integration prepared `PR_BODY-alpha-full13.md` SHA9a559aaa with the actual six-job raw summaries, native scope, one current CUDA13.2 auto table, direct before/after aggregate and all regressions. CUDA13.0 historical table and template/@humansand remain unchanged. No comment or GPU CI authorization trigger is posted; the saved upstream summary's skipped-pending-authorization state is distinct from local numerical success. Subsequent native trials may use the actual closed alpha owner without waiting for publication or another duplicate saved reread.


Entry036 alpha publication complete. Root pushed exact commit `2e8dc30df5efaf7dd1b7bf1771e72711c033d383` and published the reviewed current-alpha body. [Publication receipt](logs/pr5019-alpha-publication-001.json), SHA `34ce17593c894fc5c26d238f70d2a6367ac745cdf26adff5646d7ea440124690`, verifies draft status, exact head and body `043ca3520445fcfdc2f32c79ff17d6d69d017ab30e743eec8609cb8defef888a`, with historical CUDA13.0 table preserved and no comments. All three PR-body files match. Root changed four prose passages after integration's reviewed9a559aaa draft: removing the immutable wording, clarifying N64's zero-row alpha read, identifying skipped upstream GPU CI pending authorization, and naming the exact preceding AUTO baseline/commit. The new performance table is unchanged from the independently checked draft.

The performance receipt3a298b42 had included the ancillary mutable PR draft path at its then-current SHA9a559aaa. Its original bytes and receipt remain unchanged. Root reconstructed those bytes by reversing exactly four edits; integration independently re-rendered the same bytes from saved body4034261b and complete results, and both reproduce the recorded SHA. [Root's reconstructed draft](logs/PR_BODY-alpha-full13-before-root-review-001.md) and [publication addendum](logs/cu132-recovery0909a-fc1-alpha-auto13-independent-publication-addendum-001.json), SHA `0f759c9603c9eecbb61498a1e1ecc65c917f1a609b7db4dedfa48c8b84499018`, explicitly state this reconstruction method and resolve that one historical path while verifying the other216 original evidence paths. No benchmark or runtime validation was rerun or weakened. Keep mutable PR drafts outside frozen runtime-evidence maps in future. Integration used only the saved local publication receipt, with no repeated GitHub operation.


### 037. Register redistribution: six numerical jobs pass; Mega-only timing pending

The frozen register runtime installs source `ed75c553c0fb5ab71337af0bbe279be7e8e461f23491f5185d7650e4b1e4e77f`, changing only private Mega kernel e00942e4 → 4208e13d from retained alpha487b. The numerical map is `46ebb31d2babd835a8df9dc935dca2c7558d63b725283b55a8fc66a1252a486b`; the separate performance map is `947b0903dfb07d047e958f65d98287b9d4dba6b7c83b2dffdd38a2a81a272e64`. Actual preflight4d6908 and approved receipt3bbaddb1 bind this source, both prior native-quality captures and installation. Performance owns all source/native/GPU work.

Original numerical PTY52551 exits0 with the exact UUID and six READY paths; final fetch89090 closes. [Completed summary](logs/cu132-recovery0909a-epi144-decode96-validation-sequence-001/summary.json), SHA `a285afd7975dd930d2103fb74f1a114cfc3735a546da2c31ed64ce68a09c34e8`, retains all 70 evidence hashes. [Independent saved audit](logs/cu132-recovery0909a-epi144-decode96-numerics-independent-final-001.json), SHA `b0a3e5ff8f91dde35d308cb4b83072c06d68a587aa45c4689f1ea19926558a1f`, invokes each of the six original reference/geometry validators once and verifies 125 consumed hashes, exact commands and loaded source/helper/preflight maps, result hashes, predecessor links and successful final launcher. All 44 rank-tests and 104 actual REG96 / 640 threads / two decode groups / pool61440 / local0 records pass. EP1 tests both return schedules for N128/N64; EP2 also covers the retained tiny/partial/ring-reuse cases and M128/N64 C1/C2. These public fixtures have four experts. No fresh split, host, lifecycle or sampler run is claimed. All 76 saved native entries remain identical to completed alpha AUTO cba7683d. Launcher receipt `180e8953ee3fa2b2373e0d5310ad87a3f71ddf22f3af480b7812bac3351c4f51` records 597.740714292 seconds for the managed numerical sequence, including its guards and excluding staging/fetch.

The first Mega-only CONTROL outer launcher96201 stops before GPU measurement because successful original validator diagnostic lines precede its dry-plan JSON. Performance preserves that failure and prepares a narrow outer-parser successor; no original driver, numerical gate, source, cache or timed call changes. The ready same-phase [report command](logs/cu132-recovery0909a-epi144-decode96-control13-report-command-001.txt) remains held until completed timing fetches. It uses retained alpha CONTROL, all thirteen Mega rows and 100 samples, with explicit removal of preceding split work and the resulting process-history difference. No completed CONTROL latency or promotion follows from numerical success.

Root also authorizes full Mega-only AUTO regardless of a mixed fixed result: actual CONTROL always selects M256/N128/F4/epilogue and cannot judge the changed N64 register allocation. The next raw-stage 5→7 candidate changes N64 on the primary shape, so it should go directly to full AUTO rather than repeating unchanged N128 CONTROL. The next baseline must be the actual retained AUTO source after the register decision. General Mega scheduling, communication-warpgroup, stage-count and weight/dequant overlap experiments have priority over cold scorer or decode microtrials. A future publication table may pair new current-best Mega rows with explicitly reused alpha split AUTO rows and both run/source provenances; no new split measurement is required for every trial. Published alpha commit2e8/body043ca352 remains unchanged.


Entry037 completed CONTROL subprocess and saved-only recovery. The initial outer-launcher96201 JSON parsing failure remains preserved. Its narrow successor uses the same run name, original driver9f0 and performance map947b; it reaches the benchmark under PTY1260. The benchmark subprocess completes with returncode0 and wall251.388635 seconds, retaining all13 Mega rows /13 arrays of100 samples /104 actual compiled records. The original controller then returns1 because parser abe86aa9 expects eight empty split recorder files and encounters FileNotFoundError. It never writes original `control.json`, `results.json` or final controller-owned `native-cache-after.json`; phase-specific execution/source/native-after files exist and were fetched. No GPU rerun is needed to read this completed measurement.

The original assumption was unsupported: the earlier CPU projection fabricated empty recorder fixtures without proving runtime creation. The preserved `capture_benchmark_tactics.py` writes rank JSON only in `capture_ep`'s finally, and only `_benchmark_distributed_ep` is wrapped. The benchmark's `variant.use_megamoe` branch calls `_benchmark_distributed_megamoe` directly and never reaches that split wrapper. [Separate v2 reader](candidates/w4a16_mega_only_screening_v2/saved_result.py), SHA `6793d0ca7671d10ca83ec37074659fd7bd35610b67e66efcd1f344df64967160`, handoff `436b27eff2ac4b6306cce78b2c746e2c918e9fe77ad9deff995a673dd8541b49`, requires explicit full13 Mega-only EP, rejects split/other CSV rows and every rank JSON path including empty files/dangling symlinks, and accepts the actual absence. Original AUTO winner/cache validation and full13 finite raw validation ASTs are unchanged. Actual fetched CONTROL raw plus focused CPU negatives pass; independent call-site/final-reader review passes. This is not an actual AUTO result, and no frozen parser, controller, source or run artifact was modified.

[Recovered same-phase table](logs/cu132-recovery0909a-epi144-decode96-control13-comparison-001/README.md), SHA `f36e7e97f759fe53470c8979b7c76cc47027cf89efedf0f3101eb64ae04dd244`, and [comparison](logs/cu132-recovery0909a-epi144-decode96-control13-comparison-001/comparison.json), SHA `f662940b84b426140810564695c41e0bd2c01e47f8aaabb8de137c64a5c3d8b0`, rerun the original candidate source/preflight/resource/MRO/timing-sample/provenance checks with only v2 raw/recorder parsing, then reuse the exact prepared before/after math. Retained alpha CONTROL is revalidated independently by its sealed saved reader. The separately derived result16a0929f sits inside the comparison folder, not at original result paths. All104 actual fixed configurations agree: M256/N128/F4/epilogue. Both sources'208 records remain local0. The comparison retains54 evidence hashes and explicit GPU0/controller1 and unpromoted/unrun-AUTO status.

| Tokens | Previous Mega ms | Current Mega ms | Change | Previous/current |
|---:|---:|---:|---:|---:|
| 1 | 0.092977 | 0.088320 | -5.009% | 1.052729× |
| 2 | 0.118817 | 0.117680 | -0.957% | 1.009662× |
| 4 | 0.134641 | 0.134562 | -0.059% | 1.000587× |
| 8 | 0.170658 | 0.169457 | -0.704% | 1.007087× |
| 16 | 0.180017 | 0.187649 | +4.240% | 0.959328× |
| 32 | 0.198849 | 0.212482 | +6.856% | 0.935839× |
| 64 | 0.234866 | 0.231298 | -1.519% | 1.015426× |
| 128 | 0.252371 | 0.231347 | -8.331% | 1.090876× |
| 256 | 0.255698 | 0.244001 | -4.575% | 1.047938× |
| 512 | 0.251970 | 0.260082 | +3.219% | 0.968810× |
| 1024 | 0.279635 | 0.268562 | -3.960% | 1.041231× |
| 2048 | 0.353090 | 0.350676 | -0.684% | 1.006884× |
| 4096 | 0.519910 | 0.512402 | -1.444% | 1.014653× |

Candidate/alpha CONTROL geometric-mean latency is `0.9892844254000595`, 1.0716% lower, with10/13 lower. T16/T32/T512 regress4.240/6.856/3.219%; all thirteen values remain above. Candidate Mega timer-utility wall is6.244132766 seconds versus reused alpha Mega5.905688749 seconds. Candidate process wall251.388635 seconds is separate from alpha's paired313.248735 seconds: removing preceding split setup/tuning/measurement changes process history. Canonical weights/input/routing and the primary cold-L2 CUPTI metric remain unchanged, but the wall delta is not a controlled kernel saving and no drift adjustment or row minimum is used. Fixed N128 cannot assess the candidate's N64 budget; fullAUTO remains necessary before retention.

Box0909a disappears after successful live source/native/idle/recorder-absence command70514 at `2026-09-09T07:11:44.491853+00:00`, before fetching its canonical remote JSON file. The full successful object is durable in [command stdout](logs/cu132-recovery0909a-epi144-decode96-control13-recovery-idle-command-001.log), SHA `e39a4fb1ee5d126fd5566df3055464f3a9ec6707c4988356c097d622e66291a4`. It binds exact manifest8d720a61, rawaff3cf4a, executionf395a5a5, sourceed75, preflight4d6908, empty GPU/native workers, the existing empty tactic directory and all eight absent rank paths. Its reported live inventory equals the fetched phase native-after cba7683d, unchanged across all76 entries. This is saved stdout evidence, not a verified canonical remote-file hash or a current live owner. The original controller failure receipt is da4dfd56. AUTO never launches; register is not promoted, alpha commit2e8/body043ca352 stays published, and root requests a replacement node. Integration made no remote/native/GPU/source or PR changes.


Entry037 recovery cross-check and successful replacement. Performance's separate [recovered result](logs/cu132-recovery0909a-epi144-decode96-control13-recovery-001/recovered-result.json), SHA `1cf64a3fe98e2202f0d3b594bef6dc9223d68878de134aef5667ac75ff943e26`, with only its added job key removed equals integration's independently derived result16a0929f exactly. [Recovery receipt](logs/cu132-recovery0909a-epi144-decode96-control13-recovery-001/recovery.json), SHA `e1660411a15907c24eeabe09ac50a3604d7d5d388500ab1d576d7478f4b703f9`, verifies128 saved hashes and retains GPU subprocess0 / controller1, stdout-only idle evidence and lost-node status. Its first local path-normalization failure is preserved. This cross-check uses the already validated saved output; no numerical or GPU rerun is made, and the original run still has no original control/results files.

The user clarifies that the managed `/usr/local/bin/h` may run with an effort-owned HAI checkout as its working directory. The restriction is on the executable, not that cwd. Root's provision attempts001 and002 stopped because the managed CLI requires HAI checkout context; those logs remain unchanged (SHA4acab99d and c08e91b9). Root then runs the same managed binary from the project-local `hai/` checkout. [Request003](logs/cu132-recovery0909b-devbox-request-ziangli-003.log), SHA `7d450f461491098fffee817b7075785448150da5f03e725514def2c72b757870`, completes under original PTY35973 with exit0 in39.8 seconds and reports `fi-w4a16-mega-0909b` READY in c2/ziangli with eight B300 allocated. The image is explicit `nvcr.io/nvidia/pytorch:26.05-py3`; bare mode skips code sync/bootstrap, and no size override is supplied. Successful003 supersedes the earlier provisioning blockers without rewriting their evidence. Root reports public GitHub identity restored and verified as zianglih; integration performs no additional GitHub or HAI call.

Performance now exclusively owns 0909b setup, source, native caches and GPU execution. Fresh source/environment admission remains required; READY is not a completed setup or benchmark. The minimal replacement starts from published alpha commit `2e8dc30df5efaf7dd1b7bf1771e72711c033d383` / source487b. The agreed sequence is one fresh alpha Mega-only AUTO100 full1–4096 baseline, register AUTO100 on the same node, retain/reject register, then raw7 AUTO100 against the selected retained AUTO. There is no repeated fixed baseline or split timing. Current-source/runtime review is local and parallel, not a redundant GPU gate; old0909a cache inventories and results remain historical rather than live new-node owners. Alpha stays retained and the PR remains unchanged.

Entry037 replacement preparation review. The minimal0909b setup handoff `d04934c44f712c490354fee914158ee6b448dab2894635fdf4d8d4cd2f055446` passes integration's bounded local review: all20 staged union files match, stage transport is AST-identical after the sole recovery-label substitution, environment/image/package helpers are byte-identical, environment data differs only in node descriptions, and setup command changes are only published source/path/label substitutions. Bootstrap and source guard require clean commit2e8/source487b, no overlays, the full existing inventory/four helpers and exact initialized submodules. Explicit systemPATH/CUDA13.2, original CUPTI dispatch ownership and actual imported-source checks remain. Actual new-node setup success is separate and still performance-owned; no remote/native/GPU operation or duplicate public suite is run by integration.

The fresh four-job runtime receives only [inherited_public.py](candidates/cuda132_recovery_0909b/performance/inherited_public.py), SHA `249563cfef652be9c9aef4706bdc8c243d7f30ce83bf76569bd86e6f38eb410d`, and its [association](candidates/cuda132_recovery_0909b/performance/inherited-public-evidence.json), SHA `e0483723f432c000f50b3498785c31057cfcc3b742c51b7810a8c6b0c03d7e77`. The API hashes only the already verified historical summarybd300 and independent receipt715ad, checks exact source487b / six jobs /44 rank-tests /104 local0 records, and compares stable loaded toolchain/import fields to the supplied preflight. The fresh runtime's existing full source snapshot and approved environment gates remain authoritative; imported decoder/Mega preflight fields alone cannot attest the changed alpha epilogue. A historical-preflight CPU fixture passes, changed native hash and imported module map reject, and Ruff/format pass. These are association checks, not fresh numerical execution or traversal of the historical raw/helper/native ownership closure.

For any later current-best PR, root requests final design/current exact-source validation and raw outputs, required CUDA13.0/host boundaries, one currentCUDA13.2 table and unchangedCUDA13.0 table. Historical sampling-prefix/timer-utility diagnostics and prior-trial narrative remain here in the ledger. No new draft or publication is requested until a new complete AUTO best exists.


Entry037 fresh0909b setup and four runtime gates complete. [Setup completion](candidates/cuda132_recovery_0909b/completion.json), SHA `5e987b9b91756455b077244676ed502c7c12ff799f2b5db94cdbb7c5ae335bc7`, records successful original staging78547, bootstrap74713, setup93042 and fetch96997. Clean published commit2e8/source487b is verified on hu-pdx-115 with eight B300 and explicit `nvcr.io/nvidia/pytorch:26.05-py3`; system CUDA13.2, Torch2.12.0a0+5aff3928d8.nv26.05, DSL4.7.1/native13.3 direct decoder and exact native extension bb367e30 remain pinned. The recurring physical hostname does not import old0909a native ownership. Actual preflight `8b6f5ff46e8b623ccf594287bfa50187a34d36ad24d9aeb9b182d10dede289eb` and approved829d6af7 bind the new source/environment. Compact historical alpha numerical association e0483723 passes this actual preflight without rewalking the older public raw suites.

Original four-job PTY53361 exits0 and final fetch79264 closes. [Summary](logs/cu132-recovery0909b-alpha-validation-sequence-001/summary.json), SHA `399cbb037a4962a892e7ecdbe8dc95aa331b8b6075edb4cbf44a2e157f066668`, and [launcher receipt](logs/cu132-recovery0909b-alpha-validation-sequence-001.launcher-exit.json), SHA `deb30c6a54fb66ce1015e2b31e788c88f442f8631d1f97040f95f5d5a8bc6106`, retain all four ordered paths, no progress errors and the actual UUID exit0. [Independent saved audit](logs/cu132-recovery0909b-alpha-four-gates-independent-001.json), SHA `9b911b8d31fef0a4e96001ee5eecdf602c1eed1ece1cbef3fde385c754cbbeb0`, runs each original output validator once and checks58 summary files /116 consumed hashes, exact commands, source snapshots/provenance, helper maps, approved preflight and immediate native predecessor links. The no-Mega EP2 resource probe contributes2 records, lifecycle EP1/EP2 contributes18/36, and sampler EP2 contributes2: all58 actual records are REG96,640 threads,two decode groups,pool61440,local0 with the original shared MRO/decoder identity. Lifecycle checks32 nonempty and16 empty candidate outputs across catalog16,9 stable and3 changed-input graph replays. Sampler retains32 replay calls,6 resets and8 measured samples across success, peer-capture failure and recovery. No fresh public suite, host test, live cache check or GPU rerun is claimed by this audit.

The first fresh job starts with empty native directories; each later job's before inventory equals its immediate predecessor's saved after inventory. Final native SHA is `fc2998ca78092cf27d9986ef3534cb58a9cc85667a7c8b1868c98296e1a241a4`. Numeric map `9bbb28cb3f81d4ecd931cce245adbd542f65d788fc7b22d76bd8558961f4b06f` binds47 files; the separate performance map `3493bb9560fc7839ae383fc87529c648c7bd3023838b675c80ca3eb59726c3f9` binds53. Both maps match their saved inputs. Driver `e9d08f986c2cdca59520789fae1a862ac171f7cd015d5b8aa7b1a6a491f1be7e` admits only full13 Mega-only AUTO100, uses v2 absent-split parsing plus original resource/choice/ranking/sample checks, and reuses only the final fresh sampler's native directories while creating fresh DSL/driver paths. It does not import an old performance or CONTROL owner. The bounded independent source review finds no blocker.

Performance has launched original70476 for the fresh alpha Mega-only AUTO100 baseline while this saved audit completes; full performance remains pending. The next comparison must use this fresh0909b alpha AUTO versus0909b register AUTO, followed by a retention decision and raw7 AUTO against the selected retained source. No repeated fixed baseline or split sweep, new acknowledgment gate, source mutation or PR change is added. Root's new unapplied `candidates/w4a16_alpha_public_cleanup` is the current comments/docs/four-test successor for a later publication window; it preserves runtime ASTs and timing source labels and supersedes the older combined195946 cleanup as a preparation choice.


Entry037 fresh same-container alpha AUTO baseline completed. Original70476 exits0 with the exact UUID marker; full fetch62062 and canonical idle/fetch52358 close. [Manifest](logs/cu132-recovery0909b-alpha-auto13-001/stack-manifest.json), SHA `38c40193bdc3f926d0087a9310aa403564ecfefa329694c61d0399bb7f5a7c76`, [results](logs/cu132-recovery0909b-alpha-auto13-001/results.json), SHA `44d257f6debdd72ff0704d4fab03ea0d1e0077d5a1c6695e8915c3ead16934b8`, and [closure](logs/cu132-recovery0909b-alpha-auto13-closure-001.json), SHA `3ef9db4dc101e69e205c5dfb583bcd328a4ca2dfc947f99e78129174b363f20c`, bind published alpha2e8/source487b on the new0909b container. Original driver e9d08f98 and performance map3493bb95 retain the actual V2 Mega-only path, all thirteen token counts and100 samples.

[Accepted baseline](logs/cu132-recovery0909b-alpha-auto13-baseline-001/accepted-baseline.json), SHA `d80825c1742a2456f564e6578ff258ce174bb339c5589c43fbacd61c8d61d2bf`, is a compact saved comparison receipt containing all13 rows,104 actual winners and74 direct file hashes. One execution of the current original V2/raw/resource/MRO/sample/provenance/winner/ranking/cache validators reconstructs the entire saved `auto.json` exactly. Counts are13 raw rows, no split recorder files or split rows,104 rank-confirmed winners and compiled records,13 complete sixteen-candidate rankings,1,300 samples and10 final capacity buckets. All104 actual records are REG96 /640 threads /two decode groups /pool61440 /local0. Every100-sample median agrees with its six-decimal raw line. The already completed fresh four-job summary399c and independent audit9b911b8d supply direct numerical association; neither those jobs nor older public suites/controllers are rerun.

| Global tokens | Alpha Mega ms | Actual selected tactic |
| ---: | ---: | --- |
| 1 | 0.093617 | M128/N64, C1, F4, epi |
| 2 | 0.120785 | M256/N64, C2, F4, epi |
| 4 | 0.131585 | M128/N64, C2, F8, epi |
| 8 | 0.154864 | M256/N64, C2, F4, epi |
| 16 | 0.158690 | M256/N64, C2, F4, epi |
| 32 | 0.205185 | M256/N64, C2, F4, epi |
| 64 | 0.227841 | M256/N64, C2, F8, epi |
| 128 | 0.235425 | M256/N64, C2, F8, epi |
| 256 | 0.230385 | M256/N64, C2, F4, epi |
| 512 | 0.235474 | M256/N64, C2, F4, epi |
| 1024 | 0.285155 | M256/N64, C2, F8, epi |
| 2048 | 0.347970 | M256/N128, C2, F4, reuse |
| 4096 | 0.499300 | M256/N128, C2, F4, reuse |

The [complete baseline table](logs/cu132-recovery0909b-alpha-auto13-baseline-001/README.md), SHA `37ee64f563087df324be826a7ffcf13e53e03964d2d522fd61912cfebba2135a`, uses the original median of100 per-iteration maximum-rank cold-L2 graph-CUPTI activity spans after3 warmups. Tactic scoring remains hot staged W4A16 wrapper plus post-FC2 reducer, excluding public staging/routing preparation; it is a distinct metric. Actual benchmark subprocess wall is899.1776187079959 seconds; summed timing utility is5.848272062001342 seconds. No shortened-sample trial, phase-cost attribution from the remainder, split timing, row minimum, historical paired/fixed substitution or source promotion is introduced.

Fresh saved native-before fc2998ca equals the immediately preceding sampler's after inventory and roots. Final native inventory `055618ecfc9f530f058009845beb7ee099d0cf4215aa3e59f916d0f3104995b8` equals the phase after inventory. Exact-object comparison retains all entries:12→22, ten added dsv3_fused_routing build files, only the included JIT log changes among existing paths, no removals. Canonical idle `3332b58d99ce5c91c985488059886bf3d0bd85f9f48e8e0df7ae49d8b9974385` verifies the exact final source/native inventory and empty GPU/native workers at its captured boundary. Original launcher83dbc751 and phase executionb91c5f05 both pass, and all owned sessions/fetches close. The integration audit is saved-only and makes no new live-cache claim.

Performance proceeds with register installation and full Mega-only AUTO100 without waiting for this independent reread. Its comparison must reuse this exact0909b alpha AUTO baseline, then advance the retained baseline if register is selected before raw7 AUTO. Published alpha source/PR table remains unchanged by this baseline measurement alone. No remote/native/GPU/source or PR operation is performed by integration.


## 038 — Register AUTO retained; source/PR association and raw7 preparation

Recorded 2026-09-09T08:42:14Z. The fresh same-container register AUTO finishes under original
PTY46136 with the exact UUID/phase-ready marker and exit0; canonical final
fetch82602 and idle/fetch71865 also close0. This run has successful original
benchmark and controller completion, unlike the separately preserved lost-node
0909a CONTROL reader failure. No analysis recovery or synthetic result/rank
file is used here. Performance owns every remote/native/source/GPU action;
integration reads only completed local artifacts.

The actual run is `cu132-recovery0909b-epi144-decode96-auto13-001`, measured
source `ed75c553c0fb5ab71337af0bbe279be7e8e461f23491f5185d7650e4b1e4e77f`,
preflight `e691199cb96016944fb964efb239eed0a4c35d0b5d9be57349d1247ce48d6802`,
performance map `db804391cc055e90ee6012855da47274633aa56ed4e928d8ff90bd420a0f7413`.
[Manifest](logs/cu132-recovery0909b-epi144-decode96-auto13-001/stack-manifest.json)
has SHA `8c70f077d73f4e6a7d76bd513ffab5d93f690a39100f76993ade732f67ac3adb`;
[results](logs/cu132-recovery0909b-epi144-decode96-auto13-001/results.json)
has SHA `e305223da0f57e495c97c80f1a1b9fbaf0baf960f2bcf54246c0cc93acd31c75`.
Execution SHA is `0e3d171eb5f3165a72060a14267355738c12989ca49e6af50f7e6c356a7e5cce`;
original outer receipt is `2ba40f7cdc0536ca44e764229a660f44afd8486d4382e2ba7b39e74f08c9dfe7`.

The [complete independent comparison](logs/cu132-recovery0909b-alpha-vs-register-auto13-comparison-001/comparison.json),
SHA `574cf11e6f24d8906600ac6effacf5d291a67dde818310a06475b4d02af0c74c`, checks
111 direct hashes and reconstructs candidate auto.json exactly through the
current original V2, raw, resource/MRO, sample, provenance, winner, ranking and
cache validators. Accepted alpha baseline d80825c1 is consumed by direct
integrity checks and its retained rows/choices, without rerunning baseline
validators or walking older controllers. Both runs preserve13 raw rows,
104 actual choices and compiled objects,13 complete catalog16 rankings,
1,300 post-rank-MAX samples and10 final capacity buckets. Every sample median
agrees with its six-decimal raw row. All208 resource objects retain REG96,
640 threads, two decode groups, pool61440 and local0. The source delta is
exactly Mega kernel e009→4208 across the full1,572-file inventory; unchanged
canonical weight/input preparation and hot staged-wrapper/reducer scorer are
retained. The current-source numerical association binds the already audited
six-job summarya285/reviewb0a3 and loaded environment; it does not rerun them.

| Global tokens | Previous alpha Mega ms | Current register Mega ms | Change | Previous tactic | Current tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.093617 | 0.082961 | -11.383% | M128/N64, C1, F4, epi | M128/N64, C1, F4, epi |
| 2 | 0.120785 | 0.109761 | -9.127% | M256/N64, C2, F4, epi | M128/N64, C1, F8, epi |
| 4 | 0.131585 | 0.130481 | -0.839% | M128/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 8 | 0.154864 | 0.142034 | -8.285% | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 16 | 0.158690 | 0.168225 | +6.009% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 32 | 0.205185 | 0.201377 | -1.856% | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 64 | 0.227841 | 0.218049 | -4.298% | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 128 | 0.235425 | 0.222354 | -5.552% | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 256 | 0.230385 | 0.227202 | -1.382% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.235474 | 0.239698 | +1.794% | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 1024 | 0.285155 | 0.271025 | -4.955% | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 2048 | 0.347970 | 0.347571 | -0.115% | M256/N128, C2, F4, reuse | M256/N128, C2, F8, reuse |
| 4096 | 0.499300 | 0.502692 | +0.679% | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

Register/alpha geometric-mean latency is `0.9686392416280418`, or3.1360758%
lower. Ten of thirteen points are faster; T16/T512/T4096 regress6.009/1.794/
0.679%. Seven actual tactics change. Both runs use the same0909b container
on hu-pdx-115, eight B300, image `nvcr.io/nvidia/pytorch:26.05-py3`, full13
Mega-only AUTO100 and the original median of per-iteration maximum-rank
cold-L2 graph-CUPTI spans after three warmups. Sequential, unbracketed tuning
prevents an isolated fixed-tactic causal claim. No row minimum, drift
correction, split timing or fixed-vs-auto substitution is used. The complete
[table](logs/cu132-recovery0909b-alpha-vs-register-auto13-comparison-001/README.md)
has SHA `93d757c3f93411e01c2997bba42223e0209d527f7df5659b97a98a6b8bc8cc82`.

Candidate process wall is877.625750437 seconds versus alpha899.177618708;
timing utility is5.781311815 versus5.848272062 seconds. These wall totals do
not establish compile/autotune cost from their remainder. Keep100 samples and
all13 token sizes; no reduced-count GPU experiment is added.

Canonical [idle](logs/cu132-recovery0909b-epi144-decode96-auto13-idle-001.json)
SHA `2a4e4c0a24d2cded407569e27ac8895f69c25c65aa9b3f1d3a02288d360ebd30`
and [closure](logs/cu132-recovery0909b-epi144-decode96-auto13-closure-001.json)
SHA `7499557d8e5df04f103ec360a47a1b565c9eb48eadc8e456a055bd2d3c38b09a`
record empty GPU/native workers, exact source/helpers and native inventory.
All22 native entries are byte-identical to alpha final inventory
`055618ecfc9f530f058009845beb7ee099d0cf4215aa3e59f916d0f3104995b8`, including
the JIT log. All owned sessions and canonical fetches close. This audit uses
the captured boundary, not a new live-cache check.

Root retains register after reading the full table and sends it to the user.
The sealed report's original pending-retention field stays unchanged; this
ledger records the subsequent decision. Root commits and pushes
`0109c39368acca7fe6e6d8d811f6f5e9270b2b72` to fork/feat/w4a16-megamoe.
The commit's full source ID
`f5dcb31c7100149fca17872d933944f5af79aabe644681b42dba5b6ea85daccc`
differs from measureded75 only by a frontend comment. Integration checks the
frontend runtime AST against2e8 and the committed kernel's exact measured
SHA4208. Root's executed pre-commit log `logs/pr5019-register-precommit-001.log`
passes all applicable checks, including mypy, Ruff and formatting. No claim
of a benchmark on different executable source is introduced.

The proposed [PR body](PR_BODY-register-full13.md), SHA
`3795d8c041bd6ad73270c4d3a9d07d023a14325606e2888133ff830dd12721a6`, combines
current register Mega AUTO with unchanged alpha split AUTO rows from
`cu132-recovery0909a-fc1-alpha-auto13-001-auto`, source487b/commit2e8. Both
run/container identities are explicit; this is not a fresh paired table.
Current Mega beats the reused split column at12/13 points, only T32 below
parity0.9824×; T4096 is0.502692ms and1.1968× the reused split. The separate
direct Mega-before/after paragraph carries the3.136% improvement and all
three regressions. Current six-job raw test summaries and the four alpha
runtime PASS summaries are included with their actual source labels. The
CUDA13.0 table and PR checklist remain byte-identical; historical timing
utility/prefix/profiling chronology is condensed out of the body and retained
in this ledger. Local draft proof is
`logs/pr5019-register-body-review-001.json`, SHA
`6794a7ee0827137489b855e08aa80949185d4333b2ba10d386c16ee4ca2294d0`.
Root owns GitHub publication; no new body publication is claimed at this point.

Raw7 preparation is complete and independently source-reviewed under
`candidates/w4a16_raw_ceiling7_validation`, handoff
`19ba07dfe4161cc022ef7e9fae98ab00d62904028a10fbe050d615f5f1da8156`.
The three focused helpers are raw_stage_observation.py282840b3,
geometry_c1_flag8_test_plugin640.py0179a39f and reference_subset.pya74d8333;
run-plan185188cf and READMEecd294c2 bind the five proposed jobs. One isolated
copy of the original public test adds only the normalized H7200/I2112/M257
geometry; original oracle function bodies and tolerances remain unchanged.
The observer delegates the original fitter once, returns its exact pair,
and records actual fitted depths/layout/storage in the compiled object.
Ceiling7 does not imply observed depth7: actual resource observations must
bind the selected source, geometry and layout. Source predictions are
explicitly distinct from execution.

Proposed jobs are M256/N64/C2 EP1 (both references plus wrap geometry),
M256/N64/C2 EP2 (both references plus wrap and H9472 fallback), M256/N128/C2
EP2 (both references plus fallback), and M128/N64 C1/C2 EP2 (both references).
Expected totals are25 rank-tests and79 objects, not completed tests. Existing
reference schedules supply balanced/skewed/sparse/all-empty/refill behavior
and three stable plus one changed graph replay per reference rank-case.
H7200/I2112 gives29/9 K256 tiles with partial tails, so it exercises the
within-FC raw7 wrap that short reference shapes do not. H9472 intentionally
checks raw6/raw4 fallback; exact fitted storage and per-FC depth must be
observed during future execution. No extra catalog16 lifecycle rerun or
synthetic decoder test is requested. Native/actual numerical success remains
pending, and performance owns the retained-register raw7 binding/transition.

Execution policy follows the user's latest direction: all future trials use
full13 Mega-only AUTO100 against a reusable actual retained Mega AUTO baseline.
After the register decision this baseline is the completed0909b register run,
not hardcoded alpha. No additional CONTROL/fixed/split runs are requested
unless evidence invalidates reuse. Frozen scheduler-depth README wording
'adjacent controls' and no-peek wording 'fixed or AUTO' are superseded policy,
not reasons to add a new gate or rewrite frozen candidate hashes. Prioritize
Mega scheduler/communication-WG/stages/weight-dequant overlap before cold
scorer or decode microtrials. No2048-specific or CUDA13.0 work. Independent
saved audits run alongside native/GPU progress, without a second acknowledgment
hold. Integration makes no remote/native/GPU/source/GitHub operation.


Entry038 root body review corrections. The unpublished draft initially mislabeled
historical6315 profiles as CUDA13.0 by inferring from the cross-stack source
label; root caught that incorrect attribution. The amended profile section
uses the actual experimental f377 CUDA13.2 EP8 NSYS global32/4096 and standalone
EP1 NCU T4096 evidence, exact source and recorded effort-harness commands. It
keeps EP1 local-shape, sampled-count, unresolved-source and NVTX limitations
explicit and makes no current-register profiling claim. The Compute bullet
also explicitly includes M128/N64 cluster1. Current draft SHA `4606c2c7946152321e974f8198e4440004069ad23a4d1b8583597cf9b5081c96`;
review002 SHA `7ccb9950f80309c6622bcbca4df6f4936d6342e547238f43b42530e627c6f62f`. The original review001 remains historical and no frozen
runtime artifact is changed. Root independently confirms current-head precommit
and BuildDocs success; GPU CI remains skipped pending repository run-ci label
authorization, rather than a numerical failure. Publication remains root-owned.


Entry038 publication closed. Root's [publication receipt](logs/pr5019-register-publication-001.json),
SHA `d9bdf95eb8452b3128d3cda43a7e7dcafdb34bffcfd745644abdedf82329ebf1`, verifies PR5019 remains draft at0109,
body `4606c2c7946152321e974f8198e4440004069ad23a4d1b8583597cf9b5081c96`, at2026-09-09T08:46:51.328600+00:00.
Canonical PR_BODY.md/current-modern and the prepared draft are byte-identical.
The body preserves one current132 table with explicitly reused alpha split,
unchanged130 and the repository checklist. Current-head precommit/docs succeed;
GPU setup/matrix is skipped because the synchronize event did not apply run-ci.
No comments or CI trigger were posted. Integration reads only this saved receipt
and updates local publication bookkeeping, without another GitHub operation.


Entry038 next scheduler validation is prepared without new executable helpers.
`candidates/w4a16_fc1_scheduler_nopeek_validation/selector-plan.json` (SHA
`94cbb0aa9f6c2933377b5720b8c8584ad5f0f306b993f1fffd8220f68a68952f`) drops
the raw7-specific geometry rows from the same five geometry/EP jobs. Only the
two existing reference_schedule return modes remain:18 rank-tests/72 objects,
with54 stable and18 changed-input exact graph comparisons and18 six-round
empty/refill sequences expected. Source inspection confirms four layers per
case and unchanged original oracle/tolerances. These are planned counts,
not new numerical observations. Use the existing private reference validator
branch, because the full raw7 dispatcher still requires geometry/flag8 rows.
Observer/fitter ceiling follows the eventual raw7 verdict; no source/base/owner
is preselected. No new all16 lifecycle, sampler, split or host rerun is proposed.


## 039 — Raw7 retry numerics complete; first NVSHMEM failure preserved

Recorded 2026-09-09T09:24:41Z. Root/design accepted the separate N128/N64 native quality
review before execution (final receipt 77e52248). Experimental source is
`e9b752c8f6f2a9394123d964d3c3ed04376ec889f326a72245b7f53362b322c2`, with
Mega kernel `bcb121a8d9c5b8f0b859c3d50c0dc9d99a958c210492b207058f2203ccc79349`
on the retained register base and published frontend comment. Actual preflight
`99c30d5829951172f4de748968f34bfde12f8851c03679abc5804dcd3beb3a1a`, approved
receipt ba098c4c and numeric map
`b17244947403ba798c6611f33250dc3c93cd4016376d3d1e10ef7a5d6fc9ac9a`
bind the source and original five-job payload 19ba07df.

First attempt 53180 failed with controller 1 / pytest SIGSEGV11, after live
source/native/idle admission. The first epi_warps reference case completed;
the second return case completed its initial numerical and partial-tile
checks before NVSHMEM host initialization failed during the seventh layer
construction, before that layer's resource/config record. The stack passes
through nvshmemi_get_devices_by_distance, setup_connections and common_init.
The new fitter observer delegates once and records plain JSON values; the
bounded source read found no retained CuTe/native object or concrete observer
lifetime fault. No helper/kernel root cause was established, and prior memory
corruption was not ruled out. This is not a completed numerical sequence.

[Failure receipt](logs/cu132-recovery0909b-raw7-failure-001.json) SHA
`65cad479114d0529790c036f59aa59cecbb4a84d08172feb35ef3ab08e6a8ed5`
and all 15 declared files remain unchanged; failure log SHA d49eaf82, original
exit 8a0246b6 and idle c11a79d4 are preserved. The six partial compiled objects
are excluded from the retry totals. The recurrence-only init/finalize command
at `logs/cu132-recovery0909b-nvshmem-reinit-diagnostic-command-unused.md`
(SHA e5d917ab) remains unused after the authorized unchanged retry succeeds.

Retry1 original launcher 11194 completes with the exact
`FRESH_MODERN640_VALIDATION_deec109477d444489aa01d8e85e8babc_EXIT=0` marker;
final fetch 57898 closes 0. [Summary](logs/cu132-recovery0909b-raw7-retry1-validation-sequence-001/summary.json)
SHA `067fb5050c7aa384627471c02045c2ad8978da3a1aa0572538064dfb01316d06` and original launcher
`dc9f2b1b8d1c4ee7b1f506c52a4383139712a731a8014c8a5403f5a571030a84`
record the exact five jobs. Integration invokes the five original saved
output validators once, then checks source/input/helper hashes, commands,
setup/call/teardown reports, immediate native predecessor links, summary and
outer completion. No native/Torch/pytest execution or live inventory read is
performed. The [independent audit](logs/cu132-recovery0909b-raw7-retry1-numerics-independent-001/audit.json),
SHA `dac647e0bd3b38b3deaadde1e8b86cbd73ec4d6bfb9275d995bd820d49bca0b2`, checks all 59 summary files and 137 direct hashes.

| Geometry / EP | Passing rank-tests | Compiled objects | Result SHA prefix |
|---|---:|---:|---|
| M256/N64/C2 EP1 | 3 | 9 | fd096613 |
| M256/N64/C2 EP2 | 8 | 20 | 47880c88 |
| M256/N128/C2 EP2 | 6 | 18 | b9971748 |
| M128/N64/C1 EP2 | 4 | 16 | 970a98e2 |
| M128/N64/C2 EP2 | 4 | 16 | c646b127 |

All 25 rank-tests, 75 phase reports and 79 objects pass. Actual fitted depths are
75 raw7, two raw6 and two raw4; all objects retain REG96 / 640 threads / two
decode groups / register pool61440 / local0 and the exact shared transform/MRO.
H7200/I2112/M257 gives three observed M256/N64/C2 raw7 objects across EP1/EP2,
219904 B, FC1 K29 and FC2 K9 including partial tails. H9472/I64 gives N64 raw6
at 219648 B and N128 raw4 at 215552 B, two objects each. These are actual fitter
and layout observations accompanying successful original-oracle executions,
not predicted stage counts. Public fixtures use four experts/top2.

The 18 completed original reference cases cover both return modes and six
numerical rounds (balanced, skewed, single token, empty source, all empty,
refill), exact sparse scale/routing, and graph replay. Their unchanged bodies
entail 54 stable and 18 changed-input graph comparisons, rather than separate
instrumented replay counters. The added long-K fixture separately verifies
normalized partial-K numerical wrap; no long-K graph/empty-refill claim is made.
All five native before/after inventories are byte-identical 055618ec, all 22
entries including the JIT log. Each job gets distinct DSL/driver paths and
reuses only its immediate completed native predecessor. No recursive retained
baseline validation is added.

Performance starts full 13-token Mega-only AUTO100 under original launcher 69085 alongside
this audit; last relayed progress is 3/13 through T4. Performance map
`b16b52e91d7b7444f2db3fa0db4e66cf9e9eb688a9e34e79a5d8f8549c594535`
and driver b9401df8 bind the successful retry summary, while failed attempt 65cad
stays historical. Compare directly against accepted retained register AUTO
574cf11e, not alpha or a repeated fixed/split sweep. Performance and retention
remain pending; PR5019 stays draft at 0109 / body4606c2c7. Conditional publication
wrapper `candidates/w4a16_raw7_public_wrap_test` is unapplied and selects the
measured N64/C2/flag8 geometry with the unchanged H7200/I2112/M257 oracle.
No production, runtime, remote, GPU or GitHub changes are made by integration.


Entry039 complete raw7 AUTO — rejected default. Recorded 2026-09-09T09:39:45Z.

Original69085 completes all 13 token sizes with 100 samples and the exact
`FRESH_MODERN640_FULL13_4dd9009fe3f44c5faa5521f637023320_EXIT=0` marker.
Full fetch19999 and canonical idle/fetch43372 both close0. The benchmark
subprocess and original controller succeed; this is not a recovered result.

[Manifest](logs/cu132-recovery0909b-raw7-auto13-001/stack-manifest.json) SHA
`0efbcc2605be853974b93734f045d21a9ac255a930459c1496dbbb4dc457d142`;
[results](logs/cu132-recovery0909b-raw7-auto13-001/results.json) SHA
`bcbc91feb298d71082804ee13bd625c5c6535def7b95f5e2d59aa28f41adc6e1`;
execution ee0b6cd7, original exit f87cbe46, canonical idle cf533a5f and
[closure](logs/cu132-recovery0909b-raw7-auto13-closure-001.json) SHA
`7fdbc43094f2d26a6fd0b71ea409f7cbb7830ac039327790c250b99b3a6b3437`
are saved. All 22 native entries remain byte-identical 055618ec, including the
JIT log. Source e9b7 and all frozen helpers match before/after and the captured
idle closure, with no GPU/native workers. The audit makes no new live check.

The [independent comparison](logs/cu132-recovery0909b-register-vs-raw7-auto13-comparison-001/comparison.json),
SHA `a7ce456ee484f10278b47d13318df8efeb2f3d00c40498696dfa75585fc2048d`, uses accepted register574cf11e current_mega_ms/current_choice
columns plus direct current-run file hashes. It does not rerun baseline
validators or traverse alpha/older owners. The candidate original V2 raw,
resource/MRO, sample, command/source provenance, catalog16 winner/ranking and
cache validators reconstruct auto.json exactly. All 13 raw rows, 104 choices
and compiled objects, 13 complete 16-candidate rankings, 1300 samples and 10
capacity buckets are preserved. Every sample median agrees with the printed
six-decimal row. The review checks 87 direct hashes.

| Global tokens | Retained register ms | Raw7 ms | Change | Speedup | Register tactic | Raw7 tactic | Actual raw depth |
|---:|---:|---:|---:|---:|---|---|---:|
| 1 | 0.082961 | 0.092593 | +11.610% | 0.8960× | M128/N64, C1, F4, epi | M128/N64, C1, F4, epi | 5 |
| 2 | 0.109761 | 0.101521 | -7.507% | 1.0812× | M128/N64, C1, F8, epi | M128/N64, C1, F4, epi | 5 |
| 4 | 0.130481 | 0.124721 | -4.414% | 1.0462× | M256/N64, C2, F4, epi | M128/N64, C2, F4, epi | 5 |
| 8 | 0.142034 | 0.155121 | +9.214% | 0.9156× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 7 |
| 16 | 0.168225 | 0.168930 | +0.419% | 0.9958× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi | 7 |
| 32 | 0.201377 | 0.203266 | +0.938% | 0.9907× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 7 |
| 64 | 0.218049 | 0.217570 | -0.220% | 1.0022× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 7 |
| 128 | 0.222354 | 0.232067 | +4.368% | 0.9581× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 7 |
| 256 | 0.227202 | 0.237907 | +4.712% | 0.9550× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi | 7 |
| 512 | 0.239698 | 0.242114 | +1.008% | 0.9900× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi | 7 |
| 1024 | 0.271025 | 0.261139 | -3.648% | 1.0379× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi | 7 |
| 2048 | 0.347571 | 0.345475 | -0.603% | 1.0061× | M256/N128, C2, F8, reuse | M256/N128, C2, F4, reuse | 5 |
| 4096 | 0.502692 | 0.508773 | +1.210% | 0.9880× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse | 5 |

Raw7/register geometric-mean latency is 1.0118975699679376, or 1.189756997%
higher. T2/T4/T64/T1024/T2048 improve; all eight regressions are shown above.
Tactics change at T2/T4/T256/T512/T1024/T2048. Actual selected raw depths are
64 raw7 objects and 40 raw5 objects. All 104 resource objects retain REG96,
640 threads, two decode groups, pool61440 and local0. The report keeps the
actual force_static_sched=true, num_sched_stages=null, clc_bundle_size=null,
group_hint512, atomic_counter, epi_flag_batch[2,4], disabled FC1 top-k
application/IKR/IKET/clamp and selected flags/return modes. The raw7 name is
a ceiling; it does not imply seven stages on every fitted selected geometry.

The metric and canonical input/weight path are unchanged: same 0909b container
on hu-pdx-115, eight B300, explicit nvcr.io/nvidia/pytorch:26.05-py3, three
warmups and 100 per-iteration maximum-rank cold-L2 graph-CUPTI spans. The hot
tuner still scores staged W4A16 wrapper+reducer, excluding public staging and
routing preparation. Independent sequential AUTO retuning prevents a fixed-
tactic causal claim; no minima, drift adjustment or split substitution occurs.
Measured ed75→e9b7 changes kernel4208→bcb1 and the previously associated
frontend comment e9eb→6e44. Shared decoder and benchmark bytes are identical.

Raw7 process wall is 885.368779664s versus register
877.625750437s. Timer utility is 6.049787905s versus
5.781311815s. The remainder is not assigned wholly to compilation
or tuning. Retain 100 samples and all 13 token sizes for future screens.

The first local saved closure assertion expected an empty list for
gpu_compute_apps, but the original helper records stripped nvidia-smi stdout
as an empty string. The final review checks that actual schema; no original
evidence, runtime/source or gate was changed. Original validation and exact
saved-result reconstruction pass. This reader issue is unrelated to the
preserved first numerical NVSHMEM failure65cad. Successful retry067fb and
its 25 rank-tests/79 objects remain separately associated through auditdac647.

Root rejects raw7 as the default after the complete before/after table.
Performance is restoring retained register f5dc and proceeding to no-peek on
raw5; this entry does not preclaim restoration or subsequent native results.
Raw7 source/native/functional evidence, possible explicit stage selection and
the conditional public N64 wrap test remain deferred and are not deleted.
PR5019 remains draft at 0109/body4606; no slower raw7 performance table or
public test is published. Integration changes only local reports/state/ledger.


Entry039 retained register restoration closed. Original27609 exits0 in
13.640146917 seconds; canonical fetch47844 closes0. The [remote receipt](logs/cu132-recovery0909b-restore-register-from-raw7-install-001/receipt.json),
SHA `b1a5ccbfda2269862586ed6a723c5a3254eb93f160be2e18e5dbbc3636b3b27c`,
and local receipt `e53f062f1234f616153292ff3cd147d645801f1f253c88a2b61ba7f3e8b2ea30`
record exact source e9b7→f5dc, changing only the Mega kernel bcb1→4208 and
preserving both raw7 backups. [Preflight](logs/cu132-recovery0909b-restore-register-from-raw7-preflight-001.json)
SHA `a8f5a1190a0debbcff39c687f6608228427765a2c81ee585d8a13437f818259c`
confirms loaded kernel4208, system CUDA13.2, native extensionbb367e30 and
direct BF16 decode. Integration checks these saved receipts and backup
hashes only; it performs no restore or live import. Subsequent no-peek native
and numerical work uses retained raw5 and remains separately evidenced.


Entry039 next no-peek adapter source review passes. Receipt
`logs/cu132-recovery0909b-nopeek-reference-adapter-review-001.json`, SHA
`e19e73a86c3e15e5446731a5ee18e87a7ae426a8a97ce0c08bc5d9964e7a0389`, records the exact seven helper hashes. Four payloads are
byte-identical to the retained 0909a register raw5 contract. The new runner
selects only the original two reference-return node IDs, uses checkout
rootdir so recorded tests/... IDs align, and retains all five geometry/EP
jobs. Expected totals are18 rank-tests/72 objects, with eight observed objects
per rank and exact setup/call/teardown requirements. Original resource/MRO/
local0 Counter reconciliation is AST-identical; _validate_reference_records
retains raw-stage2..5 and four paired layers per case. It does not invoke the
raw7 fitter or full geometry validator. Empty/refill, H288/I448/M257 partial
K and exact graph bodies/oracles/tolerances are unchanged. Two unsealed stale
raw7 labels were corrected by the author before the final reviewed hashes.
No new GPU/native/numerical test or approval gate is introduced, and these
counts are not execution results. Runtime source/install/preflight receipts
remain separately owned by performance/root.


## 040 — No-peek reference numerics complete; AUTO active; scheduler5 held

2026-09-09T10:07:07+00:00. The retained publication remains register commit0109/body4606.
The current no-peek trial is source
`02a1db353c03544e14c2a7f0d2998ed5e6506990037f4cabc92562d305983f7c`,
kernelbed245, with the retained raw5 fitter and register allocation. Its change
removes the scheduler FC1 readiness peek while retaining the actual activation
acquire wait and FC2 peek. Native quality is separately completed in
`candidates/w4a16_fc1_scheduler_nopeek_native_review/receipt.json`, SHA
`95e20d69a5184873c13436e43a916d9b8cd49f02ffa56527097b26ef5283f560`.
Integration reuses that receipt without a duplicate native review.

Actual numerical preflight0fc85c1e and numeric mapf269b580 bind source02a1.
Original84539 exits0 with exact UUID
`FRESH_MODERN640_VALIDATION_56f85a6219344e54bb11196005dbab9d_EXIT=0`,
all five ordered paths and no progress errors. Job3 fetch94508 and finalfetch78118
close0. Summary0868be3758eddbf76e5e5afe941a580ac2ce60ddb5dfc05bcb2fa65e376ccad9
and launcher cd0c5c7c2200b434d432ec3d1af285308b00a614590304e84e88a0964eb30df1
remain the original completed receipts.

[Independent saved audit](logs/cu132-recovery0909b-fc1-nopeek-numerics-independent-001/README.md),
audit SHA `62ecd4b43b4fb154bf1ae681f0094c24acc041183fabd1f3656e66e21ea74878`,
executes original fresh_session.validate_job_outputs once for each job:

| Geometry / EP | Rank-tests | Objects | Result SHA prefix |
|---|---:|---:|---|
| M256/N64/C2 EP1 | 2 | 8 | b63d149a |
| M256/N64/C2 EP2 | 4 | 16 | 50724732 |
| M256/N128/C2 EP2 | 4 | 16 | ff8e4eb8 |
| M128/N64/C1 EP2 | 4 | 16 | 6e38c06b |
| M128/N64/C2 EP2 | 4 | 16 | c4d0baf6 |
| Total | 18 | 72 | all passed |

All 54 setup/call/teardown reports pass. All 72 objects are raw5, REG96 / 640
threads / two decode groups / pool61440 / local0. Exact loaded source/helper
aliases, commands, source before/after and immediate native chain pass along
with 59 summary evidence files and 107 direct hashes. All five native before/after
files equal055618ec, including all22 entries/JIT log. No live inventory check or
historical baseline traversal is performed by this saved audit.

The completed original reference bodies cover both returns, ordinary empty/refill,
H288/I448/M257 partial K and exact scale/routing. They imply18 empty/refill sequences,
18 exact scale/routing cases and54 stable/18 changed graph comparisons; those graph
counts are derived from successful test bodies, not separate replay counters.
No stage-specific long-K/raw7 case, scheduler-stage observation or fitter allocation
claim is added. The first manifest native_cache_session_kind has stale register-AUTO
prose, while its actual native_predecessor/cache_policy correctly bind raw7 AUTO plus
restoration. The exact chain passes and frozen bytes remain unchanged.

Full Mega-only AUTO100 is active under original16294, run
`cu132-recovery0909b-fc1-nopeek-auto13-001`, UUID
`FRESH_MODERN640_FULL13_cb0f2bad523a4265b4ee677e15e6c10b`.
Launch JSONcb830e17 binds driver6f496035 / performance map60d9970a and completed
summary0868/outercd0c. Performance reports live/dry gates passed and the first
actual timing point emitted. The full13 final report will compare directly to
accepted register574cf current_mega_ms/current_choice. No alpha recursion, fixed
or split rerun, launch acknowledgment gate or preemptive retention is introduced.

Scheduler-depth3→5 source-only validation preparation is sealed in
`candidates/w4a16_scheduler_depth5_validation_preparation`, handoff
`86dc01e7cd6c12b3c2c3e17bde570dde4e7e66c22eb019654be96f2708462337`.
Validation patch310ef59c and AUTO observation patchf356e10a reuse the same five
reference jobs/18 rank-tests/72 objects and original timing/oracles/resources.
A small actual-fit observer (79ead99b) records scalar depth/storage facts inside
the original CuTe fitter call and returns its exact pair. Both kernel and scheduler
params must5, configNone resolves to5, raw candidates remain2..5, and decoded depths
remain distinct. The source control prediction is16*raw +16*decoded +48*5 +112;
scheduler metadata adds96 B. Original layout/communication/storage accounting and
deepest-fitting selection are checked against actual observations at future execution.
Patch-application/hash proof and focused pure negative checks pass, without native
imports or GPU work. Handoff execution_ready isFalse; selected base/source/owner are
None until the no-peek AUTO verdict. Root's stage5 register/no-peek source copies and
B3 source patch are separate preparation, not executed evidence. No production,
frozen runtime, remote source, PR body or memory was edited by this work.


Entry040 complete no-peek AUTO and default rejection. Original16294 true exit0,
full canonical fetch52780 exit0 and source/native/idle close54475 exit0 bind
manifest13684cb9756b97bca6f9c1da96591c155f46fc71e2240780039d50ae2d3fba35,
results1cbf8df31d6a2a444478031ac378fbd6e9e0a7ac35eeb40bedb8536a24276104,
executionc32c6a7e, outer2d191ce1 and idleb3b033c9. Canonical closure
`logs/cu132-recovery0909b-fc1-nopeek-auto13-closure-001.json`, SHA
`1f4b7c659c8624f804936413a61cd094024aaad9a28685e49beed2d87ff6b14f`,
records all owned sessions closed. Source02a1 and all22 native objects including
JIT log055618ec remain exact. This is the saved captured boundary, not a new live check.

[Independent comparison](logs/cu132-recovery0909b-register-vs-nopeek-auto13-comparison-001/comparison.json),
SHA `a3276ae8afdb35ef09c099d926469bd87c82f23cf504e0a2a83fb5cb3fbf0778`,
uses accepted register574cf current rows/choices plus direct baseline hashes, with
no older validator recursion. The current original V2/raw/resource/MRO/sample/
provenance/winner/ranking/cache validators reconstruct auto.json exactly. All13 raw
rows,104 compiled objects/choices,13 complete16-candidate rankings,1300 samples and
10 cache buckets are preserved. Every resource is REG96 /640 threads /two decode
groups /pool61440 /local0; all104 selected objects have raw depth5. Source before/after,
numerical summary0868/audit62ec, immediate native chain and original success UUID are
bound by75 direct evidence hashes. The complete arithmetic/choices exactly agree
with original report536fec7b00ba55ceab42fb48f79b0d91e771e438508263350c1b4d4195ec135f.

| Global tokens | Register ms | No-peek ms | Change | Speedup | Register tactic | No-peek tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.082961 | 0.090529 | +9.122% | 0.9164× | M128/N64, C1, F4, epi | M128/N64, C1, F4, epi |
| 2 | 0.109761 | 0.106689 | -2.799% | 1.0288× | M128/N64, C1, F8, epi | M256/N64, C2, F8, epi |
| 4 | 0.130481 | 0.135873 | +4.132% | 0.9603× | M256/N64, C2, F4, epi | M128/N64, C1, F8, epi |
| 8 | 0.142034 | 0.155953 | +9.800% | 0.9107× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 16 | 0.168225 | 0.170002 | +1.056% | 0.9895× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 32 | 0.201377 | 0.199395 | -0.984% | 1.0099× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 64 | 0.218049 | 0.217298 | -0.344% | 1.0035× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 128 | 0.222354 | 0.233746 | +5.123% | 0.9513× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 256 | 0.227202 | 0.241938 | +6.486% | 0.9391× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.239698 | 0.243922 | +1.762% | 0.9827× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 1024 | 0.271025 | 0.256403 | -5.395% | 1.0570× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 2048 | 0.347571 | 0.339059 | -2.449% | 1.0251× | M256/N128, C2, F8, reuse | M256/N128, C2, F8, reuse |
| 4096 | 0.502692 | 0.501605 | -0.216% | 1.0022× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

No-peek/register latency geometric mean is1.0184696646051195 (+1.84696646%).
Six points improve: T2/T32/T64/T1024/T2048/T4096. Seven regressions appear in full
above, including +9.800% atT8 and +9.122% atT1. Tactics change atT2/T4/T8/T64/T1024.
The report retains every actual selected M/N/cluster/flag/return knob and rank0
full config, with direct hashes of all104 original compiled records. Actual configs
retain force_static_sched=true, num_sched_stages=null, clc_bundle_size=null,
group_hint512, atomic_counter, epi_flag_batch[2,4] and disabled FC1 top-k application,
IKR/IKET/clamp. Shared decoder and benchmark are unchanged; measured register source ed75
versus no-peek source02a1 changes kernel4208→bed245 plus the previously associated frontend
comment e9eb→6e44. No change to canonical weights/routing/input preparation or primary
cold-L2 graph-CUPTI timing is introduced. The hot scorer remains the staged W4A16
wrapper+reducer, excluding public routing/staging preparation. Sequential unbracketed
AUTO retuning prevents a fixed-tactic causal attribution; there are no minima, drift
adjustments, split timings or fixed reruns in this comparison.

No-peek process wall882.349677081s and timer utility6.032989086s compare with
register877.625750437s and5.781311815s. The remainder is not treated as pure compilation
or tuning time. Continue full13/100 samples. The frozen manifest comparison_scope
still says Raw7; actual source, measurement purpose, driver and command identify
no-peek. That stale prose is preserved/disclosed, with no original runtime edits.

Root rejects no-peek as the default and requests exact restoration of registerf5dc,
then scheduler-depth5 register option8f116a49. Performance owns that transition;
this entry does not preclaim a completed restoration or native run. No no-peek PR
draft is created and register0109/body4606 stays published. No-peek source/native/
functional/performance artifacts remain available. The JSON report retains its
technical-reader pending-decision field; this ledger and report README record the
subsequent explicit root verdict without mutating the hashed report.

Scheduler5 preparation handoff86dc received a bounded independent source review:
atomic scheduler storage is48*n+32 bytes; enclosing control is16*raw+16*decoded+
48*n+112, so3→5 adds96 bytes before surrounding alignment. Actual kernel/scheduler
params depths are observed separately; only plain data is retained and the original
fitter pair is returned. No contract issue, native execution or edit was reported.
The earlier unbound handoff is preserved; the next runtime must associate root's
selected register base and actual restored checkpoint, not infer it from preparation.


Entry040 no-peek restoration and later host-layout preparation. The actual remote
restore receipt1f1ef8bbcbfadeff831ed643ac588642e0faaa18f82cb95c18f06e8ce2f7d67c
and locald2c447b39fe6821e093aae3493a6e5e511700aab57f6cafd6f1df20046453654
record passed02a1→f5dc restoration, changing only kernelbed245→4208. Both saved
backups rehash to the exact no-peek source. Original install/preflight exitd46656a5
is0 with13.586618459s wall, ending2026-09-09T10:17:50.080389Z; fetched preflight
b1616062ee2444e36184b5194f8e1d162a90ac18641b94566c41a5abf2a7ddb1 is retained.
These are saved transition receipts, not an assertion that source remains f5dc
after subsequent performance-owned scheduler5 work.

The B3 host-layout preparation is held under
`candidates/w4a16_activation_b3_layout_preparation`, handoff
`f6e46605cf7995665d2446f14f3a8cbcb2463b8001aada4a77ed855a851fe2ea`,
scriptf6b2211b0bced377d615c99239b619e5389663f2b58dc97a3cf7063ec75f81d4.
The existing n64_transform3 real-CuTe host harness produced224 configurations and
896 raw-depth measurements; the older stage_fitter harness produced552 cases.
The adaptation reuses their isolated modules, real MLIR context/layout/struct
sizing and original _smem_size/_fit_raw_stages. It changes the private B3 signatures
and three-value fitter return, with54 planned control/candidate fixtures covering
current shapes/both returns, M128/N128 B2 fallback and selected large-H admission
boundaries. It omits unrelated descriptor, frontend, GPU and distributed tests.
Only syntax/source checks were performed; no CuTe/native/GPU execution occurred.

Root's source-only scheduler5 capacity finding is included as a later real-CuTe
fixture: M128/N128/H8000/E32 is predicted S3 B2/raw2=232448B versus S5 minimum
232576B. S3/S5 override behavior is checked explicitly, preserving expected reject
records rather than assuming all default3 shapes survive default5. Current
H7168/E256 scheduler5 work remains valid and unblocked. A later default promotion
must preserve baseline shape admission using explicit stage5 selection or resource
fallback; the planned probe does not itself implement either policy. B3 remains
pinned to register/S3 source4208→7e16537e and requires deliberate source association
if later combined with scheduler5. No execution-ready owner, pipeline modulo3 proof,
native resources, numerical parity or performance result is claimed by this plan.


## 041 — Scheduler5 register native pair complete; detailed review pending

Root confirms the preceding no-peek→register restore is complete: stage22554,
remote20911 and fetch71016 all exit0; remote wall13.587s, receipt1f1ef8bb /
locald2c447b3, preflightb1616062 with nativebb367. Production remains retainedf5dc.

Scheduler5 N64/N128 native originals89112/6539 and fetches15961/43916 all exit0.
Original resources observe scheduler3→5 with raw5 and no spills. Detailed N64
native review passes; detailed N128 review is still pending. Root retains the
review boundary before installing candidate source8f116a49/kernelccf. Integration
records this root-relayed native status without another native/GPU review or
source mutation. No numerical or performance result is claimed. Subsequent
five-job numerical/AUTO independent saved audits remain queued alongside original
runtime checks; the directly accepted register574cf baseline is reused once.


Entry041 detailed native review and actual installation closed. Both N64/N128
reviews pass in `candidates/w4a16_scheduler_depth5_native_review/receipt.json`,
SHA `efd10c1f54935d590cefb2bbee12cb391d4d75865cf4ef6f1fbfe5bfde02dac6`.
Scope remains compile-only M256N64/N128 C2 H7168/I2048/E256, epi return/flag4;
other geometry/return and fit boundaries require the queued numerical checks.
No second native review was run by integration.

The local receipt cc0447fa47c271183bd88cd1257aac0acb14f58ccd56e213b711001662ea4d6a
and remote receipt f3e000562ae1046cadfd6b2f07d483d2f46d63f18dc8455b32f51465dc464077
record passed f5dc→8f116a499b13f4fdc36d31aea02ab5d559a0a538678253c65b69dfd39c14f362,
changing only kernel4208→ccf61580. Both saved backups rehash exactly to4208.
Original remote93393 install/preflight exits0 in13.730446125s, exit receiptf0962f7a;
actual preflight2eb7cd3c9992d3f601399a78463be913dc4cb6e01c45fffb2862707ee30a4c60
is fetched and saved. Performance is sealing/launching the five reference jobs;
18 rank-tests/72 objects remain expected until actual completion. The independent
saved audit will call original validators once after final fetch and retain actual
kernel/scheduler-param5, control allocation and raw5 observations. No additional
acknowledgment gate or recursive baseline validation is introduced.

The later B3 helper received a brief source-only API review with no concrete
blocker: explicit activation arguments and the three-value candidate fit return
match pinned source; control preserves its original signatures. Complete allocation
order, B2 fallback, FC2 depths and the distinct S3/S5 boundary are checked by the
prepared script. No helper execution, source edit or runtime gate was added.


Entry041 numerical sequence active. Corrected staging52858 exits0; original83083
now runs the five scheduler5 reference jobs with UUID
FRESH_MODERN640_VALIDATION_1add7c9d030a4c02b06fe62049b62360. Numeric map
7dd9eb3c4908ebb951130483a202fdd3edc9468d4fd6c2764eea3002633911b1 pins43 files;
actual preflight2eb7cd3c and source8f remain frozen. AUTO map
65195d3070eebdaa81476d83277624334c768576026ceaea8bd0768276b23b8c and driver
16edad8f2c6ce22e7cf33b7dc20a380921baed39ea0101597de34d5a6d558e13 are sealed.
The first staging alias failure remains transport-only; no numerical attempt
occurred there, and no test rerun is inferred from corrected staging.

Prepared one-pass saved audit is
`logs/cu132-recovery0909b-scheduler5-numerical-audit-prep-001/audit.py`, SHA
cb81dbc78d433ce53f32b030df783ad983f54972e8cc5cc77fde09a45ca2910f. It calls
original validate_job_outputs once for each completed job, preserves source,
command/helper, summary/exit and native-chain checks, and collects actual S5
kernel/params/control allocation/raw-stage records. No result or original validator
has been read/run during preparation. Expected18 rank-tests/72 objects remain
pending until final fetch; independent audit proceeds alongside AUTO with no hold.


Entry041 scheduler5 numerical sequence completed. Original83083 exits0 with exact
UUID FRESH_MODERN640_VALIDATION_1add7c9d030a4c02b06fe62049b62360_EXIT=0 and all five
ordered completion paths. Final fetch4573 closes0. Summary
70d84f34d140cadbd0ca509e14f20381ffa2b47d1e7299728ba70ad61ff6c5ac and outer
6602ea0926c2025e1c9734eed20279b8225a0564782440fed360f97b7f5f3196 are the original
completed receipts. The transport-only first-stage alias failure remains separate;
no numerical attempt occurred in that failed staging operation.

[Independent saved numerical audit](logs/cu132-recovery0909b-scheduler5-numerics-independent-001/README.md),
JSON SHA `3f1cf7c7a374e70d739b1395475dd3d50de620247cff3721121937c926d4ef05`,
executes each original fresh_session.validate_job_outputs once. All18 rank-tests,
54 setup/call/teardown reports and72 objects pass. Five result hashes are04bb4e78,
2a587943,61409bb2,79072b13,005b544b in declared geometry/EP order. Actual source8f,
map7dd9, preflight2eb7, 59 summary evidence files and108 direct hashes agree.
No live native/cache/source lookup or baseline validator recursion is performed.

All72 actual compiled kernel and scheduler-param depths are5; source default
configNone resolves to5. All raw and FC2 raw depths remain5, decoded TMEM remains
three stages forN64 and two forN128, with activationB2/accumulator2. Every resource
retains REG96 /640 threads /two decode groups /pool61440 /local0. The original pure
fit validator checks actual struct/layout bytes, alignments, deepest-fitting raw
selection and every paired config. Actual allocation cases are:

| Tile | H / I / E | Objects | Control bytes | Total bytes |
|---|---|---:|---:|---:|
| M256/N64/K256 | 256 / 256 / 4 | 18 | 480 | 127616 |
| M256/N64/K256 | 288 / 448 / 4 | 6 | 480 | 127872 |
| M256/N128/K256 | 256 / 256 / 4 | 12 | 464 | 160256 |
| M256/N128/K256 | 288 / 448 / 4 | 4 | 464 | 160512 |
| M128/N64/K256 | 256 / 256 / 4 | 24 | 480 | 160384 |
| M128/N64/K256 | 288 / 448 / 4 | 8 | 480 | 160640 |

Control480 B occurs56 times and464 B occurs16 times. Full records preserve actual
communication/packed-A/scale/B bytes and the original allocation order, including
the captured scheduler depth and K-tile counts. These are successful reference
fixtures withE4; H7168/E256 has separate native evidence, and all-domain stage5
shape admission is not inferred. Original both-return, ordinary empty/refill,
H288/I448/M257 partial-K, exact scale/routing and stable/changed graph assertions
remain unchanged. The distinct S3-accepted/S5-over-capacity large-H boundary remains
explicit and is not exercised by this reference-only subset.

All five saved native before/after inventories are byte-identical055618ec,
including22 entries and the JIT log. The immediate no-peek native checkpoint is
bound directly, while the retained timing baseline is register574cf. Performance
is staging the completed original receipt and proceeding to full13 Mega-only
AUTO100 with map65195d30 / driver16edad8f. No completed AUTO result, retention,
publication change or additional execution acknowledgment is claimed by this audit.


Entry041 scheduler5 AUTO active. Original65991 runs full13 Mega-only AUTO100 with
UUID FRESH_MODERN640_FULL13_a047280a87aa440785c5104b98b965ff. Source8f116a49,
driver16edad8f and performance map65195d30 remain frozen; the last relayed progress
is 5/13 through T16 at 370 seconds. Original numerical summary70d84f34 / outer6602ea09
and independent audit3f1cf7c7 are complete. The retained comparison remains direct
register574cf; no completed AUTO result or retention is inferred from progress.

The final saved comparison will also preserve per-tactic rounded secondary hot-L2
selection scores, grouped by geometry, flag and return mode. Those are scorer
outputs, not the primary public full-forward metric or causal throughput evidence.
Any later mixed scheduler3/5 catalog needs its own complete AUTO measurement; old
dictionaries must explicitly select scheduler3, and no row-winner splicing is used.


Entry041 scheduler5 full AUTO completed and default rejected. Original65991 UUID
FRESH_MODERN640_FULL13_a047280a87aa440785c5104b98b965ff_EXIT=0, final fetch20157 and
canonical close92888 all exit0. Manifest853175f28035fc81fdb5fc54de9f88639eacc5989c75513269bcb9c7d9b3d270,
resultsd414fa1d71745bfc8a771d81a4ba42ef9bb54c210a408dabc3ea9bfb37ff9e1d,
idle499c705a3388b8cb1a93037cf9f0eb9ebf4e3b884dfa6fffc4bfae5c1ad96b94 and
closure357d1a2e070fc4ab1eb9ca6836b4b0604b324f174b5c45abf74cac405cfc4ffe are canonical.
Source8f116a49 / driver16edad8f / map65195d30 and numerical summary70d84f34 remain frozen.

Independent comparison `logs/cu132-recovery0909b-register-vs-scheduler5-auto13-comparison-001/comparison.json`,
SHA1e91aedacafa757a5039dea799448f1d1f845c04ec90bf9832e0d86e5a2b73d1,
calls original current-source validators once and reconstructs auto.json exactly.
Direct retained register574cf rows/choices and hashes are consumed without baseline
recursion. All13 raw rows/104 compiled/104 choices/13×16 rankings/1300 samples and10
cache buckets agree;76 direct hashes, source-before/after, original exit and idle
are checked. Actual scheduler5/raw5/local0 holds on all104 records. Native055618
is byte-identical before/after, including22 entries and JIT log. The current pure
reader cb31eb53 preserves the prior load_phase/check_candidate function ASTs.

Full comparison against retained register/S3:

| Tokens | Register ms | Scheduler5 ms | Change | Speedup | Register tactic | Scheduler5 tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.082961 | 0.094913 | +14.407% | 0.8741× | M128/N64, C1, F4, epi | M256/N128, C2, F4, epi |
| 2 | 0.109761 | 0.116786 | +6.400% | 0.9398× | M128/N64, C1, F8, epi | M256/N64, C2, F4, epi |
| 4 | 0.130481 | 0.138273 | +5.972% | 0.9436× | M256/N64, C2, F4, epi | M128/N64, C2, F4, epi |
| 8 | 0.142034 | 0.158689 | +11.726% | 0.8950× | M256/N64, C2, F8, epi | M128/N64, C2, F8, epi |
| 16 | 0.168225 | 0.171698 | +2.064% | 0.9798× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 32 | 0.201377 | 0.204338 | +1.470% | 0.9855× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 64 | 0.218049 | 0.225842 | +3.574% | 0.9655× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 128 | 0.222354 | 0.234274 | +5.361% | 0.9491× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 256 | 0.227202 | 0.240354 | +5.789% | 0.9453× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.239698 | 0.245858 | +2.570% | 0.9749× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 1024 | 0.271025 | 0.257778 | -4.888% | 1.0514× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 2048 | 0.347571 | 0.347539 | -0.009% | 1.0001× | M256/N128, C2, F8, reuse | M256/N128, C2, F8, reuse |
| 4096 | 0.502692 | 0.513477 | +2.145% | 0.9790× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

GM S5/S3=1.0424572798464427 (+4.246%); onlyT1024/T2048 lower, all other11 rows slower.
Six tactics change atT1/T2/T4/T8/T32/T1024. All rows, exact ratios and both complete
knob dictionaries independently agree with performance's original e1f0b5fe report.
Process wall892.496413493s versus timer utility6.101599653s; the remainder is not
assigned solely to compilation/tuning. Sequential unbracketed AUTO retuning does
not isolate a fixed-tactic causal effect. Root rejects default5; retained register
PR0109/body4606 and its one final table remain unchanged. No S5 PR draft is made.

Secondary hot-L2 selection scores are separate:
`secondary-hot-scores.json` SHA40053f4f1f5d55768edb227db38e587c30189c2932a4866947ac2a0b09168ab3
and `secondary-hot-scores.md` retain all208 exact original one-decimal printed
score pairs, matched by complete dictionary at all13 points. Only M256/N64/C2,
flag4,reuse has a lower aggregate0.998544 (-0.146%,7/13 lower); other15 grouped
ratios are higher. These are rounded staged-W4A16-wrapper-plus-reducer graph-event
selection scores, excluding public routing/staging preparation, not primary CUPTI
latency or causal throughput. No selected-winner splice is performed. OptionalS5
remains lower priority; any mixed catalog needs its own fullAUTO and explicit
stage3 in every retained old dictionary to avoid default admission loss.

Actual local/remote8f→f5dc restoration completed at11:00 UTC. Local receipt
 ec10ebdd296203cf4cdc147b5208733bbd469a71d2d1ab223e09bc20133b1b26 and remote
b9abdf67b17368938698603da2370d83b41e6cb981a945332e4179a0bd0d7c39 restore onlykernel4208;
both saved backups rehash toccf61580. Original exit8ed2263d return0 in14.298113625s,
actual preflight92ce81c7/nativebb367 passed. No live source lookup was used by this
independent saved audit. Performance proceeds B3 on retained register/S3.

B3 real-CuTe host-layout run original13649 exits0 in14.114704375s; result
90c3973dd69e544584e36349cc82b66247ef9878aace434acf750f2133c5c49f and exit
 d2354a96f66026a5a39bce73d93a652122e8c33b309383e141922572bfeb6360 are saved.
Root independently checks all54 actual layouts:22B3,21B2 fallback,11both-rejected;
first-fitting selection and admission match, and each B2 fallback equals control.
Actual H8000/E32 S3 fits232448 B while S5 needs232576 B and rejects. The immutable
result method string contains stale preparation wording 'No execution has been
performed'; preserve its bytes and use the original exit/log as execution evidence.
Host layouts do not establish native quality or GPU phase/numerical correctness.

Held B3 numerical addition handoffb81e69d9 and selected-source observer/capture
payload handoff244b0b1521e1c6759fb66f6f0a4862618dde052af10dc251585430c25356fdcc
are saved under candidates/w4a16_activation_b3_validation_preparation and
candidates/w4a16_activation_b3_validation_payload. Source03c41/kernel7e165 is selected
register/S3. Five jobs retain18/72 reference coverage and add10 long rank-tests/
10 objects, totaling28/82. H7200/I2112/M257 both returns on N64 EP1/EP2 and N128 EP2
exercise within-work29/9 K tiles with tails32/64; actual B3/raw5 N64=199424 B and
B3/raw4 N128=230144 B must be observed. Original small empty/refill and exact graph
assertions remain separate; no long-K graph/empty-refill claim. All original public
AST/oracle nodes are unchanged in the copied fixture; no new oracle/controller.

The six payload files preserve resource/shared checks and observe actual FC1/FC2 B
inside the original CuTe context, call original fitter/mixed construction once,
return identical original objects and store plain metadata only. Exact B3 thenB2,
raw5..2 selection and complete allocator order are checked. Numerical and benchmark
observer bodies have identical ASTs. Pure CPU negative cases, exact selectors/counts,
Ruff and patch application pass; actual GPU assertions remain pending the normal
runtime. Runtime/source/native ownership remains performance's; this saved review
creates no transition or publication acknowledgment gate.


Entry041 B3 transition preparation handed off. Root relays both candidate-only native
captures and detailed quality PASS: original checkd044c423, N64 summary5b686a94 and
N128 summary65aedf03. Performance is authorized to proceed install/preflight and
numerics without another acknowledgment. The runtime child independently reads
payload244b: no blocker; exact six copies/APIs, five-job28/82, original resource
Counter and AUTO timing loop are preserved. No second native review by integration.

Held numerical saved reader is
`logs/cu132-recovery0909b-activation-b3-numerical-audit-prep-001/audit.py`, SHA
5eab76e27ed75cd830815cfbe81e09492d55771a52cc1bec5505c40fd22c0e1f. It is the previous
five-job saved checker with B3 source/prefix, exact28/82 and actual FC1/FC2 B metadata
plus ten K29/K9 objects. Actual runtime map/preflight/UUID remain unbound until
execution pins arrive. No numerical outputs or original validators are read/run by
this preparation. The public B3 wrap wrapper6c71 remains held for retention only.


## Entry 042 — B3 activation ring on retained register/S3, numerical sequence active

Actual source03c41ac1bb3eb3d6feb3175983d6806e88ad1d006a6cc1f785c0e768f64c6cc1
is installed with passing preflightfa58f5fe8bd3aea88340a25335c7117bdafd436a1405b8ebe5cef9b6f12c122a.
Stage65796 closes0. Original51052 now runs the exact five jobs with UUID
FRESH_MODERN640_VALIDATION_eb7e23f65ee946c69574a50a781b31e6. Numeric runtime map
f1da793014242bee7f8a6b74e645d276b10252ffe40e2f42fa5e6f1c5a73a64c pins47 files;
AUTO map066d57aa is prepared separately. Expected28 rank-tests/82 objects remain
pending actual completion; no job or AUTO timing is claimed from launch alone.

The original saved numerical reader's three held fields are now bound to the
actual map/preflight/UUID. Final prepared SHA4394fca3d05248df9a6b1377da756d7b9e6f47de75678fc86b5f129a064ec879; prior unbound5eab76e2 is
historical preparation only. No completed output or original validator has been
read/run yet. One final saved audit follows original successful sequence/fetch
closure alongside AUTO, without a GPU acknowledgment hold or baseline recursion.
Root's later scheduler2 integer-change alternatives remain separate source-only
preparation; they do not change the B3-first queue or its retained register baseline.


Entry042 B3 numerical sequence complete. Original51052 exits0 with exact UUID
FRESH_MODERN640_VALIDATION_eb7e23f65ee946c69574a50a781b31e6_EXIT=0; finalfetch37364
and original receipt stage39726 close0. Summarybdfeba0151e8eda17c0439647a5d1023910b287de53ca4ad264a037747e4f2b7
and outer1fa04fc9c421313c449af1ad007fcdecf92ef331c780f2e2773f320cfad4ff80 are canonical.
Performance reports managed numerical wall392.735s. Actual source03c41, mapf1da7930,
preflightfa58f5fe and exact payload244b remain frozen.

[Independent saved numerical audit](logs/cu132-recovery0909b-activation-b3-numerics-independent-001/README.md),
JSON925c0573976914f757b2c9a96a82d0cc3c976f12953fb6a9eb1ea18574bc596a,
calls each of the five original validators once. All28 rank-tests,84 phase reports
and82 objects pass, with59 summary evidence files and112 direct hashes. Job result
hashes in order are9a386c1c/9bb0d0da/585b34e6/7a0bd3c9/b3722b1b. All82 actual FC1
and FC2 activation rings areB3; kernel/scheduler-param depths are3. Actual raw5×78 /
raw4×4, control400×62 /384×16 /368×4, REG96/640/two decode groups/pool61440/local0.

All ten normalized H7200/I2112/M257 long objects pass original numerical oracles
on both return modes: six N64 EP1/EP2 objects useB3/raw5/199424 B and four N128 EP2
objects useB3/raw4/230144 B. Both phases have actual K29/K9, including partial tails.
Original18 reference rank-tests retain six-round empty/refill, partial H288/I448,
exact scale/routing and three stable plus one changed graph equality per rank-test.
These small reference graph checks are separate from the added eager long-K cases;
no long-K graph/empty-refill or extra all16/B2-fallback numerical claim is made.
Every saved native before/after inventory is exactly055618ec, including22 entries
and JIT log. Immediate completed S5/native/restore association is pinned directly;
no live cache/source/owner lookup or older baseline-validator recursion is used.

Actual AUTO97667 is launched with UUID
FRESH_MODERN640_FULL13_05a268179be148738e556ff021af0861. Driver91ded99187c7058254fa81f0a60f22f23cc4fb5b98870ccce82671c20f796d14,
performance map066d57aab1c807b4623865a933fd0abd13bdee4692c67da8ae52b03950c0a1d0
and source03c41 use retained register574cf/e305 as the direct timing baseline.
The bound saved comparator SHA8798d10cb1342050cc437204decfc7c8736c303ba5cd4712f461aa167c0ae9d5 is ready; no active performance output
has been read. Its original check_candidate/load_phase ASTs are preserved, adding
only B3 row/allocation fields and current exact pins. Run once after actual full
fetch/source/native/idle closure; no extra acknowledgment gate or split rerun.

Frozen performance comparison_scope retains stale 'Raw7 full13 AUTO' prose;
actual B3 source, purpose, selectors, observations and baseline are correct. Root
chooses explicit disclosure and preservation of the staged bundle, not a rebuild.
This descriptive mismatch does not claim a different source or measured trial.
No B3 performance win, retention or PR change is inferred from passed numerics.


Entry042 held later scheduler2 numerical preparation. Folder
`candidates/w4a16_scheduler_depth2_validation_preparation`, handoff
3f0e6d23caf67df45231bd57563782d66c8f1ed07aa5d6fc1b0002aafa169441,
contains separate unselected register/B2 and activation-B3 observer/selector deltas.
Candidate kernel bases are4208→52e23c78 and7e165→7df57bfd respectively; whole source
and owner remain unselected. Only actual default scheduler2 and its control-byte
term change. Pair/B2 and triple/B3 fitter behavior, raw5 ceiling, allocator order,
FC1/FC2 B observations, resource checks and exact numerical oracles are preserved.

The same five original two-return checkout reference jobs total18 rank-tests and
72 objects. They retain ordinary empty/refill, H288/I448/M257 partial K, exact
scale/routing and stable/changed graph checks. No long-K addition or all16/split
rerun is proposed for this metadata-only delta. Exact adapter APIs, checkout
rootdir/selectors and caller-owned source/stack/map changes are documented.

Both geometry wrappers are byte-identical to their established versions. Reversing
the few scheduler/formula literals restores each allocation helper's original AST.
Pure metadata tests reject stale kernel3, params3, old S3 control bytes and raw6;
exact selector counts, patch roundtrips, Ruff and formatting pass. Atomic scheduler
storage176→128 bytes removes48 control bytes at fixed pipeline depths; alignment
means total allocation need not decrease by48. Source-only predicted control sizes
are336/320 B for B2 N64/N128 and352/336 B for B3 N64/N128. These are not actual S2
layout or runtime results. Performance received the sealed payload; B3 fullAUTO
and its direct accepted-register comparison remain first, with no new launch gate.


Entry042 B3 AUTO complete, fallback passed, retained and committed. Original97667
and fullfetch92759 exit0. Corrected post-run close17488 exits0 with canonical
closure8d3bcb53ef00e6a3e488a142c546c6cdbb41350bc6a0cf1059ba6c42ec70f081 and
idle002 a3b5d04f. The first copied close71260 fails on stale S5 driver/preflight
pins before idle write; preserve it separately. Only those literal pins change,
with no source/kernel/numerical/timing rerun. The frozen Raw7 comparison_scope
wording defect remains explicitly disclosed.

Independent comparison b0cd2993603d9e2eb56b14d339cb562e40de01a2201d09ca5ec6e3709a1d5f4a
at logs/cu132-recovery0909b-register-vs-activation-b3-auto13-comparison-001
uses accepted register574cf directly and runs current original saved validators
once. Complete auto.json reconstruction agrees:13 rows,104 compiled objects and
choices,13×16 rankings,1300 samples,10 cache buckets and80 direct hashes.
Actual FC1/FC2 B3×104, raw5×80/raw4×24; resources remain REG96/640/two decode
warpgroups/pool61440/local0. The80/24 AUTO allocation count differs legitimately
from78/4 in the82 numerical objects. Process wall884.9766216509961s and timer
utility5.921042910988035s are separate from primary median GPU latency.

GM B3/register0.9750494362380544 is2.495% lower latency (1.02559× speedup),10/13
wins, six selected tactics changed. All sizes>=16 improve; regressions T1/T2/T8
are retained below. No minima, drift correction or fixed-tactic causal claim.

| Global tokens | Register ms | B3 ms | Change | Previous tactic | Current tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.082961 | 0.084849 | +2.276% | M128/N64, C1, F4, epi | M128/N64, C1, F8, epi |
| 2 | 0.109761 | 0.113488 | +3.396% | M128/N64, C1, F8, epi | M256/N64, C2, F8, epi |
| 4 | 0.130481 | 0.120641 | -7.541% | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 8 | 0.142034 | 0.153585 | +8.133% | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 16 | 0.168225 | 0.166960 | -0.752% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 32 | 0.201377 | 0.193825 | -3.750% | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 64 | 0.218049 | 0.214466 | -1.643% | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 128 | 0.222354 | 0.211697 | -4.793% | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 256 | 0.227202 | 0.222562 | -2.042% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.239698 | 0.221681 | -7.517% | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 1024 | 0.271025 | 0.245986 | -9.239% | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 2048 | 0.347571 | 0.330724 | -4.847% | M256/N128, C2, F8, reuse | M256/N128, C2, F4, reuse |
| 4096 | 0.502692 | 0.489156 | -2.693% | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

Separate fallback original67021/fetch2202 complete0. Canonical closure
604d07417f8672a5b960b18a0254434c5952ea99c16aafa9023ce6e470089aa8 binds result065d96c5,
outerc680c6cb, idlecc94651c and24 direct evidence files. Integration calls its
original saved validator once and checks all24 hashes: one EP1 eager normalized
H18272/I64/T257/E4 M256/N64/C2 flag4 epi-return case, actual FC1/FC2B2/raw2,
decoded3/ACC2/K72-K1 and216192 allocator bytes, all three test phases pass.
No fallback EP2 or graph claim. Child27.591961225s / managed30.763858875s.
Source03c remains exact before/after; native fe40ce79 serializes the same complete
22 entry objects as055618 (TORCH_EXTENSIONS_DIR0 + FLASHINFER_WORKSPACE_BASE22).
Recent messages saying76 native objects were a count error; hashes/object equality
are unchanged. Earlier ledger22-entry statements are correct.

Root retains B3 and commits/pushes02cfbb1b555947e2babe15bdd66b9251f72907a5 with all
commit hooks passing including mypy/Ruff/format. Measured source03c41ac1 maps to
published489e210540a631f277ae648386bffd6f3e9c1345cabba7fdab7d11d99c3a44c1 through only
publictesta7c513f9. Kernel7e165 remains byte-identical. Public pipeline-wrap and
fallback wrappers have exact effective helper parameters/configs matching the
executed external fixtures; the new public wrapper functions were not rerun GPU.
Actual source sync stage36436/original31588/fetch75549 closes; receiptfe452909 and
closure1686396e record exact03c→489e test-only change and no native-object delta.

Proposed PR_BODY-b3-full13-proposed.md SHA7a6da05bf9074d53985bb8daac0116fbbea92ae1c9ff3e8f346f4f7bbb3e29cc
contains one current132 table, all13 faster than explicitly reused alpha split,
exact unchanged130 table/checklist/@humansand and source-specific profiler scope.
Proof logs/pr5019-b3-body-preparation-001/proof.json verifies raw table derivation,
unchanged historical table/template and separate fallback saved validation.
Canonical PR drafts and live body remain untouched by integration. Root owns
publication/readback; no PR comments. Next source trial is S2 on retained B3,
using held3f0e6d23 references18/72; B4 remains later untested preparation, outside PR.


Entry042 B3 PR publication complete. Root writes and verifies PR5019 at drafttrue
head02cfbb1b555947e2babe15bdd66b9251f72907a5, body
7a6da05bf9074d53985bb8daac0116fbbea92ae1c9ff3e8f346f4f7bbb3e29cc.
Receipt logs/pr5019-b3-publication.json SHAb0ea5508580e17dd0500ae81e0dc602d3ebe51bc76b384654fdf8014ba0f7c28
and logs/pr5019-b3-body-readback.json preserve actual readback. Canonical PR_BODY.md,
PR_BODY-current-modern-full13.md and PR_BODY-b3-full13.md match exactly; register
draft remains historical. No additional timing or GPU tests were inferred from
publication. Next S2 trial uses retained B3 and direct acceptedb0cd baseline, no
recursive earlier-controller checks or fresh split/fixed rerun.


Entry042 current02cf upstream CI refresh is saved by root in
logs/pr5019-b3-check-runs.json and logs/pr5019-b3-gpu-ci-summary.log. Pre-commit/docs
pass; GPU jobs skip and summary run34348072540 explicitly reports CI skipped
pending authorization. No labels/comments/approval action, and no body change.

Held next B4 numerical plan is candidates/w4a16_activation_b4_validation_preparation,
handoff8ab16a2d711d7962d3ab9331a03d6cbb31b1720300c0b22473820191badd1be5.
Two unselected S3/S2 patches change only the B3 generic allocation helper's
allowed activation/preference order and exact long-case B4/raw/allocation scalars,
plus selected scheduler literals for S2. Existing wrappers/resource/oracle/role
checks are unchanged. Same five jobs28/82 retain ten eager K29/K9 long cases;
small original graph/empty-refill evidence remains separate. Pure existing-model
projections give B4×82, raw5×78/raw2×4. N64 long is215808 B in both; N128 long
is226048 B(S3) or225920 B(S2). Optional published-selector mapping keeps only the
two matching long parameters per eligible job; no implicit fallback or full-matrix
addition. Independent source review agrees. No tests, real CuTe/native/GPU work,
production change or repeated completed-B3 validator. S2 remains first and current
retained timing baseline is acceptedB3b0cd.


## Entry 043 — Scheduler2 completed, default rejected; B3 retained

Root accepts both detailed native reviews and releases installation. Performance
reports actual source9605cb9a7f9b26406b485159718c7c68106530cf5344d53102caa7737271f32f,
kernel7df57bfd after published B3 source489e/testa7; install22001/fetch50385 close0.
Preflight01eb7d41b8378bda4eea1443627c8f7c1a6145da4850f7589d854f54eb1981ab / approvedc4f50ba7.
Original70829 runs five reference jobs18/72 with UUID
FRESH_MODERN640_VALIDATION_387b3d7a748243d4a4352756efa22ad4; numerical mapa38f4e6a
contains79 consumed files. This is launch status, not completed numerical evidence.

Prepared AUTO name cu132-recovery0909b-scheduler2-auto13-001 uses original driver
0dad3934c13d3fc7cd681e8d00348d89a2ff1abbde9f9f034a2cb55155bd571e and86-file map
fbef63bda85a0672197e94398872f33bf2d13670b131055c232e5e1e3a2a3ac4. Direct retained
baseline is acceptedB3 comparisonb0cd, not register574cf or alpha. Full13/100
Mega-only AUTO remains unchanged, with no split/fixed/baseline rerun.

Held saved reader logs/cu132-recovery0909b-scheduler2-auto-analysis-prep-001/
check_and_compare.py SHA829c5321ae428023ce0fa7c3b01aa7566314b60936667bb68e4a97dee9423ab6,
preparation7e1abbc9, preserves original check_candidate/load_phase AST exactly. It
uses only baseline current rows/choices with direct hashes, validates current
original13/104/13×16/1300 outputs once after closure, and derives actual B/raw/S2
histograms without pinning B3 winners. Exact source delta is kernel7e→7df plus
publictest868d→a7c; completed test-only publicationfe452909 independently binds
measured03c to published489e. Current completed numerical audit/summary and AUTO
UUID remain None. Main rejects before candidate reads until actual fields bind.
No completed outputs or original validators executed, no historical-controller
recursion or new owner/launch framework.

S2 detailed native receipt is candidates/w4a16_scheduler_depth2_native_review/receipt.json,
SHA8d3ef8f2095b0cd9513ecf1542296cef1f3962baf380de4ed9dd65dd66ae74b8.
Root reports the first two N64 EP1/EP2 numerical jobs passed, N128 EP2 active;
full five-job summary remains pending. AUTO staging95668 passes with the same
fbef/0dad pins; no AUTO execution is implied by staging.

Entry043 actual numerical completion supersedes the preceding launch-only status.
Original70829 / finalfetch76339 close0 with exact UUID387b3d7a; summary
c38ed85af2e3c0524661adb0addf540597698e34e86754bf770ef7d18575ddce and outer
02502f5146295def960182353be92c4764a09f0c6f07ef6bebe83f9a52d77ff4 are complete.
[Independent saved audit](logs/cu132-recovery0909b-scheduler2-numerics-independent-001/audit.json),
SHA767195c2f20a090a36607a7eeefcb3b93394431ee1530db929f0482d8cc2c060,
calls five original job-output validators once:18 rank-tests /54 phase reports /
72 compiled objects, allS2/params2/configNone→2, B3/raw5. Actual control bytes352×56
N64 and336×16 N128 match allocation; unchanged REG96/640/two-decode/pool61440/local0.
All59 summary evidence files and144 direct hashes pass. Original two-return
references retain six-round empty/refill, partial H288/I448, scale/routing and
3 stable+1 changed graph replay; no long-K/new fallback claim. Native055618 is
unchanged, with published fe40 serialization linked by exact object equality.

AUTO original93292 is active after source/native/idle PASS and catalog16 start,
UUID FRESH_MODERN640_FULL13_72d99ee9eaeb48778f6db4df97e6b13a, samefbef/0dad;
outer receipt stage62685 passes. Final saved reader is bound to actual summary /
independent audit /UUID, SHA87e5dfbe58b10c48fde15a22f224f3990714da5ad7660fc716940615248d3509.
It consumes direct accepted B3b0cd current rows only. No active AUTO outputs read,
no repeated baseline/split/fixed run, and no independent audit launch hold.
Retention remains B3 at02cf/body7a6d until the completed full table.

Entry043 bounded iteration-speed source audit completed while AUTO runs:
[cache-policy report](logs/cu132-recovery0909b-compile-cache-policy-audit-001/README.md).
Current installed DSL4.7.1 captures1f32a0bb and50fd4065, associated with actual
preflight01eb/nativebb367, were independently rehashed:52 files /1,870,102 bytes.
The harness explicitly chooses fresh DSL/driver roots, separate from loaded
source/resource/numerical checks. Actual cute.compile is CompileCallable and
unconditionally forces compile_only=True/no_cache=True; Mega and its reducer
both use it. Thus merely sharing the DSL directory does not skip those compile
calls. Generic cache-enabled paths do support compiled-IR hits, with original
IR/environment/options/package/DSO keys, but still trace and construct JIT state;
that path must not be conflated with current explicit compilation. Knob cache
must stay fresh for new scorer rankings. No driver-key guarantee, observed cache
hit, saved-time estimate or need for fresh baseline is established. Historical
prepared same-source failed-retry cache reuse is a policy precedent only, not a
completed current reuse measurement. No remote/import/native/GPU/runtime edits.

Entry043 full AUTO completed and defaultS2 rejected. Original93292 / fullfetch13979 /
canonical close84362 all true0; closure250355a9e0a44061dd74860b9671a5a329daf8ae682e5ab2428b5f2d925ce71b,
idle001e2726db63e02f106f577cc617de218f487bdd76521822e25865af5af43bae9b3.
Manifest1443debf/result8858ea53/outer14965856/execution6bd2fa1f bind actualsource9605,
driver0dad/mapfbef. Independent [full saved comparison](logs/cu132-recovery0909b-b3-vs-scheduler2-auto13-comparison-001/comparison.json)
SHA161348af1bf1ba8d9a1217d3855b5be45668f6041614f6ff9ddd50603e91afee
runs original current-source validators once, directly consumes accepted B3b0cd
current rows and reconstructs saved auto.json exactly. All13 rows /104 choices /
104 resources /13×16 rankings /1300 samples pass; actualS2/B3×104, raw5×80/raw4×24,
REG96/640/local0. Native inventory055618 remains identical. Whole process
895.474033634s versus B3 884.976621651s, timer utility6.060429055s versus5.921042911s;
remainder is not assigned wholly to compilation/tuning.

| Tokens | Retained B3 S3 ms | Candidate B3 S2 ms | Change | Speedup | Retained tactic | Candidate tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.084849 | 0.084721 | -0.151% | 1.0015× | M128/N64, C1, F8, epi | M128/N64, C2, F8, epi |
| 2 | 0.113488 | 0.130065 | +14.607% | 0.8725× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 4 | 0.120641 | 0.121665 | +0.849% | 0.9916× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 8 | 0.153585 | 0.147761 | -3.792% | 1.0394× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 16 | 0.166960 | 0.164273 | -1.609% | 1.0164× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 32 | 0.193825 | 0.182226 | -5.984% | 1.0637× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 64 | 0.214466 | 0.207346 | -3.320% | 1.0343× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 128 | 0.211697 | 0.211026 | -0.317% | 1.0032× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 256 | 0.222562 | 0.222770 | +0.093% | 0.9991× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.221681 | 0.227986 | +2.844% | 0.9723× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 1024 | 0.245986 | 0.243810 | -0.885% | 1.0089× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 2048 | 0.330724 | 0.331843 | +0.338% | 0.9966× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |
| 4096 | 0.489156 | 0.473909 | -3.117% | 1.0322× | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse |

Equal-token geometric mean S2/B3=0.9985823327826323 (0.14177% lower latency,
1.00141968× speedup);8/13 lower, five tactics change atT1/T2/T8/T16/T1024.
Root rejects defaultS2: near-neutral aggregate does not justify T2+14.607% and
T512+2.844%; other regressions atT4/T256/T2048 remain visible. Published02cf/B3
source489e/body7a6d is unchanged. Performance owns restore9605→489e thenB4/S3;
that transition's completion will be recorded from actual receipts. No split,
fixed, baseline or profiling repeat, no row minima/drift adjustment.

Keep S2 as a possible later curated tactic after B4: M256/N64/C2/F8/epi has
better same-config T32/T64 rows, and M256/N128/C2/F4/reuse improvesT4096. This is
candidate motivation, not a causal fixed-tactic result. Two optional dictionary
entries could use existing num_sched_stages=2; all original16 would need explicit3
to avoid sticky configuration. No new public knob/catalog change now; any mixed
catalog must be measured by its own full13 Mega-only AUTO100 against the then
retained baseline. Source/default2/native/numerical evidence remains preserved.

Entry043 restore actually completed, as relayed by root: stage54774 /
install-preflight2758 /fetch31498 true0. Receipt08f64472feaf4806f4c2e9cfcbd4308f1338cb7757bae4a78a36b8ffc5491c91,
preflightbbf8ca7f /outere0fc190c, exactsource489e/kernel7e and cleanHEAD02cf.
Performance proceeds B4 on S3; no saved-audit hold.

Held later curated18 scheduler tactic preparation is now at
[candidates/w4a16_scheduler_curated18](candidates/w4a16_scheduler_curated18/README.md),
handoff6631128a11df115eb1e8a013ec03582fd92d4233c563e8aaf5c1ef1f101473ab;
baseautotune6d7→candidate8454669facd021ba5d476fe6614d8fa78a9dfe546cf76b4416c99fd569c24c8d,
patcha38e5367823583ad2cd19675a9aa592dce41ecc81689bc78ed4dbcd6f98f4d66.
The only changed function is w4a16_candidates. Every old16 dictionary keeps order
and all previous fields, addingexplicitstage3; appended N128C2/F4/reuse and
N64C2/F8/epi useexistingstage2. Otherprecisions/scorer/cacheAPI/sharedbase remain
unchanged. This is separate from heldgroup_hint256curated18, not a combinedgrid.

Portable CPU proof executes actual factory/config/apply_knobs/with_knobs bodies:
32 two-extra→old-winner stage resets,32 negative controls proving omission sticks
at2, compile-key/workspace invalidation and capture-before-release preservation.
No Torch/CuTe imports, native/GPU work, numerical or timing claim. Only capture
and workspace operations are mocked. Whole-module AST reverses exactly after
restoring the factory; Ruff/format/gitapplycheckpass. A future selected runtime
must expect13×18rankings and reconcile each actualstage2/3 selected object with
its dictionary, preserving104finalobjects/choices and1300samples. No runtime/
production change now; B4 remains next, kernel base unselected until its verdict.

## Entry 044 — B4/S3 complete, default rejected; B3 retained

Root accepted both detailed B4 native gates and released actual installation.
Sourcecaddbf55883e42bf1a0cd324dd5077064ef642145975e9187c23ffbbf843f25d,
kernel466d64d6baf888fdf520adb12e507bca5abc9dfe284a3833c27cd5017b6a0986,
manifest9a6c1588, changes only activation preference/comment from published489e.
Scheduler3 stays selected. Install81634/fetch15126/preinstall49232/runtime63924
all true0; actual preflight7b8e25524df864d1ac8153a89787f462a3e41bf2acef59b8da3d24ea321d24fd.

Original numerical40670 is active after source/native/idle PASS, UUID
FRESH_MODERN640_VALIDATION_fc634ffbe9b4487d878f44c3c1dd30bc. Numeric mapec0efc85
contains46 files. Expected five jobs28/82 include ten K29/K9 eager wrap/partial
cases plus original reference/graph contracts. Actual completion remains pending;
the expected B4/S3 and raw5×78/raw2×4 allocation counts are not yet results.

Bound local saved numerical readercfeb6e56 at
logs/cu132-recovery0909b-activation-b4-numerical-audit-prep-001; prospective AUTO
reader136e4b57 at logs/cu132-recovery0909b-activation-b4-auto-analysis-prep-001.
AUTO map8fbdae75 (53 files) /driver504108f3 are prepared; actual numerical summary/
audit and AUTO UUID/closure remain pending. Direct timing baseline is accepted
B3b0cd. The immediate native owner is completed S2 followed by actual restore08f;
no historical controller is re-run. Original AUTO check/load ASTs are unchanged,
full13/100 and dynamic actual allocation histograms preserved. No active outputs
read, GPU acknowledgment gate, curated18 application or PR change.

Entry044 actual numerical completion supersedes launch-only status above. Original40670
/UUIDfc634 and final successful fetch44344 true0; earlier fetch91005 is preserved
as a wrong driver filename, corrected without a GPU test rerun. Summary
 eae045ba5772d3d891d5492486f0ca2421b9165cf89e9067f0406ed4544f90de and outer
6e41c2bdde702565db373ce1d9614d3d56dea5c34631d8e356d7d786dc45385f complete.
[Single independent saved audit](logs/cu132-recovery0909b-activation-b4-numerics-independent-001/audit.json),
SHAd5ac24d436e5c144633a5ae228d816361dca0e22c75aba26e1fec178330f631f,
calls five original validators once:28 rank-tests /84 phase reports /82 objects,
FC1+FC2B4/S3 throughout, raw5×78/raw2×4, unchanged REG96/640/two-decode/pool61440/local0.
TenK29/K9 eager cases are6N64/raw5/215808B and4N128/raw2/226048B. Actual control
bytes416×62/400×16/352×4. All59 summary files /111 direct hashes pass; every native
before/after055618 exact. Original small reference assertions retain both returns,
empty/refill/partial/scaling/routing and exact graphs; no long-K graph reuse or
new lower-B fallback scope is inferred. Direct immediate S2 native and restore08f
association only, without rerunning any baseline controller/validator.

AUTO25551 is active after source/native/idle PASS and catalog16 start, UUID
FRESH_MODERN640_FULL13_756c99105018421180895cb42bf8dff5. Samecaddbf/8fbmap/5041driver,
full13 Mega-only100. Bound comparatora5f0a2a1772e1708d3ef15e4182c61304e2661e2caeadd95072fa7b0ceeb344f
uses retainedB3b0cd current fields directly and original new-candidate validators.
Actual numerical summary/audit/UUID now bind; canonical final AUTO remains pending.
No active timing output read, no independent launch gate, no PR/shared-state change.
Any conditional B4 fallback follows a positive completed full-table decision;
curated18 scheduler tactics remains held for the then-retained source.

Entry044 full AUTO is now complete and B4 default rejected. Original25551 /
fullfetch67691 /canonicalclose20194 all true0, exactUUID756c. Closure
 a45c6786e5ec34fcc9af9f04859548c4b60ea8c9b3a81620c0c6452c87fed7e5 and idle001
 d5f52982ae4fe551b04bae4b6b60b0c266b95ae9cc44659e610988941f2910a5 bind
manifesta0853ae3/results361253ce/outera0dc370e, sourcecaddbf /8fbmap/5041driver.
[Independent original saved comparison](logs/cu132-recovery0909b-b3-vs-activation-b4-auto13-comparison-001/comparison.json)
SHAaca87e8b7286e78581c7a8a8b8425709c57d74843a4e71e13a019d13300f08bb
reconstructs original auto.json exactly once, directly consuming retainedB3b0cd
current rows/choices and hashes. All13 raw rows /104 objects+choices /13×16rankings /
1300 samples and80 direct evidence hashes pass. Actual winners allM256/N64,
B4/S3/raw5×104, REG96/640/local0; no N128/raw2 AUTO winner is inferred from the
numerical fixture. Native055618 unchanged. Process896.076744923s versusB3
884.976621651s; timer utility6.217165971s versus5.921042911s. Remainder is not
attributed wholesale to compilation or scoring.

| Tokens | Retained B3 S3 ms | Candidate B4 S3 ms | Change | Speedup | Retained tactic | Candidate tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.084849 | 0.090177 | +6.279% | 0.9409× | M128/N64, C1, F8, epi | M256/N64, C2, F4, epi |
| 2 | 0.113488 | 0.098722 | -13.011% | 1.1496× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 4 | 0.120641 | 0.130865 | +8.475% | 0.9219× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 8 | 0.153585 | 0.152562 | -0.666% | 1.0067× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 16 | 0.166960 | 0.167617 | +0.394% | 0.9961× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 32 | 0.193825 | 0.188273 | -2.864% | 1.0295× | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi |
| 64 | 0.214466 | 0.199858 | -6.811% | 1.0731× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 128 | 0.211697 | 0.214466 | +1.308% | 0.9871× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 256 | 0.222562 | 0.221266 | -0.582% | 1.0059× | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi |
| 512 | 0.221681 | 0.228241 | +2.959% | 0.9713× | M256/N64, C2, F8, epi | M256/N64, C2, F4, epi |
| 1024 | 0.245986 | 0.242051 | -1.600% | 1.0163× | M256/N64, C2, F4, epi | M256/N64, C2, F8, epi |
| 2048 | 0.330724 | 0.345363 | +4.426% | 0.9576× | M256/N128, C2, F4, reuse | M256/N64, C2, F4, epi |
| 4096 | 0.489156 | 0.535237 | +9.421% | 0.9139× | M256/N128, C2, F4, reuse | M256/N64, C2, F4, epi |

GM B4/B3=1.0041646566074116 (+0.41647% latency),6/13 lower,7 regressions,
8tacticchanges atT1/T2/T16/T64/T512/T1024/T2048/T4096. Root rejects B4 default,
includingT4096+9.421% andT2048+4.426% regressions. Skip conditional fallback
executions and public B4 wrapper/source patch; retain all native, numerical and
fullAUTO evidence locally. Published02cf/source489e/B3/body7a6d remains unchanged.
Performance owns restorecaddbf→489e/kernel7e/testa7, staging10057 in progress;
completion receipt is pending. Next is held curated18 scheduler tactics on B3
with directB3b0cd baseline, original full13 Mega-only100 and unchanged scorer.
No split/fixed/baseline/profiler repeat, row minima or drift correction.


Entry044 restore supersedes the pending statement above: original19571 and
fetch40530 true0; actual receiptc390f80622ca8eab53f1882d8c11ba6b8c816620da10f9940a72df0ef58d83eb
restores caddbf→489e/kernel7e/testa7. Preflightd737d312 and outerd87e61e2 pass.

## Entry 045 — Curated18 scheduler tactics: installed, numerical payload prepared

Retained B3 is selected after B4 rejection. Catalog-only source
ef5a912ead29a3389932de54d2e7f3fd087b72de4449ed4e01471b7edff2d159 is installed
from489e: manifest1fe4d427, receipt5be07228, outer72bea433 true0; actualpreflight
763766d07a33ca8726977eff10bec16d45bdc086b1d0ca3c04217f10213da07d reports18 tactics.
Kernel7e/publictesta7 and loaded CUDA13.2/DSL4.7.1/nativebb367 are unchanged.
Old16 explicitS3 plus two explicitS2 extras use sealed factory8454669f. No scorer,
public knob, geometry grid or cache API change. B3b0cd stays direct timingbaseline;
PR02cf/body7a6d unchanged pending full13 Mega-only AUTO100 retention decision.

Numerical preparation at candidates/w4a16_scheduler_curated18_validation_preparation
is sealed with handoff65151d7237c3343e790f301ae3a727a810a8c508fa8d9decd82d0ee134c88b16.
Exact copies: reference_subset d14aa103; geometry observerc6976f2c; separate fixed
reference_stage_observation1585c6a4. Existing API maps N128/C2/F4/reuse EP2/S2 then
N64/C2/F8/epi EP2/S2 to one original reference node each:4 rank-tests/16 objects.
Public a7 oracles/tolerances and original empty/refill/partial-tail/scale/routing/
3+1 exact graph assertions remain; both returns are covered across geometries,
not both on each geometry. Original knobs are retained separately from selected
flag4/8/explicitS2 config. No extra long-K/EP1/fallback/all18 lifecycle run.

Portable CPU proof executes actual selector/merge and pure allocation ASTs, checks
original observation/layer AST identity and source hashes, rejects wrong topology/
geometry/return, and preserves the original knob dictionary. Ruff/format pass.
It imports no pytest/Torch/CuTe and executes no numerical oracle/native/GPU work.
All16 B3/S2/raw5 allocations are predictions until execution. Independent fixedS2
numerical helper avoids the timing wrapper's mixed2/3 b3_stage_observation helper.
The separate existing32-reset proof remains host evidence, not a GPU reset claim.

Performance owns runtime/launch and source/native gates. Numerical launch/results
are not yet claimed. Once actual AUTO driver/map is frozen, the independent reader
will use direct accepted B3b0cd current rows, original candidate validators once,
18 ranked choices per token and actual per-choice scheduler depth, preserving all
13 rows/104 choices+resources/1300samples. No baseline/controller recursion or
acknowledgment gate; no baseline/split/fixed rerun.


Entry045 subsequent environment loss supersedes the installed/live implication
above.0909b disappeared before numerical runtime staging upload: neither two GPU
reference jobs, exact public CPU reset test nor AUTO launched. Previously completed
local selector/AST and host-reset preparation is separate from the unexecuted
runtime checks. Installedef5a/receipt5be07228/preflight7637 remain durable historical
evidence on the vanished container; local runtime4fa9 is staged preparation only.
Sealed payload65151d7 is preserved unchanged. No numerical completion/owner is
inferred. B4's fully fetched original closure and rejection remain complete.

Managed inventory61283 true0 in logs/cu132-recovery0909b-curated18-devbox-inventory-001.log
reports no ziangli/c2 devboxes and0 schedulable nodes. Replacement request94255
for fi-w4a16-mega-0909c is applied and pending capacity, using c2/ziangli,8B300,
bare/no size and explicit nvcr.io/nvidia/pytorch:26.05-py3. Root's contemporaneous
live image record is logs/cu132-recovery0909c-image-selection-001.json; original
request log is logs/cu132-recovery0909c-devbox-request-ziangli-001.log. No replacement
container/host/source/driver identity or runtime result is yet established.

Hold reader binding until actual replacement source/runtime exists. Its changed
container/hardware identity can justify one new B3 Mega-only AUTO100 baseline;
this does not authorize routine per-trial baseline/split/fixed reruns. Published
02cf/B3/body7a6d remains unchanged. Performance owns request/setup; no new GPU
acknowledgment gate, remote operation or broad historical reread by integration.


Entry045 replacement recovery supersedes pending94255 above. Actual0909c setup
completiond37989e0 admits clean published489e/02cf on hu-pdx-115 with the same eight
physical GPU UUIDs and explicit26.05. Actualpreflight09ef71ef matches stable
B3 loaded stack fields apart from ASLR maps; prior native roots are absent.
The compact inherited267cc97e/evidence820c2ed4 directly associates prior B3
28/82, separate EP1 B2 fallback and test-only publication03c→489e. No old raw
validator/controller/cache-owner recursion or new-public-suite claim.

Two fresh EP2 runtime gates complete: original59395/fetch12035 true0, exactUUID
164ceb6300d647e99276cdd0da0d5632; summary2e5f4452 and outer02b1cb0d, numericmap4eec633d.
Independent audit7914bfd396ad982787d689c8bc62d40c09bd9e8b5695284affb4c090747cb51c
(logs/cu132-recovery0909c-b3-runtime-independent-001/audit.json) invokes original
validate_job_outputs once per job:24 summary file hashes,4 observed resources with
REG96/640/pool61440/two decode groups/local0. Resource probe has zero Mega launches;
graph sampler preserves valid/fault/recovery, replay8/0/8, samples2/0/2, one reset
per attempt and no failed-capture timing. These are runtime checks, not public
EP2/lifecycle reruns. Saved native chain0→12 and exact12 reuse d79f8c70 is new,
not the historical0909b22-entry inventory. Live ownership stays with performance.

Baseline001 outer47929 failed before driver/GPU on a stale outer four-mode guard;
failed outputs are preserved. A literal two-mode correction plus fresh002 run
name launches actual73292, UUIDFRESH_MODERN640_FULL13_3e3ff9f315c648cc874c85ffd8eb260a,
after source/native/idle PASS. Sealed driver/runtime unchanged (performance
b1a07209/47 files); no GPU timing rerun occurred. Full13 Mega-only AUTO100 now
measures retained B3 on the replacement container once.

Source-only baseline002 reader60b5e644 reuses the exact original pure checker AST
and direct completed new runtime receipt. It does not read active timing files
or older baseline controllers. Final accepted13 rows/104 choices+resources/
13 catalog16rankings/1300samples and native/allocation histograms remain pending
full fetch/canonicalclosure. Curated18 execution remains pending and will compare
against this actual new baseline. No PR/source promotion or fixed/split repeat.


Entry045 fresh0909c B3 baseline002 is now closed and independently accepted.
Original73292/fetch4515/close1952 all true0; closurec797184d570afa8fd3d4627636b7642b0e215fec89adfd9bc5a9d4a8d486035a
and idle50d4e80972c5071486c7d5a3b74a7f03c8fc93af2c0d6d7118a29cc3e9264ced bind
manifest a417f039/results8e172b41/executionc18547da/source489e/runtimeb1a.
[Accepted baseline](logs/cu132-recovery0909c-b3-auto13-baseline-001/accepted-baseline.json)
SHA92a17842f2aa3ea604079955f622a6569b436766abef19f44f610f9186040844 reconstructs
original auto.json once using its original saved validators; no older baseline or
public numerical controller walk. All13 rows/104 choices+resources/13 complete
catalog16 rankings/1300samples and68 direct hashes pass. Every actual compiled
object is B3/S3/REG96/640/two decode groups/local0; raw5×80/raw4×24.

| Tokens | Fresh0909c B3 Mega ms | Actual selected tactic (all S3) |
|---:|---:|---|
| 1 | 0.092945 | M128/N64, C2, F8, epi |
| 2 | 0.124737 | M256/N64, C2, F8, epi |
| 4 | 0.130897 | M256/N64, C2, F8, epi |
| 8 | 0.154385 | M256/N64, C2, F4, epi |
| 16 | 0.167729 | M256/N64, C2, F8, epi |
| 32 | 0.196273 | M256/N64, C2, F8, epi |
| 64 | 0.238881 | M256/N64, C2, F8, epi |
| 128 | 0.221042 | M256/N64, C2, F8, epi |
| 256 | 0.222547 | M256/N64, C2, F4, epi |
| 512 | 0.232866 | M256/N64, C2, F8, epi |
| 1024 | 0.246593 | M256/N64, C2, F4, epi |
| 2048 | 0.322929 | M256/N128, C2, F4, reuse |
| 4096 | 0.490194 | M256/N128, C2, F4, reuse |

Primary metric remains median of100 per-iteration maximum-rank cold-L2 CUDAgraph
CUPTI samples with3warmups; hot staged-wrapper/reducer graph-event scorer remains
secondary. Process917.801804702s and timingutility6.285932756s. No compilation
causality is assigned to the remainder. Native grows12→22 only through ten
dsv3_fused_routing entries and included JITlog update, no removals/otherdelta;
final7adab0d8dc60f9d95b2e8d7db47623967af3475d33e54344ea894f5ab4b1b58a.

This is the one replacement-container B3 timing baseline for subsequentcurated18,
not a source promotion or per-trial baseline repeat. Performance stages curated18
installer83027 alongside this audit; no candidate result yet. Receipt rows retain
raw winner dictionaries plus validated scheduler_stages3/config/actualallocation.
Future effective tactic-change counts normalize only the absent-before scheduler
field to this observed3 before comparing explicit2/3; all otherfields stay exact,
and raw dictionaries remain available. PR02cf/B3/body7a6d unchanged.


Entry045 curated18 execution update supersedes pending installation/numerics above.

Curated18 is installed on0909c: original64326/fetch20711/local exactsource pass
ef5a from489e; preflight89dcfd100f135b95a07f0eafda22a63fba6a57ac5ff7f8d42f729e69374b9ca4.
Numerical14995/fetch79052/41729 true0, UUID10c03d66307545cfb30d9f2d2a929fd6;
summary5e267f00ad96621fd1740e1841c12df70a7dbd071e2a28f0132b39fa0527afd9 /outer1e75e699,
numeric44-file mapeab270c1. Independent auditf94b7219297bcdbbd017874ccb4ee63eca470f93ba2e96b149708116cc5be91a
(logs/cu132-recovery0909c-scheduler-curated18-numerics-independent-001/audit.json)
runs original saved validators once:4 rank-tests/12 phase reports/16 actual
B3/S2/raw5/local0 objects, control336×8(N128)/352×8(N64). Original reference/
empty-refill/partial/scale/routing and3+1 exact graphs remain. Held public CPU
reset JUnit5ec35bf8 has exactly1pass, suite7.353s/test5.646s. All24 summary hashes
and both unchanged22-entry native7ada pairs pass; no baseline controller rerun.

AUTO00119240 failed before driver/GPU because numerical exit receipt1e75 was not
yet uploaded. Failure preserved; exactreceiptstage79998 true0. ActualAUTO002
original59344 runs after source/native/idle PASS, UUID
FRESH_MODERN640_FULL13_8cb57fedf7844f4594f5bdf32a34f5b8. Driverddd8067e /52-file
performance-map7ba92242 unchanged; no numerical/GPU timing rerun. Source-only
comparatorb6149024 awaits final002fetch/canonical002idle/closure, consumes direct
accepted92a, preserves13/104/1300 and13×18 rankings, and compares effective
tactics by resolving only absent-before scheduler field to validated actual3.
Rawdict changes remain separate; each actual candidate2/3 must agree with
config/kernel/fitter/params. No active timing read, baseline/split/fixed repeat,
new oracle or launch gate. Candidate performance/retention pending; PR02cf/body7a6d
unchanged.


Entry045 full curated18 AUTO comparison supersedes pending performance above.

Curated18 AUTO002 is now fully complete, original59344/fetch8317/close10293 true0.
Canonical closure448999e33e7ff844072db586f6f11eb54ef0c8453c28271697ee89170c02838a
and idle0a745569b76362b48ecee31562e5bbb840084530167a998a11a6aff73508b03a are exact.
Independent comparisonf8826827de034ade367c9d54407d96288b0314b6008b8e7af33a98bebd2f32ca
at logs/cu132-recovery0909c-b3-vs-scheduler-curated18-auto13-comparison-001
reconstructs original AUTO once against accepted92a:13 rows,104 choices/resources,
13×18rankings,1300samples,75 direct hashes. All actualB3/local0, raw5×80/raw4×24;
S2×64/S3×40. Kernel7e/testa7 unchanged; source delta is only autotune6d7→8454.
Native7ada remains exactly22 entries. Process947.304062993s versus917.801804702s;
timer utility5.908078584s versus6.285932756s. No causal attribution of remainder.

GM curated18/B3=0.9519206430453637:4.80794% lower latency,1.050507736× speedup,
11/13points faster. RegressionsT256+1.143% andT2048+4.494%. Eight effective
tactic changes atT2/4/8/32/128/256/512/4096 all selectS2; other5 remainS3. All13
raw dictionaries differ because old16 previously omitted the scheduler field;
those differences are preserved separately, with only absent-before stage
normalized to validated3 for effective comparison. Complete table is in the
report and ledger. Sourceef5a remains installed; retention/publication decision
is pending root. Published02cf/B3/body7a6d unchanged; no PR action by integration.

| Tokens | Baseline B3 ms | Curated18 ms | Change | Speedup | Baseline effective tactic | Current tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.092945 | 0.091473 | -1.584% | 1.0161× | M128/N64, C2, F8, epi, S3 | M128/N64, C2, F8, epi, S3 |
| 2 | 0.124737 | 0.112496 | -9.813% | 1.1088× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.130897 | 0.128033 | -2.188% | 1.0224× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.154385 | 0.137617 | -10.861% | 1.1218× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.167729 | 0.155218 | -7.459% | 1.0806× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S3 |
| 32 | 0.196273 | 0.179777 | -8.405% | 1.0918× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.238881 | 0.214370 | -10.261% | 1.1143× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S3 |
| 128 | 0.221042 | 0.200002 | -9.519% | 1.1052× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.222547 | 0.225090 | +1.143% | 0.9887× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.232866 | 0.222722 | -4.356% | 1.0455× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.246593 | 0.244978 | -0.655% | 1.0066× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F4, epi, S3 |
| 2048 | 0.322929 | 0.337443 | +4.494% | 0.9570× | M256/N128, C2, F4, reuse, S3 | M256/N128, C2, F4, reuse, S3 |
| 4096 | 0.490194 | 0.482980 | -1.472% | 1.0149× | M256/N128, C2, F4, reuse, S3 | M256/N128, C2, F4, reuse, S2 |


Entry045 retention and publication preparation supersede the pending decision
above. Root retains curated18: GM0.9519206430453637 (4.808% lower latency),
11/13 wins, with T256 +1.143% and T2048 +4.494% disclosed. Eight effective
choices select S2; unchanged-tactic variation (T64 −10.261%, T2048 +4.494%)
precludes fixed-tactic causal attribution. The full table and frozen independent
comparisonf882 are unchanged. Its current rows/choices are now the direct
retained baseline for later authorized full13 Mega-only AUTO100 trials.

Root committed and pushed5aa053a5cbda629ac2cefaf11d0ec1fcac3585be, all hooks
PASS and push12540 true0. Published source6d253a72896a0a82ac50a2c44c8b2d340f8ed0bd155069490d1ea4aa51bf35a6
is measured ef5a with only tests/moe_ep/test_w4a16_autotune.py52fb→the exact
executedb862 CPU regression module. Catalog8454/kernel7e are byte-identical.
Proof logs/pr5019-curated18-publication-source-001.json
SHAd17f709faeecb3839af5f0ad0357a6d657e639ea6d86a96f1e19c668b17e6c9f;
no numerical/timing rerun accompanies this test-only publication change.

Proposed PR_BODY-curated18-proposed.md
SHA6dfafa6b45eb2b483ce98e6689f36d7c9a4f22a5454fd04e10e56abed2e69180
contains one current132 table, unchanged explicitly reused0909a split column,
selected S2/S3, exact measured/published association, current4/16+CPU execution
and inherited B3 28/82/fallback scope. The130 table, checklist and @humansand
are byte-identical. Direct latency examples T32 .196273→.179777ms and
T4096 .490194→.482980ms are included without another history table. Two separate
EP2 reproduction commands invoke published helpers with exactly the executed
reference arguments; standalone commands were source-checked, not rerun, and
are distinguished from actual private observer receipts. Proposed proofac9cb602.
The native statement correctly records completed baseline22-entry reuse;
baseline first-use inventory grew12→22, outside primary timing.

Root's current-head5aa checks in logs/pr5019-curated18-check-runs.json and
logs/pr5019-curated18-ci-annotations.json report pre-commit/Build Docs/claude-review
success; GPU matrix skipped, summary explicitly pending repository authorization
(run34374949025/check102545319534). No labels/comments/CI trigger. At this entry
root body publication remains pending; integration changed only the proposed
draft and local state/ledger, not canonical PR bodies or GitHub.


Entry045 publication closure: root published and read back PR5019 as draft at
head5aa, exact body6dfafa6b45eb2b483ce98e6689f36d7c9a4f22a5454fd04e10e56abed2e69180.
Receipt logs/pr5019-curated18-publication.json
SHA70fe607d15dd94ef55fbb30abd650c0f93f28184fc43608552a8ca847a5565ca;
readback logs/pr5019-curated18-body-readback.json
SHAb12963cc7518669a457d208293a7095b79b11d073afeb3c79fe2b8a61144364e.
Integration rehashed the saved body and canonical PR_BODY.md/current-modern/
curated18-full13 exact; oldB3 body7a6d remains historical.130 table/template/
@humansand unchanged, no comments or labels. This supersedes pending publication
above without changing the frozen proposed proof's historical status.

Remote publication sync association2b86b3e9/completion3fe3f722 under
logs/cu132-recovery0909c-curated18-publication-sync-001 are passed. Only executed
public CPU-test bytes52fb→b862 change, exact ef5a→published6d253; completed22-entry
native7ada inventory is unchanged. No GPU/native/numerical rerun.

## Entry 046 — Cold graph-event scorer installed; validation and AUTO pending

Performance installed selected source
7bfafa1b0d5e38d64c717cc1c9c7824fec808a9e8ae64e8c438490f2bedf1f00
from published curated18/source6d253 on0909c. Original install/preflight exit
logs/cu132-recovery0909c-cold-graph-install-preflight-001.exit.json
SHAe38f1f880a592c11791f2956cf9b470a8fbf9f30699db2b69b465d13786641b8 is0;
install receiptac4896b2e673ad90be520b15fe5ca64c1401bdefaf2f760326a08e1605bf8fc5
and actual preflight819227c801dca35767912f3226204b41e6cac582c358c4d86f58757934bb259d
are fetched. Source-constructionbb969593 records module8454→325169b2 through
only the scorer/cache-source changes; the18-tactic factory, B3 kernel7e and
publictestb862 are unchanged. Its held-source-only status is preparation-era
prose; actual installation is established by the separate receipts above.

The selected scorer requests the existing outside-event L2-flush mechanism and
uses a distinct cold scoring cache source. It does not prove complete hardware
eviction and does not replace the primary CUPTI rank-MAX metric. Approved runtime
scope is9 CPU checks plus1 existing EP2 graph sampler, then one full13 Mega-only
AUTO100 against directly accepted curated18f882 current rows. No outcomes are
claimed yet; frozen runtime/launch/results/closure are performance-owned and
independent saved audits wait for actual completed artifacts. They are not
additional execution gates. No repeated baseline/fixed/split timing or old
numerical suite. The frozen candidate README's16-tactic/lifecycle scope is
historical and is superseded by the selected18-tactic9+1 scope here. Published
PR5aa/body6dfa and retained curated18 evidence remain current.


Entry046 actual validation closure: original10924/finalfetch23127 true0,
UUID FRESH_MODERN640_VALIDATION_b944ee43a31d4ab7ab1153e24d481d75. Summary
660da5151c645333d19a8b279cf8389b5f6f2dce0e931a4e1f06189c12e849f6 /
outer9536166f017074e3fa2f4045d277bc0ea0768593fadd905c46279e18bcc12733.
Independent original saved auditb903f77ca645eeadcc69441190701587cf41345c06be61ed77fb9e5c9740415d
in logs/cu132-recovery0909c-cold-graph-numerics-independent-001 passed once:
9 exact CPU tests/0.038s, original EP2 sampler2 local0 resources,6 attempts and4
actual cold-utility calls, original valid/fault/recovery/own-rank sample/reset
contracts,12 summary hashes and unchanged22 native entries. No public-suite or
baseline-controller rerun. Numeric runtime8066c9ee contains49 files.

Actual cold AUTO31887 is running after receipt stage21925 and live source/native/
idle gates pass: UUID FRESH_MODERN640_FULL13_b95957d6dc4c41daa6fcbf6f9093644d,
run cu132-recovery0909c-cold-graph-auto13-001, performance57-file map368ee78a.
Held saved reader logs/cu132-recovery0909c-cold-graph-auto-analysis-prep-001/check_and_compare.py
SHA5413f6b62dbd35a7a48f17ba4a439a936da5a65b9b63424222e1ff0a53c73132
preserves the original current-source checker AST, directf882 current columns,
full13/104/13×18/1300 and exact explicitS2/S3 dictionaries without normalization.
It will run only after completed saved fetch/source/native/idle closure. No
partial timing or retention claim; current publication remains curated18.


Entry046 next-trial steering supersedes the earlier16-then8 recommendation:
root favors direct fixedS2 M256-only8 (N64/N128 × F4/F8 × epi/reuse) if the
completed cold rankings show marginal M128/S3 advantages; clean Cartesian16
S2/S3 is the fallback. Current cold31887 is still running, so neither next source
selection nor a performance outcome is recorded. Hot-only ranking JSONdef5b557
is unchanged; its README recommendation is updated. Only2 of8 prospectiveS2
configurations have scores so far; subset score differences are rounded
secondary evidence, not predicted primary CUPTI latencies or permission to
splice winners. Full cold13 comparison/rankings await actual saved closure.


Entry046 full AUTO closure and rejection. Original31887/fetch24409/close78461
all true0. Canonical closure4a04dcceb524588c35e1cb745802172c52b2bf5757a1c928815406772146674e /
idle33e16b3eaab6114c09233f9a5c025f7c129b52faddefc068b25440d89243976f
bind exact source7bfafa and unchanged22 native7ada entries. Independent original
saved reader passes once; full report
logs/cu132-recovery0909c-curated18-vs-cold-graph-auto13-comparison-001/comparison.json
SHA2b042ead03a2a5b97b82a9a69550da75ccea30ba894b581ceebbcfda97a4b079.
All13 rows/104 choices+resource objects/13×18 rankings/1300 samples reconstruct
exactly,79 direct hashes pass. Actual B3×104,raw5×80/raw4×24,S2×48/S3×56,local0.
Process969.659847804s; timer utility6.047071689s, distinct from the primary metric.

Root rejects cold scoring: GM1.0153689677759803 (+1.537% latency),6/13 wins,
4 exact tactic changes at1/64/128/256. All7 regressions are preserved below;
T32+11.633% occurs with the same selected dictionary, so this sequential trial
does not establish a fixed-tactic causal effect. No minima/drift adjustment or
new split run. Root authorized restore to published hot18/source6d253; restoration
is pending the actual performance receipt at this entry. PR5aa/body6dfa remains
current. The report's original pending-root field remains frozen and is
superseded by this rejection decision.

| Tokens | Retained curated18 ms | Candidate cold scoring ms | Change | Speedup | Retained tactic | Candidate tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.091473 | 0.091409 | -0.070% | 1.0007× | M128/N64, C2, F8, epi, S3 | M128/N64, C1, F8, epi, S3 |
| 2 | 0.112496 | 0.115409 | +2.589% | 0.9748× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.128033 | 0.126801 | -0.962% | 1.0097× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.137617 | 0.147713 | +7.336% | 0.9317× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.155218 | 0.160994 | +3.721% | 0.9641× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S3 |
| 32 | 0.179777 | 0.200690 | +11.633% | 0.8958× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.214370 | 0.202498 | -5.538% | 1.0586× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F4, epi, S3 |
| 128 | 0.200002 | 0.217842 | +8.920% | 0.9181× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S3 |
| 256 | 0.225090 | 0.225891 | +0.356% | 0.9965× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S3 |
| 512 | 0.222722 | 0.229683 | +3.125% | 0.9697× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.244978 | 0.237619 | -3.004% | 1.0310× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F4, epi, S3 |
| 2048 | 0.337443 | 0.320211 | -5.107% | 1.0538× | M256/N128, C2, F4, reuse, S3 | M256/N128, C2, F4, reuse, S3 |
| 4096 | 0.482980 | 0.476181 | -1.408% | 1.0143× | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Full secondary ranking ablation
logs/cu132-recovery0909c-scheduler-ranking-ablation-001/full/analysis.json
SHA11aac43bafcb036e360e7ce5fe4365b8a0f788ff558d098ae427ad612acb9c1a
preserves all13 rows in each of freshB3 hot16, retained hot18 and cold18, with
source/run/direct input hashes and every rounded candidate score/dictionary.
It calls no historical validators. M128 has a lower best score only atT1:
67.6→68.5us (+0.9us/+1.331% M256 penalty) for hot16;
67.5→68.4us (+0.9us/+1.333%) for hot18;
69.6→69.7us (+0.1us/+0.144%) for cold18. Printed precision is0.1us.

Worst availableS2-versus-bestM256S3 gap is hot2048 +2.8us/+0.955%, and coldT1
+2.0us/+2.869%. ColdT1 compares different flags; matched N64/F8/epi S2 andS3 both
score71.7us. Other coldS3 subset advantages are at most2.0us/+0.678% (T2048).
All13 exact two-pair comparisons are separately tabulated. Only2 of8 prospective
S2 combinations were measured; these are secondary graph-event selection
scores, not primary CUPTI rows or predicted fixed8 latencies.

## Entry 047 — Fixed-S2 M256-only8 selected; actual runtime pending

Root selected direct fixed_s2_8 on retained hot scoring, using M256/C2 ×
N64/N128 × F4/F8 × epi/reuse with explicitS2. The Cartesian16 S2/S3 option remains
a held fallback, not a mandatory preceding run. The small cold subset margins
and T1-only M128 contribution justify testing this reduced catalog; they do not
prove all8 S2 configurations dominate. Performance is authorized to install,
validate and run the complete full13 Mega-only AUTO100 after its original gates,
without another acknowledgment. Direct retained baseline remains curated18f882
current rows/choices; cold rejected output is not the timing baseline. Actual
fixed8 source/runtime/launcher pins and completed outputs are pending; integration
will adapt the existing saved reader narrowly and audit only completed files.


Entry047 held reader/body preparation: saved AUTO skeleton
logs/cu132-recovery0909c-fixed8-auto-analysis-prep-001/check_and_compare.py
SHA4f139fdf977f1e43e8a9a87b2bb4a63e648245315f51b9a3174a72044eba9262
reuses the existing checker with only catalog18→catalog8 API change, direct
hot18f882 current columns, exact explicitS2 dictionary matching and dynamic
resources. It is deliberately unbound and stops before candidate reads until
actual source/map/driver/numerical/summary/launcher pins arrive. The selected
runtime folder is candidates/cuda132_recovery_0909c/m256_fixed_s2_8. Planned
fresh scope is one original EP2 all8 lifecycle (16 oracle records but20
prelaunch resources:8 candidates+2 observations/rank) plus the updated public
CPUreset once; no all8 completion is claimed from earlier two-case evidence.

Held PR_BODY-fixed8-proposed.md
SHA9f26242088823ddf023fb9dd6a64571304e8ac5240ea3a7816635f943865140f
contains clean8 M256/C2×N64/N128×F4/F8×epi/reuse with fixedS2, preserving manual
M128/S3/default3/cache behavior and hot scoring. Exactly one132 table keeps the
13 reused split values with new Mega/ratio/tactic cells pending;130 table and
PR template/@humansand remain exact. Measured-source/CPU/all8 lifecycle/fullAUTO
fields await actual completed data. Inherited B3 remains explicit. No
canonical PR/GitHub or production edits; root owns later publication decisions.


Entry047 actual direct validation and AUTO launch supersede the held coordinator
preparation above. Installed source2fe05f0abbf337ef0353407be941cdac74fe0a1efa3aa5d83a4a0e01b822704a,
factory69116625/test7292/kernel7e, actual preflight7cac48e0. Direct completion
logs/cu132-recovery0909c-m256-fixed-s2-8-direct-validation-001/completion.json
SHA7dd53a9cc93c84802fe55b2b651e19291fbd5cd433bbb9ff683a05d00205e5cb
binds original77781/fetch57532/idle34614/stage7019, all closed0. Independent audit
logs/cu132-recovery0909c-fixed8-direct-numerics-independent-001/audit.json
SHA689fd22ec6e76dc014a8fe256bba73381ee49c93835b70559c9e88c28c36dc5b
uses the existing pure lifecycle validator with only its explicit lifecycle.log
filename parameter. No coordinator success/summary/map was fabricated.

Actual CPU public module7292 passes one test, eight S3-to-selected-S2 reset
transitions, JUnit suite0.336s/test0.072s (printed0.34s), process7.448227818s.
The original EP2 all8 lifecycle passes16 candidate-oracle records (eight nonempty,
eight empty),20 prelaunch resource observations, one tune per rank, cache-loaded
layer/winner agreement and three stable plus one changed-input exact graph replay
per rank. All16 scalar candidate records are B3/S2/raw5; control bytes336×8/352×8.
All20 resources are REG96/640/local0, pool61440; the extra two observations per
rank remain resource-only scope. Lifecycle process58.812407058s. Source before/after
matches and complete22-entry native inventory7ada is unchanged.

Actual AUTO90531 uses direct runcu132-recovery0909c-m256-fixed-s2-8-auto13-direct-002.
Unchanged benchmark shell/640 observer/full13×100, fresh knob/DSL/driver caches
and completed22-entry native reuse. Direct001 failed before benchmark invocation
on duplicate metadata key; corrected runtime_helper_sha256 in002, no timing rerun.
Actual invocation/execution/raw/provenance/source/native files replace the
unexecuted held controller schema; no original auto.json/results.json claim.
The independent direct comparison will use acceptedf882 only after complete fetch.
No retention or new timing values are assigned while execution remains active.

Held draft PR_BODY-fixed8-proposed.md nowSHA3f8aed076048c2f62c127f4fd98dc26e719c80162f93c093a21bd0fa2c9e5da2;
proof002 preserves unchanged130 table, template and canonical6dfa. Actual validation
is populated; thirteen current132 values and publication IDs remain pending. The
public all8 numerical/graph-helper reproduction is source-checked but not executed
as a combined snippet; it does not claim to be the private cache/resource harness.


Entry047 completed fixed8 direct result — rejected by root.

Original90531/fetch70044/canonical idle47283 allclosed0. Completion2de966ab4f18c140374bc9aee23aa477248becf14a0ea883c2b602179c137f4f,
invocation9166c3bc/execution8559b56f/outer6c36d13e/native7ada. Idle66760826 was
separately executed after AUTO; its exact source/native/empty-process fields match
the prior numerical idle JSON, hence equal bytes, not an inferred reused check.
Independent comparison logs/cu132-recovery0909c-hot18-vs-fixed8-direct-auto13-comparison-001/comparison.json
SHA395a8dce3eda0cdff09b854fa3586451b123dc6dcba30b561b9f2f30a7dbd743
calls original pure raw/sample/resource/catalog/scorer validators once on actual
completed direct files. The separately named reconstruction is not an original
auto.json/results.json or coordinator completion. Direct acceptedf882 only;
no baseline validator recursion.

Complete13/104/13×8/1300 checks pass. All104 B3/S2/local0, raw5×88/raw4×16;
complete22-entry native inventory unchanged. GM1.0335363709449932 (+3.354%),
onlyT256/T2048 faster, seven exact choices changed. Benchmark subprocess
581.6157582269952s versus947.304062993s is38.603% shorter. Outer583.744444709s
and timerutility5.963020334s are distinct, with no wholesale attribution of the
remainder to compilation or tuning. Several unchanged choices regress; no causal
fixed-tactic interpretation, minima, drift correction or selected-row replacement.

| Tokens | Hot18 ms | Fixed8 ms | Change | Speedup | Hot18 tactic | Fixed8 tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.091473 | 0.092689 | +1.329% | 0.9869× | M128/N64, C2, F8, epi, S3 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.112496 | 0.122017 | +8.463% | 0.9220× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.128033 | 0.135169 | +5.574% | 0.9472× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 8 | 0.137617 | 0.148738 | +8.081% | 0.9252× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 16 | 0.155218 | 0.165250 | +6.463% | 0.9393× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 32 | 0.179777 | 0.192369 | +7.004% | 0.9345× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.214370 | 0.214466 | +0.045% | 0.9996× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F4, epi, S2 |
| 128 | 0.200002 | 0.218194 | +9.096% | 0.9166× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.225090 | 0.220193 | -2.176% | 1.0222× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.222722 | 0.227042 | +1.940% | 0.9810× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.244978 | 0.245235 | +0.105% | 0.9990× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F4, epi, S2 |
| 2048 | 0.337443 | 0.331411 | -1.788% | 1.0182× | M256/N128, C2, F4, reuse, S3 | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.482980 | 0.485093 | +0.437% | 0.9956× | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Root rejects default fixed8 and selects clean Cartesian16 with adjacent S2/S3
pairs next, on the retained HOT scorer. Canonical PR/source retention remains
curated18/5aa/body6dfa. Historical proposed fixed8 body b18ee9e44807465fb9a739b4a593138fc23138856da9647bd3dbf257eba5f80b
contains the complete132 rows and actual validation, explicitly unpublished;
130 table/template/canonical remain unchanged. No further fixed8 audits.

## Entry 048 — Clean M256 Cartesian16 selected; actual execution pending

Use M256/C2 × N64/N128 × F4/F8 × epi/reuse × explicit scheduler2/3, adjacent
S2/S3 dictionary pairs, HOT scorer and unchanged B3 kernel. Root authorizes direct
install, one actual64-reset CPU test and complete13×100 Mega-only AUTO. Reuse
just-passed all8 S2 lifecycle coverage plus existing same-kernelS3; no broad
numerical/native/coordinator rerun. Actual source/driver/CPU/launch pins pending.
Primary retained timing comparison is hot18f882. Report fixed8/395a as a separate
secondary whole-run comparison using saved rows only, without promoting it or
calling it a causal fixed-tactic control. Preserve all13 matched S2/S3 score pairs
from the complete16 rankings; these rounded hot-event scores differ from primary
CUPTI latency. No production/GitHub changes by integration.


Entry048 actual install/CPU completed and direct AUTO active.

Selected sourceab35b52e32b3882bfbc04c17d6548de74bc9e38e3462d9a6fa7baf607ebfe4a0,
source-manifest140999c5, factory99b624cceaeaa81525c826c4a45da64a0f84b551e80799c9e68e758e7b9e2761,
restored public CPU testb862dc217ff6199c1b35863ce977ca9d14af1bea7f99e70d6d30e684380b9e90.
Kernel7e and source helpers unchanged; installreceiptb3ab68f8 changes only the
factory/test paths from fixed8. Original80345/fetch16570 closed0. Actual preflight
f199772a, CPUexit13a81eec/sourceafterd100ac92, native7ada22 entries unchanged.

One saved CPU/install audit:
logs/cu132-recovery0909c-product16-cpu-independent-001/audit.json
SHAfc98e6100030cc3940cbd13292ac54d3ab4a9d7b820a894b60b64444e7308c54.
The executed testb862 nests eightS2 choices and eightS3 winners:64 actual reset
transitions, one passing public test. Printed0.40s; JUnit suite0.398s/test0.116s;
CPU subprocess12.628752670s, outer install/preflight/CPU27.215968375s. No local
CPU regression rerun or new GPU lifecycle. Static extraction of the exact
source factory matches catalog16 ordered adjacentS2/S3 pairs. Existing S2 all8
lifecycle689 and inherited same-kernelS3 cover GPU behavior separately.

Six-helper stage92192 passed; original directAUTO51139 is active as
cu132-recovery0909c-m256-cartesian16-auto13-direct-001. HOT scorer/full13×100;
actual timing/closure pending. Original pure saved reconstructor1dc94e61 imports
only result/sample/scorer/catalog/compiled checks, no run_full13/fresh_session/
owner. Independent successor66b0d8dd at
logs/cu132-recovery0909c-product16-direct-auto-analysis-prep-001/check_and_compare.py
retains actual16 rankings and per-object2or3 equality, direct primaryf882 and
secondary whole-run395a. It records all13×8 matchedS2/S3 secondary score pairs,
with rounded0.1us tie/finite boundaries; no causal CUPTI or fixed8 promotion claim.
No active output reads; actual completion/closure supplies the final bound inputs.

Held PR_BODY-product16-proposed.md now3834179b81fdfce8df33760117b445c68214765d0d77e26e87d95abc6b1495f1;
proof002 records actual source/CPU and inheritedGPU scope; all13 timing rows and
publication remain pending. Canonical PR6dfa,130 table and template unchanged.


Entry048 full direct AUTO and independent comparison completed; retention pending.

Original51139/fullfetch28841/idle11770 alltrue0. Completionb97b90c767bd665d6b998d8c68d5b686d4e5919887a8f271889ef352b6fcc50a,
idle93796998, invocation46a51001/execution4f269ae7. Actual22 native entries7ada
unchanged. The original pure reconstructor1dc94e61 reports e315d525 and
resultfabdfa44; integration calls that same pure path once on saved files into
its separate reconstruction folder, with no original coordinator files claimed.

Independent comparison:
logs/cu132-recovery0909c-hot18-vs-product16-direct-auto13-comparison-001/comparison.json
SHAcc8125bede03a0dd54890b88ed176b102e19c513f1559bacf6113ce13c366228.
Full13/104/13×16/1300 passes, B3×104/local0×104, raw5×88/raw4×16, S2×64/S3×40.
Direct retainedhot18/f882 primary GM1.029682434652108 (+2.968%),4wins
(64/256/1024/2048),9 choices changed. Actual subprocess931.376520229s versus
947.304062993s (-1.681%); outer933.347782500s and utility6.108232847s are separate.
No timing minima, selected rows, drift adjustment or causal fixed-tactic claim.

| Tokens | Hot18 ms | Cartesian16 ms | Change | Speedup | Hot18 tactic | Cartesian16 tactic |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.091473 | 0.093120 | +1.801% | 0.9823× | M128/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S3 |
| 2 | 0.112496 | 0.120913 | +7.482% | 0.9304× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 4 | 0.128033 | 0.136881 | +6.911% | 0.9354× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 8 | 0.137617 | 0.147537 | +7.208% | 0.9328× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 16 | 0.155218 | 0.164466 | +5.958% | 0.9438× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S3 |
| 32 | 0.179777 | 0.193778 | +7.788% | 0.9277× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.214370 | 0.205570 | -4.105% | 1.0428× | M256/N64, C2, F8, epi, S3 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.200002 | 0.210610 | +5.304% | 0.9496× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 256 | 0.225090 | 0.223714 | -0.611% | 1.0062× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.222722 | 0.232994 | +4.612% | 0.9559× | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 1024 | 0.244978 | 0.239347 | -2.299% | 1.0235× | M256/N64, C2, F4, epi, S3 | M256/N64, C2, F4, epi, S3 |
| 2048 | 0.337443 | 0.331955 | -1.626% | 1.0165× | M256/N128, C2, F4, reuse, S3 | M256/N128, C2, F8, reuse, S3 |
| 4096 | 0.482980 | 0.488757 | +1.196% | 0.9882× | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S3 |

Secondary whole-run comparison against rejected fixed8/395a uses its accepted
current rows only, without re-running its validators or treating it as retained:
GM0.9962711169135137 (-0.373%),6/13wins, subprocess+60.136%. This is sequential
AUTO behavior, not an isolated effect of addingS3. Full secondary table follows.

| Tokens | Fixed8 ms | Cartesian16 ms | Change |
|---:|---:|---:|---:|
| 1 | 0.092689 | 0.093120 | +0.465% |
| 2 | 0.122017 | 0.120913 | -0.905% |
| 4 | 0.135169 | 0.136881 | +1.267% |
| 8 | 0.148738 | 0.147537 | -0.807% |
| 16 | 0.165250 | 0.164466 | -0.474% |
| 32 | 0.192369 | 0.193778 | +0.732% |
| 64 | 0.214466 | 0.205570 | -4.148% |
| 128 | 0.218194 | 0.210610 | -3.476% |
| 256 | 0.220193 | 0.223714 | +1.599% |
| 512 | 0.227042 | 0.232994 | +2.622% |
| 1024 | 0.245235 | 0.239347 | -2.401% |
| 2048 | 0.331411 | 0.331955 | +0.164% |
| 4096 | 0.485093 | 0.488757 | +0.755% |


All104 exact S2/S3 matched score pairs are saved in matched-scheduler-scores.md
and comparison.json, and concise all13 subset summary JSON59464fd818b4dd6e505534a1cc10fe94133fb87e6021cfed39914b693907f47a
at scheduler-score-summary.json. Of104 pairs, S2 lower65/S3 lower28/11 printed ties.
Best S3 subset wins onlyT1/16/1024/2048/4096, with bestS2 cost1.1/.1/.4/2.1/1.4us,
1.630/.081/.191/.715/.309% relativebestS3. Largest exact-pair S3 gap isT1
N64/F4/reuse82.8→81.0us (2.222%) but that nonwinning pair is not the best subset.
These are rounded0.1us hot CUDA-event max-of-rank-median selection scores;
no primary latency prediction, throughput claim or uncertainty estimate.

Held PR_BODY-product16-proposed.md now47963c76e503a3416eec6b54f8f74efddf231a5ccbbcdfb64ebe64ee14ebf17b:
one complete current132 table, actualsource/CPU/resources/closure, comparable
process-wall scope, explicit higher GM/unchanged-choice limits, unchanged130/
template/@humansand. Only publicationcommit remains pending. Canonical5aa/body6dfa
is untouched; retention/sourcewindow belongs to root.


## Entry 049 — One fresh retained18 control authorized for the new discrepancy

Root explicitly authorizes ONE later retained18 whole-run control after the three
cold/fixed8/product16 trials: both reduced catalogs are approximately3% behind
oldf882, with repeated unchanged-tactic regressions; product16 is only0.373%
faster geometrically thanfixed8 while pairedS3 best-subset benefits are limited.
This concrete discrepancy justifies a check of the retained control now, not
routine per-trial baseline reruns. Restore exact publishedsource6d253 and run
one direct full13 Mega-onlyAUTO100 on HOT18, without numerical/native/CPU reruns.
No publication before the result; performance owns restore/launch/closure.

Preserve f882,395a andcc812 as complete independent runs. The later control is a
fourth whole-run column, with no row replacement, minima, interpolation or drift
adjustment. Report fresh18/old18 primary, plus separately labeled fresh18 versus8
and16 whole-run comparisons in both ratio directions. Neither candidate evidence
nor earlier retention is retroactively altered. Unchanged-choice comparisons
remain descriptive rather than causal throughput estimates.

Minimal pure report helper:
logs/cu132-recovery0909c-hot18-control-direct-auto-analysis-prep-001/four_run_report.py
SHAd7105d216fc8278cd6324eba33ceb3402c57c9c92f3e467bf7d0506fe0dde2f1.
It consumes a caller-validated complete fresh report and direct accepted rows from
f882/395a/cc812, preserving source/run/process/sample metric identities and all13
rows. It calls no validators. Actual fresh run/interface/closure are pending,
so no fresh result is read or fabricated. Performance child owns minimal original
HOT18 pure reconstruction. Current PR remains5aa/body6dfa unchanged.


Entry049 actual restored control and active benchmark:
exact restore65889/stage9034/fetch53239 alltrue0, completion95c5fccb35d948794819cff57072beef1c1fa6d96862417e07240303cc300c5d
under logs/cu132-recovery0909c-hot18-restore-from-cartesian16-001.
Receipt1305becc changes only the factoryab35→6d253; testb862/kernel7e remain
published bytes. Native22 unchanged7ada, sourceafter2d7c1693. No CPU/GPU/native
validation rerun. Actual source gate checks full6d253, original89dc preflight
matches unchanged loaded runtime modules. Six HOT18 helper copies remain exact.

Original later-control AUTO88514 active:
cu132-recovery0909c-hot18-later-control-auto13-direct-001, full13/100. Prepared
original pure reconstructor1eb9f58e3d2cca9f32f5e54d33307843cbe46e7d9391091609d4ffbf09b6edf0
and independent direct wrapper3522280aad1529e9d97c8e10db7f69aca709c4295d6daff5caf41d0e7f73fc9f
at logs/cu132-recovery0909c-hot18-control-direct-auto-analysis-prep-001/check_and_compare.py
bind actual restore/source/native fields, all18 candidates and mixed2/3 observations.
No invented currentCPU/lifecycle evidence or coordinator files. Report helperd710
adds all13 whole-run columns from directf882/395a/cc812 only, preserving ratio
direction, choices and subprocess-wall scopes. Actual full fetch/closure are
pending; no active timing data read. Current PR/publication remains5aa/body6dfa.


Entry049 complete later retained18 control and four-run saved audit.

Original88514/fullfetch41505/idle61157 alltrue0; completion8f96833091e36346fad5a8430dc6be8275aa6ccb45233d5f1e5f1c1d3f8e9cf0,
idle9770fa50. Original pure reconstruction2bfa9de6/result187cd430; independent
single saved pass uses the same original pure checks into a separate reconstruction,
with no historical validator rerun or synthetic coordinator files.

Independent complete report:
logs/cu132-recovery0909c-hot18-later-control-four-run-comparison-001/comparison.json
SHAbc0874949f880b024bd599179e2d7bc43116144f62406626e04a287206829f91.
All13 raw rows/104choices-resources/13×18 rankings/1300 samples pass. B3all/local0,
raw5×88/raw4×16,S2×80/S3×24; exact22 native entries unchanged7ada. New source6d253
differs from the original hot18 measuredsourceef5 only by the executed public-test
publication52fb→b862, with no timing/kernel/factory change. Existing validation
is reused, no new CPU/lifecycle/native execution. Actual subprocess944.747875375s,
outer946.977045708s, timerutility5.955946419s are distinct.

Four complete-run columns are bound in four-run-comparison.json
SHA3155657e9148dd25f5bc23b38921e8b487c429c96c499238f56bb963f4cc1fd0.
No row replacement, minimum, interpolation, drift correction or retrospective
baseline alteration. Full table follows.

| Tokens | Old18 ms | Fixed8 ms | Product16 ms | Fresh18 ms | Fresh18 / old18 change |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.091473 | 0.092689 | 0.093120 | 0.081041 | -11.404% |
| 2 | 0.112496 | 0.122017 | 0.120913 | 0.122417 | +8.819% |
| 4 | 0.128033 | 0.135169 | 0.136881 | 0.134609 | +5.136% |
| 8 | 0.137617 | 0.148738 | 0.147537 | 0.144962 | +5.337% |
| 16 | 0.155218 | 0.165250 | 0.164466 | 0.165697 | +6.751% |
| 32 | 0.179777 | 0.192369 | 0.193778 | 0.188546 | +4.878% |
| 64 | 0.214370 | 0.214466 | 0.205570 | 0.214753 | +0.179% |
| 128 | 0.200002 | 0.218194 | 0.210610 | 0.221490 | +10.744% |
| 256 | 0.225090 | 0.220193 | 0.223714 | 0.218754 | -2.815% |
| 512 | 0.222722 | 0.227042 | 0.232994 | 0.229153 | +2.887% |
| 1024 | 0.244978 | 0.245235 | 0.239347 | 0.247938 | +1.208% |
| 2048 | 0.337443 | 0.331411 | 0.331955 | 0.323122 | -4.244% |
| 4096 | 0.482980 | 0.485093 | 0.488757 | 0.488421 | +1.127% |

| Whole-run reference | Fresh18 / reference GM | Fresh18 latency change | Reference / fresh18 GM | Reference latency change |
|---|---:|---:|---:|---:|
| old18 | 1.020362992 | +2.036% | 0.980043384 | -1.996% |
| fixed8 | 0.987254073 | -1.275% | 1.012910483 | +1.291% |
| product16 | 0.990949207 | -0.905% | 1.009133458 | +0.913% |

| Run | Benchmark subprocess wall s | Timer utility wall s |
|---|---:|---:|
| old18 | 947.304063 | 5.908079 |
| fixed8 | 581.615758 | 5.963020 |
| product16 | 931.376520 | 6.108233 |
| fresh18 | 944.747875 | 5.955946 |

Subprocess wall is compared only with subprocess wall; neither wall quantity is the primary median CUPTI latency. Full raw choices and exact dictionary changes remain in the JSON.


The later18 control is2.036% slower geometrically than oldf882, with three points
lower and five selected dictionaries changed. Relative to this separate later
control, fixed8 is1.291% slower geometrically (7/13 lower) and product16 is0.913%
slower (5/13 lower). These results are unadjusted full-run ratios in each stated
direction. They do not replace the earlier candidate-versus-old18 comparisons.

Same-choice evidence is saved in same-choice-variation.json
SHAd928442b0b81a1b611d916d3ca3574b93dc5cffab3495b89862e430e03f73f71,
with all13 dictionaries and row-level comparisons in its Markdown companion.
Exact earlier/later matches: old18 eight rows, fixed8 six, product16 four.
Earlier/later same-choice percentage ranges: old18 -9.702..+4.432%, fixed8
-1.488..+2.028%, product16 -4.276..+2.775%; descriptive same-choice subset GMs
-3.594%, -0.060%, +0.170%. These subsets do not replace all13 primary results.

Later18 has no M128 winner. T1..T512 allchooseM256/N64/C2/F8/epi/S2;
T1024F8epiS3; T2048/T4096N128/F4/reuseS3. Later T1 .081041ms contrasts old18
M128/F8/epi/S3, fixed8M256/F4/epi/S2 and product16M256/F8/epi/S3. The candidate
T1 gaps+14.373%/+14.905% versus later18 cannot be labeled an M128-pruning cost.
The observations establish variation and selection changes, not causal throughput.
Root's final catalog/publication decision remains pending. Source6d253/PR5aa/body6dfa
stays unchanged; all completed proposal/control evidence remains durable.


## Entry 050 — Fixed8 retained as the requested simplification/tuning-cost tradeoff

Root's final decision revises the provisional rejection in entry047 after complete
product16 and later18 control evidence. Retain the clean eight-dictionary M256/C2
× N64/N128 × F4/F8 × epi/reuse product, all explicitS2. This is a simplicity and
measured tuning/benchmark-process-cost tradeoff, NOT a new kernel-speed win.
Preserve fixed8 +1.291% GM latency versus later18 and+3.354% versus original18;
subprocess581.615758s versus later944.747875s is38.437% shorter. Product16 offered
only0.373% lower primary GM versus8 while taking60.136% more benchmark subprocess
time. Its bestS3 subset gaps are≤0.715% outsideT1; fresh18 has noM128 winner.
The actualT1 fixed8/latercontrol+14.373% remains visible and is not an M128-removal
attribution. No run rows or earlier audit bytes are rewritten or spliced.

Published code commitdced675bbb924b2fafbe764e0ff07e2815ec1caf, push3834true0;
source association logs/pr5019-fixed8-publication-source-001.json
SHAe323658fcdaf2e8cfbeca2450155ba93e8e22dc093ec43856c82c3c8c3febb0a
verifies1572 files, exact measured=published2fe/test7292/kernel7e/factory6911 and
post-hook bytes unchanged. No test overlay, CPU/GPU numerical or timing rerun.
The actual fixed8 numerical689/CPU1-eight-transitions/lifecycle16oracles20resources
remains current evidence. Product16's CPU64-pair diagnosticfc98 is labeled separately.

Final proposed body PR_BODY-fixed8-proposed.md
SHA122ccfad915a970c46945b764011714b5d66bbebd48bf955bc3cd1e6faf7e8e7
records the decision, both comparison scopes, unchanged-choice ranges and full
current132 rows;130 table/template/@humansand unchanged. Proof005 binds exact
commit/source and no placeholders. Root owns GH write/readback; none by integration.
Earlier provisional-rejection draftb18 is retained byte-exact in
logs/PR_BODY-fixed8-provisional-rejection-001.md. Canonical body/readback update
is pending at this checkpoint. Last saved remoteclosure remains later18/source6d253;
actual final fixed8 remote restoration will be recorded after its receipt.


Entry050 actual remote publication sync closed:
stage45604/sync40325/fetch14526 alltrue0; completion300fcdfd1fbfec63a71ca65389b61620c30dd3451a4b64d6725622242f77c735
at logs/cu132-recovery0909c-fixed8-publication-sync-001/completion.json,
installer1b72e96de38c3b1e278c63fa8b6a0eb46a1cfdb8fc91d3ff1f374fe31b5ec6a7.
Exact source2fe corresponds to publisheddced675, native22 unchanged7ada, no
benchmark/compilation/numerical rerun. Remote GitHEAD02cf is explicitly separate
from exact published content. Authorized subsequent CPU factory probe53236
completed; finalfetch80219/result pending, not timing evidence.


Entry050 auxiliary factory probe closed as reported by performance:
logs/cu132-recovery0909c-shared-weight-factory-probe-001/completion.json
SHAb7f6e86d1908fe7d9174609811f97b91245f3e568cb1c8eaa73fe60b4931944e,
JSONL880ad9cfd376864abead532daed6b69b9dc1bdcf2a4fcaed67b0c6e7a5445539.
Original53236/fetch80219 true0; first3.179792s, repeats0.008213/0.008374s.
Twelve repeats≈0.099–0.100s is per-rank extrapolation only, not a measured distributed
full-run saving. All6+7 tensor views exactly match, allocations return0 afterrelease;
source2fe/benchmark0f/native22 unchanged. No Mega/distributed/graph execution,
source hoist or benchmark/numerical revalidation. Performance supplied these closed
results; integration did not perform another factory/runtime audit.


Entry050 final PR publication and saved readback closed:
PR5019 remains draft at `dced675bbb924b2fafbe764e0ff07e2815ec1caf`.
Publication receipt logs/pr5019-fixed8-publication.json has SHA
`ab706c3522e49559eebd1f1ea5a9260af6696e2d6cef8ff09b3b3c4770d9edd9`;
full readback logs/pr5019-fixed8-body-readback.json has SHA
`55b6e14fb5f270d96730300f5a425bc36f274ac1ff508cc928650b451391bf43`.
Readback body and canonical PR_BODY.md/current-modern/fixed8-full13 are exactly
`fc2dbfd4f0a0e8bb4029c4e4de0fc5b39dd83806c9b827d77c30f891cfd98f8f`.
Root simplified the current-runtime paragraph after proposed body122cc, without
changing facts. One complete current CUDA13.2 table, both whole-run latency-cost
comparisons, unchanged CUDA13.0 table and template/@humansand are preserved.
This closes the earlier body-pending checkpoint. Measured=published source2fe;
remote exact-content sync300fcdfd and unchanged native22 remain as recorded above.
Remote Git HEAD02cf is separate from the published-content commitdced.

Current-head saved CI logs/pr5019-fixed8-check-runs.json
SHA `7e4876b08d687617e4acf7b59d222c0696f401f35aa0718c0a4768ecf528464e`
shows pre-commit, Build Docs and claude-review success. GPU setup/matrix were
skipped. The summary failure annotation is explicitly "CI skipped — pending
authorization" in logs/pr5019-fixed8-ci-annotations.json, SHA
`f76d4c918a3e34b00e1cad1338f31be3d79ef24c0277b67748d2f86a8b869f3d`.
No labels, comments or CI trigger were sent. Integration read the saved records;
no GitHub request, baseline validator rerun or new runtime audit was performed.

Factory-probe completionb7f6e86d has now been read directly as a saved receipt.
It confirms the reported timings and equal13 tensor views, allocation0 after
all three releases, unchanged source2fe/native22 and closed original53236/fetch80219.
Its one-GPU virtual-rank0/world8 scope excludes NVSHMEM/Mega/graph/full benchmark
execution. The0.099–0.100s per-rank twelve-call estimate is an extrapolation,
not measured EP8 savings or proof of lifetime through Mega execution. It is
negligible beside581.616s benchmark subprocess wall; root did not apply a hoist.
The factory probe adds no new primary timing or numerical-validation claim.

## Entry 051 — future retention range: 8–4096 tokens

User direction, 2026-09-09: exclude 1, 2 and 4 tokens from future performance
optimization retention criteria while keeping them in the PR performance table.

Use the ten power-of-two rows from 8 through 4096 for decision-facing geometric
means, win counts and regression assessments. Keep measuring and publishing
the complete thirteen-row 1–4096 sweep. Full-range descriptive summaries, if
reported, must be labeled separately from the retention-range summary.
Correctness requirements continue to cover every tested size. This policy is
prospective; preserved historical tables and retention decisions are unchanged.
Recorded in CURRENT_STATE.md and README.md. No benchmark or source change was
needed for this policy update.

## Entry 052 — raw-stage ceiling four on fixed8 (rejected)

Resumed 2026-09-09. Existing devbox fi-w4a16-mega-0909c remains hu-pdx-115,
eight B300 GPUs. Managed `/usr/local/bin/h` availability check72686 exited0:
retained source2fe, unchanged22 native objects7ad, and idle GPUs. Receipt:
`logs/cu132-recovery0909c-fixed8-resume-availability-001.json`, SHA
`25cfff54120c5d38af3ae98e06f054b1725d13f68f7241946915e898cb564f67`.

Candidate `candidates/w4a16_raw_ceiling4_fixed8/source.patch`, SHA
`d46062bb9ff0cf7b68e7525b9ca6ae1e95062a3f4b9f2ec18e999a2a9dba4800`,
changes only the fitter's `range(5, 1, -1)` to `range(4, 1, -1)`.
Expected N64 raw5→raw4; N128 already fits raw4. No new runtime dispatch,
knob, role, numerical operation, activation-stage preference or TMEM layout.
This tests a smaller producer window and raw/SF allocation on the current
B3/fixed-S2 design; no occupancy or speed improvement is presumed.

Plan: candidate compiled-resource observations, existing N64 reference-schedule
and long-K partial-tail numerical cases on EP1/EP2, then complete AUTO100
1–4096 against the unchanged saved fixed8 baseline. Retention uses only
8–4096 under entry051. No split or baseline rerun. Separate held BF16 fused
input-staging preparation does not change the raw4 measurement source.
Results and retention remain pending.

Entry052 execution update: corrected candidate-only N64 capture72938/fetch97801
and N128 capture59574/fetch91837 exited0. Original N64 capture56422 failed
artifact lookup because dump settings were applied after the CuTe import;
its compile-only result is preserved and the corrected capture is separate.
Detailed native review in `candidates/w4a16_raw_ceiling4_fixed8/native-review.md`
passes raw4 barrier/index/phase/tail ownership and unchanged data operations.
N64 has REG96/640 threads/local0; N128's5840 instructions and PCs equal the
earlier actual S2/B3/raw4 capture. These are compiled-code observations.

Exact candidate source1032373c is installed locally and remotely. Ordinary
preflight exited0, but the original installer wrapper exited1 because its
native inventory acquired a single zero-byte `flashinfer_jit.log`; all22
previous files were byte-identical. Separate closure34779 records the actual
source/preflight/idle state and new inventorya2bfadf0, without reinstalling or
rerunning preflight. Future checks should record diagnostic log additions or
growth separately from compiled artifacts. The original failure remains intact.
Original numerical PTY90036 now runs EP1 then EP2 (12 rank-tests/30 compiled
observations planned). No numerical or timing pass is claimed by this update.

Separate held follow-ons: FC1 post-scratch release patchd40af01a preserves the
current alpha placement and uses the earlier final-static-subtile peel; the
historical512-thread native captures are not current640-thread validation.
BF16 fused-staging patch2bddff48 introduces one vector-copy/routing kernel for
eligible layouts, retaining the original Torch path otherwise. Its eligibility
includes inner stride1 because singleton contiguous views can have other
strides. Both patches pass source checks only and remain unapplied.

Entry052 EP1 outcome: four tests/ten objects passed in158.132s. Original90036
then exited1 before EP2 on its strict native-inventory check. This second delta
was not diagnostic-only: the FP4 quantization object/library and Ninja logs
changed. The direct numerical launcher omitted the established PATH prefix,
selecting local Ninja1.13 rather than system Ninja1.11. The saved build.ninja
bytes/flags, nvcc13.2 executable and G++13 were unchanged. On the resulting
cache, Ninja1.13 reports no work while Ninja1.11 reports changed commands.
Performance will restore the established PATH in runtime job environments,
verify current generated packs against saved factory-probe hashes, and continue
only the pending EP2 job. Successful EP1 tests will not be rerun. No baseline
performance rerun or compiled-binary equivalence claim is intended.

Entry052 continuation: factory check91682 exited0 in100.911s including the
normal system-Ninja freshness rebuild. All three generated packs match every
saved tensor byte hash (six canonical plus seven split-format views). Closure
d3e77489 records source unchanged and new native inventory2db32756. This
establishes benchmark input consistency, not binary identity or new timing.
Only pending EP2 launched under original12818, with PATH explicitly set in
both the outer command and job environment. EP1 and baseline timing remain
untouched. AUTO is prepared against the saved fixed8 baseline.

Entry052 numerical completion: original EP2 continuation12818 exited0 in
88.431s; both rank validators and the admitted native-generation check passed.
Together with preserved EP1, all12 rank-tests/30 objects passed. Closure92af7fbc,
final fetch50140 and idle67762 completed. No EP1 rerun. Full AUTO13/100 launched
as original87892, `cu132-recovery0909c-raw4-auto13-direct-001`, with the
established PATH inside the job environment and outer command. At19:00:23UTC,
one of thirteen rows was complete without reported errors. Retention remains
pending and uses only8–4096; all13 rows will be reported.

Entry052 final outcome: original AUTO87892 exited0; all13 rows,104 winner/
resource observations,13×8 candidate rankings and1,300 samples completed.
Corrected fetch94098 and idle20823 exited0; closure
`logs/cu132-recovery0909c-raw4-auto13-direct-001/completion.json`, SHA
`e5068b021223aa1d69fc29436a15930b86c6c51ab48a514e143f3e7599d8af2a`.
First fetch72819 failed on two incorrect artifact paths before extraction;
its failure is preserved and the corrected fetch did not repeat the benchmark.

Root rejects raw4 under entry051: over8–4096, GM after/before is
1.0174478298943763 (+1.744783% latency),3/10 wins at32/256/2048, seven regressions
at8/16/64/128/512/1024/4096. Seven selected dictionaries change. Full13 secondary
GM is0.9915585427254822 (−0.844146%),6/13 wins, explicitly excluded from the
retention decision. All13 raw rows, both choices and exact aggregate membership:
[complete comparison](logs/cu132-recovery0909c-fixed8-vs-raw4-independent-comparison-001/README.md),
JSON SHA`a84c461b20f1cf2fb49aba788a2c1f489a05f438f1d6e2db942834ec00300084`.
The direct accepted fixed8 baseline395a current columns were used once without
baseline validators or reruns. Original pure reconstructionf2607478 was consumed
directly; the independent check rederived ratios and medians from its saved
rows/arrays and verified the final closure, without rebuilding a controller.

Benchmark subprocess582.550899s versus retained fixed8 581.615758s. The report
separates subprocess, outer and timing-utility wall scopes. All104 observed
objects areB3/raw4/S2/local0. Same-choiceT16+3.737%,T2048−0.0045%,T4096+4.806%
within the retention range limit causal interpretation; no fixed-tactic
throughput improvement or noise correction is claimed. Native2db32756 remains
exact from the admitted post-factory state throughEP2/AUTO, including its23
entries. Earlier quantizer binary changes remain a specific admitted boundary,
not a blanket permission for compiled-artifact mutations.

Independent numerical audit:
`logs/cu132-recovery0909c-raw4-direct-numerics-independent-001/audit.json`, SHA
`8ffe98f3d0670f70a83706dfa65da13d1db492813242fb6299d59226bd6bede4`.
The original two saved validators pass once each:12 rank-tests/30 objects,
six long-K29/K9 cases at180864B/B3/raw4/S2, both return modes, original
empty/refill, scale/routing and exact3+1 graph replay. The long-K eager fixture
does not imply long-K graph coverage. All original prelaunch-resource records
reconcile to the30 observed objects. EP1 pytest0/wrapper1, untouchedEP1records,
three exact saved6+7 tensor-pack checks and EP2-only continuation are preserved.
No GPU or historical validator was launched by this audit.

The published fixed8/raw5 PR remains atdced675/bodyfc2dbfd4. Performance owns
the authorized restoration tosource2fe and next FC1 post-scratch release trial;
those later completion receipts are separate. Held BF16 staging has since
received narrow capture-miss Torch fallback and final dtype-transition tests:
sourcepatch8b28b65e, test2d4898d0. These are source-checked preparation only,
unapplied and GPU-unexecuted; they are not part of the raw4 measured source.


## Entry 053 — FC1 accumulator release after final scratch read

Raw4 is rejected and the exact published fixed8/raw5 source2fe restored locally
and remotely (completion3e6337dd); native inventory2db is unchanged. The next
independent candidate changes only epilogue1131→943f, patchd40af01a, on the
retained kernel7e. It peels the final static64-token subtile and releases ACC
after its final TMEM scratch read completes, overlapping subsequent GEMM work
with register permutation, BF16 conversion, address calculation and stores.
Alpha-before-wait, two decode WGs, five total WGs, caps, stages and eight tactics
stay unchanged. A constexpr dispatch avoids a runtime last-subtile predicate.

Current candidate-only native N64 and N128 captures completed successfully:
`profiles/fc1-post-scratch-release-raw5-fixed8-m256n64c2-001` (cubin769af972) and
`profiles/fc1-post-scratch-release-raw5-fixed8-m256n128c2-001` (cubin2879478e).
The [detailed native review](profiles/fc1-post-scratch-release-raw5-fixed8-independent-review-001.md),
SHA5b7280b2, accepts both. Final scratch loads and TMEM-load fence precede the
ACC arrival; no later FC1 TMEM read follows release. Zero, partial and full
paths release exactly once; N128 explicitly covers 1–64 versus65–128 rows.
Early alpha remains live across the accumulator wait. REG96/640 threads,
zero stack/local accesses and sixteen MMA remain. N64 gains8 listed SASS rows;
N128 gains232 (3.97%) from static final-subtile specialization, with some
surrounding compiler CFG changes. This is a code-quality pass, not a speedup.

Performance owns installation and the existing EP2 N64/N128 reference-schedule
and long-K wrap selectors, both return modes:16 rank-tests/40 objects. The
T257 skewed fixture routes every row to experts0/1 and covers full/partial
N128 tiles; empty/refill/graph cases remain in the reference selectors. No EP1
or baseline rerun is planned. On numerical success, run all13 AUTO100 rows
against saved fixed8 comparison395a. Retention uses8–4096 only; all13 rows
remain reportable. PR5019 stays draft atdced675 with its current body unchanged.

Actual numerical closure is now complete for installed source
`96c9e674884bdf5fa3ad3ce1f2370a5d052cbfb1d788ff83b327077d4af50a2f`.
Original13857/idle27495/final fetch39995 all closed0. Completion
`logs/cu132-recovery0909c-fc1-post-scratch-release-direct-validation-001/completion.json`,
SHAe3334f7e4e8cc5d54cd4d4a0141cb94c5d52d90ab7547d33ee4a55be3d5db2b8,
records N64 subprocess87.344530s and N12892.397218s (outer181.975451s), with
native2db unchanged in the original closure. Independent saved audit
`logs/cu132-recovery0909c-fc1-post-scratch-release-numerics-independent-001/audit.json`,
SHA47a908d87921d1f4ba75a52246bf5acc2f4b60fd90a66b6148aad294d4855a0c,
invoked each original numerical reader once and reconciled all original
PRELAUNCH resource records. Exact16 rank-tests/40 objects pass, with B3/S2
and local0 throughout, raw5×36/raw4×4. Eight long-K29/K9 eager observations
use N64 raw5=199424 B ×4 and N128 raw4=230016 B ×4. The original reference
selectors retain both returns, scale/routing, partial H/I, empty/refill and
exact3+1 graph replay separately; long-K graph reuse is not claimed. No
baseline/native validator, numerical GPU job or historical controller was
rerun by the audit.

Full AUTO13/100 launched under original72090,
`cu132-recovery0909c-fc1-post-scratch-release-auto13-direct-001`. The prepared
original direct readerfb807270 uses fixed8 comparison395a directly and the
ten-row retention policy. The independent saved audit did not hold the launch.

**Interrupted by devbox loss; no performance decision.** Original72090 exited1,
managed h reported137, and the remote completion marker is absent. The last
saved progress contains6/13 rows (through32 tokens) at299.171417s. Subsequent
ordinary progress retrieval reported0909c absent; bounded managed inventory
79369 completed0 and found no ziangli/c2 devboxes. Absence receipt
`logs/cu132-recovery0909c-fc1-auto-box-absence-inventory-001.json` has SHA
cf63a0ad2e1a7e161027cbf2960c63eb7475fed47d862460d8919e122135f3b6.

Interruption receipt
`logs/cu132-recovery0909c-fc1-post-scratch-release-direct-auto13-interrupted-001.json`,
SHA73faac2f6a6fb32894524338972a7145bcfa8f436ada73985ed23b58f8666f5c,
preserves and supersedes the erroneous outer rc0 receipt894ba205. The helper
caught CalledProcessError only; absent execution markers raised RuntimeError,
so its finally block wrote the initialized zero status. Original PTY1/h137 and
missing completion take precedence. No final native/source/idle closure exists,
and no partial timing table, aggregate or FC1 retention decision is produced.
The already completed native review and numerical16/40/audit47a908d8 remain
separate successful evidence; they are not invalidated or rerun by this loss.

Performance requested fi-w4a16-mega-0909d under original17420, c2/ziangli,
eight B300, bare and no explicit size, with nvcr.io/nvidia/pytorch:26.05-py3.
Root's live catalog check is saved at `logs/cu132-recovery0909d-image-selection.json`,
SHA68f1562f70706a44556f33bc4c9a7024c0e5884c7ea8dd5032faae0dc2952ab6:
26.05 is the newest release providing CUDA13.2; actual replacement provisioning
and runtime validation are pending. Root selected recovery of published2fe,
ONE fresh complete fixed8 AUTO control on the new node, then an FC1 retry.
The new control is reused thereafter, without row replacement or repeated
per-trial baseline runs. Candidate96c9 remains local and held. No broad
numerical rerun, extra oldbox probe or new controller framework is requested.
PR5019 remains draftdced675 with its body unchanged.

**Recovery update: same physical GPUs; direct395a reused.** Replacement0909d
published-fixed8 setup33492 completed0 (77.332754s). The saved environment
receipt `logs/cu132-recovery0909d-same-gpu-environment-match-001.json`, SHA
b7d5a8b5d7d94d9677df2d0e8ae4d1fa495f486d06bd4fee0131ba6c98240b09,
confirms the same hu-pdx-115 GPU UUIDs and loaded stack. Preflight224058fa
matches the preceding FC1 preflight except process address maps; environment
comparison also excludes process timestamps and the expected original16 versus
current8 setup catalog count. Exact source/catalog identity is separately bound.
Factory68302/fetch64893 closed successfully; all three calls match saved six
canonical plus seven split-format tensors. Completion
`logs/cu132-recovery0909d-fixed8-factory-check-001/completion.json`, SHA
70511e7fe49c147580931e6e300187001c115a99a465eb70a2568500e61e45f3,
records12 fresh native entries3ef1f134. It does not claim that the previous
container's23 native files were restored. Root therefore superseded the
provisional new-control plan above: no fresh baseline is run, and the complete
saved fixed8 comparison395a remains the timing baseline.

Exact FC1 install28623 completed0 in2.033346s. Install completion
`logs/cu132-recovery0909d-fc1-install-001/completion.json`, SHA
a9fedf60282b3d19f21fde38586f6e5f42469a519e8e57f527c9ea2714b78004,
binds source96c9, receipt e4a8a270 and native3ef1f134. Full13 AUTO100 retry67292
launched as `cu132-recovery0909d-fc1-post-scratch-release-auto13-direct-001`,
direct drivere2999cdc and original pure reconstruction8753b478. Historical
numerical completione333/audit47a9 is reused only as code-validation evidence;
no broad numerical, baseline or saved-validator rerun accompanies recovery.
The current successor records first-build native additions and requires all
preexisting non-diagnostic entries to remain exact. Current final source/native/
idle closure and the complete retry result remain pending. The interrupted
0909c arm remains intact and is not merged with this new whole run.

The first0909d attempt001 then stopped during worker import, before compilation
or any timing row, because unchanged transport dependency
`candidates/cuda13_cross_version/capture_stack_benchmark.py` had not been copied.
Its saved `execution.json` has SHAb6291035fd388bf59c3d4d779108c8f9aa22cd935f84346426f59fb79d8e9496,
process1 and9.345008s; native-build delta is empty and native3ef remains unchanged.
Final fetch15384 completed; original failed files and traceback are retained.
Performance staged that helper under16971 and launched fresh002 under83972,
`cu132-recovery0909d-fc1-post-scratch-release-auto13-direct-002`. Its direct
driver is97228b5a7b5aa81466f3dd1f9f68e08dbf1fb2610f0beb383ae1655cfc7dc63a;
the ratio-free original pure reader iscf8b54941e107bb9af4f3a880064b73197568cd978b3d55ce9bfa60a71f88eb8.
Only002 is the candidate timing arm. Source96c9, preflight, metric and
baseline395a stay unchanged; no kernel source change or numerical rerun
accompanies this missing-file correction.

**Completed002: retain FC1 under the ten-row policy.** Original83972, canonical
idle76713 and full fetch26573 all closed0. Completion
`logs/cu132-recovery0909d-fc1-post-scratch-release-auto13-direct-002/completion.json`,
SHA12b5814799a8866b6dc93d53339495199d407cd905988985f46a81d6b72bd5ba,
binds unchanged source96c9 and final native5ee38836. Original pure reconstruction
`logs/cu132-recovery0909d-fc1-direct-auto-reconstruction-002/reconstruction.json`,
SHAa22229795c2026d01949eab4b7f1f64724fea279f7b3897254f2ea162c697182,
passed all13 rows/104 winners/resources/13×8 rankings/1,300 samples; reconstructed
result SHA3ecfff3454a78d7c4e88c01a852ed841b2b873338286846aa83b2668a90cf475.
The one independent arithmetic check consumes that result and the accepted
fixed8 current columns directly, with no original/baseline/native validator
rerun. All13 sample medians, eight rank configurations/winners per row and
ten-row aggregation reconcile. Its [full before/after table](logs/cu132-recovery0909d-fixed8-vs-fc1-independent-comparison-002/README.md)
is paired with comparison JSON SHAca224f0523a2d410992c05ccbbf54f4b323a358b3ae2a31f60803b6b0154f27a.

Over8–4096, after/before GM is0.9890047647595082, or1.099524% lower latency,
with6/10 wins (8,16,32,64,1024,4096). Four regressions remain:128 +0.220%,
256 +1.628%,512 +2.163%,2048 +0.034%. Root retains this general FC1 overlap
change after the original checks passed, without using the excluded1/2/4 gains.
The full13 secondary GM is0.9717398940734807, or2.826011% lower,9/13 wins.
Only4,64,2048 changed tactic; eight of ten retention rows keep the same tactic,
including regressions at128/256/512. This is a sequential whole-AUTO comparison,
not an isolated fixed-tactic causal throughput measurement.

All104 actual objects areB3/S2/local0, raw5×88/raw4×16. Accepted original native
checks record12→23 entries through11 first-build additions, with no changed
preexisting non-diagnostic entry. Same-GPU/stack matchb7d5 and exact pack7051
support the reused395a baseline; prior native binary identity is not claimed.
Benchmark subprocess616.903775s versus581.615758s, outer620.238064s and timing
utility5.984077s remain separate from per-shape latency. Numerical16/40/audit47a9
and detailed native review5b7280b2 are the already completed source96c9 evidence.
Old0909c interruption and0909d001 missing-helper failure remain intact, with
no row replacement or merged samples. Root owns commit/push/PR publication;
the canonical body remains unchanged by this audit.

Later source-only note: [single-accumulator/three-decoded-stage audit](candidates/w4a16_single_acc_three_decoded_audit.md).
It is held and unexecuted, with no patch or queue change; FC1, staging and
group256 retain their selected order.

**FC1 publication closed.** Commit `1aa0cccbfd52a9a47208c9885d6f1e6985f844f4` is pushed and
verified as draft PR5019 head. The commit changes only the epilogue fromdced;
its Git object hash943f matches the measured96c9 source snapshot. Full pre-commit
passes, including mypy/Ruff/format. Root edited and read back exact body
46ab704fa7ba3cda7de0b5d29de1ec2fba8ac62a4356874cee1689d05a94f7df.
Receipt `logs/pr5019-fc1-publication-001.json` SHA9ffb7b31c4409bbf5cdb7411b0a0db1ff1225bf5ca45913d3273fc38ce2c4d77
and snapshot `logs/pr5019-fc1-post-publication.json` confirm head/draft/body.
Canonical PR_BODY.md/current-modern/fc1-release-full13 match; oldfc2 body is
preserved at logs/pr5019-body-before-fc1-release-001.md. Table audit verifies
all13 current rows/choices/split ratios; CUDA13.0 table remains byte-identical
(925 bytes, SHA7315a98ee6338f682cf15fb7daf9f3dc2f56ca32da281352712f872a8a41d76a),
as do fallback commands and the checklist. The source-checked standalone FC1
reproduction matches all effective N64/N128×return F4/S2 arguments, including
long-K skewed routing and normalize_fc1=True; it was not separately GPU-run.
Argument proof9bd9be2f remains a source-only check. No remote Git HEAD is
claimed from source-content equivalence. Performance owns the next fused-BF16
staging trial, which reuses accepted FC1 ca224 as its direct timing baseline.

Final published-body/table verification is saved at
`logs/pr5019-fc1-published-table-audit-001.json`, SHA
9e498472900a08d591ff0e1265b1c6e07ca369af77a88940a199844c45a40c38.
All three canonical files match actual readback46ab; all13 current medians/choices
and unchanged split values/ratios recheck againstca224. The925-byte CUDA13.0
table, fallback commands and checklist remain identical after root's readability
edit. No body/GH/source mutation accompanied that final check.

## Entry 054 — fused BF16 staging retained; code published

Root retained the completed staging run and pushed commit
`ca03a947ccdfd0969c58f2a4a4423812daa272d8`. Measured source is
`a7470e52eabc9a3952271fce42d40459d9db396f54ceb14a7c0d79be043fbcf9`.
Over the ten retention points8–4096, latency GM is **3.363447% lower** than
accepted FC1 ca224, with **9/10 wins**; the only regression is1024 (+1.0074%).
All13 rows remain in the [complete before/after table](logs/cu132-recovery0909d-fc1-vs-bf16-staging-independent-comparison-001/README.md).
Comparison SHA9cefe6b509d43a08e31970f9bb5886af6f524d6bf6729b87ee7559cca2a1d15d
uses ca224 current columns directly. Full13 secondary GM is2.864297% lower,
11/13 wins; the1/2/4 rows do not determine retention. Tactics changed at
1/2/8/128/2048, leaving seven of ten retention choices unchanged. Sequential
AUTO variation is not a fixed-tactic causal measurement.

Original AUTO82468, idle3631 and finalfetch55843 all closed0. Completionb828bfe1,
original reconstruction0d621b02 and result244f55b1 preserve13 medians,104 Mega
winners/resources,13×8 hot rankings and1,300 cold-L2 CUPTI samples. The direct
arithmetic check recomputes all sample medians and ratios without rerunning any
original/baseline/native validator. Every Mega object isB3/S2/local0,
raw5×88/raw4×16. Separate staging observations are104 total:87 fused nonempty,
17 empty Torch fallback and all80 retention observations fused. Eight rank-local
staging callables have18 registers,128 threads,shared0/local0. The23-entry native
inventory5ee remains unchanged. Benchmark subprocess599.645277633s versus
FC1616.903775103s, outer601.479226250s and timer5.971667201s remain separate.

Current validation56289/idle11073/fetch85370 closed0: nine copy/graph GPU cases
plus4 N64 EP2 rank-tests/16 Mega objects, completion398af0f0 and independent
numerical audite78a3ea6. The nine tests cover exact bits and both ID dtypes,
H7168 vector copies, dynamic n/capacity, empty/refill, strided singleton fallback,
two graphs and int64 warmup→int32 capture→later eager compile→original replay.
All current Mega observations areB3/raw5/S2/local0. No new long-K matrix or
inherited FC1/B3/all-eight lifecycle rerun is claimed.

Measured kernel d7dde1c9 and backend cb11e7d1 are byte-identical at publication.
Required lint cleanup adds explicit default zip(strict=False) in two host calls
(c64f→e066) and12 test calls; public test e12efc44 relocates measured69d3 with
header/docstring/formatting changes. The saved
[source association](logs/pr5019-bf16-staging-publication-source-association-001.json)
proves normalized AST equality. Full published source is not claimed identical
to measureda747, and these default-only/publication edits were not GPU-rerun.
PR body edit/readback is complete: draft headca03, exact body
fba7bee4d0b85693daa0640241dce1ec95ae6a404851e21bc0606bcf58c7e10a.
Receipt logs/pr5019-bf16-staging-publication-001.json SHAd3d98d82fa20a31e68ecd399ec9b054e589f76ee87ad14bcf9e80e99e5628f87
and saved post-publication snapshot verify the result. Canonical PR_BODY.md,
current-modern and bf16-staging-full13 match; old FC1 body46ab is archived.
Root independently confirms the925-byte CUDA13.0 table remains unchanged;
only spacing changed after the proposed table/source proof.

Next selected direction is the held static-rounds stager on the published
staging base, followed by group256 as root selects. The current captured SASS
has a seven-round runtime vector-copy loop. Held patchbaaef60b makes full rounds
constexpr and predicates only a remainder; source review found no indexing or
routing/graph contract issue. Static code size/register liveness remain actual
codegen risks. No static-rounds execution result is claimed here.


## Entry 055 — static BF16 staging rounds, initial compiler failure

Original validation79277 on source1628/kernel a262 ended1. The saved original
inspection log `logs/cu132-recovery0909d-bf16-static-rounds-validation-failure-inspect-001.log`
(SHA1ce099015636c7acaac3b63cb7bd1628aa1b9d8de2b3f1aca9bfb0542a550f81) reports4 H7168/H7200 passes then1 failure in H288/id_dtype0:
CuTe TYPE_UNSTABLE_JOIN at staging_kernel.py:73, `chunk` is None on the zero-trip
constexpr-loop path and Int32 inside the dynamic tail. Pytest stopped after
1 failed/4 passed; subprocess12.721130s. This is a compile-time binding error,
not a numerical mismatch. No static-rounds validation completion or AUTO result
is claimed. Initial a262/baaef candidate and failure remain preserved.
Root authorizes a narrow tail_chunk/tail_values rename and a fresh eleven-test
retry; no tolerance, oracle, Mega cohort or benchmark change. Original source
indexing review missed this CuTe AST join constraint; the retry must establish
compilation and exact outputs on the original fixtures. Retained staging9cefe
and publishedca03/bodyfba7 remain the completed result.


**Corrected retry completed; AUTO active.** Sourcea80c824e5eff97218df7ee73398cea4aca6523945bf8e0e2868e54c64ed1ff42
uses kernel8daaec34, with only distinct tail_chunk/tail_values and formatting
relative to faileda262. Original27963, idle51450 and fetch30580 all closed0;
completion5a1e966786865afc4af3e03ceb5f934ab8a6a47c212e51b18e944148dff192a3
records all11 staging tests passed,0 Mega/reference objects. Pytest11.33s,
JUnit11.319s, subprocess12.901015s. The H7168/H7200 and H288 cases cover full,
full+partial and zero-full-round paths; graph/cache/fallback cases remain exact.
The independent saved audit
`logs/cu132-recovery0909d-bf16-static-rounds-retry1-numerics-independent-001/audit.json`
SHA20e71bcc2e9183c9e713dc0976cec027ce5c59e16dd97258eb36ef147ed0d354
checks only original completed files/counts and preserves first-attempt failure.
No original/native/baseline validator rerun or new GPU cohort. Same-callable
H7168/int32 resource query reports30 registers/128 threads/shared0/local0,
compared with retained loop18 registers; root owns detailed saved native review.
All23 original native entries5ee remain unchanged.

Original AUTO98048 is now active as
`cu132-recovery0909d-bf16-static-rounds-retry1-auto13-direct-001` on sourcea80c.
Prepared readerf854ea50 preserves the direct original result API. Its eventual
complete comparison uses retained staging9cefe current columns (initiala747),
8–4096 primary and all13 reported. This is one whole-run baseline, not a second
independent comparison arm; no partial timing result or retention verdict yet.


**Completed AUTO and rejection.**

Corrected static sourcea80c/kernel8daa completed full AUTO98048, idle52745 and
fetch21384 with exit0. Original proof8ebca27a/result57468614 and completionb70a3c6c
pass all13 rows/104 Mega winners/resources/13×8 rankings/1,300 samples. The
[complete independent before/after table](logs/cu132-recovery0909d-bf16-staging-vs-static-rounds-independent-comparison-001/README.md)
and comparison SHA5d26706174921973be74593baf85c2fa86354b37a5b9c8dbcc82905f438242d5
consume the completed original result and retained staging9ce current columns
directly, without original/baseline/native validator reruns.

Root **rejects static rounds**:8–4096 latency GM is1.742299% higher,4/10 wins.
Regressions: T8 +12.112%; T16 +1.927%; T32 +10.963%; T64 +0.421%; T1024 +0.308%; T4096 +2.353%. Full13 secondary GM is0.858369% higher,7/13 wins;1/2/4 do
not determine retention. Tactics change1/4/16/128/1024; seven of ten retention
rows retain their dictionary. No fixed-tactic causal attribution is claimed.
Benchmark subprocess599.043463545s versus retained599.645277633s; timer utility
5.821111927s. The23-entry native inventory5ee remains unchanged. Mega objects
remain B3/S2/local0,raw5×88/raw4×16; separate staging87 fused/17 empty and all80
retention cases fused. Actual static stage resources are30 registers/128 threads,
shared0/local0 versus18 registers in the retained loop version.

The corrected eleven-test validation passed (audit20e71bcc, completion5a1e9667),
with zero new Mega/reference cohort. First original79277/a262 remains a separate
compile failure:4 passes then H288 TYPE_UNSTABLE_JOIN; the tail-local rename
fixed that CuTe binding. Root's codegen review confirms the static copy backedge
is gone but seven LDG/STG pairs remain; native code shape is separate from E2E
performance. Prefetch4 is held and unmeasured.

Performance is authorized to restore published stagingd891/kernel d7dd and
proceed with the independent group256 main-kernel trial. No completed restore
receipt is claimed yet. Published PRheadca03/bodyfba7 and current performance
table remain unchanged; staging9ce remains the next timing baseline.


## Entry 056 — group_hint 256

Selected source `90a1bafce650ce6808b7f5c1d1e0be27ee29a74e2e6b1935bfe70ececc6f9437`
changes only the W4A16 factory group_hint 512→256 on the published staging base.
Install 35206 passed. Localhost numerical retry 42662, idle 86541 and fetch
14891 all closed with exit 0; completion SHA is
`14b0486f033f640d9e18832a8a1037dfd02438c1a96ab395d73dfa79e24bdd87`.
The [saved numerical audit](logs/cu132-recovery0909d-group256-numerics-independent-001/README.md)
(SHA `4516bc40f6425a97ce0c2cccb601c41e5bd9e8995b6da7adee7db9125376c04c`)
reconciles 8 original case passes, 8 compiled objects and 8 resource records.
Every object is B3/raw5/S2/local0. The subprocess took 51.534504540 seconds;
the original closure reports all 23 native entries unchanged.

The E8 EP2 fixture runs N128/N64 × group_hint 512/256, F4/epi only. Actual
routed IDs give 260 rows per expert: source-derived N128 grouping changes
3+1→2+2 and N64 pairs→singles, including four live tail rows per expert.
This is not scheduler execution telemetry. The unchanged public oracle passed;
no new graph/lifecycle, return-mode or all-catalog cohort was run. Original
49706 remains a separate unresolved-hostname rendezvous failure, stopped with
return code −15 and zero case/resource records.

**Full AUTO completed; group256 rejected.** Original 51022, idle 16878 and
fetch 41094 all closed with exit 0. Canonical completion
`2930cb0ad5434c33040b726132d0a4edb5e82ba24d80a4c163b3918c122ae646`,
original reconstruction `b08eaeb8` and result `0d129d8f` pass all 13 rows,
104 winners/resources, 13×8 secondary rankings and 1,300 primary samples.
The [complete independent table](logs/cu132-recovery0909d-staging-vs-group256-independent-comparison-001/README.md)
uses retained staging 9ce current columns directly; comparison SHA is
`9d1044f56a478e6c3b7a23f670a6018a5e6700de007529b4c1864179ca527d3b`.

Over 8–4096, latency GM is **4.222221% higher**, with **0/10 wins**. The largest
regressions are T32 +11.415% and T16 +10.477%. Full-13 secondary GM is 1.998146%
higher; only the excluded 1/2/4 rows improve. Every dictionary changes group_hint.
N/flag/return selectors change at 1/2/16/256/2048/4096; six of ten retention rows
keep those selectors. Sequential AUTO variation does not isolate a group-only
or fixed-tactic effect. No baseline, original or native validator was repeated.

Actual Mega objects are B3/S2/local0, raw5×80/raw4×24. Separate staging records
remain 87 fused/17 empty, with all 80 retention records fused. The original
checks report all 23 native entries unchanged. Benchmark subprocess cost is
601.491638550 seconds versus retained 599.645277633; outer 603.554998041 and
timer utility 5.894709638 seconds are reported separately.

Performance is restoring published staging d891/group512. The next selected
candidate is the MMA decoded-readiness probe, whose held source review found
no state/phase blocker; actual codegen and timing remain unmeasured. PR head
ca03/body fba7 and its current performance table remain unchanged. No group256
PR body was created or published.


## Entry 057 — MMA decoded-readiness probe rejected

The selected probe changes only the retained Mega kernel's decoded-readiness
wait sequence: source `66ccf5c4017d4de24e0b1dee56fdf46191cd2a1d70d1955f999fcfeb70e88601`,
kernel 3238 on published staging d891/group512. Candidate N64/N128 native
captures retain 96 registers, zero local memory and the existing stage counts.
The matched saved controls use kernel7e plus FC1 epilogue943f, not older S3
or four-warpgroup captures; see
[capture identities](candidates/w4a16_mma_decoded_readiness_probe/SAVED_NATIVE_BASELINES.md).

Numerical original 49844, idle 69515 and fetch 62608 closed with exit 0. Completion
`11717cc1fc83321bb04c16db874b7d7871dcd9a2f2678e22081ffe6ab79e9e9a`
and the [saved numerical audit](logs/cu132-recovery0909d-mma-decoded-readiness-probe-numerics-independent-001/README.md)
(SHA `4c50f4c41c22eb52753498b23f1ddb564f5a8cd51dbfb24dd4fd7f863f5bfb19`)
reconcile 16 successful rank-test calls and 40 public configs, compiled objects
and matching prelaunch resources. Both N64/N128 EP2 jobs preserve both-return
reference/scale/routing/graph coverage and eight long-K rank cases at H7200,
I2112,T257,K29/K9. All objects are B3/S2/local0/96regs, raw5×36/raw4×4.
N64 took 91.159830472 seconds; N128 83.996616564. Original closure reports all 23
native entries unchanged. The audit repeats no original, native or baseline validator.

Actual measured arm is AUTO003/original 98105,
`cu132-recovery0909d-mma-decoded-readiness-probe-auto13-direct-003`, using fresh
actual preflight 309b, unchanged numerical receipt and direct retained staging
9ce current rows. AUTO001/96799 stopped before the benchmark because inherited
preflight pinned kernel7e. AUTO002/7525 also stopped before the benchmark on
an added empty diagnostic flashinfer_jit.log; its original failure is retained.
The established diagnostic-log-only policy now applies at the initial boundary
as well, while rejecting non-log changes. These attempts produced no benchmark
rows.

**Full AUTO closed; readiness probe rejected.** Original 98105, idle 1684 and
fetch 57020 all closed with exit 0. Completion
`ce9bc713298ee7865e6265e5e82e4fb06be79564421c67f21a640142b120b910`,
original proof2dca1174 and result311e1c57 provide the complete run. The
[independent full comparison](logs/cu132-recovery0909d-staging-vs-mma-readiness-independent-comparison-001/README.md)
(SHA `97df413d429aeae5ec572f9f57fdaeb33ae38964af29f2ebbeeefdfc4f8250b5`)
reproduces all 13 medians from 1,300 samples and reconciles 104 winner/resource
records, 13×8 candidate rankings and 87 fused/17 empty staging observations;
all 80 retention observations are fused.

Over 8–4096, latency GM is **0.65894675% higher**, with **4/10 wins**.
The wins are T16/T128/T512/T1024. Regressions are T8 +5.633%, T32 +7.819%,
T64 +0.850%, T256 +1.452%, T2048 +4.563% and T4096 +1.694%.
Full13 secondary GM is 0.13474759% lower with 6/13 wins; excluded 1/2/4 do not
change the decision. Seven full-run dictionaries change; six rows keep their
tactic, with both improvements and regressions, so these whole AUTO runs do
not isolate a fixed-tactic effect. Every Mega object remains B3/S2/local0,
raw5×88/raw4×16.

Benchmark subprocess 598.367583816 seconds versus retained 599.645277633;
outer 600.420715084 and timer utility 6.407088273 seconds are separate. Original
saved checks report existing non-diagnostic native entries unchanged; the
initial empty flashinfer_jit.log addition is recorded, not treated as binary
identity failure. No original, baseline or native validator was rerun.

Root authorized restoration of published staging d891/kernel7e and the next
shared NVFP4 prepared-weight layout trial. No readiness-probe publication or
PR body change is made; retained staging ca03/bodyfba7 remains current.


The separate shared W4A4/W4A16 prepared-layout candidate is next under
[candidates/w4a16_shared_nvfp4_weight_layout](candidates/w4a16_shared_nvfp4_weight_layout).
Weight-side 30 selected CPU cases passed; frontend/kernel and four prospective
GPU cases passed source review only. Root selected four focused GPU cases plus
the existing 16/40 numerical scope and candidate native captures; those results
are not claimed here. Its prepared tensor/scale contract is an
independent change and is not part of the current MMA probe measurement.
Published PR5019 stays draft at ca03/body fba7 with the retained staging table.


## Entry 058 — shared NVFP4 prepared-weight layout

Selected source `af938d808556e72925933208f0844cd92f44dff5cc7f407b050897c5660b2e9e`
changes W4A16 preparation and decode views to W4A4's actual prepared contract:
gate16/up16 FC1 ordering, K-major FP4-x2 `[E,K/2,N]` transpose views and native
per-expert E4M3 `[E,P]` scales, with equivalent uint8 aliases. FP32 expert alphas
remain separate metadata; W4A4's unsupported-global rejection is unchanged.
Canonical unquantized weights now reach the existing quantizer through a 2D
view before reshaping and per-expert SF padding. The candidate also includes
the shared single-copy gate16 helper, contract tests and architecture text.
The rejected MMA readiness probe is not part of this source.

**First current-source contract evidence is complete.** Original 19133 and
fetch 26163 closed with exit 0; completion
`e7281fff0c51be8b0161c6050f9d67753f5e44d1f5c9aaa1fbedaa20236333f8`.
The [saved contract audit](logs/cu132-recovery0909d-shared-layout-contracts-independent-001/README.md)
(SHA `0070f5ef6f79227dec29e57150cc52e732dcc57ee02303860391c9358a9a60ea`)
reconciles **129 public host-contract tests and 4 GPU tests**, all passing with
zero errors or skips. Both FP4/E4M3-first and uint8-first cases switch backing
pointers on the same compiled frontend and pass the unchanged non-unit-alpha
numerical oracle plus stable/changed-input graph replay. Real BF16 and FP32
preparation for 3 experts, H288/I448 matches W4A4 packed/SF bytes exactly.
These executed CUDA checks resolve the corresponding gaps in the earlier
selected 30-case CPU proof, whose quantizer/swizzler boundary was mocked.

Twelve actual static/dynamic CuTe descriptors preserve leading axis1. FP4-x2
Torch packed K expands to logical K in CuTe; uint8 aliases remain packed until
the kernel's explicit recast. This covers partial H288 and benchmark H7168
weight descriptors plus `[E,P]` SF. Descriptor inspection launched no kernel.
Source before/after is exact and original native inventory pins remain c6da.
Host pytest took 4.61s (subprocess 11.070096747s); GPU pytest 26.88s
(subprocess 33.553500216s); descriptor inspection 6.177780046s.

**The separate reference suite is now complete.** Original 14851, canonical
idle 71224 and fetch 30833/76463 closed with exit 0. Completion
`f12ede0b8c99ba94d21b6d217bf69d9b294c0330613665f4cf619a50d9b02b80`
and [saved reference audit](logs/cu132-recovery0909d-shared-layout-numerics-independent-001/README.md)
(SHA `e5ac00ff6de671b2ccb98600d9606b9815ecf65f326b3b214aaa7b2d3684dc9a`)
reconcile 18 successful rank-test calls and 48 public configs, compiled objects
and matching resources. N64/N128 EP2 both-return reference and long-K cases
supply 16/40; manual M128/N64/C1 EP1 both-return references supply 2/8 with actual
one-CTA MMA. All objects are B3/S2/local0/96regs, raw5×44/raw4×4; eight long-K
rank cases use H7200/I2112/T257,K29/K9. Manual coverage adds no long-K case.
Subprocesses took 83.509990331s (N64 EP2), 94.185258070s (N128 EP2) and
51.339660583s (manual EP1). These counts remain separate from 129 host and 4 GPU
contract tests. No original, native or baseline validator was rerun.

Matched candidate native captures under 72667/97852 retain REG96,
STACK0/LOCAL0, stage allocations, memory/synchronization opcode counts and 16
UTCHMMA.2CTA instructions. Root's saved native-counts.json reports listed
instructions 5536→5504 at N64 and 6072→6032 at N128; differing NOP counts give
36 fewer non-NOP instructions in each. This is code-size/resource evidence,
not a latency measurement.

**Full AUTO is complete.** Original 2466, idle 45110 and fetch 18425 closed with exit 0;
completion `8219bfc4868d96cf75d95a1813fb20b741541936dea01af1f43d7a3024bfb2c5`.
Original proof4bd4351a/result7f86f38e and the
[independent complete comparison](logs/cu132-recovery0909d-staging-vs-shared-layout-independent-comparison-001/README.md)
(SHA `1a763323d8f36f670ac2213f3580236a884a0fb033fe799ce21cfb31ec4575da`)
reconcile 13 rows, 104 winner/config/resource records, 13×8 rankings and 1,300
primary samples on source af938. All Mega objects are B3/S2/local0 with
raw5×88/raw4×16. Separate staging records remain 87 fused/17 empty and all 80
retention observations fused. No original, baseline or native validator was
rerun; the retained staging9ce current rows were consumed directly.

Root selects retention for the user-requested shared interface and simpler
maintenance, **not an overall performance improvement**. Over 8–4096, latency
GM is 0.173116856% higher with 5/10 wins. Every row from 64 through 1024 improves;
regressions are T8 +9.290%, T16 +2.553%, T32 +0.797%, T2048 +2.774% and
T4096 +2.018%. Full13 secondary GM is 0.152697543% lower with 7/13 wins and does
not drive the decision. Six full-run choices change at 1/2/16/32/128/256.
Seven rows keep the same dictionary, including the T8 regression and both large
rows; sequential AUTO variation does not establish a fixed-tactic cause.

Benchmark subprocess 596.187686985s versus retained 599.645277633s; outer
599.651496083s and timer utility 6.022677812s are separate. The complete af938
run and its 1a763323 current columns become the next trial's baseline; no row
replacement or minimum selection is used.

**Publication is complete.** [GitHub edit/readback receipt](logs/pr5019-shared-layout-publication-001.json)
confirms draft head `056ce0d090d425ee09171e47f6faea61c76c9551` and exact body
`fd2fc607a50406fff33fbfc5ff503fe4402ffca8412e11dbeed9a91e0a436e54`.
The canonical body and current-modern copy match. The
[source association](logs/pr5019-shared-layout-publication-source-association-001.json)
verifies all 1,575 measured source files against committed Git blobs; measured
source af938 is the published source, without a test-only overlay. CUDA 13.0's
925-byte table remains unchanged and historical; it does not validate this
shared layout. Root performed the GitHub publication; this audit updated local
evidence documents only.

## Entry 059 — ACC1 / decoded3 rejected

The selected source `e8996291e4ad0aaa4acde731b1d128f6844e371282799c5f50a9ee70e3106c6d`
changes only the W4A16 kernel and epilogue on published shared-layout source
af938/commit056ce. N128 reserves one physical accumulator stage to fit three
decoded stages; N64 retains two accumulators and three decoded stages. Kernel,
pipeline and epilogue stage counts agree, without overlapping-accumulator
mode. Five warpgroups, two decode groups, the shared weight layout, B3/B2 fitter,
FC1 release and fused BF16 staging remain in place. Root's
[saved native review](candidates/cuda132_recovery_0909d/single_acc_three_decoded/NATIVE_REVIEW.md)
passes the N64/N128 M256 and manual M128/N128 captures; no native control or
validator was repeated by the independent audit.

**Numerical validation is complete.** The combined completion
`c653b7e495f098ccdd4f3c2f9f339fbe08ab1c94cffb41f8997cacd22978467d`
and [saved audit](logs/cu132-recovery0909d-single-acc-numerics-independent-001/README.md)
(SHA `c83655d4336224a4c0db6c2c230afab37f5383d7273cca1977bab329376f608b`)
reconcile 13 rank tests, 40 public configs, 40 compiled objects and 40 matching
prelaunch resources. N128 EP2 both-return references plus long-K cases provide
8/20; unchanged N64 EP2 both-return references provide 4/16; manual
M128/N128/C2 EP1 epi-return reference provides 1/4 with actual one-CTA MMA.
Four long-K rank observations retain H7200/I2112/T257 and K29/K9. Original
partial-shape, scale/routing, empty/refill and graph oracles are unchanged.

Actual resources are ACC1×24 / ACC2×16, decoded3×40, raw5×36 / raw4×4,
S2/local0/REG96 throughout. Activation depth is **B3×36 and B2×4**: the manual
M128/N128 case uses the existing two-stage fallback. Physical, pipeline and
epilogue counts match each geometry; no blanket B3 claim is made. Successful
subprocess times are 94.704587964s (N128 EP2), 70.255589574s (N64 EP2), and
40.692981622s (manual EP1). Native inventory remains c6da in the original closure.

Original 98210 completed both EP2 jobs, then its manual EP1 attempt failed
before any public config or compiled object because env:// rendezvous lacked
MASTER_ADDR/MASTER_PORT. That failure and outer status remain preserved; the
outer is not relabeled successful. Only the manual case was retried under
83226 with explicit localhost and passed. Original fetch27040, manual fetch7116,
canonical idle32918 and idle fetch55519 are closed. The successful original
validators ran once per job in their original processes; the saved audit runs
no original, native or baseline validator. Prior shared-layout 129 host/4 GPU
contract evidence is inherited and is not part of the new 13/40 count.

**Full AUTO is complete; ACC1 is rejected.** Original63593, idle53232 and
fetch15523/21034 are closed; canonical completion
`3093d31103906ffb616ab9843d001d56268de4b211e422a423ad145eab2b6c01`
binds the complete `cu132-recovery0909d-single-acc-auto13-direct-001` run.
Original proofed612586/resultafe919e3 and the
[independent full comparison](logs/cu132-recovery0909d-shared-layout-vs-single-acc-independent-comparison-001/README.md)
(SHA `04a7d3abe67047dbe6c6bc9eaa1d322f53d6d2e0168635d770d7077fdbeec7d2`)
reconcile all 13 medians, 104 resources and winners, 13×8 rankings and 1,300
primary samples. The whole accepted shared-layout1a763 current columns are
the baseline; no original, native or baseline validator was rerun.

Over 8–4096, latency GM is **2.515221455% higher**, with **1/10 wins**.
Only T1024 improves (−3.357%). Regressions are T8 +0.377%, T16 +1.369%,
T32 +5.969%, T64 +4.785%, T128 +4.627%, T256 +3.475%, T512 +5.692%,
T2048 +1.227% and T4096 +1.364%. The separate full13 GM is 1.133364704%
higher with 3/13 wins; excluded T1/T2 gains do not affect retention. Six full
choices change at 4/8/32/128/512/2048. Seven rows retain their dictionary,
including both improvements and regressions; these sequential AUTO runs do
not establish a fixed-tactic cause or attribute all changes to ACC1.

Actual AUTO scalars are ACC1×16 / ACC2×88, decoded3×104, B3/S2/local0,
raw5×88 / raw4×16, with agreeing physical/pipeline/epilogue stages. Separate
staging counts remain 87 fused / 17 empty and all 80 retention observations
fused. Initial/build diagnostic native deltas are empty. Benchmark subprocess
593.708782435s versus retained 596.187686985s; outer597.043369875s and timer
utility6.002159850s remain separate from primary latency.

The [actual restore closure](logs/cu132-recovery0909d-single-acc-restore-001/closure.json)
(SHA `c53504dae590d3ea73b5bf5b83faa4ce6bd99a0fd7ce5864f0b5a62941522b91`) confirms the published ACC2 shared-layout source af938
is restored, with no GPU compute processes and unchanged native inventory.
Published head056ce/bodyfd2 and its PR table remain unchanged. The next planned
K128 trial combines held core2335 and catalog1ddb: original eight K256 entries
first, then eight K128 entries, fixed S2 and ACC2. Native checks, the agreed
18 rank tests/42 objects and existing catalog-reset test precede one complete
catalog16 AUTO; these are future scope, not completed evidence. The baseline
remains whole shared-layout1a763, without another baseline run or row splicing.


## Entry 060 — K128 geometry and sixteen-tactic catalog

Final five-file source `5898605107a1057fdb2a079fb9f5d9c7ca7e18d30d0967cf4baa3009eff3f108`
is installed (receipt `6cbfcac1f56f510bc4f5a0389f7807b283f4fd4b7d8a07bbc9bd42c6d5c13fb5`).
The shared prepared-weight contract, ACC2, five warpgroups/two decode groups,
FC1 scratch release, fused BF16 stager and hot scorer remain unchanged.
The automatic product keeps the eight K256 entries first and adds eight K128
entries for M256/C2, N128/N64, F4/F8 and both returns, all S2. Selected K128
has decoded depths 6/4 versus K256 3/2; manual K256 geometries remain supported.
The [saved native review](candidates/cuda132_recovery_0909d/k128_catalog16/NATIVE_REVIEW.md)
passes both M256 K128 captures with ACC2, B3/raw5/S2, REG96 and no stack/local
memory. Static instruction counts are not performance evidence.

**Numerical validation is complete:** combined closure
`781a9ef37f6c52635a498afa4898dcf03263618398328f2a46c1ac0b090ad1e0`
and [independent saved audit](logs/cu132-recovery0909d-k128-catalog16-numerics-independent-001/README.md)
(SHA `c458d0cd8f010bcb32f0e4980e9db5302463d0e46580fdcb8b436203b38af1e1`)
reconcile 18 rank calls / 42 configs, compiled objects and matching resources,
plus one existing public catalog-reset CPU test over sixteen candidates.
Both K128 EP2 reference/wrap returns for N64/N128 supply16/40; the existing
EP1 H64/I64/M257 short fixture supplies2/2. All42 actual selected configs use
F4/group512/S2 and all resources are ACC2/B3/raw5/REG96/local0. Decoded depth
is six for21 N64 objects and four for21 N128 objects. Eight long-K rank cases
retain H7200/I2112 and K57/K17 with32/64 tails; both short cases have K1/K1.
The short public fixture retains original knobsNone, while the artifact helper
explicitly selects K128/S2/F4; its flags are not inherited from a default.

Original42195 passed CPU reset, then its first GPU pytest rejected obsolete
`--w4a16-test-group-hint` before collection. Failed outerc189 and original
logs remain preserved with zero GPU cases/objects. Only the four GPU jobs
retried under11043 in a fresh folder, removing that option; the original CPU
result is reused. Both original and retry source/helper identities agree.
Retry subprocess times are84.394230869/87.350834055s for N64/N128 EP2 and
27.506039984/27.531491576s for N64/N128 EP1. Idle94634 and fetches69658,
23148/17402 are closed, with nativec6da unchanged in the original closure.
No original, native or baseline validator was rerun by the independent audit.

**Full AUTO is complete; the initial K128/catalog16 is not promoted.**
Original59096, idle21787, full fetch62430 and idle fetch92829 are closed.
Canonical completion `1a3178e0930ca7599846662bd80a9dbc09f6f23f8094a84d2a12528926b8d16c`,
original proof9bbf4439/resultc996071f and the
[complete independent comparison](logs/cu132-recovery0909d-shared-layout-vs-k128-catalog16-independent-comparison-001/README.md)
(SHA `1da1bf3b18e3462c0fa76edb37ed3add413ed947225b97cc2a6a06d993b10d11`)
reconcile all13 cold-L2 CUPTI medians,104 winners/resources,13×16 hot rankings
and1,300 samples against the whole retained shared-layout1a763 CURRENT rows.
No original, native or baseline validator was rerun.

The8–4096 GM is **0.463699748% higher**, with **6/10 wins**. Regressions:
T32 +3.488%, T64 +2.010%, T256 +3.059%, T512 +2.760%. All13 secondary GM is1.838736383% lower with8/13 wins;
tokens1/2/4 do not affect retention. Seven dictionaries change at1/2/8/32/128/
512/1024; six full rows retain their dictionary. **All13 winners and104 actual
objects select K256**, so no gain is attributed to executing K128. Current
resources are ACC2/B3/S2/local0, raw5×80/raw4×24, decoded3×80/decoded2×24.
Separate staging remains87 fused/17 empty, with all80 retention cases fused.
Initial/build native deltas are empty; source589 and nativec6da close exact.

The [complete secondary score comparison](logs/cu132-recovery0909d-shared-layout-vs-k128-catalog16-independent-comparison-001/SELECTION_SCORES.md)
(SHA `01dabbf44dcf98ccec591c225374724797281fbfb481b40ee4db55e9a1a8fc16`)
preserves all13 best-subset rows and104 exact K-only dictionary pairs.
Every matched K128 score is higher, with zero printed ties; best K128 subset
loss over8–4096 ranges7.820%–20.287%. These rounded0.1us hot graph selection
scores are separate from primary CUPTI latency and do not predict it.

Benchmark subprocess932.001498857s versus retained596.187686985s is 56.327%
longer; outer935.068686625s and timer utility6.053761550s are separate.
Root does not promote the initial sixteen-entry catalog: no K128 selections
and materially higher tuning/setup wall. The complete initial16 run is kept
as an **experimental BEFORE for B6**; published shared-layout1a763 remains the
retained baseline. No row substitution, drift correction or new baseline run.
Published056ce/bodyfd2 is unchanged. The filled K128 PR draft and architecture
patch remain unpublished historical/held artifacts; root owns further source
selection and any later publication.



## Entry 061 — K128 activation preference B6

Final source `b496327b6666e23af6a0a0ccc557952c5ad10d6c2019e15e5064c50acb7120bd`
was installed for the completed trial (receipt `f2e91a9963b72e61ed5c0a94a5d7b54f1e06831a4d090f9c46a6574cbea7f6e6`),
with preflight `78f08f8a8b515e7a7ef123e92941f8f49fc0d69730ad65781d0b7d1dbec6564d`.
Relative to the complete initial16 experiment, K128 now tries activation
stages six down through two; K256 keeps three down through two. The existing
raw-depth search, ACC2, decoded depths, sixteen-entry catalog, shared prepared
weights, five warpgroups/two decode groups and hot scorer are unchanged.
The public fallback test is parametrized as old `[n64-k256]` and new
`[n128-k128]`, preserving H18272/I64/T257, normalization and its oracle.

The [saved native review](candidates/cuda132_recovery_0909d/k128_activation_b6/NATIVE_REVIEW.md)
passes both H7168/I2048 M256 K128 captures: B6/raw5/ACC2/S2, decoded6 at N64
and decoded4 at N128, REG96/640 threads, zero stack/local memory. N128 uses
separate activation-depth6 and decoded-depth4 state/phase wraps. These native
records do not cover the large-H fallback or establish a latency improvement.

**Numerical validation is complete.** Original7890 passed all five jobs;
idle4568 and fetches89124/77758 are closed. Combined completion
`a50ca075e3bb29b91ac4c15a87ee5f64a0bebf3d4eb45d0e14b618505768046b`
and the [independent saved audit](logs/cu132-recovery0909d-k128-b6-numerics-independent-001/README.md)
(SHA `bd835762c4582e5be491033c5577cdfa4766b1f475d072741f8ecd7a9edfca08`)
reconcile 19 rank tests, 43 configs/compiled objects and matching prelaunch
resources. N64/N128 EP2 references and long-K cases supply 16/40, both EP1
short cases supply 2/2, and N128/K128 activation fallback supplies 1/1.
All objects retain ACC2/S2/F4/REG96 and zero local bytes. The first 42 use
B6/raw5; the H18272/I64/T257 fallback uses **B4/raw2 and 230,528 bytes**, with
K143/K1 and 96/64 tails. Decoded6×21 / decoded4×22 agrees with geometry.
Nativec6da is unchanged in the original closure. Original launch stdout has
five zero exits and its actual terminal PASS marker. No fabricated controller
or original/native/baseline validator rerun is used. The catalog CPU reset
c458 remains inherited, with zero current CPU tests.

**Full B6 AUTO is complete; B6/catalog16 is not promoted.** Original94539,
idle55245 and fetches50352/77945 are closed. Completion
`09ea7d274a151639e6c4a921f1f5940aedc59e96bdf14a61ff585553b79ac51f`,
original proofdf09a54b/resulte0d2adaa and the
[full independent comparison](logs/cu132-recovery0909d-k128-catalog16-vs-b6-independent-comparison-001/README.md)
(SHA `dcdc74ff37e427f27408e9b24b5e4611cd8fb8eabbf16983dfa837769307f9dc`)
reconcile all13 medians,104 choices/resources,13×16 rankings and1,300 samples.
Both complete baselines use CURRENT columns: initial16 1da1 is the experimental
BEFORE and published shared-layout1a763 is the retained overall baseline.

Over8–4096, B6 is **0.234344013% lower latency GM versus initial16**, but
**0.228269083% higher versus published**, with4/10 wins in either comparison.
All13 secondary GM is1.987509569% higher versus initial16 (4/13 wins) and
0.112228124% higher versus published (5/13 wins). Excluded1/2/4 rows do not
affect retention. Published-baseline regressions are T64 +2.664%, T128 +3.863%,
T256 +3.660%, T512 +6.925%, T1024 +0.666% and T4096 +0.044%.
**All13 winners and104 actual objects still select K256/B3**, with ACC2/S2,
raw5×88/raw4×16, decoded3×88/decoded2×16 and zero local bytes. No primary row
executes B6/K128. Initial/build native deltas are empty and nativec6da closes
unchanged. Source/runtime boundaries are established by the original proof;
no original, baseline or native validator is rerun by the independent audit.

The [complete secondary K-score summary](logs/cu132-recovery0909d-k128-catalog16-vs-b6-independent-comparison-001/SELECTION_SCORES.md)
(SHA `fa2f6299f823fdd6ed5feaf1af13a6943732de3e34839fba33a286b19ea6f129`)
retains all13 subset gaps and104 exact K-only pairs, plus each score's change
from initial16. B6 narrows the best-subset K128 gap at32–4096: T2048 changes
9.597%→4.295%, T4096 7.820%→2.575%. Every matched K128 score remains higher;
zero wins/ties. Scores are hot-graph rank-MAX medians printed to0.1us, not
primary cold-L2 CUPTI latencies or a fixed-tactic causal experiment.

Benchmark subprocess is932.617467093s versus initial16 932.001498857s and
published596.187686985s (**56.430% longer than retained8**); outer936.030871167s
and timer utility5.994566776s are separate. Root does not promote unchanged
K256 timing with the added catalog cost. Published056ce/sourceaf938/bodyfd2
and its performance table remain unchanged; experimental runs stay intact.
No baseline rerun, row replacement or drift adjustment is used.

**Current-best profiles are downloaded and delivered.** Exact published056ce /
af938 was restored (receipt `4e97f4599b4ba51d87fa5ca3ab36ba883aefb16b9024146e04ace80efb0f45a3`).
The [profile index](profiles/current-best-056ce-0909d/README.md) links two NSYS
reports at EP8 T32/T4096 and eight NCU reports from EP8 T4096. Original/fetch
sessions28180/52164,88979/8108 and3276/86163 are closed. Final closure
`13a18a33e826a134454c041d4f41804a1f7e9e986d7876ec8dd0add6b5e68e22`
records exactaf938, unchanged nativec6da, all three zero exit markers and no
GPU compute processes (original83784/fetch63172 closed).

The [delivered archive](profiles/current-best-056ce-0909d.zip) is immutable:
6,592,684 bytes, SHA256 `014fc2816f808d4eefd0ebbf772921402061c20ef4d1cb8639bf69da7ac290a2`.
All ten report sizes/hashes match their closed download receipts; NSYS/NVR
headers and zip CRC pass. Source/tactic/tool metadata, commands, small logs,
NSYS SQLite/CSV summaries, checksums and source mapping notes are included;
no driver or DSL compilation caches. Container26.05-py3, NSYS2026.2.1.210
and NCU2026.1.1.0 are explicit. Each NSYS trace has2×8 Mega kernels,
REG96/640/local0. The index records eager across-device launch skew; these
instrumented spans and aggregate GPU times do not replace AUTO cold-L2
latencies. NCU report filename RANK is distinct from its communicator peer ID.
No profiler, benchmark or previous validator was rerun for delivery. Old
f377 profiles remain historical, and the published PR/table is unchanged.



## Entry 062 — Current-best full NCU capture and download

At the user's request, regenerated NCU with `--set=full` and no custom metric
filter on retained publication `056ce0d090d425ee09171e47f6faea61c76c9551` /
source `af938d808556e72925933208f0844cd92f44dff5cc7f407b050897c5660b2e9e`.
The preceding 0909d attempt was interrupted when the devbox disappeared after
37 replay passes; no full reports finalized. Its original failure remains in
`logs/cu132-recovery0909d-current-best-ncu-full-interrupted-001.json`
(SHA `6d4028d3af578e74e1118b9216ca4525834b525cc42c8dadc5d1d2b5f4098f54`).

Replacement `fi-w4a16-mega-0909e` uses explicit image
`nvcr.io/nvidia/pytorch:26.05-py3`, selected after the live NGC release check,
on the same hu-pdx-115 / eight B300 UUIDs and matching loaded stack.
The environment comparison is
`logs/cu132-recovery0909e-same-gpu-environment-match-001.json`
(SHA `644301efa4d461d045db04f68040f5c2ae65f12a661eba5e7bd1a0a5e3516b5c`).
No baseline was rerun solely for this replacement. Native cache started empty;
profile setup produced 22 fresh native build records. Existing native records
were unchanged, diagnostic delta empty, and the closed after-inventory is
`d3cefec87413033d3ec80ad5badc720dfadc9b71e857ee6f6d4ec131a8ceb002`.

**Completed capture:** original99693, closure60776 and download97834 all
returned true zero exits. All eight peers completed application-replay passes
1–40 and finalized one Mega action each. Shape is EP8/global T4096,
H7168/I2048/E256/top-k8, fixed retained M256/N128/K256/C2/S2/F4,
reuse_dispatch_warps, group512, atomic counter, epilogue flags(2,4), no
in-kernel FC2 reduction. NCU 2026.1.1.0 uses strict/grid coordinated
application replay with TCP eight-peer rendezvous and lockstep Mega NVTX.
Three warmups precede one profiled action per rank. Overall replay passes
are unrestricted; `--warp-sampling-max-passes=1` limits adaptive PC sampling
only. Source closure still matches af938, GPU compute processes are empty.
Closure SHA `ba29d096820662cb3e914850ee492820b975bd3cd463a0b51510f5fda77b155d`.

**Actual full-metric verification:** CPU-only API79898/CSV40588 and export
fetch94473 completed. Each report exposes 2,472 metric names, 14 rendered
CLI section headings, one Mega action on matching CUDA device0–7, and
`profiler__replayer_passes=40`. All 14 embedded project sources per report
match the capture manifest. Named valued counters include SM1072, SMSP262,
DRAM32, LTS211 and L1TEX314. The generic installed set lists 22 sections and
estimates 7,314 metrics; it is not the actual per-action metric count.
Aggregate values exist for 2,459 names, except rank2 with 2,436. Sections
include compute/memory/scheduler/warp/instruction/source/launch/occupancy,
PM sampling, roofline and workload distribution. Hierarchical rooflines
extend SpeedOfLight; NUMA/NVLink properties are present, while Tile IR is
not this kernel's execution model.

All peers report six C2C `ctc__rx/tx_bytes_data_user` variants unavailable.
Some derived throughput values exceed 100%, and reported per-rank durations
vary greatly under coordinated replay. These are preserved raw diagnostic
artifacts, not stable throughput or AUTO performance measurements.
Application replay IDs, replay metric and PC aggregated passes are separate
fields. Exact coverage, warnings, units, source hashes and per-rank values:
`profiles/current-best-0909e-ncu-full-t4096-001/full-report-verification/coverage.json`.
No counter result was promoted as a performance gain.

**Delivered bundle:** [full index](profiles/current-best-056ce-0909e-full-ncu/README.md)
and [ZIP](profiles/current-best-056ce-0909e-full-ncu.zip), 47,467,071 bytes,
SHA `7c2affaac4d411b792fd953f46ffaab049e5bcea38f056c68b6c8f62efcf0b50`.
Root independently checked ZIP CRC and its eight new full NCU plus two
unchanged current-056ce NSYS reports. Raw NCU reports total 1,404,214,785 bytes;
automatic/base-unit CSVs, sections, source mapping and original receipts
are included. The two NSYS captures remain the completed 0909d T32/T4096
runs; no new NSYS or benchmark was run for packaging. Old PC-only ZIP
014fc281 remains unchanged. PR Profiling scope now records this evidence
and reproduction; readback verified OPEN/draft/head056ce, body
`96c2677c97ab0b72906e716e46f64549809111432d88438455960176e3e3baf0`.
Final performance, historical CUDA13.0 table and checklist are byte-exact.

After full-profile source/native/idle closure, GPU ownership transferred to
the prepared K128 full-predecode experiment. Its native review, numerics and
whole AUTO result belong in a later entry; this capture establishes no new
kernel winner.

**Final archive reconciliation:** the already-running packaging rebuild finished
after the first delivery/check above. The same download path now holds
47,467,778 bytes, SHA
`9bf5498b71d42713044eaee5a4d2f5dc125397787cca7b768e66efbadf9c8bd2`.
The delta is README spacing and inclusion of the existing CPU-export helper
staging receipt, with regenerated metadata/checksums and archive timestamps.
All ten report files and raw measurement exports are unchanged. The first
7c2affa archive bytes were overwritten by that in-flight builder and no saved
copy was found; its first verification receipt remains historical. Root
rechecked final ZIP CRC and all ten embedded report hashes against local
reports. Final 9bf549 is frozen; later analysis is a separate sidecar. The
public profiling text and performance values are unchanged by packaging.

## Entry 063 — K128 decode-before-acquire: full AUTO, no promotion

**Change:** experimentalB6/sourceb496 → source934d moves decoded TMEM producer acquisition after the source-to-RMEM FP4 decode for K128 only. The shared decoder has a private constexpr `_predecode_before_acquire=False`; Mega selects it only for K128. K256 and split false paths remain unchanged. No early raw release, cache prototype, shared operand release or CLC change is combined. Source manifest1b82f080 and native/package records are under `candidates/cuda132_recovery_0909e/k128_full_predecode/`.

**Native evidence:** fresh N64/N128 compile-only captures use the actual retained shared-layout frontend, direct BF16 decoder and compiler13.3.27 on system CUDA13.2. N64 first capture failed before compilation because an unchanged transitive helper was missing; staged the exact helper and used a fresh retry directory. Successful N64cubin1a6dec38/N128ebd78b08 preserve REG96,640threads,61440-register initial pool,2decode WGs,80/144/64 redistribution, zero stack/local spills. All32 FP4 conversions precede the decoded-slot wait. FC1 still has12 BF16 multiplies sunk after that wait; FC2 has all scaled payloads before it. Therefore this is decode-before-acquire scheduling, not a claim of complete scaled predecode in both phases. SASS adds57 nonNOP instructions pergeometry (+30MOV/+27IMAD.MOV), including28 payload register copies perphase. The original native review is `profiles/cu132-recovery0909e-k128-full-predecode-native-closure-001/CODEGEN_REVIEW.md` with raw PTX/SASS/resources under each codegen directory.

**Numerics:** original managed46543 and fetch48344 completed true zero. Existing N64/N128 EP2 reference/partial/long-K/graph tests, N64/N128 EP1 short-K tests and N128 H18272/I64/T257 activation fallback all passed, unchanged oracle/tolerance:19 rank tests/43 compiled objects. All are640threads,2decode WGs,REG96,local0,ACC2/S2;42B6/raw5 plus one B4/raw2 fallback, decoded6(N64)/4(N128). Root checked the original outcomes/source/resources and wrote completion8e4f717d. No numerical validator or GPU run was repeated for reporting.

**Full measurement:** original managed78831 and fetch58353 completed true zero on fi-w4a16-mega-0909e / c2 hu-pdx-115 /8B300 / `nvcr.io/nvidia/pytorch:26.05-py3`; same loaded stack and physical GPUs as the saved wholeB6 and retained baselines. One complete13-row/catalog16 sweep,100CUPTI samples/row,3warmups,coldL2,CUDAgraph,median per-iteration maximum-rank GPU activity span. Only Mega ran; no split/baseline rerun. Process wall931.968931s includes autotuning/compilation. Source934d remained exact, native inventoryd3ce unchanged, final compute-app and native-worker lists empty. Original executioncb1d8510, benchmarklog40cffc6c, outerexit0, independent completiondcdcc174. Adapted existing saved readers passed once:13rows,104compiled/104winners,13×16 candidate rankings,1300samples. Both whole saved CURRENT columns were reused as-is; no row replacement or minima.

| Tokens | B6 before (ms) | After (ms) | Before / after | After choice |
|---:|---:|---:|---:|---|
| 1 | 0.085409 | 0.085313 | 1.0011x | K256/N128/F8/epi |
| 2 | 0.097809 | 0.104545 | 0.9356x | K256/N64/F8/epi |
| 4 | 0.129841 | 0.122689 | 1.0583x | K256/N64/F4/epi |
| 8 | 0.140193 | 0.141921 | 0.9878x | K256/N64/F8/epi |
| 16 | 0.150657 | 0.147825 | 1.0192x | K256/N64/F4/epi |
| 32 | 0.175362 | 0.178930 | 0.9801x | K256/N64/F4/epi |
| 64 | 0.208386 | 0.201874 | 1.0323x | K256/N64/F8/epi |
| 128 | 0.215538 | 0.206290 | 1.0448x | K256/N64/F8/epi |
| 256 | 0.215298 | 0.217410 | 0.9903x | K256/N64/F8/epi |
| 512 | 0.220643 | 0.220562 | 1.0004x | K256/N64/F8/epi |
| 1024 | 0.239442 | 0.237746 | 1.0071x | K256/N64/F8/epi |
| 2048 | 0.315315 | 0.319155 | 0.9880x | K256/N128/F8/reuse |
| 4096 | 0.483813 | 0.475492 | 1.0175x | K256/N128/F4/reuse |

**Decision:** no promotion. The recorded8–4096 latency GM is0.649321% lower vsB6 (6/10 lower), and0.422534% lower vsretained056ce. However all13 selected tactics are K256 and execute the unchanged constexpr path. These timings do not establish a gain from this change. Secondary paired hot GPU-event scores (0.1us printed precision) are worse for all80 same-tactic K128 rows8–4096, GM+6.604764%; unchanged K256 pairs are+0.118100% (34lower/7ties). Secondary scores are diagnostic and do not replace the primary cold-CUPTI timing. No new current best or PR Final-performance update is warranted.

Full arithmetic/evidence pins: `logs/cu132-recovery0909e-b6-vs-k128-full-predecode-independent-comparison-001/comparison.json` SHA d009b54ce427797c7eb5e8d8ace7515063d4bead2c42dc3b42270add316a5369. Same-tactic selection matrix is `selection-scores.json` in that directory. Retained publication remains056ce0d. After all original processes and fetches closed, restored exact six-file af938 source; candidate bytes were backed up and the restore receipt is43457ee9. Next independent candidate shares eligible activation/decoded completion rings; broader CLC redesign remains separate.

## Entry 064 — Shared operand completion ring

**Change:** retained056ce/af938 → source0a7bac shares the activation-SMEM and decoded-weight-TMEM empty/completion barriers when their stage counts and cluster-consumer ownership match at compile time. Full/readiness barriers stay independent; both producer waits and both MMA readiness waits remain. A single MMA completion releases both operands. Other geometries use the original pipeline construction and releases. No tuning knob, runtime condition, decoder arithmetic, weight layout or CLC change is combined. Only `shim/w4a16/kernel.py` changes (9c9fb36a → 0afda8f8); patchc4bb9afd is under `candidates/w4a16_shared_operand_release/`.

**Native evidence:** N64 B3/D3 removes three mbarrier initializations and one operand-completion commit per K-loop body, saving16 padded control bytes and16 non-NOP SASS instructions. N128 B3/D2 takes the independent path; its complete6032-instruction PC/SASS sequence matches retained. Both captures preserve REG96/640threads,61440-register pool, two decode WGs,80/144/64 redistribution, stack/local0 and no LDL/STL. The saved review is `profiles/cu132-recovery0909e-shared-operand-release-native-closure-001/CODEGEN_REVIEW.md`. Cubins84d11403 and0a065bdf; source/native closure and downloadde896025 completed before numerical installation.

**Numerics:**20 rank tests/50 compiled objects passed the existing reference, partial-tile, long-K, scale/routing and CUDA-graph checks with unchanged tolerance. Coverage includes N64/N128 EP2 both returns, manual M128/C1, and two activation-stage fallback cases. There are29 shared and21 independent objects; all REG96/640/local0/ACC2/S2. N64 H7200 B3/raw5/D3 is shared; N128 long-K B3/raw4/D2 is independent. N64 H18272/I64/T257 B2/raw2/D3 is independent; N128 H12800/I64/T257 B2/raw3/D2 is shared. The last case changes only an existing test's hidden size and tactic, keeping its oracle. Original N64 GPU execution succeeded, but the outer saved reader initially expected199424 rather than actual199296 shared bytes: the16-byte control shrink crosses the subsequent128-byte alignment. Corrected only that expectation and validated saved records; no N64 rerun. The four remaining jobs then completed true0. Completion8688ac50, archive730ac3d9 and idle26f0d1e0 preserve the original reader failure and subsequent closure. Source0a7bac and native inventoryd3ce remain exact.

**Performance in progress:** the first complete-sweep attempt001 failed before importing the benchmark or producing timing rows because two relocated helper modules retained the old `parents[4]` path. Preserved failed001 and original helpers, corrected those two roots to `parents[3]`, verified CPU catalog import, and started fresh full13/catalog8/AUTO100 attempt002 with new output/cache paths. No timing, tactic or source change was made. The complete saved retained CURRENT columns from comparison1a763 are the before baseline; no split or baseline rerun is requested. Attempt002 then completed true0, with13rows/104compiled objects/104winners/13×8rankings/1300CUPTI samples. Benchmark subprocess593.398235s; managed outer596.000066s. Source0a7bac and native inventoryd3ce are exact before/after; GPU apps/workers empty. Original executiond6322094, archive7974e1a2, completion169c5161 and comparisond5af9ec8 preserve the complete evidence. Existing saved readers ran once after download; no timing or earlier validator rerun.


| Tokens | Retained Mega before (ms) | Shared release after (ms) | Before / after |
|---:|---:|---:|---:|
| 1 | 0.085088 | 0.071552 | 1.1892x |
| 2 | 0.106128 | 0.114385 | 0.9278x |
| 4 | 0.121106 | 0.129169 | 0.9376x |
| 8 | 0.148705 | 0.142609 | 1.0427x |
| 16 | 0.160066 | 0.158721 | 1.0085x |
| 32 | 0.178001 | 0.186738 | 0.9532x |
| 64 | 0.202978 | 0.210850 | 0.9627x |
| 128 | 0.207521 | 0.213010 | 0.9742x |
| 256 | 0.207697 | 0.211089 | 0.9839x |
| 512 | 0.206354 | 0.218818 | 0.9430x |
| 1024 | 0.237858 | 0.235619 | 1.0095x |
| 2048 | 0.320691 | 0.310883 | 1.0315x |
| 4096 | 0.483602 | 0.480788 | 1.0059x |

**Decision:** no promotion or PR Final-performance update. Complete8–4096 cold-CUPTI latency GM is0.906776% higher, with5/10 lower rows;32–512 regress1.63–6.04%. Secondary hot GPU-event scores are essentially unchanged:40 same-tactic N64 pairs GM+0.006771% (17lower/3ties),40 N128 independent-path pairs GM−0.061784% (22lower/6ties). The fewer instructions/barriers do not establish an end-to-end gain. The correct compile-time candidate is preserved for later pipeline work, not discarded as a correctness failure; production remains056ce/af938. Full choices and arithmetic: `logs/cu132-recovery0909e-retained-vs-shared-operand-release-independent-comparison-001/`. GPU ownership transfers to the separate broader CLC implementation after all benchmark/fetch processes close.

**User design decision / publication race:** after the general preference to keep pure cleanups, the exact validated barrier patch was committed as089cb0e8c and its push started. The user then explicitly rejected this particular design as too tedious. The in-flight push had reached the branch, so root immediately reverted it infa2a892038f54def18c83571e50b47804f8de1cb and pushed the revert. Live PR readback confirms OPEN/draft/headfa2a892, source tree byte-exact to056ce, body unchanged96c2677c and no performance-table edit. Readback record `logs/pr5019-shared-release-promotion-reverted-001.json`, SHAdf6df0be. The candidate is not retained in the PR; do not reintroduce it based on the superseded general cleanup preference. CLC remains independently based on056ce/af938.

## Entry 065 — Configurable CLC bring-up and precision ownership

**User requirements:** exactly two decode WGs/five total, CUDA13.2, general scheduling/overlap work, and no shared-operand-release design. Active source must be inspectable in the primary checkout. The user identified W4A4 core inheritance as an ownership hazard and requested W4A16 alongside existing MegaMoE precisions. The intermediate separate `cutedsl_w4a16_megamoe` package was rejected and removed; final organization is `cutedsl_megamoe/src/moe_nvfp4_w4a16/` plus `shim/w4a16.py`. This owned precision is a documented exception to the original verbatim source-drop rule; existing vendored files are unchanged.

**CLC control:** immutable sourcebd842/patch39b6 uses fixed128-thread dispatch, elastic640-thread CLC FC1/ready-FC2 compute, fixed128-thread finish. Bitmap ownership is exact-once across initial CTAs, successful cancellation and permanent software fallback after first failure. One release-published descriptor per completed row retains FC2 feature parallelism. Warp8 obtains claims; warp7 maps/publishes through a two-stage pipe; only whole-grid completion permits workspace reset. All three launches must be included in performance results. The public default eight tactics remain unchanged; CLC is explicit/configurable.

**Initial codegen and correctness:** earlier native attempts caught missing constexpr dispatch and an SSA loop-state carry, both fixed. N64C2/reuse, N128C2/reuse and C1/epi large-shape captures compile with REG96/640 and no spills; transport capacity is checked per return geometry. The first small C1/epi reference fixture stopped at the strict resource observer before numerics. A diagnostic observer retained the actual fields: REG96, driver-local8 for compute, normal transport resources. Exact no-lineinfo native capture shows ptxas STACK8, 4STL/3LDL; the spilled scalar is warp8's CLC bundle, not dequantization or MMA payload. Artifacts: `profiles/cu132-recovery0909e-clc-small-m128n64c1-epi-001/codegen/`.

**First actual numerical invocation:** original66493, `cu132-recovery0909e-clc-numerical-c1-epi-spill-known-001`, passed1 rank test/four compiled objects with unchanged reference, scale/routing, tail and graph replay oracles. The helper records the known spill; no numerical tolerance or mandatory launch-capacity check was relaxed. Earlier strict resource failures remain preserved. Remaining EP2 coverage is in progress on the unchanged bd842 control. No CLC performance or speedup claim exists yet.

**Ownership cleanup in progress:** source audits are `candidates/w4a16_ownership_refactor/DEPENDENCY_AUDIT.md` and `ORGANIZATION_PLAN.md`; pre-refactor source is saved there. W4A16 now owns its constructor, BF16 workspace tables/views, BF16 epilogues, dynamic BF16 instruction helper, FC12 scheduler and specialized work extension. It no longer initializes fake FP4 activation/epilogue state through the W4A4 compute classes. Generic transport, flag tracking, scheduler records/rings and pure coordinate mapping remain shared. The retained split-W4A16 decode helper and common NVFP4 prepared weight contract remain intact. Root's ten original kernel compute/JIT method ASTs are unchanged except owned symbol names. Initial whole-change precommit passed mypy and Ruff checks; its formatter changed one file, so final checks follow completion. The ownership source is not yet installed/GPU-validated and is uncommitted.

**Next scheduler trial:** held patch48c6 in `candidates/w4a16_configurable_clc/bundle_lifetime/` rotates the CLC claim loop, consuming each queried bundle immediately and removing the loop-carried bundle scalar. Initial claim stays before the loop; ready-pop/terminal/query/claim ordering is preserved. No new runtime state, register redistribution or shape dispatch. Compile and numerical outcomes are pending; no retention decision or PR table change.

**Completed CLC correctness cohort:** immutable bd842 passed11 rank-tests/41 compiled objects without changing the reference/scale/routing/tail/graph oracles or tolerances. Six S2 public-wrapper cases cover10 rank-tests/40 objects; manual C1/S3 graph coverage adds1/1.31 compute objects report driver-local0 and10 report local8 (C1/epi3, N64C2/epi6, S3graph1); all are REG96/640 threads/two decode WGs, with legal transport resources. Zero spills remain an optimization objective, not a mandatory correctness gate. Original invocations66493,75191,76031,66173,71507 and their fetch/idle records closed true0. No passed node was rerun just to consolidate reporting. Completion `candidates/w4a16_configurable_clc/numerical_spill_known/completion.json`, SHA1534a4d7810754a41c54d2771cb28ddfbeb9266d837af8e352981b2f04569528. Final native inventoryd3ce and sourcebd842 were unchanged; GPUs idle before ownership install. No CLC timing result follows from these checks.

**Whole-PR scope cleanup:** removed `validate_global_scale_support`, the associated generic capability flag/layer gates, and rejection-only tests. Seven existing dtype/core/layer files now match PR base91bda exactly; NVFP4 W4A4 preprocessing retains only the intentionally shared byte-layout helper. Actual W4A16 scale validation and optional alpha fields remain. Removed unrelated global benchmark argument guards, retained profiling/replay controls required for the requested NSYS/NCU loop, and corrected stale W4A16 autotune/stage documentation. Read-only scope audit is `candidates/w4a16_pr_scope_cleanup/AUDIT.md`, SHA9179b61c8dbdf20c09da1247c2638bde2ce5f666ec1ffa4dcfa898e21c46878b. All precommit checks passed after the final source cleanup (`logs/w4a16-ownership-and-scope-precommit-004.log`).

**Ownership validation:** final source098c89e4dbc049ddb94c98362f4570098aea3d638dfbd0914604bee632d5c85a, manifestb7812d41 and deltae88ab0e1 are frozen under `candidates/w4a16_ownership_refactor/validation/frozen/`. The install6459 replaced bd842 and verified exact source/helper inventories, backing up changed/deleted files. The first actual constructor comparison35222 failed because its helper omitted the public frontend's explicit `apply_topk_in_fc1=False` and compared the old inherited, publicly unreachable True default. A fresh corrected helper retained the same180 configurations; original33155 passed all180 actual CUDA-hidden old/new constructor comparisons, including selected state, complete workspace region offsets/sizes/reset prefixes, and transport configuration. Product source was unchanged. Host/import, native, numerical and full default8/CLC8 timings remain separate pending checks; constructor equivalence is not a GPU performance claim.

**Next candidates remain isolated:** the independent loop-rotation review `bundle_lifetime/REVIEW.md` (SHA79a9da1a074b81c99ad4c4d5ccc796bcca2b7d889fc37fd6d4a7719f8e0e8ba1) found no new ownership, ordering, collective participation or termination defect. Generated liveness and spill removal are unverified. A separate balanced physical-launch budget candidate is being prepared; its workspace/bitmap sizing and software fallback must continue covering all actual work under skew. The review also identified that future activation-SF state removal must preserve the existing eight-word physical record alignment rather than changing to a seven-word stride. None of these changes is included in source098c.

**Ownership native preservation:** current source098c passes139 selected host tests/no skips in4.54s plus the actual180 constructor comparison. Host closuree3fb6fce and preflightff6e410d record the real compiler/modules. Corrected default N64 original55006 and N12842057 produce exact retained device instructions, including PC/disassembly and both encoded words/scheduling controls:5504 N64 and6032 N128. Both preserveREG96/640/STACK0/LOCAL0, dynamic shared200064/230784. Small C1/CLC original29378 also exactly matches its saved descriptor across dispatch832, compute3232, finish400 instructions, with unchanged computeSTACK8. Root review and comparison JSONs are under `candidates/w4a16_ownership_refactor/`; these are actual byte comparisons, not AST equivalence or normalized register names.

**Native observer repair boundary:** first N64 original39063 compiled once but failed its postcompile reader because the outer wrapper set KEEP/DUMP/CACHE/LINEINFO after importing CuTe. Requested lineinfo1 was not confirmed effective. Strict extraction recovered the actual165512-byte fatbin and165376-byte cubin from the original host MLIR; cubin ef8ca3e2 has88064 code bytes and2184 constant0 bytes. The text differed at2989 bytes from the saved lineinfo1 control; constant0 was exact. Corrected native_v2 sets options before import, and candidate-only capture55006 then matched all instructions/encodings. No baseline rerun, fabricated PTX or original-output replacement was used. The reader's unconditional zero-stack/local assertion was separately removed so it records the already-known legal small CLC spill. Future captures use native_v2; initial helpers and failed artifacts stay preserved.

**Final ownership validation and publication:** all six matched CLC geometry/return captures (18 symbols) preserve the bd842 instructions, both encoding words and resources; summarya23d2626 is `native-admission-summary-098c.json`. N128 saved manual controls usebundle3; initial validbundle1 captures are preserved for AUTO and two candidatebundle3 captures establish the matched manual comparison. No baseline was recompiled. Native/capacity closure8b6fc691 verifies source098c/native d3ce/idle. Full numerical original45541 then passed11 rank-tests/41 objects: C1S2two tests/8 objects, N64S2four/16, N128S2four/16, C1S3one/1. All33 setup/call/teardown reports passed, with31 compute local0/10 local8 and all82 transport objects local0. Idle75170, fetch65998 and idle-fetch63923 closed true0; closure380be263/resource summarycd354ad9 preserve the original records without a second validator invocation.

Source098c was committed and pushed as6bc8b323c760d221bfb76996d93ebf32d1d72984, with commit-time precommit passing and a clean primary checkout. Live PR5019 readback confirms OPEN/draft/head6bc8b323, body2a4956917d7104f0abda6554d1037b07106f4fae1555c3ea296ef9736e8cc715. Body describes ownership/CLC/scope and exact validation; all30 lines of the two existing performance tables remain unchanged. No PR comments. Receipt `logs/pr5019-ownership-published-001.json`; raw readbackdbcf6d5d. Default full13 AUTO original49267 is in progress, and a separate CLC8 full13 follows. Neither is yet a completed timing claim.

The next loop trial uses `bundle_lifetime/narrow_pipeline/source.patch` SHA25d0dec7ec156904c5bed7334e1eb4f9b92f25c8206fc789788b4e736f53a848, proposedclc2c9dc3dd. It keeps the reviewed rotation but passes only the cluster pipeline to its helper instead of the entire serialized scheduler; explicit ds/claim_state carry and operation order are unchanged. Source checks/Ruff/format/apply-check pass, no primary port or native/GPU result yet. Separate balanced-launch patchd6cc4384 and activation-SF cleanup7c533913 are held; the latter has independent serialization/alignment review53bb5cea. A transport-overlap design audit is saved separately and is not implementation/performance evidence.


## Entry 066 — Complete default and CLC baselines; documentation cleanup

Source098c/commit6bc8 completed both independent full13/catalog8/AUTO100 invocations on the same0909e eight-B300 stack. Default original49267, idle64526/fetch66543; CLC original45517, idle44330/fetch80450 all returned true0. Each has13 rows,104 selections,13x8 rankings,1300 primary samples and staging87 fused nonempty/17 empty paths; all80 retention-range rank cases use fused staging. Default subprocess585.255315s; CLC607.071433s. Whole original outputs and source/native/idle closure are pinned by BASELINE_COMPLETION.json SHAe60272e9. Default reconstruction9d6b063c/result490bdf86; CLC reconstruction57eb28fc/resultb7475026. No split run or baseline rerun was added.

# Retained default versus ownership default

| Tokens | Before ms | After ms | Change | Before tactic | After tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085088 | 0.088081 | +3.518% | N64/F4/epi | N64/F8/epi |
| 2 | 0.106128 | 0.097697 | -7.944% | N64/F8/epi | N64/F4/epi |
| 4 | 0.121106 | 0.120145 | -0.794% | N64/F8/epi | N64/F4/epi |
| 8 | 0.148705 | 0.142850 | -3.937% | N64/F8/epi | N64/F4/epi |
| 16 | 0.160066 | 0.150097 | -6.228% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178001 | 0.180274 | +1.277% | N64/F4/epi | N64/F4/epi |
| 64 | 0.202978 | 0.205010 | +1.001% | N64/F8/epi | N64/F4/epi |
| 128 | 0.207521 | 0.214977 | +3.593% | N64/F8/epi | N64/F4/epi |
| 256 | 0.207697 | 0.206642 | -0.508% | N64/F4/epi | N64/F4/epi |
| 512 | 0.206354 | 0.202609 | -1.815% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.237858 | 0.229410 | -3.552% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.320691 | 0.332499 | +3.682% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.483602 | 0.479478 | -0.853% | N128/F4/reuse | N128/F4/reuse |

8–4096 geometric mean: -0.781942%; 6/10 lower. The 1/2/4 rows are excluded from this summary.

Direct arithmetic from original checked saved result; no original or baseline validator rerun, no row replacement or drift correction. Default device instruction encodings are unchanged; timing differences are not attributed to ownership extraction.


### Default versus optional CLC

| Tokens | Default ms | CLC ms | Change | Default tactic | CLC tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.157281 | +78.564% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.279458 | +186.046% | N64/F4/epi | N128/F8/epi |
| 4 | 0.120145 | 0.429859 | +257.784% | N64/F4/epi | N128/F4/epi |
| 8 | 0.142850 | 0.602326 | +321.649% | N64/F4/epi | N128/F8/epi |
| 16 | 0.150097 | 0.715973 | +377.007% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.909385 | +404.446% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 1.064458 | +419.222% | N64/F4/epi | N128/F4/epi |
| 128 | 0.214977 | 1.100475 | +411.904% | N64/F4/epi | N64/F4/reuse |
| 256 | 0.206642 | 1.110937 | +437.614% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 1.121626 | +453.591% | N64/F8/epi | N128/F8/epi |
| 1024 | 0.229410 | 1.150028 | +401.298% | N64/F4/epi | N128/F4/epi |
| 2048 | 0.332499 | 1.265997 | +280.752% | N128/F4/reuse | N128/F8/epi |
| 4096 | 0.479478 | 1.875520 | +291.159% | N128/F4/reuse | N128/F8/epi |

8–4096 geometric mean: +376.166014%; 0/10 lower. The1/2/4 rows are excluded.

Whole-invocation default8 versus explicit CLC8 on identical source. No numerical/native/sample/scorer validators rerun; no row replacement or drift correction. Both catalog selectors are measured independently. Default compute epilogue flags are2/4; CLC effective compute flags are1/1. F4/F8 remain transport settings; all CLC bundles are1. CLC includes dispatch/compute/finish launches and unchanged staging/reduction.


Default native encodings are unchanged, so the small aggregate timing difference is performance preservation rather than a causal kernel improvement. Optional CLC is4.761660x slower over8–4096. All104 large-shape CLC compute observations areREG96/640/local0; dispatch104REG34/128/local0; finish96epiREG16 and8reuseREG26, all128/local0. The slowdown cannot be explained by the observed small-fixture spill. Default stays unchanged. The complete CLC resultb747 is the BEFORE for subsequent CLC decisions.

**Requested documentation/configuration cleanup:** commit057fc30c0568669bafd6937ce9673515544bb198 restores .pre-commit-config.yaml and pyproject.toml byte-for-byte to PR base91bda. README/VENDOR/SKILL additions now describe the precision package and provenance without user-authorization/exception rhetoric or custom lint-policy claims. No kernel, tactic, test or benchmark changed, and no GPU rerun was performed for this cleanup. Commit-time text/config checks passed. PublishedPR5019 remains OPEN/draft/head057fc30c; body112f53cd3ecc409e2a6460e86b8b84faf72cf931a4b633e234b34b16b1a642d2 carries the entire fresh default column, unchanged split/CUDA13.0 columns and explicit CLC limitation. No PR comments. Readback: logs/pr5019-neutral-cleanup-after-body-edit-001.json.

**Next trial:** root applied narrow_pipeline/source.patch25d0dec7 to primary, passed explicit Ruff lint/format and git diff checks, and generated the standard sole-clc.py delta. Source11ea88a3c99960a9a1006e487abb69578210d4296b6304b04897c7f2c6b0eace, manifest2017b23d/delta2c57d17d/stagea7c651de under candidates/w4a16_ownership_refactor/clc_loop_rotation_001. The narrow helper consumes each claimed bundle before the loop boundary and passes only its cluster pipeline, preserving explicit ds/claim_state updates and operation order. Integration owns install/native/unchanged11/41/fullCLC8 validation. No native outcome or retention decision yet.


## Entry 067 — CLC loop lifetime and centralized maintained implementation

The loop trial11ea installed via original53425, preflight87878, exact native inventoryd3ce. SmallC1 original37524/fetch6248 produces compute3296 instructions versus3232 before; all3LDL/4STL are removed and STACK8→0, REG96/640 and dynamic193024 unchanged. Its dispatch832/finish400 instructions and encodings are exact. N64 original33310/fetch69312 computes4360 versus4288 instructions, stillSTACK0/LOCAL0/REG96/640/dynamic200192; N128 original1487 computes4888 versus4824, same zero-local resources/dynamic230912. Large dispatch1768 and finish392 are exact. Native source/idle closure34626 and transport associationf59047da passed; original11/41 numerical cohort87782 is running. This is native spill improvement, not yet latency evidence. Whole CLC baselineb747 remains BEFORE.

After the complete13-row loop AUTO and saved reader close, integration will capture one NSYS diagnostic using the selected T128 CLC tactic, existing profile_nsys mode,2 profile iterations,cuda-sw and all8GPUs. `--num-tokens=128` is128 global source tokens/16 per rank; misleading historical helper field names do not change this. No default or NCU rerun is requested.

**New user organization decision:** the user recognized the repository's VERBATIM kernel-team drop rules and superseded the earlier requirement to add W4A16 directly under that src tree. The selected maintained home is `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`, a precision sibling layout for future maintained MegaMoE implementations, with frontend beside kernel modules and no extra src/shim layers. The public MegaConfig/MoEEpLayer API is unchanged. Root is preparing the kernel/import migration and restoring the3vendor docs to base; iteration_prep moves host/autotune functions and updates consumer/test imports. Shared primitives continue through the existing public kernel_helpers boundary, without editing vendor source.

**Cleanup:** held44f7e419 removes six token-communication forwarding methods at seven callsites and flattens the transpose implementation's docstring-only subclass. Expanded/flattened module AST checks pass; all18transpose methods/class constants and the meaningful alpha/MLIR serialization, workspace and guarded-compute helpers are preserved. There is no native lowering claim. Root merges this with the mechanical move under `candidates/w4a16_central_refactor/kernel_proposed/`; normalized move ASTs are exact to these reviewed inputs. The pending three-warp payload overlap and tight-row launch remain separate performance changes and will be rebased to the new structure.


**Entry067 completion — source11ea, commit765383cf7:** the original numerical cohort completed all11 rank-tests/41 compute objects with unchanged oracles/tolerances; all41 now record LOCAL0 (the preceding source had10 LOCAL8 objects). Original numerical/source/native/idle completion is `logs/cu132-recovery0909e-clc-loop-numerical-full-001-idle.json`, SHA `0d429799d75d6816236abb9836f5819e31bc835ac3b74d70df58c03246e801d4`. This completes the numerical run reported as active above; it is not a new test cohort.

Original whole CLC8 AUTO100 (`cu132-recovery0909e-clc-loop-auto13-direct-001`) and source/native/idle closure completed. The original saved reader records13 rows/104 compiled records/104 actual choices/13×8 rankings/1300 samples. Loop reconstruction `0e2f3b06554611d8c86360836186b26b02324932f2ffd68768a412e103a22a55`, result `458e3fc4e1299a65d706962b5e7dad9fa0d5c9f15561a0f18c1ec0493b8d01f8`; whole preceding CLC proof57eb/resultb747 remains BEFORE. Independent comparison `logs/cu132-recovery0909e-clc-before-vs-loop-independent-comparison-001/comparison.json`, SHA `0f9ebc70d2d0df935de55342378ff55bbeac7e738055719e85e9f5b63f072943`, supplies the complete table:

| Tokens | Before ms | Loop ms | Change | Before tactic | Loop tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.157281 | 0.160994 | +2.361% | N64/F4/epi | N128/F4/epi |
| 2 | 0.279458 | 0.280483 | +0.367% | N128/F8/epi | N128/F8/epi |
| 4 | 0.429859 | 0.431571 | +0.398% | N128/F4/epi | N128/F8/epi |
| 8 | 0.602326 | 0.584901 | -2.893% | N128/F8/epi | N128/F4/epi |
| 16 | 0.715973 | 0.714055 | -0.268% | N64/F8/epi | N64/F8/epi |
| 32 | 0.909385 | 0.905479 | -0.430% | N64/F8/epi | N64/F4/epi |
| 64 | 1.064458 | 1.073177 | +0.819% | N128/F4/epi | N128/F4/epi |
| 128 | 1.100475 | 1.105851 | +0.489% | N64/F4/reuse | N64/F4/reuse |
| 256 | 1.110937 | 1.110124 | -0.073% | N64/F4/epi | N64/F4/epi |
| 512 | 1.121626 | 1.111834 | -0.873% | N128/F8/epi | N128/F8/epi |
| 1024 | 1.150028 | 1.148381 | -0.143% | N128/F4/epi | N128/F8/epi |
| 2048 | 1.265997 | 1.256331 | -0.764% | N128/F8/epi | N128/F8/epi |
| 4096 | 1.875520 | 1.883359 | +0.418% | N128/F8/epi | N128/F8/epi |

Retention8–4096: latency GM **−0.376683%**,7/10 lower; regressions at64/128/4096. Secondary all13 GM−0.052067%;1/2/4 remain reported but excluded from retention. T8/T32/T1024 change tactics. This is a whole independent CLC AUTO comparison, not fixed-tactic causal attribution; the loop cleanup removes the known spill but does not resolve CLC's large slowdown versus default. Timing includes dispatch/compute/finish and existing staging/reduction, with unchanged bundle1/S2, graph scorer and primary cold-CUPTI method. No default/split/baseline rerun, row replacement or repeated original validator was used for this completion update.

Root committed the validated loop change as `765383cf71971c09812bec04ca4a0a7427cb7635` (`perf(moe): shorten W4A16 CLC bundle lifetime`); publication confirmation is pending. The central host/kernel/import proposal and wrapper cleanup44f7 are prepared only, with source-local checks; no central runtime result is claimed. Pending after its primary port/freeze:5 native comparisons (2default+3CLC), existinghost139, unchanged11/41 numerics, and default8/full13 AUTO100 against the complete owned098c default run. CLC full timing will be repeated only if native comparison does not establish preservation and root selects further validation. Tight rows, SF-state cleanup and payload overlap remain separate held source changes.


**Entry067 publication/central-port update:** root confirmed push of765383cf71971c09812bec04ca4a0a7427cb7635 to the fork. The reviewed central move is now ported to primary and frozen as source `184b73863665d3485d6099dc1e8e935e893590c631b9f25f983ace17e722cbc6` / manifest68fcd483 under `candidates/w4a16_central_refactor/validation/frozen/`. Integration has the execution handoff; five native comparisons, host139, numerical11/41 and default8/full13 timing remain pending. No central test or runtime result is claimed by the port.
## Entry 068 — Central maintained package and wrapper cleanup

The user superseded the earlier placement inside the vendored source drop.
The primary implementation now lives in
`flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`, with the frontend and autotuner
beside the device modules. There is no additional `src/` or `shim/` directory
inside this maintained package. The old precision directory and W4A16 shim are
removed; existing vendor source, VENDOR.md, SKILL.md, and repository tooling
configuration match PR base91bda. The kernel_src README has only a generic
consumer-boundary clarification. Common vendor primitives are exported through
the existing public package/kernel_helpers boundary, without reverse W4A16
exports or direct raw-package imports in maintained code.

The cleanup removes six token-communication forwarding methods and a
docstring-only transpose subclass. The meaningful scale serialization,
workspace, frontend lifecycle, and guarded compute helpers remain. Expanded
wrapper ASTs and relocated operation ASTs match the preceding implementation;
the default eight tactic dictionaries and scoring algorithm are unchanged.
The activation-SF serialization cleanup, physical launch estimate, payload
overlap, and row-metadata redesign remain separate held decisions.

Initial source184b was never installed. Moving the modules under normal
repository checks exposed an existing optional IKET import's mypy `no-redef`;
a targeted type-ignore comment preserves its runtime AST. Final source
`57e2d2793d99321aeebd7db4aa619e81759993a56a8c508cb126eb27f5942fd2`,
manifesta0bd502a/deltaf4d781c8/stage66f9969b, is frozen under
`candidates/w4a16_central_refactor/validation/frozen_v2/`. All precommit hooks
pass (`logs/w4a16-central-refactor-precommit-002.log`). The project benchmark
launcher's only change updates its source-hash paths; timing is unchanged.

Stage54497/install83058/preflight61142 closed true0 on the existing 0909e
CUDA13.2/eight-B300 stack. Host71654 passed139 tests, zero skips/failures/errors,
two existing warnings, in5.73s. Native original97986 passed all five captures:
default N64/N128 have5504/6032 instructions; CLC small C1 has832/3296/400,
N64 has1768/4360/392, and N128 has1768/4888/392 dispatch/compute/finish
instructions. All eleven role comparisons preserve PCs, disassembly, both
encoding words, scheduling controls, configuration and resources. Comparisons
are saved under `candidates/w4a16_central_refactor/execution/`. This establishes
matched native preservation, not a new latency gain. Numerical11/41 and the
complete default8 AUTO13 sweep are pending; the complete loop CLC result stays
the CLC reference without an unnecessary timing repeat for the relocation.


**Entry068 completion/publication update.** Central source57e2 is committed and
pushed as `6af61c1ff35ec5863b7699a54d2f402299c24437`. Host139 and all five native
captures/eleven exact role comparisons above are complete. The unchanged
numerical cohort also completed11 rank tests/41 objects, all observed compute
LOCAL0, with all original oracles/tolerances retained. The final
[numerical/source/native/idle closure](logs/cu132-recovery0909e-central-numerical-full-001-idle.json)
is SHA `b606e83680a2f074218481b393d79e244994e916331ab1b8a08d008b0e4eadb1`;
closure consumes the saved summaries without invoking the original validator again.
The [compact numerical result](candidates/w4a16_central_refactor/execution/numerical-result.json)
is SHA `3af0c73011396f977e725b54cc9369c087447efa06ec138d18fc67140f0f50e8`.
The complete default8/full13 AUTO100 process59432 is active as
`cu132-recovery0909e-central-default-auto13-direct-001`; it is not completed timing
evidence. Its whole BEFORE remains owned098c result490bdf86/proof9d6b063c.

[PR readback](logs/pr5019-central-after-body-edit-001.json) confirms OPEN/draft,
head6af61c1f and body SHA
`4e8de415df74f513af5d51a37c8167dd07009d9a6b4f7ca40996710666f47bd5`.
The architecture/validation body is current; its two performance tables retain
all26 numeric rows unchanged, as recorded in
[body preparation](logs/pr5019-central-body-preparation-001.json). No new default
performance number or CLC timing repeat is claimed by this publication.

The completed selected global-T128 CLC NSYS diagnostic is locally delivered:
[report](profiles/clc-loop-0909e-nsys-t128-001/ep_w4a16_megamoe_t128.nsys-rep) and
[README/analysis](profiles/clc-loop-0909e-nsys-t128-001/README.md). It is source11ea,
128 global source tokens/16 per rank, two eager iterations/all8 GPUs, with
source/native/idle closure. Its durations remain diagnostic and separate from
the complete loop AUTO comparison.

The next held trial is [tight rows](candidates/w4a16_configurable_clc/central_refactor_followups/tight_rows/README.md)
(patch101b7cca), with [prepared three-native/11–41/CLC8-AUTO13 adapters](candidates/w4a16_central_refactor/tight_rows_validation/HANDOFF.md).
Future source and runtime receipts remain unbound. The [task-or-terminal candidate](candidates/w4a16_configurable_clc/central_refactor_followups/task_or_terminal/README.md)
is separately held at patche8662a2a with [independent review45d2a6c7](candidates/w4a16_configurable_clc/central_refactor_followups/task_or_terminal/INDEPENDENT_REVIEW.md).
[Row metadata](candidates/w4a16_configurable_clc/row_metadata/README.md) ccb26f62,
[repaired central payload overlap](candidates/w4a16_configurable_clc/central_refactor_followups/payload_overlap/README.md)106d6ab9,
and activation-SF cleanup remain separate source proposals; none is combined
with57e2 or claimed as an executed result.


**Entry068 final default AUTO closure.** Original process59432 completed the
entire central57e2 default8/full13 AUTO100 run, with exact source/native/idle
[closure](logs/cu132-recovery0909e-central-default-auto13-direct-001-idle.json)
SHA `4539c36365adf3ee6b684e9ea3d8bbd998a7c51ac5bd7b13dcb2b8a7c554ad07`.
The saved reader ran once: [proof](logs/cu132-recovery0909e-central-default-direct-auto-reconstruction-001/reconstruction.json) SHA `d56db1c9303192c53d91a12e84e304ce206e3ea42981cc35ec25a69608b3438e`;
[result](logs/cu132-recovery0909e-central-default-direct-auto-reconstruction-001/reconstructed-result.json) SHA `0c19b3eecd74b2d6e92c3d34d4474a6f1653d69930d94c47c188e748f8c9d567`. It retains13 rows,
104 compiled/winner records,13×8 rankings and1,300 primary samples. The separate
arithmetic [comparison](logs/cu132-recovery0909e-owned-default-vs-central-independent-comparison-001/comparison.json) is SHA `f15e1811abba2a948a085ffc4497cc948e7b3881de242aff5a6120b91b4fafdb`.
The whole BEFORE is the complete owned098c default run (result490bdf86,
proof9d6b063c), using its current columns without row substitution.

All rows below come directly from that completed saved comparison. Both are
M256/C2/K256/S2 public default8 AUTO sweeps; N/F/return labels identify the actual
selected tactics. Tokens are global source tokens distributed across8 ranks.

| Global tokens | Owned098c ms | Central57e2 ms | Change | Owned tactic | Central tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.095521 | +8.446771% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.114609 | +17.310665% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.116753 | -2.823255% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.140369 | -1.736787% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.153313 | +2.142614% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.185074 | +2.662614% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 0.210722 | +2.786206% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.208066 | -3.214763% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.218787 | +5.877314% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.218546 | +7.865889% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.237154 | +3.375616% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.322643 | -2.964219% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.479478 | 0.470949 | -1.778809% | N128/F4/reuse | N128/F4/reuse |

Primary8–4096 latency GM is **+1.437758851%,
4/10 rows lower**. The secondary all13 GM is
+2.767275%,5/13 lower.
The1/2/4 rows stay reported and are excluded only from retention. Central
subprocess wall is577.895060s versus
585.255315s for owned098c. Matched default
native code and successful central validation establish implementation
preservation; this sequential AUTO comparison does not establish a performance
gain or a code-level cause for the timing differences. Keep the previous
owned098c whole default best table. There was no baseline/split/default rerun,
row splicing or repeated original validator during this documentation update.

## Entry 069 — Scoped init export cleanup

The user requested init cleanup without rerunning the pending performance run,
then narrowed the scope to preserve unrelated code. The final change touches
only three init files: `flashinfer/moe_ep/__init__.py`,
`kernel_src/cutedsl_megamoe/__init__.py`, and its `shim/__init__.py`. The shim
initializer is restored exactly to PR base91bda. The root imports the five needed
private helpers directly from the curated shim modules and deduplicates only
the28 PR-added primitive names through `_KERNEL_PRIMITIVES`. All98 root exports,
the34-name lazy sequence, its original handler AST, eager import origins and the
old helper names remain intact. `kernel_helpers.py` is byte-exact6af; the owned
kernel, frontend, autotuner and their named public imports/exports are unchanged.

[Static identity proof](candidates/w4a16_init_cleanup/checks.json) SHA
`dc703c5a8a42521a7e73cd3a6d8efcf83d891e4798555548db1527888596c8eb`
binds source `c2675f51751cab84febe84e173ae3971cacd7fbe85b6ef8bcb9b8cd55c193ba7`
and [manifest](candidates/w4a16_init_cleanup/source-manifest.json) SHA
`507e128b730d2e45b172e04b353b18cf09f11f07893123fc048f3e995574ed8e`.
This is static import/export identity evidence only; no host/GPU/numerical or
performance cohort was rerun for the cleanup. Commit
`5152a9e7cf50c46b76719735d7269a28a4e01130` is published.

[PR readback](logs/pr5019-init-cleanup-after-body-edit-001.json) confirms
OPEN/draft/head5152a9e7 and body SHA
`8183aeada98c46175aa31e7a02c3a42551da8fdb93afc182a85c2c8d5f126463`.
The prepared `PR_BODY-central-closed.md` was copied to the normal draft files by
root; this documentation update does not edit them. Both performance tables
retain the same26 numeric rows, including the previous098c whole default best
table. Central57e2's closed result is described separately without a gain claim.

## Entry 070 — Tight-row launch trial prepared in primary

The reviewed physical launch estimate (held patch101b7cca) is now in primary
and handed to integration as source
`4cf25bd564991ca232f399c36faa4f625c1d7417675846282c6259bbdae363a6`.
Its frozen package is
[candidates/w4a16_central_refactor/tight_rows_validation/frozen](candidates/w4a16_central_refactor/tight_rows_validation/frozen/):
manifest `1f937b40c648a8965b3351c8f0b5d741d0715be04da2cce06e50d64e9064bbaf`,
delta `5d5dd9eeffb183c7d8e8f188ac76e4a65a76759adbef405d2edd0e2ac147253c`,
stage manifest `d87a354c7ee3085ccae23e9e7148955c599edbc69dda3a238bb900bc71ae5ec9`.
This four-file delta from remote57e2 contains the exact three init cleanup files
plus the reviewed kernel constructor/CLC-launch change. Full workspace, bitmap,
queue and software-fallback capacity remain intact; the public default path,
two decode WGs and five total WGs are unchanged.

Validation is **pending**, not a completed result. The
[handoff](candidates/w4a16_central_refactor/tight_rows_validation/HANDOFF.md) reuses
three CLC native fixtures, unchanged11/41 numerics and wholeCLC8/AUTO13. Its
[init-cleanup amendment](candidates/w4a16_central_refactor/tight_rows_validation/INIT_CLEANUP_AMENDMENT.md)
accepts only the pinned static cleanup proof alongside the reviewed kernel AST;
it adds no host/GPU/capacity cohort for init cleanup. The six original transport
capacity receipts are reusable only through the existing exact native-role
association. Whole completed loop11ea result458e3fc4/proof0e2f3b06 remains the CLC
experimental BEFORE; the retained default table remains owned098c.

Task-or-terminal e866/review45d2, row metadata ccb26f62, payload overlap106d6ab9
and activation-SF state cleanup remain separate held proposals, not part of4cf2.
No native, numerical or timing outcome is claimed for the pending tight-row trial.


**Entry070 recovery interruption before execution.** The0909e devbox disappeared
before tight-row staging; the stage failed before remote mutation and no tight
compile ran. Managed c2/ziangli inventory showed no boxes/jobs across18 nodes.
Integration is requesting `fi-w4a16-mega-0910a` (request98013), explicit
`nvcr.io/nvidia/pytorch:26.05-py3`, B300×8/bare/no size. Root checked the live NGC
catalog and official26.08 support table to confirm26.05 as the latest CUDA13.2
image before this request. Replacement readiness, source, loaded toolchain and
native inventory are pending; oldd3ce is not a fresh-node cache claim.

The selected new-node sequence is exact published5152/sourcec267, one fresh
whole CLC BEFORE, then candidate4cf. Historical loop458e/proof0e2f stays a useful
reference, but the next primary comparison must use the new node's whole
baseline; no cross-node timing is presented as same-node evidence. The init
cleanup does not acquire an extra host/GPU validation cohort, and completed
host/default runs are not repeated for this recovery. All historical packages,
closed results and source identities remain preserved. Integration owns the
replacement request, transport and eventual GPU execution.


**Entry070 recovery completion and baseline-plan correction.** Request98013
returned ready on the same physical hu-pdx-115. The subsequent
[hardware continuity record](candidates/cuda132_recovery_0910a/hardware-continuity.json)
SHA `8e48214fdc300e6ac94bb8b4dada27456160479b12c780f4be5a6e3db6865fb5`
confirms all eight GPU UUIDs and driver, with matching recorded idle clocks
(120MHz SM/3996MHz memory) and1100W power limit. No clock-setting operation was
performed. Bootstrap57976/setup22690 and their fetches completed with exit zero.
[Stack continuity](candidates/cuda132_recovery_0910a/stack-continuity.json) SHA
`7df582c47007bbb7750e44bc86c491d3b2e802838db180192f070f456c9570ea`
records matching Torch/CUDA/DSL packages, loaded library bytes, nvcc, profilers,
launcher and device count against completed0909e.

These observations supersede the provisional fresh-node timing plan above:
reuse complete loop11ea result458e/proof0e2f as BEFORE on the same physical GPUs
and restored pinned stack, without adding a fresh baseline or repeating init,
host or default cohorts. The old loop remains its original measured source/run;
this is not a new baseline measurement or a timing-drift correction.

Published5152/c267 was restored with the sealed
[bootstrap5152 handoff](candidates/cuda132_recovery_0910a/bootstrap5152/handoff.json)
SHA `575dec1d994891cf1bdfb5fd1c493e897e11f4d8358d878cc35e573c94219501`.
The new [recovery delta](candidates/w4a16_central_refactor/tight_rows_validation/frozen_recovery0910a/delta.json)
SHA `dee6d6d9e3f3d39481c7529dabf709b5efe9f6e897ff7f64a6361887772515fc`
changes only the kernel fromc267 to4cf; its stage is6d36499c and target manifest
remains1f937b40. [Install receipt](logs/cu132-recovery0910a-tight-rows-install-001/receipt.json)
SHA `68eef661d8355fd090560dfeec23f4a57f1f7372c198b031a024533faae33438`
reports passed. Numerical and timing validation remain pending at this update.
The observed fresh cache inventoryf15fd1e7 contains only an empty diagnostic log;
historical d3ce native binaries were not restored or claimed present. Required
native builds and later inventories are recorded separately by integration.

The held task-or-terminal e866 proposal now has
[minimal unbound adapters](candidates/w4a16_central_refactor/task_or_terminal_validation/HANDOFF.md)
(helper mapd6a3da93): the same three CLC native fixtures, unchanged11/41 and whole
CLC8/AUTO13, exact run-only source association, and explicit future whole BEFORE
inputs. It remains separate from tight rows and has no runtime result. Existing
observer/oracle bytes and historical bundles are preserved.


**Entry070 native preparation completed.** The three actual4cf CLC native
fixtures completed on0910a, recorded in [native summary](candidates/w4a16_central_refactor/tight_rows_validation/execution/native-summary.json)
SHA `4db560e1330107d6468fe55cc5a0a40eeb6bcd8761feeac23f234b3cadcc93f7`.
All nine dispatch/compute/finish roles match their actual central controls in
SASS/disassembly/encodings and resource values. Small C1 compute grid.z remains
148; N64 C2 shrinks9216→1520 and N128 C2 shrinks5120→1008. Fixed transport grids,
blocks and cluster shapes are unchanged. These are compile/codegen observations,
not numerical or timing results. The original missing run_cached_stack_retry.py
staging dependency failed before compilation; its exact helper was added before
the successful captures. Later close_native.py entrypoint staging was also
repaired without recompiling the captures.

The [transport association](candidates/w4a16_central_refactor/tight_rows_validation/execution/transport-association-4cf-0910a.json)
SHA `5e379f73247e930f08862f9ef11d4a79c7a193d987f314cdd92ea67f9c3e5087`
consumes the exact init identity proof, reviewed kernel delta, three actual
native comparisons and six original capacity receipts. Its existing pure loader
passed once (check069e4749); no original numerical validator ran during binding.

The [native dependency completion](logs/cu132-recovery0910a-native-dependencies-001/completion.json)
SHA `55b0c7364e75142956b1ce4be10c46380fb321f159e8889ad5f069f1867b9894`
records the existing `gen_fp4_quantization_sm103_module().build_and_load()` and
`gen_dsv3_fused_routing_module().build_and_load()` entrypoints only, with zero
tensor operations/kernel calls. The resulting22-record inventory38a68fe8 is a
fresh build: object/library sizes match historical entries but binary hashes
differ. It is not the oldd3ce cache. The unchanged numerical driver will use the
actual observed inventory; no extra warmup/test or timing cohort was added.
Unchanged11/41 and wholeCLC8/AUTO13 remain pending at this update.

[Skip-empty ownership](candidates/w4a16_configurable_clc/central_refactor_followups/skip_empty_ownership/README.md)
is a separate held source proposal, patch
`eceefc318d7d2d1cc03b495799d6528dfc0a318ea7f2df2d1a8832bd70031484`,
with [independent source review](candidates/w4a16_configurable_clc/central_refactor_followups/skip_empty_ownership/INDEPENDENT_REVIEW.md)
SHA `2329fe07d3f5c6fa2bc47e4de6ac0ac12bc8782e14dd725bd2c412a2f993c3cf`.
It is not part of4cf, has not run, and carries no performance claim. Task-or-terminal,
row metadata, payload overlap and activation-SF cleanup likewise remain separate.


Public CI readback for published5152 reports pre-commit and BuildDocs passed.
GPU setup/matrix is skipped;
[Test Results Summary](https://github.com/flashinfer-ai/flashinfer/actions/runs/34452838892/job/102792347308)
says “CI skipped — pending authorization.” No GPU-test failure was observed and
no bot comment/label/run was requested. This does not change the active devbox
validation or claim an additional cleanup/GPU cohort. CodeRabbit
explicitly did not review the draft; no human review is recorded. Successful bot
workflow status is not kernel-review approval.


**Entry070 numerical completion and benchmark observer repair.** The unchanged
four numerical jobs passed on source4cf: C1/S2 EP1 both returns 2 passed
(45.59s), N64/C2 EP2 both returns 2 passed per rank (61.17s/61.52s),
N128/C2 EP2 both returns 2 passed per rank (71.61s/70.24s), and C1/S3 graph
1 passed (17.97s). This totals11 rank tests and41 compiled compute objects.
All41 compute objects report REG96/640 threads/two decode WGs/LOCAL0; all123
dispatch/compute/finish records report LOCAL0. Oracles and tolerances are
unchanged. [Numerical/source/native/idle closure](logs/cu132-recovery0909e-central-tight-rows-numerical-full-001-idle.json)
SHA310c8b7d passed; fresh native inventory38a68fe8 is unchanged. An initial
preworker failure for missing saved capacity JSONs was repaired by restoring
the exact six receipts, without rerunning those capacity tests.

Whole CLC AUTO001 failed after50.827697s during the first global-T1 warmup:
all eight candidate preparations encountered default-Mega storage accounting
in the copied helper. [Failure receipt](candidates/w4a16_central_refactor/tight_rows_validation/execution/auto-failure001.json)
SHA03875590 preserves the original worker/log/source/native/idle evidence.
Workers, NCCL/NVSHMEM and input preparation ran, but no timing row or successful
Mega compiled-resource/launch record was produced. Source4cf/native38a68 did
not change. This is a benchmark observer failure, not a numerical kernel failure.

The [fresh002 package](candidates/w4a16_central_refactor/tight_rows_validation/execution/auto-retry002-preparation.json)
restores the actual completed CLC lineage: returned-storage observer97b3bb0c
(b9f68577 plus only the central token_comm storage accessor), three-role resource
querycc826116 and CLC saved checks288896f0. The other ten performance helper
bodies are byte-exact. Stage504a1ec5 and pure reader load6c8c2687 passed; original
11886 runs the unchanged whole13/CLC8/AUTO100 measurement as attempt002. Native
and11/41 are not repeated. Attempt001 and its original helpers remain immutable.
The task-or-terminal future package is separately corrected using fresh unbound
map38603d81; earlier maps are preserved and superseded for future CLC execution.
No performance retention decision has been made at this update.


**Entry070 full AUTO closure and retention.** Retry002 original11886, closure11553
and fetch10017 completed with exit zero. Saved reconstruction67a27f2b/result89420688
checks13 rows,104 compiled records,13×8 rankings and1,300 samples. Source4cf and
native38a68 remained exact; idle closure0f0dbdff passed. Process603.333211s versus
618.699863s for the reused complete loop11ea BEFORE.

[Complete comparison](logs/cu132-recovery0910a-loop-vs-tight-rows-independent-comparison-002/README.md)
SHA2bcf7da8:8–4096 latency GM−0.910432714%,6/10 lower; full13−0.844123468%,9/13 lower.
The largest regression is512 at+1.341%;4096 improves3.103%. These are independently
autotuned complete columns, not fixed-tactic causality or selected minima.
All1/2/4 rows remain visible but do not decide retention. Retain the clean host
launch estimate with full skew capacity, unchanged native code/resources and
passed numerics. Commit16b7170fe793825ba07cf0f521f4745902c8cc1d is pushed; commit
hooks (including mypy/Ruff) passed. [Retention receipt](candidates/w4a16_central_refactor/tight_rows_validation/execution/retention.json).

AUTO cache inspection found no saved host-grid IR: the per-run CUTE cache was
empty and the fresh driver cache held24 binaries. Native fixtures directly
observe reduced launch grids; AUTO binds current source/fresh caches but is not
a direct grid trace. No extra capture/compile was added to fill this diagnostic
boundary. CLC remains slower than default and outside its catalog. The entire
Final performance PR section remains unchanged at owned098c, including26
CUDA13.2/13.0 numeric rows. PR draft/head16b/bodybf1e7fa7 was verified after the
validation/implementation update, with no comment or review posted.

## Entry071 — One CLC task-or-terminal broadcast

The separate reviewed e8662a2a patch changes only maintained clc.py run(): a
successful FC2 pop is always published, including the final task; an unsuccessful
pop may publish terminal−2. The single task/terminal broadcast replaces two.
Claim drain, epilogue completion, DONE and fixed finish retain their order.
Primary was updated before staging, atop retained16b/source4cf. Frozen source
85a1d65167110936c92662116613cd622bfa28f1d523d8a59cf404e72b21d08c is at
[candidates/w4a16_central_refactor/task_or_terminal_validation/frozen](candidates/w4a16_central_refactor/task_or_terminal_validation/frozen/),
manifest77e6f1ed/deltae783c29d/stage96450b5a. It uses corrected map38603d81 and
whole tight002 BEFORE proof67a27f2b/result89420688. Initial staging only needed
the declaration path rebound to the already-present identical1f937 recovery
manifest; no payload/source change. Install12862 and preflight48127 passed;
three native fixtures original48749 are running on0910a. Unchanged11/41 and
whole CLC8/AUTO13 follow on passing native/resource checks. No result is yet
claimed and no default/split/cleanup cohort is added.

A separate held query/claim-overlap candidate2130620b is based on proposed
task-or-terminal882d. It issues the existing single-slot CLC query after the
nonterminal task broadcast, before publishing an independent ready FC2 claim,
then consumes the response as before. No extra query/slot/decoded bundle state
or public knob. Source-only checks passed; native/numerical/performance outcomes
are untested. Skip-empty ownership, row metadata and payload overlap remain
separate. A bounded read-only full-PR scope audit found no further unrelated
removal or vendor drift and recommended no additional cleanup.


**Iteration cost from the completed tight002 samples.** Saved rank-zero
`bench_gpu_time` wall metadata sums to6.601327s across all13 primary timing
calls, or1.094% of the603.333211s subprocess.
[Arithmetic-only accounting](logs/cu132-recovery0910a-loop-vs-tight-rows-independent-comparison-002/timer-wall-accounting.json)
reads the already validated result89420688; no timer/validator rerun. Remaining
process time is not decomposed into compilation, setup and tuning by this
observation. Reducing primary samples cannot remove more than the measured
6.6s of primary-timer scope, so keep100 samples/full13 and prioritize baseline
reuse and dependency preparation.


**Entry071 native/numerical completion, then user cancellation.** Three85a1 native
fixtures compiled with40/48/40 fewer instructions, unchanged REG96/640/LOCAL0
and exact dispatch/finish roles. Independent native review found successful
FC2 tasks survive termination, query/failure/tail protocol remains paired, and
decode/MMA/BF16 arithmetic encodings remain identical. Unchanged11/41 passed:
C1/S2 2passed44.14s; N64/EP2 2passed56.31s and55.25s; N128/EP2
2passed68.04s and66.63s; C1/S3 graph1passed18.21s. Numerical closurefc48f590
passed with source85a1/native38a68 exact.

At the user's subsequent explicit request, all CLC work was cancelled and its
implementation selected for removal, since even the improved whole CLC baseline
is substantially slower than the existing atomic-counter path. AUTO55672 was
stopped by SIGTERM to its verified owned torchrun30932, exited1 at124.915s, and
produced onlyT1/T2 rows. No full reconstruction/comparison/retention is claimed.
Cancellation closure104fc649 and fetch1491/receipt3a6d446d preserve source/native
evidence and confirm the GPU is idle. Query/claim overlap, skip-empty, row
metadata, payload overlap and bundle trials are archived, not pending runs.
All local helpers/logs/profiles remain intact.

## Entry072 — Remove optional CLC, retain static/atomic scheduling

The user requested a separate removal commit to reduce PR scope and retain CLC
through Git history for future reference. Primary removal deletes clc.py and
clc_transport.py, removes CLC mode/bundle/config/key/workspace/queue/epilogue
plumbing and its numerical/host tests, and inlines the unnecessary _compute_body
wrapper into the default kernel. Static/atomic paths, tolerances and unrelated
repository code are preserved. The inherited split-W4A16 layout method's
use_clc_scheduler parameter and the requiredFalse constructor argument remain;
they are generic parent ABI, not MegaCLC support. Current diff is about1,100
net lines removed across nine files. Ruff checks/format and diffcheck passed.
Retained default host/native/numerical validation is next, with no full timing
rerun for this cleanup. Default full57e2 is the primary BEFORE for the next
performance decision; owned098c remains the published whole-best table.

A new, separate default-only direction is under source review: omit BAR1 after
nonterminal direct-epi FC2 work, retaining it for FC1, reused-dispatch return and
terminal NEXT/TMEM free. This will not be combined into the removal commit and
has no native/numerical/performance result yet.


Entry072 completion: separate removal commit8d7718c9a6c76e5722e1cf201395b0df538b081e
is pushed. Parent16b7170fe retains the CLC implementation. Final scope is9 files,
+69/−1162, net1,093 fewer lines; no vendor/shared decoder/other-dtype edits.
Sourceeb036705ebe71f940bf567c94fdcb78020a5fdc21bdeb3e7ea361cc1d140a09d
matches all1,582 inventoried primary files. Host135 passed/2warnings/4.14s.
Default N64/N128 native instructions and both encoded words match central57e2
exactly (5,504/6,032); REG96,640threads,STACK0,LOCAL0 and allocations unchanged.
EP2 numerical selection passed8 rank-tests/32 objects (both geometries and return
modes), allREG96/640/two decode WGs/LOCAL0. Raw rank lines: N64 2passed61.66s,
2passed61.99s; N128 2passed65.66s,2passed65.27s. Existing numerical/oracle/tolerance
bodies unchanged. Native/source/idle closured15d65756086f63b04ad28eae672416655134d438364e6fbab1f08549ca2e0eb;
see candidates/w4a16_clc_removal/execution/VALIDATION.md and numerical-summary.json.
Commit-time hooks including mypy/Ruff pass. No default/full/split timing rerun.
PR bodyc4456a0673bd526808256bbfdcaa3a04615d0be5470d03c6a64b7f6bdad2076f
was published/read back at draft/head8d7718; entire Final performance unchanged.

## Entry073 — Nonterminal direct-FC2 epilogue barrier

Applied the independently reviewed source-only +6/−1 epilogue patch988e57ec
in primary after the separate removal commit. Existing constexpr dispatch return
retains unconditional BAR1. Direct return keeps BAR1 after every FC1 and terminal
NEXT, skipping only intermediate FC2. No new knob, pipeline, stage, role or storage.
FC1 publication, direct-FC2 null tracker, per-warp stores and all accumulator
releases remain ordered; terminal rendezvous still protects warp0 TMEM free.
Source-only checks and independent reviewd80b1297 are under
candidates/w4a16_fc2_nonterminal_barrier/. Fresh native, default8/32 numerical and
whole13/default8/AUTO100 are next; no gain or retention decision yet. Primary
BEFORE remains the complete central57e2 default run0c19/proofd56d, and owned098c
result490b/proof9d6b is a separate whole-best comparison. Reuse saved columns;
no split or fresh baseline, no row splicing, retention uses8–4096.


Entry073 completion: **not retained**. Native lowering is the intended predicated
BAR1 (N64@!P1/0xb930, N128@!P0/0xdb10), with REG96/640/STACK0/LOCAL0;
independent native review8550ee28. Existing8 rank-tests/32 objects pass, allcompute
LOCAL0; numerical closure95853757. Full13/default8/AUTO100 original20783,
idle10180,fetch81467 alltrue0; result45f6f6ef816e15c6a983070422d61107ca649d35a4a731ee6b724a61f269e249,
proof1cba9bae288d9ed582fe04ee79da0b94420e8d4d9f7483908b2acdc0207999b9,
comparison d6dd21d3, idle0079bbb4. 13rows/104records/13×8rankings/1300samples;
wall578.813056s; selected11epi/2reuse(2048,4096).
Full latest-default57e2 comparison:8+ latencyGM+0.5730895%,5/10lower;
all13secondary−0.9300053%,7/13lower. Separatebest098c:8+GM+2.0190880%,4/10lower;
all13secondary+1.811534%,6/13lower. See both complete13-row tables at
logs/cu132-recovery0910a-fc2-nonterminal-barrier-independent-comparison-001/README.md.
No rows were substituted and no baseline/split run or old validator was repeated.
The excluded1/2/4 improvements do not determine retention. No native/resource or
correctness defect explains this result; the clean implementation did not show
an end-to-end gain under the fixed full protocol. Primary reversed only988e57ec
after verifying the exactb73f source, restoring clean8d7718/sourceeb036 (all1582
source hashes exact). Remote reverse installation is separate and pending. No
performance commit or public table change; detailed candidate/results preserved.
Next: full NCU on retained direct-epiT1024/N64/F4/S2 with actual source/PC wait
attribution, using the prepared w4a16_direct_epi_profiles handoff. No next kernel
change is justified solely by the bounded source audit; use measured waits.


Entry073 restoration complete: reverse stage2386, install41018 and closure39585
alltrue0; receipt3f611edb and closure12435a4c confirm exacteb036/native38a68,
no GPU workers. Download59989 passed. No numerical, native compile or timing
rerun for restoration. Candidate RESULT.md records the final unretained state.

## Entry074 — Full NCU on retained direct epilogue

Launched original90579 after stage28886 on exact retained sourceeb036, published
8d7718c9a, same0910a CUDA13.2/B300 hardware and native stack. Bound evidence
7f15dcc2 under candidates/w4a16_direct_epi_profiles pins restoration12435a4c,
source/preflight/native and rejected-trial chronology. Workload is globalT1024
(128 per rank), EP8/H7168/I2048/E256/topk8/N64/F4/epi/S2/group512/epiflags2,4,
matching the T1024 dictionary in both complete default controls. This intentionally
uses retainedF4, not rejected7c's selectedF8. Full --set=full/no metric filter,
coordinated8-peer application replay, one profile invocation after3warmups;
warp sampling bound1 does not limit overall replay passes. Output is
profiles/direct-epi-0910a-ncu-full-t1024-001. Capture is in flight, not yet verified.
The full-reader/CSV and per-PC/source/SASS ranking helpers are prepared; do not
conflate generic installed section/metric estimates with actual report coverage.
Followups depend on mapped actual wait sites and keep instrumented durations
separate from AUTO latency. A bounded history/source audit identifies FC1
completion batching2→1 as not independently tested in the current default;
old sweeps coupled schedule and transport. This is a diagnostic hypothesis only,
with no code change or new autotune axis. The readiness dependency remains needed.


Entry074 completion: original90579 exited0 after all eight peers completed40
replay passes. Closure38794 passed, saved as70ca8599 under
profiles/direct-epi-0910a-ncu-full-closure-001: sourceeb036/db4a and native38a68
exact, no additions, GPU idle. Read-only idle SM120MHz/memory3996MHz/power1100W
matches prior state. Raw fetch5521 completed; all reports have verified SHA,
size and NVR header. Archive5d4c542ad5ee62b81dc78f12fb055c421fa2c5e2abce5704a08e80c76a77f6fc
is36,594,582 bytes. All API/CSV/PC/SASS export originals passed; analysis fetch23557
passed. Each report has2,472 names,14 rendered sections includingSourceCounters,
40 replay passes; PC sampling aggregatepasses2 is a separate measure. The same
six unavailable C2C warnings remain. Reports contain96registers/640threads/
200064dynamicshared and no dropped PC-sampling bytes/overflow. Exports are under
profiles/direct-epi-0910a-ncu-full-analysis; full-report-verification and CSV
artifacts are beside the raw reports.

ActualT1024 SASS attribution finds no sampled FC2 counter poll in0x5680–0x5700
on any rank. The sole rank7 source-tagged sample is address setup0x5620. MMA
accumulator-empty and decoded-full cold loops likewise have zero samples;
activation-full cold-loop counts are[0,40,64,0,37,21,34,74] byrank. Dominant
metadata waits at0x14120/0x146b0 belong to first work-record consumption by
decode WGs/epilogue, not operand readiness. Total samples vary13,591–3,168,470
across ranks, with replay durations0.208096–64.954560ms; these are diagnostic
replay observations, not AUTO times or stable per-stage stall percentages.
Detailed ownership review is being saved separately.

Decision: keep the reviewed FC1 batch1 patch949831e6 and its held validation
adapters unrun; this capture does not support its readiness-delay hypothesis.
The separate atomic preclaim proposal is next source work. Current SASS places
record publication and cluster-slot acquire before the next atomic, then adds
an internal result-consuming shuffle/IMAD/reconvergence before the explicit
shuffle. A source-only move is insufficient; implementation must delay the
first native result use to create overlap. No new queue, tactic axis, CLC,
shared operand release or primary source change is included at this point.


## Entry075 — Atomic next-claim overlap

Source-driven trial on retainedeb036: issue the next leader-lane scalar atomic
before blocking on current scheduler-record publication, then first use/shuffle
it after publication and the existing cluster broadcast-slot acquire. A narrow
predicated inline-PTX operation defines inactive-lane results without the old
high-level result-yield branch. No queue, public option, serialized state,
scheduler-stage count, role, decode, data layout or numerical operation changes.
First pre-init cached claim and static traversal are unchanged. Current valid
work still publishes before the next descriptor is decoded; terminal publication
and cluster pipeline participants/phases remain intact. Earlier reservation may
reduce balancing flexibility; timing must decide retention.

Existing native code put the atomic after record publication/cluster-slot wait,
and ptxas added an internal dependent shuffle/IMAD/reconvergence before the
explicit shuffle. Therefore merely moving the high-level call is insufficient.
Required native review: actual atomic precedes current-record wait/publication,
no dependent result use closes the intended overlap window, broadcasts/claims
remain correct, and register/stack/local resource limits remain retained.
ActualT1024 PC evidence is dominated by INITIAL work-record/replay waits; it does
not establish a steady scheduler bottleneck. Batch1 is held and not combined.

Patchc4df1e4dec5b9088fdddd6c0990da5b07f02073d78005cd84e2902d77037a4c9
passed author parse/Ruff/format/apply checks and independent review53ac9cd5.
Root applied it to the primary checkout and froze the actual full inventory:
sourceca2328e9fe421f684b01f0b6e6d86f8efe711ccdbe20db7619e856d3d0d9e563,
manifest26697b5368dfa513b8ced6e10059b2eff35c88ee8742f9a5ed86ee0df70f04fd,
delta76ec1e05881623974e0280a936ba9a05a1a2349b82a4bd9417c83af9fcd5c5a0,
stagea459d0c10f03d4f27f2f6ea0403539a46bc06de05f2e8d2dcb41a6ce0f76826d.
Two files,+61/−16; scheduler eefefaab/kernel140b147e. Separate removal commit8d7718
remains HEAD. Integration owns pending native2; original8/32 numerics and the
full13/default8/AUTO100 follow only after native review. Pair2,4 and timing/scorer
remain unchanged. Primary BEFORE is whole57e2; separate whole-best098c stays
independent, with no fresh baseline/split run. No result is yet claimed.


Entry075 first-native quality result: install29632/runtime14470/preflight71967
passed; receiptf0574b68/preflight49c055a3. Native10322 completed both captures
with one compile/zero launches, REG96/640/STACK0/LOCAL0, unchanged grid/stages/
SMEM and5504/6032 instructions. Downloads34270/12602 passed. Independent native
review4cd8de92 and validatione4b1ea65 identify failure of the intended overlap:
N64 ATOMG28e0 → SHFL2920 → IMAD2930 → BSYNC2950 precedes record wait2960 and
publication2a00; N128 similarly28a0→28e0→28f0→2910 before wait2920/commit29c0.
The implicit SHFL's encoded wait mask0x4 consumes the atomic write barrier2.
PTX source delays the result, but ptxas aggregation closes the window and now
also delays current-record publication. No correctness/count defect was found.
Closure12443/55ad3358 and fetch21090 passed, sourceca2328/native38a68/idle exact.
No numerical or AUTO run was started; this is a native-quality failure, not a
performance result. Preserve the original candidate and fix the lowering before
evaluating the direction.

Refinement799c5383 in fresh candidates/w4a16_atomic_preclaim_inc changes only
the predicated asm ADD1 to INC0xffffffff plus intent comments. The official PTX
atom semantics return the old value and define inc(r,s)=(r>=s)?0:r+1, so at
s=0xffffffff this preserves unsigned32 addition's complete wraparound domain:
https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-atom
This mathematical equivalence does not establish better lowering. The compiler
may still canonicalize/aggregate the operation; actual native first use remains
required. Predication, inactive zero, operands, scope, pipeline and kernel are
unchanged. Root reviewed/applied/froze the actual refinement: source8336b16d3e24afcfdb641ecc77613df08586f9930929eff75d7a58716b89274e,
manifestf450433682f9ec600cd6133cd2d316bbf4308a40ce0c015aa910b71189111e8e,
deltafad2e88aa5cdd27419a943a0e7c0f27d8db9be15f287021562056358b5835281,
stage08995e6ee10c3fad55e893bd9d99993c5b255e0a0238d5fb54375c83f6c2c272.
Integration is proceeding native2 only with reused helpers and fresh source/
output bindings; numerical/AUTO remain held. No host repeat or new test matrix.


Entry075 INC native outcome: source install57686/preflight63005 and native99541
passed; preflight3cb2851e/install38d97edd. Fetch15740/10298 passed. Both new
captures contain the actual INC PTX and bound scheduler a79ec4ae, yet match the
failed ADD proposal's full SASS exactly: all5504/6032 instructions and both
encoded words, including scheduling bits. REG96/640/STACK0/LOCAL0 and all other
resources remain unchanged. Native validation23cef6f7 and original saved-parser
comparison JSONs preserve this compiler result. Closure94903/fetch36380 passed,
closurec1514c50 source8336/native38a68/idle exact. No numerical or AUTO run.

The next refinement uses the existing elect.sync single-issuer pattern, carrying
the actual elected lane to a later shuffle; no lane0-election assumption or
synthetic limit is allowed. Official PTX elect.sync returns the selected lane,
requires executing threads belong to the member mask, and elects deterministically
for a given mask; full-warp participation here is uniform. Source design is under
candidates/w4a16_atomic_preclaim_elect; no applied elect code or compile claim yet.


Entry075 ELECT source refinement: the full scheduler warp elects one issuer,
ANDs that predicate with leaderCTA, issues the original ADD1 directly into a
lane-local output, and returns its actual elected source lane separately. Neither
a lane0 election nor eager atomic-result shuffle is assumed. Both local scalars
reach one common shuffle after publication and cluster-slot acquisition; the
fallback supplies source lane0 at compile time. No state field/queue/public knob.
Original first preclaim/cache/static/DONE and participant/phase behavior remain
unchanged. Bounded existing-code search found source election and multioutput
userop patterns but no verified elected returning-atomic native precedent;
actual compiler output remains required.

Author checks and independent source review found no issue, including multioutput
operand aliasing and full-mask participation. Root applied exactpatch
ba51996a17241747a2b2b5df13ad2eac5a2e365ff908f6de68fe645709050b88 and froze actual
sourceef43bf0fd928f6eaf3c35c5997cd8089efc8b1e3d93c0afb6b3248a4d5cfd5ef,
manifest31fa4fb2431ecc4c422f38d7288223ea84077bab4c5db8b4a174141adc5816ae,
deltab7c78f83fd308993318f67b0a30cd3acd5151ef7d142a564000f00258b802721,
stage2a50fb99305326c08c72d0275ebb998e98cfd39ce5dff8dd53d95ac67e3534fb.
Scheduler3bacac6c/kernel271420e0; the separate CLC-removal HEAD remains8d7718.
Integration proceeds native2 only with existing helpers/fresh source/output
bindings. Both failed prior native variants remain immutable and unbenchmarked.


Entry075 ELECT native/numerical closure: both native captures pass the actual
machine-code ordering. N64 claim28b0 precedes record-empty wait28e0 and
publication29a0; first result SHFL2a10 is after cluster acquire29e0. N128
claim2870 precedes wait28a0/publication2960; first result SHFL29d0 is after
cluster acquire29a0. Atomic write barrier5 is consumed with wait mask0x20 at
that delayed shuffle, not before publication. Pointer read-barrier1 waits are
separate. Earlier VOTEU/POPC/FLO/internal-SHFL aggregation is absent. Native
instructions decrease8 padded/six non-NOP per geometry (5496/6024) with exact
REG96/640/STACK0/LOCAL0/grid/stages/SMEM. Native closurea9444b31 confirms
sourceef43/native38a68 and idle. This establishes an overlap window, not speedup.

Original numerical66516 and closure97054/fetch31556 completed successfully:
eight EP2 rank tests/32 objects, both N64/N128 and both return modes, unchanged
scale/routing/tail/graph oracles and tolerances. All observed objects retain
96 registers/640 threads/two decode WGs/LOCAL0/S2. Closure0963a11b binds exact
sourceef43/native38a68 and idle. Existing full default13/catalog8/AUTO100 is
active under original56333, run cu132-recovery0910a-atomic-preclaim-elect-default-auto13-direct-001.
Effective epilogue flags2,4; no baseline/split rerun. Whole57e2 primary and
whole098c separate comparisons follow complete closure; retention uses8–4096.


Entry075 full ELECT AUTO complete and rejected: original56333 true exit0,
589.757506s; closure91890/fetch54715 true0. Closure199f8f19 binds exactsourceef43,
unchangednative38a68 and idle. Existing saved reader ran once and verifies13 rows,
104 selected objects/13×8 hot rankings/1300 primary samples. Result37d047c3 and
proof06da025a; full tables and comparison2ddb0431 under
logs/cu132-recovery0910a-atomic-preclaim-elect-independent-comparison-001/.
Primary whole57e2: +2.379625% latency GM8–4096,3/10 lower (all13+1.297238%).
Separate whole-best098c: +3.851597%,2/10 lower (all13+4.100411%). No row splicing,
baseline/split rerun, timing/scorer change or partial-row retention. Numerical
and native quality pass, but the actual overlap does not deliver end-to-end gain.
Reject and preserve all source/native/numerical/timing artifacts; root restored
only scheduler+kernel to exactHEAD8d, clean primary. Integration owns remote
reverse overlay and source/native/idle closure, with no tests/timing rerun.

PR profiling-only update is published and read back OPEN/draft/head8d:
bodyb4959ceb, receiptlogs/pr5019-profiling-after-body-edit-001.json. It adds the
retained8d T1024/N64 fullNCU source/command/coverage/attribution beside historical
056ce T4096NCU+NSYS. Every byte outside Profiling scope, including the complete
Final performance section, is unchanged. No rejected-trial performance inPR.

Entry075 restoration closed: stage97501/install73972/closure58707 and both
fetches71178/96441 exited0. Exact retainedeb036/db4a restored with only the
scheduler and kernel reversal; native38a68 unchanged, GPUs/native workers idle.
Receiptbb47edf9; closure561691e5. No compile/test/benchmark reruns. All failed
and rejected source/native/numerical/timing packages remain preserved.


### Entry076 — move the tail system fence after TMEM deallocation

**Status: native/numerical/full AUTO complete; rejected and restoring retained source.**

The source proposal is in `candidates/w4a16_epilogue_tail_fence_after_free/`.
Move the existing system fence after allocator-permit relinquish and TMEM free,
while keeping it before the common CTA/rank tail. This matches the existing
BF16 MegaMoE order. It moves one statement (+1/−1), with no additional knob,
branch, participant, interface, shape specialization, or vendor change.

The potential gain is overlapping outstanding output stores with TMEM release
and the peer-CTA deallocation rendezvous. The allocator interval uses shared
allocator state and TMEM operations, with no output-store/counter dependency.
All four epilogue warps still execute the system fence for both return modes.
Final TMEM load fences, accumulator releases and the 128-thread terminal
rendezvous remain ahead of deallocation; direct peer-store visibility still has
its system fence before the common tail. Complete fence elision is unproven and
held. The earlier tail-scope experiment only relocated the original three
statements while preserving their order; this experiment changes their order.
The source proof and its BF16/CUTLASS references are in the proposal README.

**Applied source and freeze:** root verified the exact base, patch and proposed
bytes, applied the change in the primary inspection checkout, and passed parse
and diff checks. HEAD remains the separate CLC-removal commit `8d7718c9a`.

- Patch: `bd48468216901aafdd3247bd8483163c03071ca433fad79246a4b052fd71a4f5`.
- Kernel before: `5d6d7c6c5a4265b98feef5603ad215909dd60262fae628878dcc89f154786fab`.
- Kernel after: `b6ba2019e2197246509c23c8ce3f74ab3fd07d0506b977142dac3a943e2e8d6f`.
- Complete source: `d88c380d2459fa520314b9ade12fe6ecf387cebc615db662fb08e6f989beedc5`.
- Manifest: `62504dfee4a36bf0f526aa977e6fa930f2cf3e01d542417c614d429cf220c0b0`.
- Delta: `f490a61d7b8123981b836fc64b05c47ebe92a96ab25fa85124e47133875b88ab`.
- Stage: `92b2d12223097de547876fef6e5f8151070606ead55a8e2e58c50e10628ed5c5`.

The freeze is under `candidates/w4a16_tail_fence_after_tmem/frozen/`. The
existing freezer checks the complete inventory and sole changed kernel; no
helper changes or deletions. Native/numerical/performance Python helpers are
reused exactly, with fresh output paths and saved-reader run bindings. No new
validation layer, baseline, split run or profile capture was added.

**Native quality:** stage 22768, install 55204 and preflight 41298 passed
(preflight `ec87aba3`, receipt `ab87f37f`). Native 96145 and downloads 40521/52162
exited zero. Each direct-epilogue fixture compiled once and launched zero times.
N64/N128 retain 5,504/6,032 instructions and unchanged opcode counts, REG96,
640 threads, STACK0/LOCAL0, dynamic shared memory 200,064/230,784 bytes and grid
`[2,1,74]`. Actual N64 ordering is UVIRT `bd50`, peer arrive/wait `bdb0/bdc0`,
UTC deallocation `bf60`, then CTA/system fences `c030/c040`; nonallocator warps
branch from `bce0` to `c030`. N128 has `df50`, `dfb0/dfc0`, `e160`, then
`e230/e240`, with nonallocator branch `dee0` to `e230`. Every epilogue warp
reaches the retained fence before common NB8. Closure 98348, SHA `e7956909`,
confirms exact source, unchanged native inventory `38a68` and idle GPUs/workers.
These are two direct-return native fixtures; source proof and numerics cover
both return modes. Native ordering establishes an opportunity, not speedup.

**Numerics:** original 4143, closure 66820 and fetch 88173 passed the unchanged
8 EP2 rank tests / 32 compiled objects across N64/N128 and both return modes.
Completion `013134923254c1a2fd79818b56829fdc0420273be6efba6a39507efcf78f531d`
binds exact source `d88c`, unchanged native inventory `38a68` and idle GPUs.
No oracle, tolerance or test matrix was changed.

**Completed performance:** original session 61214 ran
`cu132-recovery0910a-tail-fence-after-tmem-default-auto13-direct-001` with all
13 token rows, the original eight-tactic catalog and 100 primary samples per
row. Effective epilogue flags remain `(2,4)`; timer, scorer and inputs are
unchanged. The complete saved `57e2` run is the primary BEFORE; complete `098c`
is a separate retained-best comparison. Retention uses 8–4096 tokens; 1/2/4
remain reported. The completed comparison and decision follow below.

**Iteration-cost audit (saved ELECT run, protocol unchanged):**
[ITERATION_COST_AUDIT.md](candidates/w4a16_atomic_preclaim_elect/execution/ITERATION_COST_AUDIT.md)
(SHA `108e7e9453b96e8dac2ed9d043b382362073e9764dd8f5dbd8b81986194d58f3`)
finds 5.949343 seconds in the thirteen explicitly logged rank0 final
`bench_gpu_time` scopes, only 1.009% of the 589.757506-second process wall.
The 1,300 per-iteration rank-MAX GPU spans sum to 0.729769 seconds, a different
quantity from process time. The remaining process time is outside those rank0
scopes, not an exact measure of compilation or CPU overhead; existing phase
markers lack separate timestamps. Reducing the final 100 samples is therefore
unlikely to save minutes. Keep the protocol; no parser/scorer/validator or GPU
execution was repeated for this arithmetic-only audit.

**Entry076 completed decision:** AUTO 61214, closure 60351 and download 11766
all exited zero. The original saved reader ran once and verified all 13 rows,
104 selected objects, 13×8 rankings and 1,300 primary samples. Process wall:
586.984 seconds (12:20:36–12:30:23 UTC). Result `27aed5cb`, proof `50bc733e`,
comparison `11860643`, and source/native/idle closure `0c59b40b` are preserved.
Full rows and selectors are in
`logs/cu132-recovery0910a-tail-fence-after-tmem-independent-comparison-001/`.
Only inherited Markdown labels are being corrected; original generated text
and numeric/proof artifacts remain unchanged.

Against primary whole57e2, 8–4096 latency GM increased 2.023030% (1/10 rows
lower); all13 increased 2.937780%. Against separate whole098c, 8–4096 increased
3.489875% (2/10 lower); all13 increased 5.786351%. Reject the reorder despite
correct native ordering and numerical results. Root restored the sole kernel
to exact HEAD8d with clean primary status; integration owns remote reversal
and source/native/idle closure. No benchmark, test, profiler or validator is
repeated for restoration. Final PR performance remains the retained whole run.

**Entry076 restoration closed:** stage 37459, install 2254, closure 3029 and
both downloads exited zero. Receipt `4075d3d4` / closure `b9fdc28b` confirm the
exact one-kernel reversal to source eb036/db4a, unchanged native38a68 and idle
GPUs/workers. The numeric/proof artifacts remain unchanged. Corrected human
comparison README `e83cb525` labels this trial Tail fence reorder; original
README `73c80c88` is preserved as `README.generated.md`.

### Entry077 — remove the empty FC1 bulk-copy group

**Status: source reviewed and applied; native checks pending.**

The current W4A16 epilogue writes FC1 and FC2 outputs with ordinary BF16 STG.
Its four warps do not issue bulk-group producers, so the inherited FC1 bulk
commit/read-wait pair operates on an empty per-thread group. Remove that block
and the adjacent stale commented-out fence: five deleted lines, no new branch,
knob, interface, specialization or vendor change. Keep next-work/phase order,
BAR1, TMEM fences/releases, GPU-release flags and the real dispatch drains.
Source and saved current native proof are in
`candidates/w4a16_fc1_empty_bulk_drain/README.md`.

Root separately checked the current PTX specification: bulk commit collects
eligible operations initiated by the executing thread, and without them creates
an empty group. Ordinary STG and other warps' copies are not group members.
https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-commit-group
The real transport bulk groups are issued/drained by dispatch warps8–11; TMA
weight/input loads use mbarrier completion in different warps. Their code stays
unchanged. Removing the empty wait does not remove the ordinary-STG completion
ordering supplied by the retained barrier and release/acquire flag path.

The bounded history search found an earlier private 512-thread native proposal
(−8 instructions per geometry) and an unstaged e9a725 runtime adapter, but no
completed numerical or performance run or rejection. This is a new trial of
the current 640-thread implementation; those old artifacts are not new evidence.

- Base HEAD: `8d7718c9a6c76e5722e1cf201395b0df538b081e`, source eb036.
- Patch: `1f90695c17f20592a97b49b0afea1c2afe98042b69e2b5857cb71ba12c13c29b`.
- Epilogue before: `6026bd7a265c4be5e273c4c1af2cbe62dd4eda132ef0944b1f4f70489e69bfde`.
- Epilogue after: `ee769bd01526a728cd582643337c649e53e608f3f8dfeb4dc5ba85196a0f2170`.
- Kernel remains `5d6d7c6c`; rejected tail-fence and ELECT changes are absent.

Root verified exact base/patch/proposed bytes, applied the five-line deletion
in the primary inspection checkout, and passed parse/diff checks. The initial
four-line patch is preserved separately; its only additional change here is
removing the adjacent dead comment. Integration reuses native2 direct fixtures,
8 rank tests / 32 objects across both return modes, and full AUTO13/catalog8/
100-sample checks with fresh source/output bindings. Arithmetic and validation
bodies remain unchanged; comparison labels now say Candidate. No new test
matrix, baseline, split run or profile. Primary BEFORE stays whole57e2; whole098c
is separate. Retention uses 8–4096, with 1/2/4 still reported. Native quality
must show only the empty epilogue drain/control overhead removed, while BAR1,
release flags, actual dispatch drains and resources are retained.

**Entry077 source installed:** actual primary freeze is
`3efa6e71d3ca07bdcd3fd41c6498879b346088dd64252ccd3162f6cc2a1ddc26`;
manifest `f85d1a5d18780edfc825187b655ec215a038ec73496b06bc9548d306f100afa3`,
delta `41ec77a3035b76fb393c9cdf90480913792e4b09ae0cd3ca978b58901a52de68`,
stage `23da384f8a469c5b07c0875a7ba8b4f8a10c7bad76949f4e4025ce40e7c84c78`.
Existing inventory checks confirm only epilogue6026→ee769, with kernel5d6d and
all other sources retained. Stage 86359, install 39075, preflight 42386 and
both downloads exited zero. Actual preflight SHA:
`c978237a31a9424eb75b248dcb291fa46b71510e3a2ed7da33ccb659408dd4fc`.
Native session 41864 is running the existing direct N64/N128 fixtures.
Integration may proceed to unchanged8/32 and full13 AUTO after actual native
quality and numerical/source/idle gates pass; no additional root handoff delay
or validation matrix is required.

**Entry077 native quality passed:** actual downloaded direct N64/N128 PTX and
SASS remove the empty epilogue bulk commit/read-wait. BAR1 remains at N64 `b8c0`
and N128 `dac0` before the original flag-publication branch. All20 CTA barrier
sites and the exact six `atom.release` plus seven `red.release` instructions
remain. The actual dispatch commit/full-wait from token_comm.py1113/1114 stays
at N64 `11b70/11b80` and N128 `13d70/13d80`. Resources remain REG96/640 threads,
STACK0/LOCAL0, dynamic shared200064/230784 and grid `[2,1,74]`.

N64 instruction count falls5504→5496 (three executable instructions and five
NOPs removed). N128 remains6032 padded instructions: four executable operations
removed, one MOV added and three NOPs added, for net three fewer executable
instructions. This is native simplification, not yet a speedup measurement.
Result pins are N64 `cc64beed8b4bfdc205bccb962e62603c2986b53f8cd204e5b5c03423edaea99e`
and N128 `4cbd09ca8e5ff9a981107dd9503264fc69dadf372bf07d30e7fdff29ccefc836`.
Integration owns source/native/idle closure then immediate unchanged8/32 tests,
followed by the complete13-row AUTO sweep if the numerical cohort passes.

**Entry077 numerical completion and full sweep:** native source/idle closure
93239 passed, SHA `bcd1324a47924e0163148afd16db1dda6c54be6daa11e5d26ec60f07e9e622d1`.
Numerical23851, closure96335 and download47581 all exited zero: unchanged eight
EP2 rank tests /32 objects, both N64/N128 and return modes. Completion
`ff5aa8a68890dfed13d8ecef0fba142c85dbd38f278b6857cb5c809cd6305ae0`
binds exact source3efa, native38a68 unchanged and idle GPUs before AUTO.
Original full AUTO session82856 is now active:
`cu132-recovery0910a-fc1-empty-bulk-drain-default-auto13-direct-001`.
All13 rows, eight tactics,100 primary samples and effective flags(2,4) remain
unchanged. No extra cohort, baseline, split run, profiler or validator repeat.

**Entry077 retention scope before results:** this deletes producer-free work
and a dead comment, with all real synchronization retained. It qualifies for
the user's preference to keep pure cleanups even without a clear end-to-end
win. Native/numerical correctness is required; the complete8–4096 comparison
will quantify impact and check for a material regression. No per-row wins,
small-token results or historical row substitution will be used to manufacture
a speedup claim. Any performance claim must follow the complete measured run.


**Entry077 completed and retained as cleanup:** root keeps the five-line deletion
under the user's pure-cleanup preference, explicitly **without a speedup claim**.
Original AUTO82856 exited0 in585.834476614s; closure82706 and download32240 exited0.
The original saved reader and arithmetic comparison each ran once. All13 rows,
default8 tactics,104 compiled/winner records,104 rankings and1300samples are
complete; exact source3efa and native38a68 remain unchanged, GPUs/workers idle.

- Proof: `e607b4726152216ae87a179d2823a5a08f88286f7cba2a33601a3deef92f2cb5`.
- Result: `353b1b64fb750fc2bf6447ee954c4500417ed0f259e7c4f149c931d2ac98daf9`.
- Comparison: `cb37def2789007c651fa62ed772be0d9ed1b96d7e0280d534526d056dc6597c9`.
- AUTO source/native/idle closure: `35532e29c4680bfc0806f78850c8f6b2fcac6ee6d8be09b4b7f969d59a7530a6`.

| Complete control | 8–4096 latency GM change | Lower rows | All13 latency GM change | Lower rows |
| --- | ---: | ---: | ---: | ---: |
| Primary default57e2 | +0.519590% | 3/10 | −0.751061% | 5/13 |
| Separate whole-best098c | +1.964819% | 4/10 | +1.995430% | 5/13 |

[Both complete13 tables and all selected tactics](logs/cu132-recovery0910a-fc1-empty-bulk-drain-independent-comparison-001/README.md)
remain authoritative; no row minima, baseline rerun, drift adjustment or
reinterpretation of excluded1/2/4 rows. The measured8+ regression is reported,
not described as a win. Whole098c remains the published performance table.
Native2 direct and unchanged numerical8/32 both-return results above remain
separate evidence; host135 stays historical on8d.

Root committed exact executed bytes as
`0f361bc04664c574c91f96ecff3c259b8d4fdb14`: one epilogue file/five deletions,
all applicable hooks passed including mypy/Ruff, primary clean. Source3efa and
epilogueee769 are unchanged by commit. The fork push8d7718→0f361bc04 and live draft PR head0f361 are confirmed.
[Retention record](candidates/w4a16_fc1_empty_bulk_drain/execution/retention.json)
and [execution summary](candidates/w4a16_fc1_empty_bulk_drain/execution/README.md)
preserve the decision and exact pins. No source restoration or additional
host/numerical/timing/profile run is required by this cleanup decision.

### Entry078 — release packed-weight slots before TMEM store completion

**Status: source applied in primary checkout; native validation pending.**

Base is pushed cleanup commit `0f361bc04664c574c91f96ecff3c259b8d4fdb14`,
source `3efa6e71d3ca07bdcd3fd41c6498879b346088dd64252ccd3162f6cc2a1ddc26`.
This is a distinct overlap trial after CLC removal. Move only the raw FP4/SF
consumer release ahead of the TMEM store-completion wait, after the final
register-fed, warp-wide TMEM store issue. Decoded-full publication stays after
the wait. Every raw consumer warp/multicast participant still contributes its
original arrival; states, stage counts, two decode WGs and tails are unchanged.

A small private `_finish_transform_stage` hook preserves the shared split
decoder's existing fence/release/commit sequence. Only `_MegaMixedInput` overrides
that order. No duplicated decoder, public knob, runtime branch or new buffer.
The source proof expands the default hook to recover the entire old shared AST;
removing the override recovers the prior Mega AST. This is source preservation,
not a fresh split compilation or timing result. Root independently checked PTX
9.4 register-source, `.sync.aligned` and asynchronous-store completion semantics.

Proposal and ownership evidence: `candidates/w4a16_raw_release_before_tmem_wait/`.
Final patch SHA `51944eca8c2ddf0c83781701f3316f7b3958a0d6af730016ede3271e98e6a7ed`.
Shared decoder `4a870648` → `a92267936c99501687c35f9539375f0c1c33f6d6655f5d98a30e1b6ce6b2177f`;
Mega kernel `5d6d7c6c` → `8cc10121ca09761b354476eeb98adbf96fd927ecdba2466721a94bf000015ed0`.
Root verified pins, applied both files in the primary inspection checkout, and
passed parse/diff checks. Existing native2 direct fixtures, numerical8/32 both
return modes and full AUTO13/catalog8/100 remain the execution protocol.

Actual primary BEFORE is the complete source3efa sweep (proof `e607b472`,
result `353b1b64`). Whole098c remains a separate historical-best comparison.
Retention uses 8–4096; 1/2/4 are reported only. No baseline/split rerun, new
profile, additional matrix or timing changes. Native admission must show a real
raw-release/TMEM-wait overlap window with decoded readiness still fenced and
no new implicit wait, spill or resource regression. Source ownership supports
the trial; existing profiles do not establish raw-ring pressure as a bottleneck.

**Entry078 pre-run source freeze:** exact trial source
`3b42507e7fd9c405c9e4112a0692942dc303c6d2a2cfd5268aeb57e67f72f186`,
manifest `0db9fc365964a3b415587b76159139f90f08fcd65d931a8e2d9348a127309380`,
delta `cef4d82ae25f0b1b93049bb604d89ffc04fe483d9fc95d42da69e7d3d787444a`,
stage `356bd3795d6755b5ad5877edae010d6b04ee89daa2885cac354fc40d4d43ce36`.
Root source review passed; compile-only native validation may proceed while
independent source review finishes. No numerical launch until source/native
admission passes. This is a performance scheduling change, not a pure cleanup: a
correct native overlap window and the complete 8–4096 before/after comparison
must justify retaining its extra implementation boundary. Do not retain solely
for small-token wins or assume that earlier raw reuse guarantees a speedup.

**Entry078 native admission passed:** stage21957/install50377/preflight47166
and fetches exited zero; preflight `b0527282c3369845c66d990b449a97961cde9b51383edc14dc5ead9a9c1db9e1`.
Independent source review `143c70c9` also passed. Actual N64 raw release appears
at FC1 `7040` before TMEM fence `7050`, decoded arrival `7060`; FC2
`8060` → `8070` → `8080`. N128 FC1 is `6f60` → `6f70` → `6f80`,
FC2 `7f80` → `7f90` → `7fa0`. Each raw release follows the final register-fed
STTM. Raw arrivals have wait mask0, the fence writes dependency2, and decoded
arrivals wait mask4: the compiler preserves the intended overlap window.

REG96/640 threads/STACK0/LOCAL0, shared200064/230784 and `[2,1,74]` launches
remain unchanged. Native results are N64
`7e13bb98e205a5e9726272722cd8c40a7752f9d1e48d1ee752a1020d1c16331c`,
N128 `2ec8f618d1ffa33f83798c7e7d86564063fc2a60a4f63cafe0c71527f68e01f3`.
Root separately inspected downloaded SASS ordering. Existing source/native/idle
closure and unchanged8/32 numerics follow, then full13 AUTO if they pass.

**Entry078 numerical completion and AUTO launch:** native/source/idle closure
`9ec80cf5abfa7dc7ec53c077a829b33a7f148256541dc7ba57f9ecda1d272610` passed.
Numerical9847, closure88892 and fetch1338 exited zero: unchanged eight EP2 rank
tests /32 objects, N64/N128 with both return modes. Completion
`ebaa79942850120d19f9713543d184ad8c3b7d612144e74378ff5659f886a858`
binds source3b425/native38a68 and idle GPUs. Full AUTO original19307 now runs
`cu132-recovery0910a-raw-release-before-tmem-wait-default-auto13-direct-001`:
all13 rows, catalog8 and100 primary samples, against completed3efa. Only three
BEFORE metadata literals changed in the candidate-local driver; numerical
oracles, timer, catalog and scorer are unchanged. No baseline/split run or
additional profiling is added.

**Entry078 full completion and retention:** original19307, closure19932 and
fetch71783 exited zero; process wall590.4240545899956s. The original saved reader
and arithmetic comparison each ran once, passing13 rows/104 compiled records/
104 ranking records/1,300 primary samples. Proof
`819534c5b08a154323038dcb9835b1608cb8e164453046c99d117766e8785dcb`,
result `ee550fead0748804748e491e245d27e9efb9a60955ca68eea6860fe0795c2dbf`,
comparison `52304da1d09b85548276c8b8b6ad04e37514241dc0af84171c7c5e61d4c0435c`.
AUTO closure `0d54a5c79c7a2140ab88a58e4ae3b44dddcf45124ad44c6d4623c2d5fa22c3df`
records exact source3b425/native38a68 and idle GPUs/workers.

The [complete13-row tables](logs/cu132-recovery0910a-raw-release-before-tmem-wait-independent-comparison-001/README.md)
report8–4096 latency GM **−0.424211% versus actual whole3efa**,6/10 lower;
all13 secondary is−0.034425%,7/13 lower. Against the separate whole098c best,
8–4096 is**+1.532273%**,4/10 lower; all13 is+1.960318%,5/13 lower.
The controls remain complete independent runs, with no row minima, paired-run
claim, drift adjustment or baseline rerun. Tokens1/2/4 remain reported but do
not determine retention.

**Root retains** the general scheduling change: native shows the intended
early raw release with decoded readiness still fenced, unchanged instruction/
resource cost, and source plus unchanged8/32 numerical checks pass. Timing is
marginal and mixed; this is **not a new whole-run best**. The published098c
performance table stays unchanged. Promotion commit/push are pending root;
source3b425 remains installed and idle, with no restoration or further test run
required for this decision. [Retention record](candidates/w4a16_raw_release_before_tmem_wait/execution/retention.json)
and [execution summary](candidates/w4a16_raw_release_before_tmem_wait/execution/README.md)
bind the existing proof, tables and native/numerical closures. This completion
entry does not rerun arithmetic, readers, scorers or validators.

**Entry078 publication:** root committed and pushed
`ceb619b21b02fb9d6235edd3eed10ea06627ba51`: two files,+35/−8 (net27),
all applicable hooks passed including mypy/Ruff; checkout clean. The tested
shared decodera9226793 and Mega kernel8cc10121 bytes remain unchanged, preserving
source3b425. PR-body publication/readback is root-owned; the numeric retained
performance tables remain unchanged. No additional validation run accompanied
this publication.

**Entry078 PR readback complete:** OPEN/draft headceb619b21, body
`1b0b855f06a31c58a0fa2790c2f618f2c1d236cc8841ff2871da6c6f5c15df19`.
Root verified `logs/pr5019-raw-release-after-body-edit-001.json` and
`PR_BODY-raw-release-publication-proof.json`: all numeric tables, history and
profiling preserved. Canonical publication is complete; no pending promotion
or publication action remains for Entry078.

**Entry078 retention tradeoff:** the independent design reviewer recommended
archiving the candidate because a marginal 0.42% complete-run improvement with
mixed regressions may not justify 27 additional source lines. This was a
maintainability/performance judgment, not a new correctness or native-quality
finding. Root retained the narrowly scoped hook: it exposes an actual independent
raw-buffer lifetime, preserves the split default, adds no device instructions,
state, stages or tuning knobs, and improves the complete primary 8–4096 result
slightly. The numerical result is deliberately described as marginal and mixed,
not a robust or new-best claim. The full source patch, native proof, complete
tables and separate commit preserve both the evidence and a clean reversal
point if broader workloads later argue against the tradeoff.


### Entry079 — remove direct FC2 null flag bookkeeping

**Status: source applied in the primary checkout; fresh-node control pending.**

The prior `fi-w4a16-mega-0910a` allocation was reclaimed. Replacement0910b
(request80106) runs on hu-pdx-129 rather than hu-pdx-115, with all eight B300
UUIDs changed. Model, driver and recorded idle settings match; setup and loaded
stack verification are in progress. The current official NGC catalog still
selects `nvcr.io/nvidia/pytorch:26.05-py3` for CUDA13.2, explicitly pinned.
`candidates/cuda132_recovery_0910b/hardware-continuity.json` records the boundary.
One complete current-head baseline on the replacement node is required; the
prior3b425 timings remain historical rather than a paired current-node control.

On published ceb619/source3b425, direct FC2 return still increments and checks
a flag batch whose addresses are always null and whose publication is disabled.
The one-function change retains dispatch-return accumulation exactly and returns
a null, zero-count tracker with the next phase in the constexpr direct branch.
FC1 flushes its pending flags at the transition into FC2, and the original direct
FC2 path also clears count/address before reentering FC1. This preserves FC1
release order, all barriers, stores, accumulator ownership and tail behavior.
There is no new runtime branch, buffer, public option or shared-vendor edit.

The earlier null-tracker proposal was never compiled; it is not a previously
rejected timing trial. Current saved N64 native has eleven bookkeeping
instructions in the direct FC2 completion arm. Current proof and source review
are in `candidates/w4a16_fc2_no_publish_tracker/current_ceb619/PROPOSAL.md`.
The actual primary diff is one file, +8/-7, and passes diff whitespace checks.
Independent source review passed; no new test or model validator is introduced.

Use existing native N64/N128, unchanged eight EP2 rank tests /32 objects covering
both return modes, and the complete AUTO13/catalog8/100 protocol. Native should
remove the null arithmetic without changing real publication or resources.
Retention considers 8–4096; 1/2/4 remain reported. As a pure bookkeeping cleanup,
prefer retaining it absent a material regression; a small mixed result is not a
speedup claim. The final timing decision must use the whole fresh-node control,
without split reruns, row minima or historical-node drift adjustments.

Next source-reviewed candidate is moving the first atomic claim past common
pipeline initialization so it no longer blocks dispatch startup. Its separate
proposal is `candidates/w4a16_startup_claim_after_init/README.md`; it is not
applied alongside this trial. No performance result is claimed for either.


**Entry079 fresh-node control and native lowering:** retained source3b425 completed
AUTO13/8/100 on hu-pdx-129 in568.944s (original69072, exit0). Its source/native/idle
closure is1c2cace3; reconstruction19a83070/result e94d7f2f verifies13 rows,
104 configurations/rankings and1300 samples. The full table is
`logs/cu132-recovery0910b-retained-ceb619-default-direct-auto-reconstruction-001/`.
The earlier prelaunch failure76314 created no output or benchmark worker; it
was resolved by creating the declared empty torch-extensions cache directory,
without changing source or the saved file inventory. A reader's stale host
literal was corrected from115 to129 before remaining reconstruction checks;
original diagnostics remain preserved. Neither event reran a completed sweep.

Candidate source3d5183a6/manifestd58b5e09 was then installed (stage32808,
install37013, preflight30250, all exit0; preflight9275ba66). Original79386 compiled
both native fixtures once with no launches; local downloads are complete.
N64 result4f05f433 and N128 e9b4de0c retain REG96/640/STACK0/LOCAL0 and shared
200064/230784. The direct FC2 completion arm shrinks from11 to3 instructions
in both geometries: countzero, nextphase extraction, nulladdress. Whole native
counts are5496→5488 and6032→6024. BAR1 and real FC1 release remain; root and
independent review agree on the removed null arithmetic. Native details live
with `profiles/cu132-recovery0910b-fc2-null-tracker-default-n{64,128}-001/`.
Unchanged numerical8/32 and candidate full AUTO follow native/source/idle closure.
No timing effect is inferred from this instruction reduction.


**Entry079 numerical completion and AUTO:** native review38f0f1b passed and
source/native/idle closure62b4441c completed. Unchanged numerical64438, closure43251
and fetch27592 all exited0: eight EP2 rank tests /32 observed objects, both
return modes and widths; all REG96/640/LOCAL0/two decode WGs. N64 rank outputs
are2passed52.01s/51.64s, N1282passed60.02s/60.37s. Numerical closure26bae0a9
records exact source3d518 and native inventoryf13fedf6. The original full
AUTO60485 is now active on this source, against whole current-node control
19a830/e94d. No baseline, split or profiler rerun accompanies this candidate.


**Entry079 completed and not retained:** original60485, closure59658 and fetch73494
exited0; wall568.892838s. Reader7cfd2ac5/result7db772c2 and comparison6b45b13c
close all13 rows/104 compiled objects/rankings/1300 samples. Same-node retention
latency GM is **+1.892538%, only2/10 rows lower**; all13 is+1.970811%,4/13lower.
The [complete table](logs/cu132-recovery0910b-fc2-null-tracker-vs-current-and-whole-best-comparison-001/README.md)
includes every selected tactic. The different-node historical098c comparison
is not admission evidence, and no rows are substituted. Idle closureb0646960
confirms source3d518/nativef13fed and no GPU workers.

Root archives the cleanup despite native11→3 and passing numerics: the observed
whole-run regression is too broad for promotion under the stated performance
criterion. This does not prove all of the timing change is caused by the null
arithmetic removal; unchanged reused-dispatch rows also vary. No additional
baseline/probe/repetition is introduced. All source, proofs, logs and profiles
remain available. Primary epilogue is restored byte-for-byte to HEADceb619;
remote guarded restoration is in progress. No commit/push/PR-body edit is made
for this trial. The startup candidate proceeds on retained3b425, not on3d518.

### Entry080 — first atomic claim after common pipeline initialization

**Status: reviewed two-file change applied to the primary checkout.**

Base remains publishedceb619/source3b425; actual same-node BEFORE remains the
complete19a830/e94d run from Entry079, reused without another baseline sweep.
Initialize the existing atomic cluster-broadcast pipeline in scheduler.create,
then perform the unchanged first atomic claim in warp7 after common init and
before the NB9 metadata wait. This removes the first atomic result dependency
from the common initialization barrier, letting dispatch start independently.
Static first decoding stays after metadata readiness; steady claims, work
records, broadcast phases, tails and all hardware resources stay unchanged.

The moved factory makes the private, nonserialized `_sched_storage` reference
unnecessary; remove its constructor/copy plumbing in the same two-file change.
Primary diff is+24/-42, net18 fewer lines, with no new runtime option or queue.
The reviewed proposal, source ownership proof and native expectations are in
`candidates/w4a16_startup_claim_after_init/`. Native must confirm all mbarrier
initialization remains before the common fence/arrival, while the first ATOMG
and its result use move after the common wait and before NB9 in warp7.
This is a scheduling trial, not a claim that startup atomics are the dominant
bottleneck. Five total WGs and exactly two decode WGs remain fixed.

Reuse native2, numerical8/32 and AUTO13/8/100. Retention again uses8–4096; do not
combine this with the rejected null-tracker cleanup or the held raw6 proposal.
Source freeze/staging and GPU evidence are pending. The current draft PR and
its historical final-performance table remain unchanged.


**Entry080 source freeze and predecessor restoration:** local kernel3ad6f6df /
scheduler8c2c34bf match the reviewed proposal and pass parse/whitespace checks.
Complete source12b87629 / manifestc42f746d changes only those two files versus
retained3b425; epilogueee769 confirms the null-tracker trial is not combined.
Remote3d518→3b425 restoration passed before startup staging: receipt75cd61ff,
closurefd1a12e8, unchanged nativef13fed and idle GPUs. No tests or timing were
repeated for restoration. Full pins live in the candidate freeze and recovery
receipts; the complete same-node19a830/e94d control remains the sole BEFORE.

**Entry080 native admission:** original41148 and both fetches exited0. N64
resultd65723a5 and N128 result7d6ee53b retain REG96/640/STACK0/LOCAL0,
shared200064/230784 and grid[2,1,74]. Source/native/idle closure2f450e17 passed.
Independent review confirms broadcast mbarrier initialization before the common
fence/arrival/wait, then first atomic in warp7 before NB9 and metadata decoding.
Steady claim/publication/broadcast and tails remain; static-mode preservation is
source/constexpr evidence, since these actual native fixtures use atomic mode.
Whole instruction counts are5496→5520 and6032→6048 (+24/+16); unchanged resource
allocation does not mean identical code size. Numerical24469 is running, followed
by the complete candidate sweep against the existing current-node control.

**Entry080 numerical completion:** original24469, close36024 and fetch69268
exited0; all eight rank tests /32 objects passed with unchanged oracles and
tolerances. Closuree8d0cb22 confirms source12b876/nativef13fed and idle GPUs.
AUTO88624 now runs the unchanged13/8/100 protocol against whole19a830/e94d;
no baseline or split rerun. Native reviewe3e73b2e is sealed in the candidate
execution folder. Held raw6 source/adapters review6adf579b passed independently;
it adds buffering costs, not a performance claim, and remains unapplied.

**Entry080 completed and not retained:** original88624/close12625/fetch56186
exited0, wall568.906165s. Reconstructionace8103f/resultbab63810 verifies all13
rows/104 objects/rankings/1300 samples; comparison67cc8542 measures8–4096
**+2.768335%, only1/10lower**, all13+2.553115%,2/13lower. Full per-row values and
tactics are in [the complete comparison](logs/cu132-recovery0910b-startup-claim-vs-current-and-whole-best-comparison-001/README.md).
Different-node098c remains historical and does not determine admission.
Closure5cc4920b confirms source12b876/nativef13fed and idle GPUs.

Root rejects the observed broad regression despite the correct intended native
overlap and net18 fewer source lines. This single completed comparison does not
prove every timing change is caused by the startup reorder. No rerun, row
substitution or drift adjustment is introduced. Primary kernel and scheduler
were guarded-restored to HEADceb619 byte-for-byte; remote restoration is pending.
All source and evidence are archived; no commit, push or PR body edit. Live PR
readback still confirms OPEN/draft/headceb619/body1b0b855f.

### Entry081 — raw-stage ceiling six with B3/S2

**Status: isolated one-line change applied in the primary checkout.** Retained
base remainsceb619/source3b425; whole BEFORE remains19a830/e94d on hu-pdx-129.
Change only the private raw search from5..2 to6..2 under the same activation
preference(3,2). No new public knob, tactic or shape branch. All previous fitting
fallbacks remain; canonical host allocation predicts N64/raw6/218624 bytes and
N128/raw4/230784, to be checked by native captures. Two decode WGs, five total
WGs, decoded/accumulator rings and early raw-slot release remain unchanged.

Independent source/adapters review6adf579b confirms general six-slot state wrap,
ownership and tails. Extra SMEM, barrier initialization/drain and TMA pressure
are material costs; deeper buffering is not assumed faster. Prior raw7/B2/S3
and raw4/B3/S2 regressions remain in the proposal. Current kernel SHAebe0ff43
passes parse and whitespace checks; scheduler2b6ddf97 and epilogueee769 match
retained HEAD, proving neither rejected predecessor is combined.

Reuse native2/numerical8–32/AUTO13×8×100. The existing numerical/performance
stage observers and duplicate reference metadata bound are adapted only from
five to six; public tests, numerical oracles/tolerances, scorer and timing are
unchanged. Source freezing and actual validation are pending; remote will first
close the guarded startup restoration. No baseline or split rerun is planned.

**Entry081 freeze and predecessor restoration:** source25a8d4b8/
manifestff99bf27 changes exactly the kernel fitter ceiling versus retained3b425;
source stage29bb4c8b/deltaee1a08c8 are sealed. Startup reversal completed before
staging: stage62189/install35760/close55135/fetch78227 all0; receipta1c7d59d and
closured0bffb1d confirm source3b425/nativef13fed and idle GPUs. No completed
tests or timing were repeated. Integration proceeds through raw6 native2,
unchanged numerical8/32 and the full candidate sweep with the existing control.

**Entry081 actual native capture:** source installation/preflight passed
(receiptff4669b2/preflight6b551ff4). Native64690, fetch74679/19300 and closure39460
exited0. N64 result45fddefe observes B3/raw6/decoded3,218624 bytes; N128
result8446420c observes B3/raw4/decoded2,230784 bytes. Both retain REG96/640,
STACK0/LOCAL0 and grid[2,1,74]. All6032 N128 instructions and both encoded words
including scheduling bits match retained3b425. N64 grows5496→5512, including
the extra ring initialization/drain. Independent review checks actual six-slot
state/release/tail correctness before unchanged numerics; no timing claim yet.

**Entry081 completed and not retained:** independent native89db0e67 passed;
unchanged numerical80342/close40161/fetch17493 all0, closurea3b71ac0. All32
small H256/I256 objects actually fit raw6/B3 in both widths/phases, with no
resource regression. Canonical N128 remains raw4. AUTO65078/close16177/
fetch75733 all0, wall566.766s. Readerc83135a9/result2a4528d3 verifies13 rows,
104 objects/rankings and1300 samples; completione94be05b/closure6e3b4be7 bind
source25a8d/nativef13fed and idle GPUs. Actual selected allocations are88 N64
epi/raw6/B3/D3/218624 and16 N128 reuse/raw4/B3/D2/230784, all REG96/640/LOCAL0.

Comparisonb319412a measures **+2.169545% latency GM over8–4096,1/10lower**;
all13+2.673236%,2/13lower. [Complete values and tactics](logs/cu132-recovery0910b-raw6-b3-s2-vs-current-and-whole-best-comparison-001/README.md).
Root does not retain it. Identical N128 native code and the same4096 tactic
also show+2.36% between runs, so no claim attributes the entire difference
causally to deeper buffering. No drift adjustment, repeated baseline, row
substitution or different-node098c admission is used. Primary kernel was
guarded-restored to HEAD8cc before the next isolated trial; remote restoration
is pending. No raw6 commit, push or PR body edit.

### Entry082 — larger FC1/FC2 groups through the existing catalog

**Status: one-line catalog512→1024 change applied in the primary checkout.**
All kernel, scheduler and epilogue bytes match retainedceb619/source3b425;
raw6 and startup are excluded. Patch9cf161f8 changes only `_SWEEP_BASE.group_hint`
in owned autotune.py. Eight tactics, fixed S2, two decode/five total WGs and
manual/default512 remain. Whole BEFORE stays19a830/e94d on hu-pdx-129.

This general phase-order trial increases the FC1 work budget before switching
to FC2. It may reduce phase transitions while delaying FC2/activation reuse;
group256's earlier rejection does not establish that1024 will win. The original
E8 H64/I8192/topk2/EP2/520-per-rank fixture has260 routes/expert: atN64,512 gives
two640-tile groups and1024 one1280 group; N128 changes576+192 to one768 group.
These are source-derived fixture boundaries, not runtime scheduler telemetry.
Keep that existing8-rank/8-object numerical cohort with512/1024, unchanged
oracle and tolerances; no need to repeat the unrelated raw6 small-shape matrix.
Native2 explicitly selects1024, then full AUTO13×8×100. Only needed metadata,
boundary checks and current import paths are adapted. Source/BEFORE binding
and remote restoration are in progress. No public knob or autotune axis is added.

**Entry082 freeze:** sourcedcb6010c/manifest12157121 changes exactly the owned
autotune literal versus3b425; stage18f8391a/deltac2f157ec are sealed. Kernel8cc,
scheduler2b6d and epilogueee769 are retained. Native/helper subset includes
explicit1024 and the existing targeted E8 cohort; final AUTO binding follows.

**Entry081 closure bookkeeping limit:** the optional evidence list in its native
closure retained old FC2 result-file entries. Its actual source/native-cache/idle
checks remain valid; actual raw6 capture/result/SASS pins are independently
bound by the saved native-resource comparison and native review. The historical
closure is preserved, with the limitation recorded in raw6 VALIDATION.md;
no missing native execution or repeated check is claimed. Raw6 reversal is
complete: receiptb0dd456c/closure886ff415, source3b425/nativef13fed/idle.

**Entry082 native admission and launcher repair:** install28ec1309 and
preflight84eb5970 passed. Native26795 exited0; resultsb3c6a1e1/05698a74 show
actual config/kernel1024, N64raw5/B3/D3/200064 and N128raw4/B3/D2/230784,
REG96/640/STACK0/LOCAL0 and grid[2,1,74]. All5496/6032 instructions preserve
their opcode counts; only four immediates per geometry differ (two thresholds
512→1024 and corresponding signed-limit constants). Independent review91ff8b53
passed; fresh native closure98b1aa81 pins both actual group1024 captures.

Original numerical90805 entered the older E8 runner's `--standalone` DNS
rendezvous and produced no rank/test output. Integration preserves that launch,
stops its own exact process, closes source/native/idle, and creates a fresh
launcher-only sibling with the established localhost master address/port.
No source, oracle, test body, fixture, native binary or completed test changes.
The original Entry056 also recorded this rendezvous failure; it is an execution
adapter issue, not a numerical result. Actual retry outcomes remain pending.

**Entry082 numerical completion and full AUTO:** launcher-only retry002 uses
`--nnodes=1 --master-addr=127.0.0.1 --master-port=29587`; original51850,
closure83541 and fetch29949 all exited0. Wall52.619s, all eight rank cases/eight
objects pass the existing oracle and tolerances. Config and kernel group512/1024
are both observed; all actual objects have REG96/640/LOCAL0/two decode WGs,
raw5/B3 in both phases and D3 atN64/D2 atN128. Saved-checkdf01ae3c,
closurede723b4f and completion34673a8a bind sourcedcb6010c/nativef13fed/idle.
The original failed DNS launch remains separate with zero tests, failure4923781e
and stop-closure451b02d4. Amendmentf89be030 preserves the launcher boundary.
Full AUTO7354 now runs the original thirteen rows/eight tactics/100 samples
against saved whole19a830/e94d, with actual002 closure bound. No timer, scorer,
public test, source, completed native capture or baseline was rerun or changed.

**Entry082 completed and not retained:** AUTO7354/closure39482/fetch50185
exited0, wall566.101s; source/native/idle closure5dcd66f6. Proof9134a6ca and
result94669d7b validate13 rows,104 selected compiled objects/rankings and1300
samples. Same-host BEFORE19a830/e94d gives **+1.905248% latency GM over8–4096,
2/10lower**; all13+3.222286%,3/13lower. The complete G512/G1024 tactics and
raw values are in the [comparison table](logs/cu132-recovery0910b-group1024-vs-current-and-whole-best-comparison-001/README.md).
The separate older-node098c comparison is historical and not admission. Root
does not retain1024; primary autotune.py is byte-restored to HEADe9941066,
git status clean. Remote guarded restoration is pending. No commit, push or
PR-body change. No baseline/split rerun, row substitution or drift adjustment.

The original saved-reader attempt failed at E8 count accumulation (`rank_tests`
versus saved `rank_cases`) after two source checks and before any result/sample/
resource/scorer validator. A minimal continuation reuses those completed source
checks and corrects the mapping; all result validators and comparator ran once.
The original failure and continuation records remain separate. No numerical
or GPU execution was repeated for this bookkeeping correction.

**Entry082 restoration closed:** only autotune.py d4fe→e994 reversed,
receiptcf047b6e/closure82955c7f confirms source3b425/nativef13fed and idle
hu-pdx-129 GPUs. Stage84498/install74247/closure69316/fetch15929 all0.
Final AUTO completionafd414ed and comparison7d8d1842 preserve actual104
REG96/640/LOCAL0/two-decoder/G1024 objects:88 N64epi/raw5/B3/D3/200064
and16 N128reuse/raw4/B3/D2/230784. No test or timing rerun after restoration.

### Entry083 — scheduler construction cleanup with retained claim order

Primary now contains only the reviewed one-file scheduler patchcb9d857c:
2b6ddf97→64073302, +14/−32. Build the atomic broadcast pipeline alongside
the other scheduler pipelines in `create`, removing the dead Python storage
reference/prototype copy. The kernel remains exact8cc; its first atomic claim
still precedes common pipeline initialization. This extracts only mechanical
construction cleanup from rejected Entry080; its claim scheduling change is
absent. Static initialization, dynamic state serialization and all claims,
publication, waits, releases and tails are unchanged. Independent source
review is ready; freeze/native-only package is being sealed. No speedup or
full timing sweep is planned unless generated differences require it.

Actual retained source3b425 G512 native controls are the0910a raw-release
N64/N128 captures, not new0910b captures. Recorded compiler/DSL/target stack
continuity supports comparing generated instructions despite a different
physical GPU; timing still uses the current-node whole19a830/e94d baseline.
A separate local-FC2 router wait specialization is saved source-only under
`candidates/w4a16_fc2_local_router_wait/`, not applied or stacked here.

**Entry083 completed and published as cleanup:** actual source641c6fe8/
manifested24f1a2, staged855e6a9/delta9c7c3602. Source install4c53b442 and
preflightae7a0c9a passed. Native6823 exited0; resultsab337956/6864bd63 match
the retained controls byte-for-byte for complete5496/6032-instruction SASS,
including PCs and both encoded words. Actual descriptors, options, stages and
resources are exact: REG96/640/STACK0/LOCAL0, SMEM200064/230784, grid[2,1,74].
First atomic remains before common init; direct atomic native scope only,
static/reuse invariants remain source-reviewed. Independent reviewad8cc6e3,
resource comparison4ac7cfad, completion19a95df0 and closure28894955 preserve
source641/nativef13fed/GPU idle. No numerical/AUTO/profile rerun or speedup.

Committed and pushed `b8ecada440c4b81993abcadcbb36ad1642b19f5d`; all applicable
hooks including mypy/Ruff passed, source bytes unchanged and checkout clean
before the next trial. Live PR readback remains OPEN/draft at this commit,
body3cc265aa; every raw table row is exact to the prior body. New validation
distinguishes native-only cleanup from earlier numerical/timing evidence.

### Entry084 — compile-time local FC2 routing wait

Root applied only reviewed epilogue patch0046b332/epi34dbafab (+6/−3) above
retained/published641/b8ecada. In reuse-dispatch return, local affine routing
reads no dispatch provenance; an outer constexpr guard removes only the early
peek-dependent acc wait. The final full wait still precedes all accumulator
reads. Direct metadata protection, alpha load, releases, flags and tails remain.
Source review672ffa8d passes. Native paired reuse N64/N128 controls on current
remote641 and candidate captures are being prepared before unchanged numerical
8/32 and full AUTO13×8×100 admission. Native-only constructor equivalence is
not claimed as fresh reuse capture; current-node whole19a830/e94d remains the
complete performance BEFORE. No new timing baseline or split rerun is planned.

**Entry084 control refresh selected:** repeated sequential trial differences
include about2% movement in unchanged native code (e.g. raw6 N128), so root
selects one occasional complete retained641/default8/AUTO13×100 refresh on
current129 before staging the local-router candidate. This is a control-drift
check and the next whole BEFORE, not a repeat for each trial or a timing claim
for the constructor cleanup's publication decision. Keep the original19a830/e94d
run and all prior comparisons/decisions unchanged. No row minima, correction
factors, split rerun or replacement of selected rows. New BEFORE binding stays
pending actual full closure/reconstruction. Remote source641 remains installed
for the affected reuse native controls and the refresh; primary's reviewed
epilogue candidate remains visible separately.

**Entry084 native baseline/freeze and active refresh:** candidate source61ee217a/
manifeste88d1758, stagea8c48a54/delta9ad14f2a changes only epilogue34dbafab.
Affected reuse controls on641 completed1520/closure12e805e4; actual5736/6224
SASS instructions, REG96/640/LOCAL0 and SMEM200064/230784. Review541a0541 maps
mutually exclusive early/final waits to the same accumulator barrier. N64 peek
a490, waits a520/a560 then LDTMa5b0; N128 peekb520, waits b5b0/b5f0 then
LDTMb640. The proposal removes branch/duplicate code, not two sequential waits.
Full retained641 refresh7428 is running before candidate staging, standard
13/8/100 with explicit historical3b numerical association32ea5b44; no fresh
641 numerical test is claimed. Baseline adapters ef8eedcd/ae59a173/7a4a1749
preserve result/sample/resource/scorer/ranking validation.

The control-refresh rationale is bounded: raw6's exact N128 SASS comparison was
the direct-return capture. The4096 benchmark selected reuse, with unchanged
allocation/configuration and source fitting; its timing cubin was not independently
proved byte-identical. Repeated sequential variation motivates one whole control
refresh without claiming a measured causal drift correction or replacing rows.

**Next held communication proposal:** final source-only refinement is
`candidates/w4a16_dispatch_read_wait_f1_elect/`, fullpatchb04cec7a/tokencommd03984fc.
One private BF16 pull override uses existing universal transport and four needed
primitive exports; vendor bytes remain untouched. At most one pool write is
pending, overlapping the next input pull/mapping. F1 uses compile-time immediate
publication handling; one redundant pre-store sync is omitted because full-mask
election supplies the rendezvous at a boundary with no payload visibility handoff.
Publication/tail syncs and read-completion scratch protection remain. Reviews
653039a7/c102e047 pass source ownership; actual new native lowering, resources,
multiple-pull/full-batch/partial-tail numerics and full performance remain pending.
Earlier a34f and F1-only proposals/checks are preserved and never staged.

**Entry084 occasional control refresh completed:** retained641 run
`cu132-recovery0910b-retained641-default-auto13-direct-001`, original7428,
full closure86158 all0, wall569.738367651s. Single saved reader/comparator pass
13rows/104compiled/104winner/1300samples. Proof26b65baf0a1f65c91e16b5d0cb80e0817cea85c75bad6cf1d35021de819ac160,
result825908b8102c0cd15b4dd9e884eb58f192aaa6619f4f593bcd74073c61708f33,
closurec819475cf6366c0df50874506219e5d86161a5c326109d6b50ec91a410e46e42.
Source641/nativef13fed and idle confirmed. This complete run is the new BEFORE
for61ee and subsequent trials, replacing19a830/e94d only prospectively.

Old→refreshed8+ latency GM **+2.009389%,2/10lower**; all13+2.040623%.
[Full control comparison](logs/cu132-recovery0910b-retained641-vs-current-and-whole-best-comparison-001/README.md),
READMEf1739d4a/comparisonebeeacf7, preserves every row. This is observed
sequential variation across a mechanical cleanup, not a measured cleanup
effect or drift correction. Prior trial outcomes and their original controls
remain unchanged. No split run, row minima or retrospective correction.
New1..4096ms: .073713,.118865,.115377,.140321,.155425,.178642,.204705,.207393,
.207809,.211249,.233442,.312547,.467970. Candidate helper binding is being
updated to these actual whole pins before numerical/AUTO admission. Candidate
stage86234 passed and guarded installation87818 is in progress.

**Entry084 candidate native:** guarded install87818/receipt4f2f57c3 and
preflight92374/9278db99 passed, source61ee. Native37319 completed both affected
reuse cases; results9bfaab6b/7c4a3d49 remove16 instructions each:5736→5720 and
6224→6208. Resources/descriptors/options/stages remain exact, comparisonf56f2a17.
Integration maps the surviving N64 waita4b0 before LDTMa540 and N128waitb540
before LDTMb5d0; independent instruction-order review is pending. Closure
eff67099fda1785a2eb4952dd148410c683248d6e6403e038ccc6d58f566fc99 confirms
source/native/idle. Bound runtime stage35bf096e/driver7875d21b/reader8d3b0e82
uses fresh26b65baf/825908b8. Numerical8/32 and full13/8/100 remain required.
No timing gain or retention decision yet.

**Entry084 native/numerical admission completed:** independent native review
259124f05ec126df8c7a589c4d4fa7c6b752d39f09a9d325a96348499aab3d0d passes
both reuse fixtures, including unchanged protected synchronization and MMA
subsequences. The original numerical84165 exited0 with8 rank-tests/32 objects
across both return modes. Closure
50c7039a1eaa376da338323a9bb4af8dc6082aef6e2aa24627087dd3e9a75004
confirms candidate61ee/nativef13fed and idle. Full candidate AUTO83872 is now
running against the completed refreshed641 whole26b65baf/825908b8, with no
extra gate or probe. No numerical tolerance, workload, timing or catalog change.

**Entry084 completed and retained:** original83872/closure39212/fetch45068
all exit0, wall569.657859143s. Saved reader/comparator run once,13 rows/104
compiled+winner records/1300 samples. Proof7b23defbf4df776e3ac8fe86bdcfbe254e5536a5f04d08a342ebd12a6172b4c3,
resulteffe5a0d99f1fde5432b62b4938ae375ac11c9b31843e3380aa29212d9db0478,
idle d114b3c3 confirms61ee/nativef13fed. Same-node fresh641 comparison9f39c77d:
8+ latencyGM−1.435173%,6/10lower;all13−.877587%,7/13lower. The affected
reuse winners are mixed:2048+.235% (F4→F8),4096−.653% (sameF4). Most other
rows select unchanged direct-return code. Retain for compile-time simplification
and no material affected-path regression; do not claim aggregate−1.44% as
isolated causal speedup. Other-node098c comparison is historical only.
[Full table](logs/cu132-recovery0910b-fc2-local-router-wait-vs-current-and-whole-best-comparison-001/README.md).

Commit773c9b0725f19500ffdd6bdd03c84f56f552dbc5 pushed96472, hooks including
mypy/Ruff pass and tested epilogue34dbafab exact. PR readback OPEN/draft/head773c9b,
body3bb7471f211f0fc1c684f24f85a220fbd1d6a137014460d0d4cf632b73d32c7d.
Validation rewritten around current evidence, all raw table lines unchanged.
Archives README d3fb2bf1/VALIDATION558a3d82/retention081121a3 preserve decision.
This complete61ee run becomes the next whole BEFORE, not selected-row minima.

### Entry085 — overlap BF16 pool writes with the next input pull

After publishing61ee, root applied exact b04cec7a patch to primary: three
modified kernel/helper-boundary files plus new owned token_comm.py (332 lines).
VERBATIM source stays untouched. It overrides only BF16 pull and preserves
universal setup/storage/metadata/return/tail ownership. At most one pool-write
group is pending; read wait protects SMEM reuse, full wait protects subsequent
store/publication. F1 specialization omits added inter-token/tail drains at
compile time. One pre-store sync is replaced by existing full-mask election;
publication/tail visibility syncs remain. Source reviewc102e047 passes.

Actual primary freeze: sourceb4078959b8043835eb24a18b43c0190c08b5063c7e019c938d286e6d9289e7e6,
manifestacfda9adc4f228bcf7a88f095e03a1f4fe3f1710e2a3357613312ab3ea6ebd17,
deltac8dd073f40332a01e0c1ddcb9fb60e2442686bc727a81dec1709b3177c94f7b3,
stage9ccffc5c837ef2ce7378fdc6354de4f79b4454baa87b2ac4e4c8f4b107be7409.
Paired native BEFORE19890 completed3 cases on61ee: N64/F4/direct, N128/F8/reuse,
N64/F1/direct, results9c3e2147/2ae43b93/fe797083. All REG96/640/STACK0/LOCAL0;
SMEM200064/230784/200064. Closure77883 precedes candidate install.

Next admission is actual native3+independent order/resource review, original
numerical8/32 plus6/6 large-skew rank-cases/objects using unchanged public
oracle (total14/38), then full13/default8/AUTO100 on existing complete61ee
proof7b23defb/resulteffe5a0d. No baseline/split rerun. The large skew counts
derive from actual rank0 launch warps and exercise repeated full batches,
partial tails, local/peer sources and zero-work destination. No tolerance,
catalog, retention-range or timing change.

The separate future two-sync source audit0b5ef924 identifies inherited BF16
barriers after input TMA issue and before lane0 weight STG; no SF stores remain.
Saved61ee PTX supplies election/rendezvous landmarks, not new-candidate proof.
That potential follow-up remains held and is not part of b04c.

**Entry085 native compile / binding progress:** BEFORE source/native/idle
closurefdae964053a8aed130ee97ef3a19bc0ab4e4d5cfd613fe7abe69ec8971a1925c
passed, completion35ac3ddd. Candidate stage88260/install8796/preflight76077
passed, receipt711844fa6da4c332fa0a59610797e4be2a0749cfd9f7472ca734e616fc7d9174,
preflight58e9d0d6083984616634c77965701f4118af8abd2e78a86dcd55bbf810964505.
All three candidate native captures22237 exited0; native review follows actual
download. Bound runtime stage95b0a3424d3d2206f1c9603fde3af065ba3acd388e2673e7b5849624b87267a7
passed60494. Numerical14/38 and fullAUTO13/8/100 remain pending native admission.

The held two-barrier follow-up is saved at candidates/w4a16_dispatch_pull_barriers/:
patchb1ced40375666ba426eb80f105253476684ea0cc2785cd9ec5bf0634e596c6d4,
tokencommd039→53f968fa681a0109ef15fcf14d7813023a6b99ef38a98706318e2597b9a594ce.
It removes only the two previously source-reviewed calls; AST/apply check pass,
primary unchanged. Minimal helper package1cb759de/plan0c7eee7d reuses existing
native3/numerical14/38 infrastructure with unbound whole-source/performance pins.
No runtime/native/GPU/validator work or new timing measurement for that proposal.

**Entry085 native3 admission passed:** original22237 captures all pass, with
paired counts N64/F4/direct5496→5496, N128/F8/reuse6208→6200, N64/F1/direct
5472→5448. Resources/config/stages/options unchanged, no stack/local bytes.
Independent review verifies actual read-only completion on nonpublication
iterations, full completion before publication/tail and subsequent store,
full-mask election and required convergence. F1 has no read/batch/pre-store/
tail-drain arms. Protected MMA/TMEM/async-fence sequences remain exact.
Native/source/idle closure
c2bb752a3f929dfb8caba7f66425e152dd6290fb7b2dae13c84befa1acea0800
passes, sourceb407/nativef13fed. Expanded numerical14/38 launched58376.
No performance or correctness result is claimed before that run completes.

**Entry085 expanded numerical coverage passed:** original58376 true0, all three
jobs passed: N64standard4/16, N128standard4/16, large-skew6/6 =14rank-cases/
38compiled objects. Source/native/idle closure54613/fetch52432 both0, SHA
a4b919236e090f3884a804f49917490914a15bfdacdaa4d266d92e589e5ee27f; nativef13fed
unchanged. Independent native note8ef37e77155268c0a25d15cf587267b7525fdc14d94e88f97338d094c779b6cc
is sealed. FullAUTO22056 started onb407 against the complete retained61ee
proof7b23defb/resulteffe5a0d,13rows/8tactics/100samples unchanged.

Read-only historical full T4096 NCU review identifies dispatch routing-weight
load consumption at PC135a0 (LDG13540) with442–669 samples/rank, chiefly
long_scoreboard; input TMA13410 already issued. Input wait17cd0 has87–143
samples/rank, mainly sleeping. Store full-wait13900 and removed-sync sites
17b40/17c10 have no recorded samples, not proof of zero cost. These are
source/PC-attributed dispatch samples, not whole-kernel latency shares. Replay
durations.437–215.495ms/throughput>100% and launch/rank skew prevent ranking
the proposals from this profile alone. Existing saved files were read without
new import/export/profile/GPU execution. A future source audit will consider
metadata load/use overlap; it is not added to activeb407 or held two-syncpatch.

**Entry085 full result / decision:** original22056 exited0, wall567.827462s;
closure74276/fetch46808 both0. Saved reader/comparator each once,13rows/
104compiled+winner records/1300samples PASS. Proof
adba763d8dd174172c8fa29c0663551846c48949ce7ffd8ad47875dd53d43045,
resultad27222221c96b27ccbb6ba6ccb53092a9379c410f13dd5c5216ec4fbda62ff3,
closure58dc906d43c7c9599ccf93e3071997a57bda87af77561c0ea3799363fe697135
confirms b407/nativef13fed/idle. All104 selected objects REG96/640/LOCAL0.
Against selected whole61ee,8+ latencyGM **+1.628212%,3/10lower**; all13
+.562043%,5/13lower. Comparison2af7fde5 and complete tablecfb0df50 are in
[full comparison](logs/cu132-recovery0910b-dispatch-read-wait-f1-elect-vs-current-and-whole-best-comparison-001/README.md).
Historical other-node098c comparison remains separate and is not retention
evidence. No row substitution or baseline/split rerun.

Root does not promote b407 alone. Keep it installed as the experiment base
for the already-reviewed two-sync refinement rather than perform a restore
roundtrip between related trials. No commit/PR body update for b407. Published
source stays61ee/773c9b; all code/artifacts remain preserved.

### Entry086 — remove two BF16 pull-only warp barriers

Root applied exact b1ced403 patch in primary over b407, token_comm.py
SHA53f968fa681a0109ef15fcf14d7813023a6b99ef38a98706318e2597b9a594ce.
It removes only the inherited sync after input TMA issue and before lane0
weight STG. Source review0b5ef924 identifies no memory-ownership transfer at
these two points; all initialization/metadata collection, publication/tail,
scratch-reuse syncs and full-mask elected wait/store boundaries remain.
No runtime condition, knob or pipeline state is added. Actual source freeze
is pending; syntax/apply/diff checks pass.

Next primary complete BEFORE is b407 adba763d/ad272222 to isolate the barrier
decision. The same candidate whole run will also be compared separately to
retained61ee7b23/effe for joint retention, replacing the unrelated historical
node comparison for this trial. No rows mix between controls; no timing rerun.
Matching actual b407 native3 captures supply BEFORE without recapture; new
native3→independent review→same numerical14/38→full13/8/100 is authorized.
No source restore before this refinement.

The later routing-weight proposal is source-only at
candidates/w4a16_dispatch_weight_after_payload/: patchc2c36243 on two-sync53f,
proposed0cbc2af8, audit aa294a1a. It removes the lane0 load guard and moves
only lane0 routing-weight STG after payload/provenance/commit, before existing
publication full-wait/sync. No new primitive/state/knob or compiler coercion.
Source uniformity/lifetime review finds no concrete blocker; actual early-load
and delayed-first-use lowering and resources remain unverified. It is not
part of active Entry086.

A separate publication-time split-only adapter is held at
candidates/w4a16_publication_split_refresh. It preserves the canonical shared
weight factory used by Mega (ordinary split-only preparation would bypass it),
uses existing split timer/tuner/recorder, and keeps actual source/native/Mega
bindings unset. This is not selected or queued for GPU work. One same-node
split run may be needed only when a retained Mega result warrants refreshing
Final performance; no split per optimization trial.

**Entry086 actual freeze/staging:** sole token_comm d039→53f change froze as
source7da15d3b3e456b40aff35eadd66433dd71a206644e6675ad44c6b1d34ca088b7,
manifest5175cb8b91260b79dbe8516cf77e1a46419caaa86a97b02de7d0dd900b5f660a,
delta7fc13268ec32e06e1683525560a6212bda569b867e3d8b46c79f80d8824f6d25,
native-stage193441a5724d7002831a586cd97fa6728b39f30a1e68d50120238d82cef328ec.
Integration started stage61376 immediately. Runtime binds complete b407
primary and retained61ee secondary; no control recapture. B407 archive
README69ff27a8/VALIDATIONab7545e5/retention10ddbaaf is closed with corrected
completionada47c95 (13 timing arrays×100), preserving previous receipt and
all proof/result/closure/comparison bytes.

The held native3 parallelization audit finds all admitted native roots read-only
and every case's Torch/FlashInfer/driver/CuTe dump/cache private before imports.
Separate driver064852df preserves exact3cases/options with separate process
groups/logs and waits for every started child. CPU/RAM contention and actual
wall-time benefit remain unmeasured. It is not used in active Entry086; original
serial helpers remain immutable.

**Entry086 native progress:** stage61376/install81489/preflight15263 all0,
receiptf7b8e4d072bb5b1e846406b0ca7086ed13ea28e4ea5ddfaff7325e8f4ab3d952,
preflight3d45a96ffe4da25ff19cd0694b67c038a8f396851f457a3958e7cd1b99302daa.
Native27196 completed3 cases with−24 instructions each:5496→5472,6200→6176,
5448→5424; two WARPSYNC.COLLECTIVE sites removed each. Actual configuration,
stages, compiler options and REG96/640/STACK0/LOCAL0 are unchanged. Independent
order review is in progress; closure81128 passed, fetch94933 pending. Runtime
stage0e6c996c is sealed, binding40ac291f/source-mapc5541a72, pure reader load
4cc03395 passed once. Same numerical14/38 and full13/8/100 follow admission.

**Entry086 native admission passed / numerical active:** actual3cases remove
exactly2 PTX warp-sync sites and24 SASS instructions each. Full-mask input/store
elections, F4/F8 READ/full waits, F1 immediate publication and batch/tail memory
ordering remain; all tcgen05 PTX lines match. Config/stages/resources exact.
Transport ordinary register allocation and branch folding also change; this is
not full residual SASS byte equivalence. Native/source/idle closure
010f528e7184c29554efe4cac91cb991f51a9a5b0b5b326409cb7f4280032c28
passes, source7da/nativef13fed. Unchanged numerical14/38 launched61309
immediately; fullAUTO follows its closed PASS without another root gate.

**Entry086 numerical complete / full AUTO active:** original61309,
closure66502 and fetch56496 exited0. Numerical14/38 passes, closure
0adf967b4157723a95a6a27c62207cc3676a271dc8e63708aeb7694844537fd3.
Saved summaryf116c71de7df2d9a47d3564ef09fe843ae4d1c5e8ff40932626e53d6af99d018
records every object REG96/640/LOCAL0/two decode; large-skew F4/F8/F1 each
use T1777 with actual destination7108/0 and transport53f. Native review
64a62e13 is sealed. FullAUTO43592 launched immediately, with completeb407
primary and retained61ee secondary. No baseline capture or validator rerun.

Held routing-weight handoff1aa2e3e9 supplies an exact root apply/freeze command,
parallel native3 map2d01bb05 and unchanged shared numerical14/38/AUTO13/8/100
logic. Only three narrow new runtime templates carry identity/path substitutions.
Whole7da BEFORE/source/runtime bindings remain pending; no route source apply,
freeze, stage or execution has occurred.

**Entry086 complete / held for refinement:** original43592 true0,
wall564.903732s; closure57231/fetch93821 true0. Proof
6c3458a39fdf7f0dc2362252eac897ed7dbcd6029abc4514f7c1e728dfec2662,
resultacb3ef49bfa00fcef45fe31cd7cfb332075d2bd5212622b4a29732991066c1e5,
source/native/idle closuref6e603a8aeccfb8ca7508df5e2b537c1749c41397d5934e33cd015f9ac9509a7.
Single reader/comparator PASS13rows/104compiled+winner records/13arrays×100
=1300samples, all104 REG96/640/LOCAL0. Completiond511ddc3; comparison57fe781b
and README6602453d. Whole8+ latency−1.158901% vsb407 (6/10lower),
+.450442% vs retained61ee (5/10lower); all13+.131507% /+.694288%.
[Full tables](logs/cu132-recovery0910b-dispatch-pull-barriers-vs-b407-and-retained61ee-comparison-001/README.md).
Root does not promote the combined transport change yet. Preserve7da as the
experiment base for routing-weight overlap, with no restore/recapture.

### Entry087 — routing-weight consumption after payload issue

Root selected and applied exactc2c36243 in primary. The existing raw weight
load becomes warp-uniform, and only lane0's weight store moves after payload
TMA/provenance/commit, before required publication handling. No new load helper,
queue, state, public knob, or vendor-drop edit. Source uniformity/lifetime
audit aa294a1a applies; generated load/use placement is still unverified.
Actualsourceb9db4c19d57fff531a64b90683a5cd9c33be5134624156b3f1f9d2efd63d9826,
manifestb9e68860015f4d8ae21e33bc0e508590d0ba3cd8ac0415c15d02d2fa41c85f61,
deltaf56fb34e1ee766cd20497d8813f358305f459922e69de75af8a9d3f45fef4db9,
staged85d83d792a9a9fe1f2791ccc92fa54ba3477b225e1b8627922ee7468275e782.
Integration starts native3 with selected parallel064852df, reusing actual7da
controls; unchanged numerical14/38 then full13/8/100 follows native admission.
Primary wholeBEFORE7da6c3458a3/acb3ef49, secondary retained61ee7b23/effe.
Neither earlier transport trial is promoted alone; no split queued.

Held pure initialization cleanup4fec9dbd removes only first of two syncs before
independent expert-count setup. Proofe181b51a explicitly notes PTX syncs survive
but final SASS has no explicit first WARPSYNC, so its native effect may be nil.
No apply/runtime work selected. Stage-policy auditf8bb7952 confirms separate
ring depths/full TMEM and no credible fresh stage-only trial; no repeat sweep.

**Entry087 native admission and numerical run.** Staging, installation and
preflight passed; install receipt7ac6ad62984400eeaaed6e0a9d2b1523dc0ed6c7f59c6452c87706756e807e24,
preflightb1864d7b797cd00f7820714572600d1b9f9c384b2e8f2cf02f4672f05464365f.
Parallel native original74447 and all four downloads exited0. Instruction
counts are5472→5496,6176→6208,5424→5448 (+24/+32/+24), with unchanged
config/stages/options/REG96/640/STACK0/LOCAL0. Closure
17bb5bdf346e8f3416c41ef40e0928d947ce2dcd74cf602c4d98bf08d2dda7c5
(original54786/fetch95676) confirms unchanged source/native and idle GPUs.

All three cases pass independent safety/resource review: full/READ waits,
initialization, phase and publication/tail ordering remain. On the normal
full-warp path, routing LDG uses write scoreboard5 and its first waitmask0x20
is the post-payload weight STG. N128: LDG132f0, input TMA13440/wait134b0,
payload13660/provenance13670/commit13680, weight STG136c0. The intervening
DEPBAR names SB0 and does not wait scoreboard5. Generated BRA.DIV election
recovery includes waitmask0x24 before pool issue; overlap is not claimed on
every generated CFG path. The source loop/election uses all32 participants;
expected ordinary execution takes the mainline. This qualification does not
weaken the safety admission and requires end-to-end timing for retention.
Numerical14/38 launched99535; full13/8/100 follows its normal closed PASS.
Runtime stageeca507e8/binding0930223e/mapdc608b18 reuse unchanged validation;
pure reader loadd29516fa passed once against the actual preflight.

Next held candidate is the single post-accumulate warp-sync deletion, patch
2e064056/proof004eb010 on current transport0cbc→8eef. Its narrower proof
requires constant tracker phase0, the same full-mask elected issuer for
payload-store/read-completion/next-input reuse, and all existing prepublication
and tail synchronization. Election is not a memory fence. Minimal held reuse
package675f65d4 is ready but not applied/frozen; wholeb9db BEFORE is pending.
This per-token candidate precedes the held one-time initialization cleanup.

**Entry087 numerical completion.** Original99535, closure8994 and fetch15946
exited0. Closure `7a931df79a02a65ddb85526a536b863377a463b3a26b19dd2e737f6e445728f4`
passes14 rank-cases/38 compiled objects. Saved summary
`b338c0ecb1406bb59422f3c576b34ffd3897b95adbb9e83dbf0b5c46858a00b4`
confirms REG96/640/LOCAL0/two decode throughout; large F4/F8/F1 calls use
T1777, destination7108/0 and transport0cbc. No original validators were rerun
for aggregation. Native mainline/fallback scheduling qualification remains
explicit. FullAUTO is admitted against complete7da and separate retained61ee.

Later held source cleanup: let the existing elected payload/provenance writer
also perform the uniform routing-weight store immediately after commit. Patch
`29abf56a` is a two-line deletion against prospective post-flag transport8eef,
producing41bf; proof `146badad` is in
[candidate notes](candidates/w4a16_dispatch_weight_payload_issuer/README.md).
It removes a separate lane0 branch without adding an election or state.
Pure-load predication/sinking and actual dependency placement remain native
questions. No primary application/freeze/runtime execution has occurred.

**Entry087 full sweep and recovery.** The actual benchmark subprocess exited0
in568.609843636s, started2026-09-10T23:12:45.114158Z and ended23:22:13.724021Z.
After the execution owner stopped responding, root performed one read-only
managed-h status check26099 (true0), confirming all13 rows and the saved
execution result. Integration was interrupted; iteration_prep took over
closure/download/one reader/one comparator. No benchmark or validator was
repeated. The original outer launcher ID/exit remain unknown/null in receipts;
underlying subprocess exit is not relabeled as outer-wrapper success.

Saved source/native/idle closure `c52c7bcfe0700267f3d924fe6bc309972eca542ad672f96bc868ced6c9119c20`
and reader/comparison pass13 rows,104 compiled and winner records,1300 samples.
Proof `4a7394fcef68e198df7e594389cfe15c76e2ea79a44b3a403a82d7caaef2dd28`;
result `a88fc9bafb7e24cd8c78f958e3b8f00eb6977f5f08fe31936be39f246d59f1ee`;
comparison `9bf7bff70e159d2274c5f520888b63c1ff4f72e9b3781078319c2a58cacc45a4`.
[Complete before/after tables](logs/cu132-recovery0910b-dispatch-weight-after-payload-vs-current-and-retained-comparison-001/README.md).
Over8–4096, latency GM+.069733% vs7da (6/10 lower),+.520489% vs retained61ee
(5/10 lower). All13−.771745%/−.082815%. Root holds promotion and preserves
b9db as the next experiment base. No PR/body update or split run selected.

### Entry088 — remove the post-counter warp barrier

Root applied exact patch `2e064056` in the primary checkout. This is one
`sync_warp` deletion after `flag_tracker.accumulate`; no new condition, state,
knob, phase change or other source edit. [Ownership proof](candidates/w4a16_dispatch_post_flag_sync/README.md)
requires constant phase0, full-mask same-issuer payload-store/read-completion/
next-input reuse, and all existing prepublication/tail synchronization. It does
not treat election as a memory fence.

Frozen source `4bfbe75be7011d7ff9b8f55305452b474e2d82480f447154792d15295b5a8dd9`,
manifest `ae9725dd99071da51a474bd919f098216f8cad07f7ace7d613cf08863ee75a35`,
delta `857463e04714d1a167fb3cff9fd2816c26e2d997dd3d65c4c5340d3a1fba582a`,
stage `4f5908acdbf30196c2e930757a625a48d292f24904c87edcf9c90f96cce40618`.
Transport is8eefb5eb. Sole remote owner iteration_prep is authorized to stage
immediately, reuse actualb9db native3 controls, and run native review → shared
numerical14/38 → fullAUTO13/8/100. Primary whole BEFORE is completeb9db
4a7394fc/a88fc9ba; retained61ee7b23/effe remains the separate joint-retention
control. Parallel native driver stays unchanged and will record wall time;
no serial recapture. Older integration remains interrupted.

**Entry088 native admission.** Stage8064/install2518/preflight43146 and
fetch91355/76398 exited0; actual preflight
`271ebf45d6345134b4a1da5bb583ada0bfb4ae3277bc5dd943a33ce1efafdcbc`.
Parallel native31714 and runtime stage73658 passed. Three captures and exits
were fetched; `/usr/bin/time` was unavailable, so the unchanged driver ran
without that wrapper. Missing elapsed-stderr fetch50960 exited1 and is
preserved; there is no wall-time inference or capture repeat.

Independent native3 review passes: exactly one PTX warp sync and one native
WARPSYNC/ENDCOLLECTIVE recovery block removed, eight fewer SASS instructions
per case. Config/stages/REG96/640/LOCAL0/STACK0 remain exact. Required full-mask
elections, full/READ waits, releases, initialization,20 CTA barriers and tcgen
operations remain. Some register-only phase/index updates move before release
without depending on tracker phase0. Mainline routing-weight dependency and
the conservative election-recovery qualification remain unchanged.
Source/native/idle closure79113/fetch85290 exited0. Shared numerical14/38
launched94762 immediately after admission; full13/8/100 follows. Actual runtime
stage888d37c5, source-bound helper-map68d2e047 and receipt8d39d800 preserve the
three narrow identity substitutions; pure reader-loada78c8546 passed once.

**Entry088 numerical completion and AUTO launch.** Numerical94762,
closure46487 and fetch30696 exited0. Summary7f0fd26a confirms standard8/32
plus large6/6, all38 REG96/640/LOCAL0/two decode groups. Closureb1cb2aa5
confirms source4bf/nativef13fed and idle GPUs. Full13/8/100 AUTO launched66788,
run `cu132-recovery0910b-dispatch-post-flag-sync-default-auto13-direct-001`.
Primary wholeb9db and secondary retained61ee remain unchanged; no split run.

Native completion466da5b0 and independent reviewb22a7a1a are sealed. One local
comparison attempt received a directory instead of `sass.txt` and failed before
reading any SASS or producing a comparison. The original comparator then ran
once per actual pair. The failure remains recorded in
`execution/native-comparison-input-failure001.json`; no native capture was repeated.

A bounded follow-up source audit found no further credible per-token barrier
removal after the elected routing-weight writer. Remaining input completion,
one-pending-write drain, ordinary-store publication and return handoff edges
have live consumers. Moving expect_tx into input election is source-plausible,
but actual issue/arrive are already close and no operation is eliminated.
Earlier BAR1, null-tracker and tail-fence negatives remain applicable. This is
a source conclusion, not a throughput claim; no additional trial is selected.
[Audit8888714f](candidates/w4a16_remaining_transport_overlap_4bf.md).

**Entry088 completed sweep and retention.** AUTO66788, closure48848 and
fetch74176 exited0. Wall564.711888067s (2026-09-10 23:44:47.380–23:54:12.092 UTC).
Source/native/idle closure9efcbda32b956962ac8c50c3ef26436965266b918aa30de3d97c479983db52c3;
proof93dad2ac2ac31f2bcb5d139f1ec184f8f0d95402795a4703c60c5e7786d2d1c6;
resultdc8f77197925228e211c3019a2df8241198f0fdcd1fc1b37f30e0f975b8f236e;
comparison40d4faa7ec60e24a359a3290c32388253fc63fd52928ceb285198929485fbba5.
Single reader/comparator passes13 rows/104 compiled and winner records/1300
samples. Over8–4096: latencyGM+.863031% vsb9db,2/10lower; +1.388013% vsretained61ee,
2/10lower. All13+1.189782%/+1.105982%. [Full tables](logs/cu132-recovery0910b-dispatch-post-flag-sync-vs-current-and-retained-comparison-001/README.md)
SHAd322537a. Root holds promotion and uses4bf only as refinement base; no
PR/body/split update or benchmark repeat.

### Entry089 — one elected writer for payload, provenance and routing weight

Root applied exact two-line patch29abf56a in the primary checkout. It moves the
scalar routing-weight STG into the existing payload/provenance election after
commit, deleting a separate lane0 branch. Warp-uniform scalar/address/slot and
disjoint warp ownership retain exactly one same-value writer. The ordinary STG
remains protected by existing prepublication/tail sync; bulk commit itself is
not an ordinary-store fence. No new election/state/knob or value coercion.
[Source proof](candidates/w4a16_dispatch_weight_payload_issuer/README.md)146badad
and prior mainline versus divergent-election dependency qualification remain
explicit; consumer movement could sink/predicate the load and must be inspected.

Frozen source03459447d3e5375745a385056ca59c29d6730e4278829c5a9b39cd89493f3572;
manifestcdaeaf7d7225b310ccfde7d31eac6380caa031254e510c7b08116b23fd27c3c0;
deltad6af8e55fa7e5c4f36a753a7162282b2ff13b36f522f7499caf6eb924c4c1f0c;
native stagea3abc19f43fd673decbb2b9a47418829728a6442095f61b83eef126aa5908283.
Transport8eef→41bf; exact single-file delta frozen once. iteration_prep remains
sole remote owner, source stage64336 active. Native3 reuses actual4bf BEFORE;
unchanged numerical14/38 and fullAUTO13/8/100 follow native/source/idle closure.
Whole4bf93dad2ac/dc8f7719 is primary BEFORE; retained61ee stays separate. No split
or baseline rerun. Reviewer binds the three existing runtime templates while
native work runs; validators and arithmetic remain unchanged.

**Entry089 staging/native capture.** Source stage64336/install55731/preflight9403,
runtime stage40213/fetch82518+21742 all exit0; actual preflightc78257b4. Runtime
stage54b47c65/map204300fb/binding441cf0f9 preserves the three narrow substitutions.
Pure reader-loadd6f9ba8f passed once. Parallel native48943 exited0; native3/exits
fetch34905/97079/20300/1444 and elapsed fetch13144 all0. The tiny inline stdlib
wrapper measured17.369935244s for the unchanged driver subprocess, child exit0.
Prior serial/parallel walls were not saved, so this is not a measured speedup.
Actual source/native/idle closure38298 and independent native review are pending.

**Entry089 native admission.** Independent native3 PASS: the elected scalar
STG follows payload/provenance/commit before BSYNC, with no separate lane0 arm.
Pure LDG remains early/unpredicated; first mainline scoreboard5 result wait is
at the delayedSTG. Existing divergent-election recovery still has0x24 and
is not claimed to preserve overlap on every CFG path. No side-effecting load
wrapper is needed or selected. N64F4/F1 remain5488/5440 instructions; N128F8
6200→6192. REG96/640/LOCAL0/STACK0/config/stages remain exact. Source/native/idle
closure38298/fetch72449 pass816dcc3f. Shared numerical14/38 launched18123.

**Entry089 numerical completion/AUTO launch.** Original18123, closure68365 and
fetch62416 exited0,14 rank-cases/38 compiled objects PASS. Closure
9c9b5eba346fa28642b927dce8e8f5d717ae855382e9a02b6856d928b86d9047 binds exact
source0345/nativef13fed and idle GPUs. Native completion31f43b7d/independent
review00f3b145 preserve the mainline/recovery qualification. FullAUTO97992 is
running `cu132-recovery0910b-dispatch-weight-payload-issuer-default-auto13-direct-001`,
unchanged13/8/100 with primary4bf93dad2ac/dc8f7719 and separate retained61ee.

A held guarded restoration package is prepared at
`candidates/w4a16_dispatch_transport_restore61ee/`: delta75f9476c, stage1194a0c9.
It targets exact61ee through only the three tracked source files and deletion
of the archived owned token_comm. Nothing is restored/staged before the result.

A broader source-only two-buffer input-pipeline design is being evaluated in
`candidates/w4a16_dispatch_pingpong/`. It trades scratch storage against raw/B
ring depth, must preserve phase/layout compatibility and current supported
shapes using constexpr fallback, and has no selected source or timing claim.

**Entry089 completed performance decision.** AUTO97992/closure1751/fetch22744
exited0, wall568.126318033s. Source/native/idle closure
8236616b45295860d15bc640991566311a8cfde906a24c47f36517857e506bbe;
proofceab13caf1c4b7d23a505305040448ab6dd4bad555aa50e4b63f6feb7c760d47;
result46f0535a00815f202d9e55b4332d623f559f85ab8693488d26dd92ba83fbef88;
comparison319232690dc46f4eb48607c78681fd44df7591deca933c75dd1504ec6e0d6551.
One reader/comparator passes13rows/104compiled+winner records/1300samples.
Over8–4096: latencyGM−1.236098% vs4bf,7/10lower; +.134758% vsretained61ee,
6/10lower. All13−.201608%/+.902145%. [Complete table](logs/cu132-recovery0910b-dispatch-weight-payload-issuer-vs-current-and-retained-comparison-001/README.md)
SHA89b590b3. Root holds combined transport promotion, retains0345 as the next
refinement base, and does not update PR/body or run a split/control repeat.
Numerical summary78fffbfc confirms14/38 allREG96/640/LOCAL0/two-decode/61440pool,
including actual41bf large7108/0-route cases.

### Entry090 — received-token bound avoids exhaustion scans

Selected source proposal42dbb68c at
[candidates/w4a16_dispatch_total_bound/](candidates/w4a16_dispatch_total_bound/README.md)
adds a constexpr lane sum of already-cached per-expert counts, one full-warp
`warp_redux_sync(..., "add")`, and replaces the outer loop guard with the
received-token bound. It avoids idle-warp/final suffix cursor scans; valid-token
mapping and all payload/publication/return ordering remain unchanged. No count
reload, workspace, API restriction, defensive fallback, knob or extra per-token
branch. Nonnegative-count reassociation inherits the existing Int32 prefix/index
domain. Empty count lists/ranks preserve phase0 and the old tail. Root reviewed
proofce9d4592; no earlier equivalent trial found in the bounded ledger search.

This is currently selected source-only (+10/−1), base transport41bf→199a9c28.
Primary has not yet changed. iteration_prep prepares minimal native3/reuse
metadata, then root will apply/freeze. Whole0345ceab13ca/46f0535a is primary
BEFORE; retained61ee remains separate. Native review must check reduction
placement/participation, unchanged protected operations and resource pressure.
The existing numerical14/38 cohort covers empty/skew/F1/F4/F8/tail boundaries;
full13/8/100 will determine retention. No split or baseline rerun.

**Entry090 applied and frozen.** Root applied exact42dbb68c to primary and ran
the existing freezer once (only its proposal-root literal changed). Source
64a81ed859ecf81c6e91dd8816cd2eceb1be5d397303faca84dcab58376a6e5a;
manifest1fd5d00d9a310729b467803e86d67dc747ea5aaf6fff032eb20e4f50638f771d;
deltaef53c7c10c3ade5db9bb7ae1bc0c7deb64daef9313b6b40f1330cda755a5bc97;
native stagebe1f775b6cd5551298393bec457a9abe54a4f018d67d286ab2fe1878e49cce28.
Native helper mapcbabf61f/freezer8ea50c65. Exact one-file transport199a9c28.
iteration_prep is authorized to stage/capture/review, then unchanged14/38 and
13/8/100 after ordinary closures, without another root gate. Actual0345 native3
and complete0345 AUTO are controls;61ee remains separate. Reviewer binds only
the three runtime templates while native runs. No split/control repeat.

The independent [two-buffer design note](candidates/w4a16_dispatch_pingpong/DESIGN.md)
7159ff78 confirms source-derived N64raw3/B3=220544B and N128raw2/B2=218496B,
with57376 additional scratch/barrier bytes. READ0 is necessary before input
reuse because that plane can belong to the newest output group; a separate
full wait1 bounds outstanding destination groups. It preserves plane0 return
layout/phase and requires largeH constexpr fallback. Small workloads often
have no lookahead work and would still lose GEMM stages. No two-buffer source
or runtime experiment is selected; the total-bound cleanup takes priority.

**Entry090 capture launch.** Stage17622/install75893/preflight21108/runtime59224
and fetch96527+62331 exited0. Parallel native3 launched2704 with unchanged
driver/ABI/cases and inline elapsed wrapper. Actual0345 captures are BEFORE.
Runtime stagee3a66f0e/map88898896/binding8851dc8f preserve the three narrow identity
substitutions only. Native quality, numerical14/38 and fullAUTO are pending.

**Entry090 native capture completion.** Native2704 exited0. Native3/exits fetch
16363/97966/11273/63340 and elapsed27969 passed. Same-scope inline driver wall
13.245422677s, child exit0; differing source captures do not establish general
compile speed. Pure reader-load43abbbd5 passed once against preflight8096e41c.
Source/native/idle closure13345 and independent native review are pending.

**Entry090 native admission.** Independent review passes all3 captures: one
startup full-mask add reduction and actual token/total guards at initial and
steady entries, unchanged valid inner mapping/token stride/phase/tail. Protected
PTX operation sequences are preserved modulo register renaming, not whole-SASS
byte equivalence. N64F4/F1 each add8 instructions, N128F8 count unchanged.
Resources/stages/grid remain exact; routing LDG first mainline wb5 wait remains
at the post-payload elected scalarSTG, with earlier recovery0x24 still qualified.
Closure13345/fetch50440 passf5745a41; shared numerical14/38 launched76559.

**Entry090 numerical completion/AUTO launch.** Original76559, closure99372 and
fetch61980 exited0,14/38 PASS. Closure39fa3e216d95d6834cec76940c67f8b81a02cb5393c1ba1de59a42df7a421152.
Native completion317fe20b/independent review1a8c76df sealed. FullAUTO5672 is
running `cu132-recovery0910b-dispatch-total-bound-default-auto13-direct-001`,
unchanged13/8/100 with whole0345ceab13ca/46f0535a and separate61ee control.

Held follow-up1ec5e789, proof04d739bd, in
[candidates/w4a16_dispatch_total_bound_no_exhaustion_checks/](candidates/w4a16_dispatch_total_bound_no_exhaustion_checks/README.md)
removes exactly the prefix loop's expert-bound conjunct plus count-fetch and
token-body expert-valid wrappers. The total bound/nonnegative prefix invariant
guarantees a valid containing expert, including zero prefixes and strided
jumps. All-empty work skips the existing outer loop; phase, tail and tracker
addresses remain unchanged. Expanded AST is exact after those three unwraps
and one invariant comment; textual+193/−196 is predominantly dedentation.
Current64a8 native retains all three guards, so this is not claimed already
elided. Native/register/performance costs for the held source remain unknown.
Root reviewed whitespace-insensitive diff and proof. Reviewer prepares minimal
held reuse metadata, with no source apply, imports, remote or GPU action.

Held three-guard reuse packagec83bc40c is ready: freezerbe0b621f, native map
09a30ca6, helper map6c298658/preparationf0105556. Actual64a8 native controls
are pinned; the whole64a8 AUTO fields remain unbound until completion. Root
inspected existing public coverage instead of adding tests: sparse scale/routing
uses routes[0,E−1], yielding a leading-zero prefix on rank1 and trailing zero on
rank0 at EP2/E4; reference schedules refill through skew/empty-source/all-empty
rounds. Large cases add13/12 pulls per warp and F1/F4/F8 tails. The unchanged
14/38 cohort remains appropriate; no new harness or validator replay is selected.


**Entry090 infrastructure interruption and recovery.** AUTO5672 outer exit1
included remote wrapper137 without the end marker. Underlying benchmark exit
and completed-row boundary are unknown. A later managed progress call failed
before remote execution because fi-w4a16-mega-0910b was not found. Managed
listing40979 exited0 and showed no ziangli/c2 devboxes/jobs (35 schedulable,
117 allocated, 3 disabled, 156 total). The evidence establishes disappearance,
not its cause. No complete sweep was downloaded, reconstructed or compared;
no closure/reader/comparator was invoked for the interrupted run. Saved receipt
[candidates/w4a16_dispatch_total_bound/execution/auto-interruption001.json](candidates/w4a16_dispatch_total_bound/execution/auto-interruption001.json)
SHA cb7a1ef0aac4b5699d5c30f6d31c64d07ab09fdfc597e24fa36ebee916d485f1;
status0748b4ee, entry logfc32f948, listing3ae4f57d. Native3 and numerical14/38
remain complete with their original provenance; no performance claim is made.

Root rechecked the live [NGC catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch)
and [26.08 release matrix](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html)
immediately before authorizing recovery. Catalog latest is26.08-py3, updated
August28;26.08/26.07/26.06 useCUDA13.4.1/13.3.1/13.3.0, so the newest CUDA13.2
release remains explicit nvcr.io/nvidia/pytorch:26.05-py3 (13.2.1.009).
iteration_prep is sole request/setup/execution owner, using managed
/usr/local/bin/h from the project HAI checkout, c2 B300, bare, no size, ziangli
first. Actual replacement node/UUID/compiler identity must determine whether
old hu-pdx-129 controls are reusable. Current primary64a8 and the held
three-guard patch are unchanged. No source/PR commit or split sweep selected.


**Replacement0911a progress.** Managed request48271 exited0 for
fi-w4a16-mega-0911a (ziangli/c2, B300x8,26.05-py3,bare,no size or queue override).
Identity20841 exited0 and records the same hu-pdx-129 node and all eight GPU UUIDs
as0910b. Driver590.48.01 and idle120/3996MHz,1100W,persistence/default-compute
match, with no GPU applications. Identity56ca889f and continuity3cd2ef5e preserve
this observation. Stack equivalence is still pending; the new container lacks
the prior checkout/caches. Published773c/61ee bootstrap93921 completed after
helper staging26289; setup55156 is running. No timing baseline is rerun solely
because the pod name changed. The exact frozen64a8 overlay is prepared without
changing primary. A fresh distinctly named fullAUTO may replace the interrupted
attempt only after loaded-stack comparison; completed native/numerical evidence
is retained with its original run identities.

**Held next design: compact rank peeling.** Root prepared
[candidates/w4a16_dispatch_rank_peeling_loop/](candidates/w4a16_dispatch_rank_peeling_loop/README.md),
patch6a6c297f, on the held three-guard transport4a27. Proposed transport6ff2b21c
replaces compile-time world_size+1 round duplication and its repeated runtime
`decided` guard with one `while decided == 0`; the entire body is AST-identical.
Current64a8 N64/F4 native shows nine VOTE/MIN bodies and eight subsequent
BSSY/decided-branch/BSYNC regions even after first-round success. This motivates
a control/code-size experiment, not a measured gain. Monotone positive count
peeling removes at least one rank per unsuccessful round, so it terminates
within the old world_size+1 bound and keeps full-warp collective participation.
No mapping arithmetic, payload/wait/release, scratch, GEMM stage or knob change.

The proposal also adds one `uneven_sources` round to the existing public
`_check_numerical`:5 tokens on rank0 and17 on rank1. This creates per-expert rank
counts3/9 or2/8 and forces a second nonempty peel for later slots. The same
independent oracle, tolerance, layer and workspace are reused. Existing fixtures
have equal counts or one empty source and do not demonstrate that loop boundary.
No primary apply, native capture, runtime helper change or test execution yet.
Independent source review is requested after recovery binding preparation.


**Recovery0911a baseline boundary decision.** Setup55156 and fetch96819 passed.
Actual environmentd995c513/continuityb282fdfc matches13 compiler/loaded-library,
package, Torch/CUDA/CuTe/NCCL and profiler fields. Exact source64a8 stage71599
failed before writes because the declaration pointed to an absent old manifest;
corrected declaration-only stage63189, install54692, preflight68299 and fetch51408
passed. Installb0865e94/preflight568a433c bind64a8. Runtime stage56101 passed;
existing support builder71953/fetch19043 built/loaded FP4 quantization in110.0476s
and fused routing in21.1124s. New inventory85d7e44b differs in12 .so/.cu.o/build
records from oldf13fed; source/compiler and .so sizes match, most host .o files
are exact, but native executable equivalence has not been established.
Old0910b .so hashes are absent from all three local native-cache backups. No
archive extraction, comparison against a substitute old binary, or broad rebuild
was used. Source/native/idle closure63902 passed for the new build.

Root chose one fresh retained61ee/published773c full Mega-only13/8/100 baseline,
followed by restored64a8 on the same new support inventory. The64a8 result will
measure the complete unpromoted transport chain versus retained61ee, not an
isolated received-total-bound change versus old0345. Subsequent decisions reuse
these same-build complete controls. This is one control reset after recovery,
not a baseline per trial. Historical0345 and old61ee tables retain their original
native provenance; their mixed-build microdifferences are not retention evidence.
Primary64a8 remains inspectable while the sole remote owner uses exact guarded
61ee/64a8 source snapshots. No new numerical/native3/profile/split sweep selected.
After AUTO closes, the existing native-cache backup workflow will preserve the
new support build locally for faster future recovery; no compression during timing.

**Later wait-scheduling proposal.**
[candidates/w4a16_dispatch_read_wait_before_overwrite/](candidates/w4a16_dispatch_read_wait_before_overwrite/README.md)
patch604b58bf, transport6ff2→ed6b90d6, delays the F>1 source-read wait until just
before the next input overwrites scratch. Tracker bookkeeping and immutable
prefix/rank selection may overlap that read; all full publication/tail waits
and synchronization remain. It adds empty READ waits at first/after-full-batch
iterations, removes the old else arm and adds no runtime state/condition. F1 is
unchanged through constexpr selection. Independent source reviewa94a5a75 passes;
actual native placement/resources and performance remain untested. The linked
PTX specification was checked live for source-read versus destination-completion
semantics. No primary edit or execution. Rank-loop reviewe549d17c also passes;
its unchanged mapping and added5/17-source fixture are ready for a later trial.


**Fresh retained control launch.** Reverse source stage45500 and restore76148
passed, restoring exact published61ee on remote only. Preflight42146/runtime
stage11801/source-native-idle66914/fetch71900 passed. FullAUTO40802 is running
`cu132-recovery0911a-retained61ee-default-auto13-direct-001`, command0d79bbd0,
preflight53670902,newnative85d7/env7025, historical exact61ee8/32closure50c7039a.
This is the sole GPU workload; no cache archive compression/download is concurrent.
The control remains incomplete and no final reader/comparator has run.

**Held proposal formatting before execution.** Root checked the proposals
with the repository-pinned Ruff0.12.8 (pre-commit revv0.12.8), formatted the three
transport snapshots and propagated formatted predecessor bases. AST equality
was verified for every old/new source; original snapshots, patches and notes
remain under each candidate's `before_format/`, with `formatting.json` receipts.
The added public test was already formatted. The four proposed files pass pinned
Ruff format-check and lint. No primary or runtime-source mutation occurred.
Current no-exhaustion transport199a→b848151a, patcha5563156;
rank-peeling b848→85f21176, patch4f22b8ac (test change preserved);
late-READ85f2→f3b43320, patch245be199. Existing independent source proofs apply to
the same executable AST; native quality remains untested. Reviewer refreshes
only current held snapshot maps/digest notes. This avoids changing trial source
identity after a performance run merely for formatting.


**Fresh retained control complete.** AUTO40802/closure7708/fetch22112 all exited0.
The saved reader ran once and passed13rows/104compiled/104winner records/
1300samples. Wall565.2958466s; same protocol3warmups/100cold-L2CUPTI samples,
primary per-iteration rank-MAX activity-span median,8 tactics. Whole proof
29b1e822539f2a9d4037fc8da2c806cc1e49cba0f2cafd7a3d7219217e35537c;
resulta0e022f96b26de51ed77c0b05f8c9bbd4231e4264ed558fdc8222c9354f9378a;
source/native/idle closure8c93898bc3d92c3a0d580c47b6cf85b6d380ddb55cc3a543b87d882eda19c718.
Artifacts: logs/cu132-recovery0911a-retained61ee-default-direct-auto-reconstruction-001/.
All13 global powers-of-two token rows1..4096, ms:
.073505,.103809,.116896,.140624,.155264,.178401,.203889,.206945,.209217,
.209874,.232737,.310850,.468179. These are one complete retained61ee invocation
on the rebuilt native85d7 libraries. No mixed-build derived gain is claimed.
Exact64a8 reapplication follows; reviewer binds its three standard templates to
this whole control. No source promotion, PR edit or split refresh yet.


**Recovery64a8 sweep launched.** Exact61ee→64a8 install28885, sourcepreflight85850,
48-file runtime stage29358, source/native/idle21183 and fetch29571 exited0.
The support native85d7 inventory is byte-exact across the completed61ee control.
Actualpreflight5268b5e3; distinct fullAUTO79283 launched
`cu132-recovery0911a-dispatch-total-bound-default-auto13-direct-001`,
command4283e5e7. Same13/8/100, new whole61ee29b1/a0e0 as primary control;
old61ee is historical context only and old0345 is removed from this promotion
comparison. Same-source64a8 native3/numerical14/38 evidence remains explicitly
reused from0910b, with matched compiler and no new numerical/native cohort.
No cache backup, profile or other GPU workload overlaps timing.

Formatted held maps now bind current proposed bytes: no-exhaustion native
9954f43a/recoveryfull704b3943, unchanged freezerbe0b; rankloop nativef5a20251,
freezere5b316c0. Previous maps/handoff notes are archived underbefore_format.
The next no-exhaustion proposal remains unbound to pending64a8 performance and
unapplied; root will apply/freeze after a complete current result.


**Entry090 same-build result and decision.** Original79283/closure88226/fetch86811
all exited0; wall562.989909s. Saved reader and comparator each ran once and pass
13rows/104compiled/104winners/1300samples. Proof
a4ab91d1399cdc5d34baf237f40f1fb6809fcd573f8ce97270086c105f91158a;
result5dffdb7abdf1637ad7fbd3d5d38b42391da42aeec5111f4f41d9701d4ed2efd8;
closure8fa28b046c25b92020bf77e88ed98297c03895a959ed2af8fa2f6ab012846ccc;
comparisondc097500acbc567d0a922f248435474d3f5b064788feb4acdaa9847415597bf1.
Fulltable logs/cu132-recovery0911a-dispatch-total-bound-vs-same-build-retained-comparison-001/README.md,
SHAdb6ec32198b4ab6b292718b11b74e9734076a433073443ce9b99aa65b017a0e8.
Over8–4096, latencyGM−1.211942% vs freshsamebuild61ee,6/10lower; all13+.021177%,
6/13lower. T128+5.575% with the sameN64/F4/epi tactic is a material mixed result.
Root holds combined-chain promotion, keeps64a8 as a refinementbase and proceeds
with general dispatch cleanups. No shape-specific fix, PR/body update, split
refresh or timing repeat selected. Historical61ee+0.084400%8+ is separate and
not retention evidence. Candidate ms1..4096:
.080033,.104304,.121041,.134113,.147377,.171698,.203169,.218482,.204722,
.204977,.232913,.312053,.470949.

### Entry091 — remove redundant dispatch exhaustion checks

Root applied exact formattedpatcha5563156 to primary and ran the existing
freezer once. Source
d78808f4a7573a0f6e36be6e369c14c4f925299ae22201ef7d9621a5be94668a;
manifestb85f584ce13e2e2616ec684de966a2977f113f93fea9f3bfb74a04bd2e92513c;
deltac77f0da00e03a10be1828e10b4f587af877021bf764b889626f693cf1c494d72;
stage96f50fb78ce1744be138e0822f1fc164e99d0996d4db9090d80a9b97d42d3713.
Sole source change: ownedtoken_comm199a→b848151a. The outer total bound guarantees
a containing expert, so the prefix-loop expert-bound conjunct and count-fetch/
selected-token expert-valid wrappers are removed. All mapping and publication
operations remain in order; no runtime fallback/state/knob is added. Existing
proof and AST-equivalent pinned formatting were reviewed before application.

After the approved idle support-cache backup, iteration_prep stages/installs,
captures standardparallel native3 against compiler-matched actual64a8 controls,
obtains independent review, then runs existing14/38 and full13/8/100 without an
extra root gate. Newwhole64a8a4ab/5dff is immediate BEFORE; fresh61ee29b1/a0e0
remains separate. No baseline/split/profile repeat and no guard performance
claim yet. Runtime binding proceeds concurrently with native capture. Primary
is visible for user inspection; all earlier source artifacts remain preserved.

**Entry091 native admission and recovery backup.** The support-cache archive
completed3997 and downloaded66521, both exit0. Archive09d57636c1e85695ee246a02c4c7a80f439c6bd30a3313ef363c4a4fd00a3356
has2,882,586bytes undernative-cache-backups/cu132-recovery0911a-support85d7-001/;
receipt459be14b recordsunchanged64a8/native85d7 and restore_validated:false.
No archive operation overlapped timing and no restore was performed.

Entry091 stage74426/install12916/preflight40937/runtime92938/fetch1994 all
exited0. Actualpreflighteb888bcf; runtimee803c97f binds67files. Native3 original
83086 and all five downloads completed0. Independent review2128140c passes:
N64F4 5496→5480, N128F8 6192→6184, N64F1 5448→5432 instructions. Config,
REG96/640/STACK0/LOCAL0, SMEM200064/230784 and raw/B/D stages stay exact.
The obsolete exhaustion guards disappear while initial/steady total bounds,
prefix/rank mapping and normalized protected transport sequence are preserved.
RoutingLDG still waits at post-payload weightSTG on the mainline; election
recovery retains an earlier wb5 wait, so no unconditional overlap claim.
Native source/cache/idle closure70257 passes2c1c2f8f. Unchanged numerical14/38
started50588; no numerical or timing result exists at this update. Full13/8/100
follows after success, using whole64a8a4ab/5dff and separatefresh61ee29b1/a0e0.


**Entry091 numerical complete / AUTO launched.** Original50588, closure91690
and fetch39662 exited0. Unchanged14rankcases/38compiledobjects pass, closure
21a58573; numerical source/native85d7/idle checks pass. FullAUTO94214 started
cu132-recovery0911a-dispatch-total-bound-no-exhaustion-checks-default-auto13-direct-001
with unchanged13globalpowers-of-two rows,8tactics,3warmups and100cold-L2CUPTI
samples. Whole64a8a4ab/5dff is the immediate BEFORE and fresh61ee29b1/a0e0 the
separate retained comparison. No completed current timing result or promotion.

Held rank-loop recovery preparation is complete: validation_recovery0911a/
HANDOFF.md0b5bb5bb, fullmap9817eb2a and native-controls66a00909 bind actuald788
captures. The two-file patch retains the independent oracle and adds the5/17
uneven-source round inside existing layers; numerical/reader bodies need no
adaptation and expected14/38 remains. Source/performance fields requiring the
future completed run remain unbound. Root prepared held late-READ freezerd51e39fe
by changing only the proposal root of the established guard freezer; it has
not run. The PTX elect.sync contract was checked live and linked in its README:
same member mask deterministically elects the same issuer, with no extra memory
fence claim. No primary source change or additional GPU work was selected.


**Held follow-up scope and rejected polling direction.** Root prepared
candidates/w4a16_dispatch_nonempty_rank_round/ after the held lateREAD source:
basef3b43320→target55650c3c, patch39efd6cf. Every compact-loop round retains
0<=slot<sum(remaining source counts), so the active-count guard/empty fallback
is unreachable; only the nonempty branch body is promoted. AST scope and pinned
Ruff format/lint pass. Independent source review is pending, no primary edit or
execution selected. This explicitly depends on compact early loop exit and
must not be applied directly to the still-unrolled mapper.

Independent polling audite7c014fd is saved at
candidates/w4a16_readiness_polling_audit_d788.md. No polling patch is selected:
first acquire is immediate, sleep follows only failed conditions, and actual
saved T1024 PC evidence supplies no positive FC2 polling hotspot. A smaller
constant changes retry pressure; BF16's different wait/mapping is precedent,
not W4A16 performance evidence. The nanosleep argument is approximate time,
not exact cycles despite the existing helper name. Main priorities remain
compact rank selection and late scratch READ wait, with no new public knobs.


**Entry091 complete / decision.** Original94214, closure72065 and fetch67698
exited0; wall565.251130785s. Saved reader/comparator ran once each, validating
13rows/104compiled/104winners/1300samples. Proof
d094203c2e6a39cef8e4bd0ceb1e8e55b01d6cecc433a01a5a5b13da8cae1c81;
result59f0a00d610ca161762c528c81e877083cd7f7af335464f3853c24ef47e76135;
comparisonfae757698ef87c1790a9df5ecbd80797eb1bc3c6d6522692d017fa7d1b584990;
closure70a7262c/completion8156b128. Fulltable2835a888 is
logs/cu132-recovery0911a-dispatch-total-bound-no-exhaustion-checks-vs-current-and-retained-comparison-001/README.md.
LatencyGM8+ +.988840% vs64a8,3/10 lower; -.235087% vsfresh61ee,7/10 lower.
All13+.878661%/+ .900024%,4/13 and8/13lower respectively. T256+8.902% vs64a8
and+6.562% vsretained61ee is a material mixed row. Root holds promotion, keeps
d788 as refinement base and proceeds with general compact rank selection.
No shape-specific adjustment, PR/body/split/control repeat. Candidate ms1..4096:
.084960,.107825,.112002,.139842,.154881,.173713,.192673,.205633,.222946,
.208913,.232449,.312514,.473363.

### Entry092 — compact dispatch rank selection

Root applied exact formattedpatch4f22b8ac and froze once. Source
71a1b68888f3d1d114e82c28489fc141037d6ab6214472790fa71a6de5300db8;
manifest81193dfce3d84f08029ae29935241fdf647975eefb32ca3bfc9a4596818ba1b8;
deltacf47b1c1eb65bf9f9f1b00fd7db1ca3695927652afec530f5766f846dfeb5bc7;
stage57bfdd58ad6b90a507b56c4872d5130ebdd67d1c55b49d553a95ce1623676900.
Only ownedtransportb848→85f21176 and publictestb7cc→5675d34f change. The loop
body, token mapping, payload/flag/tail and pipeline resources are unchanged;
one early-exit loop replaces repeated guarded unrolled rounds. Existing test
layers/oracles gain an uneven5/17 source round that exercises a later peel.
Expected14/38 counts remain; no new numerical harness or tolerance is added.

iteration_prep remains sole remote/GPU owner. Stage/install/preflight, native3
versus actuald788 captures, independent review, numerical14/38 and full13/8/100
are authorized sequentially without an extra root gate. Reader/helper binding
uses completedwholed788d094/59f0 immediate BEFORE and separatefresh61ee29b1/a0e0.
No baseline/nativecontrol/split/profile repeat. Primary source is visible for
user inspection; no native, numerical or performance outcome exists yet.


**Source-proof correction for held nonempty-round cleanup.** Independent review
41873cab and the proposal README now correctly state that old unrolled decided
checks also skip all later bodies after success. Only repeated guards remain;
there is no executed empty-body suffix. The nonempty-body invariant needs that
decided gating, not specifically a while loop. Patch39efd6cf still mechanically
uses the compact/lateREAD predecessor, and all proposed source bytes are
unchanged. Metadata consistency is source-traced to the same dispatch-barrier
status records supplying per-source counts and the expert sum. No trial or
validation was rerun for this documentation correction.


**Entry092 native admission.** Source/native stage77517, install30390,
preflight7935, sourcefetch27592/4537 and boundruntime14278 exited0. Actual
preflight21efd405; runtime6fa0d945 binds69files, helper4c56c10f, binding8e22d625.
Parallel native20438 and fivefetches81092/1843/50285/77138/15155 all exited0.
Original comparator ran once/case. Independent review21d8ea7686039ddd94ceadb149d18aef944fa9dc328de13ca5fb6772543ff51c
passes: N64F4 5480→4464, N128F8 6184→5168, N64F1 5432→4416 instructions.
All3 remove1,016 instructions, retain REG96/640/STACK0/LOCAL0, existing SMEM and
raw/B/D stages. Actual rank mapping is one full-warp round with failed-peel
backedge and successful exit; total-bound/prefix remain. Normalized protected
PTX operation sequences remain exact. Conditional mainline/postpayload weight
wait versus election-recovery earlierwait remains qualified, not a universal
latency claim. Native closure7050/fetch31389 passescc7b694b forsource71a1 and
byte-exact85d7/idle. Pure reader load oncebe929292, final saved reader unrun.
Numerical39884 started14/38 with the new in-layer uneven_sources round; no
numerical/performance outcome yet. No extra capture or benchmark control.


**Entry092 numerical complete / AUTO running.** Original39884, closure52453
and fetch21340 completed0. Saved14/38 summary5f12349f confirms allREG96/640/
LOCAL0/two decode groups; eight uneven_sources markers plus test5675 source
pins establish that the new round ran in both standard geometries/return modes.
Source/native85d7/idle closureb43256136493aa52126d546ddf16a3e7b96680d3021bae19708de887cb0bc552
passes. FullAUTO69639 launched with the unchanged13/8/100 protocol and d788
whole d094/59f0 primary control, separatefresh61ee29b1/a0e0. No fresh timing
result or saved-reader/comparator pass yet; no baseline/split/profile repeat.

Held lateREAD preparation is ready without changing primary: native-helper
959a9b67 (22files), freezerd51e39fe, fullhelperbd2ee276 (60files), actual71a1
nativecontrolsbff9d83b and handoff992a7e46. Target transport85f2→f3b4 only; test5675
remains. Future whole71a1 result and proposed source id remain unbound until
completed. This is preparation, not an extra execution gate or a selected run.


**Entry092 local static check.** Repository pre-commit mypy hookv1.17.1 passes
for the four changed implementation/import-boundary files in0.984s. This is a
local type-check only; primary source is unchanged, no numerical or timing run
was repeated, and the full pre-commit hook set has not been claimed for71a1.
OriginalAUTO69639 has exited0 and the executor is closing/fetching before its
once-only full reconstruction/comparison. No retention decision yet.


**Entry092 full result / retention / publication.** Original69639/closure81390/
fetch65471 exited0, wall537.484839s. Reader/comparator each ran once and passed
13rows/104compiled/104winners/1300samples. Proofae17821694673401b8bb013e4d94f07bb38f2f441c78e03f232012d7d80a6f7a;
result94e1a8c9f18539fa7014a7a00c6b17e2d3518528ce401c820d36962bb9fb2575;
comparisonb41024cf361306c0e7826d4522ef7245fa0fa9a7a173ff9588acc8f9a21fe268;
closure1d61d0eb/completion031840b4. Tablec03945b6:
logs/cu132-recovery0911a-dispatch-rank-peeling-loop-vs-current-and-retained-comparison-001/README.md.
Over8–4096, -.621516%vsd788,7/10lower; -.855141%vsfresh61ee,7/10lower.
All13-.566007%/+ .328923%,9/13 and8/13lower. Versus61ee higher rows are512+1.174%,
2048+.067%,4096+.612%. Root retains whole71a1 dispatch chain as modest gain plus
simpler native control, not all-row improvement or a large isolated causal gain.
Current ms1..4096:
.076080,.102849,.129634,.139922,.151810,.173473,.202353,.201394,.207394,
.212338,.231506,.311057,.471044.

All changed-file pre-commit hooks passed (0.882s), then commit hooks passed.
Commit2699213f62b57dafccec5f8beeed9ef3fee58288 was created and successfully pushed
to fork feat/w4a16-megamoe,773c→2699. Five files,+336/-2 including321-line owned
BF16 transport and one public-test round. All1,583 Git blobs equal frozen71a1;
receipt candidates/w4a16_dispatch_rank_peeling_loop/execution/commit-source-match001.json.
Live public GH read after verifiedzianglih identity confirmsOPEN/draft/head2699;
body3bb7471f equals PR_BODY-local-router-current.md and remains unchanged pending
Final refresh. Evidence logs/pr5019-dispatch-before-body-edit-001.json.

Root reviewed/approved exactly one current-node publication split-only13 sweep:
recovery0911a command0f7ca1ec, finalstage6afc488d (supersedesearlierstageee306297),
reader3ce4de69 delegates existing result/provenance/sample checks. Shared-weight
bridge/benchmark/recorder/launcher are unchanged. iteration_prep alone prepares
the usual absent-output/source71a1/native85d7/idle/originalexit envelope then
runs it; no second root gate, no Mega/numerical/profile repeat. Use complete
Mega94e1a8c9 with the new same-node split result for PR Final. LateREAD is next
once publication baseline closes; no primary or remote source change yet.

**Publication split58069 execution and dependency boundary.** Stage28743 passed.
Original split benchmark completed all13, returncode0 in632.989829s. Wrapper
58069 returned1 at its strict native-inventory equality check, after timing
completed. First split use compiled mnnvl_moe_alltoall/moe_utils/trtllm_utils and
fetched batched_gemm cubin/header dependencies. Actual aftersnapshot53132
returned0: inventoryb5866755141449b8abb6172afc77af071cb7d6305b434ff95d387fa2686de5d2,
integrity65aad148,54 additions and one diagnostic-log change. Every preexisting
85d7 non-log entry is exact,0missing/0changed. Expanded closure/read is pending;
no full inventory equality, failure of underlying benchmark, or timing retry
is claimed. Reviewer independently checks closure/table for the PR update.

### Entry093: move scratch READ wait before the next overwrite

Root applied patch245be199 in the primary checkout and froze only transport:
source d1849fe467c186af7b418be09b69df134bef571e9cf76f462bdb829822f2b858;
manifest c49b098843025f5866f2576819aeb947ccc206fb060467b041bae3d7e183cfce;
delta1088e7dea4686e7c0a628a054875fc2bb79b5ed98168def05be4b3b8ca385794;
stage6b30a89eb17cdf98dc3bcb25633b453d8e2a9a66e30372440e355bd053e48c3c.
The7+/5− patch moves F>1 source-read completion after next-token mapping and
immediately before the elected input TMA reuses scratch. Full publication,
pre-store destination drain and tail waits are unchanged. F1 uses constexpr
exclusion. It adds empty first/after-full-batch waits instead of a pending-state
predicate. Independent source proof is preserved; actual overlap remains a
native/performance question. Public test5675 is byte-exact. No native, numerical
or timing result exists for d184 yet. iteration_prep alone stages/executes after
closing the split run with the inspected expanded dependency inventory. Reuse
whole71a1 proofae178216/result94e1a8c9 for BEFORE; no new control/split/profile.

**Current Final published / source2699.** Split saved reader ran once and passed
13rows/104tactics/1300samples: proofb8d3b2b17d5b7b135feeda252fbbf8890ecdd8cc55934bfa4ed11253cf892b40.
Expanded closure88009/fetch87983 passedf4145df3. Independent inventory/table
reviewb3767051 confirms22old entries,0missing/changed nonlog,1logchanged,54new
(alltoall10/moe_utils17/trtllm_utils9/cubin18). Split ms1..4096:
.076192,.102209,.144177,.163249,.180146,.203809,.225651,.246738,.243090,
.241298,.250850,.350915,.555413. Whole71a1 Mega is lower10/10 over8–4096,
GMsplit/Mega1.156129 (13.504456% lower latency); all13 lower12/13,GM1.126832.
These are separate process runs with shared preparation recipe/residency, not
interleaved paired measurements or a cross-process tensor-equality test.

Root updated PR5019 body from3bb7471f to03cf2d6cea3f530638a9875903b9d09fd2319f0d6a1fdf4743d4cfec1fb561aa.
Verified OPEN/draft/head2699213f and exactbody after original33005 true0. Final
13 rows use whole current-source Mega and current-node split; historicalCUDA13.0
and setup/profile suffix remain exact. All bash blocks parse, bridge AST parses;
standalone public bridge is not claimed executed. Preserved @humansand/template.
Evidence logs/pr5019-dispatch-published-001.json and
PR_BODY-dispatch-publication-check.json. No PR comments or new timing runs.

**Entry093 native admission / numerical running.** Stage92503/install38329/
preflight33704 passed; preflightb7423711 with expandednativeb586 and unchanged
stack. Native87464/allfivefetch passed, actual71a1 controls only. Independent
review finds F>1 READ after prefix/rank mapping and before scratch overwrite;
compiler hoists before source-index LDG, so exact source adjacency is not claimed.
F1 SASS is byte-identical; resources and full-batch/tail publication remain.
Source/native/idle closure37b81a4f passes. Numerical19422 runs unchanged14/38 on
frozen publictest5675. Boundruntimec6dc0f15/receiptcbc41e15 retains whole71a1
proofae178/result94e1 BEFORE. No candidate timing result yet.

**Parallel requested test consolidation.** User asks to merge the five added
W4A16 test files into existing MegaMoE suites, extending Cartesian products and
shared refs with explicit W4A4/W4A16 mode checks (futureW4A8), avoiding bespoke
behaviors not covered by existing suites. Integration owns only primary tests;
root owns review/separate commit. Active remote d184 and test5675 remain frozen
while local tests change; no perf resnapshot/rerun for test organization.

**Concurrent-test boundary for the held next trial.** The local nonempty-round
freezer now snapshots non-test source and exact helpers, overlays only the
proposed transport on the whole actual predecessor manifest, and retains every
base test hash/required path. This avoids racing the independent primary test
refactor or copying/reverting its work. Source-id formula and remote full-source
installer checks remain unchanged. Freezer70cf2f27, native map136f2f6f,
fullmapd8d336a7; original freezer/maps are archived. Local helper lint/format and
AST parse pass. No next trial apply/freeze/stage has occurred; d184 AUTO84724
still supplies the pending decision. This is a source construction boundary,
not permission to silently omit remote tests from validation.


**Entry093 completion and hold.** Numerical19422/closure55018/fetch70762 passed
14/38 (summarycb5959f9/closureb22538a8). FullAUTO84724/closure4538/fetch32319
completed0 in536.463376s; one reader/comparator pass validated13rows/104compiled/
104winners/1300samples. Proof52c95075/result e51c4070/closureafc1b269/
comparison1e761801/completion84f57788. Over8–4096,+0.444494% versus published71a1,
4/10 lower, T32+3.044%; all13+0.878873%. Held as a refinement base, no promotion.
Complete table: logs/cu132-recovery0911a-dispatch-read-wait-before-overwrite-vs-current-and-retained-comparison-001/README.md.

### Entry094 — remove the nonempty rank-round guard

Primary applied/frozen source600cff5f7e179d31f6eec8ba31ee6724046ee9c589fa5164162ba04fd2415776;
manifestc1b1f37a55fb0237b8c44f5db7c6fe0a5cabff5647a16bfe2b78ccdb937c4edb,
transport55650c3c06f62560c0beb4340b6460ea1de9c981250dc21ec8387360c9debfba,
delta1b429824/stagef2bfbc8d/patch39efd6cf. Valid slot remains below remaining
count sum after every failed positive min-count round; every reached round is
nonempty. Remove the wrapper/fallback without state or knobs. The old unrolled
mapper also skipped later bodies after selection; compact looping is a mechanical
base, not a logical prerequisite for this invariant. Existing Int32 domain remains.

Stage40285/install58200/preflight81386/fetch35209 all0; preflight8ee01441.
Parallel native6440 completed0 in16.722464s; all five fetches0. Closure52902/
fetch62821 passed; completion0a9bf5fd. Root native review75e604c8 passes:
N64/F4 4456→4456,N128/F8 5168→5128,F1 4416→4408. REG96/640/STACK0/LOCAL0,
staticSMEM1024/dynamic200064,230784,200064 and raw/B/D stages unchanged.
Protected PTX sequences exact335/380/330. Removes empty-mask branch before
POPC; valid arithmetic/backedge and READ/prestore/publication/tail waits intact.
One print-only KeyError after the first completed native comparison was repaired
without replay; its result was reused and only two unstarted comparisons ran.

Numerical10219/closure75479/fetch64930 all0;14/38, summary67515ae8,
closurea03581c1a774bf71344d6fe4103ca8c240e52b892e42f6d05766e88fb442e07c.
All objects retain REG96/640/LOCAL0/two decode. FullAUTO70617 is active with whole
d184 proof52c95075/result e51c4070 primary, separate published71a1 ae178216/
94e1a8c9 secondary. No row mixing or baseline/split/profile rerun.

**Independent primary cleanup.** Five new upstream test files removed, eight
existing suites extended; public W4A16/W4A4 mode checks are explicit. Shared
shim/autotune.py and W4A4 weights.py restored to exact base bytes, owned timing
implementation moved without behavioral AST changes, private shared exports
removed, and weight API keyword-only restrictions removed. Five production
paths and thirteen test paths changed; no other backend pipeline edits.
Changed-file pre-commit passes including mypy/Ruff. Local collection only reports
46 host cases before three missing-dependency errors; no runtime pass claimed.
Combined real-environment validation is being prepared, after600c AUTO closes.
Frozen600c retains all original test hashes; current primary cleanup is excluded.

**Next held source proposal.** candidates/w4a16_dispatch_two_pending_writes
contains patch5cbe89e6/proposed transportfde0f4d5. Only F>1 prestore fullwait0→1:
READ0 still protects the shared source buffer; at most two destination groups
can remain after commit; full threshold/tail drains preserve publication and
return handoff. Manual F2–32 has the same bound. Existing native3/large14/38
cohort covers the future executed F1/F4/F8 configurations. No primary/GPU changes,
resources or speedup claimed. Root/independent source review supports a trial.


**Entry094 full result / retention / push.** AUTO70617/closure41532/fetch67269
all0;537.570946s. Reader/comparator each once passed13rows/104compiled/104winners/
1300samples. Proofa48e09664d9857cf3ebc0221ae7988c491e32a312accb3ef030460ec0faa8f8c;
resulte862342dfafa3214ab906d4cd86bc502875f5edf89dd1ef12f7d0c65b0b11e48;
closure9030627ab8a7b9a954abec2ce0cb8a0815be3914c97bbd705ec322079fce629e;
comparisonef998a5c89dab43e5b951f168ef4f54402772f345514b3e2318d7067bea3e7b7.
8+−1.119975% vs whole d184,6/10 lower;−0.680459% vs whole published71a1,5/10
lower. T8−9.823%,T32+2.685%,T128+2.264% vs71; mixed, not isolated causal speedup.
Root retains modest result and simpler rank selection. Kernel-only commit
597b797be0c96b4bcb634163a4f62adb176ebe35 passes hooks and matches all1,583 frozen600c
blobs; pushed normally to fork branch. Source match and retention receipts saved.

Current Final table derives600c and unchanged whole0911a splitb8d3b2b1:8+GM
split/Mega1.164049805,14.093025% lower latency,10/10 lower. All13GM1.142258084;
2-token remains slower. Source/cache/setup/profile provenance stays explicit;
no timing, oracle or result-validator replay. FINAL_TABLE.md58972a97 underEntry094.

**Combined cleanup freeze and execution.** Actual primary full fingerprint is
6617e0e9e43354a09dd4209326a814565d9889bcad04128390c489feb548bde8;
manifestf646a0859334195450b3b22ba3f8a7ab66639c6022d0ed440eed0d9d1fe3adf6;
deltad4a644807d0826e58b6902e0bb0daa96de1855e9663399de127df0da016a34a1;
stagef13797018f6b381364acacb2ffeaa1d34ef8cb852485b5bf8fbf0fdf7c127133.
13 modified paths/five deletions,1,578 full paths/354 required; all unchanged
helpers match. Historical-test substitution is not used. Generic source-delta
installer reused. Stage40511/install79500/wrapper-stage94542 passed; host18965
active. Expected81host,42EP1,25EP2perrank; counts remain static until execution.
No native/AUTO/split repeat is selected for this cleanup. Tests include actual
W4A16 auto lifecycle, original W4A4 controls and unchanged per-mode oracles.


**Cleanup host and EP1 findings / fixture correction.** Host original18965:
79passed,1failed,1skipped in5.72s. Existing unchanged dist-workspace error test
reached CUDA capture checking first with CUDA hidden. Only that node reran on
visibleGPU0 (89021),1passed;80 uniquehostpasses/1unrelatedDeepGEMM importskip.
Original failed wrapper/result remains archived. Its strict nativepostcheck saw
one new diagnostic log only; all existing binaries exact. Expanded inventory
ba6d4358 admitted through source/idle20667; combinedhostreceipt21ce8709.
No source workaround or unnecessary DeepGEMM install was added.

EP1 original33564 executed42items in122.266165s:37passed,5failed,0skipped;
source6617/nativeba6d closurepasses, completion73645b0f/closuref06e4868.
All five failed before kernel launch in manual W4A16 pooled workspace key due
missing EP process group with MEGA_NO_DIST/auto_bootstrap=False. Both realauto
cases, allpreparation/layout controls and mainoraclespassed. Auto bypasses the
pool key; its pass does not fix missing fixture setup for manual cases.

Two testfiles now share a real session NCCL/world1/rank0 group with fresh file
rendezvous and actualCUDAdevice. Existing conftest sessionfinish owns teardown;
existing groups must also be NCCL. Oracle/tolerance/production ASTs unchanged.
Simply enabling auto_bootstrap underMEGA_NO_DIST would leave emptyrequirements;
publicTORCH_DISTbootstrapwithoutlauncherenv would chooseGloo, incompatible with
CUDA allreduce in realautotuning. Neither inadequate fix was run.

Actualfixedsource512cc1b37b3c525fec764a9d63f5f46e339c3217da0fdc2f23fc70e331ddbd06;
manifest83c4f83aab1e1bf3a1a9c0d1916ad3301c65dfdebbb8dea1d0c64633569e39fe;
deltadd4244177c81d9cd156d55a452087f7031c47bda1635e521f0e93ed67515c8f0;
stagead6d6116a1f8ab94bbff7ab3291215fa3060f22c1c1dbf0176c47e693081b165.
Referenceb5a1abe1/graph7db36f4f; hooksandindependentreviewpass. Stage30144,
install84795,wrapperstage13653 passed. Rerun47565 runs seven affectedW4A16
cases (fivefailed plus twoauto with changedPGsetup);35unaffectedEP1passes and
80hostpasses retained. PendingEP2hasnotstarted. No benchmark/native/splitrepeat.
Production scope cleanup already committed locallye6ca01d01; testcommit/push waits
for correctedvalidation. LatestpublishedPRkernel remains597b/source600c; body
11b29efe5f7cbd3b90fe58c87c5479ab699eca3a10c2662d8c8d909511bc1147 verifieddraft,
FinalwholeMega/splitGM1.1640×. NoPRcomments.


**User-directed priority: revisit owned BF16 communication.** After testrefactoring,
compare current _Bf16TokenComm against inheritedTokenInPullTokenBackPush using
fresh fullAUTO1–4096 sweeps. Keepcurrentcompute/layout/catalog/5WG/twodecode;
retention8–4096, reportall13 and codecomplexity. Do not compare oldwholecommits
that contain unrelated scheduling changes. No split arm. Integration/reviewer
prepare minimal constructorcontrol read-only and native/numericaladmission.
Wait1 is now held, no primarysourcepatch or benchmark started for it.

FixedEP1 original47565/source512c closedPASS;7/7 affectedcases pass, completion
60825461, plus35 unchanged originalpasses yields42uniqueEP1cases. Host80passes/
1unrelatedskip retained. PendingEP2original54162 has launched25expectedperrank.
Executor will finish/close only this suite beforeholding forcleanupcommits and
newcustom-versus-shared plan; no automaticwait1 followon.

**EP2 cleanup stall, preserved before diagnostic.** Original execution 54162 ran
882.623355 seconds (04:04:28.319615–04:19:10.942968 UTC), with only one completed
item per rank. Both GPUs were at 100% utilization; no pre-stop stderr. Existing
stack tools were unavailable. This did not establish the exact blocked call.
The likely second item is W4A16/static/epi with S3/F1/default group hint, which
is supported by source but differs from the prior atomic/S2 performance cohort.
Workers 80599/80600 received SIGTERM in their isolated process groups; no KILL
was needed. Torchrun and the original wrapper both exited 1. Source 512c,
expanded native inventory ba6d, and idle closure passed with receipt
`e7a3d66b467a1391c92c0a8c2e78dcaf8d7045158d0438203fce8fc088014c4d`.
Fetch 72891 exited 0. This suite remains incomplete. Next is one isolated exact
case using project-local helper tracing and a 180-second process-group timeout,
without changing test or production source. The communication comparison and
held wait1 trial have not started.

**EP2 exception diagnosis and scalar-scale fix.** Isolated diagnostic 52428
reproduced the first balanced17 forward without preceding W4A4 work. At60s,
rank1 was inside the compile exception handler's collective symmetric free;
rank0 had launched Mega and was loading the top-k reducer. The run timed out124
in181.343066s; source/native/idle closure0c7aa3fc passed. Exception tracing in
11400 then captured `RuntimeError: Tensor data pointer is not aligned to16bytes`
at `cute.compile` argument binding. It timed out124 in181.567720s, closure
`e41b0c913feb02307abca78fb9159da368f120cfa5cdfa21145d25a8311f4f81` passed,
complete receipt9842cedb. No static scheduler or dispatch deadlock was established.

The test's rank1 alpha2 is a contiguous FP32 view starting at byte offset8;
`_global_scale(...).contiguous()` preserves it, while `_to_cute` advertised16.
Both epilogue alpha reads are scalar FP32, so the frontend now passes alignment4
for alpha1/alpha2 only. All other descriptors retain16. The existing helper
normalizes alpha1 before sharding, preserving its values while testing the same
valid view alignment for both scales. No oracle/tolerance is changed. The
compile call now mirrors shared BF16/NVFP4 frontends without a unilateral
collective free in its exception path. Like those frontends, a failed compile's
unattached symmetric allocation may remain until process/heap teardown; this is
not coordinated in-process failure recovery. Split W4A16 also assumes16 for its
alpha pointers, so the four-byte contract is justified by Mega's scalar loads
and accepted input contract, not claimed as an existing split implementation.

Frozen actual source414b5a140ea7d5c8b102dc53cf734876f016c0f88de1ea283885b562caa462cd;
manifestb7c91a1f0a286309ffcd94ad0bf1965a9d7d213a6432fb116bc98fb943890950;
delta4f2ba08557387c1beeedf8b1d2292e6bb07f3d2caf876e5be996a2cc06e04918;
stage05cfca200183fc5a7fcc0a041bfb4575305734fbada057f2e1c938fef7178c32.
Exactly frontend and multirank helper differ from512c; full1578/required354.
Independent review and hooks pass. Production fix committed locallyf22a18d21;
all test edits remain in primary. Full25-case-per-rank EP2 retry is authorized
with -vv and900s timeout, without tracing. Current native3 follows a passing
suite before fresh owned/shared AUTO. No new split or CUDA13.0 run is requested.

**Cleanup completed and pushed.** Final EP2 execution95790 returns0 in185.208415s:
25 passed per rank in179.60s/179.59s, no failures or skips. Source/native/idle
closure1579b52ed141364c1a39a3da81daf5de4fe2c8febb4857d02ea54d4c42c0a545 passes;
completion8167a212 and fetch9959 preserve the full rank outputs. Host80+1skip and
EP1 42 remain bound to their preceding cleanup sources as stated above.
Separate commits are e6ca01d01 (API scope), f22a18d21 (scalar alignment) and
ffb6adc5c67935f060a61faffd00b97a2839ec40 (test consolidation). All1,578 final
committed source blobs match frozen414b; the working tree is clean. The test
commit removes1,491 net lines. Normal push succeeded. PR5019 is verified
OPEN/draft onffb6adc5c; bodySHA2a4d5911658d7ebc53842ecbabb3a875616cf49cca99d644025e616a03183193
updates cleanup/scale contracts and exact test boundaries while retaining the
existing Final table verbatim. No PR comment was posted.

Current-owned native3 execution61514 completed0 in15.013s using the reviewed
alpha4 fake-descriptor adapter. All three SASS captures, including scheduling,
match600c exactly:4456/5128/4408 instructions. The adapter preserves old16-byte
checks and verifies the real CPU offset8 FP32 descriptor against its4-byte fake.
Final source/native/idle closure and independent review are being collected
before the fresh owned AUTO sweep. This is codegen evidence, not a new latency
measurement. Shared control and wait1 remain unapplied.

**Fresh custom-versus-shared comparison: owned arm complete.** Owned source414b
AUTO66457 completed0 in536.799015s; closure20064/fetch71078 passed and saved
reader ran once, passing13rows/104compiled/104winners/1300samples. Proof
c6a9c07fb1d3a35582ddb09d3fa3aa836bcc8f2bbb000a9c7b7e1d06b728362a;
result3299f281cc3424afd7acb2816f7b19f2af2ced7f8c4b7aef2a4d5c2ddb6d4a71;
closure5720cedfa98982aa01d9d618ea2a5c5e292d921b11e8d1a2a2b671dec95a4de8;
completionfabfac1940b432afa71f1a060ee298f783218466ac7fb862cc9e6924ab62e931.
Full13 table: logs/cu132-recovery0911a-transport-owned-default-direct-auto-reconstruction-001/README.md.
This whole fresh run, not historical600c or selected row minima, is the sole
BEFORE for shared. The explicit cleanup admission uses actual finalEP2/source414b
and current native3, preserving historical host/EP1 source boundaries; no extra
owned routing cohort was run.

Root then mirrored the shared control in primary: only the import and constructor
callee change to TokenInPullTokenBackPush. All constructor kwargs, compute,
layout, scheduler, catalog and remaining source bytes stay unchanged. Owned
`token_comm.py` remains present during measurement. Hooks pass. Actual frozen
sourcec8efa3189d2e35e0283412bd98ff33ed8937dea71d5d25c4bdc815b00a0b0d71;
manifest899bb52ec8ccb03a274ec97c5a03e3264223fa2fd82e111755a911f80b0d9648;
deltaead43ea465b456f893838fa09867ca5918274c916804c7eba7cd4008f65b50f1;
stageee2378f96f0798834ca27a472cbfd0cec4c8705aca3376ab17e9ffbee54697ba;
kernel8cc10121ca09761b354476eeb98adbf96fd927ecdba2466721a94bf000015ed0.
Shared native3 is followed by the prepared14rank-call oracle and then one full
AUTO if both pass. Inherited transport source path/hash must be observed; its
intended full-wait protocol is assessed directly rather than requiring the
owned READ-wait schedule. No shared timing result or retention decision yet.
Wait1 and the partial-last-subtile accumulator-release idea stay held.


### Entry095 — reuse shared transport after full autotuning comparison

**Decision: retain `TokenInPullTokenBackPush`; remove `_Bf16TokenComm`.** The
fresh whole-run comparison provides no broad latency benefit for maintaining
the custom loop. Shared/owned latency GM over8–4096 is0.998113102 (−0.188690%):
6/10 rows lower,4 higher. This is effectively flat and mixed, not an established
speedup. The largest included regressions are32+2.541%,2048+1.941%,256+1.530%
and512+1.217%. All13 GM is+0.787345%; T1+18.163% is reported and explicitly
excluded from retention with T2/T4 per the user's instruction. Both runs
retune independently; tactic changes and sequential execution limit causal
interpretation. No historical rows, minima, drift adjustment or repeat runs.

**Experiment:** after the finished test/API cleanup414b, change only the
transport import and constructor callee in primary and freeze sharedc8efa.
Keep all kwargs, BF16/SF0/swap-AB, four dispatch warps, publication counts,
compute/layouts/catalog/scorer and100-sample timing unchanged. The custom
file remains installed during measurement. Same c2 nodehu-pdx-129,8B300,
image`nvcr.io/nvidia/pytorch:26.05-py3`,systemCUDA13.2.78,DSL4.7.1/native13.3.27,
loadedNVSHMEM3.6.5/NCCL2.30.4,CUPTI13.2.0/runtime13.2.86. EP8,H7168/I2048/E256,
top8;13global powers-of-two1–4096;8 tactics,3warmups,100 cold-L2 graph samples,
primary median of per-iteration rank-MAX GPU spans. No new split/NSYS/NCU/CU130.

**Shared native:** original83992 returns0. Review7f81a4af admits the actual
full-completion protocol; REG96/640threads/two decode WGs/STACK0/LOCAL0,
dynamicSMEM200064/230784,B3/S2 andraw5/4 unchanged. Counts5496/6208/5472 versus
fresh-owned4456/5128/4408 are larger by1040/1080/1064 instructions; this did not
predict an end-to-end latency gain. Closure183de876 passes.

**Shared numerical:** original25827/closure3796/fetch3106 return0. Four standard
cases×2ranks plus three large-skew cases×2ranks give14 completed rank-calls and
14 actual compiled objects (not the historical38). Every object records shared
transport sourceb3a46284,REG96/640/two decode groups/LOCAL0. Standard cases use
N64F4/N128F8×both returns and the consolidated changing-route reference. Large
H288/I448/E4/top2/T1777 cases use148CTAs×4dispatchwarps,7108 received rows on
rank0 and0 onrank1, andF4/F8/F1 full-batch/tail coverage. Same oracle/tolerance.
Summaryfb2d2145; numerical closure358940c0.

**Shared AUTO:** original24044/closure17267/fetch40348 return0;568.525820s.
Saved reader and sole fresh-owned comparator each run once, passing13rows,
104compiled/104winners/13×8rankings/1300samples. Shared proof
0e7996fe37a5918ebbb17a0083a2b84893af592c75ed44ba7256b0e478ac0f72;
resultb8f07dab0db9a646ef5411c4aadb01902d9ef3a1cc983bf1ca6056c607aa1f5d;
closured82cf98636987d7bd327bdadd791834ac3d6704bf31b7c9035bec768306c9321;
completiondc7de7b75813378e7bbc6f3a2f99de1e0258ff701beee5f81d5378c02abf3fbe.
Fresh-owned run66457 is the only control, proofc6a9c07f/result3299f281,
536.799015s. Comparisonc32a5e57, independent arithmetic/provenance review3610bd5f.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073472 | 0.086817 | +18.163% | N64/F8/epi | N64/F4/epi |
| 2 | 0.107280 | 0.102560 | -4.400% | N64/F8/epi | N64/F4/epi |
| 4 | 0.119536 | 0.119409 | -0.106% | N64/F4/epi | N64/F8/epi |
| 8 | 0.138369 | 0.137697 | -0.486% | N64/F8/epi | N64/F4/epi |
| 16 | 0.152082 | 0.147233 | -3.188% | N64/F8/epi | N64/F4/epi |
| 32 | 0.174434 | 0.178866 | +2.541% | N64/F4/epi | N64/F4/epi |
| 64 | 0.200545 | 0.193537 | -3.494% | N64/F8/epi | N64/F4/epi |
| 128 | 0.208130 | 0.206737 | -0.669% | N64/F4/epi | N64/F8/epi |
| 256 | 0.205843 | 0.208993 | +1.530% | N64/F4/epi | N64/F4/epi |
| 512 | 0.210289 | 0.212849 | +1.217% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.232161 | 0.229825 | -1.006% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.305153 | 0.311076 | +1.941% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.468260 | 0.467877 | -0.082% | N128/F4/reuse | N128/F4/reuse |


**Why simplify:** the321-line/279-nonblank subclass overrides only a300-line
pull method; metadata/storage/initialization/return were already inherited.
It duplicates expert/rank mapping, address/provenance math, scratch/phase
lifetimes and flag publication, requiring future universal fixes to be reviewed
and ported. Its compact mapping and source-read-only wait allow more overlap in
principle, but the full autotuned result does not justify that ownership cost.
Delete only the custom file and four newly added primitive exports at three
sites (12lines):fns_b32,ldg_f32_raw,tma_load_1d_raw,tma_store_1d. Keep underlying
universal implementations and GpuReleaseFlagBatchTracker. No vendor edits.

**Publication source:** commit`dde36ec13cacb0ee8768275ff8ab660d19748a7d`, pushed
normally after passing all applicable hooks, includingmypy/Ruff. Final source
03da8ead50fccb632ae404699c0d356c3507f26a755fd067a34c15e11879ae66;
manifest65086299b1a0cb790e85ca1560060c01e37952c16323f895dbc6277c230d22c9;
delta6e783b087c8ff54f4fab1dc8e3648b78fc3431f80fb30a583d1bcd9de9575fc2;
stage8a18191c3e23d9a83dac80649fabe5cb6b4154f24007af93d895b7384a3d0f19.
Exactly3 post-measurement paths differ fromc8efa:dead file plus two export lists.
Measured kernel8cc10121 and all other1575 entries match. Source review41941c22
passes; no GPU rerun for unreachable-code removals. Frozen retained package and
receipt are undercandidates/w4a16_shared_transport_control/.

Final table arithmetic reuses the unchanged complete same-node split71a1 run.
Shared Mega beats split at every8–4096 row,GM1.160562740× (13.834904% lower
latency). T1/T2 remain slower and visible. Detailed artifacts are
execution/FINAL_TABLE.{json,md}; this new whole shared column replaces600c in
PR Final performance. CUDA13.0 table remains historical and unchanged.

**Next scope:** the unlaunched two-pending-write proposal belonged to the removed
custom pull loop and is no longer applicable to the retained implementation.
Do not resurrect it or modify the VERBATIM shared transport for this PR. The
FC2 last-valid-subtile accumulator-release note remains source-only, unimplemented
and unmeasured; future performance work stays in the owned compute/epilogue path.

**Publication and remote completion:** live PR5019 is verified OPEN/draft on
dde36ec13,body27e35ac4c0923db4155a3d2d30bbfe35110daec2a951fa877a3cd3f503701fa9.
The one CUDA13.2 Final table now uses sharedc8efa; historicalCU130 is unchanged.
Independent text review corrected a stale graph-replay claim: the new14-call
shared cohort is eager changing-route coverage; graph evidence belongs to the
separately source-bounded cleanup suites. No PR comments. Remote final source
03da8ead is installed;stage5449/install79304/closure45861/fetch24931 pass.
Closureb3dd1d832b42ecd3ecab8d54cbe53949930a8d0504c3619bae63edcd7f25b878
confirms source/native cacheba6d unchanged and GPUs idle;completion3f377233.
No GPU/compiler/test/benchmark rerun for the dead-code cleanup.


## Implementation cleanup after shared transport

The user paused performance experiments to reduce implementation complexity and
LOC. Starting from `dde36ec13` / source `03da8ead`, the cleanup removes 869 net
lines across ten owned implementation files (6504→5635). It removes dead
scheduler/group/activation-scale state, specializes fixed epilogue callbacks
and TMEM paths, simplifies declared workspace views, and drops redundant host
config/compile state. Public contracts and manual configurations, eight autotune
candidates, universal token communication, and five WGs/two decoders remain.
Shared W4A4 weight preparation, shared autotune, build configuration and vendor
source stay unchanged. No test or benchmark source edits are included.

Initial source `40fec0ef` failed all three native fixtures before code generation:
generic tuple reconstruction queried `PipelineState.__get_mlir_types__` on
Int32-wrapped fields. A seven-line fix rebuilds nested dataclass fields through
their own extraction/reconstruction protocol. No pipeline/vendor behavior was
changed; the original failure and idle closure are retained. Final source
`eb9cc9a1877da7dfea0f35ff51ffbc1666036fdcbe1500d109ec46f56fd824df`, manifest
`51b972d9059c321a523da38a948aee5c7050ecd8efed49734a42592d4f0ebb3d`, passes
native3. Shared c8 controls are reused: 5496→5480,6208→6192,5472→5456
instructions, unchanged REG96/640/STACK0/LOCAL0, raw/B/decoded stages,
workspace descriptors and ordered synchronization/copy/MMA/release sequences.

CUDA13.2/c2/hu-pdx-129/B300×8/image26.05: host80pass+1 existing DeepGEMM
skip; EP142pass; EP225pass per rank; M128/N64/C1+C2/static/S3 two existing
oracle calls per rank, all seven routing rounds, pass. One-CTA MMA is enabled
for both M128 clusters. Final source/native/idle closure6bc7714e passes.
Completion `candidates/w4a16_implementation_cleanup/execution/validation-completion001.json`
SHA `fdb61867854202da98b61aa7455acbede8896ccf60949468817f3d5a07ea1ca5` binds
all cohorts. No performance sweep ran and no speedup is inferred from code size.

Commit `a8b5a47cdeb7b09f784d6a76d35b952bd1e4e3e5` passes hooks; all1577
committed blobs match frozen source. PR Final performance retains measuredc8
with explicit cleanup timing boundary. The user then requested resuming perf
work through substantial established pipeline/orchestration patterns rather
than micro lifetime changes. The independent review begins under
`candidates/w4a16_pipeline_orchestration_review/`.


## Winner metadata restoration and interrupted baseline

User explicitly permits keeping `_autotune_winner` if convenient. Restore exactly
the pre-cleanup backend field and returned-dictionary copy; it is the direct
benchmark consumer interface and avoids reconstructing knobs through workspace
frontend internals. Commit `a26dc8b88eae499b90c02b0d9869b90887b81812` passes all
applicable commit hooks and is pushed. Three net lines restored; cumulative
cleanup866 lines across9files. Benchmark source is unchanged froma8b/dde.
Retained99681e83/manifestca4ecbbc contains exactly this host-only change fromeb9cc.

Baseline001 failed the old project helper's `_SWEEP_BASE` catalog assumption
before launching. Baseline002 on eb9cc tuned its first row, then failed at the
benchmark's removed `_autotune_winner` read: return1,77.762321s,zero CSV rows.
Its source/native/idle closure2e840a6e passes. Temporary source d3acae changed
only benchmark reporting to read actual candidate fields from frontend config.
Baseline003 original96872 launched with that correction, but its devbox vanished.
The HAI command reports137, outer1, and no terminal marker or row artifacts were
recovered. Source/native/idle closure is unavailable. This is incomplete, not a
benchmark result. The temporary reporting implementation is not promoted.

Replacement image checked live at https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-
and https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html .
26.08 uses13.4.1,26.07 uses13.3.1,26.06 uses13.3.0;26.05-py3 remains newest
CUDA13.2.1.009. Executor requests fi-w4a16-mega-0911b on c2/ziangli, B300x8,
--bare, no --size/hell. Existing native cache and bootstrap are reused where
actual stack identity permits; baseline will be whole retained996 on the newnode.

N256 candidate has14 net lines in3files and remains unpromoted. Rebased freeze
`candidates/w4a16_n256_acc1/frozen-retained-base` binds source59bbe378/manifest
73d1cdb4/deltacfe2a73d/stageeefb9fe5 to retained996. All three N256 bytes match
the original source-reviewed66c candidate; only host winner/benchmark metadata
differs in combinedsource. No N256 native, numerical or performance result yet.


### Fresh retained996 baseline on hu-pdx-15

Replacement fi-w4a16-mega-0911b is ready, c2/ziangli earth-non-preempt,
B300SXM6ACx8/driver590.48.01. Published source996 and pinned packages/loaded
library/profiler hashes match the intended stack. Reusing the archived support
cache still required normal Ninja rebuilds for newer source inputs:89.963s fp4,
19.468s routing. Actual new support hashes routing7510bc9c/fp442679531 differ
fromold85d7 and are recorded in inventory47f6150f. No old-build identity claim.
No timestamp manipulation or bypass. Actual preflighta7f9407a passes.

Retained AUTO original23652/closure53637/fetch13240 all true0, underlying
570.176644s. Full13rows,104compiled objects,104ranked candidates,1300 cold-L2
CUPTI rank-MAX samples. Saved reader and historical-context comparator each
passed once. Whole proofa419b6e2c1b3dd591f2e397ac6a27aeab1f61360d79e316d8a3b25826a13dafb;
result9bc538d743d953be9562c4f17834b0c23675c8d91c5f3149e90d6fe689d3a911;
closure1f71403928ea6ce720366d931543ecf2fa57e600444dce231029ff1b9fe34dad.
Result directory:logs/cu132-retained996-default-direct-auto-reconstruction-001.

| Global tokens | Retained996 Mega ms |
| ---: | ---: |
|1|0.087008|
|2|0.104785|
|4|0.118976|
|8|0.134464|
|16|0.154144|
|32|0.180001|
|64|0.200577|
|128|0.208544|
|256|0.207008|
|512|0.232992|
|1024|0.231633|
|2048|0.311298|
|4096|0.457218|

This is the same-node/build BEFORE for N256 and future trials. No cleanup
speedup is inferred by comparing it with old hu-pdx-129. PR Final split/Mega
columns stay their complete same-node129 sources pending a new retained best
and corresponding publication evidence. Restored winner metadata is exercised
across all13rows; no duplicate state-removal benchmark workaround is promoted.


### N256 feasibility passed; full AUTO12 pending

Original native4 69850 completed0 in18.914s; closure8ad378ab. N256 direct/reuse
actualraw2/B2/D2/ACC1,226688B dynamicSMEM,REG96/640/STACK0/LOCAL0,6616/6600
instructions. N64/N128 retain exact5480/6192 instruction encodings/schedules.
Independent detailed reviewea10972d95287c2ca5587f1d445a4c0913daefe7859a58f3842151ee7a773778
checks one full/empty ACCpair +96/+104, fixedslot0, phaseXOR1 per work, decoded
base256/two128colslots, two-stage ringwrap, scratchcolumns<=255, releasebefore
next-work waits and16 scalar direct pointer stores with no local accesses.
No throughput conclusion from native counts.

Numerical95123/closure45038/fetch26444 all0:24/24rankcalls(changing8,longK4,
partial-subtiles12), closure48dfd05c, unchangednative47f6150f/source59bbe/idle.
Graph95127/fetch44520 both0:2passed/rank,37.01s pytest/42.589831s wrapper,
finalclosure54cf7daf. Original oracles/tolerances and graph function preserved;
existingmoe_ep session plugin and confcutdir used. Combined admission
`candidates/w4a16_n256_acc1/execution/validation-completion001.json` SHA
 e1b7c493e0b71db0122997fbd780a120e073b2044ac1ee65dead7a5b7a48e52d.

After admission, append N256 to the existing N128/N64 tile tuple, yielding12
candidate dictionaries in the same product; old8order unchanged. Add one
existing geometry-tail parameter H7200/I2112/N256, both existing return modes.
All5changed-filehooks pass. Frozen-auto12 source50fa1daffc300dbad62a0ca2d940a7fdd0cd20fc28e0d0fa222f7187be7c840b,
manifesta60accb475ffe200c1323ab02630b158deb775b0d7a343363ab6b5ddd5505f58,
delta9796b3be/stage8dd19ba9 changes only catalog+test from validated59; all3N256
implementation files are byte-exact. Added-test selection2cases/rank will cover
514routes/expert using existing default257source tokens, followed by AUTO12.
Only ranking entries become156; winner/selected records remain104, rows13,
samples1300. Same cold-L2 CUPTI and hot graph-event scorer boundaries retained.
No performance result or source promotion at this point.


### N256 AUTO12 complete; hold for activation-width refinement

Whole AUTO original15885/closure84886/fetch43182 and the saved reader/comparator
passed. Run time802.144196s versus570.176644s for the preceding AUTO8 baseline;
this includes preparation/tuning and is not kernel latency. Source50fa,
nodehu-pdx-15, native47f6150f remain unchanged and idle. The added geometry test
passed2cases/rank before timing (35.007729s, closure5c8b86f1).

Whole resulte443f36d/proof3b660010 contains13rows,156candidate rankings,
104selected/winner records and1300samples. Completion is
`candidates/w4a16_n256_acc1/execution/auto-completion001.json` (d32350a3).
Full before/after: [table](logs/cu132-n256-acc1-vs-retained996-comparison-001/README.md),
comparisonfba125fa. Relative to whole retained996, 8–4096 latency GM is
0.996040557 (−0.395944%),5/10lower and5higher. All13 is−1.534210%,7/13lower.
N256 wins **zero of13**; every selected kernel remains N64/N128. Even rows with
the same tactic range fromT32+5.537% toT512−8.288%, so do not attribute the
mixed lower aggregate to N256, select individual rows, or publish a new best.
The existing PR Final split/Mega table stays unchanged; no split rerun.

The following diagnostics are the printed hot-input autotuner scores from this
single completed run, not the cold-L2 CUPTI forward metric:

| Tokens | Selected score (us) | Best N256 score (us) | N256 gap |
|---:|---:|---:|---:|
| 1 | 65.1 | 75.1 | +15.36% |
| 2 | 81.5 | 99.9 | +22.58% |
| 4 | 91.7 | 116.4 | +26.94% |
| 8 | 110.2 | 148.1 | +34.39% |
| 16 | 124.5 | 171.6 | +37.83% |
| 32 | 149.1 | 208.6 | +39.91% |
| 64 | 173.6 | 239.9 | +38.19% |
| 128 | 177.9 | 249.5 | +40.25% |
| 256 | 181.4 | 255.5 | +40.85% |
| 512 | 187.0 | 263.7 | +41.02% |
| 1024 | 208.5 | 282.9 | +35.68% |
| 2048 | 293.2 | 345.7 | +17.91% |
| 4096 | 444.2 | 451.6 | +1.67% |

Decision: keep the five candidate files visible but uncommitted while drafting
a general per-work half-width activation-copy refinement. Dynamic MMA already
uses fewer rows; static activation TMA still transfers full N256 buffers.
The design retains the fixed B ring, its swizzle/K-plane/stage strides, N256
global work ownership and correct full/half transaction expectations. It adds
immutable full/half descriptors with a uniform work-count selection, no public
knob or single-global-shape dispatch. Prior inactive-half trials did not reduce
activation TMA payload. See
`candidates/w4a16_pipeline_orchestration_review/ACTIVATION_WIDTH_DESIGN.md`.

Whole source50 AUTO12 is the BEFORE for this refinement; retained996 remains
the separate upstream control. No baseline, split, or current N256 correctness
cohort is repeated merely for the design note. Any changed loader requires its
own focused native/numerical checks before a new whole AUTO12 sweep.


### N256 activation-width implementation and native admission

The one-file refinement is visible in primary. It constructs immutable full/half
TMA atoms only for N256 and selects one constexpr-specialized copy body per work.
Both FC phases preserve full N256 shared allocation, K-plane/stage strides and
scheduler ownership. Half work (valid<=128) uses64local rows/CTA and65536
combined expected bytes; full work uses131072. No public knob, dispatch rewrite,
decoder change or BF16 weight materialization.

Initial source64e22e5c/kernel6050a631 compiled N64/N128 but failed bothN256
before codegen at an overlystrict shape-tuple equality check; native18583
exit1 in11.336681s, closure3ec3c3cb. Actual installed4.7.1 helpers derive logical
N/K then tile the shared atom, so direct partition nesting is not its contract.
Sourcea15b5d68/kernel8ae757cd corrected the guard to logical size with layout
diagnostics. Native12290 exit1 in14.791334s then exposed a host-jit half-MMA
object captured across the kernel region; closure3e464c92. Neither failure
ran a GPU test or supplied performance evidence. Artifacts are preserved.

Final source50696104/kernel4ab7b2bf passes the half-MMA explicitly through the
kernel and activation helpers, using None for old geometries. Scoped hooks pass.
Batched install/preflight/native4 original6380 succeeds, native18.791719s,
closureddb46134/source5069/native47f/idle. N256 direct/reuse6744/6728instructions
(+128 versus original wider-tile code), REG96/640/STACK0/LOCAL0, SMEM226688 and
raw2/B2/D2/ACC1 unchanged. New-signature N64/N128 controls preserve exact
instructions/encodings/schedules5480/6192.

Actual direct/reuse PTX verifies valid>128 branch outside the K loop; half
base physical_row+tile_idx*256 and nonleader split-64+CTA64; original full
split-128+CTA128; expected_tx65536/131072 for both FC phases; four old
destination offsets95616/112000/128384/144768 and stage<<16; same empty-slot
acquire and modulo2/XOR phases. Native admission passes. Planned numerical28
adds exact128-route coverage to66/130/194 and long-K full/tail/changing
rounds, with original oracles/tolerances. Existing graph2/rank follows.
Whole AUTO50 remains the immediate BEFORE; retained996 remains the separate
control. No new timing or promotion is claimed at this point.


### Measured iteration-time budget

Rank-zero `bench_gpu_time` wall totals from all13 saved timing records are
- cu132-retained996-default-direct-auto-reconstruction-001: 4.259s of 570.177s process time (0.747%).
- cu132-n256-acc1-default-direct-auto-reconstruction-001: 4.235s of 802.144s process time (0.528%).

Thus the100 CUPTI samples/row account for less than1% of these full AUTO runs.
Reducing sample count would save little total wall time; keep100 and full13
coverage. This does not separate compilation, preparation and tuning costs
inside the remaining process time. Remote helper orchestration is outside
the recorded process boundary and has been batched where safe.


### Activation-width numerical/graph admission complete

All28 numerical rank-calls/28 actual compiled objects pass on source5069.
Original20871 then exited1 because its inline Python orchestration parent argv
contained the serialized names of worker scripts and was misclassified by the
idle checker. This is a harness check failure, not a numerical/GPU failure.
Standalone unchanged closure5290 passed (189117f3). Future batching uses code
and plan files rather than embedding the whole plan in argv; checks are intact.
Graph upload82373 initially failed before test launch because its helper
directory was absent. After creating only that directory, original4471 passes
two graph cases on each rank, subprocess27.920617s, executione2b20d1f and
closure3d7d0104. Final source5069/native47f/idle pass. No numerical replay.

AUTO12 admissionbaf01431, exactargvbea1c36f and stage69b0660a bind those actual
results. Use whole50/proof3b660010 as immediate BEFORE and retained996/proof
a419b6e2 as separate control. Do not attribute unchanged-N64/N128 variation
to N256, mix rows, or run another baseline/split merely for this trial.


Coverage clarification from saved numerical resources40f0a8a: the changing
cohort's257 is capacity, not514 observed routes. Current5069 full-tile coverage
is long-K258routes→[256,2], with partial66/128/130/194. The514-route geometry
test belongs to the preceding source50 admission, before the activation-width
change. No new test is added for this documentation correction. All28 current
rank-call results and native layouts/resources remain passed.

Full AUTO12 AFTER completed as original75059 in815.607396s,
`cu132-n256-activation-width-default-auto13-direct-001`; closure8002 passed.
Saved reader/comparator passed with proofb7701365/resultd3161f78 and
comparison4a09b39c:13rows/156rankings/104selected+winners/1300samples.
The complete tables are in `logs/cu132-n256-activation-width-comparison-001`.
N256 selects4096 only, F4/reuse. Over8–4096, latency GM is+0.199263% versus
immediate50 (4/10 lower), and−0.197470% versus retained996 (3/10 lower).
4096 cold latency .463187→.458531ms is−1.005% versus50, but+.287% versus
retained996 .457218ms. This mixed result does not demonstrate a broad gain.
N256's best printed hot scores improve in all13 rows by1.683–4.929%, with
4096 going451.6→444.0us, narrowly ahead of the same-run best old geometry
446.7us. Hot-score derivation20e7852d is preserved in the candidate execution
folder; it is not a cold-forward before/after metric.

The user added8192 to retention and requested one follow-on point without
repeating1–4096. Original41480 completed in98.673429s, closure99825/fetch37080
returned0. Saved-reader attempt001 failed only at a hard-coded thirteen-row
admission in its shared helper. A singleton-reader repair is pending locally;
no GPU rerun or source change. There is no existing8192 cold BEFORE.


### N256 retention decision and separate revert

The final8192 reader passes: proof50b9d784/resulta9e677c8 and completion8ab54d80.
Selected oldN128/F4/reuse gives cold0.796246ms. BestN256 hot765.0us loses to
oldN128730.4us by4.737%; no cold BEFORE exists at8192. The full13 refinement
selectedN256 only at4096, hot444.0 versus best old446.7us (~0.604% lower).
As the user clarified, N64/N128 native code is identical, so unselected-row
variation is noise and is not used to reject this N256 change. The user then
judged the only selected-case benefit too small and requested commit-and-revert.

Commit4db0979cff9adfe7553b5ab0fcb066a41a360616 preserves the fully validated
source5069 implementation (+115 net lines across5files); all1577 frozen source
hashes matched before committing and hooks passed. Separate revert
4733b060227ec8cba05c4facb2b1d65dde116225 restores the entire tree exactly to
retaineda26dc8b88/source996. No patch/artifact/log was deleted. Final performance
in the PR is unchanged. The planned publication split was cancelled before any
staging or GPU work; no new timing is necessary for restoring identical code.
A boundedN256/K128 feasibility read suggested more operand stages but was
stopped before implementation. Remote source restoration uses source/native/
idle checks only. Keep8192 in future retention, with1/2/4 reporting-only.


### Fixed F4/F8 comparison requested; full14-row sweep policy

The user requested fixed flag_batch4 and8 full sweeps to decide whether the
autotune axis is useful. A subsequent instruction replaces separate8192
follow-ups with a single1–8192 sweep for every future experiment. Each arm
keeps N64/N128 and direct/reused return tunable using the existing four filtered
candidates, ordered as in the retained eight-dictionary product. Use restored
source996, separate fresh caches, unchanged100-sample CUPTI timing, F4 thenF8.
No new primary source change or split baseline is needed. Exclude1/2/4 only
from retention; retain all14 rows in reporting.


### Fixed F4 selected after matched full14 AUTO arms

Both complete arms measured retained source `99681e83066e76ede3dc4054582f130e96bc7da15dfe97c5ee3ebde9c60a3ebc` on `hu-pdx-15`, eight B300 GPUs, CUDA 13.2 / DSL 4.7.1 and the existing native inventory 47f6150f. The benchmark bridge passes the original ordered product filtered only by `flag_batch` through the existing autotuner's `candidates=` parameter. It changes no production source, scorer or timer. F4 then F8 each uses four dictionaries (N128/N64 × epilogue/reused-dispatch return), all 14 token counts 1–8192, three warmups, 100 cold-L2 CUPTI samples per row and distinct initially empty knob/DSL/driver caches.

- F4 original 17417, closure 85112 and fetch 86077 all exit 0; benchmark 423.277835619 s. Saved proof `28617b7e0d0f5a42988d6c8cdc299898fbedd608642d4ffacad4b732161e798f`, result `d4f1a6189a0ad444f0186aacacfe723813971af2d45ab55e14c4c1c0e2ff6cac`.
- F8 original 39394, closure 53851 and fetch 43450 all exit 0; benchmark 423.880581141 s. Saved proof `164d34b5e9140e24aa07d4c364d5bf3a959cb8a8cd5ce1b380732821d57c41f4`, result `ba7c2c82bd86cd2dc5fb419e6c8fdf9434ab888f3aa704db411bd685f71e36d9`.
- Each saved reader passes on its first execution: 14 rows/arrays, 112 selected configurations/resources/winners, 56 candidate entries and 1,400 samples. Staging verifies 95 nonempty fused, 17 empty and 88 retention records. Actual public eight versus filtered four catalogs are recorded per rank. Source/native/GPU-idle closure passes; no numerical or benchmark replay.
- Comparison SHA `93254905465f94266d02ee54c083e6e452b93ffb1fe7525806fa4795cdcd636c`, at `logs/cu132-fixed-f4-vs-f8-auto14-comparison-001/`. Existing saved GM arithmetic gives F8/F4 **1.016189412 (+1.618941%) over 8–8192**, with F4 lower 7/11 and F8 lower 4/11; all 14 ratio 1.009800179 (+0.980018%), seven lower rows each.

| Tokens | F4 cold ms | F8 cold ms | F8/F4 change | F4 selected | F8 selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.086544 | 0.086208 | -0.388% | N128/F4/epi | N64/F8/epi |
| 2 | 0.107953 | 0.104289 | -3.394% | N64/F4/epi | N64/F8/epi |
| 4 | 0.122257 | 0.122049 | -0.170% | N64/F4/epi | N64/F8/epi |
| 8 | 0.137856 | 0.135888 | -1.428% | N64/F4/epi | N64/F8/epi |
| 16 | 0.151857 | 0.150113 | -1.148% | N64/F4/epi | N64/F8/epi |
| 32 | 0.180256 | 0.176544 | -2.059% | N64/F4/epi | N64/F8/epi |
| 64 | 0.203409 | 0.203314 | -0.047% | N64/F4/epi | N64/F8/epi |
| 128 | 0.205072 | 0.217570 | +6.094% | N64/F4/epi | N64/F8/epi |
| 256 | 0.208176 | 0.211521 | +1.607% | N64/F4/epi | N64/F8/epi |
| 512 | 0.214753 | 0.215329 | +0.268% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.231153 | 0.234592 | +1.488% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.306179 | 0.315121 | +2.921% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.467649 | 0.495394 | +5.933% | N128/F4/reuse | N128/F8/reuse |
| 8192 | 0.793748 | 0.830194 | +4.592% | N128/F4/reuse | N128/F8/reuse |

The matched hot tables in the comparison keep geometry and return mode fixed. N64/epilogue scores differ by less than 0.82% through 2048; the small-token cold advantages for F8 do not have a clear corresponding hot advantage. At 4096 and 8192, F8 is slower in all four matched geometry/return pairs, respectively 5.86–6.94% and 4.99–7.09%. Hot printed 0.1 us graph scores use maximum of rank medians; cold CUPTI rows use median of 100 per-iteration rank maxima. These serial whole runs provide no statistical confidence bound or drift adjustment.

**Decision:** root selected fixed F4 for the curated catalog. Commit `d6f8502b7f69da64e78641203917186280d01ebb` changes only owned autotune policy and its W4A16 documentation. Frozen source `eb73a83c5c8f104efa01b814b06e26f01ea2b9bce9b11f64be4b211fa16af1d7`, manifest 07d2d729, differs from measured source 99681e83 only in `autotune.py`; documentation is outside the source inventory. Root verified exact ordered equality with the measured four-dictionary F4 subset. All device code and other supported/manual configurations, including F8, remain unchanged. No Mega timing replay is needed for this equivalent candidate selection.

Keep the F4/F8 trial table local. One separately authorized current-node split-only publication sweep over 1–8192 will supply a new split column beside the completed F4 Mega run. Its sealed adapter lives under `candidates/w4a16_publication_split_refresh/recovery0911b`; prior Final/CUDA13.0 tables remain historical until that complete split result is validated. Source-audit context remains in `candidates/w4a16_fixed_flag_batch/FLAG_BATCH_AUDIT.md`; runtime/result adapters stay under `candidates/w4a16_fixed_flag`.

### Fixed-F4 publication completed

The one same-node split publication run `cu132-recovery0911b-publication-split-auto14-001` passed on promoted source `eb73a83c5c8f104efa01b814b06e26f01ea2b9bce9b11f64be4b211fa16af1d7`, commit `d6f8502b7f69da64e78641203917186280d01ebb`, node `hu-pdx-15`. Original 82899 and fetch 34853 exited 0; the benchmark took 711.024306 s. The first saved reader passed 14 rows, 112 rank/token tactics and 1,400 samples. Source/native/idle closure passed; 54 first-use support files were added, with no missing or changed preexisting non-log file. Split result SHA `a66e1894527e45e427cc3663413d7b87e82a68afc797d21b9000f4d1d2eb79fc`.

The Final table pairs that complete split run with the completed source996 filtered-F4 Mega result `d4f1a6189a0ad444f0186aacacfe723813971af2d45ab55e14c4c1c0e2ff6cac`; the promoted public four-tactic catalog is exactly the measured ordered subset. No Mega replay. All 14 raw rows and selected dictionaries are in `candidates/w4a16_publication_split_refresh/recovery0911b/FINAL_TABLE.json` (SHA `99805930af05a5d2f2719ad44da13e28c25bec409ce2c5a80b924d70f2458502`) and its Markdown sibling. Over tokens 8–8192, geometric split/Mega is **1.142387284×**, or **12.464012% lower Mega latency**, with Mega lower in all 11 rows. Only T1 is slower across all 14. These are sequential complete runs, with no row substitutions, confidence bound or causal attribution to catalog narrowing.

Root published PR body SHA `12244235b9ce764013e010364e8704ed1f8d3de0ca90ed21757f13aadbadf443` and read back exact bytes: PR5019 remains draft at head `d6f8502b7f69da64e78641203917186280d01ebb`. `PR-fixed-f4-published.json` and `PR_BODY.md` preserve the publication. Historical CUDA13.0 raw results remain unchanged; F4/F8 optimization history remains local. The later 32-line host-only autotune inlining is a separate uncommitted local patch and is not included in this publication or measurement source.

### Two bounded post-publication cleanups retained

Commit `c8155c6f23cc8374912019810fff8fa10ed3b056` removes 32 host-only lines by inlining the single-use owned autotune protocol/callback plumbing. The public signature, four dictionaries, graph lifetime helper, candidate exceptions/barriers, MAX-of-rank-medians scoring and winner cache/print order remain unchanged. The proposed primary file matches SHA `2cfda9753679b231437326fb2ce6a716e480d877fdffd14e8e91a9de8bd960e8`; scoped and commit hooks pass. Actual frozen source `c8f48f4434a8cb9378fe65e588d15923a8821c32bd5a13a9307636131b5d95da` passed existing AUTO lifecycle coverage on node15: two EP1 cases (28.266842 s), one EP2 case per rank (27.267829 s), original 18872 and fetch 13061 successful. Closure `dfb01a81554a0847559ab218dc25a7de0d1f7ff3b316e0862138c5ec7bdff964` confirms unchanged source/native06752caf and idle. No performance or standalone native capture.

Commit `21fd7ce48b0a7406175191aa5542f0578a6371e8` then removes 21 lines of unreachable optional-None state handling in the owned scheduler extension. The actual pointer was already supplied at the sole constructor call. Both live FC1/FC2 peeks and their consuming waits remain; whole-file AST after actual non-None specialization and doc/type normalization is equal, including MLIR field/value order. Proposed/retained `custom_ext.py` SHA `a4f690c006f25ea242674cc194bc68a87ed788a2fc1235c37cc2d3bba3097b40`; source patch/proof is under `candidates/w4a16_custom_ext_required_ready`. Scoped and commit hooks pass. Root retained this exact specialization without a GPU/native/timing rerun; no new runtime result is inferred. Primary is clean at this pushed head.

Combined implementation reduction is **919 net lines** (866 earlier +32 autotune +21 readiness). `PR_BODY.md` and `CURRENT_STATE.md` now separate these two validation boundaries. The draft's entire Final performance section remains byte-exact to published body12244235, retaining measured source996 filtered F4 versus promoted d6/eb73 split. This local body update is not a new live publication; root owns publication.


### Early decode audit and exact tail-reduction candidate

The source audit in `candidates/w4a16_pipeline_orchestration_review/EARLY_WEIGHT_DECODE_AUDIT.md` confirms that packed-weight loads and both decoder WGs already proceed independently of FC1 remote payload readiness and FC2 activation readiness. The scheduler is released after count exchange, before payload pulls; only the activation loader waits for data. Current decoded TMEM rings bound further runahead to D3 for N64 and D2 for N128. This is a source conclusion, not a fresh profile proving that every opportunity is exhausted. No additional early-decode rewrite is promoted on this evidence.

The active three-file candidate uses the existing compile-time `in_kernel_fc2_reduce` selector for exact ordered FP32 top-k reduction after shared communication tail completion. Both shared transport and per-route epilogue reductions stay False; the full BF16 per-route combine buffer remains. One all-640-thread local barrier hands the peer drain to a WG-striped reduction worker. It preserves the separate reducer's ordered packed FP32 multiply/FMA and one final BF16 cast, with dynamic caller-owned output and output-shape-aware launch caching. The public four-F4 catalog remains unchanged until validation and a complete before/after decision.

Initial frozen source `094eafa12eae5fab137b953d5443b063e419e267f9eaeacc9f0cbedea7e7a304`, manifest fa95a2e2, was compiled in original batch 17007. Installation and four CPU preflight cases passed. All three enabled captures failed compilation at the combine-buffer 128-bit BF16 load because dynamic strides reduced known source alignment to 16 bits. Both disabled controls compiled and match the historical controls byte-for-byte in full SASS, encodings and schedules: N64/F4 5480 instructions; N128/F8 6192; REG96/640 threads, zero stack/local memory. N128/F8 is only an identity control, not a changed performance catalog. Batch elapsed 17.706944 seconds, actual exit 1. Closure/fetch 54368 passed, closure a36dcb1a and all 62 files are preserved; no GPU numerical or performance run occurred.

The first correction changes only the two enabled host descriptors to preserve actual static combine/scores strides, as the standalone reducer does. False retains dynamic descriptors; no guessed input alignment, runtime fallback or vendor modification is added. Frontend SHA `a434b1023dbeaece5ca1acadb1e91572cda08b15cc813cffe32b6a8e4ba21a84`; delta `candidates/w4a16_exact_tail_reduce/descriptor_stride_fix/source.patch`, SHA c8e00faa. Primary is +155 net lines across three implementation files and scoped hooks pass. The original failed source and proposal remain intact. Three enabled native captures will be retried with new source pins; no success is inferred from the source fix.


The corrected native retry (original75318) passed all three True cases in 19.15 s, source7b87 / manifestd3aa00b6. Full closure e8b4e70e confirms source/native06752caf/idle; 56 files were fetched. CPU actual/fake MLIR parity passes for static combine/scores and compact-dynamic output n=0/n=3. All kernels remain REG96/640/STACK0/LOCAL0, static shared1024 bytes, with dynamic shared200064 (N64) or230784 (N128), unchanged stages and role redistribution. Root and independent review find the final barrier8/640 after peer drains and resets, dynamic-n guarded WG-striped addressing, ordered packed FP32 math and one final BF16 store. Both topk8 tails emit4 FMUL2/28 FFMA2; topk32 emits4/124. The dispatch-role reachable tail uses no register aboveR45, including vector ranges below its64-register allocation. False controls from the original failed batch remain byte-exact; they were not repeated.

The existing-test patch ccbde4dc was applied to primary, adding90 net lines across three existing files; hooks pass. Frozen test-augmented source0bf9 / manifest5bfc changes no implementation bytes from7b87. Targeted original44195 passes all groups:18 EP1 cases (62.851 s),4 graph cases per EP2 rank (35.461 s), and5 routing-helper calls per EP2 rank (41.670 s). The unchanged routing oracle exercises seven rounds including uneven/skew/empty/all-empty/refill, both assignment modes/returns, and M128/C1. Exact FP32 cancellation and graph equality remain unchanged. Each group passed source/native/idle closure. One additional unchanged-helper case is being prepared for n512/H2048 so131072 reduction workers exceed the94720-worker grid stride; this closes loop-iteration coverage without replaying completed tests or changing primary source.


### Exact tail reduction: complete table and non-retention

The extra grid-stride case (original80523) passed one unchanged reference call per rank in21.058 s, closure9744783b. The complete True four-F4 AUTO14 run then passed: original36361 exit0 in434.662663 s, closure/fetch80425 successful, measured source0bf9 and native06752caf unchanged. Saved proof36734a25/result4ab0acec checks all14 rows,112 selected/winner records,56 candidate rankings and1400 samples. The first saved-reader attempt used macOS Python3.9 and failed on the existing zip(strict=True); the unchanged checks passed under modern local Python, followed by one successful comparison20615c85. No GPU replay, scorer change or row replacement.

[Complete raw before/after and matched hot tables](logs/cu132-exact-tail-vs-retained-f4-auto14-comparison-001/README.md) compare the whole retained F4 run only. Over8–8192, after/before geometric latency is0.998246695 (-0.175331%), with6/11 rows lower. All14 ratio0.983894246 includes the excluded small-token rows. Every selected dictionary is unchanged except the intended True flag. Hot selected scores generally improve0–3us; selected8192 worsens730.3→737.4us despite a lower cold row, while256 hot improves182.0→179.8us despite cold+5.065%. This discordance limits causal attribution and no confidence bound is claimed.

**Decision: do not retain.** The mixed0.18% retention-range change does not justify155 additional implementation lines. This closes a high-quality functioning design, not an unresolved compiler or numerical failure. No new current best, PR performance change, split replay, or additional micro-tuning of this reduction mapping. All six working files were verified against measured0bf9, then archived in `candidates/w4a16_exact_tail_reduce/archived-after-auto14/`: complete patch SHA76c7d8c85a87bc7161aa6a7ce32d894dab945f32e0a7421755b6c70bec90a7e7, full source/test bytes and retention receipt. Primary was restored exactly and cleanly to pushed21fd. The held ten-line metadata cleanup is unused. Bounded remote restoration needs source/native/idle closure only.

Next source-only work is a distinct FC2 activation-readiness redesign. Each CTA contributes64 post-SwiGLU I features; a K256 region can become usable before all FC1 features of that token tile finish. The held design uses cached completion masks and one-hot GPU-release ADD contributions, with a small payload-aware specialization of the existing rotating-lane batching helper, to avoid unconditional per-K global loads and extra completion storage for I2048. Weight/decode overlap, five total WGs/two decode WGs, layouts and pipeline depths remain unchanged. The new design must preserve logical K/physical stage distinction, exact partial-I bits, bit31/word transitions, release/acquire visibility, phase flush and prefix reset. No code is yet ported or validated; see `FC2_PER_K_READINESS_DESIGN.md` under the pipeline orchestration candidate.


### FC2 K256 readiness masks: reviewed and ported

Remote restoration to retained 21fd completed without replay: original 95355 and fetch 45357 exited 0, source 578f46ab, unchanged native inventory 06752caf, idle node. Receipt 26c73685 preserves the exact-tail restoration boundary.

The new five-file candidate is now visible in the primary checkout, based on 21fd. Patch SHA `3d87ac8978817c4fbf08fa17896332d106c89c1ffac87c752784082ee2f0aed5` has 123 additions and 116 removals, seven net lines. Scoped pre-commit (including pinned mypy/Ruff), AST and whitespace checks passed. No device performance claim yet.

Each FC1 CTA publishes a unique one-hot bit for its 64 post-SwiGLU features using the existing GPU-release ADD. A payload-aware owned tracker inherits the existing batching/phase-flush state machine; no vendor body is modified. FC2 acquires and caches a mask word, then tests the four reports needed for its next K256 activation tile. A ready I2048 row requires one acquire load and the existing completion footprint; larger I uses additional words. Missing regions poll with the existing acquire helper. Logical K counts, partial final groups, bit 31, word rollover and workspace prefix resets are explicitly reviewed.

Root review caught that the first held draft a697 removed an FC2 peek consumed by the direct-return epilogue, which would force its metadata prefetch behind the accumulator wait. The revision uses one common input/metadata readiness peek for both phases instead. Shared dispatch stores the metadata before input-ready publication, and both phases have the same token-block slot and valid-token threshold. FC2 feature readiness remains separately checked per K region; its activation path never skips masks based on the metadata bit. The superseded draft is preserved locally, never run. Independent source review passes the revised contract.

Native validation will cover the public N64/direct and N128/reuse configurations, I2112 word rollover, and M128/C1 static scheduling. Existing routing and graph helpers will test partial groups, delayed publication, empty/refill and replay. The decision uses one complete four-F4 AUTO sweep over 1–8192 against the retained full F4 baseline, with 1/2/4 reported but excluded from retention. No new split baseline is needed.


### FC2 readiness masks: complete validation and non-retention

Native original 23384 passed all four captures in 16.51 seconds on source b65b / manifest 502c27a1. The N64/direct, N128/reuse, I2112 word-boundary and M128/C1 static-S3 objects retain REG96, 640 threads, zero stack/local memory and their expected stages. Independent PTX/SASS review d5d5e486 verifies cached acquire masks, logical K versus physical stage state, the partial second word, one-hot per-lane release payloads, unit FC2 return, phase/final flush, and the common metadata peek before direct router prefetch. No new barrier or spill is introduced.

Existing-helper original 85562 passed five routing calls per rank (40.66 seconds), three EP1 graph cases (23.65 seconds), and two EP2 graph cases per rank (28.72 seconds), including unchanged numerical oracles. Four routing calls each use seven balanced/skew/unequal/single/empty/all-empty/refill rounds; the fifth covers H7200/I2112 with 257 skewed source tokens. The manual graph dictionaries use epilogue batch1; routing uses epilogue batches2 and32. All source/native/idle closures passed. No production test file or tolerance changed.

The full public-F4 run `cu132-fc2-mask-f4-auto14-direct-001`, original 3477, completed in 429.973824 seconds; original and close/fetch 24955 exited 0. Source b65b and native inventory 06752caf remained unchanged. Saved reader and comparator each passed once: all 14 rows, 112 selections/winners, 56 hot candidate scores and 1,400 cold-L2 CUPTI samples. Proof c1ac2eff, result 2096961d, comparison de261c26. [Complete cold and matched hot tables](logs/cu132-fc2-mask-vs-retained-f4-auto14-comparison-001/README.md).

Over 8–8192, after/before geometric latency is 0.997980056, a 0.201994% reduction, with only 4/11 rows lower. All 14 selected geometry/return dictionaries are unchanged. T8 cold improves 8.333% while its hot selected score improves only 1.543%; T8192 cold improves 3.895% while its hot selected score worsens 0.685%. Other selected hot changes are small and mixed. These complete sequential runs provide no drift adjustment or confidence bound. Counts1/2/4 remain reported but are excluded from retention.

**Decision: do not retain the mask protocol.** The functioning implementation does not demonstrate a compelling general performance gain. This is a measured negative result after native and numerical validation, not an unresolved implementation-quality failure. The original independent weight loading/decode overlap remains. No extra mask tuning, split replay, current-best claim or PR Final update is warranted.

Root verified all five primary files against the measured/proposed hashes and archived exact patch `0d095e6d4170991a0f4781b0958dc2276511cdf425bd30346a6f986955090b21` under `candidates/w4a16_fc2_per_k_readiness/archived-after-auto14/`, alongside the retention record and preceding state. All proposed files, traces and failed-draft history remain local. The five paths were restored cleanly to 21fd before applying the independent scheduler cleanup.

### Retained sizes-only scheduler cleanup

Commit `542224a1b4619f65d4730bb4fba3daf5c1cfe097` removes 48 lines from two owned files. W4A16's sole scheduler caller always supplies the stride-two Int32 counts view from dispatch; the unused prefix-sum parameter, field, alternate device branches, validation and serialization choice are removed. Ordinary required tensor arguments preserve the sole keyword caller. Shared bases and other precision schedulers remain unchanged.

Root and independent source review confirm the two active device bodies and MLIR field order equal the old non-None specialization, and extraction/reconstruction remain unchanged. Scoped and commit hooks pass, including mypy/Ruff. Actual retained source b352415b08b71d891d9570c4b4c883b17f1b30b9a7498353162441d27869b204 / manifest 7c5ecba2 contains pre-mask kernel d3644544 and scheduler d430d779. This is separate from the rejected mask; the held cleanup was originally prepared atop b65b but only its independent hunk was applied after restoration. One N64/F4 compile-only identity check against the saved pre-mask control is in progress; no numerical or performance replay is requested.


The retained cleanup's single N64/F4 compile-only check passed: original25467 and close/fetch65593 exited0, 15.740156 seconds. All 5,480 instructions match the saved pre-mask control in PC/disassembly, encoding and scheduling bytes, with no opcode difference. REG96/640/STACK0/LOCAL0/SMEM200064 and stages/grid are unchanged. Completion0967ed4d, comparator745481a9, closure37ce9bb3 confirm sourceb352/native067/idle. No GPU launch or timing replay. Commit542224a1 was pushed; combined cleanup cohorts now remove967 net implementation lines.

### Bootstrap input-staging fusion: source feasibility only

At retained 542224a1, root and the kernel reviewer traced staging through the
frontend, graph cache and shared dispatch protocol. An owned copy worker before
the existing initialization rendezvous could remove the separate staging launch.
Route IDs must follow the dispatch CTA's row ownership because dispatch reads
them before its grid barrier; BF16 activations and FP32 scores can use balanced
grid stripes. The C2 relaxed cluster arrival would need an ordinary-memory
ordering edge. The existing count exchange could then publish completed copies
before peer pulls, without a new global barrier.

This simple arrangement does not overlap a CTA's copies with its own routing
count preparation. The shared dispatch entrypoint has no intermediate handoff
for idle-role copying. Input copy traffic remains. Host work is also substantial:
the current frontend has one compiled Mega object for canonical staged inputs,
whereas raw int32/int64 IDs and staged fallback introduce separate specializations.
The current stager's capture-time dtype fallback, aliased/strided-input behavior,
dynamic live-token count and full capacity-tail ID fill must all survive. Merely
forwarding raw pointers through workspace state would not solve those contracts.

Historical current-best-0909d NSYS records the fused Bf16InputStage at 7.118 us
average for global 4096 tokens (16 calls, source056ce/af938). It is instrumented
eager evidence with rank skew, not a current removable-latency bound. The earlier
retained standalone staging fusion and rejected static-loop unroll remain separate
experiments. No prototype, transport fork, capture, numerical run or performance
claim follows this audit. Design and source pointers are saved in
`candidates/w4a16_pipeline_orchestration_review/BOOTSTRAP_STAGING_FEASIBILITY.md`
(SHA 3b28b44a). This direction remains a documented design option rather than an
active implementation change.

### Private epilogue constructor cleanup

Root independently reviewed and ported the held patch from
`candidates/w4a16_epilogue_constructor_cleanup/` (b0a6ba5a) onto retained
542224a1. It removes seven fixed constructor arguments and redundant dtype,
geometry and mode guards from the owned W4A16 epilogue. The sole maintained
caller is the owned kernel, which retains its outer validation and supplies
the required static expert shape. The epilogue is not a package export.
All actual field assignments and their order are preserved after specializing
that required shape; all epilogue JIT bodies, transport arguments and other
kernel statements are unchanged. Two files lose 38 net lines.

Scoped repository hooks including mypy/Ruff pass. Frozen source
2e3b651a854779edcd83f060cd78ff3144c01be5b71b5241b3ad6a26b778864b, manifest
36de599d, contains only those two changes. The existing native capture tools
are being reused for one N64/F4/direct instruction-identity check. No numerical
or timing replay is requested for this cleanup; native results are pending.


PR body cleanup is published and read back exactly at draft head542224a1, SHA `9a1bb8ad2d2e01281e8fb001737ee9bc78aaa24cccf35a1e2b5817f362a3eb7a`. Repetitive chronological validation was replaced with source-attributed evidence and current reproduction; stale current-head assertions were removed. Historical CUDA13.0 remains explicitly tied to6315. The entire Final performance section and template/checklists are byte-exact to the prior publication. No rejected-mask or exact-tail history was added to the PR. `PR-sizes-cleanup-published.json` records the live readback; the prior body is saved under the scheduler cleanup candidate. Primary is clean, remote b352 is idle and no further GPU process is active.

**Private epilogue cleanup retained and published.** Original native81243 and
closure/fetch89372 exited0. The one capture took15.655116 seconds; all5480
instructions, including encoding and scheduling, match the sizes-cleanup control
exactly. REG96/640/STACK0/LOCAL0, SMEM200064, raw5/B3/D3/S2 and grid[2,1,74]
remain unchanged. Completion8e837bb5, comparison2e9ac520, closure1c2b5d9e bind
source2e3b/native06752caf and idle. No numerical or performance replay.
Commit586994d8a054470a17c3dab05be8209c75a33128 was pushed after commit hooks
passed; the primary is clean. Combined cleanup cohorts remove1005 net lines.
PR5019 remains OPEN/draft at that head. Bodyf1bc24ac was published and read back
exactly; Final performance and the template remain unchanged. The preceding body
is archived inside the candidate directory; publication snapshot is
`PR-epilogue-cleanup-published.json`.

The bounded sibling/split orchestration audit is complete, saved as
`candidates/w4a16_pipeline_orchestration_review/ORCHESTRATION_RECHECK_542224.md`
(SHA42dffdeb). It finds no sufficiently supported distinct next macro experiment:
independent weight/decode overlap is already present, and further runahead needs
more storage, different work ordering or earlier metadata availability. This is
not an assertion that broader designs cannot improve performance. No speculative
transport fork or repeat of the closed tail, mask, stage or fragment trials is
added. The retained implementation and published performance stay unchanged.

### Bounded FC1 readiness scheduling and earlier FC2 return: implementation work

The user authorized proceeding with the broader overlap plan after the preceding
source audit. The first experiment changes FC1 publication order, rather than
adding weight storage: preserve the initial work publication, then let the
atomic scheduler choose a ready FC1 row from a bounded four-record window.
Decode/claim order remains monotone. Publication may change within a group, but
must drain before an FC2, next-group or terminal boundary. The oldest work must
eventually be selected even if still unready; readiness must never block the
scheduler because the epilogue consumes its next record before publishing the
previous FC1 completion. The static scheduler remains unchanged.

The held implementation and model checks are being prepared under
`candidates/w4a16_ready_fc1_window/`. Selection must be cluster-uniform and each
CTA must refresh the selected record's acquire/metadata certificate. Lazy queue
filling is being included to avoid unnecessary work when the oldest row is
already ready. No native, numerical or performance result exists yet, and the
candidate has not been adopted into the primary checkout at this point.

The independent FC2 token-block return audit found no readiness callback in the
shared transport. A minimal, unapplied upstream helper proposal and full counter,
ordering and validation design are saved under
`candidates/w4a16_fc2_block_return/`. The proposal keeps the transfer loop shared;
the vendored source remains unchanged. This is FC2-to-network readiness, distinct
from the already rejected FC1-to-FC2 per-K readiness experiment. Cooperative
pull/push would require a larger common transport refactor with nonblocking
output checks and guaranteed input progress.

The previous `fi-w4a16-mega-0911b` devbox is no longer present. The managed HAI
CLI accepted replacement `fi-w4a16-mega-0911c` on c2 in namespace ziangli with
eight B300 GPUs, `--bare`, no size override, and explicit
`nvcr.io/nvidia/pytorch:26.05-py3`. The live NVIDIA release table still identifies
26.05 as the newest release with CUDA 13.2; 26.06 through 26.08 use newer CUDA
branches. The replacement is waiting for CPU capacity on a GPU node. Existing
bootstrap and native helpers have been adapted to committed `586994d8`, without
starting a remote workload. A fresh retained Mega-only 1–8192 baseline is required
on the replacement before comparing the candidate; the old-node table remains
historical publication evidence.

**Primary candidate port and replacement recovery.** Root applied the reviewed
two-file patch `a7cb9f7d` to the requested primary checkout. It adds 247 net lines;
the static path, transport, two decode warpgroups and weight pipeline are
unchanged. The finite scheduler model passed forced reordering and fairness,
all-ready/no-ready behavior, eight edge cases and 300 sparse cluster streams.
Independent source reviews found no remaining ordering blocker. Scoped
repository hooks, including mypy and Ruff, passed. Frozen candidate source is
`206b80001eab2a12ff6d347e6894d19d862cfeee2ee56b48b0ba478b13ad2120`
(manifest `79183e92`). A separate test-only printf patch will establish whether
a numerical case actually takes the reorder branch; it is not applied to the
primary or timing source.

The replacement is ready on `hu-pdx-59`. The initial managed CLI request timed
out waiting for pod readiness, but its allocated pod subsequently finished its
image pull; no duplicate request was made. Pinned bootstrap/setup and the two
native support-module builds passed. A retained static M128/C1 compile-only
control passed in 15.05 seconds with REG96/640, STACK0, LOCAL0, SMEM194048 and
raw5/B3/D3/S3. This is a control for later comparison, not candidate validation.
The new native inventory is `09b4c8ea`. The existing full Mega-only baseline
runner has been rebound to the new node and retained source `2e3b651a`; no
candidate timing or retention result is available yet.

**Fresh baseline and candidate correctness.** The new-node retained Mega-only
1–8192 sweep completed in 430.786475 seconds. Result `208ce173` contains all
14 rows, 112 per-rank winners, 56 tactic rankings and 1,400 cold-L2 CUPTI samples;
it is the whole control for the readiness-window experiment. No split sweep
was needed. The original candidate failed CuTe dominance verification; balanced
branch carries fixed compilation, but emitted-code review then found lost
alias-based boundary/fairness updates. Seven direct `self._ready_state` writes
fixed those transitions. These are implementation failures and corrections,
not numerical or performance results. All original variants remain archived.

Corrected plain source `07d7cebc` passed native semantic/resource review and
normal numerical/graph tests: seven routing cases per rank, three EP1 graph
cases and two EP2 graph cases per rank. Receipt `11b1a208` records the original
exits and closures. Native N64 instruction count grows 5,480 to 7,432, with
almost all growth in the scheduler's duplicated mapper expansions. A separate
held simplification will address that quality issue. The diagnostic for actual
reordering and the full plain-source performance comparison remain pending;
the candidate has not been promoted or pushed.

Two separately instrumented natural-workload diagnostics then passed their
numerical oracles but observed no actual reordered publication: EP2/H7200/
I2112/T257 and EP4/H7200/I256/T2049. The latter has two feature claims per row
and longer real input traffic. Exact plain source `07d7cebc` was restored after
each. Further blind shape retries are stopped. A complete uninstrumented
AUTO14 is authorized to characterize benefit/overhead; actual reordered-path
runtime coverage remains unestablished and blocks promotion. A held loop
consolidation removes 25 source lines and reduces six whole-scheduler mapper
expansions to two in source; model equivalence passes but native/performance
evidence is pending.

**Ready-window first full result: not retained.** The complete plain `07d7cebc`
AUTO14 finished in 544.774591 seconds; result `3ded4c2c` and comparison `5b12a768`
use the whole same-node retained result `208ce173`. Latency is 2.088392% higher
geometrically over 8–8192; four of eleven cold rows are lower, no tactic changes,
and all 44 matched hot tactic scores in that range are higher. All 14 raw rows
and 56 hot comparisons are in the comparison README. No current-best claim,
promotion, PR-body update or push follows.

To address the demonstrated implementation cost before closing the direction,
root ported mapper-loop patch `3eb90df6` after the first table completed.
Scheduler `30b714a9` removes 25 source lines and collapses repeated mapper sites;
the complete candidate now adds 276 net lines. Scoped hooks/diff checks pass.
Native semantics/resources, the normal numerical/graph suite and a full AUTO14
comparison remain required. No further diagnostic geometry retry is planned;
runtime coverage of actual reordering stays explicitly unestablished.

**Ready-window final result and restoration.** Mapper-loop source `3071a6ae`
passed all three native fixtures, with actual two-body mapping and no spill,
stage or allocation regression. N64 SASS fell 7432→5984; 504 instructions remain
above retained 5480. The normal routing7/rank and EP1/EP2 graph suite passed
(`4e48580d`). Full AUTO14 completed in 466.232496 seconds; result `e175b554` and
proof `73d8d598` passed the saved reader and both pairwise comparisons once.

The smaller version is 1.470222% slower than retained geometrically over
8–8192, with two of eleven cold rows lower and 43 of 44 matched hot scores
higher. Relative to the original candidate it is 0.605524% faster, recovering
some measured overhead. Tactic choices are unchanged throughout. Complete
single-sweep results are in
`candidates/w4a16_ready_fc1_window/mapper-loop/FINAL_COMPARISON.md`; no statistical
confidence or actual reordered-path coverage is claimed.

Both variants are rejected. The full mapper diff, original variants, models,
native code, tests, diagnostics and results remain in the candidate folder.
Root verified the saved full patch and exact current file hashes, then restored
only the two candidate files to retained `586994d8`; the primary is clean.
No candidate commit, push or PR-body change was made. Devbox restoration to
the tested control completed: local and remote source are exactly `2e3b651a`,
native inventory `09b4c8ea` is unchanged and the node is idle. Receipt `8588a01c`
records the final state. No test, compile or benchmark replay was needed.

A parallel read-only audit is saved at
`candidates/w4a16_pipeline_orchestration_review/PAIRED_N64_WEIGHT_REUSE.md`.
Two N64 tiles offer no weight reuse beyond existing N128 and match the closed
ACC1/N128 storage tradeoff. Their distinct possibility is partial bank release,
which needs new activation ordering and accumulator/epilogue coordination and
has fewer paired K steps buffered by B3. Pairing two N128 tiles similarly overlaps
the already closed N256 reuse direction. No pairing implementation is justified
by width renaming alone, and no new kernel change was made for that audit.


### 2026-09-12 — compile-time geometry dispatch audit

User requested a general audit for avoidable runtime behavior. Reviewed the
owned kernel/mainloop, scheduler, epilogues, extensions, frontend/backend,
autotuner, workspace and staging, plus the PR's actual shared adapter/decoder
hook changes. Detailed findings and exact source/native references are in
`candidates/w4a16_compile_time_dispatch_audit/README.md` and its linked notes.
No vendored source or unrelated backend is changed.

Four narrow changes are implemented over retained `586994d8` / source
`2e3b651a`: FC2 uses static H and omits hidden clipping for full feature
clusters; FC1 omits its feature predicate for full clusters; the scheduler
reuses its existing block count when token padding matches the token tile;
and positive power-of-two feature divisors use compile-time selected signed
shifts, following the existing MLA scheduler pattern. Original partial-shape,
nonpower/dynamic-divisor and unequal-padding formulas remain. Live token,
phase, CTA/warp-role and pipeline-readiness checks remain runtime. The patch
adds38 net lines across only epilogue.py and fc1_fc2_fuse_sched.py, with no
public knob, helper, changed scheduler state or pipeline reordering.

Final candidate source is `dd4ce416`, manifest `a8e7f20b`; exact final source
pins are in `frozen-aligned-h/`. All applicable scoped hooks and independent
source reviews pass. Four native fixtures pass on node hu-pdx-59, B300, image
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2 system toolkit, CuTe4.7.1/native
compiler13.3.27. REG96,640 threads, STACK0/LOCAL0, two decode WGs and all
stage/shared-memory allocations are unchanged. Emitted full-shape predicates
and the C1 merged general divide are removed. Partial-H/I SASS is byte-exact
to the preceding846 candidate after the final H-elision edit; this is not a
claim of whole-kernel identity to retained. Whole-code instruction count is
not uniformly reduced (C1 5160→5152; N64/direct 5480→5536), so latency is
measured separately. `NATIVE_REVIEW002.md` and `NATIVE_PADDING_NOTE.md` retain
the instruction-level evidence.

Focused final-source numerical checks pass with unchanged tolerances:
EP1 reference4; EP2 geometry/tails6 per rank; additional C1 routing2 per rank
(static seven-round changing/empty/refill and atomic group1 partial H/I).
Subprocess times are25.54s,46.72s and27.45s respectively; all return0 and
source/native/idle checks pass. Raw logs are under
`logs/cu132-recovery0911c-compile-time-dispatch-tests-001/`.

The audit deliberately retains configuration decisions already evaluated in
Python/CuTe tracing, fixed K pipeline loops, and the previously measured
staging copy loop. Its historical unrolled version raised registers18→30 and
regressed the sweep; it is not retried. No CUDA13.0 work, profiler replay or
new test framework is introduced. One full public-four AUTO14 (1–8192,
100 cold-L2 CUPTI samples) is running on final dd4c against the whole saved
same-node retained208ce173 result. Retention excludes1/2/4. No performance
claim or publication follows until that complete comparison is available.


**First audit result and narrow ablation.** The dd4c AUTO14 completed in
425.500872s; all14 rows,56 candidate hot scores and1,400 primary samples pass
the existing saved reader/comparator. Resultd6d482be/proofd76b5b1c/comparison
aff57f4d report +0.648466% latency GM over8–8192,5/11 lower cold rows, no
winner changes, and43/44 higher matched hot scores (one equal). All14 and56
rows remain in the comparison; no speedup/significance claim or promotion.
Root restored only the two original cumulative-padding expressions to test
whether their compiler restructuring contributes to this result. Current
scheduler30c35c2b retains the divider change, epilogue68674590 is unchanged;
net+28 lines. Independent source review and scoped hooks pass. Existing
native4/focused tests and one full14 comparison against the same whole
retained208ce173 are authorized; no control/split rerun or knob change.


**Final compile-time dispatch outcome — retained cleanup, source e470.**
The retained patch is limited to the owned epilogue bounds/static H and signed
power-of-two feature-divider specialization. Both original cumulative-padding
expressions remain; the cached-count changes are excluded. Source
`e470f255b06bd492960ec21dd1b2556e36f49827fb99f1698133ce3f62102b0b`, manifest
`e9e7e9e43664ddbf07bbd62f97b618285d27bd3bee134a71e18d0143a96a7ab3`, is frozen
under `candidates/w4a16_compile_time_dispatch_audit/frozen-padding-revert/`.
The two-file patch adds 28 net lines over retained `586994d8`; there is no new
public knob, helper, state field, work ordering or pipeline synchronization.

Native semantic/resource review passed (`90a88d64`, completion `c6321821`).
Full-shape bounds and the C1 general quotient/remainder path are removed;
partial-shape bounds and nonpower signed-floor fallbacks remain. Final SASS
counts for C1 / N64 direct / N128 reuse / partial N64 reuse are
5,056 / 5,424 / 6,120 / 5,720. The N64/direct retained-source control has 5,480
instructions. Every fixture retains REG96, 640 threads, zero stack/local bytes,
1,024 static shared bytes, two decode warpgroups, and the original stages and
dynamic shared-memory allocation. These are code-size/resource observations,
not performance claims.

Focused tests on this exact source passed with unchanged references/tolerances:
EP1 regular/tail references 4 passed; EP2 geometry/tails 6 passed per rank on
two ranks; existing C1 routing helper 2 oracle calls per rank (static changing,
empty and refill routes over seven rounds; atomic group1 partial H/I skew over
one round). Subprocess wall times were 25.33 s / 47.12 s / 26.09 s respectively.
All exited 0, and source/native/idle closures passed with native inventory
`09b4c8ea`. Test completion `b4489709` pins the raw groups under
`logs/cu132-recovery0911c-compile-time-dispatch-tests-002/`.

The one complete public-four AUTO14 finished in 423.495027 seconds. Its saved
reader and comparator each passed once: all 14 rows, 112 compiled/winner
records, 56 candidate rankings and 1,400 cold-L2 CUPTI timing samples. Compared
with whole same-node retained result `208ce173`, latency GM over 8–8192 is
−0.471073%, with 7 of 11 rows lower. All 14 rows give +0.053464%, 8 of 14 lower;
1/2/4 remain reported but excluded from retention. Selected tactics are
unchanged. Matched hot scores over 8–8192 are 24 lower / 2 equal / 18 higher,
separate from the cold-L2 full-forward metric. One sweep establishes no
statistical significance or demonstrated performance gain.

Root's decision is to retain this narrow source as compile-time dispatch
cleanup with native instruction reduction and unchanged resources. No speedup
claim or PR Final-table replacement is justified. Full cold/hot output is in
[the complete comparison](logs/cu132-recovery0911c-compile-dispatch-padding-revert-vs-retained-comparison-001/README.md);
proof `c846f428`, result `06892703`, comparison `f64b6c0e`, executor completion
`088802f6`, and performance completion `2cd23585` preserve the actual evidence.
All sealed artifacts remain unchanged; only the mutable audit README and this
ledger append record the final decision. Commit, push and PR publication fields
remain pending the root's final source check and append.


**Publication verified.** Root committed and pushed the retained cleanup as
`083a9fd39e7ddda43a8b912ef50f7a13390287f9`; commit hooks passed. The checkout is
clean and the two source-file hashes remain exact to tested source `e470f255`.
PR #5019 is OPEN/draft at that head, and its updated body passed byte-exact live
readback. The historical Final performance section remains unchanged; no new
best or demonstrated speedup is claimed. Root synchronized `PR_BODY.md` and
saved [the publication receipt](candidates/w4a16_compile_time_dispatch_audit/publication.json).
This completes the previously pending publication fields without changing any
sealed native, test or performance artifact.


**Division audit and first fast-divmod sweep — preliminary result, source 3da.**
The audit at retained `083a9fd39`/source `e470f255` separates host/trace
arithmetic, constant mappings and pipeline cursor updates from actual dynamic
division. [The complete nonscheduler inventory](candidates/w4a16_division_audit/OTHER_PATHS.md)
records no additional owned-path change warranted. Raw/activation stages 5/3
use compare/reset and phase XOR in saved PTX. The shared transport's remaining
active-rank quotient/remainder has a dynamic count divisor and already shares
the quotient; setup amortization and a common/upstream integration remain
unproven, with no local vendor-body change proposed.

The bounded candidate changes only the owned scheduler to use the existing
CuTe fast-divmod primitive for positive compile-time feature counts, retaining
the dynamic/nonpositive fallback and scalar remainder. The nonnegative index
range is proved within the existing Int32 contract; the installed helper's
unsigned behavior is explicit, and all 42 admitted nonnegative probe cases
pass. Candidate source
`3da04028baeabd5355011c52b70d01225ec47d0c3656a3c83b9f60cd3a221fd3`, manifest
`58c83c6c6180382a957d6aef277690ce40f1e7f1c5338394c0f99e6fc42262ba`, is
preserved by experiment commit `4a73571891433e7ca0420d828f2a8f255188aa52`.
The source change is net −2 lines; scoped and commit hooks pass.

[Independent native review](candidates/w4a16_division_audit/NATIVE_REVIEW001.md)
`38dbdcb5` and completion `1d904114` confirm folded divisor setup, no new kernel
arguments, and removal of both partial-shape general scheduler divisions.
SASS instruction counts for C1 / N64 direct / N128 reuse / partial N64 reuse
are 5,056→5,056 / 5,424→5,408 / 6,120→6,104 / 5,720→5,680. All retain REG96,
640 threads, zero stack/local bytes, 1,024 static shared bytes, two decode
warpgroups and the same stages/dynamic shared allocations. These simpler,
more efficient generated arithmetic sequences are code evidence, not a
latency result.

Exact-source [focused tests](candidates/w4a16_division_audit/execution/test-completion001.json)
`a376d84d` pass with the unchanged references and tolerances: EP1 reference
4 passed, EP2 geometry/tails 6 passed per rank on two ranks, and C1 routing
2 calls per rank over seven changing/empty/refill rounds and one atomic group1
skew round. All source/native/idle closures pass. Native inventory `09b4c8ea`,
node `hu-pdx-59`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2 system
toolkit and CuTe 4.7.1/native compiler 13.3.27 match the current control.

One complete public-four AUTO14 finished in 421.426308 seconds. The saved
reader and comparator each passed once, preserving all 14 rows, 112
selected/compiled/winner records, 56 candidate rankings and 1,400 primary
timing samples. Sole BEFORE is the whole same-node e470 result `06892703`;
there was no baseline/split replay. Cold full-forward latency GM over 8–8192
is **+0.801507%**, with 5 of 11 rows lower; T128 is +9.500%. All14 secondary
is −1.122209%, 8 of 14 lower. Selected tactics are unchanged; 1/2/4 remain
reported but excluded from retention. Matched hot scores are 22 lower /
3 equal / 19 higher over 8–8192 and 30 / 5 / 21 over all 56 pairs, separate
from cold-L2 latency. Full output is in the
[14-row presentation](candidates/w4a16_division_audit/FINAL_COMPARISON.md) and
[56-score comparison](logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-001/README.md).
Proof `4f15237f`, result `7b98a52b`, comparison `d830c45b`, executor completion
`6dcdb68c`, and performance completion `e2b2aab1` retain the exact artifacts.

Generated-code improvement did not establish a latency gain in the first
sweep. The increases are retained without a causal claim or dismissal as
noise; one sweep gives no statistical significance. Any future partial-shape
latency benefit is unproven. Root initially decided not to promote and made
local revert `d7ef66`, restoring the `083a9fd39` implementation. Before pushing,
the user explicitly requested exactly one benchmark repeat to investigate
possible timing variation; this supersedes that retention decision.

Root restored exact candidate scheduler `9d26c662` in the local working tree
atop the unpublished revert; remote source remains `3da04028`. Experiment
commit `4a7357189`, revert and proposed PR body remain unpublished. The repeat
packet `298ecbc8` runs `cu132-recovery0911c-division-fastdiv-f4-auto14-direct-002`
with unchanged public four candidates, 14 rows, 100 samples and fresh named
caches. Native, numerical, baseline and split work are not repeated. The sole
BEFORE remains whole e470 result `06892703`. Both complete candidate results
and their separate 8–8192 aggregates will be retained, with no minima or
cross-run row selection. Final presentation will show before microseconds,
first/second after microseconds and each before/after speedup for all 14 rows.
Retention and publication await the repeat; the PR Final table remains
unchanged. Sealed first-sweep evidence is untouched.


**Final fast-divmod outcome after the requested repeat — do not promote.**
The single authorized repeat completed in 424.295636 seconds on unchanged
source `3da04028`/node `hu-pdx-59`, with fresh caches and the same public-four
AUTO14/100-sample protocol. Its saved reader and comparator each passed once:
14 rows, 112 selected/compiled/winner records, 56 candidate rankings and 1,400
primary samples. Existing native4 and focused EP1 reference4, EP2 tails6 per
rank and C1 routing2 per rank evidence was reused on that same source; no
native, numerical, baseline or split run was repeated. Exact source/native
inventory `09b4c8ea` and idle closures passed.

Against the same complete e470 BEFORE `06892703`, the repeat's 8–8192 latency
GM is +0.293781%, with 6 of 11 rows lower; the first run remains +0.801507%,
5 of 11 lower. Their geometric speedups (before/after) are 0.997071× and
0.992049× respectively. The repeat's all14 secondary aggregate is −0.367458%,
9 of 14 lower, versus first-run −1.122209%, 8 of 14 lower. All selected
tactics remain unchanged. Both complete 14-row outputs appear in the
[six-column microsecond/speedup table](candidates/w4a16_division_audit/FINAL_REPEAT_COMPARISON.md)
(`df5b6c20`); no minima, pooled samples or cross-run row selection is used.

The repeat reduces T128's observed cold increase from +9.500% to +3.023%.
This shows variability, not proof that the first value is noise or evidence
of a causal regression. T1024 and T8192 are still about 2% slower in the
repeat. Matched hot scores remain separate from cold full-forward latency:
repeat 8–8192 has 24 lower / 3 equal / 17 higher; all56 has 30 / 7 / 19,
compared with first-run 22 / 3 / 19 and 30 / 5 / 21. Neither complete run
demonstrates a general latency gain, and no statistical-significance claim
is made. Native instruction reductions, folded setup and unchanged resources
remain valid source/code evidence; future partial-shape latency benefits are
unproven.

Repeat proof `93125497`, result `6060a404`,
[comparison `66c12b98`](logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-002/README.md),
owner completion `36c96ad6`, and performance completion `2483d65d` preserve
the repeat. Original proof/result/comparison `4f15237f`/`7b98a52b`/`d830c45b`
remain immutable. This append supersedes the prior pending-retention note.

Root's final decision is **not to promote** the trial. Root will restore
the exact e470 implementation at revert commit
`d7ef66c5d48d2795781d1d3e0d51d9b24cf10258`, preserving experiment commit
`4a73571891433e7ca0420d828f2a8f255188aa52` and its removal as auditable history.
Together these add no PR implementation change relative to `083a9fd39`.
No further runs are planned. Push and final publication readback await root;
the proposed candidate PR body is unpublished, the Final performance table
remains unchanged, and only retained-head attribution will be updated.
Sealed artifacts remain unchanged; this is a mutable documentation update.


**User-directed retention and Final-table refresh — source 3da retained.**
The user explicitly instructed retaining the fast-divmod change if its
instruction count is reduced and the implementation is cleaner. Both are
verified: the standard CuTe helper removes bespoke signed/power-of-two
dispatch with net −2 source lines, and the four native instruction deltas
are 0 / −16 / −16 / −40 with unchanged resources and folded divisor setup.
This supersedes the preceding nonpromotion decision. Both complete cold runs
and all raw hot scores remain unchanged; +0.801507% and +0.293781% latency
GM over 8–8192 do not establish a broad speedup, and partial-shape latency
potential remains unproven.

Root retained exact source `3da04028`/scheduler `9d26c662` in commit
`9a0b5d001d32a0bdef5102079a85a6843646e7d9`, with all commit hooks passing.
Experiment `4a7357189` and revert `d7ef66c5` are preserved history; the retained
implementation is the standard-helper change. Push is confirmed complete and the repository is clean; PR publication
readback remains pending the matched table refresh.

The user's requested PR Final refresh uses the entire latest completed Mega
repeat `6060a404`/proof `93125497` on node59 as its current column. No row
minima or selection across repeats is permitted. The only saved publication
split runs are recovery0911a (13 rows) and recovery0911b (14 rows); the latter
explicitly ran on node15, so neither supplies the current node59 baseline.
One [matched split14 packet](candidates/w4a16_publication_split_refresh/recovery0911c/plan.json)
is prepared under `cu132-recovery0911c-publication-split-auto14-001`, with
plan `dc8c5d97`, command `20ffc656`, and stage `d7d0eaea`. It reuses the
byte-exact shared-weight bridge `4989b005`, unchanged split tuning/timing,
eight ranks, 14 rows and 100 samples. Source3da, preflight203c, environmentfaa2
and existing native09b4 bind the same image/stack as the Mega repeat.

The sole executor owns this one split run and any first-use native-support
additions under the existing integrity closure; no new Mega, native fixture,
numerical test or oracle run is authorized or required. The current Final
raw split/Mega table and self-contained PR reproduction/validation update
await the completed saved split reader. Detailed experiment history stays
in this ledger, outside the public PR body. All previous evidence is intact.

**Matched Final table published — retained FastDivmod source3da.**
The one authorized node59 split run `cu132-recovery0911c-publication-split-auto14-001` completed with original45616 exit0, 602.454592 seconds, complete fetch84145/0 and source/native/idle integrity PASS. Its sole saved reader passed first invocation: full14 rows,112 rank tactics,1400 samples; result `2cf158b0`. Old non-log dependency bytes stayed exact, with54 first-use split support entries added.

The [full publication table](candidates/w4a16_division_audit/FINAL_PUBLICATION_COMPARISON.md) combines that whole split result with the fixed latest whole Mega repeat `6060a404`, both source3da/node59/image26.05. GM split/Mega over8–8192 is1.108024665× (9.749301% lower latency);11/11 rows favor Mega. All14 rows are displayed,13 favor Mega, andT1 is slower. No row minima, additional Mega/native/numerical replay, causal FastDivmod attribution or statistical-confidence claim is made.

Root published body `c91230ff` and verified exact live readback on OPEN/draft PR5019 at retained commit `9a0b5d001d32a0bdef5102079a85a6843646e7d9`; root `PR_BODY.md` is synchronized. [Publication receipt](candidates/w4a16_division_audit/publication-refresh-receipt.json) SHA256 `8eade366d01ba23ebf91129b2cc950676ba167d6506c919d2b529a4d685edc55`. Historical CUDA13.0 table and template/checklist remain byte-exact. Both optimization sweeps and their original decisions remain preserved history; user retention of the cleaner standard-helper implementation is the final outcome.

**Retained route-pair reuse and separate cleanup — measured5e9c, current680b.**
The one whole source5e9c AUTO72051 completed424.801690 seconds with exit0 and complete closure/fetch12497/0. Sole saved reader/comparator passed14/112/56/1400; proof4d440f94/result2ba8861d/comparison70645aeb, performance completiona035475a. [Full14 before/after speedup table](candidates/w4a16_fc2_route_pair_reuse/FINAL_COMPARISON.md) retains all rows and all56 matched hot scores against whole3da repeat6060. GM8+ latency−0.295598%,7/11 lower; choices unchanged; hot44 directions21/3/20.

[Selected-return partition](candidates/w4a16_fc2_route_pair_reuse/SELECTED_RETURN_SCOPE.md): changed N64/direct8–1024 is−0.164361%,5/8 lower, while native-identical selected N128/reuse2048+ is−0.644723%,2/3 lower. These negligible/mixed one-sweep observations do not establish material/general or causal gain. Retention is for simpler pointer reuse and fewer native address/predicate instructions (C1−24,N64−16), not fewer final LDGs; two reused native controls are exact. Native5 and focused4EP1/6EP2 perrank/2C1 perrank with unchanged oracles/tolerances/closures pass. Commit7d0434eb8b6d80cb482e44dc69a5fb35d914b3db is pushed.

The independent unused-field/required-alpha cleanup removes25 lines in pushed clean head8c975512665ec5de80d44cc54d1c8ed94a14f9f9, source680b17f0. One5392-instruction N64/F4/direct native identity capture matches5e9c in PC/encoding/scheduling, entry arguments/descriptors and resources; completion08ba20dd and review85d37005 pass. No numerical or timing replay is claimed at this source.

[Updated Final table](candidates/w4a16_fc2_route_pair_reuse/FINAL_PUBLICATION_COMPARISON.md) uses entire Mega2ba8861d with existing matched split2cf158b0 (source3da), no new split/Mega/native-test sweep. GM split/Mega8+1.111309677×,10.016081% lower,11/11; all14 raw rows favor Mega. Draft Final retains distinct measured-source and later-cleanup attribution. Root published and verified exact live readback on OPEN/draft PR5019 at head8c975512665ec5de80d44cc54d1c8ed94a14f9f9; body SHA256 e574af88b55b16878177fb183caffb8aa8e2c41c536e303c15ea810f4e35a0b2. Root PR_BODY.md is synchronized; [publication receipt](candidates/w4a16_fc2_route_pair_reuse/publication-refresh-receipt.json) records both measured sources and the cleanup boundary. Sealed trial comparisons remain untouched and no history table enters the public PR body.


## CUDA 13.0 current-head refresh — 2026-09-14

User requested a new CUDA13.0 devbox and a refreshed public Final table. No source/kernel/autotuner changes were made. Current head `7f1a093119f12b1f5b79d50bf6d0c951069224e5` passed6 exact decoder,8 EP1 oracle/precision cases and6 EP2 tail/geometry cases per rank on C2 B300/node87/image25.11. Actual DSL4.7.1 cu12 compiler12.9 selects the unmodified pre13.2 fallback; all8 worker maps verify the expected older runtime stack.

The one complete public combined benchmark passes28 latency rows,2800 primary samples,112 collective Mega winners and14 ratios. GM over8–8192 is `1.124511777900×`, `11.072518790%` lower latency;11/11 retention rows and13/14 reported rows favor Mega. Token2 is slower and remains displayed. No row minima/repetition or cross-stack causal claim. The CUDA13.2 table remains unchanged. Full current command, versions, raw tests/samples, tactics, source closure, old body and publication receipt are retained in [cu130-refresh-20260914](cu130-refresh-20260914/README.md).

| Global tokens | Split W4A16, non-fused finalize (ms) | W4A16 MegaMoE (ms) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 0.090673 | 0.081809 | 1.1083× |
| 2 | 0.117761 | 0.122049 | 0.9649× |
| 4 | 0.165169 | 0.133489 | 1.2373× |
| 8 | 0.181313 | 0.163266 | 1.1105× |
| 16 | 0.213746 | 0.185649 | 1.1513× |
| 32 | 0.251570 | 0.221602 | 1.1352× |
| 64 | 0.278898 | 0.251313 | 1.1098× |
| 128 | 0.291282 | 0.252994 | 1.1513× |
| 256 | 0.306515 | 0.247842 | 1.2367× |
| 512 | 0.295762 | 0.268978 | 1.0996× |
| 1024 | 0.313587 | 0.282274 | 1.1109× |
| 2048 | 0.359523 | 0.346067 | 1.0389× |
| 4096 | 0.551333 | 0.509108 | 1.0829× |
| 8192 | 0.982024 | 0.851399 | 1.1534× |

Over 8–8192 tokens: geometric mean speedup **1.1245×**; 11/11 rows faster.

All times are medians of 100 cold-L2 CUPTI samples, taking the maximum rank span per iteration; CUDA graphs enabled. The saved launch command must separately establish non-fused split finalization and environment provenance.

All4896 tracked files match canonical checkout; head/source/native identity and idle-GPU closure pass. The timing utility wall sum is14.932385 seconds; first-use CUDA13.0 support compilation dominated total iteration time. CUPTI stayed active, with no fallback/traceback. Detailed allocation/diagnostic history is in the linked runbook. Public body published and exact readback verified at ready-for-review head7f1a0931; body SHA256 `ddaccc0824f42094e0f86ee0d70143dac98bd49d9bb3514982356a9d1bff8679`. [Receipt](cu130-refresh-20260914/publication-check.json).

## 2026-09-15/16: four-fix cost and duplicate FC1 wait candidate

Fresh native before `7f1a093119f12b1f5b79d50bf6d0c951069224e5` versus after
`a48e5706c2a7775b0b698aa8eccb4e124b02118c` isolates the global proxy fences,
TMEM transpose completion waits, FC2 warp-row addressing, and elected scheduler
publication. Both arms use the identical current benchmark with untimed weight
quantizer PDL disabled. Eight B300 GPUs on replacement node `hu-pdx-69`, image
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2 runtime, native compiler13.3.27,
O3/maxregs96, four-tactic AUTO, EP8/H7168/I2048/E256/topk8, non-fused finalize.
Each full sweep covers global1–8192 tokens with3 warmups and100 cold-L2 CUDA
graph CUPTI samples; metric is median per-sample rank-MAX span. Order is
A1(before),B1(after),B2(after),A2(before), with fresh per-sweep caches. No Split
rerun or cross-node timing comparison is used for this decision.

All56 timing rows and448 saved rank/token output checks are valid, including
both baseline8192 rows. Full raw collection, independent parser-free arithmetic
and root review pass:98 files,32 full tensor files,5,600 raw samples. The initial
transport reset affected download only; the resumed archive matches original
SHA256 `24d07ae9cf809032d6b428a0f1d022ea5194eb5ab8670e936b7d1ec40d410304`.
Fresh recorded process/GPU closure passed before handing the node to codegen.
[All raw medians, ratios, tactics and provenance](final-four-fixes-perf-20260915/RESULT.md).
The8–8192 combined geometric ratio is1.0010155x, but that hides same-tactic
slowdowns in both orders:128 tokens+3.54% latency,512+4.78%,32+1.12%, and
4+5.05%. All four sweeps select N64/epilogue return for these rows. At128,
within-arm drift is below0.25%, substantially smaller than the observed cost.
The256 and8192 pair ratios reverse sign by order. Two sweeps per arm are
descriptive; individual graph samples are correlated. Tokens1/2/4 stay visible
and remain excluded from the aggregate.

First candidate: native local commit `979ac4bd532ca1d9e2f5309b3935e77b0759d30d`,
paired HashInfer `ec60097261c9a851e5f616adb05e3ed4349c9f8a`, both unpushed.
Exactly three lines are removed from the owned FC1 epilogue: the early TMEM
load wait and its comment. The centralized R1 wait immediately before scratch
overwrite, every other transpose wait, accumulator release waits, global
proxy fences and ownership fixes remain. Both scoped pre-commit runs pass;
the changed files match after namespace normalization. The patch and native
Git bundle are in `final-four-fixes-perf-20260915/fc1-wait-candidate/`.

The [source/ISA re-audit](final-four-fixes-perf-20260915/FC1_DUPLICATE_WAIT_REAUDIT.md)
shows only register work between the two waits. Captured guarded PTX retains
both, but ordinary generated code must establish whether removing one changes
instructions. Compare a48 versus candidate O3 N64/epilogue code at128/512
before timing the candidate; keep the original four-sweep evidence frozen.
No performance improvement or GPU qualification is claimed for this candidate
yet. Further candidates are documented in [the overhead audit](final-four-fixes-perf-20260915/OVERHEAD_CANDIDATES_A48.md)
and [all-writer publication batching audit](final-four-fixes-perf-20260915/FLAG_BATCH_PROXY_FENCE_AUDIT.md).
The register pool remains61,440 with epilogue144, two decode warpgroups and
five total warpgroups; do not repeat the prior65536-register allocation stall.

The complete four-fix table is published in PR5019; exact readback and unchanged
ready-for-review head a48 are recorded in
`final-four-fixes-perf-20260915/publication-check.json`. Body SHA256
`a97f37e0eafbc24bee0848a471ab6328465dd4a8966312861279977281db40cd`.
The new candidate remains local/unpushed and is not represented as a tested
performance improvement in that public body.

### 2026-09-16: ordinary codegen for duplicate FC1 wait deletion

- Native local/unpushed `979ac4bd532ca1d9e2f5309b3935e77b0759d30d` and paired HashInfer `ec60097261c9a851e5f616adb05e3ed4349c9f8a` remove only the early FC1 wait; R1 overwrite/release completion waits remain.
- Fixed N64 epilogue-return, global128/512, EP8, O3/maxregs96 on hu-pdx-69: all32 rank/token output checks remain exact. All16 executable text pairs differ. PTX load waits18→16; SASS drops two interior NOPs but adds trailing padding, leaving5424 slots/identical opcode histograms. Local scheduling/register assignment also changes; this is not two fewer dedicated hardware-wait opcodes or a measured speedup.
- All175 evidence files/44,447,440bytes independently rehashed; processes closed and all8GPUs idle before timing handoff. Full report: `final-four-fixes-perf-20260915/fc1-wait-candidate/CODEGEN_RESULT.md`.
- Authorized next measurement: one full AUTO1–8192 candidate sweep versus reused corrected a48 B1/B2 on the same node. Preserve every row and exclude1/2/4 only from the aggregate retention metric. No Split rerun or capture flags during timing.
- Separate unapplied alternatives: paired FC2 transpose rounds (six shared completion waits instead of twelve source waits, unchanged epi144/register pool) and earlier per-writer proxy fences before the existing epilogue rendezvous (same fence count). Source proofs/reviews live under `final-four-fixes-perf-20260915/fc2-paired-transpose/` and `proxy-fence-placement/`. Neither has compiled numerical or performance evidence yet.

### 2026-09-16: first full FC1 cleanup sweep and review followups

- C1 on979ac4bd finished in503.70s; all14 rows/1,400samples/112rank outputs and exact finite/bit-repeat controls pass. Full56-file/241,124,324-byte evidence was collected and independently verified under `final-four-fixes-perf-20260915/fc1-wait-candidate/perf/evidence/collected/20260916T034120Z-1ecb3d7b40574a2f84c02fa437e899d6`.
- Compared with corrected a48 B1/B2, the8–8192 geometric baseline/C1 ratio is0.98895456.128tokens improves to205.634us vs214.753/214.241us (1.0431x);8tokens145.073us vs136.0485/135.9855us and1024tokens235.426us vs228.162/228.6095us regress with unchanged tactics.512tokens219.6815us is within baseline218.514/227.074us spread. No promotion decision from this single sweep. Full table: `fc1-wait-candidate/perf/terminal-preview.md`.
- Authorized confirmation: one repeat979 sweep followed by one fresha48 sweep, all1–8192, same original timing/fixture gates. Collect together after both sweeps. FC2 paired-transpose and earlier-proxy-fence alternatives remain unapplied.
- Latest bot review: local nativef3a3e714/Hash8b1539f reject CPU W4A16 inputs; native also scopes NCU requirements to executable EP cases and adds one row to existing invalid-input tests. Scoped pre-commit, isolated real CPU-Torch validation/profile checks and independent diff review pass. Full package test remains pending, and neither commit is pushed. Kernel code and frozen measurement sources are unchanged.
- Staging-cache audit found no demonstrated stale-address launch bug because the descriptor key covers all tensor pointers/shapes/strides and stream. Existing universal staging likewise retains its launch cache. No cache-lifecycle code change; audit under `staging-cache-lifecycle-audit/REVIEW.md`.

- Review followup integration completed on clean nativef3a3e714:40 passed,1 deep_gemm skip in the unchanged validation file. CUDA-hidden import was blocked by unrelated mandatory GDN device-property initialization; a separately verified idle physicalGPU4 on the sanitizer node allowed package import. GPU4 returned idle, with original race GPUs0–3 unchanged. Evidence/review: `review-followups/native-gpu4-summary.json` and `root-integration-review.json`.

## 2026-09-16: FC1 retention and FC2 trial

Fresh full C2→B3 sweeps passed all 28 timing rows/2800 samples/224 output checks. Same selected tactic in each paired row. The FC1 wait deletion gives 0.991751455 geometric B3/C2 speedup over 8–8192; the initial 128-token gain did not repeat. Fresh B3/C1 is 0.999147343. Historical t8 regression was baseline drift; no benefit supports promotion. Complete paired evidence (70 files/16 raw tensors) was independently rehashed locally. Preserve trial on archive/fc1-wait-trial-20260916 in both repositories and restore FC1 wait.

Replay only the independently tested host/API fixes onto the original corrected baselines: native 7717228f, Hash e0f6b4c. These commits are pushed; public 5019 remains ready and Hash2 remains draft. The 40 passed / 1 skipped native validation-file result was obtained on originalf3a3e714; its validation/test files are unchanged by replay, and no kernel-performance claim is attached.

Paired FC2 transpose waits now exist locally as native 71f94c12 / Hash f14a1b1, unpushed. Source/address/ordering reviews and scoped pre-commit pass. FC1's early wait is retained. Ordinary O3 codegen/all-four-tactic numerical/resource checks are next; no performance or sanitizer qualification is claimed yet. Original 224b EP4 unfiltered racecheck continues unchanged.

## 2026-09-16: FC2 generated code and combined cleanup candidate

Native71f94c12 versus a48 passed all four fixed tactics at1024/8192:128 exact output/capture checks,64 executable comparisons, all normal exits. N64 epilogue/dispatch PTX load/store waits18/14→15/11 and SASS TMEM fences14→11. N128 epilogue/dispatch32/26→26/20 and26→20. All paired resources remain REG96/STACK0/LOCAL0/SHARED1024 with unchanged epi144 policy and no LDL/STL. Instruction slots include padding; no speedup is inferred. Full715-file/104,318,303-byte local collection and archive rehashed by root;64 full trial tensors remain remote with whole-file proof bound before/after collection. Full report: fc2-paired-transpose/codegen/RESULT.md; qualification7569b14d.

The user prefers keeping the correct redundant FC1 source-wait removal as a simplification, even without a clear timing benefit. Added the requested two-line ordering comment and reapplied in separate local native8da5ab77 / Hash1887e093 commits atop71f/f14. Scoped pre-commit passes and paired epilogues normalize exactly. These combined candidates remain unpushed. Isolated C3 timing remains frozen on71f against fresh a48 B3; combined strictEP4 will use1887 onBox1 GPUs4–7 while the existing224b race continues0–3. Long guarded runs wait for final performance selection and same-source ordinary qualification.

## 2026-09-16: completed FC2 and combined sweeps

The user's headline BEFORE remains `7f1a0931`, before all four correctness fixes. Corrected `a48e5706` B3 is only the control for attributing an individual optimization. All comparisons below use the same hu-pdx-69 node and full 1–8192 AUTO/O3 sweep, with 3 warmups and 100 cold-L2 CUDA-graph CUPTI samples per row. Only 1/2/4 tokens are excluded from aggregate retention criteria.

- FC2-only C3 (`71f94c12`) versus corrected B3: 1.006700735x geometric speedup over 8–8192; 7/11 rows improve, but 1024 is 2.86% slower and larger rows remain mixed. Versus original BEFORE summarized as sqrt(A1*A2), C3 is 0.997443x. Full raw evidence and all eight output files were collected and rehashed.
- Combined C4 (`8da5ab77`, paired Hash `1887e093`) versus original BEFORE: **0.995549899x**. FC2-only C3 / combined C4: **0.998102277x**. Corrected B3 / C4: 1.004790296x. All 14 selected tactics match. Complete requested table and raw evidence bindings: [FINAL_COMPARISON.md](final-four-fixes-perf-20260915/combined-candidate/perf/FINAL_COMPARISON.md) and its JSON. C4 has 14 valid rows / 1,400 samples / 112 exact finite/repeat checks; 58 archived files, including eight full output tensors, passed independent hash and closure verification.
- Retain both changes for final qualification, following the user's preference for correct source simplification. No uniform timing gain is claimed; later single candidate sweeps do not cancel temporal drift. FC1 keeps its centralized wait before scratch overwrite and now documents why the earlier wait is redundant. This removes source waits, not an observed SASS fence instruction from FC1. FC2's separately measured generated-fence reduction is recorded above.
- Combined strict EP4 passed 30 cases / 480 configurations / 5,040 exact BF16-bit comparisons / 1,200 repeats, with clean exits and scoped GPU closure. Strict EP8 and the unchanged native28/45 suite are next on Box2. Guarded EP4 now runs on Box1 GPUs 4–7; original unfiltered racecheck remains unchanged on 0–3. A launch preflight prefix mismatch was fixed only in the local validation helper, preserving the failed record and adding a test using the actual collected supervisor summary. No kernel/test/tool-option change resulted.

See [STATUS.md](final-four-fixes-perf-20260915/STATUS.md) for exact archive hashes, process identities and remaining validation gates. Commits are still local/unpushed at this point. A one-time final same-node Split sweep is being prepared for the public performance table; historical hu112 Split results must not be combined with hu69 Mega results.

### Superseding decision: retain the early FC1 wait

The user rejects the FC1 cleanup because all 8–256 decode cases regress versus FC2-only C3. Native `4d183b83` and paired Hash `dbd3cea` restore the early wait and add a short comment explaining the register-only interval and retained central overwrite-protection wait. Only comments differ from measured FC2-only native71f/Hashf14; AST identity and paired source normalization pass. Pre-commit passes, source trees are clean, commits remain unpushed.

C4 remains an archived rejected candidate. Its completed EP4 strict matrix and ongoing EP4 guarded run must not be relabeled as selected-source validation. Already running native8da tests will finish and be collected; remaining ordinary/guarded validation is redirected to selected4d/dbd. The selected performance table explicitly reuses C3 at71f, not a new timing claim on4d. Details and final source hashes: [restored-wait/decision.json](final-four-fixes-perf-20260915/fc1-wait-candidate/restored-wait/decision.json).

## 2026-09-16: retain FC1 wait; publish paired FC2 transpose

User rejected early-FC1-wait deletion because all8–256 decode rows regressed versus FC2-only. Restore it with the short explanation of correctness redundancy and decode performance. Native4d183b83 / Hashdbd3cea retain the paired FC2 transpose; Hash1ba33fa only refreshes README's upstream pin. Both are pushed. Ordinary native28/45 and selected Hashfull60 (960configs,10,080 exact-bit comparisons,2,400 repeats) pass; guarded/race sanitizer work remains ongoing and separately labeled.

One final fresh Split sweep on hu69 is complete, compared to retained measured71f C3 Mega (comment-equivalent to native4d). All14 rows are in final-four-fixes-perf-20260915/final-split/independently-verified.md; all8–8192 rows favor Mega and geometric Split/Mega is1.099079653. Original-before-fixes7f A1/A2 versusselectedC3 remains0.997442769 overall, not the corrected a48 optimization control. Both tables/provenance are in publicPR5019. Detailed full raw collections and root reviews remain under final-four-fixes-perf-20260915; no historical trial is relabeled as a current measurement.


## 2026-09-16 08:03 UTC: selected guarded memcheck completed

Selected dbd EP4/EP8 guarded memcheck passed all eight cases, all four tactics/O2/O3/eager/graphs, with 384 reference + 960 pair comparisons and 320 repeats bit-exact; all12 rank summaries report zero errors. Raw archives, codegen, source and closure are fully collected and independently checked. EP4/EP8 instrumented phases took3068.072286/3323.205032 seconds, not latency measurements. Tensor-form TMA checking remains disabled for the established standalone-control false positive; compiler TMEM guards are enabled. Full evidence: hashinfer-w4a16-megamoe/sanitizer-guarded-selected-final-20260916/SELECTED_RESULTS.md. Both PR bodies updated/readback verified; source and final performance unchanged.

Selected worker4 full-scope EP8 racecheck launched after guard/collection/idle gates. Original224b EP4 race continues unchanged until outer09:05:17 UTC. No race-clean claim; strict INFO findings remain visible. New bot final-FC2-wait suggestion was independently rejected from PTX register-dependency and all release-path analysis; see final-four-fixes-perf-20260915/fc2-paired-transpose/final-wait-review/ASSESSMENT.md.


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
