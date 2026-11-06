# Host comment/docstring review

Reviewed the six changed non-Blackwell `flashinfer/fused_moe` files against upstream `215f83cb`, on review base `54f5c682`. Four files have unstaged prose-only changes; `fused_moe.py` and `runners.py` required no further edits.

- Restored original tactic helper descriptions, sub-tactic format documentation, `_is_rubin_tactic` documentation, the Blackwell import comment, still-valid caller-facing gather example wording, the scale-factor atom comment, and the finalize tensor-helper summary.
- Preserved the five-field full tactic format, shared CLC flag, routed-token N alignment, input preparation, early-PDL metadata publication, newly supported MXFP8/SiTU behavior, and changed Blackwell weight-layout compatibility. Did not restore obsolete GEMM2 tile/layout restrictions or the old SiTU rejection comment.
- Removed the repeated module-level gather/preparation explanation and unnecessary implementation detail in the public tile/cluster descriptions. Restored the original weight-preparation sentence without interrupting it with the new layout explanation; the required layout and re-preparation warning remain.
- No executable code, signature, default, layout, license or copyright changes. Original comments unrelated to this PR remain intact.

`verify.py` passes for all six owned files: their complete ASTs are equal after removing only actual Python docstrings, all pre-module header bytes equal upstream, and `git diff --check` passes. `proof.json` records file and AST hashes; `candidate.patch` freezes the four-file diff as `27481a11c54c69c875d9932ab4d0883255c3d8fc0147f63273c244f42965569e`. No tests/GPU runs, commit, or push were performed.
