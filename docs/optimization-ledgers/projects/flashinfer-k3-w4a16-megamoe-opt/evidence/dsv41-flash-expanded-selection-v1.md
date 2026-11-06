# deepseek-v41-flash AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 54.0 | 54.7 | +0.7 | +1.28% | M128/N32/G512/epi |
| 2 | 57.8 | 58.7 | +0.9 | +1.53% | M128/N32/G1024/epi |
| 4 | 60.0 | 60.5 | +0.5 | +0.83% | M128/N32/G1024/epi |
| 8 | 75.4 | 75.9 | +0.5 | +0.66% | M128/N32/G1024/epi |
| 16 | 87.7 | 88.6 | +0.9 | +1.02% | M128/N32/G1024/epi |
| 32 | 114.2 | 115.1 | +0.9 | +0.78% | M128/N32/G1024/epi |
| 64 | 148.9 | 149.1 | +0.2 | +0.13% | M128/N32/G1024/epi |
| 128 | 182.8 | 183.9 | +1.1 | +0.60% | M128/N32/G512/epi |
| 256 | 189.0 | 191.9 | +2.9 | +1.51% | M128/N32/G1024/epi |
| 512 | 192.1 | 194.1 | +2.0 | +1.03% | M128/N32/G512/epi |
| 4096 | 349.8 | 316.9 | -32.9 | -10.38% | M256/N128/G512/epi |
| 8192 | 538.6 | 490.1 | -48.5 | -9.90% | M256/N128/G1024/dispatch |
| 16384 | 888.4 | 822.6 | -65.8 | -8.00% | M256/N128/G512/dispatch |

Selection-only aggregates (not official performance aggregates):

| Domain | Best M128 speedup vs best M256 | Selection latency reduction |
|---|---:|---:|
| all11_retention | 0.981608× | -1.874% |
| decode4_through512 | 1.008271× | +0.820% |
| prefill4096_8192_16384 | 0.913903× | -9.421% |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `2df303d61eebad7308c5fc98255b842ce593ff0d3385264600184bff4499f96f`.
