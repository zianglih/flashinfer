# K3 W4A16 MegaMoE activation review

Source base: upstream FlashInfer `a7103ae2`; inspected on 2026-10-08. Workload: K3-shaped routed latent MoE, D=3584, E=3072, N=896, K=16, SiTU gate beta=4 and up beta=25. This is synthetic NVFP4, not the released K3 MXFP4 checkpoint.

## The actual difference from #4540

PR #4540 fixed runtime FP32 division in the **split W4A16** SiTU caller. It kept beta as a Python scalar for the shared `situ_f32` helper and used `f32_reciprocal` for the up branch. Its performance result does not establish a remaining division bottleneck in MegaMoE.

Both current MegaMoE implementations already compute `1.0 / self.situ_beta` and `1.0 / self.situ_linear_beta` as Python expressions before wrapping them in `cutlass.Float32`. There is no per-element division at these source sites. Both nevertheless use the Python-double beta, unlike #4540's reciprocal of the FP32-rounded beta. This distinction does not change K3's FP32-exact 4 and 25 constants.

Sources:

- W4A16 Mega: `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py`, `W4A16Fc1Epilogue._swiglu_act` and `_tanh` (before candidate).
- W4A4 Mega: `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue_refactor.py`, SiTU branch around lines 1816–1841.
- Split W4A16: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`, gated SiTU branch around line 2030.
- Shared helper: `flashinfer/fused_moe/cute_dsl/common/kernel_utils.py`, `tanh_f32`, `f32_reciprocal`, `situ_f32` around lines 205–245.
- Archived upstream evidence: `evidence/pr4540.json` and `evidence/pr4540.diff`.

## What each implementation does

| Path | Gate sigmoid | Gate/up tanh | Pair arithmetic | FC1 output |
|---|---|---|---|---|
| W4A16 Mega | packed exponent multiply and denominator add, scalar exp2/rcp | scalar `2*rcp(1+exp2(-2*log2(e)*x))-1` | SwiGLU surrounding arithmetic is packed, SiTU's extra gate/up math is scalar | BF16 |
| W4A4 Mega | same packed sigmoid structure | same scalar exp2/rcp tanh sequence | scalar SiTU branches, packed final gate/up product | NVFP4, with fused quantization |
| Split W4A16 | shared scalar helper | shared scalar sigmoid-derived tanh | packed scaling before activation and final product, scalar SiTU helper calls | BF16 |

None of these three paths uses native `tanh.approx.f32`. W4A4 therefore supplies a control for the same activation algorithm, not an existing faster tanh implementation to copy. Its much faster tensor core path can still hide different proportions of FC1 epilogue work. This needs compiled artifacts and matched timing, not inference from source alone.

## Candidate A: packed exp2-based SiTU

Working-tree change: only the W4A16 Mega epilogue. Full baseline-relative patch: `evidence/candidates/packed-situ.patch` (also retained as `evidence/activation-candidates/packed-exp2.patch`).

- Use `f32_reciprocal` for consistency with #4540 and the split implementation.
- Process both output lanes through packed FP32 multiplies/adds for division-by-beta, tanh exponent/denominator/result, multiply-back, and gate-times-sigmoid.
- Retain scalar exp2 and reciprocal instructions: there is no packed version substituted here.
- Retain gate sigmoid, beta multiply-back, and final `up * (bounded_gate * sigmoid)` association. Ordinary and parameterized SwiGLU branches are untouched.

This reduces arithmetic issue count around the special-function operations without changing the mathematical approximation. It does not reduce the number of exp2/reciprocal operations. Generated SASS and measurements must establish whether the compiler already packs equivalent scalar expressions and whether this is on the critical path. No bitwise-equivalence or performance claim has been validated.

## Candidate B: native FP32 tanh (performance experiment)

Native tanh is more promising for reducing the dependency chain: each gate/up tanh replaces exponent multiply, exp2, denominator add, reciprocal, and result scaling with one `tanh.approx.f32`. For two output lanes with bounded gate and up branches this replaces four exp2 plus four reciprocal operations with four tanh operations. The separate sigmoid is retained.

Full baseline-relative patch: `evidence/candidates/native-tanh.patch`. It includes candidate A's packed surrounding arithmetic but replaces `_tanh_pair` with two `cute.math.tanh(..., approx=True)` calls. The retained C2 DSL 4.7.1 signature supports this argument, and its implementation calls the approximate NVVM tanh operation. The working tree remains on candidate A.

This changes the approximation. NVIDIA's [PTX tanh documentation](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-tanh) specifies maximum relative error `2^-11` over the FP32 range and support from SM75. It supports signed zero, infinities and subnormals. Accuracy must be validated after a performance win; smaller instruction count is not permission to loosen the existing correctness contract.

There is a relevant warning in current source: `flashinfer/fused_moe/cutile/activation.py::_tanh_via_sigmoid` deliberately uses the sigmoid-derived form because SiTU's linear scale can amplify approximation error. The newer SM12x SiTU path also uses `cute.math.tanh(..., approx=False)`. These justify treating native tanh as a separate experiment, not folding it silently into a vectorization change.

No tests, GPU work, or correctness validation were run by this review task. Per user instruction, the root experiment should first establish a performance win and then validate numeric behavior, including non-K3 beta values and the unbounded-up variant.
