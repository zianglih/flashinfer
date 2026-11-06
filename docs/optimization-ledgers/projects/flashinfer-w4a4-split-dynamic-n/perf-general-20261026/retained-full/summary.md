# Final A public benchmark status

Source `0def601d` + patch `8828ab24d607c27905ab6b53e19ad278869fd84655f1d96b289e43eb0bdcd03b`. All 6 tables / 78 rows / 208 printed ratios validated against native medians and source receipts. Tokens 1/2 are excluded below.

The fresh 0def601d controls and final A use different GPU assignments on the same host. Changes below describe full native-AUTO sweeps; same-GPU fixed-tactic CAAC evidence is recorded separately. Matching TRTLLM ratios use final A’s own public table. Both per-token arms share the changed standalone initial quantizer; their intermediate quantization remains backend-specific.

| Model | Format | Change vs 0def: decode | Change vs 0def: prefill | Speedup vs matching TRT: decode | Speedup vs matching TRT: prefill | Slower than TRT token counts |
|---|---|---:|---:|---:|---:|---|
| v3 | NVFP4 W4A4 | 1.0073x | 1.0033x | 1.0492x | 1.1324x | None |
| v3 | NVFP4 per-token | 1.0099x | 1.1562x | 1.0763x | 1.0910x | None |
| v3 | MXFP4x8 | 1.0063x | 0.9916x | 1.0570x | 1.0649x | None |
| v3 | MXFP8 | 1.0048x | 0.9901x | 1.0293x | 1.0403x | 64 |
| v41-flash | NVFP4 W4A4 | 1.0055x | 1.0016x | 1.0269x | 1.0661x | None |
| v41-flash | NVFP4 per-token | 1.0137x | 1.0941x | 1.0495x | 1.0006x | 8192 |
| v41-flash | MXFP4x8 | 1.0032x | 0.9937x | 1.0398x | 1.0432x | 16384 |
| v41-flash | MXFP8 | 1.0054x | 0.9914x | 1.0065x | 1.0199x | 32, 64, 128, 256, 512 |
| kimi-k3 | NVFP4 W4A4 | 0.9990x | 0.9898x | 0.9967x | 1.0651x | 16, 32, 64, 128, 256, 512 |
| kimi-k3 | NVFP4 per-token | 1.0297x | 1.2659x | N/A | N/A | TRTLLM activation unsupported |
| kimi-k3 | MXFP4x8 | 1.0072x | 1.0205x | 1.0025x | 1.1522x | 32, 64, 128, 256, 512 |
| kimi-k3 | MXFP8 | 1.0002x | 1.0089x | N/A | N/A | TRTLLM activation unsupported |

All speedups use baseline latency / candidate latency; above 1 is faster. The detailed JSON preserves every token and backend, normalized TRT ratios, and raw latency differences.
