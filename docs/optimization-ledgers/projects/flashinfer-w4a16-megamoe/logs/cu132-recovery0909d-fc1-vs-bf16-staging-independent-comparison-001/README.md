# FC1 versus fused BF16 staging — completed whole runs

Root retains fused staging after completed original checks. Retention8–4096: **-3.363447% latency GM**, 9/10 wins. Only T1024 regresses (+1.007%). Full13 secondary: -2.864297% GM, 11/13 wins. Counts1/2/4 do not enter retention.

| Tokens | FC1 ms | Fused staging ms | Change | FC1 tactic | Fused staging tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.092465 | 0.088848 | -3.912% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 2 | 0.107905 | 0.106513 | -1.290% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 4 | 0.117889 | 0.119937 | +1.737% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 8 | 0.140817 | 0.136065 | -3.375% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 16 | 0.163169 | 0.156082 | -4.343% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 32 | 0.188706 | 0.176594 | -6.418% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 64 | 0.211186 | 0.208803 | -1.128% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 128 | 0.218674 | 0.212625 | -2.766% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 256 | 0.223778 | 0.212626 | -4.984% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 512 | 0.231954 | 0.221554 | -4.484% | M256/N64, C2, F8, epi, S2 | M256/N64, C2, F8, epi, S2 |
| 1024 | 0.236642 | 0.239026 | +1.007% | M256/N64, C2, F4, epi, S2 | M256/N64, C2, F4, epi, S2 |
| 2048 | 0.331523 | 0.312035 | -5.878% | M256/N128, C2, F8, reuse, S2 | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.478853 | 0.474036 | -1.006% | M256/N128, C2, F4, reuse, S2 | M256/N128, C2, F4, reuse, S2 |

Tactics changed at 1, 2, 8, 128, 2048; 8 same-choice rows. Same-choice variation: T4 +1.737%; T16 -4.343%; T32 -6.418%; T64 -1.128%; T256 -4.984%; T512 -4.484%; T1024 +1.007%; T4096 -1.006%. These sequential AUTO runs do not isolate a fixed-tactic effect.

Benchmark subprocess 599.645277633s versus FC1 616.903775103s; outer 601.479226250s, timer utility 5.971667201s. Setup/tuning wall is separate from each primary latency.

All13×100 cold-L2 CUPTI samples reproduce the printed medians;13×8 secondary hot-score rankings,104 winner dictionaries and104 Mega resources agree. B stages {'3': 104}, raw stages {'4': 16, '5': 88}, scheduler stages {'2': 104}, local bytes {'0': 104}.

Separate staging observations:104 warmup records,87 fused nonempty and17 empty Torch fallback; all80 retention observations fused. Eight rank-local compiled staging functions report18 registers,128 threads,0 shared and0 local bytes. These are separate from104 Mega objects.

Current sourcea747 adds the private stager and its kernel plus the backend import on exact FC1source96c. Current9 copy/graph tests and4 EP2 rank-tests/16 Mega objects passed in numerical audite78a; inherited FC116/40 and B3 evidence were not rerun. Original82468/idle3631/fetch55843 allclosed0; completionb828bfe1, reconstruction0d621b02. Original saved checks report23 native entries unchanged.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-bf16-staging-direct-auto-reconstruction-001/README.md) · [Current numerical audit](../cu132-recovery0909d-bf16-staging-numerics-independent-001/audit.json)

Precision note: the exact T1024 numeric field is +1.0074289432983052%; the frozen decision sentence's +1.007435% is a prose rounding typo. Ratios, medians, aggregates and the four-decimal PR value +1.0074% are unchanged.
