# Fixed FC1 CLC / static FC2 comparison

Compared current shared FC1/FC2 CLC on/off AUTO (360 tactics) against fixed FC1 CLC on / FC2 static AUTO (180 tactics). Candidate is an unstaged experiment; no source was retained or pushed.

Across132 retained cells, the fixed policy is **-0.94%** overall: decode4–512 **-0.79%**, prefill4096–16384 **-1.32%**. It reduces observed native AUTO worker-sum walltime from2852.5s to1665.8s (**41.6% less**), but introduces material K3 prefill regressions. These are separate costs: AUTO timings are excluded from every GPU latency ratio.

| Model | Format | Overall | Decode4–512 | Prefill4096–16384 |
| --- | --- | ---: | ---: | ---: |
| v3 | CuteDSL W4A4 | -0.44% | -0.37% | -0.61% |
| v3 | CuteDSL PER-TOKEN | -0.77% | -0.56% | -1.34% |
| v3 | CuteDSL MXFP8 | -0.48% | -0.70% | +0.10% |
| v3 | CuteDSL MXFP4x8 | -0.26% | -0.53% | +0.48% |
| v41-flash | CuteDSL W4A4 | -0.13% | -1.11% | +2.50% |
| v41-flash | CuteDSL PER-TOKEN | +0.01% | -0.40% | +1.14% |
| v41-flash | CuteDSL MXFP8 | -1.08% | -1.49% | +0.02% |
| v41-flash | CuteDSL MXFP4x8 | -0.45% | -0.86% | +0.64% |
| kimi-k3 | CuteDSL W4A4 | -2.49% | -0.77% | -6.92% |
| kimi-k3 | CuteDSL PER-TOKEN | -1.68% | -0.89% | -3.73% |
| kimi-k3 | CuteDSL MXFP8 | -1.05% | -0.99% | -1.21% |
| kimi-k3 | CuteDSL MXFP4x8 | -2.38% | -0.81% | -6.46% |

The largest stable losses are K3 at16384tokens: W4A4−11.30% (811.72→915.13µs), per-token−7.18% (1082.34→1166.13µs), and MXFP4x8−9.45% (1082.44→1195.36µs). K3 W4A4 and MXFP4x8 also lose approximately6% at4096tokens. V4.1 W4A4 at16384 gains6.75% (663.69→621.71µs).

A separately authorized frozen-winner confirmation investigated V3 MXFP4x8 at16384: the primary+3.52% result had6.7% control-pass drift; the confirmation is−0.49% and still has approximately5% candidate-pass drift. No stable gain is claimed for that cell. The primary table and aggregates remain unchanged; the confirmation is reported separately. The same existing observer also records incidental MXFP8 at the target token; its original−0.71% versus confirmation+7.03% likewise shows this large-prefill point is not stable across rounds.

## Timing and validation

| Model / family | Control AUTO(s) | Fixed AUTO(s) | Four paired passes(s) |
| --- | ---: | ---: | ---: |
| v3 / nvfp4 | 397.24 | 246.63 | 201.42 |
| v3 / mxfp | 451.05 | 292.13 | 165.25 |
| v41-flash / nvfp4 | 450.64 | 241.42 | 194.38 |
| v41-flash / mxfp | 477.64 | 308.16 | 167.75 |
| kimi-k3 / nvfp4 | 492.62 | 248.94 | 244.27 |
| kimi-k3 / mxfp | 583.28 | 328.47 | 200.83 |

| Native AUTO host span | Shared | Fixed |
| --- | ---: | ---: |
| Worker-sum process wall(s) | 2852.47 | 1665.75 |
| cute.compile inclusive wall(s) | 1222.22 | 751.04 |
| Profile exclusive wall(s) | 1437.12 | 751.17 |
| Profile calls | 84,480 | 42,240 |

These are observed cache-aware host spans across six parallel workers. cute.compile includes SDK cache work; profiling excludes nested compile time but includes warmups, graph capture, GPU waits, and measurement machinery. Persistent compilation caches and smoke artifacts were reused; this is not an isolated cold compiler benchmark.

- Fresh native AUTO for both sources; then frozen C/A/A/C with10warmups and100cold-L2 CUDA-graph CUPTI samples per pass. Positive percent means faster:100×(sqrt(c0×c3)/sqrt(a1×a2)−1).
- All156cells and62,400primary samples passed source/benchmark/helper hashes, route identity, cache snapshot and selected-tactic checks. All264 comparable native admission records exactly halve. No W4A16, TRTLLM or CUTLASS measurement/search is included.
- All156candidate cells actually used FC1 CLC and static FC2; no eligibility fallback occurred. Control shared CLC selected on/off counts by format: W4A4 30/9, per-token26/13, MXFP8 33/6, MXFP4x8 23/16.
- Models: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8. All13requested token counts are reported;1/2are excluded from retention aggregates. NVFP4 input quantization is included; MX inputs are prequantized. Fused finalize is off.
- Source HEAD0b7fe90151340d4fca6a5ec41a91019dde743819; candidate patchcd7f01746aa8c82cfc95a0467b86928887fadbc1627be76ac529f090174f252c. Existing C3 B300, CUDA13.2 image nvcr.io/nvidia/pytorch:26.05-py3. Full deployment receipts and unchanged native-cache proof are under control/ and candidate/.

Full tables: [speedups.md](speedups.md). Raw phase/paired latencies and tactics: [raw-median-speedups.csv](raw-median-speedups.csv). All primary samples: [raw-samples.csv](raw-samples.csv). Structured proof: [summary.json](summary.json). Separate confirmation: [recheck-results.md](recheck-results.md), [recheck-summary.json](recheck-summary.json), [recheck-raw-samples.csv](recheck-raw-samples.csv). Raw public output, samples, snapshots and receipts: evidence/.
