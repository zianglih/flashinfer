# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0911a-dispatch-total-bound-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.009888399 (+0.988840%); 3/10 lower, 7 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.008786610 (+0.878661%); 4/13 lower, 9 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.080033 | 0.084960 | +6.156% | N64/F8/epi | N64/F8/epi |
| 2 | 0.104304 | 0.107825 | +3.376% | N64/F4/epi | N64/F4/epi |
| 4 | 0.121041 | 0.112002 | -7.468% | N64/F8/epi | N64/F8/epi |
| 8 | 0.134113 | 0.139842 | +4.272% | N64/F4/epi | N64/F8/epi |
| 16 | 0.147377 | 0.154881 | +5.092% | N64/F8/epi | N64/F8/epi |
| 32 | 0.171698 | 0.173713 | +1.174% | N64/F4/epi | N64/F8/epi |
| 64 | 0.203169 | 0.192673 | -5.166% | N64/F4/epi | N64/F8/epi |
| 128 | 0.218482 | 0.205633 | -5.881% | N64/F4/epi | N64/F4/epi |
| 256 | 0.204722 | 0.222946 | +8.902% | N64/F8/epi | N64/F8/epi |
| 512 | 0.204977 | 0.208913 | +1.920% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.232913 | 0.232449 | -0.199% | N64/F8/epi | N64/F8/epi |
| 2048 | 0.312053 | 0.312514 | +0.148% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.470949 | 0.473363 | +0.513% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0911a-retained61ee-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.997649135 (-0.235087%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.009000241 (+0.900024%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073505 | 0.084960 | +15.584% | N64/F4/epi | N64/F8/epi |
| 2 | 0.103809 | 0.107825 | +3.869% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116896 | 0.112002 | -4.187% | N64/F8/epi | N64/F8/epi |
| 8 | 0.140624 | 0.139842 | -0.556% | N64/F8/epi | N64/F8/epi |
| 16 | 0.155264 | 0.154881 | -0.247% | N64/F8/epi | N64/F8/epi |
| 32 | 0.178401 | 0.173713 | -2.628% | N64/F4/epi | N64/F8/epi |
| 64 | 0.203889 | 0.192673 | -5.501% | N64/F4/epi | N64/F8/epi |
| 128 | 0.206945 | 0.205633 | -0.634% | N64/F4/epi | N64/F4/epi |
| 256 | 0.209217 | 0.222946 | +6.562% | N64/F4/epi | N64/F8/epi |
| 512 | 0.209874 | 0.208913 | -0.458% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.232737 | 0.232449 | -0.124% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.310850 | 0.312514 | +0.535% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468179 | 0.473363 | +1.107% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
