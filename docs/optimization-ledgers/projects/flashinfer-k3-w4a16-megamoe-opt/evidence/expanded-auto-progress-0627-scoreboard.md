# AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 70.8 | 71.2 | +0.4 | +0.56% | M128/N32/G1024/epi |
| 2 | 81.6 | 83.4 | +1.8 | +2.16% | M128/N32/G512/epi |
| 4 | 92.8 | 93.8 | +1.0 | +1.07% | M128/N32/G1024/epi |
| 8 | 120.3 | 120.5 | +0.2 | +0.17% | M128/N32/G1024/epi |
| 16 | 138.9 | 138.9 | +0.0 | +0.00% | M256/N32/G1024/epi |
| 32 | 210.5 | 210.3 | -0.2 | -0.10% | M256/N32/G1024/epi |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: False. Log SHA256: `3feec89578a949c731bedf87a62bd5015ec1e0bd4e5e945b30e3d4b2c9900d42`.
