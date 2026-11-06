# Aux-amax benchmark summary

All ratios use paired log ratios from adjacent, parity-alternated A/B runs. Intervals are deterministic 95% paired-bootstrap intervals over repetitions.

| policy | config | scope | W4A4 speedup | 95% CI | reduction | W4A16 control |
|---|---|---|---:|---:|---:|---:|
| fixed | inference | activation-inclusive | 1.1364x | [1.1364, 1.1364] | 12.00% | 1.0010x (within-threshold) |
| fixed | inference | moe-only | 1.1364x | [1.1364, 1.1364] | 12.00% | 1.0010x (within-threshold) |
| fixed | deterministic-rl | activation-inclusive | 1.2000x | [1.2000, 1.2000] | 16.67% | 1.0010x (within-threshold) |
| fixed | deterministic-rl | moe-only | 1.2000x | [1.2000, 1.2000] | 16.67% | 1.0010x (within-threshold) |
| native | inference | activation-inclusive | 1.2500x | [1.2500, 1.2500] | 20.00% | 1.0010x (within-threshold) |
| native | inference | moe-only | 1.2500x | [1.2500, 1.2500] | 20.00% | 1.0010x (within-threshold) |
| native | deterministic-rl | activation-inclusive | 1.2400x | [1.2400, 1.2400] | 19.35% | 1.0010x (within-threshold) |
| native | deterministic-rl | moe-only | 1.2400x | [1.2400, 1.2400] | 19.35% | 1.0010x (within-threshold) |

## Inference gap versus TRTLLM

TRTLLM is intentionally not used as a deterministic-RL reference because `--no-fused-finalize` only changes the CuTe DSL path.

| policy | scope | off slowdown | on slowdown | gap closed | 95% CI |
|---|---|---:|---:|---:|---:|
| fixed | activation-inclusive | 25.00% | 10.00% | 15.00 pp | [15.00, 15.00] pp |
| fixed | moe-only | 25.00% | 10.00% | 15.00 pp | [15.00, 15.00] pp |
| native | activation-inclusive | 30.00% | 4.00% | 26.00 pp | [26.00, 26.00] pp |
| native | moe-only | 30.00% | 4.00% | 26.00 pp | [26.00, 26.00] pp |

Raw contract: EP=8, TP=1, 2 pairs, 2 token counts, 5 measured iterations per process.
