# Full M-cluster alignment specialization

Candidate 002 against retained `968380de3b82650c0ea3b691ca235a728baf8acc`. Source is held for native/numerical evaluation; no commit, publication or GPU run was performed by the implementation owner.

The host derives `m > 0 and m % (CTA_M * cluster_M) == 0`, adds that Boolean to the existing compile key, and passes it to the private kernel constructor. The physical span is 128 for M128/C1 and 256 for M128/C2 or M256/C2. Full-cluster divisibility matters: m384 on C2 has a padded peer even though it is divisible by CTA_M 128. Runtime m/n/k, tensor layouts, routes, scheduling, tactics and public arguments remain unchanged.

For a fully covered cluster, the nongated SIMT epilogue retains only the routed-row predicate. Fused finalize uses the fixed CTA width and omits feature clipping/positivity checks. Both share their original store/reduction bodies. For other shapes, the original Int64 remaining-element expression, positive guard, clipped width and M/route predicate remain. Synchronization and route bounds are unchanged. Gated FC1's separate store body is untouched. Existing valid-work loops exclude terminal records; neither static nor CLC work mapping creates an M padding peer when the full physical cluster span divides m.

The existing partial-finalize test keeps W4A4's per-tensor/per-token H256/H384 references. W4A16 now runs H256→384→256 in one process in each finalize mode with its existing M256/C2 tactic: full cluster, padded peer, then return to the aligned cache entry. The oracle and tolerances are unchanged. Existing 24 route-boundary cases retain all six geometries, including aligned M128/C1, M128/C2 and M256/C2. The small explicit padding test does not independently establish CLC execution.

```bash
python -m pytest \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles \
  tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph \
  -k 'w4a16 or test_finalize_handles_cluster_padding_and_partial_tiles' -v --tb=short
```

Expected selected cases: 24 route-boundary +4 partial-finalize +2 EP8 functional +12 graphs =42. Initial execution returned 40 passed and 2 failed. Both failures occurred while constructing H288 scale inputs, before its kernel launch: the flattened grouped fixture produces no per-expert M padding, while `convert_sf_to_mma_layout` requires each group to have `ceil(M/128)` scale tiles. The corrected test removes H288 and retains H256→384→256. No W4A16 partial-CTA numerical coverage is claimed; M384 on C2 checks the padded peer, while the original W4A4 M384 case retains its actual partial tile. Native inspection can separately check an M288 descriptor. The corrected tests await execution by the sole executor. Native review must establish aligned guard/count folding, preserved partial fallback, resource/spill behavior and unchanged route/synchronization semantics; source review alone is not emitted-code proof.

Local checks passed: Python syntax compilation, scoped pre-commit (mypy, Ruff, formatting and applicable hygiene hooks), and independent source review. [Original source review](source-review.json) and [test correction](test-correction.json) record exact hashes. Production [source patch](source.patch): `724a9655`; [corrected test patch](tests-corrected.patch): `bca2ff16`; [corrected combined patch](candidate-corrected.patch): `3d65dfdc`; [test-only correction delta](tests-correction.patch): `cd4ce535`. Original patches are preserved. Production diff is 4 host additions and 27 kernel additions/13 removals. No further source changes are planned during evaluation.
