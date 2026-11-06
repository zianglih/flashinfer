# W4A16 MegaMoE performance experiment ledger

## Current CUDA 13.2 state: fused BF16 staging, 2026-09-09 UTC

Code is pushed atca03a947 after the completed0909d staging AUTO. Ten-row
8–4096 latency GM improves3.3634% over direct FC1ca224,9/10 wins, with only
T1024+1.0074%. All13 rows are preserved in
[comparison9cefe6b5](logs/cu132-recovery0909d-fc1-vs-bf16-staging-independent-comparison-001/README.md).
Current9 staging GPU tests+4 EP2 rank-tests/16 Mega objects pass; FC1/B3/math
and catalog lifecycle evidence remain inherited. Full13/104/1300 and separate
87 fused/17 empty staging observations reconcile; all80 retention cases fused.
Measureda747→publishedca03 has exact device/backend bytes with explicit-default
host syntax and public-test relocation, not full-source byte identity.
[Publication/readback](logs/pr5019-bf16-staging-publication-001.json) verifies draftca03/body
fba7bee4d0b85693daa0640241dce1ec95ae6a404851e21bc0606bcf58c7e10a.
See optimization ledger054 and current state.

The following entries retain their original source and time boundaries.

## Historical measured state: 6315f94c, 2026-09-08 UTC

The curated twelve-tactic interface is pushed in draft PR5019. It reuses the
existing Mega dictionaries, collective sweep and cache. Source validation,
all twelve candidate oracles, graph/cache lifecycle, 105 public host tests
and full pre-commit pass. Full13 and adjacent repeat artifacts attest the
same 1571 source files and four benchmark helpers on C2 B300 x8 / CUDA13.2.

- [Complete full13 control/auto evidence](logs/tmem-auto-full13-001/analysis/final-table.md):
  all 52 raw latencies, 208 split choices and 104 Mega rank confirmations.
  Auto at4096 is0.487970ms vs split0.538869ms,1.1043x. Small-token losses
  remain visible. PR Final performance uses the entire auto process run.
- [Recorded-winner repeat](logs/tmem-auto-selected-repeat-001/analysis/repeat-report.md):
  8.01% lower Mega latency at256 and3.63% at4096 versus adjacent fixed
  controls;16 is nearly tied. No selected-row minima replace the full table.
- Current N64 profiles are `profiles/tmem-n64-stage3-current-nsys-001` and
  `profiles/tmem-n64-stage3-current-ncu-pc-001`. Both capture all eight ranks.
  Actual N64 resources are640threads/96registers/183808dynamicSMEM; rank0
  full SASS contains no local loads/stores. Instrumented durations are excluded.
- Detailed development record, failed experiments, source limitations and
  unapplied K128/C1 research: [optimization ledger](w4a16_optimization_experiments.md),
  section016. The paragraphs below preserve earlier decision states and are
  historical unless explicitly identified as current6315 evidence.

## Current user constraint: two transform groups

The user explicitly requires two dequantization/transform warpgroups for the
continuing W4A16 MegaMoE tuning. One-group configurations are historical
controls only and must not be a future autotuning axis. The thin tuner uses
validated M/N geometries, existing flag batching and token-return modes; raw
and decoded stage counts remain derived by the kernel, with the BF16/FP32
numerical contract fixed. This preference is recorded only in this effort
ledger; no memory files were written.

## Historical numerical-source provenance correction

Earlier geometry-run manifests used git-ls-files-only discovery. The remote
checkout carries untracked W4A16 shim/backend/test overlays, so those manifests
do not independently attest every runtime/oracle source even though observed
geometry and per-rank numerical reports remain valid. Do not backfill them or
relabel later hashes as contemporaneous. Separate codegen/timing manifests
that explicitly recorded required source files can independently attest
their own snapshots; each claim must use its actual capture.

Future `run_geometry_tests.sh` runs use `flashinfer-w4a16-geometry-source/v2`,
explicit required paths plus filesystem discovery under the public MoE,
vendor, local W4A16 decode and quantization trees. Missing required files fail
before launch. The launcher hashes helpers as well, then requires identical
source/helper inventories after successful tests. Old manifests cannot pass
the v2 source verifier. Installed dependencies are recorded by version, not
claimed to have source-hash closure.

CPU coverage: tracked-only dummy Git index deliberately omits the kernel/test;
v2 still captures both and rejects missing/mutated source or historical
manifests. The real local inventory passes capture/verification. Remote helper upload
returned success, but the managed CLI then reported the devbox missing while
fetching the log; remote verification is pending retrieval. Local evidence:
`logs/geometry-provenance-v2-local-cpu-001.log`.


This local ledger preserves optimization history. The upstream PR body contains
one current-best 13-shape timing table; earlier experiments are not final-head
results. The complete pre-cleanup PR draft is archived in
[PR_BODY.pre-final-table-c7713ba1.md](PR_BODY.pre-final-table-c7713ba1.md), and the
pre-TMEM draft remains in [PR_BODY.pre-tmem-16aa85bd.md](PR_BODY.pre-tmem-16aa85bd.md).

- Corrected H9216 stage diagnostic: [H9216_NUMERICAL_ATTRIBUTION.md](H9216_NUMERICAL_ATTRIBUTION.md)
  retains exact split/Mega equality at all three stages for both original and
  fan-in-normalized arms, the shared original-oracle failure, and its FC1
  rounding attribution. The new geometry fixture alone is normalized; no
  tolerance changed. Run001's invalid split preparation is explicitly preserved.
- Adjacent fitted one/two transform-group full13 experiment:
  [FITTED_TRANSFORM_GROUP_COMPARISON_001.md](FITTED_TRANSFORM_GROUP_COMPARISON_001.md)
  retains all 52 raw outputs and 208 actual selections. It includes the T64
  regression requiring the parent's separate repeat; no row is silently dropped.

