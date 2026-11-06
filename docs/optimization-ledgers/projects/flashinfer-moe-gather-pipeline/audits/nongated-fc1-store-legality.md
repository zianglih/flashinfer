# Nongated FC1: join already-owned adjacent output halves

Read-only legality audit; no production edit or GPU work. `nongated-fc1-store-legality.json` records the source hash and210,944 CPU geometry/alignment checks.

**Conclusion:** joining the two converted16-channel halves into one32-channel payload is legal under the existing swap-AB output contract. It does not need a new runtime full/tail branch, new tensor padding, scale-layout change, API restriction, or tactic. Native codegen and numerical qualification remain necessary; this audit does not establish a speedup.

## Ownership and bounds

- `_blockscaled_transpose16x32` gives each lane one token's16 contiguous channels. The nongated path transposes both top and bottom, then writes them to `channel_start + warp*32 + half*16` for the same `output_row` (`moe_swap_ab_kernel.py:929–990`). Therefore these halves are adjacent within a row; they are not the interleaved token ownership of the raw TMEM fragment.
- The gather launcher requires GEMM1 `n%128==0` (`moe_swap_ab.py:398–401`); nongated output channels equal n. Kernel `can_implement` independently requires channel multiples128, and the wrapper assumes the same (`moe_swap_ab_kernel.py:2037,2063–2067`).
- `channel_start` is a multiple128 from the scheduled work tile, CTA rank and optional second channel tile (`:3298–3301`, `:1037`). Each warp's32-channel base is aligned32 channels. Thus `channel < output.shape[1]` and `channel+16 < output.shape[1]` always agree. A live base guarantees all32 channels fit. M256/M512 right-edge work may contain an entirely inactive128-channel CTA/subtile; the same base guard suppresses it.
- Both halves have the same token predicate `token_start+lane<valid_tokens`. Joining them neither writes padding tokens nor changes routing. Output payload rows have exactly the logical channel stride; no additional channel padding is required. Output SF padding is a separate atom-layout rule and remains unchanged.

## Alignment and width

The shared launch path already creates `output_ptr` with assumed32-byte alignment (`moe_swap_ab.py:151`). Nongated row strides are n/2 bytes for FP4 and n bytes for FP8, with n divisible128. The32-channel warp offset is16 bytes for FP4 or32 bytes for FP8. Therefore:

| Output | Old payload copies per lane | Joined payload | Natural alignment |
|---|---|---|---|
| FP4 | two8B | one16B |16B |
| FP8 | two16B | one32B |32B |
| BF16/FP16 per-token FC1 | two32B |64B, still two32B operations |32B per instruction |

The existing32-byte pointer assumption is not a new check: caller-supplied `out` tensors are not all explicitly validated today. Do not claim support for arbitrary misaligned views or silently strengthen the assumed alignment beyond32. Ordinary allocator-owned intermediate buffers satisfy the existing contract.

[PTX9.2 store documentation](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-st) supports256-bit `.v8.b32`/`.v4.b64` stores on SM100+. [Natural alignment](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#addresses-as-operands) is required for the full access width. The current helper already uses `CopyUniversalOp` with a256-bit cap for16-bit output; no new inline PTX is inherently required. A32-element converted tensor can use `min(256, output_dtype.width * cute.size(converted))`, preserving a static dtype-derived width. Actual CuTe4.8 lowering to STG.E.128/256 must be checked rather than inferred from the source copy atom.

## Quantization and simplicity boundary

- Keep each16-channel fragment's arithmetic and conversion order. SF16 still computes two independent quantization parameters and writes two SF bytes; SF32 still computes one joint scale and writes it once. Only concatenate the already-converted payload fragments in channel order.
- The gated path has only16 final channels per lane and should retain its current geometry. Fused finalize uses atomics, so a generic converted-store helper must preserve its element-count-driven atomic loop; do not replace atomics with a vector store.
- An extra converted32-element buffer holds4 registers for FP4 or8 for FP8, but the previous implementation could retire one half before the next. This can increase live ranges even though the source already owns all32 FP32 inputs. Require resource/no-spill and native instruction qualification before timing. Do not claim it is register-free.
- Prefer one static fragment-width derivation and one shared copy path. A dtype-specific runtime branch, new API option or fallback policy would undermine the intended simplification.
