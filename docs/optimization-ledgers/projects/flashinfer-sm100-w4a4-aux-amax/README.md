# FlashInfer SM100 W4A4 per-token aux amax

## October 24 refresh

PR #4824 is rebased onto upstream `e7348161` at current head `1db8a750`, including the early PDL signal after the aux quantizer's amax barrier. The kernel and 64-replay graph-chain regression test are retained at the user's request. All **106 selected GPU tests** passed at this exact commit; all eight changed files pass pre-commit.

The replacement deterministic-RL campaign follows #7196 and compares upstream `e7348161` directly against final head `1db8a750` in before R1 → after R1 → after R2 → before R2 order. It reports **1.056619× overall**, **1.001647× decode** and **1.218412× prefill**, equivalent to **5.358%** overall and **17.926%** prefill latency reduction. See [all 52 medians, tactics and evidence](artifacts/pr7196-final-pdl-20261024/final-pdl/summary.md), [campaign metadata](artifacts/pr7196-final-pdl-20261024/campaign.json), and [the current PR body](PR_BODY.md). This complete campaign supersedes the earlier min512 table; no rows or ratios were combined across campaigns.

The isolated `3363d5d6` → `1db8a750` PDL experiment measured only 0.023% overall and 0.067% prefill latency reduction, inconclusive relative to unchanged-path variation. It is preserved as [separate incremental evidence](artifacts/pdl-early-signal-20261024/aux-early-pdl/summary.md), alongside its [original decision record](artifacts/pdl-early-signal-20261024/experiment.json) and [candidate patch](artifacts/pdl-early-signal-20261024/candidate.patch). The full upstream-to-final gain is not attributed to PDL alone. Original sources, scripts, prior results and [rebase notes](artifacts/rebase-20261024/REBASE_NOTES.md) remain archived.

The sections below describe the August implementation and historical measurements; they are not validation of the refreshed branch.

This workspace owns the implementation, exact numerical validation, controlled
benchmarking, profiling, and pull-request evidence for accelerating CuTe DSL
SM100-family NVFP4 W4A4 MoE per-token intermediate quantization.

## Source and environment

