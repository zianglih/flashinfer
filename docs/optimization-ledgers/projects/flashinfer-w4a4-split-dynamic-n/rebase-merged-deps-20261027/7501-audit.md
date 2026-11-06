# Merged #7501 / retained #7290 contract audit

Read-only comparison on 2026-10-27. No repository changes, ref updates, fetch, GitHub operation, compilation, or GPU run was performed for this audit.

- Merged #7501: `fb022756415cc9cad1e1a64ee918860e17638fe8`, parent `03d7f4a399a47e72d93631e19becd804147fc47b`.
- Retained #7290: `ee88cf2acc59748a64ee2614fed2f16f05f67988`; previous upstream base `215f83cb`.
- Compared immutable `git show` objects. #7501 changes 11 files; none intersects the paths changed by #7290 against its old base. This only establishes no direct #7501 path conflict, not absence of other rebase conflicts.
- `flashinfer/quantization/quantization_cute_dsl_utils.py` is byte-identical at both heads, SHA-256 `c4e2a0d938ce01953610a62f02a783aff82e877854cfab101dc79000c39f63c6`.

## Conclusion

Inherit #7501's production and reference changes as merged. No additional quantization arithmetic change is required in the **currently exposed split MoE families**: their fused NVFP4/MXFP8 epilogues already use the CuTe contracts that #7501 brings CUDA/cuTile into line with. Preserve the previously retained in-place epilogue arithmetic and the FP32 activation values through quantization. This is source-level alignment, not a new post-rebase runtime validation claim.

There is a separate, pre-existing lower-level FP4/UE8M0 output fallback that does not implement the newly documented standalone MXFP4 contract. It is not selected by the public MoE families or current benchmarks; see the precise boundary below rather than claiming every low-level output combination is bit-exact.

## Production overlaps

| Path | #7501 change | Retained split MoE alignment |
|---|---|---|
| Standard-fast NVFP4 | CUDA now tests the encoded E4M3 SF byte, rather than only block AMAX, before producing an inverse. A nonzero block whose SF rounds to zero must produce zero payload scaling. | `_store` calls `_nvfp4_standard_quant_from_amax(absmax, norm_const, False)`, already implementing the same zero-SF and reciprocal association. No strict/4over6 behavior should be substituted here. |
| MXFP8 | CUDA uses subnormal-preserving FP32 multiplication and an inverse constructed from the UE8M0 byte; cuTile adopts the same upward scale encoding and non-FTZ arithmetic. Byte zero gives inverse zero. | `_store` uses `float_to_ue8m0_fast(amax / 448)` and `ue8m0_to_inv_scale_fast`, followed by packed FP32 multiplication and E4M3 conversion. Both shared helpers are unchanged by #7501. |
| MXFP4 weights × MXFP8 activations | Standalone MXFP4 quantization now has exact CUDA/CuTe reference coverage, upward UE8M0 scale rounding, subnormal preservation, and global-scale-independent semantics. | The FC1 output is **MXFP8**, not MXFP4. Its fused activation quantization therefore follows the MXFP8 row above; upstream MXFP4 changes affect weight preparation/quantization, not a new FC1 FP4 output path. |
| Per-token NVFP4 | Upstream reference cleanup explicitly separates strict/fast arithmetic from the 4over6 error recipe and includes row decode scales. | FC1 produces the existing intermediate type and invokes `nvfp4_quantize_per_token_cute_dsl`. The retained row-grid/PDL changes do not replace its shared numerical helpers. Keep its selected recipe and arithmetic configuration explicit when checking the reference. |

Immutable source anchors:

