# Fresh performance status at 0def601d

Six public tables on B300 / CUDA 13.2, source `0def601d`. Ratios are matching TRTLLM latency divided by CuTe latency. Tokens 1 and 2 were measured and excluded from these aggregates. NV includes initial activation quantization. This is current status, not a paired implementation comparison.

| Model | Matching format | Decode geomean | Prefill geomean | All geomean | Slower token counts |
|---|---|---:|---:|---:|---|
| v3 | NVFP4 W4A4 | 1.0518× | 1.1310× | 1.0728× | None |
| v3 | NVFP4 per-token | 1.0598× | 0.9382× | 1.0252× | 4096, 8192, 16384 |
| v3 | MXFP4x8 | 1.0492× | 1.0583× | 1.0517× | None |
| v3 | MXFP8 | 1.0319× | 1.0458× | 1.0357× | 32 |
| v41-flash | NVFP4 W4A4 | 1.0212× | 1.0725× | 1.0349× | None |
| v41-flash | NVFP4 per-token | 1.0338× | 0.9156× | 1.0002× | 128, 256, 4096, 8192, 16384 |
| v41-flash | MXFP4x8 | 1.0335× | 1.0635× | 1.0416× | None |
| v41-flash | MXFP8 | 0.9979× | 1.0355× | 1.0081× | 32, 64, 128, 256, 512 |
| kimi-k3 | NVFP4 W4A4 | 0.9975× | 1.0668× | 1.0159× | 16, 32, 64, 256, 512 |
| kimi-k3 | NVFP4 per-token | N/A | N/A | N/A | TRTLLM activation unsupported |
| kimi-k3 | MXFP4x8 | 0.9961× | 1.1339× | 1.0319× | 32, 64, 128, 256, 512 |
| kimi-k3 | MXFP8 | N/A | N/A | N/A | TRTLLM activation unsupported |

## Largest remaining latency gaps

- v41-flash NVFP4 per-token, 8192 tokens: 0.8867×; CuTe latency 12.78% higher (+67.696 µs).
- v41-flash NVFP4 per-token, 16384 tokens: 0.9124×; CuTe latency 9.60% higher (+81.457 µs).
- v3 NVFP4 per-token, 4096 tokens: 0.9285×; CuTe latency 7.71% higher (+21.200 µs).
- v3 NVFP4 per-token, 8192 tokens: 0.9379×; CuTe latency 6.62% higher (+27.856 µs).
- v3 NVFP4 per-token, 16384 tokens: 0.9483×; CuTe latency 5.45% higher (+41.360 µs).
- v41-flash NVFP4 per-token, 4096 tokens: 0.9488×; CuTe latency 5.39% higher (+22.929 µs).
- kimi-k3 MXFP4x8, 64 tokens: 0.9688×; CuTe latency 3.22% higher (+7.311 µs).
- v41-flash MXFP8, 128 tokens: 0.9725×; CuTe latency 2.83% higher (+12.864 µs).
- kimi-k3 NVFP4 W4A4, 64 tokens: 0.9750×; CuTe latency 2.57% higher (+6.048 µs).
- v41-flash MXFP8, 64 tokens: 0.9767×; CuTe latency 2.38% higher (+8.289 µs).
- v41-flash MXFP8, 256 tokens: 0.9771×; CuTe latency 2.34% higher (+12.337 µs).
- kimi-k3 MXFP4x8, 128 tokens: 0.9781×; CuTe latency 2.24% higher (+6.463 µs).
