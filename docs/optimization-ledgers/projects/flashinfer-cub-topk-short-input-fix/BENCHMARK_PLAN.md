# CUB Top-K parent versus PR validation

The user requested fresh before/after measurements and a separate results comment on
FlashInfer draft PR #5187. This supersedes the earlier instruction to skip benchmarks.

- Before: parent `93e9eef092c11bc93a6f432a16404054e85d19c5`.
- After: PR head `30b1b2e6d12792951309b607b9e009d791aed7b8`.
- Same task-owned B300 GPU and `nvcr.io/nvidia/pytorch:26.05-py3` environment.
  Each arm uses its own source checkout and native JIT cache; CCCL remains pinned.
- Primary comparison: forced CUB versus forced CUB for the three public APIs,
  with page-table raw-output enabled and disabled, SMALL and LARGE tie modes.
  Native `default` calls are independent controls and show CUB-versus-native gains.
- Keep normal physical widths, short logical lengths, and unsupported-before short
  physical widths separate. A parent error is not a latency or a speedup baseline.
- Include plain Top-K separately. Its tail launch now runs only for K>physical
  width, following the clarified static capture/replay shape contract; ordinary
  calls retain the parent launch count.
- Reference: PR #4442's normal-random input grid, representative batch/width/K
  ranges, and FP32/FP16/BF16. Add explicit boundary-tie and windowed diagnostics.
- Primary metric: complete CUDA graph replay measured by CUDA events, divided by
  captured calls; all selection, mapping, padding, and conversion launches included.
  Reuse inputs (warm L2), pass `dsa_graph_safe=True`, exclude compilation, Python
  dispatch, allocation, capture, and reference checks. This differs from #4442's
  CUPTI/cold-L2 measurements; no historical absolute-time comparison is valid.
- Run three paired rounds, alternating arm order. Keep every raw sample, exact
  command, source/binary hash, environment, and case identifier.
  Final matrix: 394 workload IDs x 2 backends = 788 records per arm, including
  668 FP32, 60 FP16, and 60 BF16 records. Unsupported combinations remain records.
- Initial regression screen: at least 5% and 0.25 microseconds slower. Inspect
  worst cases regardless of threshold and rerun flagged fused cases in alternating
  order. Report measured regressions and exclusions rather than masking them with
  an aggregate speedup.
- Publish a concise PR comment with absolute times, paired ratios, limitations,
  and links to complete public raw evidence and reproducible scripts. Keep large
  benchmark evidence out of the PR body. Delete the task-owned devbox after
  retrieval and verification.
- After both test cleanup and performance validation are complete, mark PR #5187
  ready for review, as explicitly requested by the user. Resolve unexpected
  regressions before doing so. No unconditional plain Top-K extra launch remains.
