# Accuracy test consolidation

Committed and pushed to the primary PR7290 branch as `658a0c8942c7454050f990c0be3083aa61b6a89f`, on top of `4376662a`. Only `tests/moe/test_cute_dsl_fused_moe.py` changes. No production, reference or sanitizer changes.

| Removed standalone test | Existing destination | Preserved coverage |
|---|---|---|
| `test_swap_ab_gemm_k_tail` | `test_gather_gemm_k_tail` | All 60 swap-AB cases: K64/128/192/256/384/512 × tokens1/17 × N16/32/64/128/256. Original 16 legacy cases remain. Shared FP4-one input, reversed token map, deliberately NaN-poisoned SF guard row, one-CTA swap tactic, PDL off, exact sigmoid(1) output. |
| `test_mxfp_unfused_public_apis` | `TestCuteDslFusedMoeFunctional.test_deterministic_finalize_numerical_accuracy` and its existing `_run_numerical_accuracy` | All 12 MX cases: MXFP4×MXFP8/MXFP8×MXFP8 × SwiGLU/SiTU-gate/SiTU-gate+up × N16 one-CTA/N128 two-CTA (CLC on). Same seed, geometry (tokens17,H256,I128,E2,topk2), quantization, weights, routing and explicit tactics. Both functional and wrapper APIs still compare bit-exactly to the shared oracle. Both APIs still reject BF16 weight inputs. |

The existing four deterministic-finalize NVFP4 cases are unchanged in scope. The SiTU nonvacuity check now asserts the SiTU and plain SwiGLU references differ after both real outputs have passed exact comparison, instead of repeating mean-error comparisons with an already exact output.

The common input/reference/assertion helpers explicitly support the two MX modes. `_MOE_QUANT_MODES` and `_MOE_QUANT_MODE_CASES` remain unchanged, so unrelated NVFP4/W4A16 tests do not acquire unsupported MX combinations. The deterministic test retains flattened pytest parameter fields, including `use_per_token_activation`, so the existing SM107 autouse skip fixture still reads them through `callspec.params`. Existing architecture markers and the module's K96-plan observer remain. No new standalone test functions or files were added.

No K64/K192 coverage was dropped or forced through invalid public full-MoE dimensions: those cases remain in the existing direct FC1 accuracy test. The full-MoE MX cases use valid H/I multiples of128.

## Static validation

- `python3 -m py_compile tests/moe/test_cute_dsl_fused_moe.py`: passed.
- `python3 ../upstream-integration-20261029/design-audit/validate_test_consolidation.py`: passed. This reads the before/after AST and evaluates only parameter expressions with lightweight local stand-ins; it verifies all76 K-tail cases, all4 existing NVFP4 cases and all12 MX cases are preserved, and exactly the2 requested standalone test functions are removed.
- `/opt/homebrew/bin/pre-commit run --files tests/moe/test_cute_dsl_fused_moe.py`: passed after formatter changes.
- `git diff --check`: passed.
- GPU execution:92 passed,1132 CuTe deprecation warnings,633.19 seconds,exit0. One B300 under `nvcr.io/nvidia/pytorch:26.05-py3`,CuTe4.8.0,pytest8.4.2. The run started only after all MegaMoE measurements finished. Its full13,245 tracked-file manifest matches the pushed658a0c89 tree; the test file SHA256 is `5a8b73eb23da42036522aacfda774785672c50f463c2ee94dce9743453b80e01` before and after execution. Full logs/receipts are in `../megamoe-glm5/test-consolidation/`.

Completed scoped GPU run:

```sh
pytest -q --full tests/moe/test_cute_dsl_fused_moe.py::test_gather_gemm_k_tail tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy
```

Completed scope:76 gather cases +16 deterministic-finalize cases =92 passed tests, zero skips. The second node includes4 NVFP4 cases and12 MX cases; each MX case exercises both APIs. Commit hooks and final diff checks also pass. No sanitizer was run.
