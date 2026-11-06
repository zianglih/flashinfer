# Retained shared layout versus ACC1/decoded3

Retention8–4096: **+2.515221% latency GM**, 1/10 wins. Full13 secondary: +1.133365% GM, 3/13 wins. Counts1/2/4 do not enter retention.

| Tokens | Retained shared-layout ms | ACC1 ms | Change | Retained tactic | ACC1 tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.085088 | 0.081728 | -3.949% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.106128 | 0.097106 | -8.501% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.121106 | 0.124449 | +2.760% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 8 | 0.148705 | 0.149265 | +0.377% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 16 | 0.160066 | 0.162257 | +1.369% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 32 | 0.178001 | 0.188626 | +5.969% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.202978 | 0.212690 | +4.785% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.207521 | 0.217122 | +4.627% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 256 | 0.207697 | 0.214914 | +3.475% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 512 | 0.206354 | 0.218099 | +5.692% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 1024 | 0.237858 | 0.229874 | -3.357% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2048 | 0.320691 | 0.324627 | +1.227% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F8, epi, S2 |
| 4096 | 0.483602 | 0.490197 | +1.364% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 4, 8, 32, 128, 512, 2048; 7 same-choice rows. Same-choice variation: T1 -3.949%; T2 -8.501%; T16 +1.369%; T64 +4.785%; T256 +3.475%; T1024 -3.357%; T4096 +1.364%. Sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 593.708782435s versus retained 596.187686985s; outer 597.043369875s, timer utility 6.002159850s. Setup/tuning wall is separate from primary latency.

All13×100 cold-L2 CUPTI samples reproduce printed medians;13×8 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, accumulator stages {'1': 16, '2': 88}, decoded stages {'3': 104}, local bytes {'0': 104}.

Separate staging observations remain104 warmups:87 fused nonempty/17 empty Torch, with all80 retention observations fused. Original saved checks establish the native boundary; initial and build diagnostic deltas remain separate in comparison.json. No native validator was rerun.

Current source e899 changes only the kernel/epilogue accumulator rule on published shared-layout af938: N128 uses one physical/pipeline/epilogue stage and three decoded stages; N64 keeps two accumulator stages and three decoded stages. The current numerical audit covers 13 rank tests/40 objects, including N128 long-K and one-CTA manual coverage, with an unchanged N64 control. The prior 129 host/4 GPU shared-layout contract evidence is inherited, not rerun. Native instruction/resource review is separate from this arithmetic audit.

Only the complete direct current run is used. Its original proof/result/closure hashes appear in comparison.json; accepted1a763 current columns supply the entire baseline. No original/baseline/native validator rerun, historical controller walk, row splicing or drift adjustment.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-single-acc-direct-auto-reconstruction-001/README.md) · [Current numerical audit](../cu132-recovery0909d-single-acc-numerics-independent-001/audit.json) · [Inherited contract audit](../cu132-recovery0909d-shared-layout-contracts-independent-001/audit.json)

Root decision: **reject ACC1** on the 8–4096 criterion. Retain the entire
shared-layout1a763 baseline and published056ce/bodyfd2. The comparison JSON
remains the original immutable arithmetic report; restoration and later K128
work are tracked separately in entry059.