- Upstream base: `flashinfer-ai/flashinfer@231f70828dfe93f5bbba7f0360a64435a7a846be`
- Development branch: `perf/sm100-w4a4-aux-amax`
- Final publication head: `b6e4cdaddcfb716bf757f343c5cad5823c6dd362`
- Upstream pull request: [flashinfer-ai/flashinfer#4824](https://github.com/flashinfer-ai/flashinfer/pull/4824)
- Sealed benchmark/profile revision:
  `32f7b6d001182a0a55b453a512bf737ed93b547a`
- Reference per-token implementation: FlashInfer PR #3645
- Reference configurations and benchmark: FlashInfer PR #4048 and
  `benchmarks/bench_moe_deepseek.py`
- Container: `nvcr.io/nvidia/pytorch:26.05-py3`
- Container amd64 digest:
  `sha256:ca73b4795f0d3ae27e9cd81b1b1f1b7fc6c0a129f7d51a359d2326e95af48a3d`
- Hardware: one whole C2 B300 node (`--gpus-per-pod 8`), with the controlled
  measurements pinned to visible GPU 0

The independently cloned upstream source is under `flashinfer/`. Durable task
scripts, raw logs, environment captures, source snapshots, NCU reports, parsed
results, and PR drafts stay in this project folder rather than the upstream
repository.

## Final design and launch geometry

Each materializing GEMM1 fused-activation epilogue tile computes exact row-local
maxima after conversion to the stored FP16/BF16 intermediate and writes its own
entries in blocked-8 layout
`[permuted_m / 8, num_output_n_tiles, 8]`. Distinct epilogue tiles own distinct
`(row, output-N tile)` entries, so the producer needs no atomics or inter-CTA
synchronization. The per-token quantizer accepts this tensor through optional
`input_amax` plus an optional device-resident one-element CUDA `int32`
`input_amax_valid_rows` tail bound. Omitting `input_amax` compiles the existing
legacy full-row-scan specialization.

The GEMM has logical 2-D route-M/GEMM-N work. Its static persistent scheduler
flattens logical clusters into a 1-D work sequence; the physical launch is
`grid=(cluster_m, cluster_n, persistent_clusters)` with
`cluster=(cluster_m, cluster_n, 1)`. FC1 requires `cluster_n=1`, so `(1,1)` is
physically 1-D and `(2,1)` is physically 2-D. These x/y dimensions are
cooperating CTAs within a cluster, not expert axes.

The aux reduction uses the same maxNum, scaling, and FP4 packing operations as
the legacy consumer. Tests require bitwise equality for aux maxima, packed E2M1
values, E4M3 scale bytes, FP32 per-token scales, and final MoE outputs,
including NaN, infinity, signed-zero, subnormal, PDL, and valid-row-tail cases.

## Causal A/B contract

At the sealed benchmark/profile revision,
`FLASHINFER_CUTEDSL_MOE_PER_TOKEN_AUX_AMAX={0,1}` selects the legacy full-row
intermediate amax scan or the aux-amax consumer in the same candidate checkout.
The same-source comparison isolates the implementation switch from unrelated
source drift. The final head has no experiment gate: production selects legacy
for host-static token shapes below 4 and aux amax for shapes at or above 4.

The default benchmark matrix is intentionally larger than a one-shot before
and after run:

- Workload: DeepSeek-V3, per-token NVFP4 activations, explicit EP=8 and TP=1,
  wrapper API, CUDA graphs, CUPTI timing, cold L2, 20 dry-run iterations, and
  200 measured iterations.
- Token counts: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, and 4096.
- Configurations:
  - `inference`: fused finalize and ordinary per-token NVFP4 quantization.
  - `deterministic-rl`: `--no-fused-finalize`, 4-over-6 MSE selection, 256-way
    E4M3 selection, and deterministic no-fast-math FP4 quantization.
- Timing scopes:
  - `activation-inclusive` passes `--include-activation-quant`, so the initial
    input activation quantization and the MoE are timed.
  - `moe-only` starts from the already-quantized input. It still includes the
    targeted intermediate activation quantization between GEMM1 and GEMM2.
- Tactic policies:
  - `fixed` tunes aux-off once per configuration and byte-copies that exact
    cache to both arms. This is the primary kernel-change attribution.
  - `native` tunes aux-off and aux-on separately. This measures each
    implementation under its preferred end-to-end tactic policy.
- Repetition control: five adjacent pairs per cell. Inference pairs run
  off, TRT, on when odd and on, TRT, off when even. Deterministic-RL pairs run
  off, on when odd and on, off when even. The order alternation reduces
  monotonic clock, temperature, and system-drift bias while keeping the TRT
  reference temporally centered.

Autotuning, JIT compilation, and an explicit cache-only warmup occur in
`setup/`, before any measured repetitions, and are excluded from analysis.
Measurement commands always pass `--no-autotune`; the runner fails if a cache
changes during those runs. The activation-inclusive setup cache is reused by
the MoE-only scope because the scope switch only places initial input
quantization inside or outside the timer and does not alter MoE tactic
selection.

Every CuTe DSL invocation also emits W4A16 latency as a same-process drift
control. TRTLLM runs in its own middle process and is measured only as an
inference reference: deterministic
`--no-fused-finalize` changes CuTe DSL but not TRTLLM, so a deterministic-RL
slowdown-gap claim would not be a matched comparison.

## Final publication evidence

The final policy numbers below are a deterministic derivation from the sealed
same-source rows, not a fresh timing run of the final head. For tokens 1 and 2,
the helper substitutes the legacy row; for tokens at or above 4, it uses the
measured aux row and recomputes every paired aggregate and bootstrap interval.
Later commits change Python dispatch/cache-schema, tests, and typing; they do
not change either measured kernel specialization.

### Aggregate performance

Each aggregate spans all 13 token shapes and five adjacent A/B pairs. W4A16 is
the observed same-process off/on drift control.

| policy | config | scope | W4A4 speedup | 95% CI | latency reduction | W4A16 control |
|---|---|---|---:|---:|---:|---:|
| fixed | inference | activation-inclusive | 1.0248x | [1.0245, 1.0251] | 2.42% | 1.0004x |
| fixed | inference | moe-only | 1.0285x | [1.0283, 1.0287] | 2.77% | 1.0002x |
| fixed | deterministic-RL | activation-inclusive | 1.0240x | [1.0236, 1.0245] | 2.34% | 1.0008x |
| fixed | deterministic-RL | moe-only | 1.0265x | [1.0262, 1.0268] | 2.59% | 1.0000x |
| native | inference | activation-inclusive | 1.0250x | [1.0246, 1.0252] | 2.44% | 1.0002x |
| native | inference | moe-only | 1.0278x | [1.0270, 1.0283] | 2.70% | 1.0005x |
| native | deterministic-RL | activation-inclusive | 1.0239x | [1.0236, 1.0241] | 2.34% | 1.0063x |
| native | deterministic-RL | moe-only | 1.0278x | [1.0277, 1.0281] | 2.71% | 1.0079x |

Inference gap versus the temporally centered TRTLLM W4A4 reference:

| policy | scope | legacy slowdown | production slowdown | gap closed | fraction closed | 95% CI |
|---|---|---:|---:|---:|---:|---:|
| fixed | activation-inclusive | 7.46% | 4.86% | 2.60 pp | 34.89% | [2.57, 2.63] pp |
| fixed | moe-only | 7.28% | 4.30% | 2.97 pp | 40.87% | [2.95, 2.99] pp |
| native | activation-inclusive | 7.45% | 4.83% | 2.62 pp | 35.14% | [2.58, 2.64] pp |
| native | moe-only | 7.26% | 4.36% | 2.90 pp | 39.94% | [2.82, 2.96] pp |

### Complete per-token production results

Each cell is `speedup (latency reduction)`. The legacy rows are exactly 1.0x
by construction of the production policy.

| tokens | path | fixed inference incl. | fixed inference MoE-only | fixed deterministic-RL incl. | fixed deterministic-RL MoE-only |
|---:|---|---:|---:|---:|---:|
| 1 | legacy | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) |
| 2 | legacy | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) |
| 4 | aux | 1.0224x (+2.19%) | 1.0296x (+2.88%) | 1.0216x (+2.11%) | 1.0271x (+2.64%) |
| 8 | aux | 1.0065x (+0.65%) | 1.0132x (+1.30%) | 1.0058x (+0.57%) | 1.0078x (+0.77%) |
| 16 | aux | 0.9926x (-0.74%) | 0.9926x (-0.75%) | 0.9925x (-0.75%) | 0.9907x (-0.94%) |
| 32 | aux | 1.0023x (+0.23%) | 1.0036x (+0.36%) | 1.0009x (+0.09%) | 1.0009x (+0.09%) |
| 64 | aux | 1.0017x (+0.17%) | 1.0035x (+0.35%) | 0.9985x (-0.15%) | 0.9996x (-0.04%) |
| 128 | aux | 1.0056x (+0.55%) | 1.0066x (+0.65%) | 0.9968x (-0.32%) | 0.9965x (-0.35%) |
| 256 | aux | 1.0093x (+0.92%) | 1.0102x (+1.01%) | 1.0038x (+0.37%) | 1.0040x (+0.39%) |
| 512 | aux | 1.0223x (+2.18%) | 1.0241x (+2.36%) | 1.0158x (+1.56%) | 1.0169x (+1.66%) |
| 1024 | aux | 1.0498x (+4.74%) | 1.0563x (+5.33%) | 1.0444x (+4.25%) | 1.0435x (+4.17%) |
| 2048 | aux | 1.0792x (+7.34%) | 1.0858x (+7.90%) | 1.0828x (+7.65%) | 1.0932x (+8.52%) |
| 4096 | aux | 1.1412x (+12.37%) | 1.1572x (+13.58%) | 1.1621x (+13.95%) | 1.1808x (+15.31%) |

