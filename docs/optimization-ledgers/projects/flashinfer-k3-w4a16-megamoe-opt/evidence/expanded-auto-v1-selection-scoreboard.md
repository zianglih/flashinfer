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
| 64 | 296.5 | 294.5 | -2.0 | -0.68% | M256/N32/G1024/epi |
| 128 | 349.7 | 347.7 | -2.0 | -0.58% | M256/N32/G512/epi |
| 256 | 380.4 | 377.2 | -3.2 | -0.85% | M256/N32/G1024/epi |
| 512 | 390.7 | 385.2 | -5.5 | -1.43% | M256/N32/G1024/epi |
| 4096 | 636.8 | 578.3 | -58.5 | -10.12% | M256/N128/G1024/epi |
| 8192 | 1075.8 | 1008.1 | -67.7 | -6.72% | M256/N128/G512/epi |
| 16384 | 1923.7 | 1776.2 | -147.5 | -8.30% | M256/N128/G1024/dispatch |

Selection-only aggregates (not official performance aggregates):

| Domain | Best M128 speedup vs best M256 | Selection latency reduction |
|---|---:|---:|
| all11_retention | 0.976212× | -2.437% |
| decode4_through512 | 0.997042× | -0.297% |
| prefill4096_8192_16384 | 0.922767× | -8.370% |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `835f83564cf8199647ba7c98a4ce6a7682e6a18a920cfe03e3ebb90972bd8176`.
