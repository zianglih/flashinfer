# Tail fence reorder whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole default57e2 run. Owned098c remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_default57e2

BEFORE: `cu132-recovery0909e-central-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.020230299 (+2.023030%); 1/10 lower, 9 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.029377801 (+2.937780%); 2/13 lower, 11 higher, 0 ties.

| Tokens | BEFORE ms | Tail fence reorder ms | Change | BEFORE tactic | Tail fence reorder tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.095521 | 0.094625 | -0.938% | N64/F4/epi | N64/F8/epi |
| 2 | 0.114609 | 0.118994 | +3.826% | N64/F4/epi | N64/F8/epi |
| 4 | 0.116753 | 0.135377 | +15.952% | N64/F8/epi | N64/F8/epi |
| 8 | 0.140369 | 0.151649 | +8.036% | N64/F8/epi | N64/F4/epi |
| 16 | 0.153313 | 0.154145 | +0.543% | N64/F8/epi | N64/F4/epi |
| 32 | 0.185074 | 0.190082 | +2.706% | N64/F8/epi | N64/F4/epi |
| 64 | 0.210722 | 0.212115 | +0.661% | N64/F4/epi | N64/F8/epi |
| 128 | 0.208066 | 0.212530 | +2.145% | N64/F4/epi | N64/F4/epi |
| 256 | 0.218787 | 0.220418 | +0.745% | N64/F4/epi | N64/F8/epi |
| 512 | 0.218546 | 0.223266 | +2.160% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.237154 | 0.240098 | +1.241% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.322643 | 0.322018 | -0.194% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.470949 | 0.482325 | +2.416% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.034898750 (+3.489875%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.057863514 (+5.786351%); 2/13 lower, 11 higher, 0 ties.

| Tokens | BEFORE ms | Tail fence reorder ms | Change | BEFORE tactic | Tail fence reorder tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.094625 | +7.430% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.118994 | +21.799% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120145 | 0.135377 | +12.678% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.151649 | +6.160% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.154145 | +2.697% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.190082 | +5.441% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.212115 | +3.466% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.212530 | -1.138% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.220418 | +6.667% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.223266 | +10.195% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.240098 | +4.659% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.322018 | -3.152% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.482325 | +0.594% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
