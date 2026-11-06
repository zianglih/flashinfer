# deepseek-v41-flash AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | not present | 54.9 | — | — | M256/N64/G512/epi |
| 2 | not present | 60.6 | — | — | M256/N64/G1024/epi |
| 4 | not present | 62.0 | — | — | M256/N64/G512/epi |
| 8 | not present | 77.1 | — | — | M256/N64/G1024/epi |
| 16 | not present | 89.7 | — | — | M256/N64/G1024/epi |
| 32 | not present | 116.4 | — | — | M256/N64/G512/epi |
| 64 | not present | 153.1 | — | — | M256/N64/G1024/epi |
| 128 | not present | 190.0 | — | — | M256/N64/G1024/epi |
| 256 | not present | 198.3 | — | — | M256/N64/G512/epi |
| 512 | not present | 200.3 | — | — | M256/N64/G512/epi |
| 4096 | not present | 318.9 | — | — | M256/N128/G1024/dispatch |
| 8192 | not present | 489.7 | — | — | M256/N128/G1024/dispatch |
| 16384 | not present | 823.0 | — | — | M256/N128/G1024/dispatch |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `b41ee87416f94b2f1c3b9fefb08a857aef06a9069138750c13df17ac1359c6a3`.