- Initial scalar/SMEM source15eb1c62 and controlled vector source12b62378: full13
  baseline and adjacent vector/counter controls below.
- Isolated fixed/dynamic TMEM candidates: five-shape timing, actual tactics,
  codegen and independent EP8 oracle below; source snapshots live under
  `candidates/w4a16_swap/controls/`.
- Public compute f952b398: complete five-profile scheduling sweep, all50 raw
  values and200 actual tactic selections in
  [TMEM_REFERENCE_SWEEP_001.md](TMEM_REFERENCE_SWEEP_001.md),
  `logs/tmem-reference-sweep-001.comparison.json` and `.raw.csv`.
- Current f952 Nsight Systems and one-pass NCU: all raw stage/counter values and
  their denominator/collective-replay caveats below.
- Profiling-only c7713ba1: the combined multi-pass/PC run002 completed both32
  and4096 across all8 ranks; extraction and interpretation are still pending.
- Controlled raw2/raw3 comparison: [RAW_DEPTH_COMPARISON_001.md](RAW_DEPTH_COMPARISON_001.md)
  preserves all20 timings and80 actual split tactics, verified with only the
  kernel source changed. Raw3 improves18.10–24.63% at T8–4096 in that paired
  experiment; the one-run4096 split/Mega1.0337× observation awaits repeats.
  Raw5 and transform2 remain experiments under coordinated validation.
- N64 is an unapplied CPU-only candidate built from f952, independently of raw
  depth changes: [candidate notes](candidates/w4a16_swap_n64/README.md).
  It preserves N128 by default, uses the existing tile knob and has no GPU
  result or performance claim.

### Historical public CUPTI scheduling sweep: f952b398

DeepSeek-V3 H7168/I2048/E256/top-k8, EP8, global tokens 1/8/32/128/4096; three warmups and 100 cold-L2 CUDA-graph CUPTI iterations for each split/Mega pair. All 16 recorded repository source hashes in each of the five provenance logs match f952b398 exactly; the remote checkout base is older and is not the tested overlay identity. The tactic recorder wraps the normal benchmark, records only selection calls, and does not add recorded calls to the timed iterations. Weight preparation, compilation, autotuning, graph capture and L2 flush are excluded. The reported value is the median of each iteration's rank-MAX earliest-to-latest GPU activity span. All runs use the same canonical packed weights, routes and BF16 contract with `--no-fused-finalize`. The optional cross-backend final-tensor `--refcheck` remains omitted for the exact rank-partial rounding difference documented below; tolerance is unchanged.

These five profiles change existing scheduling knobs only, keeping M256/N128/K256, cluster `(2,1)`, dynamic N and the public BF16/FP32 contract. Relative to default, the named profiles change group size, scheduling mode and flag batching together; this is not an isolated flag-size experiment. The four nondefault profiles reuse the existing MegaMoE sweep's atomic/group/flag/return axes; they do not select its activation-quantized kernels.

| Profile | `group_hint` | Load balance | `flag_batch` | `epi_flag_batch` | Token return |
|---|---:|---|---:|---|---|
| default | default → 74 here | static | 1 | `(1,1)` | `epi_warps` |
| flag4-epi | 512 | atomic_counter | 4 | `(2,4)` | `epi_warps` |
| flag4-reuse | 512 | atomic_counter | 4 | `(2,4)` | `reuse_dispatch_warps` |
| flag8-epi | 512 | atomic_counter | 8 | `(2,4)` | `epi_warps` |
| flag8-reuse | 512 | atomic_counter | 8 | `(2,4)` | `reuse_dispatch_warps` |

Raw Mega milliseconds, to compare the scheduling profiles:

| Global tokens | default | flag4-epi | flag4-reuse | flag8-epi | flag8-reuse |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.106640 | 0.110176 | 0.123665 | 0.117216 | 0.122609 |
| 8 | 0.305458 | 0.226114 | 0.232690 | 0.227074 | 0.224450 |
| 32 | 0.401124 | 0.298051 | 0.316194 | 0.297889 | 0.314787 |
| 128 | 0.469076 | 0.346707 | 0.370691 | 0.345442 | 0.369027 |
| 4096 | 0.715687 | 0.649222 | 0.672419 | 0.674884 | 0.701848 |

All five profiles remain slower than their paired split W4A16 control at every measured shape. Default is fastest for Mega at one token. The lowest measured Mega times are flag8-reuse at eight tokens, flag8-epi at 32/128, and flag4-epi at 4096. At 4096, flag4-epi measures 0.649222 ms versus its paired split 0.555861 ms (split/Mega 0.856195). The lowest observed Mega time at 8/32/128 is 25.74–26.52% lower than default; at 4096 the reduction is 9.29%, but Mega remains 16.80% slower than paired split. Every nondefault profile regresses Mega's one-token time by 3.32–15.96%. These are one sequential sweep's observations, not an automatically selected policy, retained default change or repeated-run uncertainty estimate. Differences between nearly tied profiles require adjacent repeats. Split is independently autotuned in each process/rank; its observed max/min spreads at 1/8/32/128/4096 are 32.23/7.05/4.83/8.69/2.18%, not statistical error bars. The paired measurements are retained below.

Complete 50 raw timing values from `tmem-reference-sweep-001-{default,flag4-epi,flag4-reuse,flag8-epi,flag8-reuse}.log` (milliseconds):