| tokens | path | native inference incl. | native inference MoE-only | native deterministic-RL incl. | native deterministic-RL MoE-only |
|---:|---|---:|---:|---:|---:|
| 1 | legacy | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) |
| 2 | legacy | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) | 1.0000x (+0.00%) |
| 4 | aux | 1.0222x (+2.18%) | 1.0303x (+2.94%) | 1.0255x (+2.49%) | 1.0313x (+3.03%) |
| 8 | aux | 1.0070x (+0.69%) | 1.0105x (+1.04%) | 1.0035x (+0.35%) | 1.0088x (+0.87%) |
| 16 | aux | 0.9936x (-0.65%) | 0.9935x (-0.65%) | 0.9885x (-1.16%) | 0.9910x (-0.91%) |
| 32 | aux | 1.0025x (+0.25%) | 1.0027x (+0.27%) | 1.0009x (+0.09%) | 1.0026x (+0.26%) |
| 64 | aux | 1.0027x (+0.27%) | 1.0032x (+0.31%) | 0.9976x (-0.24%) | 0.9996x (-0.04%) |
| 128 | aux | 1.0059x (+0.58%) | 1.0063x (+0.63%) | 0.9979x (-0.21%) | 0.9997x (-0.03%) |
| 256 | aux | 1.0089x (+0.89%) | 1.0101x (+1.00%) | 1.0022x (+0.22%) | 1.0023x (+0.23%) |
| 512 | aux | 1.0214x (+2.09%) | 1.0228x (+2.23%) | 1.0171x (+1.68%) | 1.0184x (+1.80%) |
| 1024 | aux | 1.0503x (+4.79%) | 1.0563x (+5.33%) | 1.0434x (+4.16%) | 1.0463x (+4.43%) |
| 2048 | aux | 1.0780x (+7.24%) | 1.0836x (+7.71%) | 1.0841x (+7.76%) | 1.0941x (+8.60%) |
| 4096 | aux | 1.1420x (+12.44%) | 1.1534x (+13.30%) | 1.1635x (+14.05%) | 1.1841x (+15.55%) |

