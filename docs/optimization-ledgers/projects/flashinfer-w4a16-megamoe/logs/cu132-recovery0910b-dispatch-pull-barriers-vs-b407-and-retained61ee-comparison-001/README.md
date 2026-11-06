# Candidate whole-run comparisons

Arithmetic on hash-pinned completed reconstructions only; no saved source, sample, resource, numerical, ranking or benchmark validators are rerun. The primary BEFORE is the complete unpromoted b407 experiment. The second control is complete retained61ee on the same hu-pdx-129 node for joint retention. It remains a separate whole-run comparison; neither control supplies replacement rows to the other. No row minima, timing rerun, scorer/selector/timer changes, or drift adjustment. Sequential historical invocations are not a paired measurement. Tokens are global source tokens distributed across 8 ranks.

## primary_same_host_before

BEFORE: `cu132-recovery0910b-dispatch-read-wait-f1-elect-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.988410993 (-1.158901%); 6/10 lower, 4 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.001315066 (+0.131507%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.089345 | 0.086753 | -2.901% | N64/F8/epi | N64/F4/epi |
| 2 | 0.094497 | 0.106977 | +13.207% | N64/F4/epi | N64/F4/epi |
| 4 | 0.112913 | 0.117409 | +3.982% | N64/F4/epi | N64/F8/epi |
| 8 | 0.139857 | 0.139473 | -0.275% | N64/F4/epi | N64/F4/epi |
| 16 | 0.163409 | 0.146385 | -10.418% | N64/F4/epi | N64/F4/epi |
| 32 | 0.179905 | 0.178866 | -0.578% | N64/F4/epi | N64/F8/epi |
| 64 | 0.199122 | 0.201921 | +1.406% | N64/F8/epi | N64/F8/epi |
| 128 | 0.208130 | 0.207921 | -0.100% | N64/F8/epi | N64/F4/epi |
| 256 | 0.205202 | 0.209105 | +1.902% | N64/F8/epi | N64/F8/epi |
| 512 | 0.210145 | 0.211026 | +0.419% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.233569 | 0.225778 | -3.336% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.311586 | 0.313010 | +0.457% | N128/F4/reuse | N128/F8/reuse |
| 4096 | 0.471555 | 0.469380 | -0.461% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.

## retained_same_host_61ee

BEFORE: `cu132-recovery0910b-fc2-local-router-wait-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 1.004504418 (+0.450442%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 1.006942884 (+0.694288%); 6/13 lower, 7 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.085280 | 0.086753 | +1.727% | N64/F8/epi | N64/F4/epi |
| 2 | 0.103248 | 0.106977 | +3.612% | N64/F8/epi | N64/F4/epi |
| 4 | 0.118305 | 0.117409 | -0.757% | N64/F8/epi | N64/F8/epi |
| 8 | 0.131282 | 0.139473 | +6.239% | N64/F4/epi | N64/F4/epi |
| 16 | 0.153249 | 0.146385 | -4.479% | N64/F4/epi | N64/F4/epi |
| 32 | 0.178897 | 0.178866 | -0.017% | N64/F8/epi | N64/F8/epi |
| 64 | 0.195425 | 0.201921 | +3.324% | N64/F8/epi | N64/F8/epi |
| 128 | 0.208945 | 0.207921 | -0.490% | N64/F4/epi | N64/F4/epi |
| 256 | 0.204210 | 0.209105 | +2.397% | N64/F8/epi | N64/F8/epi |
| 512 | 0.210161 | 0.211026 | +0.412% | N64/F8/epi | N64/F4/epi |
| 1024 | 0.233553 | 0.225778 | -3.329% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.313282 | 0.313010 | -0.087% | N128/F8/reuse | N128/F8/reuse |
| 4096 | 0.464914 | 0.469380 | +0.961% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
