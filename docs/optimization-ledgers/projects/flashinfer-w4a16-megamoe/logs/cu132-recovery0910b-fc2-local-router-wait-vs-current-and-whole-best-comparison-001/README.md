# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-retained641-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.985648266 (-1.435173%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.991224127 (-0.877587%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073713 | 0.085280 | +15.692% | N64/F4/epi | N64/F8/epi |
| 2 | 0.118865 | 0.103248 | -13.138% | N64/F4/epi | N64/F8/epi |
| 4 | 0.115377 | 0.118305 | +2.538% | N64/F8/epi | N64/F8/epi |
| 8 | 0.140321 | 0.131282 | -6.442% | N64/F8/epi | N64/F4/epi |
| 16 | 0.155425 | 0.153249 | -1.400% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178642 | 0.178897 | +0.143% | N64/F4/epi | N64/F8/epi |
| 64 | 0.204705 | 0.195425 | -4.533% | N64/F8/epi | N64/F8/epi |
| 128 | 0.207393 | 0.208945 | +0.748% | N64/F8/epi | N64/F4/epi |
| 256 | 0.207809 | 0.204210 | -1.732% | N64/F4/epi | N64/F8/epi |
| 512 | 0.211249 | 0.210161 | -0.515% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.233442 | 0.233553 | +0.048% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.312547 | 0.313282 | +0.235% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.467970 | 0.464914 | -0.653% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.980649824 (-1.935018%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.985651201 (-1.434880%); 9/13 lower, 4 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.085280 | -3.180% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.103248 | +5.682% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120145 | 0.118305 | -1.531% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.131282 | -8.098% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.153249 | +2.100% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.178897 | -0.764% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 0.195425 | -4.675% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.208945 | -2.806% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.204210 | -1.177% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.210161 | +3.727% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.233553 | +1.806% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.313282 | -5.780% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.479478 | 0.464914 | -3.037% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
