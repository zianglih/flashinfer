# Fixed FC1 CLC / static FC2 policy comparison

Control: current pushed PR #7290 source `0b7fe90151340d4fca6a5ec41a91019dde743819`, with 360 raw non-W4A16 tactics and a shared FC1/FC2 CLC on/off flag. Candidate: the same source with only a six-line tuner policy diff, enumerating 180 geometries/depth pairs with FC1 CLC requested and FC2 static. The original legality fallback for reduced SM budgets, one-wave grids and grid-Y limits remains intact; requested and effective scheduling are recorded separately. Rubin and W4A16 policy remain unchanged.

The completed, unretained candidate source copy was removed on2026-10-27; evidence and helpers remain here. The canonical source and PR are unchanged by this experiment. Candidate selection caches carry a separate Blackwell tag.

Both arms perform fresh native AUTO on the current source. Frozen source-specific winners are then replayed control/candidate/candidate/control on the same exclusively assigned GPU. Benchmark: public `benchmarks/bench_moe_deepseek.py`, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples, PDL, unfused CuTe finalize. Standard NVFP4 and per-token NVFP4 include initial activation quantization; MXFP8 and MXFP4x8 use prequantized inputs. Skip W4A16, TRTLLM and CUTLASS. Models: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8. Tokens: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Report all; exclude 1/2 from aggregate decisions. Decode is 4–512; prefill is 4096–16384.

Percent speed change is `100 * (control_latency / candidate_latency - 1)`; positive means faster. Per-source latency is the geometric mean of its two 100-sample phase medians. Raw medians and all samples are retained.

Environment: existing C3 `fi-moe-nvfp4-port-1026`, node `hu-wtc-101`, B300 SM103, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. Six workers use separate GPUs0–5. GPU6 is reserved for a bounded existing correctness gate. Native compilation artifacts are reused only after full native-source identity verification; caches remain in persistent storage, with source-private DSL namespaces.

## Completed result

All six groups completed: 156 cells, 62,400 paired timing samples, 468 matched route/quantization records, and 264 matched admission records whose counts halve exactly. Runtime dispatch confirms effective FC1 CLC on / FC2 off for every candidate cell. The 16 existing correctness checks passed. Canonical source and PR remain unchanged; the candidate was not retained; its stale source copy has been removed.

| Model | Format | Overall | Decode 4–512 | Prefill 4096–16384 |
| --- | --- | ---: | ---: | ---: |
| V3 EP8 | NVFP4 W4A4 | −0.44% | −0.37% | −0.61% |
| V3 EP8 | NVFP4 per-token | −0.77% | −0.56% | −1.34% |
| V3 EP8 | MXFP8 | −0.48% | −0.70% | +0.10% |
| V3 EP8 | MXFP4x8 | −0.26% | −0.53% | +0.48% |
| V4.1-Flash EP4 | NVFP4 W4A4 | −0.13% | −1.11% | +2.50% |
| V4.1-Flash EP4 | NVFP4 per-token | +0.01% | −0.40% | +1.14% |
| V4.1-Flash EP4 | MXFP8 | −1.08% | −1.49% | +0.02% |
| V4.1-Flash EP4 | MXFP4x8 | −0.45% | −0.86% | +0.64% |
| Kimi K3 EP8 | NVFP4 W4A4 | −2.49% | −0.77% | −6.92% |
| Kimi K3 EP8 | NVFP4 per-token | −1.68% | −0.89% | −3.73% |
| Kimi K3 EP8 | MXFP8 | −1.05% | −0.99% | −1.21% |
| Kimi K3 EP8 | MXFP4x8 | −2.38% | −0.81% | −6.46% |
| All | All four formats | **−0.94%** | **−0.79%** | **−1.32%** |

Aggregates are geometric means of speed ratios, excluding 1/2 tokens. This policy is not performance-neutral: K3 at 16384 tokens loses 11.30% for W4A4, 7.18% for per-token, and 9.45% for MXFP4x8. All K3 prefill control winners already use static FC2, so these losses do not demonstrate a need for FC2 CLC. They reflect forcing FC1 CLC and the resulting native AUTO winners. K3 MXFP4x8 at 4096 has identical geometry/depth and only FC1 scheduling changes, with a stable 6.26% loss.

AUTO worker walltime sums fall from 2852.5 to 1665.8 seconds (41.6%); these are concurrent worker sums with persistent compilation caches, not serial elapsed time or cold compilation speedup. Raw tactic-profile call counts halve from 84,480 to 42,240.

One noisy V3 MX prefill point received a separate frozen-winner C/A/A/C confirmation. MXFP4x8 at 16384 changes from +3.52% in the main campaign to −0.49% in the confirmation, whose candidate repeats still drift by about 5%. MXFP8 at the same token also varies between runs. These gains are not stable; the original primary table remains unchanged and the confirmation is reported separately. This uncertainty does not remove the stable K3 losses.

- [Full signed per-token table](speedups.md)
- [Raw phase medians, selected tactics and runtime scheduler flags](raw-median-speedups.csv)
- [All 62,400 paired samples](raw-samples.csv)
- [Machine-readable source checks and aggregation](summary.json)
- [Separate noisy-point confirmation](recheck-results.md)
- [Independent final result verification](independent-final-result-review.json)
- [Completion and idle-GPU receipt](benchmark-completion.json)
