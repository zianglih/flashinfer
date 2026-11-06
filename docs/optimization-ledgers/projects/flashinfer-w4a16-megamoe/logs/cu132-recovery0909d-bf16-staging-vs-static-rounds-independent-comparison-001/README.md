# Retained staging versus static rounds — completed whole runs

Root rejects static rounds. Retention8–4096: **+1.742299% latency GM**, 4/10 wins. Full13 secondary: +0.858369% GM, 7/13 wins. Counts1/2/4 do not enter retention.

| Tokens | Retained loop staging ms | Static rounds ms | Change | Retained tactic | Static tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.088848 | 0.088385 | -0.521% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2 | 0.106513 | 0.104146 | -2.222% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 4 | 0.119937 | 0.115937 | -3.335% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 8 | 0.136065 | 0.152545 | +12.112% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.156082 | 0.159089 | +1.927% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 32 | 0.176594 | 0.195954 | +10.963% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.208803 | 0.209682 | +0.421% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.212625 | 0.212450 | -0.082% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 256 | 0.212626 | 0.207875 | -2.234% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.221554 | 0.209554 | -5.416% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.239026 | 0.239762 | +0.308% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 2048 | 0.312035 | 0.307042 | -1.600% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.474036 | 0.485189 | +2.353% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 1, 4, 16, 128, 1024; 8 same-choice rows. Same-choice variation: T2 -2.222%; T8 +12.112%; T32 +10.963%; T64 +0.421%; T256 -2.234%; T512 -5.416%; T2048 -1.600%; T4096 +2.353%. These sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 599.043463545s versus retained 599.645277633s; outer 601.117287084s, timer utility 5.821111927s. Setup/tuning wall is separate from each primary latency.

All13×100 cold-L2 CUPTI samples reproduce the printed medians;13×8 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, local bytes {'0': 104}.

Separate staging observations remain104 warmups:87 fused nonempty/17 empty Torch, with all80 retention observations fused. The eight rank-local staging functions report30 registers,128 threads,0 shared and0 local bytes (retained loop capture18 registers). These are separate from104 Mega objects. Original saved checks report23 native entries unchanged.

Sourcea80c/kernel8daa is the corrected constexpr-round version on published stagingd891. Eleven copy/graph tests pass in audit20e71bcc; no new Mega cohort. Original79277 failed on the H288 CuTe join after4 passes, then distinct tail locals fixed the compiler binding; failure and retry remain separate. Root's native review establishes code generation separately from this arithmetic. No original/baseline/native validator rerun.

Original98048/idle52745/fetch21384 allclosed0. Completionb70a3c6c, original reconstruction8ebca27a and result57468614 supply this entire current run. Root restores publishedca03 staging after rejection, then proceeds with the separate group256 trial; prefetch4 remains held and unmeasured. PRca03/bodyfba7 stays unchanged.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-bf16-static-rounds-retry1-direct-auto-reconstruction-001/README.md) · [Saved eleven-test audit](../cu132-recovery0909d-bf16-static-rounds-retry1-numerics-independent-001/audit.json)
