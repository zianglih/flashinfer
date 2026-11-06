# FC2 partial L1-no-allocation M1 retention

Unpromoted. Primary A2 comparison yields0.998050× decode4–512 geometric speedup (5/8 faster rows), with a large same-tactic T8 regression. Prefill4k/8k medians improve slightly and16k is effectively flat/slightly slower. Historical A1 comparison is0.993955×. This does not support a general cache-policy change or a per-shape selector.

| Tokens | A2 µs | M1 µs | A2/M1 | A2/M1 MAD µs | A1 µs | A1/M1 | Same A2 tactic |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 67.2640 | 63.9530 | 1.051772 | 1.0080/0.7840 | 66.6560 | 1.042265 | no |
| 2 | 86.4325 | 81.9840 | 1.054261 | 0.8800/1.0560 | 79.5685 | 0.970537 | yes |
| 4 | 97.6480 | 93.8885 | 1.040042 | 1.0080/0.9605 | 97.1200 | 1.034418 | yes |
| 8 | 121.1045 | 129.8245 | 0.932832 | 0.9285/0.9280 | 117.2655 | 0.903262 | yes |
| 16 | 133.9045 | 133.9525 | 0.999642 | 0.7845/0.6560 | 134.6410 | 1.005140 | yes |
| 32 | 160.9280 | 158.7205 | 1.013908 | 0.7185/0.7685 | 160.7360 | 1.012698 | yes |
| 64 | 181.5205 | 183.1690 | 0.991000 | 0.9280/0.8960 | 182.8005 | 0.997988 | yes |
| 128 | 188.7045 | 188.5765 | 1.000679 | 0.6565/0.7840 | 188.1450 | 0.997712 | yes |
| 256 | 191.9045 | 191.3125 | 1.003094 | 0.9765/0.7200 | 190.4660 | 0.995575 | yes |
| 512 | 195.7290 | 194.4660 | 1.006495 | 1.0560/0.8320 | 196.4970 | 1.010444 | yes |
| 4096 | 464.6090 | 461.9070 | 1.005850 | 4.4160/3.1830 | 465.0895 | 1.006890 | yes |
| 8192 | 777.6180 | 770.1175 | 1.009739 | 16.2400/22.8475 | 759.9215 | 0.986760 | yes |
| 16384 | 1489.1595 | 1490.0875 | 0.999377 | 63.6295/71.4265 | 1497.7690 | 1.005155 | yes |

T8 worsens121.1045→129.8245µs (7.2004% higher latency), with MAD0.9285/0.9280µs. All8 ranks retain N64 MMA[256,64,256], epi_warps return and the same remaining tactic fields. Quarter medians are A2[121.632,121.249,120.769,120.801]µs and M1[130.176,129.184,129.281,130.304]µs, clearly separated throughout each arm. The observed regression is not an AUTO winner switch or a single-sample outlier; serial-arm environmental drift remains uncancelled. Twelve of13 rows retain tactics; T1 differs and is outside retention.

Prefill quarter medians (µs), preserving within-arm drift:

| Tokens | A2 quarters | M1 quarters |
|---:|---|---|
| 4096 | 463.362, 461.953, 509.697, 464.577 | 465.667, 463.170, 461.410, 460.322 |
| 8192 | 762.659, 761.538, 780.258, 812.194 | 752.389, 750.149, 799.782, 805.990 |
| 16384 | 1346.664, 1461.925, 1526.308, 1561.540 | 1342.822, 1460.041, 1508.522, 1609.162 |

Independent full-file/raw-timing audit PASS, executed once. All1300 samples per arm retained. All104 outputs per arm are finite/repeat-exact, with104 bit-exact cross-version comparisons against each A2 and historical A1. Both sealed comparisons reproduce exactly using unchanged validators. All104 frozen source hashes, runtime/helper/review pins, explicit sourcebenchmarka82f versus executed304a, same hu15 boot/environment, previous L1 closure, and current source/process/GPU closure are bound. The59 original members reconstruct from51 verified compact members and8 SHA-identical audited A1 files. The original gzip SHA is a seal reference and was not verified against local gzip bytes.

Audit `decode13-benchmark/independent-file-timing-audit.json` SHA`25914c94169fc27faab55d1c46c92f59bec7810ae76e1af3174804a92991739b`. Original archive`ee5b3dbd181747aca8faca28ddb0ade0ee661abec972de6460941b1c7ed6eec2`; compact bundle`a86d3c535e9b0b66bdf809fda74f2ac74dfecf7939e7fd36952f81b013f1deed`.

Sourcee193a2d changes only the partial-load copy atom/policy relative to current PR8 and is independent of width16. No captured M1 PTX/SASS here proves final policy lowering or identifies the cause of the mixed result. No further M1 GPU codegen/test/sanitizer requested; retain the existing PR8 implementation.
