# Retained shared layout versus K128 catalog16

Retention8–4096: **+0.463700% latency GM**, 6/10 wins. Full13 secondary: -1.838736% GM, 8/13 wins. Counts1/2/4 do not enter retention.

| Tokens | Retained shared-layout ms | K128 catalog16 ms | Change | Retained tactic | Catalog16 tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.085088 | 0.072240 | -15.100% | M256/N64/K256, C2, F4, epi, S2 | M256/N128/K256, C2, F4, epi, S2 |
| 2 | 0.106128 | 0.092497 | -12.844% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 4 | 0.121106 | 0.122769 | +1.373% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 8 | 0.148705 | 0.147121 | -1.065% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 16 | 0.160066 | 0.156210 | -2.409% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 32 | 0.178001 | 0.184210 | +3.488% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 64 | 0.202978 | 0.207058 | +2.010% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 128 | 0.207521 | 0.206642 | -0.424% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 256 | 0.207697 | 0.214050 | +3.059% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 512 | 0.206354 | 0.212050 | +2.760% | M256/N64/K256, C2, F8, epi, S2 | M256/N64/K256, C2, F4, epi, S2 |
| 1024 | 0.237858 | 0.236451 | -0.592% | M256/N64/K256, C2, F4, epi, S2 | M256/N64/K256, C2, F8, epi, S2 |
| 2048 | 0.320691 | 0.315683 | -1.562% | M256/N128/K256, C2, F4, reuse, S2 | M256/N128/K256, C2, F4, reuse, S2 |
| 4096 | 0.483602 | 0.481540 | -0.426% | M256/N128/K256, C2, F4, reuse, S2 | M256/N128/K256, C2, F4, reuse, S2 |

Tactics changed at 1, 2, 8, 32, 128, 512, 1024; 6 same-choice rows. Same-choice variation: T4 +1.373%; T16 -2.409%; T64 +2.010%; T256 +3.059%; T2048 -1.562%; T4096 -0.426%. Sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 932.001498857s versus retained 596.187686985s; outer 935.068686625s, timer utility 6.053761550s. Setup/tuning wall is separate from primary latency.

All13×100 cold-L2 CUPTI samples reproduce printed medians;13×16 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 24, '5': 80}, scheduler stages {'2': 104}, accumulator stages {'2': 104}, decoded stages {'2': 24, '3': 80}, selected K {'256': 104}, local bytes {'0': 104}.

Separate staging observations remain104 warmups:87 fused nonempty/17 empty Torch, with all80 retention observations fused. Original saved checks establish the native boundary; initial and build diagnostic deltas remain separate in comparison.json. No native validator was rerun.

Current source58986051 adds the M256 K128 geometry and extends the original eight K256 catalog entries with eight K128 entries, all S2. ACC2 remains physical/pipeline/epilogue ownership for both N values. Each actual selected K determines decoded depth: N64/N128 use6/4 at K128 and3/2 at K256. The current numerical audit separately covers18 rank tests/42 objects and the existing public catalog-reset host test; prior shared-layout contract evidence remains inherited. Native instruction/resource review is separate from this arithmetic audit.

Only the complete direct current run is used. Its original proof/result/closure hashes appear in comparison.json; accepted1a763 current columns supply the entire baseline. No original/baseline/native validator rerun, historical controller walk, row splicing or drift adjustment.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-k128-catalog16-direct-auto-reconstruction-001/README.md) · [Current numerical audit](../cu132-recovery0909d-k128-catalog16-numerics-independent-001/audit.json) · [Inherited contract audit](../cu132-recovery0909d-shared-layout-contracts-independent-001/audit.json)

## Root decision

Do not promote initial K128/catalog16: zero K128 winners and56.33% more benchmark subprocess time, with ten-row latency GM+0.463700%. Preserve the whole initial16 run as experimental BEFORE for B6; the published shared-layout1a763 run remains the retained baseline. No canonical PR/source publication. [All K128/K256 selection scores](SELECTION_SCORES.md).
