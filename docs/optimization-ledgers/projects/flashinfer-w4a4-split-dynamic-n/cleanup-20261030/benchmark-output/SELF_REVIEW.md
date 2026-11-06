# Benchmark output selector

Scope: only `benchmarks/bench_moe_deepseek.py`; output/CLI changes, left unstaged.

- Added `--output-format table|csv|both` and appended `output_format=None` to `run_benchmark` for positional compatibility.
- Default behavior is unchanged: explicit backend selections print CSV; family runs print their existing table.
- `both` prints the unchanged CSV block followed by the same existing family table. No duplicated table builder or timing run.
- Tables remain tied to `--quant-family`; mismatched selectors (including CUTLASS) are rejected before querying CUDA. Cross-family selections retain CSV support.
- Selected subsets and unsupported/missing cells display N/A. The row printer receives the token count explicitly so fully unsupported rows retain their token label and use N/A histogram/winner fields.
- Removed now-unused row-printer swap/finalize arguments; the header retains the same model/contract metadata.

Validation: 63 CPU checks in `check_output.py`, using AST-extracted original functions, fake `BenchResult` rows, and CUDA stubs. Across all four model presets and both families, old default output is byte-identical. Both-format output equals CSV plus table byte-for-byte. Results and `_benchmark_single` call arguments are unchanged. CLI rejects invalid format/family selection before CUDA and forwards valid format selections correctly. The only changed definitions are the format resolver, orchestration output block, row printer, and CLI.

Scoped pre-commit, py_compile and git diff --check passed. No GPU validation or measurements run for this output-only change. No production/kernel/tactic/quantization changes.

Self-review: no blocker found. Intentional behavior is that table format is limited to the selected family; arbitrary cross-family/CUTLASS selections remain available as CSV.
