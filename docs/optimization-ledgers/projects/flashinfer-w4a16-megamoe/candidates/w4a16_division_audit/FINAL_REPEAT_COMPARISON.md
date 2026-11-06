# Fast-divmod first run and requested repeat

Cold full-forward latency on hu-pdx-59. BEFORE is the complete e470 run; AFTER1 and AFTER2 are two complete source3da runs. Each uses the same public four F4 candidates and 100 cold-L2 CUPTI samples per row. Speedup is BEFORE ÷ AFTER; values above 1 are faster. Both runs remain separate, with no minima or row selection.

| Tokens | BEFORE (µs) | AFTER1 (µs) | Speedup1 | AFTER2 (µs) | Speedup2 |
|---:|---:|---:|---:|---:|---:|
| 1 | 84.801 | 69.488 | 1.2204× | 84.096 | 1.0084× |
| 2 | 104.528 | 102.033 | 1.0245× | 100.608 | 1.0390× |
| 4 | 120.817 | 118.129 | 1.0228× | 116.401 | 1.0379× |
| 8 | 138.897 | 137.745 | 1.0084× | 138.193 | 1.0051× |
| 16 | 148.577 | 150.881 | 0.9847× | 146.977 | 1.0109× |
| 32 | 180.545 | 179.346 | 1.0067× | 179.329 | 1.0068× |
| 64 | 201.537 | 197.057 | 1.0227× | 202.642 | 0.9945× |
| 128 | 203.297 | 222.610 | 0.9132× | 209.442 | 0.9707× |
| 256 | 210.081 | 209.169 | 1.0044× | 208.738 | 1.0064× |
| 512 | 215.041 | 215.234 | 0.9991× | 213.170 | 1.0088× |
| 1024 | 229.794 | 234.546 | 0.9797× | 234.385 | 0.9804× |
| 2048 | 312.563 | 308.452 | 1.0133× | 310.692 | 1.0060× |
| 4096 | 468.308 | 469.108 | 0.9983× | 469.092 | 0.9983× |
| 8192 | 775.576 | 786.245 | 0.9864× | 790.761 | 0.9808× |

| Aggregate | AFTER1 | AFTER2 |
|---|---:|---:|
| 8–8192 latency change | +0.801507% | +0.293781% |
| All14 latency change | -1.122209% | -0.367458% |
| 8–8192 geometric speedup | 0.992049× | 0.997071× |
| 8–8192 lower cold rows | 5/11 | 6/11 |
| All14 lower cold rows | 8/14 | 9/14 |

All choices match BEFORE: N64/F4/direct at 1–1024 and N128/F4/reuse at 2048–8192. Tokens 1/2/4 remain reported but are excluded from retention.

AFTER1 matched hot scores: 8–8192 22 lower / 3 equal / 19 higher out of 44; all14 30 / 5 / 21 out of 56.
AFTER2 matched hot scores: 8–8192 24 lower / 3 equal / 17 higher out of 44; all14 30 / 7 / 19 out of 56.

Hot scores are separately measured maximum-of-rank medians printed to 0.1 µs; cold values are medians of 100 iteration-wise rank maxima. The repeat reduces T128's observed cold increase from +9.500% to +3.023%, while T1024 and T8192 are higher in both runs. This comparison does not identify a cause or establish statistical significance. Neither complete run demonstrates a general 8–8192 latency gain; native code reductions and possible partial-shape benefits remain separate from measured full-workload performance.

Completed saved readers/comparators each ran once per candidate run. Full raw 56-score pairs: [AFTER1](../../logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-001/README.md) and [AFTER2](../../logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-002/README.md). No baseline, native, numerical or split rerun; original artifacts remain immutable. Retention/publication awaits root's decision.
