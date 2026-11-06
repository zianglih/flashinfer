# deepseek-v41-flash AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 54.6 | 54.5 | -0.1 | -0.18% | M256/N32/G1024/epi |
| 2 | 57.0 | 58.9 | +1.9 | +3.23% | M128/N32/G1024/epi |
| 4 | 60.9 | 60.9 | +0.0 | +0.00% | M128/N32/G512/epi |
| 8 | 75.5 | 75.5 | +0.0 | +0.00% | M128/N32/G512/epi |
| 16 | 87.7 | 88.6 | +0.9 | +1.02% | M128/N32/G512/epi |
| 32 | 112.2 | 114.8 | +2.6 | +2.26% | M128/N32/G1024/epi |
| 64 | 148.5 | 149.1 | +0.6 | +0.40% | M128/N32/G1024/epi |
| 128 | 183.8 | 184.1 | +0.3 | +0.16% | M128/N32/G512/epi |
| 256 | 189.0 | 191.6 | +2.6 | +1.36% | M128/N32/G1024/epi |
| 512 | 192.1 | 194.1 | +2.0 | +1.03% | M128/N32/G1024/epi |
| 4096 | 349.8 | 317.5 | -32.3 | -10.17% | M256/N128/G512/epi |
| 8192 | 537.6 | 492.6 | -45.0 | -9.14% | M256/N128/G512/dispatch |
| 16384 | 890.4 | 821.7 | -68.7 | -8.36% | M256/N128/G1024/dispatch |

Selection-only aggregates (not official performance aggregates):

| Domain | Best M128 speedup vs best M256 | Selection latency reduction |
|---|---:|---:|
| all11_retention | 0.981822× | -1.851% |
| decode4_through512 | 1.007881× | +0.782% |
| prefill4096_8192_16384 | 0.915579× | -9.221% |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `bf186652fb32d04533379f4b4d9b4794f1ec3f8c6c4e1f88a1f2ce711cccd2b0`.
