# FC1 scale transport: no simple direct-TMA replacement

Read-only audit of retained fork source `f63e948564582a487f95900c71ef581b90c3f177` and project-local CUTLASS `91843b71d90737e0a9b86f7d9df213cff5a3526f`. CUDA/PTX constraints checked against CUDA 13.2.1 / PTX 9.2 documentation, matching the running toolkit. No repository edits, compilation, GPU launch, sanitizer or public-layout change.

**Recommendation:** preserve direct 4-byte cp.async placement for FC1 SFB. It fuses the necessary scale-layout permutation into the load. A direct TMA alternative cannot implement the required sub-16-byte permutation under the current public linear SF contract. Wider SIMT global loads are possible only with scattered stores, additional register lifetime and stronger alignment/tail handling; there is no clear instruction-count or simplicity benefit to prototype now. The independent relay-scope experiment remains the smaller synchronization opportunity.

## Current contract

Paths below are relative to `flashinfer-fc1-gather-review/` unless prefixed `references/cutlass/`.

- `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py:337–359`: FC1 accepts linear, byte-valued, contiguous per-token SF, with row length `K / sf_vec_size`. It guarantees only a multiple of four SF bytes; `_run_blockscaled_gemm` passes a four-byte alignment claim at `:147`.
- `blackwell/moe_swap_ab_kernel.py:3493–3514`: route IDs are decoded outside the K loop; each lane owns a four-byte SF word. The existing row permutation gives 32 different shared banks per warp.
- `:3534–3569`: four-byte cp.async moves directly from the selected linear token row into canonical SFB SMEM; its source-size predicate zero-fills invalid route/K positions. Each of the 128 issuing threads contributes completion to the local gather barrier.
- `:1621–1624`: SFB is full-N in each CTA, including two-CTA mode. B payload alone is split across the CTAs. A replacement must not apply the payload half-tile rule to SFB.
- `:2509–2532`: canonical SFB is copied with `tcgen05.cp.32x128b.warpx4` (the DSL `Cp4x32x128bOp`), preserving four-scale words and K/row-bank strides.
- `:2330–2353`: FC2 already uses regular TMA because its producer emits canonical 512-byte SF blocks. This is a different input layout from FC1's public linear SF.

## The exact layout mismatch

For a 128-row atom, let `r` be the logical token row and `s` the scale-byte column. Ignoring stage/outer-row offsets, canonical destination byte offset is:

```
D(r,s) = 16*(r % 32) + 4*(r // 32) + (s % 4) + 512*(s // 4)
```

The source keeps all scale columns of one token adjacent. The destination keeps only four adjacent. For one token, its first 16 source bytes must land at:

```
0..3, 512..515, 1024..1027, 1536..1539
```

Conversely, one 16-byte canonical shared unit contains four bytes each from token rows `r`, `r+32`, `r+64`, `r+96`, which generally select four unrelated source tokens. TMA cannot infer those route IDs from a rectangular descriptor.

`references/cutlass/python/CuTeDSL/cutlass/utils/blockscaled_layout.py:28–54` defines the fixed atom as shape `((32,4),(sf_vec_size,4))`, stride `((16,4),(0,1))`. `proof.py` verifies the address property for 50 width/row/count combinations, canonical disjoint coverage and the current bank-free SF lane map. This is an arithmetic proof, not a descriptor-compilation or hardware test.

## Why TMA interleave/swizzle does not solve it

