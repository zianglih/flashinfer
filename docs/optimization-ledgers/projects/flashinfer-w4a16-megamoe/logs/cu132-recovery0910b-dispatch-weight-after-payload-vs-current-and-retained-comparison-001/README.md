# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-dispatch-pull-barriers-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.000697333 (+0.069733%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.992282551 (-0.771745%); 9/13 lower, 4 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.086753 | 0.083696 | -3.524% | N64/F4/epi | N128/F4/epi |
| 2 | 0.106977 | 0.100593 | -5.968% | N64/F4/epi | N64/F4/epi |
| 4 | 0.117409 | 0.116208 | -1.023% | N64/F8/epi | N64/F8/epi |
| 8 | 0.139473 | 0.137330 | -1.536% | N64/F4/epi | N64/F4/epi |
| 16 | 0.146385 | 0.154786 | +5.739% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178866 | 0.178978 | +0.063% | N64/F8/epi | N64/F8/epi |
| 64 | 0.201921 | 0.200786 | -0.562% | N64/F8/epi | N64/F4/epi |
| 128 | 0.207921 | 0.205953 | -0.947% | N64/F4/epi | N64/F4/epi |
| 256 | 0.209105 | 0.204433 | -2.234% | N64/F8/epi | N64/F8/epi |
| 512 | 0.211026 | 0.209154 | -0.887% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.225778 | 0.232273 | +2.877% | N64/F8/epi | N64/F4/epi |
| 2048 | 0.313010 | 0.313060 | +0.016% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.469380 | 0.462003 | -1.572% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.005204892 (+0.520489%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.999171853 (-0.082815%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.083696 | -1.857% | N64/F8/epi | N128/F4/epi |
| 2 | 0.103248 | 0.100593 | -2.571% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.116208 | -1.773% | N64/F8/epi | N64/F8/epi |
| 8 | 0.131282 | 0.137330 | +4.607% | N64/F4/epi | N64/F4/epi |
| 16 | 0.153249 | 0.154786 | +1.003% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178897 | 0.178978 | +0.045% | N64/F8/epi | N64/F8/epi |
| 64 | 0.195425 | 0.200786 | +2.743% | N64/F8/epi | N64/F4/epi |
| 128 | 0.208945 | 0.205953 | -1.432% | N64/F4/epi | N64/F4/epi |
| 256 | 0.204210 | 0.204433 | +0.109% | N64/F8/epi | N64/F8/epi |
| 512 | 0.210161 | 0.209154 | -0.479% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.233553 | 0.232273 | -0.548% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.313282 | 0.313060 | -0.071% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.464914 | 0.462003 | -0.626% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
