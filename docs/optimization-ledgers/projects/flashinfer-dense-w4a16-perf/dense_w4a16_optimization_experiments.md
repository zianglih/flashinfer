# Dense CuTe DSL W4A16 optimization experiment ledger

Last updated: 2026-08-22

Scope: FlashInfer upstream `fb28d7242b3506a2348265962041acc1fb56cca4`,
SM100/SM103 dense `mm_bf16_fp4`.

Published as upstream PR #4686 at
https://github.com/flashinfer-ai/flashinfer/pull/4686, head
`693d10862df7a793f7dd9d500ddece28d536d9a0`.

## Invariants inherited from the retained MoE design

Current upstream dense already has the two requested architectural properties:

- E2M1 weights and E4M3 block scales are decoded to BF16 operands; the
  tensor-wide FP32 weight scale is multiplied into the FP32 accumulator in the
  epilogue before BF16 conversion.
- The 512-thread CTA uses four 176-register epilogue warps, four uniform
  80-register control warps, and two four-warp transform groups retaining the
  128-register launch allocation. This exactly consumes 65,536 CTA registers.
- The two transform groups own contiguous complete NVFP4 blocks and disjoint
  TMEM columns, with the required `tcgen05.st` fence before pipeline commit.
- The stage fitter matches the retained static MoE GEMM policy: two narrow or
  one wide accumulator stages, at least two load/transform stages, three static
  tile-info stages, and shared-memory-derived load/output depth.

Do not reimplement or retune these contracts without profiler evidence.

## Benchmark contract

- Prepare weights and allocate `out` outside the timed closure.
- Use one CUPTI timing call per process because `cupti.finalize()` is
  process-global teardown.
- Record the canonical tactic tuple, not only its list index.
- Keep experimental tactics out of autotuning. The harness admits one only
  behind `--allow-experimental-tactic`, after the kernel's `can_implement`
  check, and records it as outside the production search space.
- The numerical oracle must preserve the kernel's scale order:
  `FP32 MMA accumulator -> FP32 alpha multiply -> BF16 conversion`.
- Primary arm: CUDA graph plus PDL and cold L2. Fixed-tactic screening used 10
  warmups and 100 CUPTI samples; the full production-autotune gate used 5
  warmups and 30 samples after each fresh tuning process.
- Compare same-node adjacent A/B/A with a fixed tactic. Treat sub-1% movement as
  noise unless it repeats and has a mechanism-specific profile.
- Primary PR #4466 shapes:
  - `(N, K) = (6656, 19968)` and `(19968, 6656)`
  - `M = 1, 8, 32, 128, 512, 1024, 2048, 4096`

## Baseline

### O2 upstream, M128/N6656/K19968, graph + PDL

- Tactic: `((256, 64, 256), (2, 1), True)`
- Timing: `0.064320 ms` median, `0.000577 ms` standard deviation, 100 CUPTI
  samples with cold L2
- Throughput: `528.983 TFLOP/s`, `1.268 TB/s`
- Reference check: passed
- Node: first `infra` earth-queue B200 pod; this node was later reclaimed

This establishes harness/kernel bring-up, but a replacement-node baseline must
be collected before accepting any candidate.

For this fixed tactic, the current fitter derives five load-to-transform
stages, three transform-to-MMA stages, two accumulator stages, five output
stages, and three tile-info stages. Accumulators occupy 128 TMEM columns and
transformed weights 384 columns; the allocation rounds to all 512 columns.
Consequently, reducing the accumulator ring to one does not buy another
transformed-weight stage. Starting deterministic output at one stage did fit a
sixth input-load stage, but its measured effect was neutral and the production
seed of two was restored.

### Invalid O3 attempt

Discarded. The first source patch accidentally changed an SM12x compile site,
not the SM100 compile site. The source sync also removed generated build-version
metadata, causing the autotune cache to be rejected and the fallback tactic to
run. Its timing is not a candidate result.

### Explicit SM100/SM103 CuTe optimizer level 3

**Result: Retained.** Dense explicitly overrode CuTe DSL's optimizer to O2;
the retained source changes only the exact SM100/SM103 compile call to O3.
Every worker used the fixed canonical tactic, CUDA graph plus PDL, cold L2, 10
warmups, 100 CUPTI samples, a fresh process, and the same eight-GPU B300/SM103
inventory.