The aux path has a small, repeatable 16-token regression: 0.74-0.94% under the
fixed policy and 0.65-1.16% under native tuning. Every aggregate retains it.
The threshold also sees the host-static tensor shape captured by a CUDA graph,
not a device-side active-token count. A caller padding logical work into a
larger static bucket therefore selects from the bucket shape. The benchmark
captured each listed token shape directly.

### Exactness, validation, and artifact identity

At final head `b6e4cdaddcfb716bf757f343c5cad5823c6dd362` on visible GPU 0:

- `tests/utils/test_nvfp4_per_token_input_amax.py`: 44 passed, 1 skipped;
- `tests/moe/test_cute_dsl_per_token_aux_amax.py`: 17 passed;
- Ruff format/check, Python byte-compilation, `git diff --check`, and
  selected-file pre-commit including mypy: green.

The exact-head rerun used warm JIT caches whose source hashes were validated.
The complete archive is retained at
`artifacts/remote-archives/final-head-b6e4cdad/final-head-b6e4cdad.tar.gz`;
its SHA-256 is
`3bc2a299cbf0156ca5c59544a4896034bc72e3d927118ab2fb95915f17d2e160`;
the archive's `SHA256SUMS` manifest SHA-256 is
`1d7b7f3729ee902d801472ebafb2b33da7c50ca13c42ad78d2287b823f43c7d6`.

Sealed benchmark and production-derivation identities:

The immutable raw archive is
`artifacts/remote-archives/full-both-20260830T131852Z-raw.tar.gz`; the published
threshold bundle is
`artifacts/derived/full-both-20260830T131852Z-production-threshold4/`.

- benchmark script:
  `795d4af322214faed5f7442894fe133083b07f9a6853f40bc283400cecd4de4c`;
- matrix runner:
  `cfb00b7bafbf8eab748cfda45bcc4aa10bc862098e705389f4224c1fe01b7433`;
- run contract:
  `0d011fd3540e2dc97b34bca3b6e5edf3ac6f7744fbc0bfd6f0b01e61893615ea`;
- source-state digest:
  `d99f84bdcccd3c6b9cc16619de2cc9dbd5364c5419707618b747877c73291e25`;
- sealed parser recorded by the run:
  `31e63f857abb48ecf94e62d0e8db22ae3036abda109126b20d27340493a92554`;
- current hardened parser:
  `34380b47a2c6695b0cfd547af044782b5ab48ba5d1c51c3b7fba4978931c4c67`;
