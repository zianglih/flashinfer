# FlashInfer nightly W4A4 operation breakdown

This effort reruns the PR #4048 Nsight Systems operation-breakdown contract on
the immutable `nightly-v0.6.18-20260813` package, adds two NVFP4
quantizer-backend comparisons, and captures a DeepSeek-shaped per-token NVFP4
kernel pair with Nsight Compute's full section set.

The completed evidence set is run `20260813T2220Z`. All raw profiler files,
terminal logs, environment manifests, original heatmaps, reusable harness, and
machine-readable summaries are retained in this project. The E2E-matching
quantizer sweep and NCU capture were appended under the same run ID in their
own non-overlapping artifact directories.

## Retained devbox

- Name: `flashinfer-w4a4-ops-0813`
- Cluster / namespace: `c1 / infra`
- Hardware: one node, 8x NVIDIA B200 (183,359 MiB each)
- Host observed at launch: `B200-66`
- Image: `nvcr.io/nvidia/pytorch:26.05-py3@sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`
- CUDA / driver: CUDA 13.2, driver 580.126.09
- Source tag / commit: `nightly-v0.6.18-20260813` / `2febce559f466aa2b0adaca3f78c172c22066321`
- Installed package: `flashinfer-python==0.6.18.dev20260813`
- Installed cubins: `flashinfer-cubin==0.6.18.dev20260813`
- PyTorch: `2.12.0a0+5aff3928d8.nv26.05`
- CUTLASS DSL: `4.7.0`
- CUPTI Python/runtime wheel: `cupti-python==13.2.0`, `nvidia-cuda-cupti==13.2.86`
- Nsight Systems / Nsight Compute / nvcc: `2026.2.1.210` / `2026.1.1.0` /
  `13.2.78`
- CUPTI preflights: the initial setup check and independent checks before the
  plain, 4over6, and both quantizer runs all passed, with five positive
  device-kernel timing samples each.

Do **not** delete the devbox when the benchmark finishes. The user explicitly
asked that it remain running.

## Results

### W4A4 operation breakdown

