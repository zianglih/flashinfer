# NCU aux-amax action comparison

The off/on labels are assigned by the input-directory contract. Action selection itself is fail-closed on the full NCU kernel name and is verified across the details and raw exports.

Global byte counts are L1TEX sector traffic (`sectors * 32 bytes`), not logical payload bytes or DRAM traffic.

| arm | action | variant | duration | instructions | regs/thread | local spills: req / bytes / ld+st inst | global load sectors / bytes | global store sectors / bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| off | gemm1 | aux_off | 142.560 us | 20,969,030 | 168 | 0 / 0 B / 0+0 | 13,413,876 / 429,244,032 B | 0 / 0 B |
| off | quant | legacy | 217.248 us | 110,021,983 | 51 | 0 / 0 B / 0+0 | 21,003,264 / 672,104,448 B | 2,645,760 / 84,664,320 B |
| on | gemm1 | aux_on | 138.688 us | 21,247,344 | 168 | 24,576 / 24,576 B / 24,576+0 | 13,413,796 / 429,241,472 B | 16,384 / 524,288 B |
| on | quant | input_amax | 29.120 us | 7,757,934 | 60 | 0 / 0 B / 0+0 | 2,133,888 / 68,284,416 B | 532,480 / 17,039,360 B |

## Derived serialized comparison

These sums describe GEMM1 plus intermediate quantization in isolation; they do not claim CUDA-graph critical-path improvement when kernels overlap.

| metric | value |
|---|---:|
| GEMM1 aux overhead | -3.872 us (-2.72%) |
| Quant latency saved | 188.128 us |
| Quant speedup | 7.4604x (86.60% reduction) |
| Serialized off | 359.808 us |
| Serialized on | 167.808 us |
| Serialized net saved | 192.000 us |
| Serialized speedup | 2.1442x (53.36% reduction) |

## Selected kernel identities

Full names and SHA-256 values are retained in `actions.csv` and `summary.json`.

- off/gemm1 ID 0, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- off/quant ID 1, name SHA-256 `6f9f42b17245b56870fc9be540dd6dbfe0f318ac8661fe5b4ffa8ab34a38dcf0`: `kernel_cutlass_kernel_flashinferquantizationkernelsnvfp4_quantizeNVFP4QuantizePer...`
- on/gemm1 ID 0, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- on/quant ID 1, name SHA-256 `a33ecf046e16294c8d369c9d1c67cc89035d0c4ed089d284e53b8d809c2f5514`: `kernel_cutlass_kernel_with_input_amax_flashinferquantizationkernelsnvfp4_quantize...`
