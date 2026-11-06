# Final f7182d5c backend comparison

Full-precision TRTLLM / CuTe DSL median ratios; above 1 favors CuTe DSL. Tokens 1/2 are excluded. These are fresh native AUTO tables, not paired before/after measurements.

| Model / format | Decode | Prefill | All |
|---|---:|---:|---:|
| V3 EP8 / NVFP4 W4A4 | 1.0445x | 1.1295x | 1.0671x |
| V3 EP8 / NVFP4 per-token | 1.0735x | 1.0978x | 1.0801x |
| V3 EP8 / MXFP4x8 | 1.0524x | 1.0738x | 1.0582x |
| V3 EP8 / MXFP8 | 1.0424x | 1.0063x | 1.0324x |
| V4.1-Flash EP4 / NVFP4 W4A4 | 1.0385x | 1.0506x | 1.0418x |
| V4.1-Flash EP4 / NVFP4 per-token | 1.0583x | 1.0302x | 1.0506x |
| V4.1-Flash EP4 / MXFP4x8 | 1.0479x | 1.0617x | 1.0516x |
| V4.1-Flash EP4 / MXFP8 | 1.0135x | 1.0171x | 1.0145x |
| Kimi K3 EP8 / NVFP4 W4A4 | 1.0146x | 1.0757x | 1.0309x |
| Kimi K3 EP8 / NVFP4 per-token | N/A | N/A | N/A |
| Kimi K3 EP8 / MXFP4x8 | 1.0148x | 1.1683x | 1.0546x |
| Kimi K3 EP8 / MXFP8 | N/A | N/A | N/A |

Remaining observed gaps:

- V3 EP8 MXFP8: slower at tokens 8192; worst T8192 0.9586x (481.604 vs 461.653 µs).
- V4.1-Flash EP4 MXFP8: slower at tokens 32, 64, 128, 256, 512; worst T128 0.9866x (461.315 vs 455.124 µs).
- Kimi K3 EP8 NVFP4 W4A4: slower at tokens 16, 64, 512; worst T64 0.9900x (237.762 vs 235.379 µs).
- Kimi K3 EP8 NVFP4 per-token: N/A; TRTLLM backend does not support K3 SiTU.
- Kimi K3 EP8 MXFP4x8: slower at tokens 32, 64, 128, 256, 512; worst T64 0.9843x (230.930 vs 227.314 µs).
- Kimi K3 EP8 MXFP8: N/A; TRTLLM backend does not support K3 SiTU.

Per-token rows compare matching per-token recipes. K3's public per-token-vs-standard-NVFP4 ratio remains in the raw table but is a different quantization contract. Decode covers 4–512; prefill covers 4096/8192/16384. One sweep does not establish statistical stability.