Values are milliseconds, with each operation's percentage of its column total
in parentheses. Percentages use the unrounded reduced values. Each raw Nsight
aggregate is divided by 8 ranks x 20 captured iterations, matching the
published [PR #4048 CUDA 13.2
contract](https://github.com/flashinfer-ai/flashinfer/pull/4048#cuda-132-nsight-systems-rl-breakdown).

#### 32 global tokens

| Operation | W4A4 per-token EP8 | W4A4 per-token TP8 | W4A4 per-token 4over6 EP8 | W4A4 per-token 4over6 TP8 |
|---|---:|---:|---:|---:|
| Input communication | 0.040 (16.3%) | 0.026 (10.5%) | 0.025 (11.0%) | 0.042 (15.6%) |
| Routing | 0.003 (1.1%) | 0.003 (1.2%) | 0.003 (1.2%) | 0.003 (1.1%) |
| Input activation quantization | 0.007 (2.8%) | 0.004 (1.8%) | 0.006 (2.6%) | 0.006 (2.0%) |
| Route indices | 0.004 (1.5%) | 0.004 (1.5%) | 0.004 (1.6%) | 0.004 (1.4%) |
| Permute | - | - | - | - |
| GEMM1 | 0.072 (29.6%) | 0.074 (29.5%) | 0.072 (31.7%) | 0.074 (27.3%) |
| Activation | 0.001 (0.5%) | 0.001 (0.5%) | 0.001 (0.6%) | 0.001 (0.5%) |
| Intermediate quantization | 0.009 (3.8%) | 0.036 (14.5%) | 0.008 (3.6%) | 0.036 (13.5%) |
| GEMM2 | 0.032 (13.1%) | 0.039 (15.6%) | 0.032 (14.0%) | 0.039 (14.5%) |
| Unpermute | 0.009 (3.8%) | 0.018 (7.3%) | 0.009 (4.0%) | 0.018 (6.8%) |
| Output communication | 0.067 (27.4%) | 0.044 (17.6%) | 0.068 (29.6%) | 0.047 (17.4%) |
| **Total staged GPU kernel time** | **0.244 (100.0%)** | **0.249 (100.0%)** | **0.228 (100.0%)** | **0.270 (100.0%)** |

#### 4096 global tokens

| Operation | W4A4 per-token EP8 | W4A4 per-token TP8 | W4A4 per-token 4over6 EP8 | W4A4 per-token 4over6 TP8 |
|---|---:|---:|---:|---:|
| Input communication | 0.072 (15.7%) | 0.138 (16.9%) | 0.073 (15.3%) | 0.138 (16.5%) |
| Routing | 0.003 (0.7%) | 0.008 (1.0%) | 0.003 (0.7%) | 0.008 (1.0%) |
| Input activation quantization | 0.022 (4.9%) | 0.019 (2.4%) | 0.024 (5.0%) | 0.032 (3.9%) |
| Route indices | 0.007 (1.6%) | 0.009 (1.1%) | 0.007 (1.6%) | 0.009 (1.0%) |
| Permute | - | - | - | - |
| GEMM1 | 0.109 (23.7%) | 0.127 (15.5%) | 0.109 (23.1%) | 0.127 (15.2%) |
| Activation | 0.002 (0.5%) | 0.001 (0.2%) | 0.003 (0.5%) | 0.001 (0.2%) |
| Intermediate quantization | 0.060 (12.9%) | 0.070 (8.5%) | 0.063 (13.4%) | 0.075 (9.0%) |
| GEMM2 | 0.061 (13.3%) | 0.144 (17.7%) | 0.061 (13.0%) | 0.144 (17.4%) |
| Unpermute | 0.034 (7.3%) | 0.117 (14.3%) | 0.034 (7.1%) | 0.117 (14.0%) |
| Output communication | 0.089 (19.4%) | 0.183 (22.5%) | 0.096 (20.3%) | 0.181 (21.8%) |
| **Total staged GPU kernel time** | **0.461 (100.0%)** | **0.816 (100.0%)** | **0.474 (100.0%)** | **0.832 (100.0%)** |

The raw-table reducer validates all expected stages, kernel-name mappings, and
exactly 160 instances per row. These totals are diagnostic staged GPU-kernel
sums: concurrent communication is not removed, and they are not application
wall-clock spans. This is one profiler sweep, so small differences—especially
in communication—should not be treated as repeated performance claims.
`Permute = -` is intentional: W4A4 fuses gather/permute into the GEMM1 launch,
so there is no separately attributable permute kernel.

Canonical outputs:

- `results/20260813T2220Z/w4a4_operation_breakdown.md`
- `results/20260813T2220Z/w4a4_operation_breakdown.csv`
- `results/20260813T2220Z/w4a4_operation_breakdown.json`

### NVFP4 quantizer backend comparisons

Each configuration completed the same 330-shape M/K grid:

| Configuration | Backend agreement | CuTe DSL faster | Geomean CUDA/CuTe | Median CUDA/CuTe | Minimum | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| E4M3 max 256, fast 4over6 error evaluation (operation-breakdown config) | 330/330 at 100% | 330/330 | 2.37x | 2.66x | 1.01x (M=32768, K=16384) | 4.25x (M=2, K=384) |
| E4M3 max 448, exact 4over6 error evaluation (supplemental) | 330/330 at 100% | 330/330 | 2.51x | 2.83x | 1.24x (M=32768, K=128) | 3.64x (M=2, K=512) |

Speedup is CUDA median time divided by CuTe-DSL median time. Each displayed
backend time is the median of 30 CUPTI-measured iterations after five dry runs,
with cold L2 and no CUDA graph. No verification failures, CUPTI fallbacks,
errors, or missing shapes were found. Backend agreement is exact CUDA-vs-CuTe
agreement within one configuration for quantized outputs and scales; the
per-token path does not perform an independent reference or dequantization
roundtrip.

Both sweeps ran sequentially on the same B200 with the same software, shape
grid, and deterministic per-shape seed. They were not interleaved or repeated,
and individual timing samples were not retained. Cross-configuration
differences are descriptive because E4M3 max and 4over6 error evaluation both
changed; their effects cannot be separated.

Canonical outputs:

- `results/20260813T2220Z/nvfp4_quantizer_backend_comparison.md`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max256_err_fastmath_summary.md`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max256_err_fastmath_cases.csv`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max256_err_fastmath_summary.json`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max448_err_exactmath_summary.md`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max448_err_exactmath_cases.csv`
- `results/20260813T2220Z/nvfp4_quantizer_backend_e4m3max448_err_exactmath_summary.json`
- `logs/20260813T2220Z/quantizer_backend_e2e/bench_nvfp4_quantize_backend_comparison.log`
- `logs/20260813T2220Z/quantizer_backend_e2e/nvfp4_quantize_backend_comparison_swizzled_128x4_bfloat16_per_token_4over6_mse_e4m3_256_err_fastmath.png`
- `logs/20260813T2220Z/quantizer_backend/bench_nvfp4_quantize_backend_comparison.log`
- `logs/20260813T2220Z/quantizer_backend/nvfp4_quantize_backend_comparison_swizzled_128x4_bfloat16_per_token_4over6_mse_e4m3_448_err_exactmath.png`

### Nsight Compute NVFP4 quantization profile

The NCU target uses an activation-only BF16 tensor shaped
`[tokens, hidden] = [4096, 7168]`. Per-token scaling reduces axis 1 across all
7168 hidden values and returns exactly 4096 per-token scales. It uses the
linear scale layout from the distributed DeepSeek MoE activation path, not the
standalone heatmap benchmark's swizzled layout.

One CuTe-DSL action and one CUDA action were captured in one report using
`--set=full` and kernel replay. Each action has 2,461 collected metrics. Source
import succeeded: the report embeds all three referenced CuTe sources and all
29 referenced CUDA/header sources. NCU could not access six CTC fabric metrics;
that limitation is preserved in the raw profiler log.

Canonical outputs:

- `results/20260813T2220Z/nvfp4_quant_ncu_m4096_k7168.md`
- `logs/20260813T2220Z/ncu_nvfp4_quant_m4096_k7168/nvfp4_quant_m4096_k7168_cute_dsl_and_cuda_full.ncu-rep`
- `logs/20260813T2220Z/ncu_nvfp4_quant_m4096_k7168/report_summary.json`
- `logs/20260813T2220Z/ncu_nvfp4_quant_m4096_k7168/{details,raw,source}.csv`

The report is 53,693,980 bytes with SHA-256
`292e3e9b5a274ea04f9ce3d603dc99421a85012b62d5293f0359ed08a8000bed`.

## Workloads

### W4A4 per-token operation breakdown

Both cases use real EP8 and TP8 communication, deterministic finalize, PDL,
8 ranks, 10 warmups, 20 captured iterations, and 32 / 4096 global tokens.
`FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1` is retained in both cases.

- Plain per-token removes all four `FLASHINFER_NVFP4_4OVER6*` variables.
- Per-token 4over6 uses MSE, E4M3 max 256, and fast 4over6 error evaluation.

The published PR #4048 aggregation contract is preserved: each CSV contains
GPU kernel time aggregated across 8 ranks and 20 captured iterations, so each
operation is divided by `8 * 20 = 160`. These are diagnostic staged GPU-kernel
sums. Concurrent communication is not removed and the totals are not
application wall-clock spans.

On the devbox, use a fresh run ID and run both cases with:

```bash
cd /workspace/flashinfer-w4a4-nightly-20260813
harness/run_w4a4_nsys_breakdowns.sh "$PWD" <fresh-run-id>
```

After downloading, reduce the raw CSVs from the local project root with:

```bash
python3 scripts/summarize_w4a4_nsys.py \
  --plain-dir logs/<run-id>/nsys_plain \
  --four-over-six-dir logs/<run-id>/nsys_4over6 \
  --output-md results/<run-id>/w4a4_operation_breakdown.md \
  --output-csv results/<run-id>/w4a4_operation_breakdown.csv \
  --output-json results/<run-id>/w4a4_operation_breakdown.json
```

### NVFP4 quantizer backend comparison

Both sweeps compare CUDA with CuTe DSL for BF16 per-token activation
quantization in `swizzled_128x4` layout across the script's fixed 330-shape
grid. Both use MSE 4over6, disabled general quantizer fast math, cold L2, five
dry runs, and 30 CUPTI-measured iterations per backend and shape.

The operation-breakdown configuration uses E4M3 max 256 and fast 4over6 error
evaluation:

```bash
cd /workspace/flashinfer-w4a4-nightly-20260813
harness/run_nvfp4_quantizer_e2e_comparison.sh "$PWD" <fresh-run-id>
```

The supplemental configuration uses E4M3 max 448 and exact 4over6 error
evaluation:

```bash
cd /workspace/flashinfer-w4a4-nightly-20260813
harness/run_nvfp4_quantizer_comparison.sh "$PWD" <fresh-run-id>
```

The benchmark emits its full console log and one PNG heatmap. It does not emit
raw per-iteration samples, CSV, or JSON; it reduces the 30 samples to a median
inside the benchmark. `summarize_quantizer_log.py` losslessly extracts the 330
rounded per-shape rows printed by the upstream benchmark into CSV and JSON.

After downloading, reproduce the E4M3-max-448 derived files from the local
project root:

```bash
python3 scripts/summarize_quantizer_log.py \
  --log logs/<run-id>/quantizer_backend/bench_nvfp4_quantize_backend_comparison.log \
  --expected-mode 'per-token, 4over6-mse, e4m3-448, err-exactmath' \
  --output-md results/<run-id>/nvfp4_quantizer_backend_e4m3max448_err_exactmath_summary.md \
  --output-csv results/<run-id>/nvfp4_quantizer_backend_e4m3max448_err_exactmath_cases.csv \
  --output-json results/<run-id>/nvfp4_quantizer_backend_e4m3max448_err_exactmath_summary.json
```

For the E4M3-max-256 sweep, use the same command with
`quantizer_backend_e2e`, expected mode
`per-token, 4over6-mse, e4m3-256, err-fastmath`, and the matching
`e4m3max256_err_fastmath` output filenames.

### Nsight Compute harness

The standalone `bench_nvfp4_quantize_backend_comparison.py` script does not
have a native NCU mode. The reusable target and wrapper follow the existing
`profile_ncu` convention in `bench_cute_dsl_moe_distributed.py`: full sections,
kernel replay, profiler-API gating, backend-specific NVTX ranges, line
information, conditional source import, and a single report export.

On the retained devbox, use a fresh run ID:

```bash
cd /workspace/flashinfer-w4a4-nightly-20260813
bash harness/run_nvfp4_quant_ncu.sh "$PWD" <fresh-run-id>
```

The target warms and exact-checks both backends before capture, then launches
one preallocated CuTe-DSL kernel followed by one preallocated CUDA kernel.
There is no CUPTI timing call inside the NCU target. The target asserts input
shape `[4096,7168]`, hidden-axis reduction length 7168, all output shapes, and
exact backend agreement. The report validator independently asserts two
actions, action order, kernel identity, and metric presence; it records the
referenced and embedded source inventory.

## Reproduction

The nightly packages were installed from the immutable release assets. The NGC
image exports a base-image pip constraint that predates the nightly's CUDA 13
dependencies, so the install intentionally unsets it:

```bash
env -u PIP_CONSTRAINT python3 -m pip install --upgrade --no-cache-dir \
  'flashinfer-python[cu13] @ https://github.com/flashinfer-ai/flashinfer/releases/download/nightly-v0.6.18-20260813/flashinfer_python-0.6.18.dev20260813-py3-none-any.whl' \
  'flashinfer-cubin @ https://github.com/flashinfer-ai/flashinfer/releases/download/nightly-v0.6.18-20260813/flashinfer_cubin-0.6.18.dev20260813-py3-none-any.whl'

env -u PIP_CONSTRAINT python3 -m pip install \
  'cupti-python==13.2.0' 'nvidia-cuda-cupti==13.2.86'
```

The exact benchmark environment assignments and arguments are in the run
scripts under `scripts/`. The Nsight Systems and quantizer-timing scripts fail
before benchmarking unless the pinned CUPTI packages can measure a real B200
device kernel. The NCU target deliberately does not call CUPTI because NCU owns
the profiling API during capture.

## Artifact layout

```text
flashinfer-w4a4-nightly-20260813-op-breakdown/
  README.md
  flashinfer/                 # independent immutable-tag clone
  hai/                        # independent reference clone; not the CLI binary
  scripts/                    # reusable run, validation, and reduction harness
  logs/<run-id>/              # downloaded raw terminal/profiler/image evidence
  results/<run-id>/           # audited summary tables
```

All remote raw profiler/result files were downloaded without transforming
their contents and verified against remote hashes. The 114-entry top-level
manifest covers 97 run files, five setup/final provenance files, and 12
derived-result files; it passes both remotely and locally. The W4A16 controls
emitted by the canonical profiler are retained even though the requested
operation table intentionally excludes them.

The convenience bundle is `logs/20260813T2220Z-evidence.tar.gz`; its checksum
is in the adjacent `.sha256` file. It contains the original Nsight Systems and
quantizer harness plus benchmark entrypoints; it predates the NCU addition. Its
gzip stream and full tar listing were validated locally.

The NCU report, raw CSV/log sidecars, and preserved first-attempt evidence are
also bundled with the three NCU harness files and NCU result markdown in
`logs/20260813T2220Z-ncu-evidence.tar.gz`; its locally computed SHA-256 is
`400ac065b5f2cf7079db7c4c28f5ce4f93de686a66a27d2eb1f8ef82d202d4b2`.

For the Nsight runs, retain every `.nsys-rep`, exported `.sqlite`, and
`.kernels.csv` file plus both complete terminal logs. For the quantizer run,
retain the complete log and original PNG. `SHA256SUMS` is generated remotely
before downloading and verified again locally.

## Validation and status

- Both Nsight sweeps completed with all expected artifacts.
- Both quantizer comparisons completed all 330 shapes with exact CUDA-vs-CuTe
  quantized-output and scale agreement.
- The clean NCU run completed with exactly two validated actions in one report,
  exact warm-up backend agreement, hidden-axis reduction length 7168, and
  embedded source for both backends.
- Immutable nightly Python and cubin wheels are installed; `pip check` passes.
- CUDA-matched CUPTI is installed; the initial and all four run-specific
  actual-device preflights pass.
- The downloaded files reproduce both remote summary outputs byte-for-byte.
- The regenerated 114-entry remote manifest passes locally; both original PNGs
  were visually inspected and are valid RGBA images (1700 x 1478 for E4M3 max
  256 and 1710 x 1478 for E4M3 max 448).
- Devbox `flashinfer-w4a4-ops-0813` remains running on `c1 / infra` as requested.
  Managed `h list` reported `1/1 running` at `2026-08-14T01:30:35Z`.

Limitations: the operation tables are a single Nsight profiler sweep, not a
same-node repeated A/B study. The upstream quantizer benchmark retains medians,
not its 30 individual timing samples. The earlier `logs/environment.txt` was
captured before CUPTI installation; `logs/environment-final.txt` is the
authoritative post-install manifest. NCU's full set required 40 replay passes
per action and reported six inaccessible CTC fabric metrics; see `ncu.log` for
their exact names. The first combined NCU download stream reset during the
non-canonical attempt's sidecars; those files were retried and every remote
per-file hash now passes locally. The NCU convenience archive was assembled
locally from those verified files and therefore has a local, not remote,
archive-level hash.
