# BAR1 whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole default57e2 run. Owned098c remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_default57e2

BEFORE: `cu132-recovery0909e-central-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.005730895 (+0.573089%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.990699947 (-0.930005%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | BAR1 ms | Change | BEFORE tactic | BAR1 tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.095521 | 0.085921 | -10.050% | N64/F4/epi | N64/F8/epi |
| 2 | 0.114609 | 0.104849 | -8.516% | N64/F4/epi | N64/F8/epi |
| 4 | 0.116753 | 0.118673 | +1.644% | N64/F8/epi | N64/F4/epi |
| 8 | 0.140369 | 0.139458 | -0.649% | N64/F8/epi | N64/F8/epi |
| 16 | 0.153313 | 0.159009 | +3.715% | N64/F8/epi | N64/F8/epi |
| 32 | 0.185074 | 0.187890 | +1.522% | N64/F8/epi | N64/F4/epi |
| 64 | 0.210722 | 0.210593 | -0.061% | N64/F4/epi | N64/F8/epi |
| 128 | 0.208066 | 0.206770 | -0.623% | N64/F4/epi | N64/F4/epi |
| 256 | 0.218787 | 0.219842 | +0.482% | N64/F4/epi | N64/F4/epi |
| 512 | 0.218546 | 0.218194 | -0.161% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.237154 | 0.239090 | +0.816% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.322643 | 0.321427 | -0.377% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.470949 | 0.476341 | +1.145% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.020190880 (+2.019088%); 4/10 lower, 6 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.018115337 (+1.811534%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | BAR1 ms | Change | BEFORE tactic | BAR1 tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.085921 | -2.452% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.104849 | +7.321% | N64/F4/epi | N64/F8/epi |
| 4 | 0.120145 | 0.118673 | -1.225% | N64/F4/epi | N64/F4/epi |
| 8 | 0.142850 | 0.139458 | -2.375% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.159009 | +5.937% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.187890 | +4.225% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.210593 | +2.723% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.206770 | -3.818% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.219842 | +6.388% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.218194 | +7.692% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.239090 | +4.220% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.332499 | 0.321427 | -3.330% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.476341 | -0.654% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
