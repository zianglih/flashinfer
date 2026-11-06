# PR #7290 test and trace scope audit

Reviewed `flashinfer-generality-review` at retained `74388819899d0abfd1a12102f7cc108bda13c812` against PR base `a65d5b09e7e4c4c5c160b0161c48becd100b3970`, following repository `AGENTS.md`, `CLAUDE.md`, and `docs/code_review_guidance.md`.

## Test cleanup left unstaged

Only `tests/moe/test_cute_dsl_fused_moe.py` changed in this audit (+19/-22 lines):

- Compare complete legacy tactic-parameter dictionaries against explicit K/scheduler overrides instead of an exclusion-key loop and separate K assertions. Preserve strict boolean identity checks, all 360 tactic roundtrips, malformed-input checks, and Rubin rejection checks.
- Describe the test scope as block-scaled MoE, including W8A8.
- Shorten the unsupported-geometry explanation and explicitly scope missing padding-CTA support to Rubin; Blackwell now supports the padding path.

No test functions, parameter cases, selectors, or new repository test files were added or removed. `test_cute_dsl_moe_can_implement.py` and `tests/moe/utils.py` remain unchanged from the retained implementation. The 68 focused selected test functions, including their parameter decorators, are AST-identical to retained HEAD. Existing fused W4A16 tests were not expanded.

## Coverage retained and why

- K tails and routed-token N cover the new operand orientation and partial route tiles.
- Capacity and cluster tests express the supported channel-M geometry, including M512 reuse; the old N192 geometry rejection remains meaningful.
- Tactic JSON/legacy/parser tests protect the internal K pair and strict static/CLC boolean while keeping public API signatures unchanged.
- Zero-count expert assignments retain the concrete count-conservation regression, including empty local routing.
- Public MX W4A8/W8A8 tests cover the new unfused function/wrapper behavior, SiTU and the new preparation path. Their exact assertion compares APIs using the same kernel; the numerical trace remains approximate.
- Shared W4A16 test preparation still uses the same architecture-specific gated-weight layout helper. No duplicate split reference was introduced.

No further experiment-only test additions were identified that could be removed without deleting coverage of an actual retained contract.

## Read-only API/trace findings

The W8A8 preparation/API scope remains explicit: SM100/SM103 public function/wrapper support, without claiming unified `MoELayer` support. FP8 weight payload width, E8M0 scales, MX SiTU, and the nonzero local expert offset are correctly carried through the added path. Root owns the corresponding source cleanup.

Confirmed a trace-reference defect during this audit: NV W4A4/W4A16 previously skipped the 6-D MMA-scale inverse and the architecture-specific gated-row inverse. The common expert reference expects contiguous up/gate halves; FP4 dequantization itself never undoes those rows. Root repaired the trace reference only, including byte-valued NV scales and 2-D/3-D activation-scale views. This does not change native kernel arithmetic or the shared bit-exact W4A16 test reference.

The trace schema describes the logical two-dimensional activation-scale view. `TraceTemplate.build_fi_trace_fn` emits declared dimension names rather than preserving a trailing singleton. Blackwell preparation validates contiguous byte count rather than rank, so both physical views have the same supported semantics; the updated trace reference normalizes them explicitly. MX remains a strict two-dimensional public scale contract. A new rank-dependent trace-template factory is unnecessary for this correction.

## Validation

- Ruff check, Ruff format check, and `git diff --check` passed for the three owned test files.
- `tests-cpu/cpu.json`: 12 existing source-extracted tactic-test invocations passed, including all 360 JSON roundtrips. This executes the real pure-Python tuner functions and existing test bodies with only the import/raises plumbing stubbed; it is not a CUDA module-import or GPU test.
- `tests-cpu/selector-preservation.json`: all 68 selected test function ASTs/decorators unchanged.
- `trace-local-cpu.json`: 32 CPU Torch layout/dequantization cases passed. Twenty-four NV cases cover W4A4/W4A16, SM100/SM103 up16-gate16, SM107 up64-gate64, gated/ReLU2, E4M3/uint8 weight scales, 2-D/3-D activation scales, and per-token multiplication. Eight MX cases preserve W4A8/W8A8 preprocessing. All weights use actual strided 6-D MMA scales. The architecture query alone is stubbed; tensor operations are real CPU Torch.
- Trace source tested: `dc11d80a961d745784bce64fd8ab889e8d5082e0615cc8fa966d045a1fbf05f6`; preparation helper source: `fb5b71b9fa6e5bd37de1bc70507b2f743c7ea9781368ace61c970dda23d51118`.
- CPU runtime: local Python 3.12.12 / Torch 2.13.0 in `audit-final-cleanup/.venv-cpu`; exact packages in `cpu-runtime-requirements.txt`. CUDA was never initialized. Torch emitted an absent-NumPy warning; no NumPy operation was used and every assertion completed.

The initial attempt to use the prior devbox failed before program execution because the devbox no longer exists. Raw output and the corrected failure receipt are preserved as `trace-cpu.*` / `trace-cpu-launch.json`; local results are separate. No GPU checks, benchmarks, source deployment, staging, commits, or pushes were performed in this audit.
