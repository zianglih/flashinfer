# W4 output-ring primary comparison

The original 104-cell CAAC observation remains primary. The separate six-cell ACCA diagnostic does not replace any row.

![Causal heatmap](output-ring-vs-retained.png)

| Model | EP | TP |
|---|---:|---:|
| V3 | -0.015% | +0.263% |
| V41F | +0.116% | +0.305% |
| K3 | +0.172% | -0.018% |
| N3U | +0.010% | +0.114% |

Geomeans exclude tokens 1/2. Overall +0.118%; decode +0.031%, middle +0.066%, prefill +0.317%. These are neutral-scale changes, with 31 negative retention cells. The primary observation has 103 clock-exception quartiles and 2 missing windows; prefill repeat spread reaches 8.3%.

All 208 measured FC1/FC2 stage configurations/resources agree across four phases; 448 loaded kernel records have zero local bytes. Native qualification separately shows 1–4 fewer instructions per sampled GEMM.

[All 104 raw phase medians](cells.csv). The original measurement logs and detailed clock/resource records are in the sealed evidence folder.

## Unchanged native benchmark table outputs

Each file includes all 13 token rows and is byte-identical to the measured process’s table suffix. The printer was called on structured result records; no table was parsed. All 32 phase outputs are preserved.

- [ep-kimi-k3-w4a16 · 0-control](native-tables/ep-kimi-k3-w4a16-0-control.txt)
- [ep-kimi-k3-w4a16 · 1-candidate](native-tables/ep-kimi-k3-w4a16-1-candidate.txt)
- [ep-kimi-k3-w4a16 · 2-candidate](native-tables/ep-kimi-k3-w4a16-2-candidate.txt)
- [ep-kimi-k3-w4a16 · 3-control](native-tables/ep-kimi-k3-w4a16-3-control.txt)
- [ep-nemo3-ultra-w4a16 · 0-control](native-tables/ep-nemo3-ultra-w4a16-0-control.txt)
- [ep-nemo3-ultra-w4a16 · 1-candidate](native-tables/ep-nemo3-ultra-w4a16-1-candidate.txt)
- [ep-nemo3-ultra-w4a16 · 2-candidate](native-tables/ep-nemo3-ultra-w4a16-2-candidate.txt)
- [ep-nemo3-ultra-w4a16 · 3-control](native-tables/ep-nemo3-ultra-w4a16-3-control.txt)
- [ep-v3-w4a16 · 0-control](native-tables/ep-v3-w4a16-0-control.txt)
- [ep-v3-w4a16 · 1-candidate](native-tables/ep-v3-w4a16-1-candidate.txt)
- [ep-v3-w4a16 · 2-candidate](native-tables/ep-v3-w4a16-2-candidate.txt)
- [ep-v3-w4a16 · 3-control](native-tables/ep-v3-w4a16-3-control.txt)
- [ep-v41-flash-w4a16 · 0-control](native-tables/ep-v41-flash-w4a16-0-control.txt)
- [ep-v41-flash-w4a16 · 1-candidate](native-tables/ep-v41-flash-w4a16-1-candidate.txt)
- [ep-v41-flash-w4a16 · 2-candidate](native-tables/ep-v41-flash-w4a16-2-candidate.txt)
- [ep-v41-flash-w4a16 · 3-control](native-tables/ep-v41-flash-w4a16-3-control.txt)
- [tp-kimi-k3-w4a16 · 0-control](native-tables/tp-kimi-k3-w4a16-0-control.txt)
- [tp-kimi-k3-w4a16 · 1-candidate](native-tables/tp-kimi-k3-w4a16-1-candidate.txt)
- [tp-kimi-k3-w4a16 · 2-candidate](native-tables/tp-kimi-k3-w4a16-2-candidate.txt)
- [tp-kimi-k3-w4a16 · 3-control](native-tables/tp-kimi-k3-w4a16-3-control.txt)
- [tp-nemo3-ultra-w4a16 · 0-control](native-tables/tp-nemo3-ultra-w4a16-0-control.txt)
- [tp-nemo3-ultra-w4a16 · 1-candidate](native-tables/tp-nemo3-ultra-w4a16-1-candidate.txt)
- [tp-nemo3-ultra-w4a16 · 2-candidate](native-tables/tp-nemo3-ultra-w4a16-2-candidate.txt)
- [tp-nemo3-ultra-w4a16 · 3-control](native-tables/tp-nemo3-ultra-w4a16-3-control.txt)
- [tp-v3-w4a16 · 0-control](native-tables/tp-v3-w4a16-0-control.txt)
- [tp-v3-w4a16 · 1-candidate](native-tables/tp-v3-w4a16-1-candidate.txt)
- [tp-v3-w4a16 · 2-candidate](native-tables/tp-v3-w4a16-2-candidate.txt)
- [tp-v3-w4a16 · 3-control](native-tables/tp-v3-w4a16-3-control.txt)
- [tp-v41-flash-w4a16 · 0-control](native-tables/tp-v41-flash-w4a16-0-control.txt)
- [tp-v41-flash-w4a16 · 1-candidate](native-tables/tp-v41-flash-w4a16-1-candidate.txt)
- [tp-v41-flash-w4a16 · 2-candidate](native-tables/tp-v41-flash-w4a16-2-candidate.txt)
- [tp-v41-flash-w4a16 · 3-control](native-tables/tp-v41-flash-w4a16-3-control.txt)
