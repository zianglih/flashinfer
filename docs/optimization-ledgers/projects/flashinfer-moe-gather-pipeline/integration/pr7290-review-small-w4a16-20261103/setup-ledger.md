# PR7290 review fixes and small-token W4A16 regression check

Requested 2026-11-03. All repository changes stay local and unstaged; no commits,
pushes, public replies, or PR-body changes are authorized by this request.

## Scope

- Record and validate the gated weight layout in typed CuTe DSL weight packs;
  reject incompatible mixed-layout candidates before autotuning.
- Complete exported weight-interleaving helper registration/documentation and
  permit CPU checkpoint permutation; retain architecture checks at consumption.
- Extend the existing functional autotune test to swap-AB. Exercise actual
  enumeration and cached replay, retaining the backend's existing reference and
  tolerance contract.
- Measure W4A16 at 4, 8, and 16 tokens, all four model configurations in both
  rank-local EP and TP, on B200 and B300. Do not introduce a token threshold
  before confirming the reported regression.

## Sources and timing plan

- Before PR: `002529e17b22567a071091053c6c4dc2a55e050e`, original 64-row gated
  layout and standalone activation preparation. Reuse its source archive and
  documented benchmark adapter, not timings or CUDA 13.0 compiled artifacts.
- Current: `14a338579eb8acddcc5cfd1cc58871fc0788de22`, test-only delta from
  `2b4732791a3ce48bc3ae6c030a283fab73854e0e`; current kernel bytes are identical.
- Three arms: before, current swap-AB off, current swap-AB on. Current host API
  review changes do not affect this functional-API W4A16 benchmark path.
- Workloads: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8. BF16 input,
  NVFP4 weights, unfused finalization; no activation quantization or distributed
  communication in the measured API.
- Initial controlled comparison: baseline source-specific frozen winners;
  current OFF replays the same baseline winner; current ON replays its retained
  winner. Verify all actual tactics and reject cache misses. These choices have
  B300 origins; the B200 run is not a claim of independently optimal tactics.
- Balanced before/off/on/on/off/before order, two independent phase medians per
  arm, 10 warmups and 100 strict CUPTI cold-L2 CUDA-graph samples per phase.
  Each workload's arms stay on the same GPU. Compare geometric means of phase
  medians: speedup = `(before / current - 1) * 100`. Positive means faster.
- Preserve every negative cell, repeat spread, routing hash, exact source and
  environment receipt. If regression is reproduced, append native-autotune
  checks rather than replacing the original observations.

## Status

All six repository files are updated locally and remain unstaged. Full targeted
pre-commit checks pass (including mypy, Ruff, and formatting). Architecture-specific
GPU validation and timing are in progress. No numerical performance conclusion is
available yet. C1 and C3 owners preserve runtime
commands and evidence in their subdirectories. `review-comments.json` contains
reviewer comments as retrieved from GitHub before editing.

## Source inventory correction

The historical archive inventory had 542 long CUTLASS documentation paths without
the `3rdparty/cutlass/` prefix (PAX archive handling), and omitted three CCCL
export-ignored metadata/license files. Before timing, the manifests were reconciled
against exact Git source and the same four pinned submodule commits. All shared
existing file hashes are unchanged; no implementation input changed. The baseline
benchmark adapter remains SHA256
`8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`.

`reconcile_manifests.py` records the correction. The corrected inventories contain
31,069 baseline files and 34,762 current files. Historical inventories and the
small additive source archives are preserved alongside this note; only owned
new task snapshots are reconciled, not prior immutable donor snapshots.

Each timing phase also runs the established 2ms host NVML telemetry sampler.
Clock stability is inspected alongside repeat spread when interpreting negative
cells; phase timing uses CUPTI device activity, not the telemetry sampling clock.

## Validation progress

- Local targeted pre-commit: all checks passed, including mypy and Ruff.
- B200: four functional autotune/replay cases passed; the final six-file review
  snapshot passed 12 guard/CPU-helper cases, eight typed NVFP4 accuracy cases
  covering both layouts and all four activation families, and one swap-AB
  MXFP4x8 prepared-weight accuracy case. Total: 25 passed, zero failures/skips.
  The autotune snapshot predates only two subsequently added metadata assertions
  in unrelated accuracy functions; its autotune test body is identical.
- B300: 28 passed, zero failures/errors/skips: four autotune cases, 13
  CPU/layout guard cases, eight typed NVFP4 cases, two swap-AB MX prepared-weight
  cases, and one legacy MX prepared-weight case. Both timing campaigns remain
  in progress.

C1 validation evidence and independent JUnit/file-hash checks are in
`c1/autotune-audit.json` and `c1/review-tests-audit.json`.

## Completed B200 fixed-choice matrix

All eight model/topology jobs, all six balanced phases, and all 14,400 raw CUPTI
samples passed source, route, cache-hit/tactic, and timing checks. Per-cell phase
spread is at most 0.541%; sampled SM/memory clocks are constant at 1965/3996MHz.

| Scope | Swap-AB off speedup | Swap-AB on speedup |
|---|---:|---:|
| All 24 workloads | +2.15% | +2.96% |
| EP | -1.78% | -0.02% |
| TP | +6.23% | +6.04% |

At V3 EP8, 4 tokens, the full matrix measures 50.416µs before PR, 53.600µs off,
and 51.584µs on (-5.94% / -2.26% speedup). Separate pilot timeline reconstruction
places the added latency at FC1 after accounting for the removed standalone
permutation and overlapping FC2/combine. This does not establish an
instruction-level cause. OFF and before use identical tactics; OFF versus ON
also changes the recorded tactic and is not a layout-only attribution.

- Plot: `plots/b200-w4a16-small-tokens.png` (also SVG).
- All raw latencies: `plots/b200-table.md` and `plots/b200-cells.csv`.
- Independent audit: `c1/full-matrix-independent-audit.json`.
- Raw results: `c1/results/`, transfer hashes: `c1/fetch-full.json`.

The separate fresh-autotune V3 EP8 T4 replay has finished and all 600 CUPTI
spans passed independent reconstruction. It measures 50.904µs before, 54.224µs
off, and 53.696µs on: -6.12% / -5.20% speedup. Repeat spread is at most 0.119%.
Fresh tuning did not remove the loss. Its winners and timings do not replace
this fixed-choice matrix. Raw tuning costs, winners, traces, and balanced replay
are in `c1/fresh-native-v3-t4`; audit: `c1/fresh-native-audit.json`.
