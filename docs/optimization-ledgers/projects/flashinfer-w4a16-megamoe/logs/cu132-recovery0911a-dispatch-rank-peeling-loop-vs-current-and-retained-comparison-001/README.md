# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0911a-dispatch-total-bound-no-exhaustion-checks-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.993784842 (-0.621516%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.994339930 (-0.566007%); 9/13 lower, 4 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.084960 | 0.076080 | -10.452% | N64/F8/epi | N64/F4/epi |
| 2 | 0.107825 | 0.102849 | -4.615% | N64/F4/epi | N64/F4/epi |
| 4 | 0.112002 | 0.129634 | +15.743% | N64/F8/epi | N64/F4/epi |
| 8 | 0.139842 | 0.139922 | +0.057% | N64/F8/epi | N64/F8/epi |
| 16 | 0.154881 | 0.151810 | -1.983% | N64/F8/epi | N64/F8/epi |
| 32 | 0.173713 | 0.173473 | -0.138% | N64/F8/epi | N64/F4/epi |
| 64 | 0.192673 | 0.202353 | +5.024% | N64/F8/epi | N64/F8/epi |
| 128 | 0.205633 | 0.201394 | -2.061% | N64/F4/epi | N64/F4/epi |
| 256 | 0.222946 | 0.207394 | -6.976% | N64/F8/epi | N64/F4/epi |
| 512 | 0.208913 | 0.212338 | +1.639% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.232449 | 0.231506 | -0.406% | N64/F8/epi | N64/F4/epi |
| 2048 | 0.312514 | 0.311057 | -0.466% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.473363 | 0.471044 | -0.490% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0911a-retained61ee-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.991448588 (-0.855141%); 7/10 lower, 3 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.003289229 (+0.328923%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073505 | 0.076080 | +3.503% | N64/F4/epi | N64/F4/epi |
| 2 | 0.103809 | 0.102849 | -0.925% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116896 | 0.129634 | +10.897% | N64/F8/epi | N64/F4/epi |
| 8 | 0.140624 | 0.139922 | -0.499% | N64/F8/epi | N64/F8/epi |
| 16 | 0.155264 | 0.151810 | -2.225% | N64/F8/epi | N64/F8/epi |
| 32 | 0.178401 | 0.173473 | -2.762% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203889 | 0.202353 | -0.753% | N64/F4/epi | N64/F8/epi |
| 128 | 0.206945 | 0.201394 | -2.682% | N64/F4/epi | N64/F4/epi |
| 256 | 0.209217 | 0.207394 | -0.871% | N64/F4/epi | N64/F4/epi |
| 512 | 0.209874 | 0.212338 | +1.174% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.232737 | 0.231506 | -0.529% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.310850 | 0.311057 | +0.067% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.468179 | 0.471044 | +0.612% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
