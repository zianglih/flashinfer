# Constant weight-cache policy screens — rejected

Both universal constants regress materially. Preserve the retained route-aware policy: normal priority when an adjacent token tile reuses the expert, evict-first otherwise. No rescue branch or shape gate is introduced.

Each policy has its own fresh same-GPU CAAC controls on the second C2/infra node. Frozen native choices/routes,100strict-CUPTI samples per phase, original input-quantization contracts and stock clocks are unchanged. The two candidates ran on different physical GPUs; do not subtract their percentages as a direct FIRST-vs-NORMAL measurement.

| Policy | All12 | Decode6 | Prefill6 | Negative | Clock exception quartiles | Missing clock quartiles |
|---|---:|---:|---:|---:|---:|---:|
| FIRST | -2.093% | +0.321% | -4.450% | 7/12 | 7/192 | 0 |
| NORMAL | -5.417% | -10.207% | -0.372% | 7/12 | 15/192 | 0 |

FIRST gains only+0.321% in decode while losing all six prefill cells. The N3U EP W4A4 prefill loss is−5.426% with only0.030%/0.226% control/candidate repeat spread. V3 EP MXFP4x8 loses−7.050%; V3 EP MXFP8 loses−10.032% with larger repeat variation.

NORMAL loses all six decode cells by−7.786% to−13.048%, with every repeat spread≤0.331%. Its prefill aggregate is near neutral and variable. These tight decode losses suffice to reject it. Instruction savings and fewer route loads do not justify either policy.

The results support retaining the existing adaptive cache priority. They do not independently identify the cache-miss mechanism; no new cache-counter trace was collected.

## All phase medians

### FIRST

| Model | EP/TP | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| nemo3-ultra | EP8 | CuteDSL W4A4 | 4 | 33.585 | 33.537 | 33.728 | 33.552 | -0.190% | 0.097% | 0.571% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | 16384 | 588.755 | 621.923 | 623.332 | 588.931 | -5.426% | 0.030% | 0.226% |
| v3 | EP8 | CuteDSL MXFP4x8 | 4 | 44.704 | 44.272 | 44.240 | 44.673 | +0.977% | 0.069% | 0.071% |
| v3 | EP8 | CuteDSL MXFP8 | 4 | 68.656 | 68.448 | 68.544 | 68.672 | +0.246% | 0.023% | 0.141% |
| v3 | EP8 | CuteDSL MXFP4x8 | 16384 | 613.924 | 663.988 | 656.260 | 613.219 | -7.050% | 0.115% | 1.178% |
| v3 | EP8 | CuteDSL MXFP8 | 16384 | 676.419 | 754.836 | 780.213 | 704.740 | -10.032% | 4.187% | 3.362% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 4 | 44.704 | 44.320 | 44.576 | 44.609 | +0.469% | 0.213% | 0.579% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16384 | 1808.617 | 1820.746 | 1819.641 | 1806.907 | -0.683% | 0.095% | 0.061% |
| v3 | TP8 | CuteDSL MXFP4x8 | 4 | 36.224 | 36.224 | 36.112 | 36.305 | +0.266% | 0.221% | 0.309% |
| v3 | TP8 | CuteDSL MXFP8 | 4 | 44.720 | 44.672 | 44.609 | 44.704 | +0.161% | 0.035% | 0.142% |
| v3 | TP8 | CuteDSL MXFP4x8 | 16384 | 1208.183 | 1211.320 | 1212.535 | 1208.487 | -0.296% | 0.025% | 0.100% |
| v3 | TP8 | CuteDSL MXFP8 | 16384 | 1286.151 | 1327.720 | 1331.656 | 1298.120 | -2.825% | 0.931% | 0.296% |

### NORMAL

