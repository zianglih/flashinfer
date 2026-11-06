# glm5 AUTO selection scoreboard diagnostic

**Selection timings only; separate from the final CUPTI100 benchmark.**

maximum across EP ranks of each rank median CUDA-event graph replay time on hot staged inputs.
Autotuner defaults: 3 preparation warmups, 6 untimed graph replays, 10 timed CUDA-event replays per candidate; no cold-L2 flush in selection timing.
Printed selection scores are rounded to 0.1 us; apparent ties may hide finer ordering. No raw candidate timing distributions are present in the log.
These are not the final CUPTI100 cold-L2 per-iteration-rank-MAX medians. Never pool or replace official benchmark samples with these scores.
Best-of-many selection scores in one sequential tuning pass can reflect ordering/noise; within-sweep M-axis gaps inform retention but do not establish repeatable kernel speedup or correctness.

| Tokens | Best M128 score µs | Best M256 score µs | M256 − M128 µs | Selection latency reduction | Actual selected tactic |
|---:|---:|---:|---:|---:|---|
| 1 | 55.0 | 55.6 | +0.6 | +1.08% | M128/N32/G1024/epi |
| 2 | 70.2 | 69.7 | -0.5 | -0.72% | M256/N32/G512/epi |
| 4 | 79.3 | 77.4 | -1.9 | -2.45% | M256/N32/G1024/epi |
| 8 | 91.7 | 92.4 | +0.7 | +0.76% | M128/N32/G512/epi |
| 16 | 104.0 | 103.9 | -0.1 | -0.10% | M256/N32/G512/epi |
| 32 | 124.5 | 122.4 | -2.1 | -1.72% | M256/N32/G1024/epi |
| 64 | 141.0 | 140.9 | -0.1 | -0.07% | M256/N32/G512/epi |
| 128 | 146.0 | 145.1 | -0.9 | -0.62% | M256/N32/G1024/epi |
| 256 | 149.1 | 148.9 | -0.2 | -0.13% | M256/N32/G1024/epi |
| 512 | 157.2 | 155.2 | -2.0 | -1.29% | M256/N32/G512/epi |
| 4096 | 578.9 | 386.4 | -192.5 | -49.82% | M256/N128/G1024/dispatch |
| 8192 | 1053.9 | 654.9 | -399.0 | -60.93% | M256/N128/G1024/dispatch |
| 16384 | 2018.5 | 1151.2 | -867.3 | -75.34% | M256/N128/G512/dispatch |

Selection-only aggregates (not official performance aggregates):

| Domain | Best M128 speedup vs best M256 | Selection latency reduction |
|---|---:|---:|
| all11_retention | 0.872745× | -14.581% |
| decode4_through512 | 0.993067× | -0.698% |
| prefill4096_8192_16384 | 0.618458× | -61.692% |

All printed candidate scores, rounded-score ties, source log line numbers and provenance are retained in the adjacent JSON.
Full13 scoreboards: True. Log SHA256: `40071d4540062b2f56d9f4a1cd12f8ed903fdfffead361f25edb19b103f6c4a9`.
