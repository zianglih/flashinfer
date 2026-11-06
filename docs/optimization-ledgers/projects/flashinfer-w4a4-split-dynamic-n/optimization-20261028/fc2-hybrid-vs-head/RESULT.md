# FC2 hybrid versus PR head

Full direct same-GPU C-A-A-C comparison of PR head `61249e0b` with the unstaged FC2 hybrid candidate `aff28644`. Positive percentages mean the candidate is faster.

## Aggregate results

| Topology | Model | Decode 4–64 | Middle 128–512 | Prefill 4096–16384 | All displayed |
|---|---|---:|---:|---:|---:|
| EP | All models | -0.38% | -0.04% | +0.20% | -0.13% |
| EP | V3 | +0.07% | +0.06% | +1.44% | +0.44% |
| EP | V41F | -0.35% | -0.13% | -0.96% | -0.46% |
| EP | K3 | -0.57% | +0.07% | -0.77% | -0.45% |
| EP | N3U | -0.71% | -0.13% | +0.86% | -0.13% |
| TP | All models | -1.88% | +0.15% | +4.51% | +0.38% |
| TP | V3 | -0.30% | +1.71% | +5.96% | +1.92% |
| TP | V41F | -0.71% | -0.54% | +1.41% | -0.09% |
| TP | K3 | -1.66% | +0.67% | +4.33% | +0.58% |
| TP | N3U | -4.17% | -1.41% | +4.79% | -1.04% |

Geometric means over matching affected cells. Tokens 1–2 and W4A16 sanity measurements are excluded from these aggregates. Each arm latency is the geometric mean of its two phase medians.

- **Best displayed cell:** N3U TP8, 16,384 tokens, CuteDSL W4A4: **1300.619 → 1188.898 µs (+9.40%)**.
- **Worst displayed cell:** N3U TP8, 4 tokens, CuteDSL MXFP4x8: **36.240 → 40.136 µs (-9.71%)**.

## Full heatmaps

![EP](plots/fc2-hybrid-vs-pr-head-ep.png)

![TP](plots/fc2-hybrid-vs-pr-head-tp.png)

[EP SVG](plots/fc2-hybrid-vs-pr-head-ep.svg) · [TP SVG](plots/fc2-hybrid-vs-pr-head-tp.svg) · [All four absolute phase medians per cell](report/cells.csv) · [Machine-readable summary](report/summary.json)

## EP table

| Model | Tokens | W4A4 | PER-TOKEN | MXFP4x8 | MXFP8 | W4A16 sanity |
|---|---:|---:|---:|---:|---:|---:|
| V3 EP8 | 4 | +0.22% | -0.49% | -0.05% | -0.06% | -0.06% |
| V3 EP8 | 8 | +0.80% | +0.05% | -0.03% | -0.12% | +0.40% |
| V3 EP8 | 16 | +0.42% | +0.28% | +0.03% | +0.23% | +0.29% |
| V3 EP8 | 32 | +0.30% | +0.19% | -0.18% | +0.01% | +0.02% |
| V3 EP8 | 64 | +0.02% | -0.21% | +0.10% | -0.12% | -0.03% |
| V3 EP8 | 128 | +0.34% | +0.05% | +0.06% | +0.07% | +0.02% |
| V3 EP8 | 256 | +0.01% | -0.08% | +0.18% | +0.09% | -0.43% |
| V3 EP8 | 512 | +0.13% | -0.04% | -0.05% | -0.02% | -0.28% |
| V3 EP8 | 4,096 | +1.17% | +0.25% | +1.15% | +0.82% | -0.25% |
| V3 EP8 | 8,192 | +2.05% | +1.77% | +0.92% | +0.70% | +0.72% |
| V3 EP8 | 16,384 | +1.19% | +1.72% | +3.09% | +2.43% | +0.49% |
| V41F EP4 | 4 | -0.80% | -1.11% | -0.89% | -0.70% | +0.00% |
| V41F EP4 | 8 | -0.12% | -0.51% | -0.62% | -0.58% | -0.06% |
| V41F EP4 | 16 | +0.46% | -0.51% | -0.05% | +0.04% | -0.05% |
| V41F EP4 | 32 | -0.42% | +0.20% | -0.47% | -0.22% | +0.33% |
| V41F EP4 | 64 | -0.12% | +0.03% | -0.24% | -0.32% | +0.08% |
| V41F EP4 | 128 | -0.07% | -0.00% | -0.32% | -0.31% | +0.10% |
| V41F EP4 | 256 | -0.29% | -0.29% | -0.40% | -0.26% | -0.16% |
| V41F EP4 | 512 | +0.24% | -0.04% | +0.15% | +0.11% | -0.08% |
| V41F EP4 | 4,096 | -0.21% | -0.76% | -0.67% | -0.18% | -0.16% |
| V41F EP4 | 8,192 | -1.80% | -0.81% | -0.10% | -0.42% | -3.61% |
| V41F EP4 | 16,384 | -1.65% | -0.56% | -1.29% | -3.03% | +2.12% |
| K3 EP8 | 4 | -1.86% | -1.48% | -1.75% | N/A | +0.01% |
| K3 EP8 | 8 | -0.42% | -0.38% | -1.17% | N/A | +0.41% |
| K3 EP8 | 16 | -0.78% | -0.38% | -0.32% | N/A | -0.08% |
| K3 EP8 | 32 | -0.15% | -0.02% | +0.12% | N/A | +0.35% |
| K3 EP8 | 64 | -0.11% | +0.05% | +0.11% | N/A | +0.08% |
| K3 EP8 | 128 | +0.24% | +0.07% | -0.13% | N/A | -0.01% |
| K3 EP8 | 256 | +0.03% | -0.00% | +0.25% | N/A | +0.06% |
| K3 EP8 | 512 | +0.08% | +0.24% | -0.13% | N/A | +0.05% |
| K3 EP8 | 4,096 | +0.26% | -0.13% | -0.46% | N/A | -1.35% |
| K3 EP8 | 8,192 | -0.67% | +0.99% | -3.26% | N/A | +3.52% |
| K3 EP8 | 16,384 | -2.19% | -0.40% | -1.03% | N/A | -0.55% |
| N3U EP8 | 4 | -0.83% | -1.24% | -1.66% | -0.65% | -0.04% |
| N3U EP8 | 8 | -2.29% | -0.38% | -0.79% | -0.32% | +0.29% |
| N3U EP8 | 16 | -0.88% | -0.30% | -0.36% | -0.30% | -0.05% |
| N3U EP8 | 32 | -0.56% | -0.24% | -1.44% | -0.60% | +0.33% |
| N3U EP8 | 64 | -0.27% | -0.11% | -0.32% | -0.53% | -0.08% |
| N3U EP8 | 128 | -0.58% | -0.32% | -0.52% | -0.57% | -0.13% |
| N3U EP8 | 256 | -0.23% | -0.25% | +0.15% | -0.10% | -0.03% |
| N3U EP8 | 512 | +0.45% | +0.63% | -0.42% | +0.16% | -0.15% |
| N3U EP8 | 4,096 | +0.84% | +1.38% | +0.30% | -0.17% | -0.34% |
| N3U EP8 | 8,192 | +1.64% | +0.10% | +0.83% | +0.51% | -1.33% |
| N3U EP8 | 16,384 | +2.17% | +0.98% | -1.14% | +2.92% | -1.02% |

