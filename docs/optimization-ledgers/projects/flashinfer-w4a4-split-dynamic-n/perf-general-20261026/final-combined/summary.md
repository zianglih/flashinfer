# Final mixed-source public benchmark summary

Matching TRTLLM ratios use each final same-sweep table. Comparisons with fresh 0def are descriptive native-AUTO sweeps, not same-GPU causal CAAC. The per-token arms share the timed initial quantizer; TRTLLM per-token is not implementation-unchanged.

All six outputs / 78 rows / 208 printed ratios are source-pinned and validated. Tokens 1/2 are excluded below.

| Model | Format | vs 0def decode | vs 0def prefill | vs TRT decode | vs TRT prefill | Slower than TRT tokens |
|---|---|---:|---:|---:|---:|---|
| v3 | NVFP4 W4A4 | 1.0043x | 1.0008x | 1.0488x | 1.1364x | None |
| v3 | NVFP4 per-token | 1.0089x | 1.1757x | 1.0720x | 1.0982x | None |
| v3 | MXFP4x8 | 1.0068x | 1.0073x | 1.0512x | 1.0568x | None |
| v3 | MXFP8 | 1.0047x | 1.0141x | 1.0312x | 1.0384x | 32 |
| v41-flash | NVFP4 W4A4 | 1.0125x | 0.9995x | 1.0357x | 1.0712x | None |
| v41-flash | NVFP4 per-token | 1.0221x | 1.1418x | 1.0546x | 1.0337x | None |
| v41-flash | MXFP4x8 | 1.0072x | 1.0060x | 1.0409x | 1.0574x | None |
| v41-flash | MXFP8 | 1.0147x | 0.9882x | 1.0128x | 1.0197x | 32, 64, 128, 256, 512 |
| kimi-k3 | NVFP4 W4A4 | 1.0057x | 0.9983x | 1.0029x | 1.0766x | 16, 32, 64, 512 |
| kimi-k3 | NVFP4 per-token | 1.0439x | 1.2984x | N/A | N/A | TRT activation unsupported |
| kimi-k3 | MXFP4x8 | 1.0081x | 0.9978x | 1.0074x | 1.1401x | 32, 64, 128, 256, 512 |
| kimi-k3 | MXFP8 | 1.0075x | 1.0104x | N/A | N/A | TRT activation unsupported |
