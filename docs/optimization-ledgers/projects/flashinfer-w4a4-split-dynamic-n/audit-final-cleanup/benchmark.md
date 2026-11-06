# Benchmark audit and cleanup

Reviewed all four benchmark files changed by PR7290 against `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. Cleanup starts from retained `74388819899d0abfd1a12102f7cc108bda13c812` in `flashinfer-generality-review`; changes remain unstaged.

## Changes

- `benchmarks/bench_moe_deepseek.py`: copy the default model dataclass into `CFG`. Previously a programmatic `run_benchmark(..., tp_config=2)` mutated the stored V3 preset through an alias, so a subsequent preset selection could inherit the reduced intermediate dimension. The initial configuration and CLI preset-selection path are unchanged.
- `benchmarks/bench_moe_deepseek.py`: reuse `prepare._interleave_linear_and_gate(..., dim=-2)` instead of a local copy. Weight preparation remains outside timing. Remove an empty section heading and correct two docstrings for the supported model/quantization scope.
- `benchmarks/routines/moe.py`: reuse the same existing helper through its existing lazy preparation import. Its removed local helper body is AST-identical to the library helper.

These edits remove 23 net lines across two files. No changes to public flags, model values, quantization recipes or environment scopes, route generation, backend admission, public API calls, native AUTO, graph/CUPTI timing, or result formatting.

## Other changed benchmark files

- `benchmarks/bench_cute_dsl_moe_distributed.py`: retained the architecture-selected gated-weight interleave. It is required by the new Blackwell layout; routing, timing and distributed execution are unchanged by this cleanup.
- `benchmarks/bench_frost_low_latency_w4a16.py`: retained the same architecture-selected layout change. Its CuTe execution is architecture-gated separately from SM120, so the SM100/103 helper does not broaden that backend's admission.

No additional high-confidence benchmark defect found. Kept explicit mode/error branches and per-backend recipe setup rather than introducing a new registry or abstraction. Left unrelated pre-existing scaffolding alone.

## Checks

`python3 audit-final-cleanup/check_benchmark.py` passes with hashes in `benchmark-checks.json`:

- Whole executable ASTs match after the precisely listed preset-copy/helper-substitution normalization; comments/docstrings are excluded.
- 64 coordinate-label permutation cases match the removed DeepSeek helper exactly, including group sizes 16/64, empty experts and multiple leading dimensions. This verifies supported contiguous layout transformations without Torch/CUDA.
- Reproduces the old preset mutation and verifies preset independence across repeated TP 1/2/4/8/1 calls.
- 24 table renderings are byte-identical using all 13 captured native rows for each model/family, including K3 unavailable cells and winner handling.
- 27 stubbed CLI cases preserve stdout, dispatched arguments, model values, EP defaults/overrides, and activation quantization opt-in (`False` by default).

Scoped pre-commit, `py_compile` for both changed files, and `git diff --check -- benchmarks` pass. The exact pre-commit output is in `benchmark-precommit.log`. No GPU work or new numerical/performance measurements were run. The coordinate proof is limited to supported layouts; the shared helper's existing divisibility assertion remains in force.
