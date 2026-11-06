# Paired activation arithmetic audit

Read-only audit of retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`. No source changes, compilation, GPU work, timing or oracle changes. `inspect.py` regenerates the source hashes, historical-source equivalence check, complete native opcode counts and excerpts in `receipt.json`.

## Finding and proposed scope

There is a credible, bounded instruction-removal candidate in **SiTU's scaled tanh**, in both swap-AB and W4A16. The current code processes channel pairs, but calls the tanh arithmetic separately for each component. Saved native images confirm scalar FMUL/FADD/FFMA sequences remain; this is not inferred only from Python syntax.

The smallest first prototype would replace W4A16's private `_w4a16_scaled_tanh` with a paired helper and replace its two adjacent calls with one paired call. Keep the same six RN arithmetic operations per component and the same scalar EX2/RCP. This has no extra dispatch, public argument, tactic or model-dependent policy. It should remove six arithmetic issue sites per two-channel scaled-tanh invocation, before accounting for register packing and compiler changes. Both gated and optional linear saturation can use it.

Swap SiTU is also a candidate, but must preserve its **different** arithmetic sequence. Its paired scaled-tanh plus sigmoid can use existing packed add/multiply/FMA wrappers while keeping EX2/RCP scalar. Do not fold constants, reassociate products, or make W4A16 and swap share one numerical recipe. With both gate and linear saturation, the observed sequence has 30 scalar arithmetic sites and 12 scalar SFU sites per channel pair; packing would nominally replace the former with 15 paired arithmetic sites. This is a source/ISA estimate, not measured generated code or a speedup prediction.

These are proposals for native qualification, not retention recommendations. Packed register pairing may add MOVs or change live ranges. Native LOCAL0/register gates, existing bit-exact activation tests (including non-fp32-exact beta), and measured end-to-end benefit must precede retention.

## Current activation paths

| Path | Present arithmetic | Audit conclusion |
|---|---|---|
| Swap ordinary SwiGLU | Paired alpha, sigmoid exponent multiply, denominator add, gate multiply, up-beta add and final multiply | Already packed; no arithmetic candidate |
| W4 ordinary/parameterized SwiGLU | Same paired arithmetic with its existing multiplication association | Already packed; preserve association |
| Swap and W4 ReLU squared | Paired scale and square; scalar max-with-zero | No legal direct packed-max substitution |
| Clamp | Scalar NaN-propagating min and sign operations | Preserve; no direct f32x2 min/max |
| Swap SiTU | Paired entry/final products, but separate scalar tanh/sigmoid chains | Confirmed scalar duplication in current-source native captures |
| W4 SiTU | Separate private scalar scaled-tanh calls, paired remaining sigmoid/product work | Confirmed in historical native capture; helper AST is identical at current head |
| GeGLU-tanh | Scalar helper per channel | A possible later arithmetic audit, but no saved-native qualification was established here; not proposed by this audit |

## Rounding contracts that must remain separate

Swap source: `moe_swap_ab_kernel.py::_activate`, `common/kernel_utils.py::{tanh_f32,situ_f32,f32_reciprocal}`. Its exact oracle `cute_dsl_moe_swap_ab_reference.py::_tanh_approx_f32` explicitly requires the FMA shown below. Current SiTU native PTX agrees:

1. Round `beta` to FP32, then derive the FP32 reciprocal from that rounded value.
2. Multiply input by that reciprocal.
3. Multiply by `-2`, then separately by FP32 `log2(e)`.
4. Scalar `ex2.approx.ftz`, RN add one, scalar `rcp.approx.ftz`.
5. **FMA RN** `2 * inverse - 1`.
6. RN multiply by beta.
7. The separate sigmoid uses input times FP32 `-log2(e)`, the same scalar EX2/RCP and denominator add, then the bounded-value product.

W4 source: `moe_w4a16_kernel.py::_w4a16_scaled_tanh`. Its exact `w4a16_reference.py` oracle uses the same explicit inline PTX:

1. Derive FP32 reciprocal directly from the Python beta; do not substitute swap's reciprocal convention.
2. RN multiply input by reciprocal, then by the single FP32 constant `0xC038AA3B` (`-2*log2(e)`).
3. Scalar `ex2.approx.ftz`, RN add one, scalar `rcp.approx.ftz`.
4. **Separate RN multiply and RN subtraction** for `inverse * 2 - 1`.
5. RN multiply by beta.

The W4 private helper has not changed since historical native source `1b0f1f69acbb7e20055d5aaf76cc29c840779304`; `inspect.py` proves AST identity. The whole historical kernel is not claimed identical to retained49.

## ISA and exceptional values

The [CUDA 13.2 / PTX 9.2 reference](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-mul) defines add/sub/mul/FMA f32x2 as independent FP32 lanes, available since PTX8.6 on SM100+. RN and non-FTZ arithmetic preserve the corresponding scalar rounding and subnormal behavior. [FMA](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-fma) has one final rounding, so it must only replace existing fused arithmetic. Min/max, EX2 and RCP have no f32x2 forms here.

Leave all scalar SFU instructions and modifiers unchanged. Keep signed-zero behavior, original operand order, and every intermediate rounding boundary. NaNs must remain NaNs; the ISA does not establish identical NaN payload bits for arbitrary scalar versus packed operations, so do not promise a universal payload-bit proof. Existing swap exact tests explicitly require finite outputs and reject nonfinite accumulator inputs. A bounded paired-helper diagnostic should still compare zeros, subnormals, finite extremes, infinities and NaNs against the retained helper before promotion; that diagnostic is not an oracle change or a new production policy.

Current swap native captures report PTX9.4/SM103a (NVVM CUDA13.4.59) even though the container's nvcc is CUDA13.2. The proposed instructions already exist in PTX9.2; do not conflate the compiler embedded in CuTe DSL with the container nvcc.

## Native evidence

Current-source swap captures are read directly from `experiments/fc1-integer-store-gated/final-evidence/complete-evidence.tar.gz`. Its qualification binds source `482b636a...`, the exact swap source retained at49, and proves byte-identical gated control/candidate native images. Each SiTU case uses gate beta4 and linear beta25, one CTA, PDL on, N256, and LOCAL0/168 registers.

| Full native FC1 image | Scalar FMUL | Scalar FADD | Scalar FFMA | Packed FMUL2 | EX2 | RCP |
|---|---:|---:|---:|---:|---:|---:|
| Per-token SiTU | 1288 | 384 | 256 | 192 | 384 | 384 |
| W4A4 SiTU | 1304 | 384 | 256 | 256 | 384 | 400 |
| W4A8 SiTU | 1288 | 384 | 256 | 256 | 384 | 384 |

These are **whole-image** counts, not all attributable to activation or all removable. The excerpts pin the duplicated tanh chains specifically. `receipt.json` retains all opcode modifiers and the actual PTX/cubin/SASS hashes; the parser does not discard lowercase TMEM geometry or zero-operand instructions.

Historical W4 native evidence is the K3 EP4096 candidate under the old project's `w4a16-scale-dup-b52/codegen-evidence`. It has 128 scalar FMUL, 64 scalar FADD and no FFMA in FC1, alongside the already packed remaining activation work. Its scalar scaled-tanh PTX and current helper AST agree. A fresh current-head native capture is still required for a candidate comparison.

## Closed history and exclusions

- The user-reverted `b8ccad2d` optimization changed quantizer absmax from a chain to a tree. Its measured aggregate was effectively neutral for added complexity. This proposal does not change `_absmax`, maxima, dependencies between maxima, scale selection or quantization order.
- The old native-TMEM FC1 proposal changed ownership and channel pairing to avoid transpose work. Its references to paired activation did not introduce a paired SiTU arithmetic helper. This audit changes neither TMEM layout nor ownership.
- The earlier W4 packed-FC2 source rewrite is a warning against source-only inference: its scalar form already lowered to packed FMUL2. Here saved SiTU SASS actually contains scalar duplicate arithmetic.
- No dedicated SiTU paired-helper experiment was found in the inspected ledgers. That is a scoped history search, not an assertion about every historical commit.

Relevant old ledgers: `fc1-gather-20261028/optimization-next-20261029/retained-complexity-audit-20261030/AUDIT.md`, `native-tmem-fc1-audit/PROPOSAL.md` under that same parent, and `optimization-20261028/tp-ep-post-sanitizer/w4a16-port/packed-fc2-r1/RESULTS.md`.
