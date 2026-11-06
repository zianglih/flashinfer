# W4A16 FC1 activation audit

At `fe4f8132439df1b812f77279e7d033a5128f1ed4`, MegaMoE already implements the useful fusion from the local W4A16 path introduced by PR #4048: it reads FC1 accumulators, applies FP32 expert alpha and optional clamps, computes SwiGLU, and writes only the reduced BF16 FC2 input. There is no separate activation kernel or full gate/up global intermediate to eliminate. It also already emits packed FP32 arithmetic and paired FP32-to-BF16 conversion. This audit found no missing instruction-level reuse that warrants a performance patch with unchanged semantics.

## Current source and generated instructions

The source root below is `flashinfer/` in the effort checkout. All eight inspected source files match the stated commit exactly; hashes are retained in `logs/w4a16-activation-audit-001.json`.

- `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/epilogue.py:232–254` implements the same default arithmetic sequence as local `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1977–1985,2049–2072`: packed multiply by `-log2(e)`, approximate `exp2`, packed addition of one, approximate reciprocal, `gate * sigmoid`, then `up * silu`.
- Mega lines 359–369 apply FP32 alpha before clamp and activation. Although alpha appears as a tensor expression rather than explicit `mul_packed_f32x2`, the captured compiler already emits `FMUL2` for both gate and up. Rewriting those two lines into an explicit pair loop would reproduce an optimization the compiler already performs.
- Mega lines 400–414 use a bulk `.to(BFloat16)` cast followed by an aligned store. The SASS already uses `F2FP.BF16.F32.PACK_AB`; an explicit packed conversion helper is not missing.
- The existing gate32/up32 public prepared layout is composed into warp-local gate16/up16 TMEM ownership during weight decode. Activation therefore consumes each warp's own accumulator band. This mirrors the later local W4A16 redesign documented at `../flashinfer-w4a16/w4a16_optimization_experiments.md:574–602`, rather than the ledger's earlier shared-memory exchange design.

The saved T4096 EP8 capture `profiles/tmem-fitted5-transform2-codegen-001` uses the exact current epilogue SHA256 `0f6b614b0488ee79d17b3d0cff30715546f54504d687f3be08628a94a7ed86cd`. Its kernel overlay has its own recorded hash; this is not a claim that the entire instrumented capture was rerun on the later commit. All eight ranks give the same source-attributed static counts:

| FC1 operation | Source line | SASS | Static count per rank |
| --- | --- | --- | --- |
| Gate alpha | 359 | FMUL2 | 16 |
| Up alpha | 360 | FMUL2 | 16 |
| Gate × -log2(e) | 237 | FMUL2 | 16 |
| Exponential | 242–243 | MUFU.EX2 | 32 |
| Add one | 240 | FADD2 | 16 |
| Reciprocal | 248–249 | MUFU.RCP | 32 |
| Gate × sigmoid | 251 | FMUL2 | 16 |
| Up × SiLU | 252 | FMUL2 | 16 |
| BF16 conversion | 401 | F2FP.BF16.F32.PACK_AB | 16 |

These are static instruction counts for the two emitted half-subtiles, not executed counts, profiler metrics, or a performance estimate. The capture has `gate_up_clamp=None`; clamp instructions were audited from source, not claimed as captured. The compiler header is bundled CUDA 13.3.27 from CuTe DSL 4.7.1, distinct from the system CUDA 13.2 toolkit.

## Existing MegaMoE patterns

The following paths are relative to `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/`.

| Existing path | Source | Relevant behavior |
| --- | --- | --- |
| Shared SwiGLU, used by MXFP8 | `src/common/moe_utils.py:55–110`; `src/moe_mxfp8_glu/epilogue_mxfp8.py:692–705,768–809` | Same multiplication association as W4A16. Packed arithmetic is already present. MXFP8 additionally quantizes the activation and writes scales. |
| BF16 Mega | `src/moe_bf16_glu/epilogue_bf16.py:17–70,163–173` | Deliberately computes `(up * gate) * sigmoid`. The independent up×gate product can be scheduled before the exponential/reciprocal chain; its comments declare this association part of its exact reference contract. |
| NVFP4 Mega | `src/moe_nvfp4_swapab/epilogue_refactor.py:1661–1800` | `alpha_swiglu_clamp` combines packed alpha, optional scalar clamps, and `(up * gate) * sigmoid` within one helper. This is source-level grouping of several instructions, not an activation-plus-conversion instruction absent from W4A16. |
| Current FC2 conversion helper | `src/moe_nvfp4_swapab/epilogue_refactor.py:2710–2744` | Uses packed alpha and bulk BF16 casting, matching the conversion strategy already used by W4A16 FC1. |
| Legacy FC2 load/pack | `src/moe_nvfp4_swapab/epilogue.py:1091–1093` | Explicitly documents that the bulk cast lets NVVM generate `cvt.rn.bf16x2.f32`; current W4A16 SASS confirms that packing. |

Wholesale reuse of NVFP4 `alpha_swiglu_clamp` would change two contracts:

1. Current W4A16 computes `up * (gate * sigmoid)` like the local W4A16 path. Moving the up×gate product before the reciprocal changes FP32 rounding association. The helpers have the same two multiply operations; the difference is their dependency chain and arithmetic result, not removal of an unfused activation launch.
2. W4A16's `common.fmin/fmax` default to `min.NaN.f32` and `max.NaN.f32` (`src/common/moe_utils.py:113–160`). The NVFP4 helper uses plain `min.f32` for the gate and `min.xorsign.abs.f32` for the symmetric up clamp (`epilogue_refactor.py:1736–1778`). The latter assumes a nonnegative limit, while the current shared clamp resolver only resolves argument aliases (`shim/comm.py:15–42`). It is not a drop-in preservation of the current clamp contract.

Replacing the small W4A16 `_swiglu_act` body with `common.swiglu_act` could reduce source duplication. It introduces no missing fusion or demonstrated instruction/timing gain, so no optimization patch is prepared. FP8/NVFP4 quantization helpers are intentionally excluded because W4A16 hands BF16 directly to FC2.

## Validation and reproduction

```bash
python3 audit_w4a16_activation.py
```

The helper verifies eight source files against the commit, checks the captured epilogue hash, and asserts all nine instruction categories on all eight saved ranks. Full PCs, source lines, artifact hashes and instructions are in `logs/w4a16-activation-audit-001.json`. Ruff and the CPU extraction passed. No GPU, remote operation, active-source modification, tolerance change or performance claim was made for this audit.
