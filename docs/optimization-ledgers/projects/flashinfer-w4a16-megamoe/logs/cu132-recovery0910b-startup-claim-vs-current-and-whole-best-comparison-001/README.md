# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-retained-ceb619-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.027683347 (+2.768335%); 1/10 lower, 9 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.025531146 (+2.553115%); 2/13 lower, 11 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.074801 | 0.077824 | +4.041% | N64/F8/epi | N64/F8/epi |
| 2 | 0.104865 | 0.106993 | +2.029% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120929 | 0.120321 | -0.503% | N64/F8/epi | N64/F8/epi |
| 8 | 0.136609 | 0.147218 | +7.766% | N64/F4/epi | N64/F4/epi |
| 16 | 0.149201 | 0.154770 | +3.733% | N64/F4/epi | N64/F8/epi |
| 32 | 0.178001 | 0.178545 | +0.306% | N64/F8/epi | N64/F8/epi |
| 64 | 0.206034 | 0.201154 | -2.369% | N64/F8/epi | N64/F8/epi |
| 128 | 0.197795 | 0.205379 | +3.834% | N64/F4/epi | N64/F4/epi |
| 256 | 0.202737 | 0.206930 | +2.068% | N64/F4/epi | N64/F8/epi |
| 512 | 0.211250 | 0.225329 | +6.665% | N64/F4/epi | N64/F8/epi |
| 1024 | 0.229361 | 0.234306 | +2.156% | N64/F8/epi | N64/F4/epi |
| 2048 | 0.305346 | 0.309971 | +1.515% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.458195 | 0.469124 | +2.385% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.002331011 (+0.233101%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.999371920 (-0.062808%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.077824 | -11.645% | N64/F8/epi | N64/F8/epi |
| 2 | 0.097697 | 0.106993 | +9.515% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.120321 | +0.146% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.147218 | +3.058% | N64/F4/epi | N64/F4/epi |
| 16 | 0.150097 | 0.154770 | +3.113% | N64/F8/epi | N64/F8/epi |
| 32 | 0.180274 | 0.178545 | -0.959% | N64/F4/epi | N64/F8/epi |
| 64 | 0.205010 | 0.201154 | -1.881% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.205379 | -4.465% | N64/F4/epi | N64/F4/epi |
| 256 | 0.206642 | 0.206930 | +0.139% | N64/F4/epi | N64/F8/epi |
| 512 | 0.202609 | 0.225329 | +11.214% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.229410 | 0.234306 | +2.134% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.309971 | -6.775% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.469124 | -2.159% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
