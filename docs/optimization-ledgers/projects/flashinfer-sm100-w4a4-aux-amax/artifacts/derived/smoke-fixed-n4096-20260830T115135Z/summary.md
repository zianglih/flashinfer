# Aux-amax benchmark summary

All ratios use paired log ratios from adjacent, parity-alternated A/B runs. Intervals are deterministic 95% paired-bootstrap intervals over repetitions.

| policy | config | scope | W4A4 speedup | 95% CI | reduction | W4A16 control |
|---|---|---|---:|---:|---:|---:|
| fixed | inference | moe-only | 1.1493x | [1.1482, 1.1505] | 12.99% | 1.0012x (within-threshold) |
| fixed | deterministic-rl | moe-only | 1.1824x | [1.1819, 1.1830] | 15.43% | 0.9993x (within-threshold) |

## Inference gap versus TRTLLM

TRTLLM is intentionally not used as a deterministic-RL reference because `--no-fused-finalize` only changes the CuTe DSL path.

| policy | scope | off slowdown | on slowdown | gap closed | 95% CI |
|---|---|---:|---:|---:|---:|
| fixed | moe-only | -13.26% | -24.53% | 11.27 pp | [11.21, 11.33] pp |

Raw contract: EP=8, TP=1, 2 pairs, 1 token counts, 20 measured iterations per process.