```csv
profile,variant,global_tokens,ep_size,time_ms
default,w4a16,1,8,0.075968
default,w4a16_megamoe,1,8,0.106640
default,w4a16,8,8,0.158785
default,w4a16_megamoe,8,8,0.305458
default,w4a16,32,8,0.196226
default,w4a16_megamoe,32,8,0.401124
default,w4a16,128,8,0.235602
default,w4a16_megamoe,128,8,0.469076
default,w4a16,4096,8,0.552118
default,w4a16_megamoe,4096,8,0.715687
flag4-epi,w4a16,1,8,0.076496
flag4-epi,w4a16_megamoe,1,8,0.110176
flag4-epi,w4a16,8,8,0.149713
flag4-epi,w4a16_megamoe,8,8,0.226114
flag4-epi,w4a16,32,8,0.205713
flag4-epi,w4a16_megamoe,32,8,0.298051
flag4-epi,w4a16,128,8,0.233314
flag4-epi,w4a16_megamoe,128,8,0.346707
flag4-epi,w4a16,4096,8,0.555861
flag4-epi,w4a16_megamoe,4096,8,0.649222
flag4-reuse,w4a16,1,8,0.072976
flag4-reuse,w4a16_megamoe,1,8,0.123665
flag4-reuse,w4a16,8,8,0.151089
flag4-reuse,w4a16_megamoe,8,8,0.232690
flag4-reuse,w4a16,32,8,0.199074
flag4-reuse,w4a16_megamoe,32,8,0.316194
flag4-reuse,w4a16,128,8,0.232658
flag4-reuse,w4a16_megamoe,128,8,0.370691
flag4-reuse,w4a16,4096,8,0.552434
flag4-reuse,w4a16_megamoe,4096,8,0.672419
flag8-epi,w4a16,1,8,0.096496
flag8-epi,w4a16_megamoe,1,8,0.117216
flag8-epi,w4a16,8,8,0.159618
flag8-epi,w4a16_megamoe,8,8,0.227074
flag8-epi,w4a16,32,8,0.199121
flag8-epi,w4a16_megamoe,32,8,0.297889
flag8-epi,w4a16,128,8,0.216770
flag8-epi,w4a16_megamoe,128,8,0.345442
flag8-epi,w4a16,4096,8,0.552679
flag8-epi,w4a16_megamoe,4096,8,0.674884
flag8-reuse,w4a16,1,8,0.083761
flag8-reuse,w4a16_megamoe,1,8,0.122609
flag8-reuse,w4a16,8,8,0.160273
flag8-reuse,w4a16_megamoe,8,8,0.224450
flag8-reuse,w4a16,32,8,0.201026
flag8-reuse,w4a16_megamoe,32,8,0.314787
flag8-reuse,w4a16,128,8,0.225073
flag8-reuse,w4a16_megamoe,128,8,0.369027
flag8-reuse,w4a16,4096,8,0.544019
flag8-reuse,w4a16_megamoe,4096,8,0.701848
```

At global4096, all five runs select split M256/N128/K256 on six ranks and M256/N192/K256 on two ranks for both FC1 and FC2, with cluster `(2,1)` and `raster_along_m=True`. The smaller shapes have varying rank-level selections. Ranks 2 and 7 use N192 at 4096 in every run; the other six use N128. All 200 selection records (five shapes × eight ranks × five profiles), full input shapes and source hashes are preserved by `TMEM_REFERENCE_SWEEP_001.md`, `tmem-reference-sweep-001.comparison.json` and the run directories; the tuple's boolean is the raster flag. The earlier isolated candidate's tactic table below is separately labeled and is not substituted for these current records.

Public benchmark reproduction in the recorded profile order (local `run_reference_schedule_sweep.sh` additionally retains actual tactic selections and per-run hashes):

```bash
unset CUTE_DSL_LINEINFO CUTE_DSL_KEEP CUTE_DSL_DUMP_DIR CUTE_DSL_CACHE_DIR
unset FLASHINFER_CUTE_DSL_MOE_PROFILE_CASE
for knobs in \
  '{}' \
  '{"group_hint":512,"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","flag_batch":4,"token_back_mode":"epi_warps"}' \
  '{"group_hint":512,"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","flag_batch":4,"token_back_mode":"reuse_dispatch_warps"}' \
  '{"group_hint":512,"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","flag_batch":8,"token_back_mode":"epi_warps"}' \
  '{"group_hint":512,"epi_flag_batch":[2,4],"load_balance_mode":"atomic_counter","flag_batch":8,"token_back_mode":"reuse_dispatch_warps"}'; do
  OMP_NUM_THREADS=1 torchrun --nnodes=1 --master-addr=127.0.0.1 \
    --master-port=29541 --nproc-per-node=8 \
    benchmarks/bench_cute_dsl_moe_distributed.py \
    --num-gpus 8 --parallel-modes ep --variants w4a16,w4a16_megamoe \
    --num-tokens 1,8,32,128,4096 --warmup 3 --iters 100 \
    --timing cupti --cuda-graph --no-fused-finalize --megamoe-knobs "$knobs"
done
```

The fresh full 13-shape sweep and adjacent repeated controls remain pending.

### Isolated TMEM candidate timings before f952b398

DeepSeek-V3 H7168/I2048/E256/top-k8, EP8, **global** token counts, three warmups, 100 CUPTI iterations, cold L2 and CUDA graphs. CUPTI measures the earliest-to-latest GPU activity span, takes MAX across ranks for each iteration, then reports the median. Weight preparation, compilation, autotuning, graph capture and L2 flush are excluded. Tiny shapes include empty source ranks. Each run pairs Mega with split W4A16 over the same packed weights/routes, using `--no-fused-finalize`; the optional final-tensor `--refcheck` is omitted for the separately documented combine-rounding difference. No tolerance changed.

Raw milliseconds from `swap-tmem-fixedn-paired-002.log` and `swap-tmem-dynamicn-paired-001.log`:

| Global tokens | Fixed-run split | Fixed N128 Mega | Dynamic-run split | Dynamic-N Mega |
|---:|---:|---:|---:|---:|
| 1 | 0.068002 | 0.111233 | 0.089297 | 0.114145 |
| 8 | 0.161280 | 0.304322 | 0.161008 | 0.302516 |
| 32 | 0.203074 | 0.411557 | 0.196082 | 0.409203 |
| 128 | 0.235889 | 0.479267 | 0.233681 | 0.469539 |
| 4096 | 0.551635 | 0.724197 | 0.553395 | 0.712356 |

