# AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | not present | 71.2 | — | — | M256/N32/G1024/epi |
| 2 | not present | 84.9 | — | — | M256/N32/G1024/epi |
| 4 | not present | 93.7 | — | — | M256/N32/G1024/epi |
| 8 | not present | 120.4 | — | — | M256/N32/G1024/epi |
| 16 | not present | 140.3 | — | — | M256/N32/G1024/epi |
| 32 | not present | 210.5 | — | — | M256/N32/G1024/epi |
| 64 | not present | 294.5 | — | — | M256/N32/G1024/epi |
| 128 | not present | 349.5 | — | — | M256/N32/G512/epi |
| 256 | not present | 376.5 | — | — | M256/N32/G1024/epi |
| 512 | not present | 385.6 | — | — | M256/N32/G1024/epi |
| 4096 | not present | 578.6 | — | — | M256/N128/G1024/epi |
| 8192 | not present | 1008.4 | — | — | M256/N128/G512/epi |
| 16384 | not present | 1779.5 | — | — | M256/N128/G512/dispatch |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `018f117166923964de686528682c883f28276b845cf5066bb95811b541c6f244`.
