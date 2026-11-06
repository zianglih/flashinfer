# W4A16 decoder, epilogue, and MXFP8 alternative: source and arithmetic audit

This note supports the blog's decoder/epilogue sections. Code is pinned to
FlashInfer PR 5019 head `7ca3eb567a2400df70579d55e9bc717ea1784b0c`. It was read
from public raw GitHub files without changing GitHub authentication. Saved files
are under `evidence/flashinfer-pr5019-source/`. The supplied slide deck was
exported read-only by the parent task; slides 47–48 were checked against its text
export. No new GPU experiment was run.

## Findings suitable for the blog

1. W4A4 FC1 has a substantial non-MMA chain: FP32 output scaling, optional
   gate/up clamps, SwiGLU, optional routing multiplication, block scale
   generation, normalization, conversion to E2M1, and stores of data/scales.
   Fusing it avoids a launch/materialization but does not eliminate this work.
   It can become visible as the native FP4 matrix multiplication gets faster.
   This is a dependency/implementation argument, not a quantified bottleneck
   attribution from the W4A16-only traces.
2. W4A16 retains FP32 scale application and activation work in the epilogue,
   but removes intermediate activation quantization. Separate decoder warps
   perform only the local E2M1 × E4M3 reconstruction, without the FP32
   second-level weight scale.
3. Every finite E2M1 × finite E4M3 local product is exactly representable in
   BF16 and FP16. This is true for the local product only; it does not mean the
   original weights, the fully scaled weight, the GEMM, or the model are exact.
4. Standard FP8 E4M3/E5M2 do not have sufficient significand precision to
   preserve every local product. MXFP8's power-of-two block scale extends or
   shifts range but cannot supply missing significand bits.
5. PTX 9.4 has the stated mixed packed multiplication form. Direct unrescaled
   E4M3 output both rounds and can saturate. Its scale cap of 72 is an
   overflow-avoidance condition for all E2M1 inputs, not an exactness guarantee.
6. The excluded count is exactly **21 of 126 positive finite nonzero E4M3
   scales**. If zero is included, the denominator is 127. This counts possible
   encodings, not their observed frequency or an accuracy percentage.

## Source trail for W4A4's FC1 epilogue

The W4A4 Mega class inherits `Sm100SwapABSwigluFp4Fc12Kernel`; that base imports
the active refactored epilogue from `epilogue_refactor.py`, so the links below
refer to the used implementation rather than its older companion file.

