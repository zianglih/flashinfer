# kimi-k3 AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 70.2 | 71.2 | +1.0 | +1.40% | M128/N32/G1024/epi |
| 2 | 81.6 | 83.6 | +2.0 | +2.39% | M128/N32/G512/epi |
| 4 | 91.8 | 93.4 | +1.6 | +1.71% | M128/N32/G512/epi |
| 8 | 121.1 | 122.4 | +1.3 | +1.06% | M128/N32/G1024/epi |
| 16 | 140.0 | 139.9 | -0.1 | -0.07% | M256/N32/G1024/epi |
| 32 | 210.5 | 211.2 | +0.7 | +0.33% | M128/N32/G512/epi |
| 64 | 296.6 | 296.4 | -0.2 | -0.07% | M256/N32/G1024/epi |
| 128 | 351.2 | 349.8 | -1.4 | -0.40% | M256/N32/G512/epi |
| 256 | 380.0 | 378.3 | -1.7 | -0.45% | M256/N32/G1024/epi |
| 512 | 390.6 | 385.2 | -5.4 | -1.40% | M256/N32/G1024/epi |
| 4096 | 638.4 | 579.2 | -59.2 | -10.22% | M256/N128/G1024/epi |
| 8192 | 1075.8 | 1007.4 | -68.4 | -6.79% | M256/N128/G512/epi |
| 16384 | 1917.5 | 1777.1 | -140.4 | -7.90% | M256/N128/G1024/dispatch |

Selection-only aggregates (not official performance aggregates):

| Domain | Best M128 speedup vs best M256 | Selection latency reduction |
|---|---:|---:|
| all11_retention | 0.979169× | -2.127% |
| decode4_through512 | 1.000936× | +0.094% |
| prefill4096_8192_16384 | 0.923409× | -8.294% |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `41e9f642338f94cb23b5029602780bbbc15b833383ae64d6fef6143f1f5d0ab6`.
