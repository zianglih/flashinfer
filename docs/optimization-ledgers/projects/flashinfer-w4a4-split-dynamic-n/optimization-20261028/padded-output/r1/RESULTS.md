# Initial padded-output measurement (r1)

Superseded by the simpler nonempty-slab TMA implementation in r2. These raw measurements remain the retained-head control source for r2.

Baseline `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`; candidate kernel `ff6993cbaf412222b15ac5bc27ae421fbbcc30c7b1520475c0e35b7d2033620f`.

| Topology | Model | Decode speedup | Prefill speedup |
|---|---|---:|---:|
| EP | all | -0.53% | +0.48% |
| EP | v3 | -0.15% | +1.89% |
| EP | v41-flash | -0.50% | -0.96% |
| EP | kimi-k3 | -0.86% | +0.08% |
| EP | nemo3-ultra | -0.70% | +0.83% |
| TP | all | -2.66% | +3.97% |
| TP | v3 | -0.99% | +5.69% |
| TP | v41-flash | -1.16% | +0.53% |
| TP | kimi-k3 | -2.51% | +4.40% |
| TP | nemo3-ultra | -5.13% | +3.68% |

Positive is faster: geometric mean of retained-head latency divided by candidate latency, minus one. Decode tokens 4/64; prefill 4096/16384. All four model shapes and comparable scaled dtypes; unchanged W4A16 sanity rows excluded from aggregates.

Same-GPU C-A-A-C; 10 warmups and 100 strict CUPTI cold-L2 graph samples per pass. 15 jobs, 144 cells, 576 medians, 57,600 samples. Exact saved tactics and routes; no autotuning or new TRTLLM/non-swap measurements. NVFP4 includes initial activation quantization.

All 2,037 archived artifact hashes and source bindings independently checked. 208 paired exact checks and eight existing tests passed; no sanitizer. See [raw cells](report/cells.csv), [summary](report/summary.json), and [independent audit](independent-perf-review/independent-review.json).

The worst stable regression is N3U TP8, four tokens, MXFP4x8: 36.34 to 40.25 us (−9.72%). All four formats show a similar ~4 us loss with FC2 N16, so the bulk-tail duplication is not its cause. The output grows from 88×2048 to 1408×2048 BF16 (0.34375 to 5.5 MiB). Component attribution is kept separately.

R1 duplicated the predicated SIMT tail body at every bulk slab. R2 removes this by storing the complete nonempty slab inside the existing padded allocation.
