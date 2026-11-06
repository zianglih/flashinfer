# SGLang FlashInfer CuTe DSL swap-AB integration

Implement a draft SGLang PR that selects FlashInfer's swap-AB split MoE on
Blackwell SM100/SM103 and uses the public checkpoint-safe weight interleaving
API for both new and legacy layouts. The PR must wait for an upstream FlashInfer
dependency bump containing flashinfer-ai/flashinfer#7290; dependency and image
updates are outside this change.

## Status

Draft PR: https://github.com/sgl-project/sglang/pull/48350

- Source commit: `354f91325a07fe327b10a29f4f2239a94cd5fa2e`.
- Base: `58484246d26523eaf1a7f16ab524deee288d2120`.
- Immutable evidence: https://github.com/zianglih/sglang/tree/7610e51989e0732adc7eeb6703fb0fac580f6b9c
- C3: 72 registered tests and 68 subtests passed; 14 graph/reload arms across
  seven matched cases passed, with bitwise legacy/swap equality before/after reload.
- All nine untuned timing rows are retained. The M16 W4A4 untuned regression is
  material; targeted autotuning yields +11.71% scalar and +15.89% per-token
  speedup for those two layer cases. See `validation-summary.md` and `results/`.
- No full-model/A2A validation. No dependency/image changes in the PR. Keep the
  PR draft until upstream's FlashInfer bump includes #7290.
- The cache-key change separates old and swap-AB processed presharded weights.

## Sources

- FlashInfer PR: https://github.com/flashinfer-ai/flashinfer/pull/7290
- Merged commit: `338924c2541673cedb6098185690eb54f26a5cde`
- Public helper: `flashinfer.fused_moe.interleave_cute_dsl_moe_weights`
- Layout contract: paired quantized FC1 `[up, gate]` weights and row-major block
  scales, interleaved before scale swizzling/MMA conversion. `swap_ab=True`
  selects 16-row groups; false preserves 64-row groups. Execution must match.

## Workspace

- `sglang/`: independent upstream source checkout and PR branch.
- `flashinfer/`: independent source checkout for API inspection.
- C3 setup logs, validation scripts, raw results, and the final PR body live at
  this project root. Validation uses the exact FlashInfer merge commit as a
  test-only dependency override.

## Validation plan

- Trace each production weight-preparation and execution path, including reload.
- Check exact packed weight/scale row permutation and architecture selection.
- Exercise production NVFP4 W4A4 scalar/per-token and W4A16 paths on C3 B300,
  including graph replay and available dispatch coverage.
- Run changed-file style checks and inspect the final diff for dependency churn.
- Record exact source commits, image, runtime, commands, raw output, and limits
  before opening the draft PR.
