# Retained staging versus MMA decoded-readiness probe

Root rejects the readiness probe under the8–4096 criterion. Published staging ca03/bodyfba7 and its PR table remain unchanged.

Retention8–4096: **+0.658947% latency GM**, 4/10 wins. Full13 secondary: -0.134748% GM, 6/13 wins. Counts1/2/4 do not enter retention.

| Tokens | Retained staging ms | MMA probe ms | Change | Retained tactic | Probe tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.088848 | 0.085153 | -4.159% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 2 | 0.106513 | 0.097328 | -8.623% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 4 | 0.119937 | 0.126017 | +5.069% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.136065 | 0.143729 | +5.633% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 16 | 0.156082 | 0.149057 | -4.501% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 32 | 0.176594 | 0.190402 | +7.819% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.208803 | 0.210578 | +0.850% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 128 | 0.212625 | 0.205426 | -3.386% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.212626 | 0.215714 | +1.452% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 512 | 0.221554 | 0.210754 | -4.875% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.239026 | 0.234706 | -1.807% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 2048 | 0.312035 | 0.326274 | +4.563% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, epi, S2 |
| 4096 | 0.474036 | 0.482068 | +1.694% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 2, 8, 64, 128, 256, 1024, 2048; 6 same-choice rows. Same-choice variation: T1 -4.159%; T4 +5.069%; T16 -4.501%; T32 +7.819%; T512 -4.875%; T4096 +1.694%. Sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 598.367583816s versus retained 599.645277633s; outer 600.420715084s, timer utility 6.407088273s. Setup/tuning wall is separate from primary latency.

All13×100 cold-L2 CUPTI samples reproduce printed medians;13×8 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, local bytes {'0': 104}.

Separate staging observations remain104 warmups:87 fused nonempty/17 empty Torch, with all80 retention observations fused. The original saved checks preserve all non-diagnostic native records; initial empty flashinfer_jit.log addition is recorded separately. No native validator was rerun.

Current source66cc differs from published stagingd891 only by the MMA decoded-readiness probe in kernel3238. The numerical saved audit4c50 reconciles16 rank tests/40 objects, including8 long-K rank cases. Matching native N64/N128 captures and existing pipeline state review are separate source/native evidence, not new performance measurements.

Only complete AUTO003/original98105 is measured here. AUTO001/96799 and002/7525 are preserved predriver failures with zero benchmark rows. Original98105/idle1684/fetch57020 allclosed0. This report consumes original proof2dca and result311e directly, with accepted9ce current columns only. No original/baseline/native validator rerun, row splicing or drift adjustment.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-mma-decoded-readiness-probe-direct-auto-reconstruction-003/README.md) · [Saved numerical audit](../cu132-recovery0909d-mma-decoded-readiness-probe-numerics-independent-001/audit.json)
