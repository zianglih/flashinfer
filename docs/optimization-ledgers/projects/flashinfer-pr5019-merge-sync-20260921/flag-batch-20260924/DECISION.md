# Fixed F4 versus F8 decision

**Keep F4 in the curated W4A16 MegaMoE AUTO catalog for the measured workload.** F8 remains supported through the existing manual configuration; this experiment made no production source, commit, push, or PR-body changes.

Tested clean FlashInfer `19e8aebb541684df09e12cc79610338aa429a2cf` on separate C2 B300 nodes for EP4 and EP8, using `nvcr.io/nvidia/pytorch:26.05-py3` (PyTorch/NVCC CUDA 13.2, CuTe DSL 4.7.1 with its bundled CUDA 13.3 native compiler). Runtime versions and device/source receipts are retained in [RUNTIME_SETUP.md](RUNTIME_SETUP.md).

Each fixed-F arm autotuned the same eight native candidates (G512/G1024 × N64/N128 × epilogue/dispatch return), changing only `flag_batch`. Workload: H7168/I2048/E256/topk8, BF16 activations, canonical NVFP4 weights, FP32 precomputed routes, unit runtime alphas, routing in FC2, and in-kernel FC2 reduction disabled. The measured public forward includes fused staging, alpha copies, communication, compute, combine, and owned-output handling.

Two complete sweeps per arm, F4–F8–F8–F4 on the same node for each EP. Each cell below is the pooled median of 200 untrimmed cold-L2 CUDA-graph CUPTI rank-MAX spans (100 samples and three warmups per sweep). Preparation, weight conversion, routing, compilation, autotuning, capture, warmup, and L2 flushing are outside final timing. Native AUTO separately uses its unchanged hot-cache GPU-event scorer.

All tokens are global. Latencies are microseconds. **F4/F8 > 1 favors F8.** Tokens 1–2 are reported but excluded from retention; decode is 4–512, prefill is 4096/8192/16384.

| Tokens | EP4 F4 µs | EP4 F8 µs | EP4 F4/F8 | EP8 F4 µs | EP8 F8 µs | EP8 F4/F8 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 73.3445 | 72.4810 | 1.0119× | 74.1920 | 75.9040 | 0.9774× |
| 2 | 93.7280 | 92.1775 | 1.0168× | 92.5605 | 96.6570 | 0.9576× |
| 4 | 112.7685 | 115.0250 | 0.9804× | 100.4325 | 106.9440 | 0.9391× |
| 8 | 151.4900 | 155.3770 | 0.9750× | 128.3365 | 130.1930 | 0.9857× |
| 16 | 201.2495 | 203.7465 | 0.9877× | 144.9920 | 146.6085 | 0.9890× |
| 32 | 261.6985 | 260.0665 | 1.0063× | 166.3850 | 164.7850 | 1.0097× |
| 64 | 293.4265 | 294.0990 | 0.9977× | 191.1375 | 193.9055 | 0.9857× |
| 128 | 317.0900 | 320.4990 | 0.9894× | 199.9525 | 200.0015 | 0.9998× |
| 256 | 330.2755 | 326.6435 | 1.0111× | 200.3380 | 197.6805 | 1.0134× |
| 512 | 341.6510 | 343.7150 | 0.9940× | 201.5840 | 205.4415 | 0.9812× |
| 4096 | 828.3890 | 860.1700 | 0.9631× | 467.2200 | 498.4190 | 0.9374× |
| 8192 | 1545.8840 | 1590.9090 | 0.9717× | 782.1320 | 836.4350 | 0.9351× |
| 16384 | 2927.2830 | 2956.5930 | 0.9901× | 1522.5385 | 1554.1690 | 0.9796× |

## Interpretation

- **EP4:** decode F4/F8 geometric mean `0.992631×`; F8 latency is **0.742% higher**. Prefill F8 latency increases: 3.836%, 2.913%, 1.001% at 4K/8K/16K.
- **EP8:** decode F4/F8 geometric mean `0.987722×`; F8 latency is **1.243% higher**. Prefill F8 latency increases: 6.678%, 6.943%, 2.077% at 4K/8K/16K.
- Only 32/256 tokens show pooled decode wins in either EP degree, all below 1.4% speedup. EP4 wins reverse sign between paired comparisons. EP8 N32 has 0.4%/1.3% paired speedups; N256 has 5.8%/0.1%, with a group-size change in the first pair. No greater-than-2% latency improvement reproduces in both paired comparisons.
- Native hot-cache best-candidate decode F4/F8 geometric means are 0.9997725× (EP4) and 1.0001833× (EP8), effectively tied. No matched decode candidate improves by more than 2% in the aggregated native hot scores. F8 loses all eight matched hot prefill candidates at EP4 4K/8K and EP8 4K/8K/16K. See [HOT_SCORE_ANALYSIS.md](HOT_SCORE_ANALYSIS.md).
- The apparent first-pass EP8 N8 win did not reproduce: F8 changed from 122.1605 to 133.1365 µs with the same non-flag winner. The final pooled result favors F4. Source tracing also finds that these smallest workloads do not fill either flag batch; both publish via the tail flush. This rules out earlier batch-threshold firing as the explanation, without excluding compiler, layout, cache, or system effects; see [SOURCE_AUDIT.md](SOURCE_AUDIT.md).
- A post-hoc choice of the faster pooled arm for every decode row would yield only 0.2167% (EP4) / 0.2881% (EP8) geometric speedup over F4. That is an optimistic estimate from these measurements, **not a measured joint 16-candidate AUTO result**. The evidence does not justify doubling the current eight-candidate search.

## Evidence and limits

- All eight sweep/controller exits passed. The source and frozen runtime helpers remained unchanged, with the same node/boot/GPU identities for all four arms within each EP. Inputs, routes, weights, and non-flag candidate fields match across arms.
- Preserved 10,400 rank-MAX samples, 62,400 raw per-rank activity spans, and 49,920 native hot candidate-event samples. Every native winner matches the recorded collective candidate scores.
- All 624 untimed measured-winner rank-output checks were finite and repeat-bit-equal. For every token row in each EP, output hashes match across all four runs. These checks are not an independent numerical reference, all-candidate accuracy test, or validation of every timed graph replay. No full numerical suite, sanitizer, Nsight profiling, or joint F4/F8 AUTO benchmark was run for this experiment.
- [Complete results and selected tactics](final-performance.md), [machine-readable results](final-performance.json), [independent review](INDEPENDENT_RESULT_REVIEW.json), and [reproduction instructions](README.md). Raw archives and validation receipts are in `completed-sweeps/`, with extracted evidence in `evidence/`.
- Scope: this workload and runtime only. No claim is made that F8 cannot help another model shape or pipeline.

Both experiment devboxes were released after local archive verification and idle post-run identity checks. Deletion receipts: `ep4-devbox-deletion-receipt.json` and `ep8-runtime/deletion-receipt.json`.
