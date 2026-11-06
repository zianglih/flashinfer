# CuTe DSL W4A4 comparison (1–16,384 tokens)

Baseline arm: `baseline`. Candidate arm: `combined`.

Each latency is the native per-case median from one sweep. Speedup = baseline unfused / candidate unfused; values above 1 mean the candidate unfused path is faster. Ratios compare the same token count and activation scaling. No aggregate metrics or repeated-sweep statistics are computed.

## W4A4 per-tensor activation scaling

| Tokens | Baseline unfused (µs) | Candidate unfused (µs) | Baseline unfused / candidate unfused |
| ---: | ---: | ---: | ---: |
| 1 | 33.280 | 34.240 | 0.9720× |
| 2 | 42.817 | 39.744 | 1.0773× |
| 4 | 59.777 | 55.984 | 1.0678× |
| 8 | 75.857 | 72.449 | 1.0470× |
| 16 | 85.121 | 81.889 | 1.0395× |
| 32 | 117.777 | 112.929 | 1.0429× |
| 64 | 152.705 | 145.857 | 1.0470× |
| 128 | 156.353 | 150.066 | 1.0419× |
| 256 | 164.993 | 157.809 | 1.0455× |
| 512 | 166.786 | 160.673 | 1.0380× |
| 1024 | 172.577 | 168.097 | 1.0267× |
| 2048 | 184.705 | 183.602 | 1.0060× |
| 4096 | 225.074 | 224.866 | 1.0009× |
| 8192 | 321.091 | 323.106 | 0.9938× |
| 16384 | 502.884 | 514.389 | 0.9776× |

## W4A4 per-token activation scaling

| Tokens | Baseline unfused (µs) | Candidate unfused (µs) | Baseline unfused / candidate unfused |
| ---: | ---: | ---: | ---: |
| 1 | 43.520 | 46.113 | 0.9438× |
| 2 | 53.888 | 50.400 | 1.0692× |
| 4 | 74.128 | 70.913 | 1.0453× |
| 8 | 89.217 | 85.904 | 1.0386× |
| 16 | 99.697 | 95.713 | 1.0416× |
| 32 | 133.825 | 129.297 | 1.0350× |
| 64 | 169.681 | 163.905 | 1.0352× |
| 128 | 175.617 | 169.650 | 1.0352× |
| 256 | 183.634 | 177.505 | 1.0345× |
| 512 | 188.434 | 182.338 | 1.0334× |
| 1024 | 198.946 | 195.105 | 1.0197× |
| 2048 | 222.482 | 221.027 | 1.0066× |
| 4096 | 284.467 | 285.010 | 0.9981× |
| 8192 | 406.020 | 408.964 | 0.9928× |
| 16384 | 671.990 | 683.414 | 0.9833× |

## W4A16 baseline control

W4A16 consumes BF16 activations. These are baseline reference measurements, not a candidate before/after comparison. An activation-scaling run label identifies its source log and does not define a separate W4A16 precision mode.

| Source run | Finalize | Tokens | Latency (ms) | TFLOPS |
| --- | --- | ---: | ---: | ---: |
| per-tensor | unfused | 1 | 0.046512 | 1.893693 |
| per-tensor | unfused | 2 | 0.052096 | 3.381464 |
| per-tensor | unfused | 4 | 0.074625 | 4.721227 |
| per-tensor | unfused | 8 | 0.096448 | 7.305900 |
| per-tensor | unfused | 16 | 0.106017 | 13.293020 |
| per-tensor | unfused | 32 | 0.155313 | 18.147691 |
| per-tensor | unfused | 64 | 0.203906 | 27.645800 |
| per-tensor | unfused | 128 | 0.208481 | 54.078257 |
| per-tensor | unfused | 256 | 0.215970 | 104.406067 |
| per-tensor | unfused | 512 | 0.222754 | 202.452735 |
| per-tensor | unfused | 1024 | 0.235794 | 382.513182 |
| per-tensor | unfused | 2048 | 0.278259 | 648.277147 |
| per-tensor | unfused | 4096 | 0.366467 | 984.474053 |
| per-tensor | unfused | 8192 | 0.707813 | 1019.413314 |
| per-tensor | unfused | 16384 | 1.339755 | 1077.143562 |

## Complete native latency and TFLOPS rows

All native CSV result rows in each selected arm are preserved below, including any fused controls. The source logs retain setup and autotuning output.

<details>
<summary>baseline/per-tensor-unfused.log</summary>

