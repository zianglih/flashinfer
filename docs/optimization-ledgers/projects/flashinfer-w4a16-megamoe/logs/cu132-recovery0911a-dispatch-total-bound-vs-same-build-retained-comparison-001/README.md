# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the fresh complete retained61ee run on the same rebuilt support binaries. This measures the combined transport chain against retained61ee, not the isolated total-bound change. The second control is historical61ee on the earlier support build and is not an admission control. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_build_retained61ee

BEFORE: `cu132-recovery0911a-retained61ee-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.987880578 (-1.211942%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.000211771 (+0.021177%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.073505 | 0.080033 | +8.881% | N64/F4/epi | N64/F8/epi |
| 2 | 0.103809 | 0.104304 | +0.477% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116896 | 0.121041 | +3.546% | N64/F8/epi | N64/F8/epi |
| 8 | 0.140624 | 0.134113 | -4.630% | N64/F8/epi | N64/F4/epi |
| 16 | 0.155264 | 0.147377 | -5.080% | N64/F8/epi | N64/F8/epi |
| 32 | 0.178401 | 0.171698 | -3.757% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203889 | 0.203169 | -0.353% | N64/F4/epi | N64/F4/epi |
| 128 | 0.206945 | 0.218482 | +5.575% | N64/F4/epi | N64/F4/epi |
| 256 | 0.209217 | 0.204722 | -2.148% | N64/F4/epi | N64/F8/epi |
| 512 | 0.209874 | 0.204977 | -2.333% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.232737 | 0.232913 | +0.076% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.310850 | 0.312053 | +0.387% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468179 | 0.470949 | +0.592% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## historical_previous_build_61ee

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.000844002 (+0.084400%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.998307180 (-0.169282%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.080033 | -6.153% | N64/F8/epi | N64/F8/epi |
| 2 | 0.103248 | 0.104304 | +1.023% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.121041 | +2.313% | N64/F8/epi | N64/F8/epi |
| 8 | 0.131282 | 0.134113 | +2.156% | N64/F4/epi | N64/F4/epi |
| 16 | 0.153249 | 0.147377 | -3.832% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178897 | 0.171698 | -4.024% | N64/F8/epi | N64/F4/epi |
| 64 | 0.195425 | 0.203169 | +3.963% | N64/F8/epi | N64/F4/epi |
| 128 | 0.208945 | 0.218482 | +4.564% | N64/F4/epi | N64/F4/epi |
| 256 | 0.204210 | 0.204722 | +0.251% | N64/F8/epi | N64/F8/epi |
| 512 | 0.210161 | 0.204977 | -2.467% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.233553 | 0.232913 | -0.274% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.313282 | 0.312053 | -0.392% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.464914 | 0.470949 | +1.298% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
