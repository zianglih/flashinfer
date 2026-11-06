# Same-node CONTROL screen: 38870 → e359

Complete fixed CONTROL screening only; candidate auto is unrun. Same-node unbracketed comparison changes three kernel/shared utility files and preserves the benchmark/logger/scorer. Paired split source also changes. No promotion or row minima.

| Tokens | Baseline split ms | Baseline Mega ms | Candidate split ms | Candidate Mega ms | Mega change | Split change | Candidate split/Mega |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.078321 | 0.093409 | 0.091025 | 0.097713 | +4.608% | +16.220% | 0.931555 |
| 2 | 0.118209 | 0.117889 | 0.114929 | 0.130209 | +10.451% | -2.775% | 0.882650 |
| 4 | 0.151617 | 0.138209 | 0.144929 | 0.133649 | -3.299% | -4.411% | 1.084400 |
| 8 | 0.177538 | 0.156386 | 0.171073 | 0.158305 | +1.227% | -3.641% | 1.080654 |
| 16 | 0.191154 | 0.198770 | 0.189282 | 0.187634 | -5.602% | -0.979% | 1.008783 |
| 32 | 0.219602 | 0.222435 | 0.219794 | 0.213634 | -3.957% | +0.087% | 1.028834 |
| 64 | 0.228482 | 0.243602 | 0.234178 | 0.243410 | -0.079% | +2.493% | 0.962072 |
| 128 | 0.257842 | 0.250066 | 0.247331 | 0.249938 | -0.051% | -4.077% | 0.989569 |
| 256 | 0.261491 | 0.257570 | 0.260177 | 0.254786 | -1.081% | -0.503% | 1.021159 |
| 512 | 0.256355 | 0.252083 | 0.251266 | 0.258323 | +2.475% | -1.985% | 0.972681 |
| 1024 | 0.273970 | 0.277282 | 0.267859 | 0.276850 | -0.156% | -2.231% | 0.967524 |
| 2048 | 0.365924 | 0.353187 | 0.359971 | 0.350372 | -0.797% | -1.627% | 1.027397 |
| 4096 | 0.571044 | 0.531589 | 0.570613 | 0.517988 | -2.559% | -0.075% | 1.101595 |

Mega candidate/baseline geometric mean: 1.000144; 9/13 lower latencies. All 104 explicit CONTROL configs and requested knobs match. Split selections change for 49/104 rank-shape pairs.

Local bytes: {'cu132-recovery0909a-modern5wg-full13-001': [0], 'cu132-recovery0909a-scale-u16-control13-001': [0]}. Baseline phase wall includes its first native build; candidate reuses that native cache. Wall times therefore do not measure a kernel speedup.
