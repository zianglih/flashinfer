# Remaining non-TMA vectorization audit

Source: retained `98fd3566b5f945c100f48cddacf25deb2432cbc2`; CPU-only inspection, 2026-10-25. No implementation or GPU measurements. Combine and input-preparation scale-factor work are excluded. Existing regular TMA stays unchanged.

## What is already covered

- Default SwiGLU scaling, sigmoid arithmetic around the scalar SFU operations, activation multiplication, requantization scaling, and ordinary FC2 scaling already use `mul_packed_f32x2` / `add_packed_f32x2`. See [activation](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:384), [requantization](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:507), and [FC2 bulk scaling](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:866). Scalar `exp2` / reciprocal are not omissions that can be fixed by replacing an arithmetic pair alone.
- Direct output copies already cap at **256 bits** ([store](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:525)). FP4/FP8 fragments contain only 64/128 bits; widening those requires different ownership, not a larger copy atom. The large FC2 path already uses `Ld16x256bOp`, a padded shared-memory `stmatrix` transpose, and bulk row stores ([bulk epilogue](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:846)).
- A/SFA and regular B/SFB transfers use TMA. The remaining small-N SFB copy is four bytes per logical scale block; successive blocks are 512 bytes apart. Replacing it with a 16/32-byte copy at the same pointer would move other rows/scales and break short-K masking ([small-N SFB](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1151)). No simple contiguous width lift was found in the retained core.

## Bounded follow-ups, in priority order

1. **Per-token NVFP4 quantization: wider register-resident input load, then packed scaling.** Each SF16 block currently loads the same 32 bytes using two `ld_global_v4_u32` calls ([row load](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/quantization/kernels/nvfp4_quantize.py:1226)). An existing SM100+ `ld_global_v8_u32` helper provides the equivalent 256-bit operation ([helper](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/quantization/quantization_cute_dsl_utils.py:742)). Preserve clamped final-block loads, 64-bit row offsets, register order, and PDL publication. The public API only promises 16-byte base alignment; `.contiguous()` does not establish 32-byte alignment for an already contiguous storage-offset view. Use an explicit 32-byte-aligned specialization with the existing fallback, not an unconditional stronger assumption. Static K%16 gives 32-byte row/block strides for BF16/F16 once the base is aligned.

   Standard quantization then calls helpers whose inline PTX converts each half/BF16 pair to FP32 and performs **two scalar `mul.f32`** operations ([half](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/quantization/quantization_cute_dsl_utils.py:430), [BF16](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/quantization/quantization_cute_dsl_utils.py:463)). A Blackwell-only packed multiply can preserve conversion-before-multiply, both RN results, and the existing E2M1 packing order. Confirm current cubin code first: fewer PTX operations do not prove fewer SASS instructions. Preserve scale computation/rounding, fast-math branches, and 4over6 behavior; these helpers also have callers outside this MoE path.

2. **FC2 per-token bulk scaling: pair the two existing independent multiplications.** [Lines 859–865](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py:859) remain scalar while the uniform branch directly below is packed. Adjacent registers represent different tokens, so retain both metadata shuffles and feed both distinct scales to `mul_packed_f32x2`. Preserve the earlier BF16/F16 rounding of `alpha * per_token_scale[row]`; do not move or combine that rounding. This reduces arithmetic issue only, not shuffle or memory traffic.

Both proposals apply to the per-token NVFP4 path ([caller](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer/flashinfer/fused_moe/cute_dsl/fused_moe.py:734)). **The current primary AUTO campaign uses per-tensor activation scales**, so these cannot explain or improve its reported rows. Other input formats must retain their existing paths.

## Primary per-tensor scope: inspect before changing

The scalar16-value `_absmax` chain is already a **closed optimization axis**.
The older [FC1 audit](fc1-native-audit/README.md) generated a tree without testing
it, but the later [FC1 arithmetic experiment](fc1_arithmetic_experiment/README.md)
GPU-tested a balanced three-input `max.abs.f32` tree (`abs3`) and a serial
`max.xorsign.abs.f32` variant (`absxor`) on7829. Actual-routing NVFP4 FC1 at16K
measured324.3685µs control,324.2410µs abs3 (1.0004×), and325.7280µs absxor
(0.9958×); native output/SF bytes matched. Both were rejected, with no primary
campaign. The compact variant's24 six-format checks do not establish exhaustive
exceptional-value coverage. Current98fd cubin inspection may characterize the
retained chain, but the stale “never GPU-tested” note is not justification to
repeat plain balanced reduction. No new absmax experiment was launched.

CPU contract trace: installed CuTe DSL4.7.1 `cute.arch.fmax` defaults to
`nan=False, ftz=False, abs=False` and emits `nvvm.fmax`. The retained reduction
therefore returns the greatest non-NaN absolute value, +Inf if present, and
+0 for all-NaN or all-zero input. Signed zeros become +0 through `max(x,-x)`;
subnormal magnitudes are preserved. A balanced reduction of those same leaves
with an explicit +0 seed and the same modifiers preserves the result for every
FP32 input pattern: NaNs cannot become the final result, and max selects an
existing nonnegative value without arithmetic rounding. Omitting the +0 seed
would change the all-NaN case; enabling `.NaN` or `.ftz` would also change the
contract. This is a source/ISA argument, not new GPU exceptional-value coverage.
See the official [PTX max semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#floating-point-instructions-max).


Historical [epilogue evidence](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/scripts/epilogue_experiment/README.md) already verified `STG.E.ENL2.256` and rejected direct scalar-store/alternative transpose variants; [FC2 evidence](/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/scripts/native_fc2_experiment/README.md) motivated the retained bulk path. Those snapshots predate this retained source and are not current register, spill, or bottleneck measurements. Do not repeat those axes or replace working regular TMA based on this source audit.
