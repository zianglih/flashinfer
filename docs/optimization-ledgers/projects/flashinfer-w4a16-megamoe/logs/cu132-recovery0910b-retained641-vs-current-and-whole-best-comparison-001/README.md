# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the whole selected same-host retained baseline run. Owned098c is a different-hardware historical reference, not the same-host admission control. It remains a separate whole-best comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-retained-ceb619-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.020093885 (+2.009389%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.020406234 (+2.040623%); 4/13 lower, 9 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.074801 | 0.073713 | -1.455% | N64/F8/epi | N64/F4/epi |
| 2 | 0.104865 | 0.118865 | +13.350% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120929 | 0.115377 | -4.591% | N64/F8/epi | N64/F8/epi |
| 8 | 0.136609 | 0.140321 | +2.717% | N64/F4/epi | N64/F8/epi |
| 16 | 0.149201 | 0.155425 | +4.172% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178001 | 0.178642 | +0.360% | N64/F8/epi | N64/F4/epi |
| 64 | 0.206034 | 0.204705 | -0.645% | N64/F8/epi | N64/F8/epi |
| 128 | 0.197795 | 0.207393 | +4.852% | N64/F4/epi | N64/F8/epi |
| 256 | 0.202737 | 0.207809 | +2.502% | N64/F4/epi | N64/F4/epi |
| 512 | 0.211250 | 0.211249 | -0.000% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.229361 | 0.233442 | +1.779% | N64/F8/epi | N64/F4/epi |
| 2048 | 0.305346 | 0.312547 | +2.358% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.458195 | 0.467970 | +2.133% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## separate_whole_best_owned098c

BEFORE: `cu132-recovery0909e-ownership-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.994928776 (-0.507122%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.994377733 (-0.562227%); 8/13 lower, 5 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.088081 | 0.073713 | -16.312% | N64/F8/epi | N64/F4/epi |
| 2 | 0.097697 | 0.118865 | +21.667% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120145 | 0.115377 | -3.969% | N64/F4/epi | N64/F8/epi |
| 8 | 0.142850 | 0.140321 | -1.770% | N64/F4/epi | N64/F8/epi |
| 16 | 0.150097 | 0.155425 | +3.550% | N64/F8/epi | N64/F4/epi |
| 32 | 0.180274 | 0.178642 | -0.905% | N64/F4/epi | N64/F4/epi |
| 64 | 0.205010 | 0.204705 | -0.149% | N64/F4/epi | N64/F8/epi |
| 128 | 0.214977 | 0.207393 | -3.528% | N64/F4/epi | N64/F8/epi |
| 256 | 0.206642 | 0.207809 | +0.565% | N64/F4/epi | N64/F4/epi |
| 512 | 0.202609 | 0.211249 | +4.264% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.229410 | 0.233442 | +1.758% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.332499 | 0.312547 | -6.001% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.479478 | 0.467970 | -2.400% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
