# kimi-k3: full24 versus retained16 selection diagnostic

**Hot AUTO selection scores, not final cold-L2 CUPTI medians.**

Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Selected tactic | In retained16 | Best retained µs | Best removed µs | Retained − removed µs | Removed latency reduction |
|---:|---|:---:|---:|---:|---:|---:|
| 1 | M128/N32/G1024/epi | yes | 70.2 | 71.3 | -1.1 | -1.57% |
| 2 | M128/N32/G512/epi | yes | 81.6 | 84.4 | -2.8 | -3.43% |
| 4 | M128/N32/G512/epi | yes | 91.8 | 93.8 | -2.0 | -2.18% |
| 8 | M128/N32/G1024/epi | yes | 121.1 | 124.3 | -3.2 | -2.64% |
| 16 | M256/N32/G1024/epi | yes | 139.9 | 142.5 | -2.6 | -1.86% |
| 32 | M128/N32/G512/epi | yes | 210.5 | 218.8 | -8.3 | -3.94% |
| 64 | M256/N32/G1024/epi | yes | 296.4 | 304.8 | -8.4 | -2.83% |
| 128 | M256/N32/G512/epi | yes | 349.8 | 358.9 | -9.1 | -2.60% |
| 256 | M256/N32/G1024/epi | yes | 378.3 | 389.4 | -11.1 | -2.93% |
| 512 | M256/N32/G1024/epi | yes | 385.2 | 399.0 | -13.8 | -3.58% |
| 4096 | M256/N128/G1024/epi | yes | 579.2 | 638.4 | -59.2 | -10.22% |
| 8192 | M256/N128/G512/epi | yes | 1007.4 | 1075.8 | -68.4 | -6.79% |
| 16384 | M256/N128/G1024/dispatch | yes | 1777.1 | 1917.5 | -140.4 | -7.90% |

Removed tactics selected at: [].
All 13 scoreboards, 104 rank winner receipts and 312 printed candidate scores validated.
Source log SHA256: `41e9f642338f94cb23b5029602780bbbc15b833383ae64d6fef6143f1f5d0ab6`.
Positive differences favor the removed M128/N64 or M128/N128 options. Rounded-score ties are preserved in JSON. No catalog decision is made.
