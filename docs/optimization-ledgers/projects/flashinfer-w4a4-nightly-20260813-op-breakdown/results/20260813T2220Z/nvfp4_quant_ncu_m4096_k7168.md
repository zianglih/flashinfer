# NVFP4 per-token quantization — Nsight Compute full-metric capture

## Workload contract

| Field | Value |
|---|---|
| Input | BF16 activation only; no weights |
| Shape | `[tokens, hidden] = [4096, 7168]` |
| Per-token reduction | Axis 1, across all 7168 hidden elements in each row |
| Packed FP4 output | `[4096, 3584]` |
| Linear block scales | `[4096, 448]`, because `7168 / 16 = 448` |
| Per-token scales | `[4096]`, exactly one scale per token row |
| Scale-factor layout | `linear`, matching the distributed DeepSeek MoE activation path |
| Input generation | Deterministic seed 42, BF16 normal values divided by 10 |

The target asserts every shape above before starting NCU. It also requires
exact CuTe-DSL/CUDA agreement for the packed output, block scales, and
per-token scales during warm-up. The completed run printed
`warmup_backend_agreement=100%`.

## NVFP4 configuration

```text
FLASHINFER_NVFP4_4OVER6=1
FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE
FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
```

The 4over6 error-evaluation path uses fast math, while the general FP4
quantizer fast-math path remains disabled. The inverse global scale is
`1 / (256 * 6) = 1 / 1536`.

## Capture method

- Hardware: one NVIDIA B200 (SM100), selected from the retained 8x B200 C1
  devbox.
- Runtime: CUDA 13.2, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, FlashInfer
  `0.6.18.dev20260813`, and Nsight Compute `2026.1.1.0`.
- Repo convention: `--set=full`, kernel replay, profiling disabled at process
  start, NVTX range filtering, per-kernel summary, source import, and one report
  export, following `benchmarks/bench_cute_dsl_moe_distributed.py`.
- Target launches: one preallocated CuTe-DSL kernel and one preallocated CUDA
  kernel inside a single `cudaProfilerStart/Stop` region and one `.ncu-rep`.
- CUPTI timing is not called inside the target because NCU owns the profiling
  API. CUPTI remains installed on the devbox for the separate timing runs.
- CuTe DSL is compiled fresh with `CUTE_DSL_LINEINFO=1` and
  `FLASHINFER_CUTE_DSL_DISABLE_CACHE=1`, avoiding reuse of an older object that
  lacked line information.

One application launch per backend does not mean one physical execution under
NCU: the full set required 40 kernel-replay passes per action.

## Validated report

| Action | Backend | Collected metrics | Referenced sources | Embedded sources |
|---:|---|---:|---:|---:|
| 1 | CuTe DSL `NVFP4QuantizePerTokenKernel` | 2,461 | 3 | 3 |
| 2 | CUDA `nvfp4QuantAndPerTokenScaleKernel` | 2,461 | 29 | 29 |

The CUDA demangled specialization records BF16, linear layout value 2,
quantizer fast math disabled, and `NVFP44Over6Config<256, MSE, true>`. Embedded
CuTe sources include `nvfp4_quantize.py`, `quantization_cute_dsl_utils.py`, and
`cute_dsl/fp4_common.py`; embedded CUDA sources include `quantization.cu` and
`quantization.cuh` plus their headers.

NCU reported six inaccessible CTC fabric metrics:
`ctc__{rx,tx}_bytes_data_user.sum` and their percent-of-peak and per-second
derivatives. The command still used the repository's full section set and all
other collected metrics are retained in the report.

- Report: `logs/20260813T2220Z/ncu_nvfp4_quant_m4096_k7168/nvfp4_quant_m4096_k7168_cute_dsl_and_cuda_full.ncu-rep`
- Size: 53,693,980 bytes.
- SHA-256: `292e3e9b5a274ea04f9ce3d603dc99421a85012b62d5293f0359ed08a8000bed`.
- Machine-readable audit: `logs/20260813T2220Z/ncu_nvfp4_quant_m4096_k7168/report_summary.json`.
- Raw CSV exports: `details.csv`, `raw.csv`, and `source.csv` in the same
  directory.
- Per-directory integrity: all entries in the same directory's `SHA256SUMS`
  pass locally and remotely.

## Reproduction

The standalone quantizer-comparison benchmark does not provide a native NCU
mode. The added harness follows the repository's distributed-MoE NCU path while
using the same backend kernels directly with preallocated output buffers:

```bash
cd /workspace/flashinfer-w4a4-nightly-20260813
bash harness/run_nvfp4_quant_ncu.sh "$PWD" <fresh-run-id>
```

Reusable files:

- `scripts/profile_nvfp4_quant_ncu.py`
- `scripts/run_nvfp4_quant_ncu.sh`
- `scripts/validate_nvfp4_quant_ncu_report.py`

The first target and NCU capture exited zero and produced a two-action report,
but the initial wrapper then falsely rejected NCU's abbreviated console name.
That raw attempt is retained under
`ncu_nvfp4_quant_m4096_k7168_attempt1_wrapper_false_negative`; the old wrapper
and its wrapper-level failure transcript were not retained, so it is supporting
diagnostic evidence rather than the canonical run. The clean rerun above
completed with wrapper exit status zero.
