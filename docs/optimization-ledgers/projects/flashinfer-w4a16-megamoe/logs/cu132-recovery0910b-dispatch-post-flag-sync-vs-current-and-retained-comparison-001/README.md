# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete selected primary experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-dispatch-weight-after-payload-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.008630315 (+0.863031%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.011897820 (+1.189782%); 3/13 lower, 10 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.083696 | 0.087777 | +4.876% | N128/F4/epi | N64/F8/epi |
| 2 | 0.100593 | 0.099456 | -1.130% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116208 | 0.119937 | +3.209% | N64/F8/epi | N64/F4/epi |
| 8 | 0.137330 | 0.136610 | -0.524% | N64/F4/epi | N64/F8/epi |
| 16 | 0.154786 | 0.154288 | -0.322% | N64/F8/epi | N64/F4/epi |
| 32 | 0.178978 | 0.179585 | +0.339% | N64/F8/epi | N64/F8/epi |
| 64 | 0.200786 | 0.204529 | +1.864% | N64/F4/epi | N64/F4/epi |
| 128 | 0.205953 | 0.208339 | +1.159% | N64/F4/epi | N64/F8/epi |
| 256 | 0.204433 | 0.207905 | +1.698% | N64/F8/epi | N64/F4/epi |
| 512 | 0.209154 | 0.211073 | +0.918% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.232273 | 0.232786 | +0.221% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.313060 | 0.314002 | +0.301% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.462003 | 0.476003 | +3.030% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.013880127 (+1.388013%); 2/10 lower, 8 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.011059820 (+1.105982%); 3/13 lower, 10 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.087777 | +2.928% | N64/F8/epi | N64/F8/epi |
| 2 | 0.103248 | 0.099456 | -3.673% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.119937 | +1.379% | N64/F8/epi | N64/F4/epi |
| 8 | 0.131282 | 0.136610 | +4.058% | N64/F4/epi | N64/F8/epi |
| 16 | 0.153249 | 0.154288 | +0.678% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178897 | 0.179585 | +0.385% | N64/F8/epi | N64/F8/epi |
| 64 | 0.195425 | 0.204529 | +4.659% | N64/F8/epi | N64/F4/epi |
| 128 | 0.208945 | 0.208339 | -0.290% | N64/F4/epi | N64/F8/epi |
| 256 | 0.204210 | 0.207905 | +1.809% | N64/F8/epi | N64/F4/epi |
| 512 | 0.210161 | 0.211073 | +0.434% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.233553 | 0.232786 | -0.328% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.313282 | 0.314002 | +0.230% | N128/F8/reuse | N128/F4/reuse |
| 4096 | 0.464914 | 0.476003 | +2.385% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
