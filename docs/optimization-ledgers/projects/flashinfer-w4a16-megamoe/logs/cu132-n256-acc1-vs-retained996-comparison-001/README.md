# Candidate whole-run comparisons

Arithmetic on the completed whole N256 AUTO12 and retained996 AUTO8 runs on hu-pdx-15. All13 rows remain; tokens8–4096 determine retention. No row minima, historical-node substitution, drift adjustment, validator or timing rerun. N256 appends four tactics after the original eight. Timers, scorer, workload and eight-rank topology are unchanged.

## retained996

BEFORE: `cu132-retained996-default-auto13-direct-001`.

8–4096 retention: candidate/BEFORE GM 0.996040557 (-0.395944%); 5/10 lower, 5 higher, 0 ties.
All13 secondary: candidate/BEFORE GM 0.984657902 (-1.534210%); 7/13 lower, 6 higher, 0 ties.

| Tokens | BEFORE ms | Candidate ms | Change | BEFORE tactic | Candidate tactic |
|---:|---:|---:|---:|---|---|
| 1 | 0.087008 | 0.075168 | -13.608% | N128/F8/epi | N128/F4/epi |
| 2 | 0.104785 | 0.105200 | +0.396% | N64/F4/epi | N64/F4/epi |
| 4 | 0.118976 | 0.116737 | -1.882% | N64/F4/epi | N64/F8/epi |
| 8 | 0.134464 | 0.139248 | +3.558% | N64/F8/epi | N64/F8/epi |
| 16 | 0.154144 | 0.154145 | +0.001% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180001 | 0.189968 | +5.537% | N64/F4/epi | N64/F4/epi |
| 64 | 0.200577 | 0.196113 | -2.226% | N64/F4/epi | N64/F4/epi |
| 128 | 0.208544 | 0.201472 | -3.391% | N64/F8/epi | N64/F8/epi |
| 256 | 0.207008 | 0.209921 | +1.407% | N64/F8/epi | N64/F4/epi |
| 512 | 0.232992 | 0.213681 | -8.288% | N64/F8/epi | N64/F8/epi |
| 1024 | 0.231633 | 0.229330 | -0.994% | N64/F4/epi | N64/F8/epi |
| 2048 | 0.311298 | 0.310689 | -0.196% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.457218 | 0.463187 | +1.306% | N128/F4/reuse | N128/F4/reuse |

Tokens 1/2/4 stay in the table and all13 summary; they are excluded only from the 8–4096 retention summary.