Dynamic-N Mega changes by −2.03% to +2.62% versus fixed N, which does not establish a material gain. The one-token split control changes from 0.068002 to 0.089297 ms (+31.32%); this is not attributed to Mega. The fixed-run recorder missed the `CuteDslRunner` wrapper and wrote empty tactic records. Only the dynamic run has actual selections, five on each of eight ranks; those are not retroactively assigned to the fixed run.

Actual dynamic-run split tactics (`(M,N,K)`; all use cluster `(2,1)` and `raster_along_m=True`). M128 uses one-CTA MMA even in a two-CTA cluster; M256 uses two-CTA MMA. The tactic's final boolean is the raster flag.

| Global tokens | FC1 tile | FC2 tile | Ranks |
|---:|---|---|---|
| 1 | `(128, 8, 256)` | `(128, 8, 256)` | 0 |
| 1 | `(128, 16, 256)` | `(128, 16, 256)` | 1, 2, 4, 5, 7 |
| 1 | `(128, 16, 256)` | `(256, 16, 256)` | 3, 6 |
| 8 | `(128, 8, 256)` | `(128, 8, 256)` | 0 |
| 8 | `(128, 16, 256)` | `(128, 16, 256)` | 1, 2, 4, 5, 7 |
| 8 | `(128, 16, 256)` | `(256, 16, 256)` | 3, 6 |
| 32 | `(128, 8, 256)` | `(128, 8, 256)` | 0, 3 |
| 32 | `(128, 16, 256)` | `(128, 16, 256)` | 1, 2, 7 |
| 32 | `(128, 16, 256)` | `(256, 16, 256)` | 4, 6 |
| 32 | `(256, 16, 256)` | `(128, 16, 256)` | 5 |
| 128 | `(128, 8, 256)` | `(128, 8, 256)` | 4, 5 |
| 128 | `(128, 16, 256)` | `(128, 16, 256)` | 0, 1, 2, 6, 7 |
| 128 | `(256, 16, 256)` | `(128, 16, 256)` | 3 |
| 4096 | `(256, 128, 256)` | `(256, 128, 256)` | 0, 1, 3, 4, 5, 6 |
| 4096 | `(256, 192, 256)` | `(256, 192, 256)` | 2, 7 |

Candidate source snapshots/hashes and complete raw artifacts are retained as `fixed_n_timed_002`, `dynamic_n_validated_001`, the two run provenance logs, and all 40 per-rank tactic records. Public promotion additionally factors the helpers into the stable backend, prepares native scales once, and restores clamp/reused-return/batching support; its timing must be measured separately.

### Fresh EP8 numerical diagnosis on the dynamic TMEM candidate

At H7168/I2048/E256/top-k8 and eight global tokens, independently decode the benchmark's exact packed weights/scales, apply FP32 globals after each GEMM, preserve BF16 FC1/FC2 boundaries, then reconstruct both combine formulas. The unchanged strict check is `abs(error) <= 0.01 + 0.01*abs(reference)`. All 458,752 Mega/split per-route BF16 FC2 values are **bitwise identical**. Mega's final all-route oracle has no mismatches.

The final formulas differ: Mega sums all FP32-weighted BF16 route results and converts once to BF16; split converts each rank's weighted partial to BF16 before the rank combine. Reconstructing the latter from either kernel's FC2 terms matches split bitwise. The three final Mega/split failures and six split/torch-oracle near-boundary failures remain disclosed; neither baseline nor tolerance is changed. This instrumented diagnostic intentionally exits after saving; all its timings are discarded.

Complete nine-metric output from `diagnostic-swap-global8/comparisons.json` (`max ratio` is error divided by the allowed error):

| Comparison | Mismatches / elements | Max abs | Max ratio | Relative L2 |
|---|---:|---:|---:|---:|
| `mega_per_route_fc2_vs_oracle` | 0 / 458752 | 0.03125 | 0.621118069 | 0.000445055859 |
| `split_per_route_fc2_vs_oracle` | 0 / 458752 | 0.03125 | 0.621118069 | 0.000445055859 |
| `mega_vs_all_route_oracle` | 0 / 57344 | 0.03125 | 0.935243249 | 0.000792496477 |
| `split_vs_rank_partial_oracle` | 6 / 57344 | 0.03125 | 1.25000012 | 0.000783864867 |
| `mega_vs_own_fc2_all_route_reduce` | 0 / 57344 | 0.0078125 | 0.384615391 | 2.20930578e-05 |
| `split_vs_own_fc2_rank_partial_reduce` | 0 / 57344 | 0 | 0 | 0 |
| `split_vs_mega_fc2_rank_partial_reduce` | 0 / 57344 | 0 | 0 | 0 |
| `mega_vs_split` | 3 / 57344 | 0.03125 | 1.14436626 | 0.00263924529 |
| `mega_per_route_fc2_vs_split` | 0 / 458752 | 0 | 0 | 0 |

`mega_per_route_fc2_vs_split` additionally reports `bitwise_mismatches=0`. Raw tensors are retained in `diagnostic-swap-global8/outputs.pt`. This is candidate evidence before promotion, not a fresh f952b398 EP8 oracle run.

### Generated-code evidence and current public profiling

