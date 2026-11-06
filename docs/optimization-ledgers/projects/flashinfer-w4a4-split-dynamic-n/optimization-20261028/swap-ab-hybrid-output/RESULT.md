# Swap-AB output-store experiment

The original FC2 hybrid is the only candidate supported by this bounded screen: it improves prefill by **1.26% geomean**, with decode effectively neutral (**−0.04%**). Keep it as an unstaged candidate. Moving partial FC2 stores to native TMEM ownership loses performance, and adding FC1 payload TMA does not justify a blanket policy.

## Measured comparison

Positive means faster: `(R2 latency / candidate latency − 1) × 100`. The first three columns compare directly with fresh padded-R2 controls. Incremental FC1 compares the combined arm with its contemporaneous FC2-only arm; no column is constructed by multiplying speedup ratios.

- **FC2 hybrid:** full epilogue slabs use TMA; partial slabs retain the original TMEM-transposed SIMT tail. Existing bulk eligibility stays unchanged.
- **Native FC2:** uses the native packed TMEM fragment for full and partial output, with scalar16-bit SIMT tails; enables capacity-sized slabs for all routed N.
- **FC1 + FC2 hybrid:** adds FC1 payload TMA for complete slabs to the original FC2 hybrid. Partial FC1 payload and scale factors retain direct stores.

| Model | Tokens | Mode | FC2 hybrid | Native FC2 | FC1 + FC2 hybrid | Incremental FC1 |
|---|---:|---|---:|---:|---:|---:|
| V3 EP8 | 64 | W4A4 | +0.04% | -0.02% | -0.11% | -0.05% |
| V3 EP8 | 4096 | W4A4 | +0.78% | -2.66% | +0.69% | -0.13% |
| V3 TP8 | 4096 | MXFP4x8 | +3.66% | -8.57% | +3.62% | -0.02% |
| V41F EP4 | 64 | MXFP8 | +0.04% | -0.12% | -0.01% | -0.10% |
| V41F EP4 | 4096 | MXFP8 | +0.69% | +0.62% | +0.64% | -0.04% |
| V41F TP4 | 64 | W4A4 | -0.06% | -0.38% | -0.07% | -0.05% |
| V41F TP4 | 16384 | W4A4 | +0.56% | -4.00% | +0.19% | -0.29% |
| K3 EP8 | 4096 | PER-TOKEN | +1.35% | +1.04% | +0.54% | -0.82% |
| K3 TP8 | 64 | MXFP4x8 | +0.07% | -3.33% | -0.11% | -0.10% |
| K3 TP8 | 4096 | MXFP4x8 | +2.96% | -12.76% | +2.71% | -0.10% |
| N3U EP8 | 4096 | MXFP8 | -0.45% | -0.63% | -3.11% | -2.69% |
| N3U TP8 | 64 | PER-TOKEN | -0.28% | -1.18% | -0.03% | +0.01% |
| N3U TP8 | 4096 | PER-TOKEN | +0.56% | -3.28% | -2.19% | -2.75% |

| Geomean | Cells | FC2 hybrid | Native FC2 | FC1 + FC2 hybrid | Incremental FC1 |
|---|---:|---:|---:|---:|---:|
| Decode | 5 | -0.04% | -1.01% | -0.07% | -0.06% |
| Prefill | 8 | +1.26% | -3.89% | +0.36% | -0.86% |
| All | 13 | +0.76% | -2.79% | +0.20% | -0.55% |

The FC1 combined arm inherits the FC2 improvement. Its own incremental prefill effect is **−0.86%**, reaching **−2.75%** on N3U TP per-token. Native FC2 reaches **−12.76%** versus R2 on K3 TP MXFP4x8 prefill.

![Output-store speedups](output-store-speedup.png)

[SVG](output-store-speedup.svg) · [Exact scalar table](perf-cells.csv) · [All paired medians and compiled geometry](perf-summary.json)

## What the geometry establishes

- All eight prefill cases actually used 64-token, two-stage FC2 TMA slabs. The native arm uses 16/32-token, one-stage slabs for the five small-N cases. Operand stage counts and MMA geometry are identical across R2, original FC2 hybrid, and native FC2 in every measured cell. Native's losses are therefore not caused by an operand-depth reduction.
- FC1 payload staging leaves the two N3U regressions' geometry unchanged: EP MXFP8 remains M256/N256/K128 with six operand stages; TP per-token remains M128/N256/K256 with four. The new payload scratch, staging, and waits are additional work, but this screen does not causally profile which dominates.
- Only K3 TP MXFP4x8 T4096 reduces FC1 operand stages, nine to eight, with the same M256/N128/K128 geometry. Its incremental FC1 loss is only 0.10%. The other twelve cells keep their FC1 operand depth and geometry.
- Native-tail scalar stores avoid the TMEM transpose but change global-store ownership. Poorer store coalescing/instruction efficiency is a source-based explanation to investigate, not a profiler-proven cause. No further optimization candidate was tested in this round.

## Evidence and boundaries

- **Timing:** two fresh six-phase screens, `R2 → FC2 → native/combined → native/combined → FC2 → R2`, on the same GPU per cell. Each phase is the median of 100 strict CUPTI samples after 10 warmups, with CUDA Graph replay and cold L2. The arm latency is the mean of its two phase medians. Event fallback and autotuning are rejected. Frozen saved winner keys, tactics, routing, all 348 source hashes, and GPU UUIDs are verified. First/last R2 median drift is at most 0.24% in the native screen and 0.62% in the FC1 screen.
- **Workload:** `bench_moe_deepseek.py`, public functional API, swap-AB, unfused finalize; NVFP4 includes input quantization with the existing per-token recipe. Thirteen selected cells cover all four models, EP/TP, and W4A4/per-token/MXFP8/MXFP4x8. This is a bounded fixed-tactic screen, not a full all-token retune or benchmark-table refresh. No W4A16 or TRTLLM baseline rerun.
- **Hardware:** eight B300 GPUs on C3, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, driver595.91.07, CuTe DSL4.8. Existing persistent native compilation caches are retained.
- **Correctness:** [validation evidence](VALIDATION.md) records 128 original-FC2, 512 native-FC2, and 384 FC1 combined exact graph replays. Valid intermediate payloads/scales and final outputs match R2. No captured GEMM spills. Owned padded-row writes remain a diagnostic; padding preservation is not claimed. No sanitizer or full output-dtype/activation-matrix run.
- **Raw evidence:** [FC2/native archive manifest](fc2-screen-04/perf-evidence/evidence/archive-manifest.json), [FC1 archive manifest](fc1-screen-03/perf-evidence/evidence/archive-manifest.json). All 234 archived files are locally SHA256-verified; per-phase source receipts, raw 100-sample arrays, commands, environment, GPU state, and stdout are retained. Each screen's raw medians remain separate.

All arms use retained HEAD `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` plus the padded-R2 base. Only the swap-AB kernel differs from R2 in each source snapshot:

| Arm | Frozen snapshot | Kernel SHA256 |
|---|---|---|
| FC2 hybrid | `fc2-01` | `aff286440591dec41bca64a78f27515dd5f6c1563f02c87b8702f89e03755b5a` |
| Native FC2 | `fc2-native-03` | `17e72c68fa7603a17525ce934f53244a669d470c72951d3a9bb74097f2335772` |
| FC1 + FC2 hybrid | `fc1-02` | `a813327258e82661070dc6ca9efff6e366282969d1459131a518907ba23723dc` |

No source was committed or pushed, and no PR body was changed by this experiment.
