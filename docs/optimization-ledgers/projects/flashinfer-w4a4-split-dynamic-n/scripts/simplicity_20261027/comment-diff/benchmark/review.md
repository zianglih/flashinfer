# Benchmark, test, docs, and trace comment pass

Start: `54f5c682bbaa52a23a46b6bb76e3cfdce347ec97`; upstream comparison: `215f83cb`.

Reviewed all 11 PR-modified files in this ownership scope. Four files have only prose restorations:

- `benchmarks/bench_moe_deepseek.py`: restore upstream wrapper/functional API wording and header/row docstrings. Restore original local-expert, alpha, bias, result-extraction, and winner comments beside the corresponding relocated code.
- `flashinfer/trace/templates/moe.py`: restore the original alpha-folding reference description and FP4/FP8 packing comment; both remain accurate. Keep the 6-D scale and gated-interleave explanations.
- `tests/moe/test_cute_dsl_moe_can_implement.py`: restore the original generic opening and pure-classmethod wording. Keep the changed channel-M/route-N explanation because the old SFC/partial-N restriction is obsolete.
- `tests/moe/utils.py`: restore the original accurate test-tensor description.

Retained necessary documentation: DeepSeek-V3/V4.1/K3 model and backend descriptions, per-token recipe and timing boundaries, explicit unsupported backend cases, architecture-dependent weight layout, independent GEMM channel geometry, and the two SiTU capability-table entries. No code or `TraceTemplate` metadata strings changed. No unrelated original comments were shortened or removed.

Validation:

- `python3 scripts/simplicity_20261027/comment-diff/benchmark/verify.py` passes: all 10 Python files have identical executable ASTs after stripping only recognized module/class/function docstrings; the Markdown file is byte-identical. All compile as Python source.
- Scoped pre-commit passes, including mypy and Ruff:
  `/opt/homebrew/bin/pre-commit run --files benchmarks/bench_moe_deepseek.py flashinfer/trace/templates/moe.py tests/moe/test_cute_dsl_moe_can_implement.py tests/moe/utils.py`
- `git diff --check -- benchmarks tests docs flashinfer/trace` passes.
- `proof.json` binds all before/after hashes, `comment-only.patch`, and the verifier. Initial snapshots are under `before/`.

No GPU work, runtime test claims, commit, or push. Edits are unstaged and frozen for handoff.
