# Threshold-4 production-policy benchmark summary

Production selects the legacy intermediate quantizer for token counts below 4 and the aux-amax path at or above 4. The 1- and 2-token rows therefore contribute an exact 1.0x ratio to the all-token production aggregate.

Ratios use adjacent, parity-alternated pairs. The all-token confidence interval resamples whole repetitions with the sealed contract's 10000 draws and seed 42.

| policy | config | scope | production W4A4 speedup | 95% CI | reduction | observed W4A16 control |
|---|---|---|---:|---:|---:|---:|
| fixed | inference | activation-inclusive | 1.0248x | [1.0245, 1.0251] | 2.42% | 1.0004x (within-threshold) |
| fixed | inference | moe-only | 1.0285x | [1.0283, 1.0287] | 2.77% | 1.0002x (within-threshold) |
| fixed | deterministic-rl | activation-inclusive | 1.0240x | [1.0236, 1.0245] | 2.34% | 1.0008x (within-threshold) |
| fixed | deterministic-rl | moe-only | 1.0265x | [1.0262, 1.0268] | 2.59% | 1.0000x (within-threshold) |
| native | inference | activation-inclusive | 1.0250x | [1.0246, 1.0252] | 2.44% | 1.0002x (within-threshold) |
| native | inference | moe-only | 1.0278x | [1.0270, 1.0283] | 2.70% | 1.0005x (within-threshold) |
| native | deterministic-rl | activation-inclusive | 1.0239x | [1.0236, 1.0241] | 2.34% | 1.0063x (within-threshold) |
| native | deterministic-rl | moe-only | 1.0278x | [1.0277, 1.0281] | 2.71% | 1.0079x (within-threshold) |

## Inference gap versus TRTLLM under the production policy

| policy | scope | off slowdown | production slowdown | gap closed | fraction closed | 95% CI |
|---|---|---:|---:|---:|---:|---:|
| fixed | activation-inclusive | 7.46% | 4.86% | 2.60 pp | 34.89% | [2.57, 2.63] pp |
| fixed | moe-only | 7.28% | 4.30% | 2.97 pp | 40.87% | [2.95, 2.99] pp |
| native | activation-inclusive | 7.45% | 4.83% | 2.62 pp | 35.14% | [2.58, 2.64] pp |
| native | moe-only | 7.26% | 4.36% | 2.90 pp | 39.94% | [2.82, 2.96] pp |

## Fixed-policy selected token rows

The medians below are measured legacy-off and experimental aux-on latencies. Production uses the off latency below the threshold.

| config | scope | tokens | off ms | aux-on ms | measured reduction | production reduction |
|---|---|---:|---:|---:|---:|---:|
| inference | activation-inclusive | 1 | 0.041104 | 0.043072 | -4.7404% | +0.0000% |
| inference | activation-inclusive | 2 | 0.053952 | 0.054465 | -0.9676% | +0.0000% |
| inference | activation-inclusive | 4 | 0.075249 | 0.073633 | +2.1895% | +2.1895% |
| inference | activation-inclusive | 8 | 0.090049 | 0.089441 | +0.6467% | +0.6467% |
| inference | activation-inclusive | 16 | 0.100289 | 0.101025 | -0.7408% | -0.7408% |
| inference | activation-inclusive | 256 | 0.179890 | 0.178194 | +0.9218% | +0.9218% |
| inference | activation-inclusive | 4096 | 0.268547 | 0.235251 | +12.3699% | +12.3699% |
| inference | moe-only | 1 | 0.035488 | 0.037296 | -5.1141% | +0.0000% |
| inference | moe-only | 2 | 0.048673 | 0.049120 | -0.9330% | +0.0000% |
| inference | moe-only | 4 | 0.068672 | 0.066721 | +2.8789% | +2.8789% |
| inference | moe-only | 8 | 0.084305 | 0.083201 | +1.3023% | +1.3023% |
| inference | moe-only | 16 | 0.092737 | 0.093409 | -0.7489% | -0.7489% |
| inference | moe-only | 256 | 0.173569 | 0.171841 | +1.0082% | +1.0082% |
| inference | moe-only | 4096 | 0.250018 | 0.216066 | +13.5841% | +13.5841% |
| deterministic-rl | activation-inclusive | 1 | 0.047104 | 0.048897 | -3.8450% | +0.0000% |
| deterministic-rl | activation-inclusive | 2 | 0.058065 | 0.058529 | -0.8261% | +0.0000% |
| deterministic-rl | activation-inclusive | 4 | 0.076881 | 0.075297 | +2.1111% | +2.1111% |
| deterministic-rl | activation-inclusive | 8 | 0.092513 | 0.091984 | +0.5749% | +0.5749% |
| deterministic-rl | activation-inclusive | 16 | 0.101665 | 0.102561 | -0.7522% | -0.7522% |
| deterministic-rl | activation-inclusive | 256 | 0.189106 | 0.188322 | +0.3742% | +0.3742% |
| deterministic-rl | activation-inclusive | 4096 | 0.308275 | 0.265506 | +13.9517% | +13.9517% |
| deterministic-rl | moe-only | 1 | 0.040448 | 0.042145 | -4.2993% | +0.0000% |
| deterministic-rl | moe-only | 2 | 0.052160 | 0.052128 | +0.0610% | +0.0000% |
| deterministic-rl | moe-only | 4 | 0.070432 | 0.068577 | +2.6390% | +2.6390% |
| deterministic-rl | moe-only | 8 | 0.086497 | 0.085633 | +0.7701% | +0.7701% |
| deterministic-rl | moe-only | 16 | 0.096001 | 0.096833 | -0.9398% | -0.9398% |
| deterministic-rl | moe-only | 256 | 0.181762 | 0.181025 | +0.3944% | +0.3944% |
| deterministic-rl | moe-only | 4096 | 0.280100 | 0.237218 | +15.3093% | +15.3093% |

## Provenance

- Benchmark revision: `32f7b6d001182a0a55b453a512bf737ed93b547a`
- Source-state digest: `d99f84bdcccd3c6b9cc16619de2cc9dbd5364c5419707618b747877c73291e25`
- Raw checksum entries verified: 730
- Raw `SHA256SUMS`: `385fec39707c0b5791773222ca1dcf4d436f23bde18ababa8a51123790b0dc9d`
- Parsed `process-medians.csv`: `9fab11bd36868c417b20b1894e20785f04911b361dbf8f07f4e8b9097d974c29`
- Derivation helper: `fd6098bb8576d32ff2360c54b3157d4a09351b5b59f46065bb9845f2abbe893b`

This is a deterministic policy derivation from the sealed same-source A/B matrix, not a fresh timing run of the final threshold-gated commit.
