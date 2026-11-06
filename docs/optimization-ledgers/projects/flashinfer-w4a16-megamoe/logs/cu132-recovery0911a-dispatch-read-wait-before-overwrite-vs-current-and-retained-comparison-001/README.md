# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0911a-dispatch-rank-peeling-loop-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.004444942 (+0.444494%); 4/10 lower, 6 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.008788733 (+0.878873%); 5/13 lower, 8 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.076080 | 0.083985 | +10.390% | N64/F4/epi | N64/F4/epi |
| 2 | 0.102849 | 0.107809 | +4.823% | N64/F4/epi | N64/F4/epi |
| 4 | 0.129634 | 0.120081 | -7.369% | N64/F4/epi | N64/F8/epi |
| 8 | 0.139922 | 0.139105 | -0.584% | N64/F8/epi | N64/F8/epi |
| 16 | 0.151810 | 0.154641 | +1.865% | N64/F8/epi | N64/F4/epi |
| 32 | 0.173473 | 0.178753 | +3.044% | N64/F4/epi | N64/F8/epi |
| 64 | 0.202353 | 0.203041 | +0.340% | N64/F8/epi | N64/F8/epi |
| 128 | 0.201394 | 0.202945 | +0.770% | N64/F4/epi | N64/F8/epi |
| 256 | 0.207394 | 0.206385 | -0.487% | N64/F4/epi | N64/F8/epi |
| 512 | 0.212338 | 0.209938 | -1.130% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.231506 | 0.233377 | +0.808% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.311057 | 0.310098 | -0.308% | N128/F8/reuse | N128/F8/reuse |
| 4096 | 0.471044 | 0.471970 | +0.197% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0911a-retained61ee-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.995855519 (-0.414448%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.012106870 (+1.210687%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073505 | 0.083985 | +14.258% | N64/F4/epi | N64/F4/epi |
| 2 | 0.103809 | 0.107809 | +3.853% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116896 | 0.120081 | +2.725% | N64/F8/epi | N64/F8/epi |
| 8 | 0.140624 | 0.139105 | -1.080% | N64/F8/epi | N64/F8/epi |
| 16 | 0.155264 | 0.154641 | -0.401% | N64/F8/epi | N64/F4/epi |
| 32 | 0.178401 | 0.178753 | +0.197% | N64/F4/epi | N64/F8/epi |
| 64 | 0.203889 | 0.203041 | -0.416% | N64/F4/epi | N64/F8/epi |
| 128 | 0.206945 | 0.202945 | -1.933% | N64/F4/epi | N64/F8/epi |
| 256 | 0.209217 | 0.206385 | -1.354% | N64/F4/epi | N64/F8/epi |
| 512 | 0.209874 | 0.209938 | +0.030% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.232737 | 0.233377 | +0.275% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.310850 | 0.310098 | -0.242% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.468179 | 0.471970 | +0.810% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
