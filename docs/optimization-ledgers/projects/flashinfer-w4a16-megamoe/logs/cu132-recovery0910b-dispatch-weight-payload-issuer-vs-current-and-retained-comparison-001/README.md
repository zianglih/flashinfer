# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-dispatch-post-flag-sync-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.987639024 (-1.236098%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.997983924 (-0.201608%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.087777 | 0.087473 | -0.346% | N64/F8/epi | N64/F4/epi |
| 2 | 0.099456 | 0.102785 | +3.347% | N64/F4/epi | N64/F4/epi |
| 4 | 0.119937 | 0.128465 | +7.110% | N64/F4/epi | N64/F4/epi |
| 8 | 0.136610 | 0.137425 | +0.597% | N64/F8/epi | N64/F4/epi |
| 16 | 0.154288 | 0.150531 | -2.435% | N64/F4/epi | N64/F4/epi |
| 32 | 0.179585 | 0.178369 | -0.677% | N64/F8/epi | N64/F8/epi |
| 64 | 0.204529 | 0.193250 | -5.515% | N64/F4/epi | N64/F8/epi |
| 128 | 0.208339 | 0.202161 | -2.965% | N64/F8/epi | N64/F4/epi |
| 256 | 0.207905 | 0.208225 | +0.154% | N64/F4/epi | N64/F4/epi |
| 512 | 0.211073 | 0.208705 | -1.122% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.232786 | 0.233602 | +0.351% | N64/F8/epi | N64/F8/epi |
| 2048 | 0.314002 | 0.312244 | -0.560% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.476003 | 0.475910 | -0.020% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.001347578 (+0.134758%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.009021446 (+0.902145%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.087473 | +2.572% | N64/F8/epi | N64/F4/epi |
| 2 | 0.103248 | 0.102785 | -0.448% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.128465 | +8.588% | N64/F8/epi | N64/F4/epi |
| 8 | 0.131282 | 0.137425 | +4.679% | N64/F4/epi | N64/F4/epi |
| 16 | 0.153249 | 0.150531 | -1.774% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178897 | 0.178369 | -0.295% | N64/F8/epi | N64/F8/epi |
| 64 | 0.195425 | 0.193250 | -1.113% | N64/F8/epi | N64/F8/epi |
| 128 | 0.208945 | 0.202161 | -3.247% | N64/F4/epi | N64/F4/epi |
| 256 | 0.204210 | 0.208225 | +1.966% | N64/F8/epi | N64/F4/epi |
| 512 | 0.210161 | 0.208705 | -0.693% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.233553 | 0.233602 | +0.021% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.313282 | 0.312244 | -0.331% | N128/F8/reuse | N128/F8/reuse |
| 4096 | 0.464914 | 0.475910 | +2.365% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