The fixed-N candidate's production-shape eight-rank dumps show packed-weight conversion stores as `tcgen05.st...32x32b.x8` / `STTM.x8`, and MMA takes a bracketed 32-bit TMEM A operand (`UTCHMMA.2CTA` in SASS). Each rank reports `REG:128 STACK:112 SHARED:1024 LOCAL:0`, with 5,808 static SASS instructions. The static shared figure excludes dynamic shared storage. All observed local loads/stores map to the current FC2 router's explicit 96-byte destination-pointer/validity arrays; they are not evidence of transform register spills. These dumps belong to `swap-tmem-codegen-t4096-001`, before public promotion; fresh public PTX/SASS dumps remain pending; current public Nsight Systems resources are recorded separately below.

**Current public Nsight Systems: f952b398, EP8, global 32/4096 tokens.** Each named stage has 16 launches across eight devices (two profile iterations). The fused kernel accounts for 98.829758% / 98.554411% of the **named MoE-stage GPU time**, including routing and final reduction. This denominator excludes the harness NCCL barriers and L2 flush, which remain in the raw SQLite/report capture; it is not all captured GPU time. These are instrumented, non-graph durations and are excluded from CUPTI latency claims.

Raw stage aggregates from `tmem-public-nsys-001/*.kernels.csv`:

| Global tokens | Stage | Launches | Total ms | Average µs | Named-stage GPU time % |
|---:|---|---:|---:|---:|---:|
| 32 | routing | 16 | 0.055745 | 3.484062 | 0.535342 |
| 32 | output initialization | 16 | 0.024576 | 1.536000 | 0.236013 |
| 32 | fused MegaMoE | 16 | 10.291119 | 643.194938 | 98.829758 |
| 32 | final TopkReduce | 16 | 0.041536 | 2.596000 | 0.398887 |
| 4096 | routing | 16 | 0.064674 | 4.042125 | 0.337329 |
| 4096 | output initialization | 16 | 0.049728 | 3.108000 | 0.259373 |
| 4096 | fused MegaMoE | 16 | 18.895243 | 1180.952687 | 98.554411 |
| 4096 | final TopkReduce | 16 | 0.162752 | 10.172000 | 0.848887 |

The fused launches at both shapes report 128 registers/thread, 512 threads/block, grid `(2,1,74)`, cluster `(2,1,1)`, 161,152 bytes dynamic shared memory and `localMemoryPerThread=0`. This profiler field is distinct from the explicit FC2 local arrays identified in the earlier candidate's PTX/SASS. Raw `.nsys-rep`, SQLite files and `summary.json` preserve the full capture and resource query.

**Current NCU scope:** the four-metric memory capture completed on all eight ranks at global 32 and 4096 tokens, with one replay pass each; all 16 counter exports are below. An earlier wider stall-metric attempt failed on its second application replay during NCCL initialization with stale peer endpoints, before the kernels, and supplies no successful counter result. The fresh combined multi-pass/PC capture completed both shapes on all eight ranks with the replay-store fix committed in c7713ba1; its per-PC extraction and mechanism conclusions remain pending. Kernel replay previously failed at context save, and application mode rejects shapes with empty source ranks. No NCU duration is used as performance evidence.

Raw current NCU values from `tmem-public-ncu-memory-001` (source `f952b398`, one replay pass per rank/shape):

```csv
tokens,rank,profiler_duration_ms,shared_store_bank_conflicts,shared_store_wavefronts,lsu_instructions,tensor_elapsed_pct
32,0,58.794624,9802,32398,61570439,0.025315
32,1,32.234304,7035,27519,34262781,0.040877
32,2,0.730528,8308,28088,2310406,1.764682
32,3,60.980672,6298,23966,63515107,0.017836
32,4,4.165696,8019,24983,5516773,0.248016
32,5,0.375616,5474,22438,1672493,2.850771
32,6,28.35936,4749,21713,30297971,0.036318
32,7,9.933184,5012,22680,11553157,0.109686
4096,0,56.873952,10773,52377,61106615,0.289277
4096,1,32.69632,9723,50623,36397958,0.484222
4096,2,49.393024,6773,39929,53767620,0.310944
4096,3,15.198336,9164,48656,19245849,1.091072
4096,4,1.001152,6061,41329,4231974,15.83198
4096,5,0.679232,9120,47204,4210274,23.71268
4096,6,2.398912,7435,45519,5962250,6.379811
4096,7,26.912288,7955,41815,29993757,0.541488
```

These are complete values for the four requested metrics plus profiler duration. Bank conflicts, store wavefronts and LSU instructions are summed counters for each rank's captured fused kernel. `tensor_elapsed_pct` is `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed`; its elapsed-time denominator includes collective waiting under replay. Shared-store wavefronts measure shared-store work; this capture has no shared-load, TMA, DRAM or per-PC wait counters and cannot establish raw-fetch starvation. Whole-kernel LSU counts closely track the distorted profiler duration across ranks, so neither those durations nor elapsed tensor utilization establish production latency/throughput. The reports distinguish a 167,936 B configured shared-memory carveout from 162,176 B allocated per block (161,152 B dynamic + 1,024 B driver; static 0). Deeper raw rings may change that carveout. Raw reports, per-rank CSV exports, `csv-export-manifest.json` and `analysis.json` are retained.

Public profiling commands (Nsight Systems and the four-metric one-pass NCU capture completed):

```bash
python benchmarks/bench_cute_dsl_moe_distributed.py \
  --mode profile_nsys --num-gpus 8 --parallel-modes ep --variants w4a16_megamoe \
  --num-tokens 32,4096 --warmup 3 --iters 1 --profile-iters 2 \
  --no-fused-finalize --nsys-output-dir ./nsys-tmem

python benchmarks/bench_cute_dsl_moe_distributed.py \
  --mode profile_ncu --num-gpus 8 --parallel-modes ep --variants w4a16_megamoe \
  --num-tokens 32,4096 --warmup 3 --iters 1 --profile-iters 1 --no-fused-finalize \
  --ncu-megamoe-replay application \
  --ncu-megamoe-kernel 'regex:.*Sm100W4A16MegaMoEKernel.*' \
  --ncu-metrics 'l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_st.sum,l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum,smsp__inst_executed_pipe_lsu.sum,sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed' \
  --ncu-output-dir ./ncu-tmem-memory
```

