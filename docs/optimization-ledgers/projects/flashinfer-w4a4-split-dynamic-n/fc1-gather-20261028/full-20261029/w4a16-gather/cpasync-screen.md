# W4A16 five-WG cp.async screen

Candidate: unstaged `flashinfer-w4a16-gather-review`, patch `499ab9e33968ec557f8e4de0d0823301fe16715fb088871d3616e270a90ffd47`, against clean `fb66a27e`. Native frozen W4A16 tactics, C-A-A-C, 10 warmups / 100 CUPTI samples, cold-L2 CUDA Graph replay, no standalone prepare. FC2 retains the 4-WG design. B300 C3 GPU1 EP and GPU2 TP. Positive is `sqrt(C1*C2/(A1*A2)) - 1`. CSV contains all four phase medians, GPU UUID, and repeat spreads.

| Model | Topology | 8 | 256 | 4096 | 16384 |
|---|---|---:|---:|---:|---:|
| v3 | EP8 | +0.47% | +1.30% | -18.44% | -16.33% |
| v3 | TP8 | +12.53% | +7.76% | +18.56% | +17.51% |
| v41-flash | EP4 | -0.03% | -0.66% | -20.02% | -11.80% |
| v41-flash | TP4 | +2.45% | -4.02% | -8.08% | -3.07% |
| kimi-k3 | EP8 | +1.04% | +0.46% | -17.66% | -11.43% |
| kimi-k3 | TP8 | +1.45% | -0.84% | +2.96% | +7.68% |
| nemo3-ultra | EP8 | +1.61% | -0.39% | -8.94% | -9.69% |
| nemo3-ultra | TP8 | +2.05% | +0.92% | +4.09% | +7.39% |

All32 measured cells and their four phases are source-verified. All56 guarded full-shape FC1 compilations report zero local bytes. Exact tests:25 existing cases plus six derived multi-K/PDL cases; captured SASS had no LDL/STL. First harness launch stopped before timing due to an invalid backend selector; corrected harness uses the existing `--w4a16-only` observer filter, with unchanged timing/source/tactics.

The EP prefill loss is too large to retain; TP speedups establish the benefit of avoiding route-expanded BF16 traffic. TMA Gather4 comparison is in progress at the same budgets and tactics.
