# SM100 CuTe DSL NVFP4 quantization alignment

**Publication update (2026-10-26):** committed and pushed the validated three-file AMAX consolidation as `76582e976bd01aee5404cc3342eb5752031835fe`. PR #7372 and the remote branch match; the primary checkout is clean. The review-state notes below describe the pre-commit validation snapshot.

Current reference contract describes three **unstaged** files on the primary PR branch in `flashinfer/`. Published and local HEAD remain `5ead7268e7e3756abcc3c4ca129da42c818de3c2`; no AMAX-unification changes are committed or published. Production is unchanged from that head and measured arithmetic commit `599254292dce7b44b8048b4dc6e252abc118f2fd`. The original ABBA measurements and accepted minor differences remain unchanged, with no performance reruns. Baseline `c1131f1591d3538e00abcdb5b9fa7e0e17962dff` incorporates PR7290 `65c2c5c4635257d920ddb7524096f2e67bfcc9e3` and PR7196 `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939`.

## Two input contracts, one block implementation

The shared [utils_fp4.py](/Users/ziangli/playground/projects/flashinfer-cute-dsl-moe-exact-reference/flashinfer/tests/test_helpers/utils_fp4.py) now has two entry points distinguished by the scale information the caller supplies:

- `ref_fp4_quant(x, global_scale, block_size, sf_use_ue8m0=False)` preserves the supplied-encode-scale contract, arbitrary leading dimensions, and two-result return: unpacked E2M1 values plus linear FP32 block scales. Its NV branch is standard-fast only; its approximate UE8M0/MXFP4 branch remains unchanged.
- `ref_fp4_quant_te(x, global_amax, block_size=16, per_token_rowwise=False, nvfp4_4over6_config=None, disable_fp4_quant_fast_math=True, global_scale_inv=None)` accepts original tensor or row AMAX. `None` config selects standard NVFP4; a resolved config selects 4over6. The explicit arithmetic flag selects strict or fast quantization independently of candidate error-scoring mode. Optional scalar `global_scale_inv` applies only to per-token normalization and preserves the runtime API's scale contract. Per-tensor calls derive an RN encode scale from the supplied AMAX before strict or fast candidate arithmetic.

The AMAX API always returns `(q_unpacked, linear_sf_uint8, global_or_row_decode, pick_four_bool)`; the mask is all false for standard NVFP4. It requires 2D input with SF16-aligned rows. Both NV entry points share `_ref_nvfp4_quant_blocks`, which now includes candidate construction, conversion, and 4over6 error scoring/selection. `ref_fp4_quant_4over6_te` and `ref_nvfp4_quant_per_token` are removed, along with the separate selector; no forwarding aliases remain. Neither entry point reads environment state or invokes a production quantizer. Fast arithmetic requires the independent CUDA reciprocal primitive.

The existing TE-reference matrix preserves all 101 regular strict cases and adds the corresponding fast-mode cases, for 202 regular cases, plus 12 explicit-recipe tests. Both fast-math environment names are controlled together, and per-token decode scales compare storage bits against the returned reference. The published 40 ordinary NVFP4 and 16 linear-padding cases still compare E2M1/E4M3 bytes at `rtol=atol=0`, while UE8M0 tolerances remain unchanged. Tests share `pack_fp4_values` for byte packing.

## Fused FC1 quantization

“Fused” here means activation and quantization in the FC1 epilogue. It is independent of `use_fused_finalize`, which controls the later routing combine. Exact end-to-end tests still require standalone deterministic finalization.

For SF16 NVFP4 with E4M3 scales, `Sm100BlockScaledMoeEpilogue._store` calls the existing `_nvfp4_standard_quant_from_amax(amax, global_scale, False)` helper. Given a block of 16 FP32 activated values:

1. Reduce their absolute maximum in FP32.
2. Form `sf_high = RN(global_scale * RN(amax * rcp.approx.ftz(6)))`.
3. Convert to saturating RN E4M3 `sf`.
4. Form `multiplier = rcp.approx.ftz(RN(float(sf) * rcp.approx.ftz(global_scale)))`; select zero when `sf == 0`.
5. Multiply each original FP32 activation by the multiplier with RN FP32 packed multiplication and convert to saturating RN E2M1.

This is the standalone standard fast scale/multiplier contract. The epilogue retains FP32 values until E2M1 conversion; the public standalone API's FP16/BF16 input constraint does not introduce an intermediate round trip into FC1. An isolated boundary control detects 112 changed payload bytes when a BF16 round trip is inserted.

No 4over6 candidate search is added to the fused per-tensor epilogue. The standalone strict-mode environment variable does not change this path. There is no TE per-tensor parity claim: FlashInfer receives a caller-supplied global scale rather than the original tensor AMAX.

The changed branch explicitly requires E2M1 output, E4M3 SF, and SF vector size 16. Other FP4 formats and the MXFP8 output branch retain their existing arithmetic.

## Per-token standalone requantization

Production is unchanged. FC1 stores activated values in FP16/BF16, and the existing standalone per-token quantizer consumes those rounded values. Input token scales are indexed by original token; the returned FC1 scales belong to routed rows used by FC2.

The [MoE reference](/Users/ziangli/playground/projects/flashinfer-cute-dsl-moe-exact-reference/flashinfer/tests/test_helpers/cute_dsl_moe_reference.py:871) calls `ref_fp4_quant` for the fused per-tensor branch. For per-token output it converts activated values to the production output dtype, derives row AMAX, and calls the unified `ref_fp4_quant_te` with the resolved recipe, arithmetic mode, and actual `fc2_input_scale` as `global_scale_inv`. Row-scale construction remains distinct from shared block quantization.