## TP table

| Model | Tokens | W4A4 | PER-TOKEN | MXFP4x8 | MXFP8 | W4A16 sanity |
|---|---:|---:|---:|---:|---:|---:|
| V3 TP8 | 4 | -1.62% | -3.56% | -3.04% | -1.16% | +0.30% |
| V3 TP8 | 8 | -1.21% | -2.82% | -1.12% | -1.43% | -0.07% |
| V3 TP8 | 16 | +0.64% | -0.25% | +1.53% | +0.20% | +1.12% |
| V3 TP8 | 32 | +1.12% | -1.29% | +3.27% | +1.31% | +0.00% |
| V3 TP8 | 64 | +2.10% | +0.24% | +2.01% | -0.67% | +0.35% |
| V3 TP8 | 128 | +3.35% | -0.50% | +2.05% | +0.13% | +0.06% |
| V3 TP8 | 256 | +1.01% | +0.06% | +1.92% | +0.04% | +0.33% |
| V3 TP8 | 512 | +5.17% | +1.44% | +4.61% | +1.40% | +0.16% |
| V3 TP8 | 4,096 | +7.95% | +4.39% | +8.03% | +5.59% | +0.09% |
| V3 TP8 | 8,192 | +6.26% | +5.72% | +5.79% | +5.28% | +0.04% |
| V3 TP8 | 16,384 | +7.08% | +6.37% | +4.65% | +4.45% | +0.07% |
| V41F TP4 | 4 | -1.63% | -2.85% | N/A | N/A | -0.13% |
| V41F TP4 | 8 | +0.45% | -1.81% | N/A | N/A | -0.05% |
| V41F TP4 | 16 | +0.54% | -0.83% | N/A | N/A | +0.02% |
| V41F TP4 | 32 | +0.48% | -0.82% | N/A | N/A | +0.21% |
| V41F TP4 | 64 | -0.44% | -0.16% | N/A | N/A | +0.17% |
| V41F TP4 | 128 | -0.14% | -0.06% | N/A | N/A | -0.12% |
| V41F TP4 | 256 | -1.23% | -0.48% | N/A | N/A | -0.04% |
| V41F TP4 | 512 | -0.93% | -0.39% | N/A | N/A | -0.05% |
| V41F TP4 | 4,096 | +1.34% | -0.37% | N/A | N/A | -0.31% |
| V41F TP4 | 8,192 | +3.56% | +1.33% | N/A | N/A | +0.17% |
| V41F TP4 | 16,384 | +1.32% | +1.33% | N/A | N/A | +0.18% |
| K3 TP8 | 4 | -3.86% | -5.62% | -5.20% | N/A | +0.02% |
| K3 TP8 | 8 | -3.21% | -2.84% | -3.70% | N/A | +0.95% |
| K3 TP8 | 16 | -0.23% | -0.60% | -0.43% | N/A | +0.32% |
| K3 TP8 | 32 | -0.88% | -0.19% | +0.54% | N/A | -0.55% |
| K3 TP8 | 64 | +0.51% | -0.41% | +1.51% | N/A | -0.14% |
| K3 TP8 | 128 | +0.60% | -0.11% | +0.35% | N/A | +0.12% |
| K3 TP8 | 256 | +1.23% | -0.00% | +2.68% | N/A | -0.06% |
| K3 TP8 | 512 | +1.10% | -0.26% | +0.45% | N/A | -0.04% |
| K3 TP8 | 4,096 | +5.06% | +1.86% | +7.11% | N/A | -0.85% |
| K3 TP8 | 8,192 | +2.71% | +3.10% | +5.75% | N/A | +0.33% |
| K3 TP8 | 16,384 | +6.46% | +3.62% | +3.43% | N/A | +0.03% |
| N3U TP8 | 4 | -9.59% | -9.05% | -9.71% | -7.71% | +0.22% |
| N3U TP8 | 8 | -5.58% | -6.53% | -6.81% | -5.05% | -0.07% |
| N3U TP8 | 16 | -2.62% | -2.55% | -2.72% | -1.59% | -0.15% |
| N3U TP8 | 32 | -1.98% | -1.65% | -2.03% | -1.59% | -0.22% |
| N3U TP8 | 64 | -2.34% | -1.45% | -0.29% | -1.52% | +0.38% |
| N3U TP8 | 128 | -2.78% | -1.94% | -0.59% | -1.53% | -0.20% |
| N3U TP8 | 256 | -0.82% | -1.17% | -2.36% | -1.57% | -0.08% |
| N3U TP8 | 512 | -0.05% | -0.92% | -1.87% | -1.33% | -0.19% |
| N3U TP8 | 4,096 | +2.62% | +1.39% | +1.86% | +1.99% | -1.50% |
| N3U TP8 | 8,192 | +8.51% | +4.43% | +8.31% | +5.71% | -0.23% |
| N3U TP8 | 16,384 | +9.40% | +5.54% | +3.71% | +4.37% | +0.20% |