| Model | EP/TP | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| nemo3-ultra | EP8 | CuteDSL W4A4 | 4 | 34.016 | 37.792 | 37.760 | 34.096 | -9.848% | 0.235% | 0.085% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | 16384 | 590.979 | 589.732 | 589.605 | 590.596 | +0.190% | 0.065% | 0.022% |
| v3 | EP8 | CuteDSL MXFP4x8 | 4 | 44.720 | 51.456 | 51.424 | 44.736 | -13.048% | 0.037% | 0.062% |
| v3 | EP8 | CuteDSL MXFP8 | 4 | 69.457 | 77.921 | 77.888 | 69.393 | -10.885% | 0.092% | 0.041% |
| v3 | EP8 | CuteDSL MXFP4x8 | 16384 | 633.637 | 680.821 | 633.461 | 634.709 | -3.432% | 0.169% | 7.476% |
| v3 | EP8 | CuteDSL MXFP8 | 16384 | 699.717 | 701.702 | 753.318 | 765.558 | +0.667% | 9.410% | 7.356% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 4 | 44.704 | 48.576 | 48.416 | 44.736 | -7.786% | 0.073% | 0.330% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | 16384 | 1810.092 | 1807.917 | 1809.773 | 1810.060 | +0.068% | 0.002% | 0.103% |
| v3 | TP8 | CuteDSL MXFP4x8 | 4 | 35.936 | 39.681 | 39.808 | 35.856 | -9.683% | 0.223% | 0.320% |
| v3 | TP8 | CuteDSL MXFP8 | 4 | 44.609 | 49.473 | 49.505 | 44.561 | -9.909% | 0.108% | 0.064% |
| v3 | TP8 | CuteDSL MXFP4x8 | 16384 | 1230.155 | 1224.970 | 1230.347 | 1231.146 | +0.244% | 0.081% | 0.439% |
| v3 | TP8 | CuteDSL MXFP8 | 16384 | 1329.963 | 1335.483 | 1325.611 | 1333.547 | +0.091% | 0.270% | 0.745% |

## All exposed critical-path deltas

Values are candidate minus control in microseconds. Each component uses the arithmetic mean of two phase component medians; medians need not add. Overlapping raw kernel durations are not summed.

| Policy | Model | EP/TP | Mode | Tokens | FC1 extension | FC2 extension | Combine extension |
|---|---|---|---|---:|---:|---:|---:|
| FIRST | nemo3-ultra | ep | CuteDSL W4A4 | 4 | -0.104 | +0.096 | +0.000 |
| FIRST | nemo3-ultra | ep | CuteDSL W4A4 | 16384 | -4.416 | +37.120 | +1.488 |
| FIRST | v3 | ep | CuteDSL MXFP4x8 | 4 | -0.304 | -0.200 | +0.000 |
| FIRST | v3 | ep | CuteDSL MXFP8 | 4 | -0.080 | -0.056 | +0.000 |
| FIRST | v3 | ep | CuteDSL MXFP4x8 | 16384 | +22.216 | +25.385 | -1.440 |
| FIRST | v3 | ep | CuteDSL MXFP8 | 16384 | +32.104 | +42.992 | -1.023 |
| FIRST | nemo3-ultra | tp | CuteDSL PER-TOKEN | 4 | -0.136 | -0.072 | -0.064 |
| FIRST | nemo3-ultra | tp | CuteDSL PER-TOKEN | 16384 | -2.032 | +15.208 | +0.704 |
| FIRST | v3 | tp | CuteDSL MXFP4x8 | 4 | -0.008 | -0.112 | +0.032 |
| FIRST | v3 | tp | CuteDSL MXFP8 | 4 | -0.040 | -0.008 | -0.039 |
| FIRST | v3 | tp | CuteDSL MXFP4x8 | 16384 | -4.696 | +10.296 | -1.936 |
| FIRST | v3 | tp | CuteDSL MXFP8 | 16384 | +4.361 | +32.329 | -0.831 |
| NORMAL | nemo3-ultra | ep | CuteDSL W4A4 | 4 | +1.272 | +2.552 | -0.072 |
| NORMAL | nemo3-ultra | ep | CuteDSL W4A4 | 16384 | -1.040 | -0.032 | +0.016 |
| NORMAL | v3 | ep | CuteDSL MXFP4x8 | 4 | +5.544 | +1.135 | +0.072 |
| NORMAL | v3 | ep | CuteDSL MXFP8 | 4 | +6.928 | +1.488 | +0.000 |
| NORMAL | v3 | ep | CuteDSL MXFP4x8 | 16384 | +10.183 | +6.945 | +0.288 |
| NORMAL | v3 | ep | CuteDSL MXFP8 | 16384 | -1.424 | -1.296 | -0.792 |
| NORMAL | nemo3-ultra | tp | CuteDSL PER-TOKEN | 4 | +1.391 | +3.063 | -0.288 |
| NORMAL | nemo3-ultra | tp | CuteDSL PER-TOKEN | 16384 | -0.744 | -0.832 | -0.304 |
| NORMAL | v3 | tp | CuteDSL MXFP4x8 | 4 | +2.577 | +1.312 | -0.056 |
| NORMAL | v3 | tp | CuteDSL MXFP8 | 4 | +3.840 | +0.928 | +0.064 |
| NORMAL | v3 | tp | CuteDSL MXFP4x8 | 16384 | -3.065 | -3.656 | +0.048 |
| NORMAL | v3 | tp | CuteDSL MXFP8 | 16384 | -1.728 | +0.801 | -0.185 |
