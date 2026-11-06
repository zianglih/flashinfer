# Fixed8 raw5 versus raw4 — completed whole runs

Raw4 rejected: retention8–4096 GM **+1.745% latency**,3/10 wins,7 regressions. Full13 secondary GM−0.844%; small1/2/4 rows do not enter retention.

| Tokens | Retained raw5 ms | Raw4 ms | Change | Raw4 tactic |
|---:|---:|---:|---:|:---|
| 1 | 0.092689 | 0.083473 | -9.943% | M256/N64, C2, F4, epi, S2 |
| 2 | 0.122017 | 0.107697 | -11.736% | M256/N64, C2, F8, epi, S2 |
| 4 | 0.135169 | 0.128113 | -5.220% | M256/N64, C2, F4, epi, S2 |
| 8 | 0.148738 | 0.153761 | +3.377% | M256/N64, C2, F8, epi, S2 |
| 16 | 0.165250 | 0.171426 | +3.737% | M256/N64, C2, F8, epi, S2 |
| 32 | 0.192369 | 0.187906 | -2.320% | M256/N64, C2, F4, epi, S2 |
| 64 | 0.214466 | 0.215554 | +0.507% | M256/N64, C2, F8, epi, S2 |
| 128 | 0.218194 | 0.224386 | +2.838% | M256/N64, C2, F4, epi, S2 |
| 256 | 0.220193 | 0.219794 | -0.181% | M256/N64, C2, F4, epi, S2 |
| 512 | 0.227042 | 0.232882 | +2.572% | M256/N64, C2, F4, epi, S2 |
| 1024 | 0.245235 | 0.250946 | +2.329% | M256/N64, C2, F8, epi, S2 |
| 2048 | 0.331411 | 0.331396 | -0.005% | M256/N128, C2, F4, reuse, S2 |
| 4096 | 0.485093 | 0.508406 | +4.806% | M256/N128, C2, F4, reuse, S2 |

Seven tactic changes; six same-choice rows overall. Within retention, same-choiceT16+3.737%,T2048−0.0045%,T4096+4.806% limit causal attribution.

Benchmark subprocess 582.550899s versus retained 581.615758s; outer 584.653594s, timing utility 5.958210s. These are full-run costs, separate from per-shape primary latency.

Completed13×100 cold-L2 CUPTI samples,13×8 secondary HOT selection scores,104 winners/resources, allB3/raw4/S2/local0. Source1032373c; original87892/fetch94098/idle20823 closed. Failed fetch72819 is preserved; corrected path fetch did not rerun the benchmark.

Numerics12rank-tests/30objects passed; originalEP1 pytest0/wrapper1 and specific exact-pack factory admission remain separate. CurrentAUTO native2db is unchanged. No old baseline validators rerun.

[Full comparison and pins](comparison.json) · [Original reconstructed table](../cu132-recovery0909c-raw4-direct-auto-reconstruction-001/README.md) · [Numerical audit](../cu132-recovery0909c-raw4-direct-numerics-independent-001/audit.json)
