# W4A16 short-K GEMM2 work units: evidence

Evidence for the FlashInfer PR "perf(moe): group short-K W4A16 GEMM2 M tiles into work units".
Control: upstream `flashinfer-ai/flashinfer` main `67d996c0a454cf975e91fd97dcce457b4a54b202`.
Candidate: control plus `tested-candidate.patch` (sha256 in `candidate.patch.sha256`).

Runtime: 8x NVIDIA B300 SXM6 AC (SM103, 148 SMs), driver 595.91.07, image
`nvcr.io/nvidia/pytorch:26.05-py3` (`sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`),
CUDA 13.2 / NVCC 13.2.78, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, nvidia-cutlass-dsl 4.8.0, apache-tvm-ffi 0.1.16,
cupti-python 13.5.0 (nvidia-cuda-cupti 13.5.25; CUPTI attaches on this driver, no event fallback). Full package list:
`environment/`.

| Path | Contents |
|---|---|
| `sweep/fc2-unit-sweep.csv`, `sweep/summary.txt` | Kernel-level GEMM2 sweep: forced units vs one-tile units, 1,770 timed rows (+120 forced configurations that exceed TMEM and are rejected at compile time), every output buffer bit-identical to one-tile units. `tools/fc2_unit_sweep.py`. |
| `campaign/caac1/` | PR 7290-style W4A16 matrix (8 jobs x 13 tokens) on the measured snapshot: per-phase raw CUPTI samples and tactics (`*.record.json`), benchmark CSV lines, `summary.json`/`.md`. `tools/caac.py`, `tools/bench_w4a16_only.py`. |
| `campaign/caac2/` | Rerun of K3 TP8 on the final source (after the K-tail synchronization fix) and an independent V3 TP8 repeat. |
| `codegen/` | Normalized PTX/SASS hashes and resource usage: upstream, the benchmarked snapshot and the final source (`tools/codegen_identity.py`). |
| `tests/` | pytest logs: `round1/` (first candidate) and `final/` (final source), plus the upstream MegaMoE run showing the two pre-existing failures. |
| `differential/` | Whole-MoE outputs at model dimensions, upstream vs candidate, 360 cases bit-identical; oracle spot checks. |
| `tools/` | All harness scripts used. |

Method summary: each campaign job runs on one GPU as C1 / A-frozen / A-native / A-native / A-frozen / C2 (fresh
process per phase, unchanged `benchmarks/bench_moe_deepseek.py`, `--functional-api --swap-ab --no-fused-finalize
--include-activation-quant`, 10 warmups, 100 CUPTI cold-L2 CUDA-graph samples per cell, PDL on). Control and candidate
were tuned freshly in this environment; "frozen" replays the control's winners in both roles, "native" each role's own.
Speedup = sqrt(C1*C2) / sqrt(A1*A2) - 1 on per-phase medians; aggregates are geometric means over tokens >= 4.