- [Base kernel selects refactored epilogue](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py#L26).
- [FC1 reads per-expert alpha and optional normalization](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py#L1378).
- [FP32 scale, optional clamps, and SwiGLU](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py#L1710).
- [Optional routing multiplication then fused block quantization and scale store](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py#L1907).
- [Quantizer: amax, E4M3 scale, reciprocal normalization, E2M1 conversion](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py#L189).

Per-token second-level scaling adds a row-amax dependency **when that recipe is
used**. The default benchmark's lack of a custom per-token override must not be
silently turned into a claim that this extra row reduction ran in every W4A4
arm. The existing micro-block scale reduction is already visible in source.

Suggested wording:

> A fused epilogue still has work to do. After FC1's matrix multiply, it applies
> the FP32 scale, computes the activation, performs any model-specific clamps,
> and prepares FC2's input. W4A4 also generates quantization scales and converts
> that input back to four bits. Faster FP4 tensor cores can expose this remaining
> chain. W4A16 removes that activation-quantization step and gives independent
> weight preparation to dedicated warp groups.

The W4A16 epilogue still performs scaling/clamping/SwiGLU. Do not write as if
those shared operations disappear, or as if its epilogue has no cost.

## Exact local product and deferred FP32 scale

Write a stored weight as `alpha × s × q`, where `q` is E2M1, `s` is the E4M3
micro-block scale, and `alpha` is the FP32 second-level scale. The decoder
produces `s × q`, leaving `alpha` for the FP32 accumulation epilogue.

Source:

- [Decoder signature and direct BF16 conversion/multiply path](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py#L19): inputs are packed E2M1 words and E4M3 scale; there is no FP32 global-scale input. CUDA 13.2+ uses packed BF16 conversion and multiplication. The older path performs the exact local product in FP16 and converts to BF16.
- [FC1 alpha applied to FP32 values loaded from TMEM](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L615): `gate` and `up` are FP32 registers, scaled before clamp/activation at lines 632–642.
- [FC2 alpha loaded from FP32 argument](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L338) and [passed into the accumulator conversion](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L301).
- [Author's design slides](https://docs.google.com/presentation/d/1P4RbwsjYCf8nv-XNFNy-CxctzyuBzsiJVcBUMtKDhLw/edit?usp=sharing), especially 10, 27, 47.

The precision argument is algebraic before finite-precision accumulation:

```text
sum_i activation_i × (alpha × s_i × q_i)
  = alpha × sum_i activation_i × (s_i × q_i)
```

The implementation does not first multiply every decoded weight by `alpha` and
round that fully scaled weight into BF16. Deferral avoids that additional
per-weight BF16 rounding and keeps the second-level multiply in FP32. It also
keeps an extra FP32 operation/conversion sequence out of the decoder.

Finite-precision reassociation and MMA accumulation still matter: do not claim
this algebra establishes bitwise equivalence to all other evaluation orders or
uniformly smaller error for every dot product. A sound claim is **“we avoid an
additional BF16 rounding just to apply the second-level scale.”**

Slide 47 describes an older **16-warp split** kernel and its 65,536-register
budget. MegaMoE's **20-warp** kernel and 61,440-register allocation are a separate
design. Share the scale-placement principle, not the exact role diagram/budget.

## Exact representability proof

Nonnegative E2M1 values are `0, 0.5, 1, 1.5, 2, 3, 4, 6`.
For finite E4M3 values, the significand has at most four significant binary bits.
Multiplication by a two-bit E2M1 significand needs at most six significant bits.
Subnormal E4M3 values do not enlarge that bound.

For nonzero magnitudes, the local product ranges from

```text
0.5 × 2^-9 = 2^-10 = 1/1024
6 × 448 = 2688
```

This range lies inside the normal ranges of both BF16 and FP16. Their precisions
are eight and eleven significant bits, respectively, so every local product is
exactly representable. Signs do not change the precision/range proof; zero is
numerically exact. NaN scale codes are excluded.

The exact rational enumeration in `audit_nvfp4_products.py` checks all 1,016
nonnegative `(q, scale)` pairs, including zero, without approximate float
arithmetic. Its output is `evidence/nvfp4-products-exact-audit.json`.

This proof excludes the FP32 second-level scale. Multiplying by an arbitrary
FP32 `alpha` can require many more significand bits; that is precisely why the
scale's placement should remain explicit in the article.

## Why MXFP8 is not a lossless replacement for the BF16 decoder output

MXFP8 normally uses FP8 E4M3 or E5M2 elements with E8M0 power-of-two block scales.
E4M3 has four significant bits and E5M2 has three. Either can fail to represent
an exact E2M1 × E4M3 product.

For example:

```text
q = 1.5, s = 1.125
q × s = 1.6875 = 27/16 = binary 1.1011
```

The product needs five significant bits. E4M3 round-to-nearest-even produces
1.75 instead. Multiplying/dividing by a power of two changes exponent placement,
not the five-bit significand. Therefore an E8M0 scale cannot make this product
exact in an E4M3 element. Other products require six significant bits, for
example `1.5 × 1.875 = 45/16`.

Decoding to BF16 first and then quantizing to MXFP8 introduces an additional
conversion/scale path. It can increase pressure on the transformation stage.
The provided slide 48 states this design tradeoff; the current code and traces
do not contain a matched MXFP8-conversion performance ablation. Use conditional
language such as **“at shapes where transformation is already close to limiting
the pipeline, the extra conversion can offset the higher tensor-core ceiling.”**
Avoid announcing a measured universal slowdown or ruling out every possible
optimized MXFP8 encoding.

Primary background: [NVIDIA's block-scale layout guide](https://nvidia.github.io/cudnn-frontend/mxfp8-scale-factor-128x4-layout/)
and [Transformer Engine MXFP8 format documentation](https://nvidia.github.io/TransformerEngine/features/low_precision_training/mxfp8/mxfp8.html).

## PTX 9.4 direct packed multiplication and the 72 cap

The correct documentation anchor is
[Alternate Floating Point Instructions: mul, section 9.7.6.3](https://docs.nvidia.com/cuda/parallel-thread-execution/#alternate-floating-point-instructions-mul).
The ordinary `#floating-point-instructions-mul` anchor points to a different
instruction family. The HTML IDs were checked directly.

The packed mixed-input form

```ptx
mul.rn.e4m3x4.e2m1x4.e4m3x4.satfinite
```

is covered by the documented operand/destination types. PTX 9.4 introduces this
family for SM100a/SM103a. It rounds each exact product to the destination FP8
format; `.satfinite` clamps overflow to its largest finite magnitude. It is not
an instruction that preserves arbitrary NVFP4 local products exactly in FP8.

With E4M3 output and no additional rescaling, guaranteeing no overflow for every
E2M1 input requires

```text
s × 6 ≤ 448
s ≤ 448/6 = 74 2/3
largest representable E4M3 s satisfying this = 72
```

Unsigned-positive E4M3 scale encodings 1–126 are finite and nonzero, code 0 is
zero, and code 127 is NaN. Scale 72 is code 105. Codes 106–126 are the 21 excluded
values:

```text
80, 88, 96, 104, 112, 120,
128, 144, 160, 176, 192, 208, 224, 240,
256, 288, 320, 352, 384, 416, 448
```

Thus **21/126** counts nonzero positive finite scale choices. With zero included
the fraction is **21/127**. The count says nothing about how often a trained
checkpoint uses those scales or how much model accuracy is affected.

Even an overflow-safe scale does not remove rounding: `6 × 72 = 432`, which lies
between E4M3's 416 and 448 and rounds to 448 under round-to-nearest-even.
At the other end, `0.5 × 2^-9 = 2^-10` is below the smallest positive E4M3 value.
Additional rescaling or a different FP8 format can change range limitations,
but the significand limitation remains. The 72 cap belongs to the **direct,
unrescaled E4M3-output path**, not all imaginable MXFP8 implementations.

Suggested compact blog wording:

> A direct packed multiply does not make the conversion lossless. PTX 9.4 can
> multiply packed E2M1 values by E4M3 scales into E4M3 results, but those results
> are rounded. Without another rescaling step, accommodating an E2M1 magnitude
> of six also caps the block scale at 72, excluding 21 of the 126 positive finite
> scale values. BF16 holds the local product exactly and lets us keep the decoder
> focused on that simple reconstruction.

## Review of the current blog section

The new section's exact-product proof, deferred FP32 scale, E4M3 example,
conditional transform-cost argument, and 72/21-of-126 statement are technically
sound. Two edits were reported to the parent:

1. Correct both PTX links to `#alternate-floating-point-instructions-mul`.
2. Qualify the row-amax sentence with “In W4A4 recipes that use per-token
   scaling...” so it is not silently attributed to the default benchmark arm.

Keep claims about improved training agreement anchored to the separate numerical
ablation. Exact local reconstruction does not make NVFP4 weights equal to their
unquantized source or establish complete model/output equivalence.
