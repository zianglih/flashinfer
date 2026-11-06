Compared Baseline 4bc27889 `4bc278892b3ced0a8c81501f858de517931e2ae9` with Current 1098a348 `1098a348a1b2a4457cafba4e5263609451914043`.

Global tokens are the total input tokens across eight EP ranks. Latencies are milliseconds, reported as the median of per-sample rank-MAX CUDA-graph CUPTI timings. The workload and timing configuration are preserved in comparison.json.

| Global tokens | Baseline 4bc27889 ms | Current 1098a348 ms | Speedup (baseline / current) |
|---:|---:|---:|---:|
| 1 | 0.08523200 | 0.07782500 | 1.095175× |
| 2 | 0.10328100 | 0.09678500 | 1.067118× |
| 4 | 0.11499300 | 0.12000100 | 0.958267× |
| 8 | 0.13825700 | 0.13724800 | 1.007352× |
| 16 | 0.15192100 | 0.15315300 | 0.991956× |
| 32 | 0.17900950 | 0.18024200 | 0.993162× |
| 64 | 0.19942600 | 0.20163400 | 0.989049× |
| 128 | 0.20404900 | 0.20102500 | 1.015043× |
| 256 | 0.20769700 | 0.20184150 | 1.029010× |
| 512 | 0.21197000 | 0.21166550 | 1.001439× |
| 1024 | 0.23075350 | 0.23417700 | 0.985381× |
| 2048 | 0.30880200 | 0.30745700 | 1.004375× |
| 4096 | 0.46523450 | 0.46510800 | 1.000272× |
| 8192 | 0.75983200 | 0.77635800 | 0.978713× |

**8–8192 geometric mean speedup: 0.999521×.** Values above 1 favor current; 1/2/4-token rows remain visible but are excluded from this aggregate.

All eight ranks completed both full sweeps with matching canonical weight/input/route hashes and matching timing environments. Untimed eager outputs passed finite and exact repeat checks. Each row's 100 raw timing samples reproduce its reported median. Samples, selected tactics and resolved configurations for both implementations are retained in comparison.json.

Both implementations use BF16 FC2 output and external FP32 weighted combine. This check covers static unit alphas, with no claim for runtime alpha-copy or IKR performance. Numerical tests run separately. Sequential sweeps do not cancel temporal drift or establish statistical significance.
