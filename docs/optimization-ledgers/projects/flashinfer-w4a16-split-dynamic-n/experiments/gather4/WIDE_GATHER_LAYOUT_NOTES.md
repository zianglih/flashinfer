# Can non-swizzled Gather4 transfer K256 BF16 rows?

Research conclusion: **the tensor-map transfer is legal in isolation, but simply changing the MMA layout to K_INTER does not make its output consumable by TCGen05.** The blocker is the canonical MMA row layout, not merely a possible bank-conflict penalty. No production change or GPU test was made.

## Tensor map

A 2D BF16 tensor map with box `{256,1}`, no interleave and no swizzle satisfies the documented dimensional constraints: box dimensions are at most 256 elements and the inner byte count is a multiple of 16. The 128-byte inner-box cap applies when 128B swizzle is enabled. Gather4 requires four row coordinates and a one-element second box dimension; it does not support TensorMap interleave. Thus one hypothetical request would place four contiguous 512-byte rows, transferring 2048 bytes and replacing four of our current requests at the TMA level. [CUDA 13.2 tensor-map API](https://docs.nvidia.com/cuda/archive/13.2.0/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html), [CUDA 13.2 Gather4 semantics](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#tensor-tiled-scatter4-gather4).

## TCGen05 layout

Official CUTLASS `main` was inspected at **91843b71d90737e0a9b86f7d9df213cff5a3526f** (October 20, 2026; v4.8.1 update). This is primary-source research, not confirmation of the exact installed benchmark package's implementation.

- The SM100 enum exposes `K_INTER`, `K_SW32`, `K_SW64`, `K_SW128`, alongside MN-major forms. [Python enum](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/python/CuTeDSL/cutlass/cute/nvgpu/tcgen05/mma.py#L3691-L3710).
- SM100 aliases the existing canonical K_INTER layout atom. [C++ aliases](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/include/cute/atom/mma_traits_sm100.hpp#L58-L71).
- The descriptor's no-swizzle encoding is zero. Its K-major canonical layout in 128-bit units is `((8,n),2):((1,SBO),LBO)`: the first eight matrix rows have fixed 16-byte stride. The leading and outer strides do not let that inner row stride become 512 bytes. CUTLASS explicitly asserts `stride_00 == SwizzleAtomMNSize`, which is 1 for no-swizzle. [Descriptor enum](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/include/cute/arch/mma_sm100_desc.hpp#L82-L88), [canonical-stride checks](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/include/cute/arch/mma_sm100_desc.hpp#L827-L858).

For BF16, a canonical K_INTER region groups eight rows' 16-byte K fragments together, then uses a configurable leading offset for the next K fragment. A no-swizzle Gather4 box K256 instead places each512-byte row contiguously. Those layouts disagree immediately at row 1: offset 16 bytes versus 512 bytes. Making a custom arbitrary row-major CuTe layout does not remove the hardware descriptor constraint.

The `INTER` in CUTLASS's MMA layout name is not a request to enable TensorMap interleave; Gather4 explicitly forbids the latter. A wide gather could first populate a temporary row-major buffer followed by rearrangement, but that adds a separate data-movement stage and storage. It is no longer the proposed direct gather-to-MMA layout. A representation or algorithm change would need separate justification.

## FlashMLA comparison

The closest FlashMLA BF16 implementation uses box `{64,1}`, 128B swizzle and 256B L2 promotion, then emits one Gather4 for each 64-BF16 channel chunk. Its shared layout is `Layout_K_SW128_Atom<bf16>`. It amortizes index and issue work through dedicated elected issuers, not through 512-byte BF16 rows. [Pinned descriptor](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L663-L684), [shared layout](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/config.h#L53-L80).

Recommendation: prioritize issuer/index movement and existing-CTA work distribution before pursuing a wide non-swizzled row layout. The direct K_INTER proposal fails the documented canonical layout contract.
