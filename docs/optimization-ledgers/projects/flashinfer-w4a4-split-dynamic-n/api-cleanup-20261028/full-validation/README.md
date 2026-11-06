# Cleanup publication and fresh validation

PR: https://github.com/flashinfer-ai/flashinfer/pull/7290

Published commits:

- `836dd31bb`: remove stale development tactic/cache contracts, redundant prepared-weight metadata and the wrapper-only autotune flag; use managed benchmark tuning/replay contexts.
- `d1767be1f42fdc371f90db4fb06598299ea32845`: explicit selected-launcher callable annotations and remaining Ruff formatting fixes from upstream CI.

`publication-source.json` binds the clean pushed source. The full repository
`pre-commit run --all-files` passes, including mypy and Ruff. The original
upstream failure and local reproduction/fix logs are in `ci/`. CUDA image
configuration validation passes. Upstream pre-commit run `40668606532` also
passed on this exact head. The Linux compile-cache lifecycle tests did not run
correctly on this macOS host, then all 11 passed on the Linux devbox; both logs
are retained.

All 95 selected pytest cases passed (33 accuracy and 62 API/cache cases), with
zero failures/errors/skips. [`tests/RESULTS.md`](tests/RESULTS.md) records all 106
passing tests, source identity, commands and raw summaries. Test GPUs 6–7 were
released and then assigned to the two N3U benchmark jobs.

The fresh campaign uses the existing C3 eight-B300 devbox and persistent native
compilation cache. GPUs 0–5 initially own benchmark jobs, and GPUs 6–7 own
existing repository accuracy/API/cache tests. All four model configurations and
all five current CuTe DSL precisions are measured on the pushed head. Existing
TRTLLM, non-swap CuTe and pre-PR W4A16 measurements are reused as external
baselines. Tokens 1/2 are measured but excluded from the summary and retention.
The candidate uses unfused finalize, NVFP4 includes activation quantization,
and MX starts from prequantized input. Two cold-L2 CUDA-graph CUPTI replay passes
follow fresh managed-cache autotuning; CUDA-event fallback is forbidden.

The full campaign is complete: 8 jobs, 260 current cells, 520 replay medians,
and 52,000 accepted CUPTI samples. Source hashes, routing, fresh tactic winners,
frozen replay caches, raw samples, and reported medians passed independent
audits. The aggregate signed speedup against the prior retained candidate is
-0.072%, effectively neutral. Targeted diagnostics found that the K3 W4A16
4096-token slowdown did not reproduce; the prior K3 MXFP4x8 8-token tactic was
1.295% faster than the fresh winner on the current source. These diagnostics
remain separate from the unchanged full-run matrix and do not establish a
causal old-source/new-source comparison.

The refreshed external-baseline table, raw output, test results, and red/green
heatmap are published in PR #7290. Exact live-body readback matches
`report/pr-body.md`; `report/pr-published.json` records it. The immutable image
publication and byte verification are in `report/plot-publication.json`.
The PR remains draft. Source snapshot, persistent compilation caches, and all
helper/evidence artifacts are retained. Sanitizer runs remain skipped.
