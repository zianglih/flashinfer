# Descriptor-bounded MoE output experiment

Source is unstaged in [flashinfer-descriptor-output-review](../../flashinfer-descriptor-output-review), based on retained `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` plus the prior padded-output R2 experiment. Neither earlier checkout was modified. The current verified source snapshot is `full-gate-04`, which adds only the W4A16 late shared-store acquisition refinement to `full-gate-03`. The unchanged blockscaled implementation reuses source03 correctness and performance evidence; source04 has fresh validation and timing only for the affected W4A16 scope.

## Implementation

- W4A16 FC1 and unfused FC2, and swap-AB unfused FC2, use descriptor-bounded TMA stores for partial expert tiles. Swap-AB FC1 remains SIMT; fused finalize keeps its existing algorithm.
- Shared prepare publishes one immutable tensor map per active expert and output template after its early PDL signal. Keeping the allocation base and bounding the absolute final row avoids expert-start metadata and alignment-dependent policies.
- Static and CLC consumers select and cache the expert map. Only TMA-issuing warps acquire it; no descriptor mutation runs in the GEMM loop. Source-stage completion waits remain where required for safe shared-memory reuse. In source04, the W4A16 store acquire and epilogue warpgroup barrier sit directly before the next shared write, allowing the next TMEM load and arithmetic to overlap the preceding store.
- Removed the replaced SIMT output-tail paths and shape-dependent selection of TMA versus SIMT. Output staging is calculated from element size, tile size, and shared-memory capacity. Public APIs are unchanged.

## Verified correctness and scope

On B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2. Source03 evidence, reused for unchanged code:

- 224 exact paired CUDA-graph replays across 14 configurations, including actual CLC, PDL off/on, one/two CTA, old/swap W4 layouts, all supported activation families, and changed/empty/reactivated routing. Final and canonicalized intermediate outputs match R2; padding is untouched.
- 192 direct FP16/FP32 output cases across N16/N128/N256, including two store stages and accumulator overlap. These small-grid cases selected static scheduling; a separate active-CLC probe is recorded separately.
- 16 descriptor publication/replay proof cases, 11 existing pytest cases, and four paired W4 fused-finalize compatibility cases passed.
- All 112 captured candidate GEMM compilations contain no descriptor replacement instructions or local-memory spill sites.
- Scoped pre-commit, AST parsing, and diff checks passed. The local source matched all 349 files in the tested manifest. No sanitizer ran.

Source04 additionally passed all 96 exact paired W4A16 graph replays across six configurations, 10 existing W4 tests, and four exact fused-finalize compatibility cases. The only source delta is the W4A16 wait relocation; all 349 local source hashes match the source04 manifest, with no staged changes.

Detailed boundaries and receipts: [VALIDATION.md](VALIDATION.md), [validation-status.json](full-gate-03/validation-status.json), and [AUDIT.md](AUDIT.md).

## Source03 performance screen

The initial screen uses fixed saved tactics through `bench_moe_deepseek.py`, strict CUPTI, 10 warmups and 100 samples, CUDA graphs with cold L2, and tokens 4/64/4096/16384 across V3/V41F/K3/N3U and EP/TP. NVFP4 includes input quantization; swap-AB finalize is unfused.

All **144/144 cells (15 jobs)** completed and compare against saved R2 controls on matching physical GPUs: geometric-mean speedup **-1.05%** overall, **-1.45%** decode, and **-0.64%** prefill. The largest individual change is **-17.38%** for TP V3 W4A16 at 64 tokens. These time-separated measurements are a screening result, not a confirmed causal attribution.

Both original C3 devboxes disappeared after the final performance job completed. A replacement using the same image recovered persistent receipts and landed on the same physical B300 node used for TP. The fresh source-paired C-A-A-C confirmation reused the exact GPU UUIDs, routes, saved winners, strict CUPTI settings and native compilation caches. All four outliers reproduced:

| TP workload | Tokens | R2 control, µs | Descriptor candidate, µs | Fresh speedup | Historical speedup |
|---|---:|---:|---:|---:|---:|
| V3 W4A16 | 64 | 154.777 | 190.841 | -18.90% | -17.38% |
| V41F W4A4 | 4096 | 482.490 | 530.467 | -9.04% | -9.03% |
| K3 PER-TOKEN | 64 | 257.250 | 276.202 | -6.86% | -6.69% |
| V3 MXFP4x8 | 4096 | 491.620 | 523.028 | -6.01% | -5.93% |

The two fresh controls differ from the historical mean by only 0.11–0.58%. W4A16 candidate repeats vary by 2.25%; other candidate repeats vary by at most 0.064%. These four regressions are therefore reproducible with interleaved controls. This remains an unstaged implementation experiment, not a retained performance improvement; the full screen is still distinct from the fresh four-cell confirmation.

Fresh raw evidence: [confirm-evidence](full-gate-03/confirm-evidence); analysis: [confirm-analysis.json](full-gate-03/confirm-analysis.json).

Full raw evidence: [perf-evidence](full-gate-03/perf-evidence), with 94 SHA-verified files; cells: [perf-cells.csv](full-gate-03/perf-cells.csv); analysis: [perf-analysis.json](full-gate-03/perf-analysis.json). Persistent native compilation caches were preserved.

## Source04 W4A16 refinement

