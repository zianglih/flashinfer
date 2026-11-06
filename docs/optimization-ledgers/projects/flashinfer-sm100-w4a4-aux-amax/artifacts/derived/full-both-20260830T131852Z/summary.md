# Aux-amax benchmark summary

All ratios use paired log ratios from adjacent, parity-alternated A/B runs. Intervals are deterministic 95% paired-bootstrap intervals over repetitions.

| policy | config | scope | W4A4 speedup | 95% CI | reduction | W4A16 control |
|---|---|---|---:|---:|---:|---:|
| fixed | inference | activation-inclusive | 1.0204x | [1.0201, 1.0207] | 2.00% | 1.0004x (within-threshold) |
| fixed | inference | moe-only | 1.0238x | [1.0236, 1.0240] | 2.33% | 1.0002x (within-threshold) |
| fixed | deterministic-rl | activation-inclusive | 1.0204x | [1.0200, 1.0209] | 2.00% | 1.0008x (within-threshold) |
| fixed | deterministic-rl | moe-only | 1.0233x | [1.0229, 1.0236] | 2.27% | 1.0000x (within-threshold) |
| native | inference | activation-inclusive | 1.0206x | [1.0202, 1.0208] | 2.01% | 1.0002x (within-threshold) |
| native | inference | moe-only | 1.0232x | [1.0224, 1.0237] | 2.26% | 1.0005x (within-threshold) |
| native | deterministic-rl | activation-inclusive | 1.0205x | [1.0201, 1.0208] | 2.01% | 1.0063x (within-threshold) |
| native | deterministic-rl | moe-only | 1.0245x | [1.0243, 1.0248] | 2.39% | 1.0079x (within-threshold) |

## Inference gap versus TRTLLM

TRTLLM is intentionally not used as a deterministic-RL reference because `--no-fused-finalize` only changes the CuTe DSL path.

| policy | scope | off slowdown | on slowdown | gap closed | 95% CI |
|---|---|---:|---:|---:|---:|
| fixed | activation-inclusive | 7.46% | 5.31% | 2.15 pp | [2.12, 2.18] pp |
| fixed | moe-only | 7.28% | 4.78% | 2.50 pp | [2.47, 2.52] pp |
| native | activation-inclusive | 7.45% | 5.28% | 2.16 pp | [2.13, 2.19] pp |
| native | moe-only | 7.26% | 4.83% | 2.43 pp | [2.35, 2.48] pp |

Raw contract: EP=8, TP=1, 5 pairs, 13 token counts, 200 measured iterations per process.
