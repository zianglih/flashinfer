# Layout and public helper review fixes

Source: PR7290 HEAD `14a338579`, local unstaged changes only.

- `prepare_cute_dsl_weights` records integer `gated_weight_group_size` for gated views. `CuteDslRunner.pack_inputs` validates 16 versus 64 before launch. Non-gated views are unaffected.
- Untagged manual views retain the published 64-row contract: `MoEWeightPack.prepare_for` explicitly accepts caller-prepared native dictionaries; the preexisting `test_cute_dsl_mxfp4_pack_uses_unpacked_mxfp8_and_no_fc2_scale` and `_make_packs_and_config` use these dictionaries. New swap-AB gated manual views must supply the 16-row tag. There is no separate contract version or fallback kernel.
- `MoEConfig` rejects mixed swap/non-swap CuTe DSL candidates only for gated activations, since the unified pack stores one view per backend key. Non-gated candidates share the identical layout and remain allowed.
- `CuteDslConfig` documents that static `prepare_weights` requires explicit `swap_ab=True` even when accessed through an instance. It retains the existing static API pattern.
- `interleave_cute_dsl_moe_weights` is exported through the existing `flashinfer_api` decorator and utility autosummary. It performs pure 16/64-row permutation on CPU or CUDA tensors; execution architecture restrictions remain in the existing consumers.
- `MoEWeightPack` view typing now admits preparation metadata. Its representation already handles arbitrary values. The prepared view has an explicit mixed tensor/integer annotation.

## Validation selectors

CPU-safe existing-file tests (13 total cases including the existing non-gated mismatch guard):

```sh
pytest -q tests/moe/test_unified_moe.py::TestExpressiveness::test_cutedsl_mixed_layout_candidates tests/moe/test_unified_moe.py::TestExpressiveness::test_cutedsl_weight_interleave_on_cpu tests/moe/test_unified_moe.py::TestMoERunnerSupport::test_cute_dsl_mxfp4_pack_uses_unpacked_mxfp8_and_no_fc2_scale tests/moe/test_unified_moe.py::TestMoERunnerSupport::test_cute_dsl_rejects_gated_rows_for_non_gated_activation
```

Existing GPU accuracy coverage:

```sh
pytest -q tests/moe/test_unified_moe.py::test_cute_dsl_typed_activation_matches_flat_reference
```

Parent also added assertions for the metadata returned by real `CuteDslConfig.prepare_weights` calls in the existing MX accuracy matrix and explicit public tactic test in `tests/moe/test_cute_dsl_fused_moe.py`. These cover prepared 16/64-row views and absence of metadata for non-gated views without a new test function.

Local checks: Ruff lint, Ruff format check, Python AST parse, and `git diff --check` passed. No local pytest or GPU execution by this agent; root coordinates device validation.

## Scope review

No kernel, tactic, quantization arithmetic, public argument, cache key, or routing change. Existing callers that extract tensors from prepare dictionaries remain valid; the accuracy matrix uses explicit kernel arguments, so the metadata does not enter the flat CUDA API. Stable unannotated non-swap manual views stay accepted. Mixed gated candidates now fail before autotuning rather than sharing incompatible rows.