## Evidence and limits

- **Source:** candidate is exactly `swap-ab-hybrid-output/fc2-01`, reproduced in `../../flashinfer-swap-ab-fc2-hybrid-review/`. Its five-file unstaged diff versus PR head is 131 insertions / 262 deletions. This includes padded-output cleanup and FC2 hybrid tails; FC1 payload TMA and native-fragment FC2 scalar tails are excluded.
- **Coverage:** 468 measured workloads, 396 displayed cells, 308 displayed affected cells; 1,872 medians / 187,200 raw samples. K3 MXFP8 and V41F TP MX retain existing N/A eligibility. Tokens 1–2 are saved but excluded from display and retention aggregates.
- **Method:** public `benchmarks/bench_moe_deepseek.py`, fresh C-A-A-C on the same GPU for each job, identical saved tactics and routing, unfused swap-AB, 10 warmups / 100 strict CUPTI cold-L2 CUDA-graph samples per phase. No event fallback or AUTO profiling. NVFP4 includes input activation quantization with the established per-token recipe. Timing excludes setup, weight preparation and compilation.
- **Runtime:** eight B300 SXM6 GPUs, C3, reused `nvcr.io/nvidia/pytorch:26.05-py3` image, CUDA 13.2, driver 595.91.07, CuTe DSL 4.8.0. Persistent native compilation caches are retained.
- **Validation boundary:** existing exact qualification reused for the identical 348-file candidate snapshot; no new sanitizer or full correctness-matrix run. Runtime source/tactic/cache/route/sample checks are enforced in every phase. This is fixed-tactic performance evidence, not independent retuning.
- **Repeatability:** maximum first/last control spread 6.52%; maximum candidate-repeat spread 6.94%. W4A16 displayed geometric shifts: EP -0.02%, TP +0.02%. Small differences should be interpreted with this variation.
- **Raw evidence:** [verified archive](evidence/verified.json), [source/config binding](evidence/raw/source.json), [commands, environment and raw CUPTI samples](evidence/raw/perf/), [archive manifest](evidence/raw/archive-manifest.json). TRTLLM and non-swap baselines were not rerun.
- **Publication:** source changes remain unstaged and unpushed; canonical PR checkout and PR body are unchanged.

Reproduce analysis and plots from the project root:

```sh
python3 optimization-20261028/fc2-hybrid-vs-head/analyze_perf.py \
  optimization-20261028/fc2-hybrid-vs-head/evidence/raw/perf \
  --output optimization-20261028/fc2-hybrid-vs-head/report
swap-ab-full-rerun-20261027/.venv-plot/bin/python \
  optimization-20261028/fc2-hybrid-vs-head/plot_heatmap.py
```
