# Retained staging versus shared NVFP4 prepared layout

Root selects this shared interface and maintenance improvement for retention.
The completed run is **0.173117% slower over8–4096**, so this is not an overall
performance-win claim. Publication is tracked separately in the project ledger.

Retention8–4096: **+0.173117% latency GM**, 5/10 wins. Full13 secondary: -0.152698% GM, 7/13 wins. Counts1/2/4 do not enter retention.

| Tokens | Retained staging ms | Shared layout ms | Change | Retained tactic | Shared-layout tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.088848 | 0.085088 | -4.232% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.106513 | 0.106128 | -0.361% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.119937 | 0.121106 | +0.975% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.136065 | 0.148705 | +9.290% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.156082 | 0.160066 | +2.553% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 32 | 0.176594 | 0.178001 | +0.797% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 64 | 0.208803 | 0.202978 | -2.790% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.212625 | 0.207521 | -2.400% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.212626 | 0.207697 | -2.318% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 512 | 0.221554 | 0.206354 | -6.861% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.239026 | 0.237858 | -0.489% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2048 | 0.312035 | 0.320691 | +2.774% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.474036 | 0.483602 | +2.018% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 1, 2, 16, 32, 128, 256; 7 same-choice rows. Same-choice variation: T4 +0.975%; T8 +9.290%; T64 -2.790%; T512 -6.861%; T1024 -0.489%; T2048 +2.774%; T4096 +2.018%. Sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 596.187686985s versus retained 599.645277633s; outer 599.651496083s, timer utility 6.022677812s. Setup/tuning wall is separate from primary latency.

All13×100 cold-L2 CUPTI samples reproduce printed medians;13×8 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, local bytes {'0': 104}.

Separate staging observations remain104 warmups:87 fused nonempty/17 empty Torch, with all80 retention observations fused. Original saved checks establish the native boundary; initial and build diagnostic deltas remain separate in comparison.json. No native validator was rerun.

Current sourceaf938 changes the shared prepared FP4/SF layout and corresponding W4A16 frontend/decode views on published stagingd891. The contract audit0070f5ef covers129 host tests plus4 actual GPU alias/graph/preparation cases. The reference audite5ac00ff covers18 rank tests/48 objects, including8 long-K and manual one-CTA coverage. Those validation scopes remain separate from performance; candidate native instruction/resource review is also separate.

Only the complete direct current run is used. Its original proof/result/closure hashes appear in comparison.json; accepted9ce current columns supply the entire baseline. No original/baseline/native validator rerun, historical controller walk, row splicing or drift adjustment.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-shared-layout-direct-auto-reconstruction-001/README.md) · [Reference audit](../cu132-recovery0909d-shared-layout-numerics-independent-001/audit.json) · [Contract audit](../cu132-recovery0909d-shared-layout-contracts-independent-001/audit.json)