### Historical full 13-shape baseline: superseded SMEM compute

Source `15eb1c62`, with all 15 remote source-file hashes checked against that commit. Same EP8 workload, 100 cold-L2 CUDA-graph CUPTI iterations and split control as specified above. Raw milliseconds and recorded split/Mega speedup are preserved below; values below one mean Mega is slower. These results do not describe the TMEM implementation. The synchronized event control at global 1/8/32/4096 gave Mega 0.466128/2.544000/3.630128/4.366880 ms, within about 1% of CUPTI, confirming device work dominated that regression.

| Global tokens | Split W4A16 ms | Historical Mega ms | Split / Mega |
|---:|---:|---:|---:|
| 1 | 0.094273 | 0.462948 | 0.203636 |
| 2 | 0.115857 | 1.162075 | 0.099698 |
| 4 | 0.137282 | 1.859389 | 0.073832 |
| 8 | 0.157233 | 2.542509 | 0.061842 |
| 16 | 0.166961 | 2.635927 | 0.063341 |
| 32 | 0.201377 | 3.621276 | 0.055609 |
| 64 | 0.210754 | 4.316645 | 0.048824 |
| 128 | 0.233329 | 4.323877 | 0.053963 |
| 256 | 0.245202 | 4.328396 | 0.056650 |
| 512 | 0.238049 | 4.332558 | 0.054944 |
| 1024 | 0.261970 | 4.334587 | 0.060437 |
| 2048 | 0.351603 | 4.344968 | 0.080922 |
| 4096 | 0.554579 | 4.357703 | 0.127264 |

### Historical controlled vector-store experiment: superseded by TMEM

At `12b62378`, vector stores replaced scalar decoded BF16 shared stores with no arithmetic, warp/stage or pipeline-arrival change. In the adjacent scalar/vector CUPTI controls below, only that kernel store implementation changed. The paired split control varied by at most 1.4%; Mega improved 1.44–1.58×. This mechanism is historical: the current kernel stores decoded weights directly to TMEM.

| Global tokens | Scalar-run split | Scalar Mega | Vector-run split | Vector Mega |
|---:|---:|---:|---:|---:|
| 1 | 0.083280 | 0.471698 | 0.082128 | 0.328674 |
| 8 | 0.160593 | 2.542316 | 0.161393 | 1.657264 |
| 32 | 0.201761 | 3.620528 | 0.199138 | 2.315403 |
| 128 | 0.231745 | 4.321249 | 0.234401 | 2.743250 |
| 4096 | 0.550886 | 4.364761 | 0.551508 | 2.783182 |

Matched EP8 global32 TCP/application NCU replay collected one pass per rank. Raw shared-store counters:

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

Summed bank conflicts fell 68.508× and store wavefronts 7.626×. Static SASS changed from 5,305 to 4,581 instructions; 32 `STS.U16` producer sites became four `STS.128` sites. Registers stayed 115 with no `LDL`/`STL`. NCU durations were distorted by collective replay/waiting and are not latency evidence. These historical store counters are not attributed to the new TMEM path.

## C1 catalog16 complete CUDA13.2 sweep — 195946

Run `cu132-c1-catalog16-full13-002`, now-published source1959462045f502e367055bd56ec407188dc316fd, full source_id250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b. Eight B300 on hu-pdx-88, nvcr.io/nvidia/pytorch:26.05-py3, nvcc13.2.78, DSL4.7.1 native compiler13.3, image Torch2.12.0a0+5aff3928d8.nv26.05; same stack as the6315 comparison. Global tokens, H7168/I2048/E256/top8/EP8; three warmups and100 CUPTI CUDA-graph cold-L2 samples. Fixed CONTROL is M256/N128/K256/C2/F4/epi, group512/atomic/epi flags2,4; auto searches the curated16. Both use two transform warpgroups. Split uses identical packed weights/scales/routes, independently retunes, and disables fused finalize. The known final reduction-rounding difference remains unchanged; independent numerical gates apply, not a relaxed final cross-backend tolerance.

The audit verifies52 raw rows,208 split tactics,208 compiled records,104 returned winners,13 complete online rankings, full source/helper identity and unchanged before/after manifests. All13 winners attain the minimum printed online host score. Those host scores are not the final CUPTI spans. Sources and original evidence: [comparison.json](logs/cu132-c1-catalog16-full13-002-analysis/comparison.json), [raw-latencies.csv](logs/cu132-c1-catalog16-full13-002-analysis/raw-latencies.csv).

Same-source fixed CONTROL then auto16. Negative Mega change means auto is faster. Split retunes separately in each process; its change is contextual, not an error bar.

| Global tokens | Fixed split ms | Fixed Mega ms | Auto split ms | Auto Mega ms | Mega change | Split change | Changed split ranks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.071824 | 0.106224 | 0.076320 | 0.078849 | -25.77% | +6.26% | [0, 4, 6] |
| 2 | 0.091473 | 0.121569 | 0.116817 | 0.111169 | -8.55% | +27.71% | [0, 4, 6] |
| 4 | 0.145280 | 0.135649 | 0.127905 | 0.117873 | -13.10% | -11.96% | [0, 4, 6] |
| 8 | 0.154562 | 0.154481 | 0.162465 | 0.156593 | +1.37% | +5.11% | [0, 4, 6] |
| 16 | 0.169569 | 0.176593 | 0.178929 | 0.168001 | -4.87% | +5.52% | [] |
| 32 | 0.201345 | 0.210290 | 0.204545 | 0.208241 | -0.97% | +1.59% | [0, 1, 3, 6, 7] |
| 64 | 0.218258 | 0.242753 | 0.218737 | 0.226865 | -6.54% | +0.22% | [4, 6] |
| 128 | 0.233746 | 0.239921 | 0.233841 | 0.223873 | -6.69% | +0.04% | [1, 3, 6] |
| 256 | 0.245858 | 0.247745 | 0.242785 | 0.230241 | -7.07% | -1.25% | [5] |
| 512 | 0.239746 | 0.252577 | 0.239474 | 0.234833 | -7.03% | -0.11% | [0, 1, 2, 4, 5, 7] |
| 1024 | 0.264641 | 0.271026 | 0.260801 | 0.248578 | -8.28% | -1.45% | [1] |
| 2048 | 0.352131 | 0.345426 | 0.350498 | 0.334978 | -3.02% | -0.46% | [0] |
| 4096 | 0.555011 | 0.513715 | 0.562021 | 0.501842 | -2.31% | +1.26% | [] |

