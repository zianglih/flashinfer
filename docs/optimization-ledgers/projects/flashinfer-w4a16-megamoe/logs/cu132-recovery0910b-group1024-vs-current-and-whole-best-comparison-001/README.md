# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE uses G512 throughout; this candidate uses G1024 throughout. N/F/return selectors can match while complete tactics differ. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-retained-ceb619-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.019052481 (+1.905248%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.032222863 (+3.222286%); 3/13 lower, 10 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.074801 | 0.090497 | +20.984% | N64/F8/G512/epi | N64/F4/G1024/epi |
| 2 | 0.104865 | 0.109712 | +4.622% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 4 | 0.120929 | 0.119473 | -1.204% | N64/F8/G512/epi | N64/F8/G1024/epi |
| 8 | 0.136609 | 0.140289 | +2.694% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 16 | 0.149201 | 0.160625 | +7.657% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 32 | 0.178001 | 0.177041 | -0.539% | N64/F8/G512/epi | N64/F4/G1024/epi |
| 64 | 0.206034 | 0.198001 | -3.899% | N64/F8/G512/epi | N64/F8/G1024/epi |
| 128 | 0.197795 | 0.209329 | +5.831% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 256 | 0.202737 | 0.210034 | +3.599% | N64/F4/G512/epi | N64/F4/G1024/epi |
| 512 | 0.211250 | 0.211682 | +0.204% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 1024 | 0.229361 | 0.233138 | +1.647% | N64/F8/G512/epi | N64/F8/G1024/epi |
| 2048 | 0.305346 | 0.312449 | +2.326% | N128/F8/G512/reuse | N128/F4/G1024/reuse |
| 4096 | 0.458195 | 0.458260 | +0.014% | N128/F4/G512/reuse | N128/F4/G1024/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.993913063 (-0.608694%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.005892944 (+0.589294%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.090497 | +2.743% | N64/F8/G512/epi | N64/F4/G1024/epi |
| 2 | 0.097697 | 0.109712 | +12.298% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 4 | 0.120145 | 0.119473 | -0.559% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 8 | 0.142850 | 0.140289 | -1.793% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 16 | 0.150097 | 0.160625 | +7.014% | N64/F8/G512/epi | N64/F8/G1024/epi |
| 32 | 0.180274 | 0.177041 | -1.793% | N64/F4/G512/epi | N64/F4/G1024/epi |
| 64 | 0.205010 | 0.198001 | -3.419% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 128 | 0.214977 | 0.209329 | -2.627% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 256 | 0.206642 | 0.210034 | +1.641% | N64/F4/G512/epi | N64/F4/G1024/epi |
| 512 | 0.202609 | 0.211682 | +4.478% | N64/F8/G512/epi | N64/F8/G1024/epi |
| 1024 | 0.229410 | 0.233138 | +1.625% | N64/F4/G512/epi | N64/F8/G1024/epi |
| 2048 | 0.332499 | 0.312449 | -6.030% | N128/F4/G512/reuse | N128/F4/G1024/reuse |
| 4096 | 0.479478 | 0.458260 | -4.425% | N128/F4/G512/reuse | N128/F4/G1024/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
