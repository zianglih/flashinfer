# Focused post-retention checks for explicit behaviors and PDL

Plan only; **no GPU test, collection, compile, or sanitizer run has been started by this review**. Parent must authorize GPU5 after the performance screen. Target clean frozen commit `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`, byte-identical to the behavior r2 manifest. Preserve the independent unstaged review copy.

Use ten unchanged existing pytest nodes: eight numerical cases and two host forwarding cases. Do not add a plugin, override API arguments, introduce a repository test, or expand into W4A16/fused/CAKE.

| Cases | Purpose | Actual boundary |
|---|---|---|
| `test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]` | Unfused NVFP4 full chain, gated activation, per-tensor scales | Public API defaults to PDL on; existing tolerance-based reference. |
| `test_deterministic_finalize_numerical_accuracy[relu2-per-token]` | Unfused NVFP4 full chain, ungated activation, original-token and routed scale indexing, T515 partial routing | Public API defaults to PDL on; existing tolerance-based reference. |
| Six selected `test_gather_gemm_k_tail` nodes below | FC1 N16/32/64/128/256, K64/192/384/512, one and seventeen live rows, reversed mapping and poisoned source tail | Explicit PDL off, BF16 output, byte-exact (`rtol=atol=0`) against the existing analytic oracle. One CTA only. |
| `test_moe_core_forwards_enable_pdl[pdl-off]` and `[pdl-on]` | Both public control values reach routing | Host forwarding only; deliberately stops before any routing/GEMM execution. |

Source pin: `tests/moe/test_cute_dsl_fused_moe.py` SHA256 `eaedf38e81d8c2e6f17432b3d8daafb10d73a00da5be23a4c7a79c0795a04f09`.

After authorization, run from the clean frozen source checkout, with the recovered candidate native environment and private CuTe cache recorded. The parent supplies the clean checkout path and unique log/JUnit destinations; verify HEAD/source hashes before execution.

```sh
export CUDA_VISIBLE_DEVICES=5
TEST=tests/moe/test_cute_dsl_fused_moe.py
python -m pytest -q -ra --tb=short \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]" \
  "$TEST::test_gather_gemm_k_tail[16-1-64]" \
  "$TEST::test_gather_gemm_k_tail[16-17-512]" \
  "$TEST::test_gather_gemm_k_tail[32-17-192]" \
  "$TEST::test_gather_gemm_k_tail[64-17-384]" \
  "$TEST::test_gather_gemm_k_tail[128-17-64]" \
  "$TEST::test_gather_gemm_k_tail[256-17-512]" \
  "$TEST::test_moe_core_forwards_enable_pdl[pdl-off]" \
  "$TEST::test_moe_core_forwards_enable_pdl[pdl-on]"
```

The six generated K-tail IDs follow the existing decorator order: route tile, live token count, K. Require exactly ten selected items; collection mismatch is a selector error, not grounds to widen the suite automatically.

Explicit exclusions and evidence boundaries:

- The seven existing `test_w4a8_fused_moe_tactics_and_apis` cases are **fused finalize**, despite explicit `enable_pdl=False`; the wrapper rejects `use_fused_finalize=False` for W4A8 (`cute_dsl/fused_moe.py:1025–1026`). Exclude them under the requested unfused scope. They cannot establish mixed-format unfused coverage.
- Existing GeGLU/SiTU numerical tests omit `use_fused_finalize`, hence use its `True` default. Exclude them rather than alter their calls. Their host configurations were covered by the 9,408-case CPU audit and their arithmetic was not edited; this is not numerical GPU coverage.
- This small existing-test selection does not numerically cover homogeneous MXFP8, all six supported operand/SF combinations, full-chain PDL off, two-CTA numerical cases, or a true zero-work GEMM. No such claim should be attached to it.
- Reuse the already-passed source-pinned five-point native exact screen and true-zero guard as separate evidence; do not rerun them merely to fill this table. Existing full-grid measurements and earlier retained numerical/sanitizer receipts retain their original source scope.
- No broad suite, new exact-reference work, or sanitizer is scheduled here. Unexpected numerical or compilation failures should be investigated narrowly before broadening.
