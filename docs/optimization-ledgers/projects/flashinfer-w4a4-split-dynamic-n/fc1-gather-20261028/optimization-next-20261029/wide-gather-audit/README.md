# Wider Gather4 row boxes: direct-MMA legality audit

**Decision: do not implement a wider row-box candidate.** An unswizzled wider box is possible for some element formats, but its destination cannot directly feed the existing K-major MMA B operand. A shared-memory repack would be required. That violates this experiment's goal of reducing issue work without an extra transform.

Audited FlashInfer `374ed4c07ee3a8c30a30026018a96d8f613ac4b5` and CUTLASS `91843b71d90737e0a9b86f7d9df213cff5a3526f`. `source-proof.json` binds the source files and records the CPU row-offset proof. No source edits, GPU work, or performance claim.

## Hardware constraints

Gather4 is 2D and does not support tensor-map interleave. Its four independently indexed rows are four consecutive destination box images. For a non-interleaved tensor map, a swizzled inner box cannot exceed the swizzle span. Box dimensions are limited to 256 elements. These limits come from the CUDA 13.2.2 [Tensor Map API](https://docs.nvidia.com/cuda/archive/13.2.2/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html) and [PTX Gather4 specification](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tensor-tile-scatter4-gather4-modes).

| Operand format | Current gathered K | Row bytes | Largest nonswizzled row at the same descriptor element type | Why it cannot directly replace the current row |
|---|---:|---:|---:|---|
| Packed FP4 | 256 | 128 | 128 B | Already reaches the 256-element limit; payload recasting would not solve MMA layout |
| FP8 | 128 | 128 | 256 B | Wider row stride conflicts with K_INTER |
| BF16 W4A16 | 64 | 128 | 512 B | Wider row stride conflicts with K_INTER |

The FP4 entry uses packed continuous 4-bit elements; the API counts individual values for packed tensor types. No inference here depends on the existence of a different internal payload type.

## K_INTER is not an arbitrary row-major descriptor

The decisive local implementation is `references/cutlass/include/cute/arch/mma_sm100_desc.hpp:830`. `make_umma_desc<Major::K>` recasts to 128-bit units and checks that the first row-mode stride equals the swizzle atom's row stride. For no swizzle this is **one 128-bit unit**, or **16 B**. LBO controls K-block placement; SBO moves the next eight-row group. Neither changes the spacing between row 0 and row 1.

For a 256 B Gather4 box, row starts are `[0, 256, 512, 768]` B. K_INTER requires `[0, 16, 32, 48]` B. This mismatch occurs within the first four rows and cannot be fixed by the descriptor's LBO, SBO, or base address. `source-proof.json` checks this for FP4, FP8, and BF16 and all relevant row widths.

The Python helper independently gives the same result: `references/cutlass/python/CuTeDSL/cutlass/cute/nvgpu/tcgen05/helpers.py:88` constructs K_INTER as `(8, 128 / element_bits)` with a compact K stride. K_SW128 instead uses a 1024-bit contiguous row. Thus the existing 128 B Gather4 rows exactly match the native K_SW128 atom. A legal Gather4-to-K_INTER scheme would gather 16 B rows, requiring eight times as many row/K instructions for the same payload.

Switching to MN-major cannot reinterpret a gathered token-major row as the same B matrix without rearranging data or changing the GEMM semantics. A wider staging buffer followed by shared-memory repacking adds loads, stores, a destination buffer and ordering. A row-linear 256/512 B buffer also aliases shared banks for simultaneous fixed-K accesses across rows; that is a warning about a possible repack access pattern, not a claim that every legal K_INTER access has bank conflicts. No performance estimate is made.

## K96 is a second independent restriction

The PTX absolute-LBO mode used for the 48-byte K96 FP4 instruction requires K-major, SW128 with 16-byte atomicity, and base offset zero. It is not a way to relax the native layout into K_INTER. See the [PTX shared-memory descriptor and LBO rules](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html).

Local implementation evidence:

- `references/cutlass/include/cute/atom/mma_traits_sm100.hpp:3720`: the SM103 implementation enables absolute LBO and points it at the next K segment.
- `flashinfer-fc1-gather-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:203`: `_blockscaled_dynamic_mma` preserves SW128, computes the current/next K segment descriptors, and requires aligned row-zero offsets.
- Its `gather_layout` at line 2310 and W4A16's at `moe_w4a16_kernel.py:985` both create the one-row SW128 tensor map. Larger pipeline K tiles remain multiple native swizzle slabs, not one wider contiguous destination row.

## Existing Rubin and MegaMoE designs agree

- `flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:997` uses a one-row SW128 Gather4 destination to match native UMMA K_SW128.
- `flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:257` explicitly requires exactly 128 B per gathered row. It explains that larger native B stages split K into interleaved chunks that cannot be addressed by one flat Gather4 base.

These are architectural-layout choices, not a model or dtype performance heuristic. Keep the current 128 B row geometry and four issuers. Seek savings in coordinate/control work or provably unused transactions, rather than bypassing this layout constraint.