The fresh affected-scope screen contains **32 W4A16 cells**, with two bounded cells followed by 30 additional cells. Each uses source03 as control and source04 as candidate in C-A-A-C order, the same GPU within the pair, frozen saved tactics, and strict CUPTI. No blockscaled cases were rerun, and this is not a fresh 144-cell source04 benchmark.

| Backend scope | Fresh cells | Geometric mean vs source03 | Decode | Prefill |
|---|---:|---:|---:|---:|
| W4A16 | 32 | +0.37% | +0.30% | +0.43% |
| W4A4, per-token, MXFP4x8, MXFP8 | 0 | Unchanged source; reuse source03 | — | — |

The W4A16 range is **−0.80% to +4.97%**. The largest gains are TP V3 at 64 tokens (+4.97%) and EP V41F at 16384 tokens (+3.60%). The refinement meets the neutral/winning criterion and is kept in the unstaged review copy. The broader descriptor experiment remains unretained relative to the PR/padded R2 implementation because the confirmed gaps above remain.

Absolute timings below are arithmetic means of the two CUPTI medians per source. Positive percentages mean source04 is faster. The R2 columns are historical context; EP uses a different physical GPU from historical R2, so those columns are not fresh paired evidence. TP V3 T64 remains −14.94% relative to historical R2 (155.073→182.313 µs).

| Model | Topology | Tokens | Source03 µs | Source04 µs | vs03 | Historical R2 µs | vs historical R2 |
|---|---|---:|---:|---:|---:|---:|---:|
| V3 | EP | 4 | 51.417 | 51.329 | +0.17% | 51.296 | -0.06% |
| V3 | EP | 64 | 142.130 | 141.906 | +0.16% | 140.673 | -0.87% |
| V3 | EP | 4096 | 290.947 | 290.524 | +0.15% | 282.946 | -2.61% |
| V3 | EP | 16384 | 1225.606 | 1213.702 | +0.98% | 1155.063 | -4.83% |
| V3 | TP | 4 | 40.712 | 40.609 | +0.25% | 39.960 | -1.60% |
| V3 | TP | 64 | 191.369 | 182.313 | +4.97% | 155.073 | -14.94% |
| V3 | TP | 4096 | 657.940 | 654.492 | +0.53% | 645.684 | -1.35% |
| V3 | TP | 16384 | 2231.229 | 2219.052 | +0.55% | 2229.180 | +0.46% |
| V41F | EP | 4 | 39.552 | 39.568 | -0.04% | 38.888 | -1.72% |
| V41F | EP | 64 | 213.970 | 213.738 | +0.11% | 214.385 | +0.30% |
| V41F | EP | 4096 | 446.091 | 445.395 | +0.16% | 450.265 | +1.09% |
| V41F | EP | 16384 | 1560.172 | 1506.028 | +3.60% | 1534.518 | +1.89% |
| V41F | TP | 4 | 41.336 | 41.488 | -0.37% | 42.017 | +1.27% |
| V41F | TP | 64 | 232.834 | 232.930 | -0.04% | 233.034 | +0.04% |
| V41F | TP | 4096 | 617.220 | 611.365 | +0.96% | 638.899 | +4.50% |
| V41F | TP | 16384 | 2073.241 | 2078.585 | -0.26% | 2149.633 | +3.42% |
| K3 | EP | 4 | 57.344 | 57.400 | -0.10% | 58.168 | +1.34% |
| K3 | EP | 64 | 248.617 | 248.737 | -0.05% | 248.578 | -0.06% |
| K3 | EP | 4096 | 535.410 | 534.290 | +0.21% | 546.700 | +2.32% |
| K3 | EP | 16384 | 1983.382 | 1998.351 | -0.75% | 1987.791 | -0.53% |
| K3 | TP | 4 | 50.665 | 50.681 | -0.03% | 50.584 | -0.19% |
| K3 | TP | 64 | 277.770 | 277.609 | +0.06% | 280.682 | +1.11% |
| K3 | TP | 4096 | 847.116 | 843.500 | +0.43% | 849.813 | +0.75% |
| K3 | TP | 16384 | 2916.024 | 2930.112 | -0.48% | 2991.160 | +2.08% |
| N3U | EP | 4 | 42.544 | 42.593 | -0.11% | 42.081 | -1.20% |
| N3U | EP | 64 | 143.297 | 143.329 | -0.02% | 142.073 | -0.88% |
| N3U | EP | 4096 | 406.811 | 403.483 | +0.82% | 394.521 | -2.22% |
| N3U | EP | 16384 | 1543.332 | 1555.836 | -0.80% | 1497.861 | -3.73% |
| N3U | TP | 4 | 47.720 | 47.769 | -0.10% | 47.864 | +0.20% |
| N3U | TP | 64 | 153.433 | 153.401 | +0.02% | 154.729 | +0.87% |
| N3U | TP | 4096 | 639.395 | 637.027 | +0.37% | 620.245 | -2.63% |
| N3U | TP | 16384 | 2304.917 | 2292.541 | +0.54% | 2271.841 | -0.90% |

Fresh source04 raw evidence: [perf-evidence](full-gate-04/perf-evidence); [32-cell CSV](full-gate-04/perf-cells.csv); [summary](full-gate-04/perf-summary.json). Source03 snapshots and receipts remain intact. No sanitizer or further optimization rounds were run, and no changes were committed, pushed, or added to the PR.
