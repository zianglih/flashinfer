# Epilogue ownership and review-diff cleanup

The five-file candidate is based on `1fab0dc8d9da5ac0f4ca81a9fecad7cda9e95729`. Exact source hashes and the full-index patch are in `source.json` and `source.patch`.

- Follow the Rubin/Hopper boundary: the existing grouped GEMM module owns `Sm100BlockScaledMoeEpilogue` and its six exclusive helpers. Preserve the separate class, configuration, signatures, complete bodies, and useful comments. No new module or compatibility alias.
- `blackwell/utils.py` retains its original primitive/reexport surface plus PDL publication. Restore `blk_reduce_fp32` and `blk_reduce_fp16` byte-for-byte from upstream. The file is 156 lines.
- Preserve the original `pipeline_init_wait`, leader helper, comments and calls by restoring `custom_pipeline.py` from `ed67c485`. Its already-retained synchronization optimizations remain. Restore the original tuner dictionaries from the same commit; separate FC1/FC2 controls and the shared AUTO flag remain unchanged.
- Restore the original local benchmark interleave helper from upstream; retain the required architecture-dependent group-size call. Its executable AST matches the previously imported shared helper.
- Keep each file's existing license header without adding a duplicate block, as explicitly requested.

`check_move.py` verifies exact decorated definition bytes, AST, useful comments, global bindings, original helper restorations, benchmark executable equivalence and unchanged headers. Scoped pre-commit (including mypy/Ruff) and `git diff --check` pass. The source-only proof does not establish binary identity; the bounded GPU gate checks that separately against verified artifacts from `1fab0dc8`.

No numerical, tuning, synchronization, geometry or performance change is intended. The public benchmark results retain their measured source attribution. Full timing sweeps and broad sanitizer coverage are not repeated for this structural change.

## Retained status

Pushed as `54f5c682`. The final receipt is `../validation/structure-final/final-validation.json`; independent review is `gate-independent-review.md`. All 48 exact comparisons and 42 tests pass. Of 32 compiled GEMM/preparation pairs, 31 are encoding-identical; one differs only by a reviewed descriptor-register permutation with unchanged control words and resources. No timing rerun.

The completed review clone is removed after a clean bump to the retained commit. Source is available in the canonical clone or from that commit; the historical verification scripts record their original review path. All helper scripts and raw validation artifacts remain.
