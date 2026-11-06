# CuTe DSL W4A4 per-tensor versus archived TRTLLM W4A4

Indicative cross-campaign comparison, not a controlled speedup measurement.

- CuTe: published PR7290 table, measured source 442d2aa53f68b4640c3ab5118a76f1599ff60d34. B200, initial activation quantization excluded, deterministic standalone combine. Candidate latency = geometric mean of A1 and A2 native medians.
- TRTLLM: PR5301 corrected per-tensor table, source 964f6fd2a582da1a7b57b5c20e3872caea80f693. B300, initial activation quantization included, native finalize. Median of three native medians.
- Both: D7168/E2048, 256 total/32 local experts, top-k8, simulated EP8/TP1 on one GPU; no inter-GPU communication. 10 warmups, 100 cold-L2 CUDA-graph CUPTI samples per sweep. Different software and campaigns.
- PR7290 fetched head is 98fd3566b5f945c100f48cddacf25deb2432cbc2; published performance table still names 442d2aa. Do not attribute these measurements to the newer head.
- Ratio = TRTLLM latency / CuTe latency; greater than 1 favors CuTe. Tokens1/2 excluded from aggregates.

| Tokens | CuTe DSL (µs) | TRTLLM (µs) | Ratio |
|---:|---:|---:|---:|
| 1 | 25.256 | 26.080 | 1.0326× |
| 2 | 33.008 | 39.280 | 1.1900× |
| 4 | 47.400 | 50.049 | 1.0559× |
| 8 | 63.368 | 65.120 | 1.0276× |
| 16 | 73.688 | 75.041 | 1.0184× |
| 32 | 110.991 | 106.034 | 0.9553× |
| 64 | 140.389 | 139.970 | 0.9970× |
| 128 | 139.784 | 143.601 | 1.0273× |
| 256 | 148.591 | 153.873 | 1.0355× |
| 512 | 150.592 | 163.618 | 1.0865× |
| 4096 | 206.112 | 308.483 | 1.4967× |
| 8192 | 305.071 | 384.019 | 1.2588× |
| 16384 | 533.837 | 622.581 | 1.1662× |

Decode geometric-mean ratio: 1.024801× (+2.48%).

Prefill geometric-mean ratio: 1.300036× (+30.00%).

Sources: https://github.com/flashinfer-ai/flashinfer/pull/7290 and https://github.com/flashinfer-ai/flashinfer/pull/5301
