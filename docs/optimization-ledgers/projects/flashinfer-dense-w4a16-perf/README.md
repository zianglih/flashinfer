# FlashInfer dense CuTe DSL W4A16 performance work

This workspace owns the optimization effort for the SM100/SM103 dense
`mm_bf16_fp4` kernel merged through FlashInfer PR #4466.

## Layout

- `flashinfer/`: independent upstream checkout on branch
  `perf/cutedsl-dense-w4a16`.
- `hai/`: project-local HAI checkout used only as the working directory for the
  installed `/usr/local/bin/h` CLI.
- `dense_w4a16_optimization_experiments.md`: retained/rejected experiment
  ledger and reproducibility notes.
- `UPSTREAM-PR-BODY.md`: submitted body for upstream PR #4686, before
  automated review appendices.

## Upstream PR

- PR: https://github.com/flashinfer-ai/flashinfer/pull/4686
- Head: `693d10862df7a793f7dd9d500ddece28d536d9a0`
- Branch: `zianglih:perf/cutedsl-dense-w4a16`
- The final review diff contains only the production CuTe DSL file. Commit
  `c74bdec1d2a959340c8c072a8b67d0b10df07210` removes the two evidence
  drivers in a standalone commit, preserving them in history at `100e9527`.
- At initial publication, pre-commit and documentation checks passed. Public
  GPU CI was requested with `@flashinfer-bot run` but remained pending
  authorization; internal CI was not requested.

## Validation environment

- Cluster: C2 (`infra` earth queue) after C1 had no schedulable capacity
- GPU: NVIDIA B300 SXM6 AC (SM103), full 8-GPU devbox node; benchmarks pin GPU 0
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`
- CUDA: 13.2
- Driver: 590.48.01
- PyTorch: `2.12.0a0+5aff3928d8.nv26.05`
- CuTe DSL: 4.7.0 after editable FlashInfer dependency installation
- CUPTI: `cupti-python==13.2.0`, `nvidia-cuda-cupti==13.2.86`,
  `cuda-bindings==13.2.0`; a real fail-closed timing smoke passed

The first C1 `infra` B200 pod was reclaimed, and subsequent C1 requests could
not get capacity. The active C2 request received B300/SM103 despite the B200
flavor name. Do not combine its measurements with the discarded C1/B200
bring-up baseline.

## Historical benchmark harness

- Commit `100e95275d55280c110c66e9a4693b07b86ff4d4` retains
  `benchmarks/bench_dense_w4a16_sm100.py`, the fresh-process sweep
  orchestrator and artifact reducer, and
  `benchmarks/bench_dense_w4a16_sm100_worker.py`, the one-CUPTI-call worker
  with graph/replay correctness and experimental controls. They are absent
  from the final PR tree to keep the review diff minimal.
- `analyze_dense_w4a16_aba.py`: compares a candidate with the arithmetic mean
  of adjacent baseline labels and reports per-shape baseline drift plus the
  workload geomean. Separate JSON files are supported for source-changing
  A/B/A legs.

## Retained result

- Compile the SM100/SM103 dense CuTe kernel at optimizer level 3.
- Treat raster direction as a full autotune axis: 15 structural tactics become
  30 M-major/N-major tactics. The non-autotuned fallback remains the first
  M-major tactic.
- Exact-source production-autotune O2/candidate/O2 at benchmark commit
  `100e9527` across all 16 PR #4466 shapes measured `1.029759x`
  geometric-mean speedup. The range was
  `0.996866x`--`1.060623x`; the sole slower row moved only 0.31%. Fifteen of
  sixteen adjacent baseline pairs stayed within 0.52%; up-projection M=1024
  drifted 1.86% after the upstream autotuner switched from N128 to N192, while
  the candidate remained faster than both baseline arms.
- The full raster axis roughly doubles first-use tuning work (417.83 s summed
  profile time versus 196.68 s for the screened 16-tactic space across this
  suite). This is deliberate coverage for real workloads with varied shapes.

Durable result artifacts are in `artifacts/` locally and at
`/data/home/ziangli/flashinfer-dense-w4a16-perf-artifacts` on C2 Weka. The
active devbox `c2/infra/dense-w4a16-perf-b200` is intentionally left intact.