The three-repeat M128/N6656/K19968 sentinel measured median-of-repeat medians
of `60.688 us` and `60.657 us` for adjacent O2 baselines versus `55.233 us`
for O3: `1.0985x`, with `0.9995x` A-to-A drift.

A wider adjacent A/B/A gate covered M 1/128/1024/4096 in both PR #4466
projection directions. Speedups were:

| Projection `(N,K)` | M=1 | M=128 | M=1024 | M=4096 |
|:--|--:|--:|--:|--:|
| `(6656,19968)` | 1.1025x | 1.0939x | 1.1132x | 1.1014x |
| `(19968,6656)` | 1.0247x | 1.0256x | 1.1017x | 1.0808x |

The eight-row geomean was `1.0800x`; every row improved and baseline drift was
bounded to `0.9984x`--`1.0016x`. Correctness, eager repeatability, CUDA-graph
replay repeatability, and graph-versus-eager bitwise checks passed in every
worker.

### Production autotuning and full raster axis

**Result: Retained.** Raster direction is shape-dependent, so the final source
enumerates both M-major and N-major forms of every valid structural tactic.
This is a clean Cartesian product: 15 structural tactics become 30. The
non-autotuned fallback remains the first M-major tactic. Existing persisted
15-tactic selections remain launchable but need to be re-primed to search the
new N-major variants; all retained measurements use fresh per-shape caches.

A narrower 16-tactic screen first proved that hard-coding N-major would be
wrong: for `((256,128,256),(2,1))`, production autotuning kept M-major at
public M=128 but selected N-major at M=512 and M=1024. Fixed-tactic A/B/A
measured N-major gains of `1.0175x` at both M=512 and M=1024 for the full up
projection. The full Cartesian sweep then found additional N-major winners,
including `((256,192,256),(2,1))` at up-projection M=2048 and M=4096.

The benchmarked exact-source A/B/A gate at `100e9527` compared upstream O2
with the 15-tactic space, the candidate O3 with the 30-tactic space, and
upstream O2 again. The
closing upstream arm was collected after the final Cartesian candidate so the
table is genuinely bracketed; its retained artifact label is
`a3-upstream-o2`. Each leg used fresh production autotuning, CUDA graph plus
PDL, cold L2, five warmups, 30 CUPTI samples, and all 16 PR #4466 workloads on
the same B300/SM103 GPU:

| Projection `(N,K)` | M | O2 A1 (us) | O3 + raster axis (us) | O2 A2 (us) | Speedup |
|:--|--:|--:|--:|--:|--:|
| down `(6656,19968)` | 1 | 57.441 | 54.176 | 57.409 | 1.059962x |
| down `(6656,19968)` | 8 | 57.313 | 54.145 | 57.361 | 1.058944x |
| down `(6656,19968)` | 32 | 57.840 | 54.497 | 57.761 | 1.060623x |
| down `(6656,19968)` | 128 | 58.353 | 55.089 | 58.305 | 1.058814x |
| down `(6656,19968)` | 512 | 120.001 | 117.489 | 120.049 | 1.021585x |
| down `(6656,19968)` | 1024 | 178.994 | 174.754 | 178.866 | 1.023894x |
| down `(6656,19968)` | 2048 | 290.643 | 289.411 | 290.339 | 1.003731x |
| down `(6656,19968)` | 4096 | 589.478 | 586.886 | 589.590 | 1.004513x |
| up `(19968,6656)` | 1 | 40.577 | 39.232 | 40.369 | 1.031620x |
| up `(19968,6656)` | 8 | 40.560 | 38.977 | 40.544 | 1.040422x |
| up `(19968,6656)` | 32 | 40.737 | 39.393 | 40.608 | 1.032493x |
| up `(19968,6656)` | 128 | 45.601 | 45.792 | 45.697 | 0.996866x |
| up `(19968,6656)` | 512 | 104.769 | 103.473 | 104.641 | 1.011906x |
| up `(19968,6656)` | 1024 | 182.130 | 175.714 | 178.738 | 1.026859x |
| up `(19968,6656)` | 2048 | 305.635 | 298.787 | 305.587 | 1.022839x |
| up `(19968,6656)` | 4096 | 614.486 | 599.638 | 613.894 | 1.024268x |

