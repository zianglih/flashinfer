# NCU aux-amax action comparison

The off/on labels are assigned by the input-directory contract. Action selection itself is fail-closed on the full NCU kernel name and is verified across the details and raw exports.

Global byte counts are L1TEX sector traffic (`sectors * 32 bytes`), not logical payload bytes or DRAM traffic.

| arm | action | variant | duration | instructions | regs/thread | local spills: req / bytes / ld+st inst | global load sectors / bytes | global store sectors / bytes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| off | gemm1 | aux_off | 139.744 us | 20,969,356 | 168 | 0 / 0 B / 0+0 | 13,413,844 / 429,243,008 B | 0 / 0 B |
| off | quant | legacy | 82.976 us | 31,423,488 | 26 | 0 / 0 B / 0+0 | 20,985,356 / 671,531,392 B | 2,645,760 / 84,664,320 B |
| on | gemm1 | aux_on | 140.128 us | 21,247,300 | 168 | 24,576 / 24,576 B / 24,576+0 | 13,413,860 / 429,243,520 B | 16,384 / 524,288 B |
| on | quant | input_amax | 21.024 us | 4,357,952 | 31 | 0 / 0 B / 0+0 | 2,129,411 / 68,141,152 B | 532,480 / 17,039,360 B |

## Derived serialized comparison

These sums describe GEMM1 plus intermediate quantization in isolation; they do not claim CUDA-graph critical-path improvement when kernels overlap.

| metric | value |
|---|---:|
| GEMM1 aux overhead | 0.384 us (0.27%) |
| Quant latency saved | 61.952 us |
| Quant speedup | 3.9467x (74.66% reduction) |
| Serialized off | 222.720 us |
| Serialized on | 161.152 us |
| Serialized net saved | 61.568 us |
| Serialized speedup | 1.3820x (27.64% reduction) |

## Selected kernel identities

Full names and SHA-256 values are retained in `actions.csv` and `summary.json`.

- off/gemm1 ID 0, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- off/quant ID 1, name SHA-256 `6f9f42b17245b56870fc9be540dd6dbfe0f318ac8661fe5b4ffa8ab34a38dcf0`: `kernel_cutlass_kernel_flashinferquantizationkernelsnvfp4_quantizeNVFP4QuantizePer...`
- on/gemm1 ID 0, name SHA-256 `f25fec95a0eb5839020725b05b8aa0b330f65e3090248a0b7ff88c4266e0f385`: `kernel_cutlass_kernel_flashinferfused_moecute_dslblackwellblockscaled_contiguous_...`
- on/quant ID 1, name SHA-256 `a33ecf046e16294c8d369c9d1c67cc89035d0c4ed089d284e53b8d809c2f5514`: `kernel_cutlass_kernel_with_input_amax_flashinferquantizationkernelsnvfp4_quantize...`
