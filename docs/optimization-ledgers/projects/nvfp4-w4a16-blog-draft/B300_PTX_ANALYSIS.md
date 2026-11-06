# B300 NVFP4 MMA audit

Verified 2026-10-07 against NVIDIA PTX ISA 9.4 and NVIDIA CUTLASS commit `0b55a2f691d69981583568fd9eb69687b1f0de8a`.

## Suggested article wording

All of these benchmarks run on B300, where native NVFP4 has an especially strong hardware advantage. Blackwell Ultra adds a wider dense NVFP4 MMA: `tcgen05.mma.cta_group::1.kind::mxf4nvf4.block_scale.block16` can consume **K=96**, versus **K=64** on B200. That is 50% more multiply-accumulate work for the same output tile per instruction, consistent with NVIDIA's advertised **1.5× dense NVFP4 throughput**. W4A16's decode gains therefore appear on hardware that gives native FP4 computation more room to win. [PTX matrix shapes and architecture restrictions](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-matrix-shape), [NVIDIA Blackwell Ultra architecture article](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/).

## Instruction details

Illustrative single-CTA spelling:

```ptx
tcgen05.mma.cta_group::1.kind::mxf4nvf4.block_scale.block16
    [d_tmem], a_desc, b_desc, idesc,
    [scale_a_tmem], [scale_b_tmem], enable_input_d;
```

This is a **dense** instruction, with no `.sp`. For NVFP4, the descriptor selects E2M1 operands, UE4M3 block scales and FP32 accumulation. `.block16` supplies six scales along K=96, versus four along K=64. For this single-CTA form M=128. K is selected by descriptor bit 31 (0→64, 1→96), **not** a `.k96` mnemonic suffix. K=96 requires `sm_103a` for B300; B200's `sm_100a` does not support it. PTX 8.8 introduced this extension. [Syntax](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-mma-instructions-mma), [descriptor](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-instruction-descriptor), [K=96 target restriction](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-matrix-shape-target-isa-note).

NVIDIA's CUTLASS `SM103_MXF4_ULTRA_SS_VS` emits this exact instruction for vector size 16. Its `SM103MmaMXF4NVF4Op` explicitly selects instruction K=96, E2M1 inputs, FP32 output, and scale-vector size 16. These are source-level corroboration, not the compiled output of our benchmark binaries. [C++ emission](https://github.com/NVIDIA/cutlass/blob/0b55a2f691d69981583568fd9eb69687b1f0de8a/include/cute/arch/mma_sm100_umma.hpp#L1902-L1966), [CuTe DSL operation](https://github.com/NVIDIA/cutlass/blob/0b55a2f691d69981583568fd9eb69687b1f0de8a/python/CuTeDSL/cutlass/cute/nvgpu/tcgen05/mma.py).

The B200→SM100 / B300→SM103 mapping is independently documented in the [CUTLASS GPU support table](https://docs.nvidia.com/cutlass/4.5.1/overview.html#minimum-requirements).

## Interpretation limits

- The K ratio proves **work per instruction at fixed M and N**, not instruction latency or end-to-end speedup. Cite NVIDIA's independent dense-throughput claim alongside the ISA detail. Do not write that the ISA alone guarantees an identical issue rate or latency.
- The public architecture article's headline peaks are chip-family capabilities and SKU-dependent; keep the article's relative 1.5× claim instead of copying absolute 15 PFLOPS into a claim about the specific B300 test SKU without matching its spec.
- W4A16 does not use the NVFP4 MMA; this paragraph describes the native W4A4 hardware opportunity it competes against.
- This audit did not inspect generated PTX/SASS from the article's W4A4 benchmark binaries. Do not claim that every measured baseline actually issues K=96. B300 can also run older K=64 kernels.

## Local source snapshots

- `evidence/ptx-isa-9.4.html`
- `evidence/tcgen05-mma-instructions-mma.txt`
- `evidence/tcgen05-matrix-shape.txt`
- `evidence/tcgen05-instruction-descriptor.txt`
- `evidence/mma_sm100_umma.hpp`
- `evidence/cutlass-tcgen05-mma.py`
- `evidence/cutlass-tcgen05-source-url.txt`
