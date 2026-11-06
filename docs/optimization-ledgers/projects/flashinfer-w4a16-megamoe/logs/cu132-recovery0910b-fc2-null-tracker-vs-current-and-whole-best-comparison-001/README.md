# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole fresh0910b-retained3b425 run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_fresh0910b-retained3b425

BEFORE: `cu132-recovery0910b-retained-ceb619-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.018925375 (+1.892538%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.019708107 (+1.970811%); 4/13 lower, 9 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.074801 | 0.084593 | +13.091% | N64/F8/epi | N64/F8/epi |
| 2 | 0.104865 | 0.102577 | -2.182% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120929 | 0.116801 | -3.414% | N64/F8/epi | N64/F8/epi |
| 8 | 0.136609 | 0.139425 | +2.061% | N64/F4/epi | N64/F8/epi |
| 16 | 0.149201 | 0.154704 | +3.688% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178001 | 0.182529 | +2.544% | N64/F8/epi | N64/F4/epi |
| 64 | 0.206034 | 0.202577 | -1.678% | N64/F8/epi | N64/F4/epi |
| 128 | 0.197795 | 0.208833 | +5.581% | N64/F4/epi | N64/F8/epi |
| 256 | 0.202737 | 0.207074 | +2.139% | N64/F4/epi | N64/F4/epi |
| 512 | 0.211250 | 0.211042 | -0.098% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.229361 | 0.233475 | +1.794% | N64/F8/epi | N64/F8/epi |
| 2048 | 0.305346 | 0.308913 | +1.168% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.458195 | 0.466884 | +1.896% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.993789093 (-0.621091%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.993697414 (-0.630259%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.084593 | -3.960% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.102577 | +4.995% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120145 | 0.116801 | -2.783% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.139425 | -2.398% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.154704 | +3.069% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.182529 | +1.251% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.202577 | -1.187% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.208833 | -2.858% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.207074 | +0.209% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.211042 | +4.162% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.233475 | +1.772% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.332499 | 0.308913 | -7.094% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.466884 | -2.627% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
