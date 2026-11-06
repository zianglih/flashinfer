# Kimi K3 EP8 W4A4 T64 phase and memory diagnostic

Source is clean `0def601d6603df828ea39679b41ccbce64f7f09e` on c3 B300 GPU6, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2 / CuTe DSL 4.7.1. The public benchmark includes initial quantization, PDL and unfused CuTe finalization. Both backends replay the fresh full campaign's unchanged `kimi-k3/nvfp4/observed/token_64.autotune.json`. Observer receipts assert actual matching cache hits and source/cache immutability. No AUTO search, tactic edits, compiler instrumentation, or source edits.

Raw records are in `diagnostic-k3-t64-20261026/`; `collection.json` verifies their downloaded SHA256 hashes. `nsys-summary.json` and `ncu-summary.json` in that directory hold derived values. Reproduction helpers are `scripts/k3_decode_diagnostic_20261026` at the project root. This is diagnostic evidence, not retention timing.

## NSYS: the gap is exposed after FC1

Three cold-L2 public graph replays have CuTe chain durations 241.569 / 239.521 / 241.473 us and TRTLLM 234.881 / 234.080 / 237.153 us. This agrees directionally with the independent full campaign's +6.048 us CuTe gap. Adjacent kernels overlap under PDL; kernel duration medians must not be summed.

| Kernel median (us) | CuTe | TRTLLM |
|---|---:|---:|
| Input quantization | 2.272 | 2.560 |
| Routing indices | 8.416 | 9.472 |
| Routed preparation | 3.360 | — |
| FC1 | 150.272 | 154.241 |
| FC2 | 77.280 | 72.576 |
| Combine | 4.640 | 6.912 |

Per-replay endpoint deltas are additive. Relative to TRTLLM, CuTe reaches FC1 completion 0.875333 us earlier on average, takes 5.760 us longer from FC1 completion to FC2 completion, and takes another 0.597333 us longer from FC2 completion through combine. Total mean difference is 5.483 us. This localizes the gap to exposed FC2 execution, without proving a specific scheduling cause.

## NCU: FC2 is memory-bound with a static grid

Four bounded selected-kernel reports use 27 metrics and six replay passes each. NCU replay timing is not native PDL timing. Raw CSV/report names and resource values identify FC1/FC2; one TRTLLM FC2 console launch label was misleading, while the report identifies the expected Bfloat16 output kernel.

| Metric | CuTe FC1 | TRTLLM FC1 | CuTe FC2 | TRTLLM FC2 |
|---|---:|---:|---:|---:|
| DRAM reads (MB) | 956.162 | 954.123 | 478.946 | 477.290 |
| DRAM % peak | 84.26 | 84.63 | 76.74 | 78.73 |
| Long-scoreboard stall % | 70.60 | 77.47 | 75.10 | 74.94 |
| Registers/thread | 82 | 96 | 90 | 128 |
| Threads/CTA | 320 | 640 | 288 | 512 |
| Grid CTAs | 8112 | 10848 | 148 | 6328 |
| SMEM bytes/CTA | 198528 | 203664 | 198528 | 204688 |

CuTe native tactic is N16, M128, cluster1, K8/K8, FC1 CLC true; the wrapper currently requests FC2 CLC false. TRTLLM uses `[8,349]`, native N8 kernels. The similar DRAM traffic and lower CuTe FC2 achieved bandwidth motivate a current-prefetch FC2 CLC experiment. The historical FC2 CLC test predates full weight prefetch; historical descriptor-N8-only and physical-B16 tests were neutral/regressive, so these are not assumed wins.
