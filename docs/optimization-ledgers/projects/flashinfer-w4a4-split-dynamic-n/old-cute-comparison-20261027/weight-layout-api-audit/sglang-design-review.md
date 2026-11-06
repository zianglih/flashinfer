# Prequantized SGLang layout boundary — design review only

Sources read: FlashInfer `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549`; SGLang `010eb729bea2b7ef2bcd572a72c171f75ad900fb`. No production edits, imports, tests, builds, GPU work, or validation were performed for this review.

## Public boundary

`CuteDslConfig.prepare_weights` starts from BF16. It quantizes weights and constructs scale/alpha values; it is not an adapter for checkpoint NVFP4/MX bytes. SGLang should keep its existing checkpoint loading, alpha computation, activation scales, parameter rebinding, wrapper creation and reload handling.

The smallest complete layout boundary can prepare one projection's weight/block-scale pair:

```python
prepare_cute_dsl_moe_weight(
    weight, block_scales, *, k: int, sf_vec_size: int = 16, gated: bool = False
) -> tuple[Tensor, Tensor]
```

This is a proposed API, not an existing callable. Inputs are 3-D checkpoint payload `[experts, rows, packed_K]` (FP4) or `[experts, rows, K]` (FP8), and logical row-major block-scale bytes `[experts, rows, ceil(K / sf_vec_size)]`. For gated FC1, rows must already be canonical `[up, gate]`; set `gated=True`. FC2 and non-gated FC1 use `False`. `k` is the logical reduction width already known by the caller. The helper derives the expert/row counts, chooses the hardware's 16/64 gate/up pairing, applies the same row permutation to payload and block scales, and uses existing `convert_row_major_sf_to_mma_layout` to return the scale view. It does not quantize, invert/fold global scales, swap canonical half order, alter activation recipes, or infer checkpoint conventions.

`sf_vec_size` describes checkpoint quantization blocks (16 NVFP4, 32 MX), not the gate/up row grouping; exposing that semantic input does not expose the architecture layout. Both scales and payload must already belong to the intended target device. Preserve current shape/padding rules: a wrapper around the existing operations should not quietly start padding payloads or reinterpret already-swizzled scale storage. If the SGLang demo keeps its existing padding/swizzle lifecycle, an even smaller paired **row-permutation-only** helper can first replace the duplicated hardcoded interleave, leaving scale conversion where it already is. A later whole-weight preparation API should not be required merely to adopt this layout change.

## Actual SGLang callers

| Path | Current consumer / consequence |
|---|---|
| ModelOpt standard-v2 MoE | `modelopt_quant.py:2980–3003` interleaves packed W13 and logical SF rows with hardcoded64; `3054–3095` converts swizzled SF to MMA. This path needs the split-layout adaptation. `load_up_proj_weight_first` already supplies `[up, gate]`. |
| Online NVFP4 | `nvfp4_online.py:225` subclasses `ModelOptNvFp4FusedMoEMethod` and inherits post-load preparation. The same standard-v2 fix covers it; preserve online weight quantization and activation/global scales. |
| Split W4A16 through ModelOpt | The same standard-v2 preparation; runtime sets `quant_mode="w4a16"` in `flashinfer_cutedsl.py:325`. It needs the same row layout, not a separate loader implementation. |
| DeepEP low-latency masked CuTe | `modelopt_quant.py:3284–3307` passes plain `[gate, up]` weights and swizzled SF to `flashinfer_cutedsl_moe_masked`; that calls `grouped_gemm_nt_masked`. Do not apply the standard split-layout helper. W4A16 is explicitly disallowed on this path. |
| Compressed-tensors W4A4 NVFP4 MoE | Separate `compressed_tensors_w4a4_nvfp4_moe.py` implementation chooses TRTLLM or CUTLASS in `create_moe_runner`; no current split-CuTe integration. No compatibility change required. |
| Compressed-tensors W4A16 MoE | `compressed_tensors_w4a16_nvfp4_moe.py:30` is the Marlin runner, preserving its checkpoint row order. No split-layout change. |
| MXFP4 MoE | `mxfp4.py:410–436` maps `flashinfer_mxfp4` to TRTLLM on SM100 and CUTLASS on SM90/SM120; no existing split-CuTe route. Adding one is a new backend integration. |
| FP8/MXFP8 MoE | `fp8.py:2974–2987` redirects the CuTe/CUTLASS MoE backend selection to Triton for this method. The existing MegaMoE integration is separate. No existing split-CuTe MX caller to migrate. |
| Dense W4A16 | ModelOpt and compressed-tensors call `prepare_bf16_fp4_weights` / `mm_bf16_fp4`. No gated MoE row pairing is involved. Preserve its preparation and quantization-block16 convention. |
| Dense fused SwiGLU NVFP4 | The hardcoded64 interleave in `modelopt_quant.py:2030–2063` imports SGLang's own `sglang.kernels.ops.gemm.nvfp4_gemm_swiglu_nvfp4_quant`; it is a different consumer. Do not replace it with the split-MoE layout. |

This supports a small compatibility demo centered on standard-v2 ModelOpt preparation. It does not justify changing every occurrence of 64, adding new MX backends, altering the masked path, or re-quantizing checkpoint weights. The normal public BF16 API already hides architecture grouping; the missing boundary is for existing quantized payload/scale pairs.

## Minimal paired-interleave demo selected by parent

The selected demonstration API is narrower than the complete projection helper above:

```python
interleave_cute_dsl_moe_weights(weight, block_scales)
```

It returns the pair after the architecture-specific gated row permutation; SGLang retains its existing SF swizzle/MMA conversion, padding, calibration and parameter lifecycle. This is a sensible minimal compatibility boundary, with no caller-visible 16/64 parameter. The complete projection helper above remains only an alternative design, not a requested addition.

The registered SGLang test needs only two real v2 input-producer updates: `_create_cutedsl_wrapper_tensors` at original lines94–112 and `_quantize_local_expert_weights` at191–207. Quantize original canonical BF16 rows with unswizzled SF, reshape both outputs by expert, call the paired helper, then feed the permuted SF through the existing block-scale swizzle and MMA conversion. Preserve all original BF16 weight snapshots and the pure-PyTorch `_compute_reference_moe_fp4` (lines284–333), which does not call the preparation helper. W2 generation remains unchanged. Update the v2 class documentation's hardcoded64 description to describe backend preparation.

V1 masked positive tests remain unchanged. The negative test at926 intentionally supplies interleaved `[up, gate]` weights to a consumer requiring plain `[gate, up]`; its local64 permutation remains a valid malformed-layout input. For minimum diff it can stay, with wording identifying it as an intentionally incompatible interleave rather than claiming it is the current Blackwell v2 layout. Changing this negative test to manufacture the exact current v2 packed payload would require separate per-expert unswizzled quantization or scale unswizzling; that is unnecessary for this design demo and would expand the masked-path change surface.

All recommendations above are source inspection only. No validation was run.