- raw archive:
  `0daacf5dd237c202d1d9ae63add4962896f62de3bc016b7fb27a61701a45dbd2`;
- raw `SHA256SUMS` (730 verified entries):
  `385fec39707c0b5791773222ca1dcf4d436f23bde18ababa8a51123790b0dc9d`;
- parsed `process-medians.csv`:
  `9fab11bd36868c417b20b1894e20785f04911b361dbf8f07f4e8b9097d974c29`;
- production helper:
  `fd6098bb8576d32ff2360c54b3157d4a09351b5b59f46065bb9845f2abbe893b`;
- production aggregate/TRT/per-token CSVs:
  `83425e01f55fe47a06857af54658b91a89fea8b82e845c2f25dd5fb2db646d9a`,
  `9f7b3e7da4b285956be076d913406a6ab3cabbd6816afcfa8c193ba2e41fe715`,
  and `3b49ea255cb524af2e80d19088d84957eb21148024b37a7b460e24eebd076413`;
- production output `SHA256SUMS`:
  `297941867600ef8c3a88519a407ca51f7074fd54f9d566db122f004e05dbaf85`.

The production helper revalidates the raw archive and all 2,340 process keys,
reproduces the sealed 104 W4A4, 104 W4A16, 8 aggregate, and 56 TRT rows, then
applies the threshold.

### Nsight Compute mechanism evidence

At the 4096-token MoE-only point, paired `--set full` reports show:

| config | GEMM1 delta | quant speedup | serialized GEMM1 + quant speedup |
|---|---:|---:|---:|
| inference | +0.384 us (+0.27%) | 3.9467x (74.66% lower) | 1.3820x (27.64% lower) |
| deterministic-RL | -3.872 us (-2.72%) | 7.4604x (86.60% lower) | 2.1442x (53.36% lower) |

Aux-on GEMM1 reported 24,576 local-spill load instructions, no local-spill
stores, and 24 KiB of local-load traffic in each profile. The quant kernels and
aux-off GEMM1 reported none. The serialized sum is an isolated mechanism
diagnostic, not an end-to-end CUDA-graph critical-path claim. Complete NCU
raw/derived evidence is retained under
`artifacts/remote-archives/ncu-blocked8-head-20260830T122522Z/`; archive
SHA-256:
`ec448e62985194a2ca6d07fae33d6cbec9316e6305ae72691262ee2f356d9fd2`.

## Running on the C2 devbox

Copy this project’s `scripts/` directory to the devbox alongside the candidate
checkout, then run from a stable shell. The raw output directory must be new and
empty.

```bash
run_id=$(date -u +%Y%m%dT%H%M%SZ)
/workspace/flashinfer-aux-harness/scripts/run_benchmark_matrix.sh \
  /workspace/flashinfer-head-git \
  "$(command -v python3)" \
  "/workspace/flashinfer-aux-artifacts/raw/bench-${run_id}"
```

To start the causal primary first and defer the more expensive independent
native tuning, use a separate raw directory:

```bash
run_id=$(date -u +%Y%m%dT%H%M%SZ)
BENCH_POLICIES=fixed \
  /workspace/flashinfer-aux-harness/scripts/run_benchmark_matrix.sh \
  /workspace/flashinfer-head-git \
  "$(command -v python3)" \
  "/workspace/flashinfer-aux-artifacts/raw/fixed-primary-${run_id}"
```

Run the same command later with `BENCH_POLICIES=native` and a new
`native-primary-${run_id}` directory. Each directory is independently strict
and parseable; never append a second policy run to an existing raw directory.

The runner first fails closed unless:

- the supplied candidate repository and every initialized submodule have clean
  worktrees at their recorded commits;
- `flashinfer` imports from the supplied candidate checkout;
- the CUDA device and package versions can be captured;
- `cupti-python` is at least major version 13; and
- a real CUPTI-timed CUDA-graph functional check completes without the timing helper
  falling back to CUDA events.

