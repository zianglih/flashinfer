# Benchmark and test cleanup audit

Source: `flashinfer-cleanup-review`, retained base `33b7e5260132eb4ba2fdfdd97bd71a892f04a481`. Audited the owned PR diff against `002529e1`. Changes remain unstaged; no commit, push, GPU run, sanitizer run, or reference self-test.

## Changes

- `bench_moe_deepseek.py`: forward the actual `swap_ab` and `use_fused_finalize` values to reporting helpers. The old helpers used the default support predicate even when the benchmark ran another mode. This fixes notices and missing-result validation without touching backend execution or table formatting.
- `sanitize_cute_dsl_moe_swap_ab.py`: select the mode-specific GEMM once and reuse the common prepare/finalize kernel tuple. Explicit invalid-mode handling and the per-token addition remain unchanged.
- `cute_dsl_moe_swap_ab_reference.py`: reuse the existing `_mul_rn_f32` helper for three identical inline-assembly multiplications. Expanded AST equivalence confirms the same arguments, `mul.rn.f32`, constraints, purity, pack value, casts and operation ordering.

Scope: 3 files, 33 added / 49 removed lines. Distributed benchmark, all four PR-changed MoE test/helper files, and W4A16 reference are byte-identical to the retained base. All accuracy test bodies, parameter matrices and assertions are preserved. Existing comments and licenses are preserved.

## Exact reporting differences

| Model/family | Mode | Intentional change |
|---|---|---|
| V3, V41F, N3U / MXFP | non-swap-AB, unfused | Reports that both CuteDSL MX modes require swap-AB for unfused finalize; missing CuteDSL rows render N/A instead of raising the old erroneous missing-result error. |
| K3 / MXFP | swap-AB, fused or unfused | Removes false CuteDSL MXFP4x8/MXFP8 SiTU unsupported notices. TRTLLM MXFP8 and BF16 still report no SiTU kernel. |
| K3 / MXFP | non-swap-AB, fused or unfused | Unchanged: CuteDSL MX modes require swap-AB for SiTU; TRTLLM MXFP8/BF16 are unsupported. |
| K3 / NVFP4 | either swap-AB or finalize setting | Unchanged: TRTLLM PER-TOKEN and BF16 are unsupported; CuteDSL and TRTLLM NVFP4 remain eligible. |
| Other combinations | all | Unchanged. |

No TRTLLM support predicate was altered. K3 TRTLLM MXFP4x8 remains supported. Tables retain their existing column widths, backend order, latency/TFLOPS formatting, speedup calculations and winner selection.

## CPU proof

`check_bench_test_cleanup.py` extracts pure reporting and command-building functions without importing Torch/CUDA or executing reference arithmetic. It compares current source to retained `33b7`.

- 32 printed-output fixtures: four models × two families × swap-AB on/off × fused on/off. Every table/header/footer line is identical except the five intentional notice changes above. The old row formatter, supplied the correct support predicate, is byte-identical to the current formatter. The three formerly erroneous missing-row cases are recorded separately.
- AST assertions prove both `run_benchmark` report calls forward the actual local `swap_ab` and `use_fused_finalize` values; removing only the newly forwarded reporting flags yields the exact prior `run_benchmark` AST. All measurement, quantization, graph, autotune, backend and allocation functions are unchanged.
- Every missing supported backend still raises the same error. Missing unsupported TRTLLM rows remain N/A.
- Sanitizer: five mode mappings, eight mode/per-token kernel lists, and 24 tool/mode option lists match. Invalid-mode errors match. Worker/test body and parameter ASTs are identical. No script reference exists in repository CI paths; it remains outside pytest discovery.
- Reference: expanding `_mul_rn_f32` in the two modified kernels yields exactly the prior AST. This is a source-equivalence proof, not a numerical oracle self-test.

Evidence: `bench-test-checks.json`, `bench-table-fixtures/`, `bench-test-source.json` (final source SHA256), and `bench-test-precommit.log`.

## Commands and boundary

From `flashinfer-cleanup-review`:

```sh
python3 ../cleanup-20261028/check_bench_test_cleanup.py
pre-commit run --files benchmarks/bench_moe_deepseek.py scripts/sanitize_cute_dsl_moe_swap_ab.py tests/test_helpers/cute_dsl_moe_swap_ab_reference.py
python3 -m py_compile benchmarks/bench_moe_deepseek.py scripts/sanitize_cute_dsl_moe_swap_ab.py tests/test_helpers/cute_dsl_moe_swap_ab_reference.py
git diff --check
```

All passed. Pre-commit ran the applicable file checks, Ruff checks and Ruff formatting. No additional cleanup was justified beyond these changes: consolidating benchmark allocation branches would affect execution order, and merging the W4A16/blockscaled reference contracts would obscure their distinct accumulation behavior. GPU validation remains owned by the parent task's planned focused existing exact/API gate.
