# Rebased benchmark, test and trace audit

Audit base: `215f83cb`. Audit-start source: `24da0138fd67dc7172ef3dd9e6d1358e2b059a53`. The parent subsequently captured the cleanup in `3c0ec82f13ac7469440ad1acaeb43f8158986329`; the checks below bind the current source bytes. No benchmark or GPU run was performed by this audit.

## Changes

- `tests/moe/test_cute_dsl_fused_moe.py`: restored upstream `TestRubinMultiCtaTacticRejected` byte-for-byte. Removed the extra Blackwell cases and renaming that had expanded unrelated Rubin rejection coverage. Removed the six-case `test_assignments_match_requested_expert_counts` regression with the parent's removal of the unrelated ghost-token sampler patch. Kept the existing numerical/layout, public MX/SiTU, and internal K/scheduler tactic coverage needed by the replacement implementation.
- `flashinfer/trace/templates/moe.py`: reused `_dequantize_fp4_hidden_states` for homogeneous MXFP8 weights instead of duplicating its FP8/block-scale arithmetic. Restored upstream line wrapping of one unchanged description. The reference retains the necessary six-dimensional scale inverse, NV scale byte reinterpretation, shared architecture-dependent up/gate inverse, local expert offset, and per-token activation multiplier.

## Files deliberately unchanged

- All four changed benchmark files remain byte-identical to audit-start HEAD. This preserves the six table formats and columns, V3 EP8/V4.1 EP4/Kimi K3 EP8 presets, per-token recipe, N/A capability handling, initial NV quantization opt-in with default `False`, native AUTO, public API calls, and TRT timing boundaries. The smaller distributed/frost/routine deltas are the required shared weight-layout selection; Rubin retains its original group size.
- `test_cute_dsl_moe_can_implement.py`, `test_cute_dsl_mxfp8_moe.py`, `test_unified_moe.py`, and `tests/moe/utils.py` are unchanged in this pass. Their PR deltas cover replacement-kernel geometry, public homogeneous/mixed MX support and SiTU, or shared weight preparation. Restoring old N192 or channel/routing-axis assertions would incorrectly test the superseded implementation.
- Tactic parser tests retain legacy Rubin checks because the shared parser now accepts optional Blackwell K/scheduler fields. These checks guard compatibility rather than change Rubin behavior.

## Verification

- Scoped pre-commit passed for the two edited files. The parent's complete cleanup pre-commit also passed; log: `precommit.log`.
- `check_owned_scope.py`: 13 source/AST checks pass. It proves all four benchmark files and four other test files unchanged, the Rubin class exactly upstream, the test delta limited to the two described changes, and the trace AST delta limited to the two MX weight dequantization calls. Syntax compilation and `git diff --check` pass. Receipt: `owned-scope-checks.json`.
- `check_trace_equivalence_cpu.py`: **32 real CPU Torch cases pass**, using Torch 2.13.0 in `audit-final-cleanup/.venv-cpu`. Both before and after references produce identical dequantized expert inputs; the cases also check independent expected values, 6D MMA scale layouts, E4M3/uint8 storage, 2D/3D activation scales, per-token multipliers, nonzero expert offset, gated/ReLU2 activation, and the unchanged SM107 group64 path. Only architecture discovery and the expert-call sink are stubbed. No CUDA context is initialized. Results: `trace-equivalence.json`; source payload and old evidence are preserved.
- `check_tactic_tests.py`: 12 existing structural cases over 360 tactics pass, including JSON roundtrip, legacy schemas and malformed K/scheduler validation. This is a source-extracted CPU check, not a full module/GPU test. Receipt: `tests-cpu/cpu.json`.

Commands from the project root:

```bash
TRACE_LAYOUT_PAYLOAD_PATH=audit-rebased-20261026/trace-payload.json CUDA_VISIBLE_DEVICES='' \
  audit-final-cleanup/.venv-cpu/bin/python audit-rebased-20261026/check_trace_equivalence_cpu.py
python3 audit-rebased-20261026/check_tactic_tests.py
python3 audit-rebased-20261026/check_owned_scope.py
cd flashinfer-generality-review
/opt/homebrew/bin/pre-commit run --files tests/moe/test_cute_dsl_fused_moe.py flashinfer/trace/templates/moe.py
```

GPU selector changes: replace `TestUnsupportedMoeTacticRejected` with the restored `TestRubinMultiCtaTacticRejected`, and remove `TestInputsHelperContract::test_assignments_match_requested_expert_counts`. The parent's new suite includes the complete `tests/moe/test_cute_dsl_mxfp8_moe.py` and the scoped prior gate without that sampler test.

The trace checks validate the in-process numerical reference. Standalone serialized-reference export still has the pre-existing default-constant, dependency-registration and relative-import limitations recorded in `audit-final-cleanup/trace-export-boundary.md`; this audit does not claim to fix or validate export. Native kernel, GPU numerical and benchmark validation remains with the parent's source-bound campaign.
