# W4A16 five-WG TMA Gather4 screen

Candidate: unstaged `flashinfer-w4a16-tma-gather-review`, patch `1e6af46cbd316c349c18b7e293474cb235bafa53b64dc1f498012961ee9ab212`, against clean `fb66a27e`. Native frozen W4A16 tactics, C-A-A-C, 10 warmups / 100 CUPTI samples, cold-L2 CUDA Graph replay, no standalone prepare. FC2 retains the 4-WG design. B300 C3 GPU1 EP and GPU2 TP. Positive is `sqrt(C1*C2/(A1*A2)) - 1`. CSV contains all four phase medians, GPU UUID, and repeat spreads.

| Model | Topology | 8 | 256 | 4096 | 16384 |
|---|---|---:|---:|---:|---:|
| v3 | EP8 | -8.69% | +0.59% | +2.14% | +8.53% |
| v3 | TP8 | +11.84% | +6.83% | +35.47% | +30.25% |
| v41-flash | EP4 | -5.72% | +0.12% | +1.09% | +5.53% |
| v41-flash | TP4 | -6.90% | +0.38% | +13.03% | +12.76% |
| kimi-k3 | EP8 | -0.67% | +0.86% | +0.88% | +1.06% |
| kimi-k3 | TP8 | -4.01% | +1.96% | +18.99% | +19.35% |
| nemo3-ultra | EP8 | +1.24% | +0.97% | +0.12% | +4.21% |
| nemo3-ultra | TP8 | +1.51% | +2.51% | +14.32% | +16.83% |

All32 measured cells and their four phases are source-verified. All56 guarded full-shape FC1 compilations report zero local bytes. Exact tests:25 existing cases plus six derived multi-K/PDL cases and one old-layout case; captured SASS had no LDL/STL. First harness launch stopped before timing due to an invalid backend selector; corrected harness uses the existing `--w4a16-only` observer filter, with unchanged timing/source/tactics.

TMA removes the cp.async EP prefill regression and improves TP prefill substantially; remaining T8 regressions need cache/publication cleanup and existing-tactic retuning. This prototype uses zero activation cache hint, inherited from the reused Rubin helper. It remains unstaged and unretained.