Standard strict quantization deliberately has different zero-SF behavior:

- A zero-AMAX block uses a zero multiplier.
- A nonzero block whose E4M3 SF underflows to zero still uses the clamped strict FP32 multiplier. The reference now tests `block_amax == 0`, matching `nvfp4_compute_output_scale_rn`, rather than masking every zero-SF block.
- Standard fast quantization masks a zero stored SF. Fast 4over6 retains its existing candidate-specific behavior; strict and fast 4over6 scoring/selection are unchanged.

Strict per-token 4over6 remains TE-identical because row AMAX is available. Quantization fast math and 4over6 error-scoring fast math remain independent settings.

## MX and exact API coverage

MXFP8 activations with either MXFP8 or MXFP4 weights share the existing independent MXFP8 quantization reference; this round changes no MX production arithmetic. The latest refactor supports unfused public `w4a8` and `mxfp8` calls. All 12 existing public MX cases now compare both functional and wrapper outputs against the shared exact MoE oracle, preserving activation differentiation and API validation. The old statement that public W4A8 requires fused finalize no longer applies.

The shared exact block-scaled oracle is limited to SM100/SM103, finite supported accumulator arithmetic, single-GPU/local-expert execution, and standalone finalization. W4A16 uses its separate shared reference. Existing supported SM107 block-scaled and fused-finalize paths preserve their prior mathematical tests.

## Current validation status

- **Final folded-source pass, still unstaged:** 214 quantization tests (202 strict/fast matrix +12 explicit-recipe), 96 ordinary/padding tests, and 42 MoE tests: **352 selected pytest cases**. Independent controls passed 72 per-token cases plus 5 empty cases, 4 zero-SF/signed-zero modes, and 30 isolated epilogue/standalone cases. The BF16-intermediate negative control changes 112 bytes.
- All six `amax-ref-folded-*` runs exited 0; see the [receipts](/Users/ziangli/playground/projects/flashinfer-cute-dsl-moe-exact-reference/epilogue-alignment-20261026/receipts) and [final source verification](/Users/ziangli/playground/projects/flashinfer-cute-dsl-moe-exact-reference/epilogue-alignment-20261026/receipts/artifacts/amax-ref-folded-final-source-verification.json). Every tracked remote file matches the primary unstaged overlay, including `utils_fp4.py` SHA-256 `4c4ef34dcd82ae98affa07f09ad56d8187dc063b2d0a6e43e9041fdb443b949f`. These are final folded-source results; the matching pre-fold runs remain separate and are not added to the counts. Published HEAD remains `5ead7268e`, and no new benchmark results are claimed.
- [VALIDATION.md](/Users/ziangli/playground/projects/flashinfer-cute-dsl-moe-exact-reference/amax-reference-20261026/VALIDATION.md) records the exact commands, results, and source hashes. The dedicated AMAX devbox was released after final collection and verification; the primary three-file change remains unstaged.

## Historical validation

- Published `5ead7268e` consolidation: **138 selected pytest cases passed** — `centralized-ref-standalone-r1` 96 (40 ordinary NV exact +16 padding exact +40 unchanged UE8M0), `centralized-ref-moe-r1` 38, and `centralized-ref-4over6-r1` 4 unfused cases. All three runs exited 0.
- Published-state independent controls: `centralized-ref-epilogue-r1` passed 30 exact cases (14 direct FP32, 8 standalone CuTe DSL, 8 standalone CUDA); the BF16-intermediate negative control changes 112 bytes. `centralized-ref-compat-r1` passed 72 reference API compatibility cases and one empty case: 48 per-tensor standard-fast NV cases across ranks 1–4, FP16/BF16/FP32, float/tensor global scales, and strided/contiguous inputs, plus 24 legacy MX cases on CPU/CUDA. Both exited 0. The four source overlay hashes match committed `5ead7268e` files; `centralized-ref-final-source-verification.json` confirms all tracked remote source matches that published commit. That dedicated rerun devbox was released after final receipt collection.
- Earlier arithmetic-alignment validation at `599254292` remains separate: 30 isolated cases, 72 per-token cases, 5 empty helper cases, and 4 zero-SF/signed-zero modes passed. Integration passed 66 W4A16 split/backend cases, an 18-case fixture overlay, and the final in-tree selections `final-blockscaled-r1` (122) and `final-w4a16-unified-r1` (6). The final selections plus the 66 W4A16 cases comprise **194 unique selected pytest cases** at that earlier state. The fresh 138-case selection is not added to this total because coverage overlaps; the full 194-case matrix was not repeated for consolidation.
- Performance evidence is unchanged: same-GPU ABBA on V3, V4.1 Flash, and Kimi K3, all 13 token counts; T1/2 excluded only from aggregates. Overall before/after speedups are 0.998516x, 0.998485x, and 1.003286x respectively. The user accepted these minor differences. All 12 receipts match the measured source, whose production code is unchanged in `5ead7268e` and the unstaged AMAX review. See `epilogue-alignment-20261026/benchmark-summary.json` and `epilogue-alignment-20261026/PROTOCOL.md`; no parent-PR timing was used as the before arm, and no new performance run was needed for test/reference-only consolidation.
- Historical only: 34 native-output MMA replay cases and 4,000 exact-dyadic model checks. The arithmetic model is unchanged; these are not reruns or evidence for the new epilogue formula.
