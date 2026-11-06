# Retained 83dfef8a: independent performance summary

Current `83dfef8a656384f5cd10db847602593bb6f9b2c6`; published prior `d1767be1f42fdc371f90db4fb06598299ea32845`. Exclude tokens 1/2. Decode: 4–512; prefill: 4096/8192/16384.

Per-cell geometric mean of A1/A2 medians; equal-weight geometric mean of ratios across unique candidate dtype cells. External controls kept separate; W4A16 is separate sanity scope.

Freshly autotuned historical comparison across campaigns/hardware assignments, not a causal code-only A/B. Saved external control data is reused. Controlled FC2 R3 retained +4.678% TP prefill / +0.027% EP prefill on its bounded four-token fixed-winner screen; this refresh also includes prior K-tail and K96 changes.

| Comparison | Topology | Scope | Cells | Decode | Prefill | All |
|---|---|---|---:|---:|---:|---:|
| 83df vs external | EP | TRTLLM | 154 | +5.177% | +10.592% | +6.627% |
| 83df vs external | EP | Non-swap | 154 | +20.227% | +9.396% | +17.171% |
| 83df vs external | EP | Pre-PR W4A16 | 44 | -0.051% | -0.016% | -0.042% |
| 83df vs external | TP | TRTLLM | 132 | +3.315% | -16.435% | -2.493% |
| 83df vs external | TP | Non-swap | 132 | +18.309% | -18.217% | +6.975% |
| 83df vs external | TP | Pre-PR W4A16 | 44 | +0.110% | -0.917% | -0.171% |
| 83df vs d1767 historical | EP | affected | 165 | -0.052% | +0.169% | +0.009% |
| 83df vs d1767 historical | EP | W4A16 sanity | 44 | +0.144% | -0.779% | -0.109% |
| 83df vs d1767 historical | EP | all five | 209 | -0.010% | -0.031% | -0.016% |
| 83df vs d1767 historical | TP | affected | 143 | +0.049% | +6.241% | +1.701% |
| 83df vs d1767 historical | TP | W4A16 sanity | 44 | -0.081% | -1.789% | -0.550% |
| 83df vs d1767 historical | TP | all five | 187 | +0.018% | +4.294% | +1.167% |

## Worst remaining same-dtype external gaps

| Topology | Segment | Model | Format | Tokens | Control | Speedup | Latency increase |
|---|---|---|---|---:|---|---:|---:|
| EP | decode | v41-flash | MXFP8 | 128 | TRTLLM | -0.884% | +0.892% |
| EP | decode | kimi-k3 | MXFP4x8 | 64 | TRTLLM | -0.860% | +0.868% |
| EP | decode | v41-flash | MXFP8 | 64 | TRTLLM | -0.737% | +0.742% |
| EP | decode | kimi-k3 | W4A4 | 64 | TRTLLM | -0.601% | +0.605% |
| EP | prefill | nemo3-ultra | W4A4 | 4096 | Non-swap | -12.595% | +14.411% |
| EP | prefill | v3 | MXFP4x8 | 16384 | Non-swap | -7.889% | +8.565% |
| EP | prefill | nemo3-ultra | MXFP4x8 | 16384 | Non-swap | -6.899% | +7.411% |
| EP | prefill | nemo3-ultra | W4A4 | 16384 | Non-swap | -5.946% | +6.322% |
| TP | decode | v3 | W4A4 | 512 | TRTLLM | -10.977% | +12.331% |
| TP | decode | v3 | MXFP4x8 | 512 | Non-swap | -9.744% | +10.796% |
| TP | decode | v3 | W4A4 | 512 | Non-swap | -8.552% | +9.352% |
| TP | decode | v3 | MXFP8 | 512 | Non-swap | -8.213% | +8.948% |
| TP | prefill | v3 | MXFP4x8 | 4096 | Non-swap | -37.534% | +60.087% |
| TP | prefill | v3 | MXFP4x8 | 8192 | Non-swap | -37.137% | +59.076% |
| TP | prefill | v3 | MXFP8 | 8192 | Non-swap | -34.202% | +51.980% |
| TP | prefill | v3 | MXFP8 | 4096 | Non-swap | -31.864% | +46.764% |

## Largest historical latency increases

| Topology | Segment | Model | Format | Tokens | Control | Speedup | Latency increase |
|---|---|---|---|---:|---|---:|---:|
| EP | decode | nemo3-ultra | MXFP4x8 | 8 | d1767 | -8.350% | +9.110% |
| EP | decode | nemo3-ultra | W4A4 | 8 | d1767 | -2.347% | +2.404% |
| EP | decode | v3 | MXFP4x8 | 4 | d1767 | -2.203% | +2.253% |
| EP | decode | kimi-k3 | W4A4 | 8 | d1767 | -2.191% | +2.240% |
| EP | prefill | nemo3-ultra | W4A4 | 4096 | d1767 | -8.349% | +9.110% |
| EP | prefill | nemo3-ultra | MXFP8 | 16384 | d1767 | -5.500% | +5.820% |
| EP | prefill | nemo3-ultra | PER-TOKEN | 8192 | d1767 | -2.972% | +3.063% |
| EP | prefill | nemo3-ultra | W4A4 | 16384 | d1767 | -2.317% | +2.372% |
| TP | decode | kimi-k3 | PER-TOKEN | 16 | d1767 | -1.506% | +1.529% |
| TP | decode | v3 | PER-TOKEN | 64 | d1767 | -1.359% | +1.378% |
| TP | decode | v41-flash | PER-TOKEN | 16 | d1767 | -1.302% | +1.319% |
| TP | decode | kimi-k3 | W4A4 | 4 | d1767 | -1.224% | +1.239% |
| TP | prefill | v41-flash | PER-TOKEN | 4096 | d1767 | -0.200% | +0.200% |

All cell values, history grouped by model/format, exact input hashes, unsupported exclusions and counted cells are in the accompanying CSV/JSON files. A negative speedup means the candidate is slower; latency increase uses the inverse ratio and is a different percentage.
