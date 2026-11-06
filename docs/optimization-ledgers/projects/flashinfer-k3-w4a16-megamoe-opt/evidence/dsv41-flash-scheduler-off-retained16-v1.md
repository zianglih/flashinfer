# deepseek-v41-flash: full24 versus retained16 selection diagnostic

**Hot AUTO selection scores, not final cold-L2 CUPTI medians.**

Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Selected tactic | In retained16 | Best retained µs | Best removed µs | Retained − removed µs | Removed latency reduction |
|---:|---|:---:|---:|---:|---:|---:|
| 1 | M256/N32/G1024/epi | yes | 54.5 | 54.7 | -0.2 | -0.37% |
| 2 | M128/N32/G1024/epi | yes | 57.0 | 59.1 | -2.1 | -3.68% |
| 4 | M128/N32/G512/epi | yes | 60.9 | 61.9 | -1.0 | -1.64% |
| 8 | M128/N32/G512/epi | yes | 75.5 | 77.4 | -1.9 | -2.52% |
| 16 | M128/N32/G512/epi | yes | 87.7 | 91.6 | -3.9 | -4.45% |
| 32 | M128/N32/G1024/epi | yes | 112.2 | 120.2 | -8.0 | -7.13% |
| 64 | M128/N32/G1024/epi | yes | 148.5 | 160.0 | -11.5 | -7.74% |
| 128 | M128/N32/G512/epi | yes | 183.8 | 199.5 | -15.7 | -8.54% |
| 256 | M128/N32/G1024/epi | yes | 189.0 | 208.5 | -19.5 | -10.32% |
| 512 | M128/N32/G1024/epi | yes | 192.1 | 210.7 | -18.6 | -9.68% |
| 4096 | M256/N128/G512/epi | yes | 317.5 | 349.8 | -32.3 | -10.17% |
| 8192 | M256/N128/G512/dispatch | yes | 492.6 | 537.6 | -45.0 | -9.14% |
| 16384 | M256/N128/G1024/dispatch | yes | 821.7 | 890.4 | -68.7 | -8.36% |

Removed tactics selected at: [].
All 13 scoreboards, 104 rank winner receipts and 312 printed candidate scores validated.
Source log SHA256: `bf186652fb32d04533379f4b4d9b4794f1ec3f8c6c4e1f88a1f2ce711cccd2b0`.
Positive differences favor the removed M128/N64 or M128/N128 options. Rounded-score ties are preserved in JSON. No catalog decision is made.
