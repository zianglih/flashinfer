# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-retained-ceb619-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.021695452 (+2.169545%); 1/10 lower, 9 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.026732359 (+2.673236%); 2/13 lower, 11 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.074801 | 0.087760 | +17.325% | N64/F8/epi | N64/F4/epi |
| 2 | 0.104865 | 0.108449 | +3.418% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120929 | 0.113312 | -6.299% | N64/F8/epi | N64/F8/epi |
| 8 | 0.136609 | 0.150594 | +10.237% | N64/F4/epi | N64/F4/epi |
| 16 | 0.149201 | 0.152417 | +2.155% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178001 | 0.178945 | +0.530% | N64/F8/epi | N64/F8/epi |
| 64 | 0.206034 | 0.203697 | -1.134% | N64/F8/epi | N64/F4/epi |
| 128 | 0.197795 | 0.202993 | +2.628% | N64/F4/epi | N64/F4/epi |
| 256 | 0.202737 | 0.205890 | +1.555% | N64/F4/epi | N64/F8/epi |
| 512 | 0.211250 | 0.211313 | +0.030% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.229361 | 0.232706 | +1.458% | N64/F8/epi | N64/F4/epi |
| 2048 | 0.305346 | 0.312289 | +2.274% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.458195 | 0.469010 | +2.360% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.996490834 (-0.350917%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.000542492 (+0.054249%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.087760 | -0.364% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.108449 | +11.005% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.113312 | -5.687% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.150594 | +5.421% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.152417 | +1.546% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.178945 | -0.737% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 0.203697 | -0.640% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.202993 | -5.575% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.205890 | -0.364% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.211313 | +4.296% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.232706 | +1.437% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.312289 | -6.078% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.469010 | -2.183% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
