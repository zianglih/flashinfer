# FlashInfer CuTe DSL MoE compile pruning

This project contains the independent FlashInfer checkout, C1 validation
record, and upstream PR draft for reducing the native `moe_utils` compilation
triggered by the shared SM10x CuTe DSL W4A4/W4A16 MoE pipeline.

- Candidate checkout: `flashinfer/`
- Exact #4082 baseline checkout: `flashinfer-source-owned-baseline/`
- Branch: `perf/cutedsl-moe-precomputed-compile`
- Merged base: `fb28d7242b3506a2348265962041acc1fb56cca4` (#4082)
- Current PR commit and measured source:
  `4a17da2169e96559e1321524c5186d81f6880fd8`
- Draft upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/4678
- Validation record: `VALIDATION.md`
- Draft PR body: `PR_BODY.md`
- Durable helpers: `tools/`
- Retained validation devbox: `fi-cutedsl-source-owned` (`c1`, namespace
  `infra`)
- Accidentally created and retained devbox: `list` (`c1`, namespace `ziangli`);
  it was not used for validation and was not deleted without authorization.

The production change is deliberately narrow. `moe_utils` still uses the
existing TRT-LLM routing/permutation pipeline, but selects four source-owned
post-topK wrappers matching the translation-unit split introduced by #4635.
Generic and post-topK sources own their launcher policy dispatch, while one
entry implementation header holds only launchers genuinely shared by both
modules. There is no caller-specific or post-topK build-mode selector. The full
raw-logit routing module added by #4082 retains its generic source list and
runtime behavior.
W4A4 per-tensor, W4A4 per-token, and W4A16 all use this module; SM12x/B12x and
other MoE backends are outside this claim.

On one C1 B200, fresh exact-commit cold FlashInfer-JIT first-run wall time
improved from **244.03 s to 121.28 s for W4A4** (50.30% lower, 2.01x) and from
**245.19 s to 120.99 s for W4A16** (A/B/A/B means; 50.66% lower, 2.03x).
Isolated `moe_utils` A/B/A/B build/load improved from **194.29 s to 71.93 s**:
62.98% lower, or 2.70x faster.

The final source-owned cleanup was rerun on the retained C1 B200: focused
W4A4/W4A16 tests and the ten-case matrix passed, and a single-module
AOT-equivalent build/package/load plus both generic/specialized DSO load orders
passed with JIT disabled.
