# W4A16 small-token EP/TP regression check

Measured source: [`14a338579`](https://github.com/flashinfer-ai/flashinfer/commit/14a338579eb8acddcc5cfd1cc58871fc0788de22) versus pre-PR [`002529e17`](https://github.com/flashinfer-ai/flashinfer/commit/002529e17b22567a071091053c6c4dc2a55e050e). The later reviewer-fix commit changes host validation/docs/tests, not the measured kernels.

The two PNG/SVG heatmaps are unchanged copies of the verified plots. Each CSV includes all cells, absolute latency, both phase medians, repeat spread, selected tactics and GPU identity. The Markdown files show the full latency tables. Per-iteration traces are excluded from this compact publication bundle. `SHA256SUMS` covers every other file.

## Method

- NVIDIA B200 and B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2. Each rank-local job uses one GPU; there is no distributed communication in timing.
- `benchmarks/bench_moe_deepseek.py`, W4A16 functional API, BF16 input/NVFP4 weights, unfused finalization, PDL enabled. No input quantizer is timed for W4A16.
- V3, K3 and N3U at EP8 or TP8; V41F at EP4 or TP4. Tokens: **4, 8, 16**. Four models × two topologies × three token counts = 24 workloads per GPU family.
- Before/OFF/ON/ON/OFF/before order, with all arms of a job on the same GPU. Each phase uses 10 warmups and 100 strict CUPTI CUDA-graph samples with cold L2: 14,400 measured samples per GPU family.
- **OFF** retains the original 64-row gated weight layout; **ON** uses the new 16-row layout. Before and OFF replay the same baseline tactics; ON replays its retained tactics. These frozen choices originated on B300 and do not claim independently optimal B200 tuning.
- Latency is the geometric mean of each arm's two phase medians. Speedup is `(before/current - 1) × 100%`; negative is slower. Colors saturate at ±10%; labels retain the full value. An asterisk marks more than 2% repeat spread; none occurred in these matrices.

The old source uses the preserved benchmark adapter (SHA256 `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`). Sources, frozen choices, routes, raw timing spans and plot values were verified. Maximum phase-median repeat spread was 0.541% on B200 and 0.466% on B300. Sampled clocks were stable throughout; this is coarse NVML evidence, not per-kernel clock measurement.

## Separate fresh-tuning check

The following **V3 EP8 / 4-token** experiment freshly tunes each arm on its own GPU family, then replays the selected choices in the same balanced six-phase order. It is separate from the fixed-choice heatmaps and does not replace any matrix cell.

| GPU | Before (µs) | Current OFF (µs) | Current ON (µs) | OFF speedup | ON speedup |
|---|---:|---:|---:|---:|---:|
| B200 |50.904|54.224|53.696|−6.12%|−5.20%|
| B300 |50.793|50.153|50.320|+1.28%|+0.94%|

Small-token EP regressions remain, including after tuning on B200. TP improves in aggregate. CUPTI timelines localize the additional critical-path time to FC1, but do not establish an instruction-level cause. As recorded in the [review report](https://github.com/flashinfer-ai/flashinfer/pull/7290#discussion_r4456145003) and [author response](https://github.com/flashinfer-ai/flashinfer/pull/7290#discussion_r4459749590), the current design is retained and the remaining EP gaps are deferred to a follow-up.
