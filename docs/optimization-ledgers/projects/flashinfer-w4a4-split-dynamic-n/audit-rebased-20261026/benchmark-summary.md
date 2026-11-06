# Fresh eb141478 benchmark summary

Completed tables: **6/6**. Measured source: `eb141478505103f4bc65d10fb655f3deb3cd71dc`.
Ratios use full-precision native medians: TRTLLM / CuTe DSL; >1 means CuTe DSL is faster. Geometric means exclude tokens 1/2. Decode: 4–512; prefill: 4096/8192/16384.

| Model | Matching comparison | Decode | Prefill | All |
|---|---|---:|---:|---:|
| V3 EP8 | NVFP4 W4A4 | 1.0417x | 1.1319x | 1.0656x |
| V3 EP8 | NVFP4 per-token | 1.0630x | 0.9395x | 1.0278x |
| V3 EP8 | MXFP4x8 | 1.0485x | 1.0712x | 1.0547x |
| V3 EP8 | MXFP8 | 1.0333x | 1.0505x | 1.0380x |
| V4.1-Flash EP4 | NVFP4 W4A4 | 1.0282x | 1.0634x | 1.0377x |
| V4.1-Flash EP4 | NVFP4 per-token | 1.0256x | 0.9169x | 0.9948x |
| V4.1-Flash EP4 | MXFP4x8 | 1.0298x | 1.0607x | 1.0381x |
| V4.1-Flash EP4 | MXFP8 | 1.0028x | 1.0215x | 1.0078x |
| Kimi K3 EP8 | NVFP4 W4A4 | 0.9981x | 1.0672x | 1.0165x |
| Kimi K3 EP8 | NVFP4 per-token | N/A | N/A | N/A |
| Kimi K3 EP8 | MXFP4x8 | 1.0013x | 1.1423x | 1.0379x |
| Kimi K3 EP8 | MXFP8 | N/A | N/A | N/A |

The public NV table additionally compares CuTe per-token with standard TRTLLM NVFP4 (a different activation-quantization contract):

| Model | Decode | Prefill | All |
|---|---:|---:|---:|
| V3 EP8 | 0.9860x | 0.7857x | 0.9268x |
| V4.1-Flash EP4 | 0.9503x | 0.7748x | 0.8988x |
| Kimi K3 EP8 | 0.9231x | 0.6440x | 0.8368x |

## Remaining measured gaps

- V3 EP8, NVFP4 per-token: slower at T4096, 8192, 16384; worst T4096 = 0.9311x (296.818 vs TRT 276.355 µs).
- V3 EP8, MXFP8: slower at T32, 64; worst T64 = 0.9960x (225.619 vs TRT 224.708 µs).
- V4.1-Flash EP4, NVFP4 per-token: slower at T128, 256, 512, 4096, 8192, 16384; worst T8192 = 0.8846x (599.606 vs TRT 530.437 µs).
- V4.1-Flash EP4, MXFP4x8: slower at T128; worst T128 = 0.9991x (260.610 vs TRT 260.386 µs).
- V4.1-Flash EP4, MXFP8: slower at T32, 64, 128, 256, 512; worst T128 = 0.9727x (469.043 vs TRT 456.244 µs).
- Kimi K3 EP8, NVFP4 W4A4: slower at T32, 64, 128, 256, 512; worst T64 = 0.9749x (242.594 vs TRT 236.515 µs).
- Kimi K3 EP8, MXFP4x8: slower at T32, 64, 128, 256, 512; worst T64 = 0.9733x (232.882 vs TRT 226.658 µs).

K3 TRTLLM per-token and homogeneous MXFP8 are unavailable for SiTU; N/A is not an estimated ratio. This is one sweep, not evidence of statistical stability. NV times initial input quantization; MX starts from quantized input. V4.1/K3 routing is precomputed; all results are rank-local without communication. No cross-GPU CuTe before/after ratio is computed. The JSON preserves all 13 raw medians, exact ratios, output/cache hashes, timing/recipe checks, and source bindings.
