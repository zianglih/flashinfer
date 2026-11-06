# Independent final table audit

PASS: all six current public tables contain the full 13-token grid and the exact clean retained source `74388819899d0abfd1a12102f7cc108bda13c812` (87 pinned files unchanged before/after). The audit verified 377 displayed latency/TFLOPS cells, 208 displayed ratios, 39 NV winners, unsupported-arm N/As, all saved native AUTO tactics, and shared route identities between each model's two families. All 117 inputs and ratios in the separately produced summary agree.

The methodology is 10 warmups/100 iterations, cold L2, CUDA graphs/CUPTI, fresh native AUTO, no fused CuTe finalize or communication. NV initial activation quantization is included for quantized-input arms; W4A16/BF16 intrinsically have no input quantizer. MX initial quantization remains outside timing. Recipe scopes restore after each arm. All ratios are from the same family/model/GPU sweep; tokens 1 and 2 are displayed but excluded from aggregates.

| CuTe W4A4 vs TRTLLM NVFP4 | Decode GM | Prefill GM | Overall GM |
|---|---:|---:|---:|
| V3 | 1.044845× | 1.127349× | 1.066728× |
| V41-Flash | 1.029149× | 1.067118× | 1.039368× |
| Kimi K3 | 0.995638× | 1.060011× | 1.012797× |

These are single-sweep measurements, not a stability claim. K3 W4A4 at 512 tokens is 0.964820×. Matched MXFP8 also has losing points, including V41 at 128 tokens (0.971386×). K3 TRT MXFP8, per-token SiTU and BF16 remain unsupported, with no fabricated denominator.

Per-token comparisons remain distinct: CuTe per-token versus TRT per-token overall is 1.027816× for V3 and 0.997460× for V41; K3 has no supported TRT per-token arm. The displayed NV table's per-token ratios instead use standard TRT NVFP4 as explicitly labeled.

The final plain observer captures native medians and selected v4/outer-five tactics; it does **not** record actual core forwarding. The byte-identical R5 five-token screen separately verifies 60 actual host calls, while the 72 replay gate proves effective scheduling for its bounded cases. This separation is preserved in `review.json`.

Reproduce this CPU-only audit from the project root with:

```bash
python3 evidence/generality-final-74388819-independent/audit.py
```

No source edits, GPU runs, or raw-evidence changes were made.