It records the GPU/driver/toolchain, installed packages and `pip check`, exact
import resolution, all controlled environment values, command lines, source
revision/status/diff/file hashes, submodule revisions, autotuner cache hashes,
per-process start/end time and exit status, stdout, stderr, and a final SHA-256
manifest. The ignored `flashinfer/data/{include,csrc,cccl,cutlass,spdlog}`
package-data symlinks are required to resolve into the supplied worktree,
recorded explicitly, and included in the immutable source-state check; this
prevents an editable import from silently compiling JIT sources from another
checkout. Candidate source, package-data-link, or cache mutation aborts the
run. CuTe DSL JIT objects use separate off/on/TRT runtime roots outside the
checksummed raw directory; their exact location is still recorded in
`run-contract.json`.

After copying the complete raw directory back to this project, validate and
parse it without changing it:

```bash
python3 scripts/parse_benchmarks.py \
  artifacts/raw/bench-YYYYmmddTHHMMSSZ \
  artifacts/derived/bench-YYYYmmddTHHMMSSZ
```

The parser verifies the checksum manifest, successful completion, exact process
cardinality and A/B order, exact backend/token row cardinality, source and cache
hashes, fixed-cache identity, cache immutability, run configuration, and every
exit code. It then writes:

- `process-medians.csv`: every benchmark-returned process median and TFLOPS row
  with its pair and arm;
- `w4a4-paired.csv`: per-token paired geometric speedups and 95% intervals;
- `aggregate.csv`: token-range W4A4 gain and W4A16 drift control;
- `w4a16-drift-control.csv`: per-token control-arm results;
- `trtllm-inference-gap.csv`: inference-only slowdown before/after, percentage
  points closed, and the common middle reference; and
- `summary.md`, `summary.json`, and `validation.json`.

Speedups are geometric means of adjacent-pair log latency ratios, not ratios of
independently pooled medians. Confidence intervals use a deterministic paired
bootstrap over repetitions with 10,000 draws and seed 42; the token-range
aggregate resamples whole repetitions so all token counts from one A/B pair
stay together.

## Capturing and parsing paired NCU reports

The durable NCU runner captures the current candidate source at the fixed
4096-token, EP8/TP1, per-token W4A4 MoE-only point. By default it produces four
reports: inference and deterministic RL, each with aux amax off and on. Prepare
a cache directory containing byte-identical off/on copies for each selected
configuration:

```text
fixed-caches/
├── inference-off.json
├── inference-on.json
├── deterministic-rl-off.json
└── deterministic-rl-on.json
```

Then run from the project root on the C2 B300 devbox:

```bash
run_id=ncu-packed-$(date -u +%Y%m%dT%H%M%SZ)
scripts/run_ncu_aux_amax.sh \
  /workspace/flashinfer-git \
  "$(command -v python3)" \
  /workspace/w4a4-aux-artifacts/fixed-caches \
  "/workspace/w4a4-aux-artifacts/raw/$run_id" \
  "/workspace/w4a4-aux-artifacts/runtime/$run_id"
```

To resume with only the deterministic-RL pair in a new output and runtime
directory, select that configuration explicitly:

```bash
run_id=ncu-deterministic-rl-$(date -u +%Y%m%dT%H%M%SZ)
NCU_CONFIGS=deterministic-rl scripts/run_ncu_aux_amax.sh \
  /workspace/flashinfer-git \
  "$(command -v python3)" \
  /workspace/w4a4-aux-artifacts/fixed-caches \
  "/workspace/w4a4-aux-artifacts/raw/$run_id" \
  "/workspace/w4a4-aux-artifacts/runtime/$run_id"
```

`NCU_CONFIGS` accepts a comma-separated subset of
`inference,deterministic-rl`; its default is both in that order. Both output
paths must be empty. The runner copies and hashes only the selected fixed
autotune cache pairs, requires off/on identity within each configuration, and
checks both the inputs and copies for mutation throughout the run. Each report
gets a fresh configuration-and-arm JIT root, an unprofiled prewarm, and one
CUDA-profiler-ranged forward under filtered NCU `--set full` kernel replay with
all-cache flushing, base-clock control, per-kernel summaries, and node-level
graph intent recorded explicitly. The
target uses `--no-cuda-graph --no-cupti --profile-cuda --profile-backend
cute-dsl --profile-iters 1`; initial activation quantization is deliberately
excluded. The deterministic-RL arms additionally use deterministic two-stage
finalize and the recorded 4-over-6/MSE quantization environment.

