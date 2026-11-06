# Historical gap signals for the 82254e20 campaign

Saved candidate326c4a79 production kernels equal82254e20; differences are profiler selection, distributed metadata output, and manual sanitizer flags. These are historical cross-instance signals, **not** fresh822 measurements. Legacy MX TP comparisons include fused-finalize baselines; preserve that structural boundary. >2% candidate repeat spread is flagged, never filtered.

| Topology | Model | Tokens | Mode | Baseline | Speedup | Excess µs | Candidate spread |
|---|---|---:|---|---|---:|---:|---:|
| TP | v3 | 16384 | CuteDSL MXFP8 | Non-swap MXFP8† | -17.93% | +244.57 | 0.08% |
| TP | v3 | 8192 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -20.71% | +141.92 | 0.07% |
| TP | nemo3-ultra | 16384 | CuteDSL PER-TOKEN | TRTLLM PER-TOKEN | -7.67% | +138.27 | 0.10% |
| TP | v3 | 16384 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -10.71% | +133.83 | 0.59% |
| TP | v3 | 8192 | CuteDSL MXFP8 | Non-swap MXFP8† | -17.25% | +127.15 | 0.15% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A4 | TRTLLM W4A4 | -9.94% | +117.66 | 0.06% |
| TP | nemo3-ultra | 8192 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -16.22% | +111.37 | 1.00% |
| TP | nemo3-ultra | 8192 | CuteDSL MXFP8 | Non-swap MXFP8† | -14.16% | +104.43 | 2.51% |
| TP | v3 | 16384 | CuteDSL MXFP8 | TRTLLM MXFP8 | -7.02% | +95.72 | 0.08% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -7.89% | +95.69 | 5.72% |
| EP | nemo3-ultra | 16384 | CuteDSL W4A4 | Non-swap W4A4 | -14.86% | +87.79 | 0.06% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A4 | Non-swap W4A4 | -6.21% | +73.53 | 0.06% |
| TP | nemo3-ultra | 8192 | CuteDSL PER-TOKEN | TRTLLM PER-TOKEN | -7.35% | +72.07 | 0.03% |
| TP | nemo3-ultra | 8192 | CuteDSL W4A4 | TRTLLM W4A4 | -10.11% | +67.59 | 0.01% |
| TP | v3 | 4096 | CuteDSL MXFP8 | Non-swap MXFP8† | -14.26% | +65.01 | 0.06% |
| TP | v3 | 4096 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -16.40% | +63.41 | 0.02% |
| EP | kimi-k3 | 16384 | CuteDSL W4A4 | Non-swap W4A4 | -7.59% | +62.00 | 5.17% |
| EP | kimi-k3 | 8192 | CuteDSL W4A16 | W4A16 before PR | -5.96% | +61.84 | 0.31% |
| TP | kimi-k3 | 16384 | CuteDSL PER-TOKEN | Non-swap PER-TOKEN | -3.02% | +58.97 | 0.11% |
| TP | v3 | 16384 | CuteDSL MXFP4x8 | TRTLLM MXFP4x8 | -4.66% | +58.27 | 0.59% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP8 | Non-swap MXFP8† | -4.42% | +57.04 | 2.94% |
| EP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | Non-swap MXFP4x8† | -7.36% | +56.61 | 5.90% |
| TP | nemo3-ultra | 4096 | CuteDSL MXFP8 | Non-swap MXFP8† | -12.66% | +54.18 | 0.01% |
| EP | kimi-k3 | 16384 | CuteDSL W4A16 | W4A16 before PR | -2.20% | +44.70 | 1.03% |

Priorities:
1. TP MX prefill across V3/N3U: largest broad absolute gaps, but old fused-finalize comparisons require component/critical-path attribution.
2. N3U TP standardNVFP4/per-token versusTRT: both modes lose at8K/16K, useful general small-K scheduling/epilogue signals.
3. EP W4A4 prefill forN3U/K3: target general producer/consumer balance, preserving strong decode andV3/V41 performance.
4. W4A16 is a separate matched822 control arm; historical small losses alone do not justify new complexity.

All measured negative/positive rows are retained in `gaps.csv`; unsupported cells remain in the copied external summaries.
