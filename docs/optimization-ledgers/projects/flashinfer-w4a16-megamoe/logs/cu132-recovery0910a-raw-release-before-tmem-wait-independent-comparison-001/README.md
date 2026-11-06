# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole retained3efa run. Owned098c remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_retained3efa

BEFORE: `cu132-recovery0910a-fc1-empty-bulk-drain-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.995757891 (-0.424211%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.999655749 (-0.034425%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.077824 | 0.083585 | +7.403% | N64/F4/epi | N64/F4/epi |
| 2 | 0.110304 | 0.106496 | -3.452% | N64/F8/epi | N64/F4/epi |
| 4 | 0.128177 | 0.128402 | +0.176% | N64/F4/epi | N64/F8/epi |
| 8 | 0.139073 | 0.143041 | +2.853% | N64/F4/epi | N64/F8/epi |
| 16 | 0.161169 | 0.159826 | -0.833% | N64/F4/epi | N64/F4/epi |
| 32 | 0.186849 | 0.179026 | -4.187% | N64/F4/epi | N64/F4/epi |
| 64 | 0.206082 | 0.211234 | +2.500% | N64/F8/epi | N64/F4/epi |
| 128 | 0.210018 | 0.212834 | +1.341% | N64/F8/epi | N64/F8/epi |
| 256 | 0.215186 | 0.207505 | -3.569% | N64/F8/epi | N64/F4/epi |
| 512 | 0.220338 | 0.217538 | -1.271% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.240387 | 0.238434 | -0.812% | N64/F8/epi | N64/F8/epi |
| 2048 | 0.323602 | 0.320339 | -1.008% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.473988 | 0.478709 | +0.996% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.015322732 (+1.532273%); 4/10 lower, 6 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.019603181 (+1.960318%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.083585 | -5.104% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.106496 | +9.006% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.128402 | +6.873% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.143041 | +0.134% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.159826 | +6.482% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.179026 | -0.692% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.211234 | +3.036% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.212834 | -0.997% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.207505 | +0.418% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.217538 | +7.368% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.238434 | +3.934% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.332499 | 0.320339 | -3.657% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.478709 | -0.160% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