Raw reports and CSV exports are written under
`reports/<selected-config>/{off,on}/`. Both details and raw exports explicitly
use NCU base units so
values such as byte counts remain numeric and parser-stable rather than being
auto-scaled. Source state, environment and command files, subprocess exit
codes, cache and JIT manifests, per-file hashes, and a top-level `SHA256SUMS`
are retained with them. The combined function-name filter keeps GEMM1 and
per-token quant in the same report. After each off/on pair, the runner invokes
the strict parser below; a missing or ambiguous action fails the capture
instead of falling back to action order.

To parse an already exported off/on pair independently, run:

```bash
python3 scripts/parse_ncu_aux_amax.py \
  artifacts/raw/ncu-run/off \
  artifacts/raw/ncu-run/on \
  artifacts/derived/ncu-run
```

The parser requires exactly one GEMM1 fused-activation action and exactly one
per-token NVFP4 quant action in each arm. It matches the full kernel name,
cross-checks the selected action identity and primary metrics between the two
CSV exports, and fails on missing or ambiguous captures. Optional
`--gemm1-regex` and `--quant-regex` arguments support deliberate future kernel
renames without falling back to action order or a guessed ID.

Outputs are `summary.json`, `actions.csv`, and `summary.md`. They retain full
kernel names and report duration, executed instructions, registers per thread,
local spilling, and L1TEX global load/store sectors. Global byte values are
explicitly derived as 32 bytes per L1TEX sector; they are not logical payload
bytes or DRAM traffic. Derived timing reports GEMM1 producer overhead, quant
speedup, and the serialized GEMM1-plus-quant net gain. That serialized sum is a
mechanism diagnostic, not an end-to-end CUDA-graph critical-path claim.
Because the off and on specializations currently have identical NCU symbols,
their `legacy` and `input_amax` labels come from the positional input-directory
contract; preserve the experiment environment with each raw report.

## Development-only reductions

The following environment overrides make reduced or profiler-preparation runs
smaller. Any override is written into `run-contract.json`; reduced runs are not
PR performance evidence. The final evidence uses every default above.

```bash
BENCH_POLICIES=fixed                 # fixed, native, or fixed,native
BENCH_CONFIGS=inference             # inference and/or deterministic-rl
BENCH_SCOPES=moe-only               # activation-inclusive and/or moe-only
BENCH_TOKENS=128,1024
BENCH_REPETITIONS=1                 # final evidence requires 5
BENCH_WARMUP=2                      # final evidence requires 20
BENCH_ITERS=10                      # final evidence requires 200
BENCH_BOOTSTRAP_RESAMPLES=1000      # final analysis default is 10000
BENCH_CUDA_VISIBLE_DEVICES=0
BENCH_EP=1 BENCH_TP=8               # optional TP-sensitivity run; primary is EP8/TP1
BENCH_CUTE_DSL_ARCH=sm103a          # optional; unset uses native CC detection
BENCH_RUNTIME_DIR=/workspace/runtime/aux-amax-reduced
BENCH_W4A16_DRIFT_REVIEW_PCT=2.0
```

`BENCH_W4A16_DRIFT_REVIEW_PCT` only marks aggregate controls for review; it does
not discard measurements or turn performance noise into a raw-validation
failure.

The C2 B300 node is CC 10.3, so the primary run leaves `BENCH_CUTE_DSL_ARCH`
unset and records native `sm103a` detection. Do not force `sm100a` on this node.
An optional EP1/TP8 run can test TP sensitivity, but it is reported separately
from the EP8/TP1 primary result. A clean-base checkout at the recorded upstream
commit can also be run once as a supporting regression guard against
candidate-gate-off; it is not mixed into the same-source causal A/B statistics.

## Numerical validation boundary

Performance measurements never substitute for correctness. Acceptance requires
exact equality for the emitted per-epilogue-tile row maxima, packed FP4 values,
encoded scale-factor bytes, per-token scales, and deterministic end-to-end MoE
output across the tested tactics, layouts, dtypes, PDL modes, and deterministic
quantization settings. Numerical tolerances must not be relaxed.
