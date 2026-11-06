# PR7290 swap-AB exact accuracy and manual sanitizer integration

Base: `5ac452450f65c6cec179290a66503ae86143a13f` (tree `f2e6d700708cad3d2786da6882d57e66182ee35b`). Port the independent blockscaled arithmetic reference from PR7372 commit `4566840f180deef35e90c1c35f93b5e9c328dd3b` and its standalone sanitizer harness through `1f2c9084e88b9d4a49d8f2107732bf686e62c2b1`.

- Scope: SM100/SM103 `swap_ab=True`, deterministic unfused finalization. Existing legacy/fused/Rubin tests retain their original reference and tolerances. W4A16 continues to use its existing shared exact reference.
- The oracle is `tests/test_helpers/cute_dsl_moe_swap_ab_reference.py`; accuracy assertions compare finite storage bits at zero tolerance. No standalone tests of the oracle itself are retained, as requested.
- The manual harness is `scripts/sanitize_cute_dsl_moe_swap_ab.py`, outside `tests/` and pytest's default filename patterns. No CI marker, workflow, `pytest.ini`, or test-runner registration changes. Modes are `w4a4`, `per-token`, `mxfp8`, `w4a8`, and `w4a16`; there is no independent `--per-token` switch.
- The final testing follow-up contains five files. A separate externally edited `moe_swap_ab_prepare.py` in the review checkout is preserved as unstaged work and excluded from this follow-up and the measured source.

Validation uses existing C3 devbox `fi-moe-nvfp4-port-1026`, B300, CUDA13.2, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL4.8.0. Remote source and persistent caches are under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-exact-20261027`. Source receipts capture the five-file snapshot. Native compilation artifacts were reused only after source identity checks; CuTe/Triton artifacts remain source scoped.

The first attempt discovered a cache-policy limitation: sanitizer's `FLASHINFER_JIT_LINEINFO=1` and normal accuracy flags caused sequential rebuilds of the same shared native `moe_utils` cache. Future simultaneous sanitizer/normal runs must namespace native caches by compiler configuration as well as source and runtime headers. The first GPU1 bounded attempt timed out during compilation; its artifacts are retained separately from its retry.

Sanitizer execution was subsequently stopped at the user's request. One earlier W4A16 synccheck pilot passed all 23 tactics, random/skewed routes, eager and graph execution, with zero diagnostics. The waiting W4A4 memcheck pilot was canceled before tactic traversal and is not counted as a result. That successful pilot predates the final CLI-only per-token-mode refactor; no final-script GPU sanitizer qualification is claimed. The full 150-case manual matrix was not run for this port.

The separate `../swap-ab-benchmark-table-20261027/` effort fills missing Nemotron/TRTLLM and pre-PR-layout versus new-layout W4A16 comparison cells. Existing completed historical benchmark cells are reused with their original source labels.

GPU1 retry completed successfully on the frozen five-file snapshot:

```text
..................                                                       [100%]
18 passed, 997 warnings in 245.08s (0:04:05)
```

The return code is 0 and the receipt verifies all five source hashes remained
unchanged. Nine swap-AB cases passed their exact reference comparisons, alongside
nine legacy controls. This result does not cover every native tactic or the two
large MXFP8 geometry cases.

The 52-row, nine-baseline benchmark summary draft and its cell provenance are
`summary-table-draft.md` and `summary-table-cells.json`. Retained evidence fills
312 measured cells; 52 cells are unsupported; 104 cells await the new campaign.
Once that campaign has downloaded complete raw evidence, assemble its paired
medians and the final summary with:

```sh
python3 swap-ab-exact-20261027/build_fresh_cells.py swap-ab-benchmark-table-20261027/evidence
python3 swap-ab-exact-20261027/build_summary_table.py --fresh-csv swap-ab-exact-20261027/fresh-cells.csv
```

The first command verifies all phase receipts, result hashes, routing identities,
100 raw samples per public measurement, median identities, and frozen native
selection caches. It writes `fresh-cells.csv`, `fresh-pass-medians.csv`, and a
hash receipt. The second command only fills pending cells and will reject
replacing retained measurements or unsupported cases. No PR body is edited by
either helper.
