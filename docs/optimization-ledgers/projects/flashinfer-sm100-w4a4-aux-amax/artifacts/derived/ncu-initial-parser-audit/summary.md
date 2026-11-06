# NCU aux-amax action comparison

The off/on labels are assigned by the input-directory contract. Action selection itself is fail-closed on the full NCU kernel name and is verified across the details and raw exports.

Global byte counts are L1TEX sector traffic (`sectors * 32 bytes`), not logical payload bytes or DRAM traffic.

| arm | action | variant | duration | instructions | regs/thread | local spill bytes | global load sectors / bytes | global store sectors / bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| off | gemm1 | aux_off | 106.624 us | 20,990,020 | 168 | 0 | 13,413,908 / 429,245,056 B | 0 / 0 B |
| off | quant | legacy | 120.416 us | 110,021,983 | 51 | 0 | 21,003,264 / 672,104,448 B | 2,645,760 / 84,664,320 B |
| on | gemm1 | aux_on | 107.392 us | 22,321,824 | 154 | 0 | 13,413,876 / 429,244,032 B | 131,072 / 4,194,304 B |
| on | quant | input_amax | 85.728 us | 74,288,056 | 48 | 0 | 10,664,448 / 341,262,336 B | 2,645,760 / 84,664,320 B |

## Derived serialized comparison

These sums describe GEMM1 plus intermediate quantization in isolation; they do not claim CUDA-graph critical-path improvement when kernels overlap.

| metric | value |
|---|---:|
| GEMM1 aux overhead | 0.768 us (0.72%) |
| Quant latency saved | 34.688 us |
| Quant speedup | 1.4046x (28.81% reduction) |
| Serialized off | 227.040 us |
| Serialized on | 193.120 us |
| Serialized net saved | 33.920 us |
| Serialized speedup | 1.1756x (14.94% reduction) |

## Selected kernel identities

Full names and SHA-256 values are retained in `actions.csv` and `summary.json`.

- off/gemm1 ID 5, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- off/quant ID 7, name SHA-256 `6f9f42b17245b56870fc9be540dd6dbfe0f318ac8661fe5b4ffa8ab34a38dcf0`: `kernel_cutlass_kernel_flashinferquantizationkernelsnvfp4_quantizeNVFP4QuantizePer...`
- on/gemm1 ID 5, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- on/quant ID 7, name SHA-256 `6f9f42b17245b56870fc9be540dd6dbfe0f318ac8661fe5b4ffa8ab34a38dcf0`: `kernel_cutlass_kernel_flashinferquantizationkernelsnvfp4_quantizeNVFP4QuantizePer...`
