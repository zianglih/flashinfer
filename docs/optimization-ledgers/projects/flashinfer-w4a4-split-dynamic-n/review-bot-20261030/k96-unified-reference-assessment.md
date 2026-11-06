# CodeRabbit 4422345992: unified exact NVFP4 reference lacks native K plans

Reviewed source: `f173414b5b256f78a5356f611366a0b092944a1d`.
Comment: https://github.com/flashinfer-ai/flashinfer/pull/7290#discussion_r4422345992

**Conclusion: valid exact-reference contract mismatch, high static confidence.** This is a test-oracle defect, not evidence of a kernel regression. No GPU execution or repository edits were performed. Whether the current seeded end-to-end case actually fails was not observed; final activation quantization/BF16 rounding can conceal intermediate accumulation differences.

## Source trace

- `tests/moe/test_unified_moe.py:2784` parameterizes four activations, two quantization pairs and swap mode. The relevant four cases are `swap_ab=True` with NVFP4 weights and NVFP4 activations. Shapes are 8 tokens, H=1024, I=512, eight experts and top-k=2. These cases force unfused finalize.
- `test_unified_moe.py:2841` forces the selected runner with tactic `-1` and then executes the layer. `flashinfer/fused_moe/layer.py:459` forwards the selected tactic; `runners.py:5225` passes it unchanged into the inner runner.
- `runners.py:5159` constructs `CuteDslFusedMoERunner` for this NVFP4 pair and passes `swap_ab`. `cute_dsl/tuner.py:1007` maps `-1` to `DEFAULT_SWAP_AB_MOE_TACTIC`. `blackwell/moe_swap_ab_tuner.py:52` specifies M128/N128, one CTA, automatic FC1/FC2 K steps `(None, None)`, shared CLC enabled.
- `blackwell/moe_swap_ab.py:216` chooses the base FP4 K64 instruction; lines223–227 change native MMA K to96 whenever both operands are FP4, scale-vector size is16 and architecture isSM103. This condition has no token-count or activation-function exception.
- `blackwell/moe_swap_ab_kernel.py:1516` chooses automatic steps from4 or8, then `tile_k = 256 * k_steps // 4`, so this case uses pipeline K tiles256 or512. `_blockscaled_dynamic_mma` at221 emits K96 pairs in each192-wide group, followed by K64 remainder instructions. FC1 has logical K1024 and FC2 has K512: both contain K96 updates for either possible selected tile depth.
- `test_unified_moe.py:2868` calls `cute_dsl_moe_reference` without `mma_k_plans`. Its default at `tests/test_helpers/cute_dsl_moe_swap_ab_reference.py:794` is `(None, None)`; the plans are used separately at865 and914. `blockscaled_matmul` at223 documents and implements default NVFP4 K64 updates. The reference rounds/truncates the accumulator after each native update, so changing instruction boundaries can change the FP32 result before later quantization.
- `tests/moe/test_cute_dsl_fused_moe.py:76` already has a module-scoped autouse compile/cache observer. It records actual nativeK96/tileK selection and constructs a plan per FC1/FC2. However, it only patches that test module's `cute_dsl_moe_reference` alias at134. It is not a shared conftest fixture and does not affect the import in the unified test. `tests/moe/conftest.py` has no corresponding observer.

## Native versus default-reference instruction order

The exact auto-selected tile need not be guessed to establish the mismatch:

| Logical K | Pipeline K tile | Native SM103 plan | Default reference |
|---:|---:|---|---|
|1024|256|`(96,96,64)` repeated4 times|`(64,)` repeated16 times|
|1024|512|`(96,96,96,96,64,64)` repeated2 times|`(64,)` repeated16 times|
|512|256|`(96,96,64)` repeated2 times|`(64,)` repeated8 times|
|512|512|`(96,96,96,96,64,64)`|`(64,)` repeated8 times|

The two possible native plans have the same instruction counts but different update boundaries. Therefore an architecture-only hardcoded K96 plan is insufficient; the oracle should observe the selected pipeline tile for each stage, including cache hits.

## Runtime evidence boundary

The latest cleanup qualification's two pytest targets were `test_gather_gemm_k_tail` and `TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy` in `test_cute_dsl_fused_moe.py`, totaling92 existing tests. They use that module's observer and do not run `test_cute_dsl_typed_activation_matches_flat_reference`. The36 focused smokes also invoke the existing observed exact suite. Consequently those passes do not refute this finding.

Expected failure condition is an SM103 NVFP4 swap-AB sample whose K96-vs-K64 intermediate rounding difference survives the later quantization/combine/BF16 rounding. The source proves differing oracle semantics, but not that every activation parameter or this particular seeded tensor instance fails. SM100 retains native K64; the non-swap NVFP4 arm uses its existing non-exact reference, and W4A16 follows a separate exact reference. Those paths are outside this finding.

## Minimal direction, not implemented

Reuse the existing compile/cache plan observer through a shared test helper/fixture and pass the actual FC1/FC2 `mma_k_plans` to this exact reference call. Keep the production tactic/default unchanged. Avoid hardcodingK96 or a pipeline tile, and preserve the unobserved SM100 default. Merely moving the autouse fixture to conftest without fixing its module-local reference patch would not inject plans into this imported reference call.
