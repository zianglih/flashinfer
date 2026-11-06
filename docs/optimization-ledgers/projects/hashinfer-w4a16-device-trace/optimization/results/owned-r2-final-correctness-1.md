# Owned R2 correctness evidence

Tested source: `55cd345d57ccc56327966201bd0725767a11593a`; package SHA256 `a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29`.

Status: PASS.

| Suite | Status | Outer cases | Rank pytest passes |
| --- | --- | ---: | ---: |
| ep4 | pass | 3 | 12 |
| ep8 | pass | 1 | 8 |
| tails | pass | 10 | 20 |
| lifecycle | pass | 6 | 12 |
| prestaged | pass | 6 | 6 |

Per-rank raw JUnit outcomes below are `tests/failures/errors/skipped @ testcase seconds`; each accepted rank also reports pytest exit code 0 and unchanged source.

| Exact pytest node | Raw JUnit outcomes by rank |
| --- | --- |
| `tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics[topk_fc2-random-ep4-glm5-t1024]` | r0=1/0/0/0 @ 285.919; r1=1/0/0/0 @ 285.407; r2=1/0/0/0 @ 285.513; r3=1/0/0/0 @ 285.308 |
| `tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics[topk_fc2-skewed-ep4-glm5-t1]` | r0=1/0/0/0 @ 279.883; r1=1/0/0/0 @ 279.621; r2=1/0/0/0 @ 279.318; r3=1/0/0/0 @ 279.874 |
| `tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics[topk_fc1-random-ep4-glm5-t1024]` | r0=1/0/0/0 @ 269.498; r1=1/0/0/0 @ 269.619; r2=1/0/0/0 @ 269.868; r3=1/0/0/0 @ 269.864 |
| `tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics[topk_fc1-random-ep8-glm5-t128]` | r0=1/0/0/0 @ 299.825; r1=1/0/0/0 @ 300.439; r2=1/0/0/0 @ 299.847; r3=1/0/0/0 @ 299.891; r4=1/0/0/0 @ 300.122; r5=1/0/0/0 @ 299.812; r6=1/0/0/0 @ 300.421; r7=1/0/0/0 @ 299.811 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-small-epi_warps]` | r0=1/0/0/0 @ 26.765; r1=1/0/0/0 @ 27.205 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-small-reuse_dispatch_warps]` | r0=1/0/0/0 @ 18.702; r1=1/0/0/0 @ 18.699 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-tail-epi_warps]` | r0=1/0/0/0 @ 21.562; r1=1/0/0/0 @ 21.563 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-tail-reuse_dispatch_warps]` | r0=1/0/0/0 @ 17.391; r1=1/0/0/0 @ 17.388 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n64-wrap-epi_warps]` | r0=1/0/0/0 @ 16.885; r1=1/0/0/0 @ 16.440 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n64-wrap-reuse_dispatch_warps]` | r0=1/0/0/0 @ 23.091; r1=1/0/0/0 @ 23.191 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n128-wrap-epi_warps]` | r0=1/0/0/0 @ 21.550; r1=1/0/0/0 @ 21.371 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-n128-wrap-reuse_dispatch_warps]` | r0=1/0/0/0 @ 27.027; r1=1/0/0/0 @ 27.202 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-activation-tail-epi_warps]` | r0=1/0/0/0 @ 21.301; r1=1/0/0/0 @ 21.102 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails[w4a16-activation-tail-reuse_dispatch_warps]` | r0=1/0/0/0 @ 23.026; r1=1/0/0/0 @ 23.463 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill[static-epi_warps-w4a16]` | r0=1/0/0/0 @ 24.911; r1=1/0/0/0 @ 24.910 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill[static-reuse_dispatch_warps-w4a16]` | r0=1/0/0/0 @ 17.362; r1=1/0/0/0 @ 17.188 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill[atomic_counter-epi_warps-w4a16]` | r0=1/0/0/0 @ 25.747; r1=1/0/0/0 @ 26.192 |
| `tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill[atomic_counter-reuse_dispatch_warps-w4a16]` | r0=1/0/0/0 @ 18.179; r1=1/0/0/0 @ 18.491 |
| `tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-epi_warps-manual]` | r0=1/0/0/0 @ 20.385; r1=1/0/0/0 @ 20.930 |
| `tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep[w4a16-reuse_dispatch_warps-manual]` | r0=1/0/0/0 @ 19.300; r1=1/0/0/0 @ 19.479 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[regular-e4-epi_warps-w4a16]` | r0=1/0/0/0 @ 7.389 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[regular-e4-reuse_dispatch_warps-w4a16]` | r0=1/0/0/0 @ 7.446 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[tail-e4-epi_warps-w4a16]` | r0=1/0/0/0 @ 7.449 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[tail-e4-reuse_dispatch_warps-w4a16]` | r0=1/0/0/0 @ 7.568 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[singleton-e1-epi_warps-w4a16]` | r0=1/0/0/0 @ 7.134 |
| `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference[singleton-e1-reuse_dispatch_warps-w4a16]` | r0=1/0/0/0 @ 7.226 |

Strict finite-BF16-bit completion records (one rank-aggregated report per outer case):

| Case | Completed combinations | Reference comparisons | Completed pairs | Passed / failures |
| --- | ---: | ---: | ---: | --- |
| `topk_fc2-random-ep4-glm5-t1024` | 32 | 96 | 496 | `true` / `[]` |
| `topk_fc2-skewed-ep4-glm5-t1` | 32 | 96 | 496 | `true` / `[]` |
| `topk_fc1-random-ep4-glm5-t1024` | 32 | 96 | 496 | `true` / `[]` |
| `topk_fc1-random-ep8-glm5-t128` | 32 | 96 | 496 | `true` / `[]` |

Audited totals from accepted records: {'outer_cases': 26, 'rank_pytest_passes': 58, 'strict_combinations': 128, 'independent_reference_comparisons': 384, 'pairwise_comparisons': 1984}.

Reference comparisons and pair comparisons are collective reports, not counts multiplied by EP ranks. Every accepted comparison rank was checked. The planned strict scope includes both routing-weight placements, O2/O3, eight deterministic tactics, eager repeats and four graph replays; only accepted rows establish completed coverage. Tails/lifecycle/prestaged retain their source test assertions; their JUnit passes are not relabeled as the strict all-tactics matrix. No sanitizer pass is implied.

Raw logs, JUnit, commands, provenance and numerics JSONL remain in the immutable selected snapshot. Partial/failed suites are retained separately and excluded from accepted totals. Source/test/harness hashes and per-case raw pytest summary lines are recorded in the JSON report.