- [CUDA multiplication/inverse primitives](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/csrc/nv_internal/tensorrt_llm/kernels/quantization_utils.cuh#L265), [NVFP4 SF-zero guard](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/csrc/nv_internal/tensorrt_llm/kernels/quantization_utils.cuh#L505), [MXFP8 quantization](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/csrc/nv_internal/tensorrt_llm/kernels/quantization_utils.cuh#L899).
- [Retained fused epilogue](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py#L552), [public dtype selection](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/fused_moe/cute_dsl/fused_moe.py#L660), [per-token standalone invocation](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/fused_moe/cute_dsl/fused_moe.py#L781).
- [UE8M0 upward conversion](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/quantization/quantization_cute_dsl_utils.py#L159), [inverse construction](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/quantization/quantization_cute_dsl_utils.py#L209), [standard NVFP4 helper](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/quantization/quantization_cute_dsl_utils.py#L1755).

The packed payload operation is not inherently FTZ: the [official PTX multiplication contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#floating-point-instructions-mul) supports subnormals unless `.ftz` is explicitly present. Existing source-bound MXFP8 control PTX at `scripts/perf_round_20261027/epilogue-release-gate/focused-evidence/focused/control/config1-fc1-pdl0.ptx` shows the scale multiply without FTZ at line 928, exact inverse construction at 958–971, and `mul.rn.f32x2` payload operations at 1009 onward. This historical artifact corroborates the source interpretation; it is not a new compile of the rebased head.

## Reference integration

Keep upstream's complete caller migration:

- [`ref_fp4_quant`](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/tests/test_helpers/utils_fp4.py#L90) keeps its interface, but now supplies an exact standard-fast NVFP4 oracle and exact FP16/BF16 MXFP4 oracle. The latter requires block size 32 and ignores global scale.
- [`ref_fp4_quant_te`](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/tests/test_helpers/utils_fp4.py#L195) now takes the explicit recipe/arithmetic/optional decode-scale arguments and returns **four** values: unpacked payload, linear SF bytes, tensor/row decode scale, and chosen-four mask.
- `ref_fp4_quant_4over6_te` and `_ref_fp4_quant_te_with_decode_scale` are removed, folded into the shared oracle. None of #7290's modified Python files references those removed names.
- `pack_fp4_values` preserves signed-zero nibbles. Compare payload and SF **bytes**, not decoded numeric equality that would hide signed-zero differences.
- The existing MXFP8 oracle lives in `tests/utils_fp8.py` and remains unchanged. #7501 upgrades its callers to exact payload/SF assertions.

Do not compare an in-place FP32 FC1 activation against a standalone oracle fed a newly BF16-rounded tensor: that would test a different quantizer input. Standard fused NVFP4 can use the supplied-encode-scale `ref_fp4_quant` branch on FP32 activation values. Per-token calls should use the actual intermediate tensor and explicit recipe. No new end-to-end bit-exact MoE claim follows from standalone exact quantization.

## Lower-level boundary

The direct FC1 wrapper/core admit homogeneous FP4 inputs with UE8M0 SF and FP4 output ([dtype admission](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py#L1813), [wrapper output validation](https://github.com/flashinfer-ai/flashinfer/blob/ee88cf2acc59748a64ee2614fed2f16f05f67988/flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L758)). Its generic FP4 branch at core lines 573–583 still applies `norm_const`, directly converts the SF, and obtains the inverse through reciprocal approximation. The merged standalone MXFP4 contract instead ignores global scale and constructs upward-rounded UE8M0 scale/inverse bits.

This is not the mixed MXFP4×MXFP8 public MoE arm, and #7501 explicitly excludes fused activation contracts. It is therefore not a rebase blocker for the requested public-family scope. If a separate requirement is to make this direct lower-level output combination standalone-MXFP4-exact, it needs an intentional arithmetic/API decision plus focused validation; do not silently claim the current generic fallback satisfies it or change Rubin/W4A16 as part of this merge.

## Focused post-rebase checks

These are recommendations, not executed results:

1. Import/collect the upstream FP4 tests to catch obsolete oracle signatures. Preserve all #7501 migrations; no compatibility shim is needed.
2. Run selected existing [`test_nvfp4_quantize_te_reference`](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/tests/utils/test_fp4_quantize.py#L936) cases: standard-fast SF-underflow, signed/all zeros, a boundary input, and current per-token strict/4over6 settings, CUDA and CuTe only. This directly exercises the numerical change relevant to NV input quantization and per-token FC1→FC2.
3. Run existing [`test_mxfp8_quantize_extreme_scale_inputs`](https://github.com/flashinfer-ai/flashinfer/blob/fb022756415cc9cad1e1a64ee918860e17638fe8/tests/utils/test_fp8_quantize.py#L1897), including BF16 subnormal scale thresholds, both SF layouts, CUDA/CuTe. Add the existing MXFP4 backend parity/trace exact selectors if weight preparation is exercised. Skip CAKE as requested.
4. Reuse the existing focused split-MoE gate for NVFP4, per-token NVFP4, MXFP4×MXFP8 and MXFP8, preserving PDL and activation coverage. This checks integration after the rebase; it need not become a new dedicated test file or expand fused-finalize coverage.
5. If explicitly checking fused quantization in isolation, compare identical FP32 post-activation values and raw SF/payload bytes at SF underflow and UE8M0 threshold cases. Do not use a BF16 round-trip as the reference for the standard in-place path.

The changed native CUDA header must invalidate the affected C++/CUDA modules. Persistent compilation storage can be retained, but old binaries cannot be treated as new-head validation without source-key verification/rebuild. Previously published raw tables predate this merged CUDA quantizer change; keep their source provenance rather than relabeling them as measurements of the rebased head. No new benchmark or sanitizer conclusion is made here.
