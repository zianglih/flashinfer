# Host simplicity review

Baseline: `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`; reviewed the full owned-file PR diff against upstream `215f83cb`. Source changes remain unstaged in `flashinfer-simplicity-review-20261027`.

Retained cleanup:

- The shared `_run_blockscaled_gemm` launcher owns settings that both callsites always passed identically: automatic operand stages, overlapping epilogues, one tile-metadata stage, and weight prefetch whenever PDL is enabled. The kernel still receives the same explicit behavior controls. Removed these redundant launcher arguments and cache-key fields.
- Removed `prepare_input` from the compiled-kernel key: it controls host preparation, not the constructed kernel. Device behavior remains keyed by the independent activation/scatter/routing controls.
- `_extract_tactic_params` shares the FC1/FC2 geometry extraction instead of repeating its output dictionary. Separate `gemm1_use_clc_scheduler` and `gemm2_use_clc_scheduler` keys and arguments remain, as requested. Tactic tuple formats, enumeration order, defaults and explicit rejection branches are unchanged.

Preserved:

- All public signatures/defaults and all original comments.
- All Rubin factory functions and post-Blackwell-return setup/launch statements, including shared per-token pointer setup. No Rubin device or MegaMoE edits.
- `fused_moe.py`, `prepare.py` and `runners.py` are byte-for-byte unchanged from the review baseline. The briefly explored shared scheduler argument was not retained.
- Existing input/type/layout checks. The outer wrappers validate their public output/layout contracts, while the shared launcher's `can_implement` additionally checks selected K depth/resources before preparation. Combining those layers would change rejection timing or surrounding upstream code without a useful simplification.

Validation:

- `python3 scripts/simplicity_20261027/check_host.py` passes. Source-bound output is `host-checks.json`.
- 2,176 tuple/JSON tactic cases compare exactly against baseline, including legacy Blackwell lengths and all Rubin tactics. The parser and tactic lists/defaults match baseline.
- 2,160 source-extracted common-launcher cases have identical admission-call arguments, kernel-constructor kwargs, compilation arguments and runtime pointer/scalar arguments. The matrix spans six operand/scale format contracts, all five routing tiles, all three channel/CTA geometries, automatic/4/8 K depth, both phases and both PDL/CLC flags.
- AST/source checks confirm public signatures, comments, Rubin factories/tails, and untouched host files. Scoped pre-commit passed (`host-precommit.log`).

These are CPU source/host-call equivalence checks, with recording stubs rather than a CUDA implementation. They do not claim GPU correctness, emitted-code identity or performance; the parent task owns that validation.