The 16-row geomean is `1.029759x`. The only slower row is
`0.996866x` (a 0.31% movement, below the 1% noise threshold). A2/A1 baseline
ratios are `0.981376x`--`1.002105x`: the up-projection M=1024 outlier reflects
an upstream autotuner switch from N128 to N192, and the candidate remained
faster than both arms (`1.0365x` and `1.0172x`). The other 15 baseline pairs
stayed within 0.52%. Every candidate worker passed the
FP32-accumulator/FP32-alpha reference, finite-output, eager repeatability,
graph replay, and graph-versus-eager bitwise gates.

The broader search is deliberately a first-use cost. Summed production
autotuner profile time rose from `196.68 s` for the screened 16-tactic space to
`417.83 s` for the 30-tactic Cartesian space across the 16 workloads; the full
orchestrator wall time was `548.61 s`. This tradeoff was accepted to cover real
workloads with shapes beyond the benchmarked model projections.

### O3 attribution under production autotuning

The fixed-tactic `1.0800x` result is not the end-to-end production gain because
the O2 autotuner can recover part of it by selecting a different tile. A
production-selected four-row O2/O3/O2 gate measured `1.016315x` geomean:
down-projection M=128 improved `1.050380x`, down M=1024 improved `1.019052x`,
and up M=128/1024 measured `0.998767x`/`0.997945x`, both within 0.2% of
neutral. In the wider combined gate, O3 and the raster axis together deliver
`1.029759x`; do not attribute that entire number to O3 alone.

## Rejected experiments

- MoE activation `EVICT_LAST`, packed-weight `EVICT_FIRST`, and their
  combination: stable rows moved by at most about 0.6%. One apparent 1.8%
  down-M1024 result coincided with 2.6%--2.9% baseline drift and was rejected.
- Transform fragment 64 in place of production 32: regressed stable rows by
  roughly 0.8%--3.5%.
- Initial non-fused C-stage seed 2 to 1: compiled as expected and passed every
  correctness gate, but moved only `0.9965x`--`1.0025x`.
- CTA-M64 one-CTA tactics: failed the scale-TMA layout compile gate with a
  top-level SMEM-layout/CTA-V-map shape mismatch, including cluster `(2,1)`;
  they were never timed.
- Dense `alpha[0]` hoist outside the persistent loop: SASS confirmed the
  original cached scalar load sits immediately before the accumulator wait.
  A/B/A at up M=512/1024 was neutral (about `1.0000x` and `1.0009x`), so the
  source was restored.
- Remaining simple pipeline-depth changes: the selected N128 tactic already
  consumes all 512 TMEM columns with two accumulator and two transformed-weight
  stages. Accumulator 2-to-1 is the only simple way to gain a transform stage,
  and the prior MoE ledger measured that exact trade at about a 7% regression.

## Final validation

- Final source: O3 at the SM100/SM103 compile site plus the 30-tactic raster
  Cartesian product; no alpha-hoist, cache-hint, fragment, C-stage, or CTA-M64
  experiment remains.
- The final review diff is only
  `flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py`. The generic GEMM routine was
  restored to upstream because its tolerant reference check is an algebraic
  oracle, while preallocated-output behavior is already covered by the
  dedicated test. The two evidence drivers were removed by standalone commit
  `c74bdec1` and remain recoverable from benchmark commit `100e9527`.
- `test_backend_preallocated_out[cute-dsl]` plus both parameterizations of
  `test_cute_dsl_every_tactic_matches_reference`: `3 passed` in `30.90 s`.
  The every-tactic test exercised all 30 final tactics; 1,308 warnings were
  existing CuTe DSL deprecations.
- Python compilation, Ruff check/format, and `git diff --check`: passed.
- Full benchmark artifacts, logs, worker JSON, PTX, and cubins are preserved
  locally under `artifacts/` and on C2 Weka at
  `/data/home/ziangli/flashinfer-dense-w4a16-perf-artifacts`; generated input
  caches were deliberately excluded from the durable copy.

## Prior MoE experiments not to repeat blindly

- Applying the FP32 tensor-wide scale during dequantization.
- Half-block or parity-striped transform ownership.
- Mixed control-warp register targets or register rebalances away from
  176/80/128.
- Scale-only 5/6/7/8-stage rings; dense uses the merged weight/scale load ring.
- Reducing two narrow accumulator stages to one without proving a transformed
  weight stage is gained.
- K64/K128 expansion or K512.
- Broad TMA prefetch, right-sized persistent grids, cluster-N2/four-CTA
  multicast, and activation `try_acquire`; the MoE ledger already rejected
  these.