SHA-256: `1ab11c310a19bb1ae81f28766839e0904061e5e31ca4b1ce5917bb1a39b45485`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A16 | 1 | 0.046512 | 1.893693 |
| CuteDSL W4A4 | 1 | 0.033280 | 2.646606 |
| CuteDSL W4A16 | 2 | 0.052096 | 3.381464 |
| CuteDSL W4A4 | 2 | 0.042817 | 4.114320 |
| CuteDSL W4A16 | 4 | 0.074625 | 4.721227 |
| CuteDSL W4A4 | 4 | 0.059777 | 5.893931 |
| CuteDSL W4A16 | 8 | 0.096448 | 7.305900 |
| CuteDSL W4A4 | 8 | 0.075857 | 9.289098 |
| CuteDSL W4A16 | 16 | 0.106017 | 13.293020 |
| CuteDSL W4A4 | 16 | 0.085121 | 16.556366 |
| CuteDSL W4A16 | 32 | 0.155313 | 18.147691 |
| CuteDSL W4A4 | 32 | 0.117777 | 23.931432 |
| CuteDSL W4A16 | 64 | 0.203906 | 27.645800 |
| CuteDSL W4A4 | 64 | 0.152705 | 36.915259 |
| CuteDSL W4A16 | 128 | 0.208481 | 54.078257 |
| CuteDSL W4A4 | 128 | 0.156353 | 72.107917 |
| CuteDSL W4A16 | 256 | 0.215970 | 104.406067 |
| CuteDSL W4A4 | 256 | 0.164993 | 136.663848 |
| CuteDSL W4A16 | 512 | 0.222754 | 202.452735 |
| CuteDSL W4A4 | 512 | 0.166786 | 270.389341 |
| CuteDSL W4A16 | 1024 | 0.235794 | 382.513182 |
| CuteDSL W4A4 | 1024 | 0.172577 | 522.630779 |
| CuteDSL W4A16 | 2048 | 0.278259 | 648.277147 |
| CuteDSL W4A4 | 2048 | 0.184705 | 976.630987 |
| CuteDSL W4A16 | 4096 | 0.366467 | 984.474053 |
| CuteDSL W4A4 | 4096 | 0.225074 | 1602.927272 |
| CuteDSL W4A16 | 8192 | 0.707813 | 1019.413314 |
| CuteDSL W4A4 | 8192 | 0.321091 | 2247.196296 |
| CuteDSL W4A16 | 16384 | 1.339755 | 1077.143562 |
| CuteDSL W4A4 | 16384 | 0.502884 | 2869.665791 |

</details>

<details>
<summary>baseline/per-token-unfused.log</summary>

SHA-256: `308ad4331133c0e522d60edff53c7484a56b40a6b11de59f804b441b80069c52`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.043520 | 2.023906 |
| CuteDSL W4A4 | 2 | 0.053888 | 3.269017 |
| CuteDSL W4A4 | 4 | 0.074128 | 4.752849 |
| CuteDSL W4A4 | 8 | 0.089217 | 7.898125 |
| CuteDSL W4A4 | 16 | 0.099697 | 14.135693 |
| CuteDSL W4A4 | 32 | 0.133825 | 21.061706 |
| CuteDSL W4A4 | 64 | 0.169681 | 33.222014 |
| CuteDSL W4A4 | 128 | 0.175617 | 64.197982 |
| CuteDSL W4A4 | 256 | 0.183634 | 122.791203 |
| CuteDSL W4A4 | 512 | 0.188434 | 239.326641 |
| CuteDSL W4A4 | 1024 | 0.198946 | 453.360777 |
| CuteDSL W4A4 | 2048 | 0.222482 | 810.800993 |
| CuteDSL W4A4 | 4096 | 0.284467 | 1268.259190 |
| CuteDSL W4A4 | 8192 | 0.406020 | 1777.140303 |
| CuteDSL W4A4 | 16384 | 0.671990 | 2147.517203 |

</details>

<details>
<summary>combined/per-tensor-unfused.log</summary>

SHA-256: `403e901291a77813a51f7c8e50f53139eec4dfeb525e66f34db3f5e79e739acd`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.034240 | 2.572441 |
| CuteDSL W4A4 | 2 | 0.039744 | 4.432386 |
| CuteDSL W4A4 | 4 | 0.055984 | 6.293198 |
| CuteDSL W4A4 | 8 | 0.072449 | 9.726057 |
| CuteDSL W4A4 | 16 | 0.081889 | 17.209712 |
| CuteDSL W4A4 | 32 | 0.112929 | 24.958800 |
| CuteDSL W4A4 | 64 | 0.145857 | 38.648434 |
| CuteDSL W4A4 | 128 | 0.150066 | 75.128871 |
| CuteDSL W4A4 | 256 | 0.157809 | 142.884797 |
| CuteDSL W4A4 | 512 | 0.160673 | 280.676633 |
| CuteDSL W4A4 | 1024 | 0.168097 | 536.561112 |
| CuteDSL W4A4 | 2048 | 0.183602 | 982.500832 |
| CuteDSL W4A4 | 4096 | 0.224866 | 1604.409972 |
| CuteDSL W4A4 | 8192 | 0.323106 | 2233.178552 |
| CuteDSL W4A4 | 16384 | 0.514389 | 2805.484593 |

</details>

<details>
<summary>combined/per-token-unfused.log</summary>

SHA-256: `1b4a134a6b5f685d3c4672ca72df8b245cc3bfa49694a83316111b7ea2dc078f`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.046113 | 1.910099 |
| CuteDSL W4A4 | 2 | 0.050400 | 3.495253 |
| CuteDSL W4A4 | 4 | 0.070913 | 4.968398 |
| CuteDSL W4A4 | 8 | 0.085904 | 8.202633 |
| CuteDSL W4A4 | 16 | 0.095713 | 14.724083 |
| CuteDSL W4A4 | 32 | 0.129297 | 21.799209 |
| CuteDSL W4A4 | 64 | 0.163905 | 34.392650 |
| CuteDSL W4A4 | 128 | 0.169650 | 66.456365 |
| CuteDSL W4A4 | 256 | 0.177505 | 127.030666 |
| CuteDSL W4A4 | 512 | 0.182338 | 247.327253 |
| CuteDSL W4A4 | 1024 | 0.195105 | 462.284832 |
| CuteDSL W4A4 | 2048 | 0.221027 | 816.140266 |
| CuteDSL W4A4 | 4096 | 0.285010 | 1265.838462 |
| CuteDSL W4A4 | 8192 | 0.408964 | 1764.349400 |
| CuteDSL W4A4 | 16384 | 0.683414 | 2111.617572 |

</details>
