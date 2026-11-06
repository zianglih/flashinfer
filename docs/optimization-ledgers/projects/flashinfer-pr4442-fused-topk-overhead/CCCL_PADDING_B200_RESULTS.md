# CCCL DeviceBatchedTopK output-padding validation

## Environment

- Date: 2026-08-15 UTC
- Hardware: NVIDIA B200, compute capability 10.0 (GPU 0 of an 8-GPU C1 devbox)
- Driver: 580.126.09
- CUDA compiler/runtime: 13.2 (`nvcc` 13.2.78; runtime/driver API 13020)
- Container: `nvcr.io/nvidia/pytorch:26.05-py3`
- CCCL base: `4a94f9f6445f47a5cf5978b1d0eed4ed524e5546`
- Shape: FP32 scores, int32 row-local indices, 16 rows, width 202752, `k=2048`
- Selection contract: `gpu_to_gpu`, `prefer_smaller_index`, unsorted output
- Timing: cold L2; the cache flush is synchronized before each timed interval; 20 warmups and 100 CUDA-event samples per table cell

`default_plus_tail` is the existing Top-K call followed by a separate tail-fill kernel. `padded_fused` opts into `DeviceBatchedTopK::OutputPadding` and writes the tail in the existing Top-K launch. Each sweep runs separate-tail A1, fused B, separate-tail A2; `control` is the existing unpadded call.

## Raw medians (microseconds)

| Sweep | Pattern | Control | A1 separate | B fused | A2 separate |
|---:|---|---:|---:|---:|---:|
| 1 | full | 42.832 | 44.288 | 43.696 | 44.448 |
| 1 | mixed | 42.528 | 43.984 | 43.056 | 44.096 |
| 1 | short | 19.776 | 21.200 | 20.448 | 21.264 |
| 2 | full | 43.392 | 44.576 | 44.096 | 44.512 |
| 2 | mixed | 42.720 | 44.432 | 43.328 | 44.096 |
| 2 | short | 19.936 | 21.472 | 20.512 | 21.024 |
| 3 | full | 42.816 | 44.224 | 43.792 | 44.272 |
| 3 | mixed | 42.272 | 43.920 | 42.944 | 43.808 |
| 3 | short | 19.648 | 20.928 | 20.288 | 20.816 |

Patterns:

- `full`: every runtime segment length is 202752, so no tail stores are required.
- `mixed`: cycle `[202752, 131072, 65536, 32768, 16384, 8192, 4096, 2048]` across rows; no tail stores are required, but runtime lengths vary.
- `short`: cycle `[2047, 0, 2048, 1]`, exercising partial and fully padded tails.

For each sweep, the separate-tail reference is `(A1 + A2) / 2`. The median of the three paired reductions is:

| Pattern | Fused vs separate tail | Fused overhead vs unpadded control | Separate-tail overhead vs control |
|---|---:|---:|---:|
| full | 1.03% lower latency (1.010x) | +2.02% | +3.34% |
| mixed | 2.11% lower latency (1.022x) | +1.42% | +3.61% |
| short | 3.46% lower latency (1.036x) | +3.26% | +6.58% |

The result is consistent across all three sweeps, but modest: the fused feature removes a launch and roughly halves the padding overhead for this GLM-5-shaped operator, while the Top-K selection remains the dominant cost.

## Correctness and compatibility

- Targeted CUB build completed all 28 incremental CUDA compile/link actions with no failures.
- The 15 targeted CTests passed (Keys/Pairs host and graph launch variants, API, environment API, and fixture), 0 failed, in 33.35 seconds.
- The default unpadded SM100 specialization was compiled from upstream `main` and the candidate tree. Their normalized SASS files were byte-identical, both SHA-256 `738e1774d15aeae7cb210f08b26e4324fd8b6ea6b9dae19027c71f2fc2178817`.
- The benchmark verifies every selected index is in range, existing calls leave unused output slots untouched, and both separate and fused padding write exactly `-1` to every unused slot.

Remote raw artifacts are retained under `/hai-workspace/cccl-padding-results/{sass-final,perf-final,perf-final-2}` on devbox `flashinfer-pr4442-cub-fused`.
