# Atomic preclaim whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole default57e2 run. Owned098c remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_default57e2

BEFORE: `cu132-recovery0909e-central-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.023796252 (+2.379625%); 3/10 lower, 7 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.012972378 (+1.297238%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Atomic preclaim ms | Change | BEFORE tactic | Atomic preclaim tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.095521 | 0.087809 | -8.074% | N64/F4/epi | N128/F4/epi |
| 2 | 0.114609 | 0.105649 | -7.818% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116753 | 0.128770 | +10.293% | N64/F8/epi | N64/F4/epi |
| 8 | 0.140369 | 0.148594 | +5.860% | N64/F8/epi | N64/F8/epi |
| 16 | 0.153313 | 0.173314 | +13.046% | N64/F8/epi | N64/F8/epi |
| 32 | 0.185074 | 0.184546 | -0.285% | N64/F8/epi | N64/F4/epi |
| 64 | 0.210722 | 0.213090 | +1.124% | N64/F4/epi | N64/F4/epi |
| 128 | 0.208066 | 0.213523 | +2.623% | N64/F4/epi | N64/F8/epi |
| 256 | 0.218787 | 0.214850 | -1.799% | N64/F4/epi | N64/F8/epi |
| 512 | 0.218546 | 0.222195 | +1.670% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.237154 | 0.237123 | -0.013% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.322643 | 0.323587 | +0.293% | N128/F8/reuse | N128/F8/reuse |
| 4096 | 0.470949 | 0.480564 | +2.042% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.038515974 (+3.851597%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.041004108 (+4.100411%); 3/13 lower, 10 higher, 0 ties.

| Tokens | BEFORE ms | Atomic preclaim ms | Change | BEFORE tactic | Atomic preclaim tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.087809 | -0.309% | N64/F8/epi | N128/F4/epi |
| 2 | 0.097697 | 0.105649 | +8.139% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.128770 | +7.179% | N64/F4/epi | N64/F4/epi |
| 8 | 0.142850 | 0.148594 | +4.021% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.173314 | +15.468% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.184546 | +2.370% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.213090 | +3.941% | N64/F4/epi | N64/F4/epi |
| 128 | 0.214977 | 0.213523 | -0.676% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.214850 | +3.972% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.222195 | +9.667% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.237123 | +3.362% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.323587 | -2.680% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.479478 | 0.480564 | +0.226% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
