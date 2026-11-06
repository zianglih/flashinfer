# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole default57e2 run. Owned098c remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_default57e2

BEFORE: `cu132-recovery0909e-central-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.005195898 (+0.519590%); 3/10 lower, 7 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.992489392 (-0.751061%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.095521 | 0.077824 | -18.527% | N64/F4/epi | N64/F4/epi |
| 2 | 0.114609 | 0.110304 | -3.756% | N64/F4/epi | N64/F8/epi |
| 4 | 0.116753 | 0.128177 | +9.785% | N64/F8/epi | N64/F4/epi |
| 8 | 0.140369 | 0.139073 | -0.923% | N64/F8/epi | N64/F4/epi |
| 16 | 0.153313 | 0.161169 | +5.124% | N64/F8/epi | N64/F4/epi |
| 32 | 0.185074 | 0.186849 | +0.959% | N64/F8/epi | N64/F4/epi |
| 64 | 0.210722 | 0.206082 | -2.202% | N64/F4/epi | N64/F8/epi |
| 128 | 0.208066 | 0.210018 | +0.938% | N64/F4/epi | N64/F8/epi |
| 256 | 0.218787 | 0.215186 | -1.646% | N64/F4/epi | N64/F8/epi |
| 512 | 0.218546 | 0.220338 | +0.820% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.237154 | 0.240387 | +1.363% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.322643 | 0.323602 | +0.297% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.470949 | 0.473988 | +0.645% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.019648191 (+1.964819%); 4/10 lower, 6 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.019954301 (+1.995430%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.077824 | -11.645% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.110304 | +12.904% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120145 | 0.128177 | +6.685% | N64/F4/epi | N64/F4/epi |
| 8 | 0.142850 | 0.139073 | -2.644% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.161169 | +7.377% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.186849 | +3.647% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.206082 | +0.523% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.210018 | -2.307% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.215186 | +4.135% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.220338 | +8.750% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.240387 | +4.785% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.332499 | 0.323602 | -2.676% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.473988 | -1.145% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
