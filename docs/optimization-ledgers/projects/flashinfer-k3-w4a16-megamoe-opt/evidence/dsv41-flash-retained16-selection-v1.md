# deepseek-v41-flash: full24 versus retained16 selection diagnostic

**Hot AUTO selection scores, not final cold-L2 CUPTI medians.**

Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Selected tactic | In retained16 | Best retained µs | Best removed µs | Retained − removed µs | Removed latency reduction |
|---:|---|:---:|---:|---:|---:|---:|
| 1 | M128/N32/G512/epi | yes | 54.0 | 54.7 | -0.7 | -1.30% |
| 2 | M128/N32/G1024/epi | yes | 57.8 | 60.7 | -2.9 | -5.02% |
| 4 | M128/N32/G1024/epi | yes | 60.0 | 61.1 | -1.1 | -1.83% |
| 8 | M128/N32/G1024/epi | yes | 75.4 | 77.4 | -2.0 | -2.65% |
| 16 | M128/N32/G1024/epi | yes | 87.7 | 91.5 | -3.8 | -4.33% |
| 32 | M128/N32/G1024/epi | yes | 114.2 | 120.3 | -6.1 | -5.34% |
| 64 | M128/N32/G1024/epi | yes | 148.9 | 159.3 | -10.4 | -6.98% |
| 128 | M128/N32/G512/epi | yes | 182.8 | 198.3 | -15.5 | -8.48% |
| 256 | M128/N32/G1024/epi | yes | 189.0 | 208.5 | -19.5 | -10.32% |
| 512 | M128/N32/G512/epi | yes | 192.1 | 211.4 | -19.3 | -10.05% |
| 4096 | M256/N128/G512/epi | yes | 316.9 | 349.8 | -32.9 | -10.38% |
| 8192 | M256/N128/G1024/dispatch | yes | 490.1 | 538.6 | -48.5 | -9.90% |
| 16384 | M256/N128/G512/dispatch | yes | 822.6 | 888.4 | -65.8 | -8.00% |

Removed tactics selected at: [].
All 13 scoreboards, 104 rank winner receipts and 312 printed candidate scores validated.
Source log SHA256: `2df303d61eebad7308c5fc98255b842ce593ff0d3385264600184bff4499f96f`.
Positive differences favor the removed M128/N64 or M128/N128 options. Rounded-score ties are preserved in JSON. No catalog decision is made.
