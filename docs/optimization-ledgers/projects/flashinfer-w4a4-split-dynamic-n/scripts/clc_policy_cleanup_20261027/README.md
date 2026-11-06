# All-CLC tactic policy cleanup

Independent unstaged clone `../../flashinfer-clc-policy-cleanup-20261027`, base7f4e1703. This is not retained yet: the all-CLC native performance screen still exposes material K3 prefill losses, under investigation separately.

- Both Blackwell phase configurations request CLC. New AUTO tactics contain routing capacity, two GEMM geometries, and the K-depth pair, without redundant scheduler booleans.
- The original three-field geometry format remains accepted and defaults to CLC in both phases. Experimental five/six-field tuples from this unmerged PR are removed. Tuning-cache namespacev5 prevents loading their stale serialized choices.
- Existing reduced-SM and no-cancellation-opportunity fallbacks remain in the lower-level launcher; this change does not introduce dtype/model policy.
- All180 new tactics produce exactly the same extracted launch parameters as the frozen all-CLC native experiment's six-field True/True tactics. All8 Rubin tactics have unchanged parameters. No Rubin implementation changes.
- Existing enumeration tests are adjusted; no dedicated test file added. Scoped pre-commit and146 existing CPU-side tactic/cache/config tests pass. GPU performance is not claimed for this source yet.

`verify.py` records AST functional equivalence and exact diff hashes. `deploy.py` keeps verified unchanged C++ build artifacts on persistent Weka, with a private source-derived DSL namespace. The first CPU helper attempt compared a two-file receipt with the harness's larger file list and stopped before tests; the corrected helper checks exact commit/diff plus each recorded file, then requires complete before/after receipt equality. Existing checks run in `cpu-checks-r2`.