Complete auto16 sweep: unchanged 100-iteration CUPTI benchmark, global tokens, EP8. Each row reports its actual returned winner; no minimum across runs or row substitution.

| Global tokens | Split W4A16 ms | Mega W4A16 ms | Split / Mega | Actual choice |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.076320 | 0.078849 | 0.968x | M256/N64, C2, F8, epi |
| 2 | 0.116817 | 0.111169 | 1.051x | M256/N64, C2, F4, epi |
| 4 | 0.127905 | 0.117873 | 1.085x | M128/N64, C1, F4, reuse |
| 8 | 0.162465 | 0.156593 | 1.037x | M128/N64, C1, F8, reuse |
| 16 | 0.178929 | 0.168001 | 1.065x | M256/N64, C2, F8, reuse |
| 32 | 0.204545 | 0.208241 | 0.982x | M128/N64, C1, F4, epi |
| 64 | 0.218737 | 0.226865 | 0.964x | M128/N64, C1, F8, epi |
| 128 | 0.233841 | 0.223873 | 1.045x | M256/N64, C2, F4, epi |
| 256 | 0.242785 | 0.230241 | 1.054x | M256/N64, C2, F8, epi |
| 512 | 0.239474 | 0.234833 | 1.020x | M256/N64, C2, F8, epi |
| 1024 | 0.260801 | 0.248578 | 1.049x | M256/N64, C2, F4, epi |
| 2048 | 0.350498 | 0.334978 | 1.046x | M256/N128, C2, F4, reuse |
| 4096 | 0.562021 | 0.501842 | 1.120x | M256/N128, C2, F4, reuse |

Auto improves12/13 versus same-source fixed; T8 regresses1.37%. The published whole auto13 table still trails split at1/32/64. C1 wins4/8/32/64 with online host margins over best C2 of3.6/2.2/0.9/0.0us; these small margins are not stable-speedup evidence. Keep the original twelve candidates/default unchanged and retain C1 as a validated curated option, not a guaranteed improvement.

[Historical auto12 context](logs/cu132-c1-catalog16-full13-002-analysis/historical-auto12-context.md) is a different-source/catalog/time comparison: T32 Mega+8.01% with split+0.11% is a repeat hotspot; T8/T16+4.80%/+3.18%, T64/T128−5.60%/−6.15%, T4096+0.22%. Full original rows, tactic distributions, source differences and evidence hashes are retained there. No row minima replace either full table. CUDA13.0's complete6315 auto12 table remains source-specific and has not validated this extension. Detailed retention and limitations are in optimization ledger019.


### 019d. Completed halfguard v2 full13: no promotion

Full audited output: [v2 fixed/auto](logs/cu132-halfguard-v2-full13-001-analysis/fixed-versus-auto16-full13.md), [C1 comparison](logs/cu132-halfguard-v2-full13-001-analysis/C1-COMPARISON.md). Both sweeps have complete provenance and actual tactics. Fixed T4–4096 moves -3.06% to +2.12%; nine automatic choices change. No broad gain established; v2 is not promoted. The published C1 table remains unchanged.

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


### 019g. Complete v3 full13 remains experimental

[Independent C1/v2 comparison](logs/cu132-halfguard-v3-full13-001-analysis/PRIOR-COMPARISON.md) validates all source/tactic records. C1→v3 fixed T4–4096 spans-2.69% to+1.87%;4096-0.33%. Seven automatic choices change. No broad gain established; published C1 table unchanged. Exact source/runtime and split tactic deltas are retained in the accompanying JSON.

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


### 019i–019j. Scorer diagnostic and rejected scalar tail

[Paired T128 findings](logs/paired-tuner-metric-baseline128-002-analysis/FINDINGS.md) preserve all7,680 original samples and scorer/rank orders. Host/event winners agree in2/3 passes; near-tied graph margins0.288–0.608us and broader ordering differences justify the queued five-shape diagnostic, not a public timing policy.

[Scalar-tail ABA](logs/cu130-scalar-tail-aba-001/performance-audit/README.md) reconstructs all18 raw values/72split/72compiled records. Mega B is slower than both controls at allthree shapes:16.25–21.83%,51.47–52.06%,32.82–32.99%. Both split and Mega use the changed decoder; reject it. Original full13 tables remain unchanged.


### 2026-09-08 — complete replacement-node 512 and static-FC2 audits

CUDA 13.0 source e2d88 completed its actual resource probe, eight public geometry/EP suites (120 rank-level tests, 192 config/compiled pairs), two all-16 lifecycle suites, and the original fixed→auto full 13-shape benchmark. Independent audits reproduce every record; same-node C1 versus e2d88 retains 104 raw latency values, 416 split selections, 416 compiled records and 208 returned auto choices. Fixed e2d88 improves 8/13 versus C1; its complete auto arm improves 6/13 versus C1 auto. At T1/T2048/T4096, all ranks have identical e2d88 fixed/auto config, compiled resources and compiler gates despite latency differences, so these are not selected-tactic improvements. [Complete 130 comparison](logs/cu130-recovery0908b-c1-vs-zero-dest512-001-analysis/comparison.md), [independent arithmetic proof](logs/cu130-recovery0908b-c1-vs-zero-dest512-001-analysis/independent-verification-001.json).

