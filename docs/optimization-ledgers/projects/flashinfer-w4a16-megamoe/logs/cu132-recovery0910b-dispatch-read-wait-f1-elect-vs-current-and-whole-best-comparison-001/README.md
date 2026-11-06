# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.016282118 (+1.628212%); 3/10 lower, 7 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.005620427 (+0.562043%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.089345 | +4.767% | N64/F8/epi | N64/F8/epi |
| 2 | 0.103248 | 0.094497 | -8.476% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.112913 | -4.558% | N64/F8/epi | N64/F4/epi |
| 8 | 0.131282 | 0.139857 | +6.532% | N64/F4/epi | N64/F4/epi |
| 16 | 0.153249 | 0.163409 | +6.630% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178897 | 0.179905 | +0.563% | N64/F8/epi | N64/F4/epi |
| 64 | 0.195425 | 0.199122 | +1.892% | N64/F8/epi | N64/F8/epi |
| 128 | 0.208945 | 0.208130 | -0.390% | N64/F4/epi | N64/F8/epi |
| 256 | 0.204210 | 0.205202 | +0.486% | N64/F8/epi | N64/F8/epi |
| 512 | 0.210161 | 0.210145 | -0.008% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.233553 | 0.233569 | +0.007% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.313282 | 0.311586 | -0.541% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.464914 | 0.471555 | +1.428% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.996616880 (-0.338312%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.991190981 (-0.880902%); 9/13 lower, 4 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.089345 | +1.435% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.094497 | -3.275% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.112913 | -6.019% | N64/F4/epi | N64/F4/epi |
| 8 | 0.142850 | 0.139857 | -2.095% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.163409 | +8.869% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.179905 | -0.205% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.199122 | -2.872% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.208130 | -3.185% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.205202 | -0.697% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.210145 | +3.719% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.233569 | +1.813% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.311586 | -6.290% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.471555 | -1.652% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
