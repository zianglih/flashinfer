# CodeRabbit FP16 finalize findings: independent source audit

Reviewed exact PR head `f9dd3c10541e087b716772245a9d033499745048` against pre-PR base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`. Working tree was clean when inspected. No repository edits, GPU runs, or GitHub replies were performed by this reviewer.

## r4045303066: W4A16 FP16 output regression

**Not a valid regression. High confidence.** Both public W4A16 entry paths already construct `CuteDslFusedMoEW4A16Runner` with the requested `output_dtype`; its unchanged constructor raises `ValueError("W4A16 only supports BF16 output")` for FP16 before reaching the launcher/finalizer.

| Guard-chain point | Head lines | Base lines |
| --- | --- | --- |
| Wrapper constructs runner with output dtype | `fused_moe.py:765–772` | `fused_moe.py:764–771` |
| Functional API constructs runner with output dtype | `fused_moe.py:1327–1333` | `fused_moe.py:1326–1332` |
| BF16-only constructor guard | `tuner.py:1047–1048` | identical |
| Runner dispatches internal launcher | `tuner.py:1240–1255` | identical |

All paths above are under `flashinfer/fused_moe/cute_dsl/`.

The internal `blackwell/moe_w4a16.py:362–385` launcher has no `output_dtype` argument. A repository-wide call search found only the guarded runner as its production caller and one direct native test, which explicitly allocates BF16 `moe_output` (`tests/moe/test_cute_dsl_fused_moe.py:1452–1467`). It is not re-exported by the package-level public `__init__.py` files. Its scratch buffers and output-pointer types were already hardwired BF16 at the base (`moe_w4a16.py:83–88,283–287`).

A manually supplied FP16 output tensor that bypasses the constructor is not a previously working FP16 conversion path: the old native unpermute dispatch selects its input/output element type from the BF16 scratch input (`moe_utils.py:292–312`), and native `moeUnpermuteKernel` has the same `InputType` for input and output (`moeUtils.cu:159–160`). It would write BF16 bits into that FP16 allocation. A native fallback would restore that unsupported behavior, not preserve a valid FP16 result.

Suggested reply substance: the BF16-only output contract predates this PR, both public W4A16 entry points enforce it via the unchanged runner, and the private helper does not remove supported FP16 output. No fallback is necessary.

## r4045303081: `_moe_core_impl` FP16 deterministic regression

**Not a valid regression. High confidence.** The pre-PR W4A4 deterministic path allocates `gemm2_output` using `output_dtype`, but immediately supplies that buffer to FC2 with `out_dtype="bfloat16"`. The FC2 wrapper checks the provided output tensor dtype and raises before native unpermute can be called.

| Guard-chain point | Head lines | Base lines |
| --- | --- | --- |
| Unfused scratch allocated with requested output dtype | `fused_moe.py:475–479` | `fused_moe.py:476–480` |
| FC2 output buffer argument | `fused_moe.py:493` | `fused_moe.py:494` |
| FC2 expected output dtype is BF16 | `fused_moe.py:499` | `fused_moe.py:500` |
| Existing FC2 dtype mismatch error | `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:588–596` | identical |
| Finalizer executes only after FC2 | `fused_moe.py:508–521` | `fused_moe.py:509–520` |

The FC2 wrapper and runner guard files have no changes in this PR. The older native standalone helper's separate ability to process FP16 input/output does not establish FP16 support in this BF16 FC2 pipeline.

Suggested reply substance: at the base revision, `output_dtype=torch.float16, use_fused_finalize=False` already fails FC2's unchanged dtype check; replacing the later finalizer does not introduce that failure. A fallback placed at finalize would never make that input pass the earlier guard. Keep the BF16-only helper and avoid expanding this optimization into a new FP16 pipeline implementation.

## Useful stable source links

- [Base W4A16 BF16 guard](https://github.com/flashinfer-ai/flashinfer/blob/eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095/flashinfer/fused_moe/cute_dsl/tuner.py#L1047-L1048)
- [Head W4A16 BF16 guard](https://github.com/flashinfer-ai/flashinfer/blob/f9dd3c10541e087b716772245a9d033499745048/flashinfer/fused_moe/cute_dsl/tuner.py#L1047-L1048)
- [Base W4A4 FC2 call](https://github.com/flashinfer-ai/flashinfer/blob/eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095/flashinfer/fused_moe/cute_dsl/fused_moe.py#L476-L506)
- [Unchanged base FC2 output dtype check](https://github.com/flashinfer-ai/flashinfer/blob/eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095/flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py#L588-L596)

Source tracing only; root is preparing a separate host-only guard repro. No fresh GPU numerical claim should be attached to these replies.