The CUDA 13.0 replacement box then disappeared before any static-FC2 upload. Last completed e2d88 audit and idle observation was 16:01:22 UTC; repeat SSH, explicit c2/infra inventory and diagnose later found no devbox/pods. Cause is unknown, all completed evidence is local, and root held a new request until retained-source selection. The strict 28a fallback adapter passed 45 independent CPU tests and its exact four-path/native12.9 contract review but was never installed or launched. [Interruption](logs/cu130-recovery0908b-missing-before-static-001.json), [recovery plan](candidates/cuda130_recovery_0908b/NEXT_RECOVERY.md), [compiler-control proposal](candidates/cuda130_recovery_0908b/NEXT_COMPILER_CONTROL.md). No saved cache-owner JSON establishes surviving caches on a replacement node.

CUDA 13.2 static-FC2 source 28a completed both original benchmark arms. The exact original static analyzer accepts 52 raw values, 208 split selections, 208 selected compiled records, 104 returned winners and 13 complete 16-candidate rankings, with source/native/resource/cache-origin guards. All 208 selected objects report actual REG128, 512 threads, two transform groups and local_bytes=0. Original fresh C1 and base512 analyzers also pass in separate processes. All 104 fixed rank/shape configurations match across the three sources; only epilogue.py changes from e2d88 to 28a.

The [complete three-source 132 comparison](logs/cu132-static-fc2-three-source-full13-001-analysis/comparison.md) preserves all 156 raw values, 624 split selections, 624 compiled records, 312 returned winners and 39 complete rankings. Fixed 28a improves 9/13 versus e2d88 (0.30–4.60%) and 10/13 versus C1; its regressions versus e2d88 are 1.00–2.75%. Complete auto 28a improves 7/13 versus e2d88 auto and 4/13 versus C1 auto. T1 auto is 7.07% slower than e2d88 with the same selected tactic while paired split is 10.21% slower. T4096 auto is 0.526965 ms versus paired split 0.554979 ms (1.0532x), but 6.28% slower than C1 auto, which selected reused-dispatch return. Static fixed/auto at T4096 have identical config, compiled resources and gates on all ranks; their 0.94% latency movement is not a tactic change. Sequential arms, split retuning, later-process native-map coverage and unverified cross-run tensor bytes remain explicit limits; no fastest-row mixture or promotion follows from this audit.

[Independent reconstruction](logs/cu132-static-fc2-three-source-full13-001-analysis/independent-verification-001.json) passed every original stdout/rank-file/result/table comparison (SHA 191be0e49d9547f51bb6b6a3bcf79927c029faf71e8c5d58b5dd8156fb0d452b). A later prose-spacing refresh preserves every JSON data field outside interpretation/limits, every numeric Markdown row and the complete CSV; original audited versions are archived and linked by [refresh proof](logs/cu132-static-fc2-three-source-full13-001-analysis/prose-refresh-verification-002.json). No source, GPU, benchmark or PR operation was performed during this audit.


### 2026-09-08 — input-dispatch numerical gates and CUDA 13.0 recovery0908c

CUDA13.2 input-dispatch graph source21ee completed the12-stage sequence with exit0: EP2 resource probe, eight original public geometry/EP suites, all16-candidate lifecycle at EP1/EP2, and the private graph-sampler ownership/peer-error/recovery check. The [independent audit](logs/cu132-recovery0908b-input-dispatch-graph-scoring-independent-001/audit.json) retains120 public rank-tests,192 config/compiled pairs,48 lifecycle candidate records (32 nonempty oracle checks and16 empty-rank contracts),9 stable plus3 changed-input graph replays, and6 sampler rank-attempts. Every original PRELAUNCH record is hashed, parsed and reconciled:250 total, all actualREG128/512threads/two groups/65,536-register pool. Local-memory allocation is0 bytes for244 records and8 bytes for six small public M256N64/C2 objects; [exact case/config records](logs/cu132-recovery0908b-input-dispatch-graph-scoring-independent-001/nonzero-local-objects.json) preserve the boundary. This field alone does not identify a spill or source role, and these gates make no performance claim.

The replacement130 box `fi-w4a16-mega-cu130-0908c` is ready on hu-pdx-109 with explicit25.11-py3. Clean published195946 plus the frozen five-file overlay passes full source0d795 before/after setup. Image Torch/CUDA remain unchanged; actual DSL4.7.1/native12.9 fallback, isolated interpreter, native NVSHMEM3.4.5/NCCL2.28.8/cudart13.0.96 and real Python CUPTI binding pass the [fresh environment verifier](logs/cu130-recovery0908c-environment-001.json). [Completion evidence](candidates/cuda130_recovery_0908c/completion.json) links all proof. No Mega compile/test/benchmark ran during recovery. A new fresh-owner admission must precede future timing; missing C1 caches are not inferred from historical manifests.


### 2026-09-08 — user ends CUDA 13.0 branch

After successful recovery0908c setup/source/preflight verification, the user explicitly discontinued further CUDA13.0 work. No resource compile, Mega validation or full13 run occurred on this replacement. All completed artifacts are local and hash-verified. The final18:11:38UTC process snapshot found no owned setup/test/compiler workers; only `fi-w4a16-mega-cu130-0908c` in c2/infra was selected for managed release. This is a user stop, not a validation failure. The CUDA13.2 input-dispatch full13 continues separately. See the [checkpoint](candidates/cuda130_recovery_0908c/checkpoint.json) and [release log](logs/cu130-recovery0908c-user-release-001.log).
