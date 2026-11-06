# PR7290 local review fixes and W4A16 small-token performance

Completed 2026-11-03. Six source files remain **local and unstaged** on
`14a338579eb8acddcc5cfd1cc58871fc0788de22`; no commits, pushes, PR edits, or
reviewer replies were made for this request.

## Review changes

- Prepared gated weight views record 16/64-row grouping; typed runners reject
  mismatches before launch. Mixed-layout gated candidates require separate
  layers. Existing unannotated manual views retain the published64-row contract.
- The exported interleaving helper supports CPU tensors, has `@flashinfer_api`
  registration and API documentation, and retains device checks at consumption.
- The existing functional autotune test covers swap-AB, actual candidate search,
  cached replay, and the existing exact reference contract. Existing accuracy
  tests also check metadata returned by real weight preparation.

No kernel, numerical contract, tactic, or benchmark-script change was made.
The initial six-file snapshot is preserved in `review-files-manifest.json`.
A later test-only trim reduces review churn; production/docs remain byte-identical.
See [trim validation](trim-validation/README.md) for the current diff and evidence.

## Validation

| Check | Result |
|---|---|
| B200 / SM100 | 25 passed, zero failures/errors/skips |
| B300 / SM103 | 28 passed, zero failures/errors/skips |
| Targeted pre-commit | Passed, including mypy, Ruff and formatting |
| Main performance evidence | 28,800 independently audited CUPTI samples |
| Separate fresh-autotune replay | 1,200 independently audited CUPTI samples |

Correctness covers CPU interleaving, layout guards, typed NVFP4 accuracy with
both layouts and four activation families, actual MX preparation, and real
W4A4/W4A16 autotuning plus replay. This is focused validation, not a full suite.

## Performance result

The default/off small-EP regression reproduces under frozen historical tactics.
B200 remains slower at V3 EP8 /4tokens after fresh native tuning. On B300, fresh
native tuning selects one-CTA tactics and removes that particular loss. This
does not establish that retuning fixes every negative cell in the full matrix.
Positive aggregate results coexist with the individual EP regressions below.

| GPU | Scope | Swap-AB off speedup | Swap-AB on speedup |
|---|---|---:|---:|
| B200 | All24 workloads | +2.15% | +2.96% |
| B200 | EP | -1.78% | -0.02% |
| B200 | TP | +6.23% | +6.04% |
| B300 | All24 workloads | +2.71% | +3.56% |
| B300 | EP | -0.60% | +0.83% |
| B300 | TP | +6.13% | +6.37% |

### Separate fresh-native V3 EP8 /4-token check

Each arm was autotuned once into a new cache on its native architecture, followed
by the same balanced six-phase replay. These values do not replace main heatmap
cells. The autotuner selects real tactics; no default/fallback winner is admitted.

| GPU | Before (µs) | Current off (µs) | Off speedup | Current on (µs) | On speedup |
|---|---:|---:|---:|---:|---:|
| B200 | 50.904 | 54.224 | -6.12% | 53.696 | -5.20% |
| B300 | 50.793 | 50.153 | +1.28% | 50.320 | +0.94% |

CUPTI timeline reconstruction locates the frozen default/off overhead at FC1:
its increased contribution exceeds the eliminated standalone permutation cost;
FC2/combine partly offset it. Individual overlapping kernel durations were not
added as end-to-end latency. The instruction-level mechanism is not established.

### Heatmaps and raw latencies

- [B200 heatmap](plots/b200-w4a16-small-tokens.png) · [SVG](plots/b200-w4a16-small-tokens.svg) · [Full table](plots/b200-table.md) · [CSV](plots/b200-cells.csv)
- [B300 heatmap](plots/b300-w4a16-small-tokens.png) · [SVG](plots/b300-w4a16-small-tokens.svg) · [Full table](plots/b300-table.md) · [CSV](plots/b300-cells.csv)

## Benchmark contract

- Before: `002529e17b22567a071091053c6c4dc2a55e050e`, original64-row layout and
  standalone preparation, with the documented benchmark adapter SHA256
  `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`.
- Current: exact14a source, swap-AB off and on. Unstaged host/API fixes do not
  affect the functional benchmark path; the kernel source is unchanged.
- Four shapes: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8.
  Tokens4,8,16 only; rank-local simulation with no distributed communication.
- Whole unfused MoE API, BF16 input/NVFP4 weights. Input quantization does not
  apply to W4A16. Routing, FC1, FC2 and combine are included.
- Both devboxes: `nvcr.io/nvidia/pytorch:26.05-py3`, system CUDA13.2.78, Torch
  `2.12.0a0+5aff3928d8.nv26.05`; CuTe DSL4.8.0 (embedded compiler13.4).
- Strict CUPTI cold-L2 CUDA graphs;10 warmups and100 samples per cell/phase.
  Balanced `before/off/on/on/off/before`, same GPU for all arms of a workload.
  Each reported latency is the geometric mean of two phase medians.
- Speedup=`(before/current−1)*100`; positive is faster. Main before/off reuse
  identical baseline winner choices; on uses retained swap-AB choices. These
  choices originate on B300. Main B200 results do not claim native-optimal tactics.
- Every raw sample, negative result, cache key/tactic, route identity and source
  hash is retained. Timing fallback, missing choices, and default tactics fail.
- Established host NVML polling runs at2ms. Main sampled clocks were constant:
  B2001965/3996MHz, B3002032/3996MHz, no reported clock events. Maximum phase
  repeat spreads:0.541% B200,0.466% B300.
- Repeat spread does not bound cross-GPU/run variation. The separate B300 pilot
  measured V3EP8/T4 on at−1.83%, while the main run on another GPU measured
  +0.37%, with matching routes/tactics/configs and sampled clocks. Treat such
  small changes as near-neutral; preserve both observations.

## Evidence and reproduction

- [B200 runtime/run index](c1/README.md): source/config/cache paths, commands,
  raw fixed data under `c1/results`, fresh data under `c1/fresh-native-v3-t4`.
- B300 fixed data: `c3/perf-evidence/c3/results`; source/config/proof inputs under
  `c3/perf-evidence`. Fresh data: `c3/fresh-native`.
- Independent full audits: [B200](c1/full-matrix-independent-audit.md),
  [B300](c3/full-matrix-independent-audit.md). Fresh replay audits:
  [B200](c1/fresh-native-audit.json), [B300](c3/fresh-native-audit.json).
- Correctness: [B300](c3/review-validation.md), `c1/review-tests-audit.json`,
  `c1/autotune-audit.json`; raw pytest output/JUnit in each `evidence` directory.
- Exact source inventories and corrected historical archive paths are audited
  in `manifest-independent-audit.json`; no runtime source bytes changed in that
  inventory correction. `setup-ledger.md` preserves incremental setup history.

Plots are reproducible locally with the existing publication environment:

```bash
.venv-publication/bin/python integration/pr7290-review-small-w4a16-20261103/report.py \
  --results integration/pr7290-review-small-w4a16-20261103/c1/results \
  --gpu B200 --output integration/pr7290-review-small-w4a16-20261103/plots
.venv-publication/bin/python integration/pr7290-review-small-w4a16-20261103/report.py \
  --results integration/pr7290-review-small-w4a16-20261103/c3/perf-evidence/c3/results \
  --gpu B300 --output integration/pr7290-review-small-w4a16-20261103/plots
```