- A non-interleaved TMA box must have an inner width that is a multiple of 16 bytes. Its outer global strides must also be multiples of 16. A public SF row can have only 4 or 8 bytes; arbitrary row IDs cannot then be represented as an ordinary tensor-map outer coordinate without changing the layout or overfetching adjacent token data. [CUDA 13.2.1 tensor map requirements](https://docs.nvidia.com/cuda/archive/13.2.1/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html).
- Gather4 accepts a 2D tensor, four independent row coordinates and one common K coordinate. It forbids interleave and preserves each row's contiguous transfer unit. Four 4-byte SF fragments cannot become a legal four-row, four-byte-box Gather4. [PTX Gather4 mode](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#tensor-tiled-scatter4-gather4-modes).
- Ordinary TMA swizzles permute 16-byte units. The 128B/32B mode with 8B flip still cannot split a 4-byte SF word from the adjacent word. TMA interleave describes an already interleaved global tensor and requires rank >=3; it is not an arbitrary linear-to-blocked transform, and Gather4 cannot use it. [PTX swizzling modes](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#tensor-swizzling-modes).

Even when a particular SF row is at least 16-byte aligned and wide, a TMA load of its 16 contiguous bytes cannot scatter them into four separated four-byte destinations. A new descriptor per token or different outer strides cannot overcome this inner-unit mismatch.

## Why a different SMEM descriptor does not remove the transform

Changing only the SFB SMEM layout to linear rows allows wider global loads, but the S2T descriptor must then produce the same fixed MMA scale-byte positions. It has no arbitrary four-byte gather/transpose operation.

- `references/cutlass/include/cute/atom/mma_traits_sm100.hpp:129–147`: the S2T source is converted to a **K-major** UMMA source descriptor and recast to `uint128_t` units.
- `references/cutlass/include/cute/arch/mma_sm100_desc.hpp:763–860`: descriptor construction recasts to 128 bits; start/leading/stride fields are expressed in 16-byte units. Supported swizzles preserve these units (or use larger units). It cannot independently address the four words within one unit.
- `references/cutlass/include/cute/atom/copy_traits_sm100.hpp:3760–3788`: the 32x128b source image is copied and broadcast to four TMEM lane groups; broadcast changes replicas, not the four-word order within each source unit.
- The other `tcgen05.cp` shapes change copied lane/column extents and broadcast patterns; the instruction does not expose a general byte/word permutation or a source transpose control. [PTX tcgen05.cp](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-cp).

Thus a row-linear SMEM stage still needs LDS/reorder/tcgen05.st or a separate SMEM transform before canonical S2T. It cannot retain the current one-copy S2T contract merely by changing descriptor strides. This conclusion is scoped to the existing canonical scale contract and legal documented copies; no claim about every possible redesigned MMA/scale-storage algorithm is made.

## What nearby implementations actually do

### Rubin split MoE

`flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py`:

- `:2092–2190`: four SF gather warps load each row's 16 SF bytes with `cp.async.128.cg` into **linear SMEM**. This path is used even with TMA Gather4 payload.
- `:2214–2347`: a separate transform warpgroup reads LDS.128, rearranges words and issues `tcgen05.st.32x32b.x4`, with a separate SF-transform pipeline and TMEM-store publication.
- `:1024–1026,5219`: source explicitly distinguishes always-cp.async SF from the selectable payload transport.

It confirms that widening SF transport trades for a transform/pipeline; it does not demonstrate a direct-TMA solution that fits this task.

### Blackwell MegaMoE

`flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/`:

- `block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:978–988,1008–1081`: FC1 TMA-SFB waits on per-expert canonical-SF readiness and loads preformatted atom-major SF.
- `token_comm_gen_specialized.py:2039–2103,2199–2386`: communication/refine work converts the received plain SF pool into canonical atoms in global memory, then publishes `fc1_sf_ready`.

The mainloop's TMA efficiency is supported by an earlier layout conversion. Importing that contract would add the transform/preparation stage explicitly excluded here.

### CUTLASS blockscaled paths

`references/cutlass/include/cutlass/gemm/collective/sm100_blockscaled_mma_mixed_tma_cpasync_warpspecialized.hpp:392–422` creates global SFA/SFB tensors in `tile_atom_to_shape_SF` format and TMA-copies that format; `:701–725` uses the same canonical S2T copy. The word "mixed" refers to operand transport and does not imply that it accepts linear per-token SF and transforms them through TMA.

## Wider SIMT loads: possible, not currently compelling

A wider LDG can fetch 8/16/32 adjacent scale bytes into registers, followed by 2/4/8 separate 32-bit shared stores. This performs the transpose in the consumer's scatter addresses without a separate SMEM stage, but abandons asynchronous global-to-shared transport and increases memory-instruction count at the same lane ownership. It also extends register liveness and needs a valid stronger alignment/tail contract (current public SF only promises 4-byte granularity).

Source-level memory instruction counts per warp and 128-row block per K stage, before addressing, predicates and synchronization:

| Input mode | Stage K | SF bytes/token/stage | Current cp.async.32 | Hypothetical widest aligned LDG + STS.32 |
|---|---:|---:|---:|---:|
| NVFP4 SF16, K4 | 256 | 16 | 4 | 1 LDG128 + 4 STS = 5 |
| NVFP4 SF16, K8 | 512 | 32 | 8 | 1 LDG256 + 8 STS = 9 |
| MX SF32, K4 | 128 | 4 | 1 | 1 LDG32 + 1 STS = 2 |
| MX SF32, K8 | 256 | 8 | 2 | 1 LDG64 + 2 STS = 3 |

Multiply by four warp issuers and by the number of 128-row SF blocks for the CTA. These are not measured SASS or runtime costs; a compiler may change lowering. Gathering four different tokens' words into wider shared stores would require lane shuffles or another staging mechanism, returning to an ownership/transpose tradeoff. The just-rejected shared-coordinate experiment is already evidence against adding ownership complexity for small instruction savings.

No bounded GPU experiment is proposed from this audit. Keep the fused four-byte copy/placement, reduce proven synchronization costs separately, and revisit wider transport only if a profile shows its issue bandwidth dominates enough to justify an explicit transform design.
