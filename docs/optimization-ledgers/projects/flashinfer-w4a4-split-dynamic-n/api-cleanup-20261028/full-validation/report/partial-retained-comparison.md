Partial current `d1767be1f` vs retained17bff (W4A16:99f4). Separate campaigns and fresh current tuning; not causal kernel attribution.

Ready jobs: kimi-k3-mxfp, kimi-k3-nvfp4, v3-mxfp, v3-nvfp4, v41-flash-mxfp, v41-flash-nvfp4. Visible cells: 165. Tokens1/2 excluded.

| Scope | Cells | Overall speed | Decode speed | Prefill speed |
|---|---:|---:|---:|---:|
| All | 165 | -0.08% | -0.04% | -0.19% |
| v3 | 55 | -0.05% | +0.01% | -0.20% |
| v41-flash | 55 | +0.04% | +0.09% | -0.09% |
| kimi-k3 | 55 | -0.24% | -0.23% | -0.27% |
| CuteDSL W4A4 | 33 | +0.23% | +0.26% | +0.15% |
| CuteDSL PER-TOKEN | 33 | -0.21% | -0.09% | -0.53% |
| CuteDSL MXFP4x8 | 33 | -0.45% | -0.23% | -1.05% |
| CuteDSL MXFP8 | 33 | +0.07% | -0.10% | +0.50% |
| CuteDSL W4A16 | 33 | -0.04% | -0.06% | +0.01% |

| Model | Dtype | Overall speed | Decode speed | Prefill speed |
|---|---|---:|---:|---:|
| V3 EP8 | CuteDSL W4A4 | +0.10% | +0.17% | -0.08% |
| V3 EP8 | CuteDSL PER-TOKEN | -0.27% | -0.24% | -0.35% |
| V3 EP8 | CuteDSL MXFP4x8 | -0.22% | +0.02% | -0.84% |
| V3 EP8 | CuteDSL MXFP8 | +0.07% | +0.16% | -0.17% |
| V3 EP8 | CuteDSL W4A16 | +0.08% | -0.07% | +0.46% |
| V41F EP4 | CuteDSL W4A4 | +0.41% | +0.71% | -0.36% |
| V41F EP4 | CuteDSL PER-TOKEN | -0.39% | -0.43% | -0.25% |
| V41F EP4 | CuteDSL MXFP4x8 | -0.18% | +0.10% | -0.93% |
| V41F EP4 | CuteDSL MXFP8 | -0.13% | -0.19% | +0.02% |
| V41F EP4 | CuteDSL W4A16 | +0.50% | +0.27% | +1.10% |
| K3 EP8 | CuteDSL W4A4 | +0.17% | -0.10% | +0.90% |
| K3 EP8 | CuteDSL PER-TOKEN | +0.02% | +0.41% | -1.00% |
| K3 EP8 | CuteDSL MXFP4x8 | -0.96% | -0.80% | -1.39% |
| K3 EP8 | CuteDSL MXFP8 | +0.25% | -0.27% | +1.66% |
| K3 EP8 | CuteDSL W4A16 | -0.69% | -0.38% | -1.51% |

Material regressions (>3% candidate latency increase):

| Model | Tokens | Dtype | Latency increase | Speed | A1 ms | A2 ms |
|---|---:|---|---:|---:|---:|---:|
| kimi-k3 | 4096 | CuteDSL W4A16 | +3.13% | -3.03% | 0.571349 | 0.536644 |
| kimi-k3 | 8 | CuteDSL MXFP4x8 | +3.03% | -2.94% | 0.077025 | 0.077121 |
