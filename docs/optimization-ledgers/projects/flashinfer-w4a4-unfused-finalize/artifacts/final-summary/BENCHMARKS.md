# CuTe DSL W4A4 comparison (1–16,384 tokens)

Baseline arm: `baseline`. Candidate arm: `combined-v2`.

Each latency is the native per-case median from one sweep. Speedup = baseline unfused / candidate unfused; values above 1 mean the candidate unfused path is faster. Ratios compare the same token count and activation scaling. No aggregate metrics or repeated-sweep statistics are computed.

The additional baseline fused / candidate unfused ratio compares different finalize settings. Values above 1 mean candidate unfused is faster than baseline fused; it is not the same-mode implementation speedup.

## W4A4 per-tensor activation scaling

| Tokens | Baseline unfused (µs) | Candidate unfused (µs) | Baseline unfused / candidate unfused | Baseline fused (µs) | Baseline fused / candidate unfused |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 33.280 | 30.176 | 1.1029× | 32.753 | 1.0854× |
| 2 | 42.817 | 39.889 | 1.0734× | 38.256 | 0.9591× |
| 4 | 59.777 | 55.872 | 1.0699× | 54.224 | 0.9705× |
| 8 | 75.857 | 72.576 | 1.0452× | 70.640 | 0.9733× |
| 16 | 85.121 | 81.889 | 1.0395× | 79.984 | 0.9767× |
| 32 | 117.777 | 112.912 | 1.0431× | 110.401 | 0.9778× |
| 64 | 152.705 | 145.825 | 1.0472× | 143.409 | 0.9834× |
| 128 | 156.353 | 150.033 | 1.0421× | 147.585 | 0.9837× |
| 256 | 164.993 | 158.193 | 1.0430× | 155.617 | 0.9837× |
| 512 | 166.786 | 160.754 | 1.0375× | 157.185 | 0.9778× |
| 1024 | 172.577 | 168.385 | 1.0249× | 162.897 | 0.9674× |
| 2048 | 184.705 | 178.482 | 1.0349× | 179.377 | 1.0050× |
| 4096 | 225.074 | 214.226 | 1.0506× | 211.074 | 0.9853× |
| 8192 | 321.091 | 305.522 | 1.0510× | 293.586 | 0.9609× |
| 16384 | 502.884 | 480.772 | 1.0460× | 441.908 | 0.9192× |

## W4A4 per-token activation scaling

| Tokens | Baseline unfused (µs) | Candidate unfused (µs) | Baseline unfused / candidate unfused | Baseline fused (µs) | Baseline fused / candidate unfused |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 43.520 | 40.192 | 1.0828× | 39.201 | 0.9753× |
| 2 | 53.888 | 50.400 | 1.0692× | 49.889 | 0.9899× |
| 4 | 74.128 | 70.897 | 1.0456× | 68.913 | 0.9720× |
| 8 | 89.217 | 86.337 | 1.0334× | 85.520 | 0.9905× |
| 16 | 99.697 | 95.873 | 1.0399× | 94.080 | 0.9813× |
| 32 | 133.825 | 129.154 | 1.0362× | 127.713 | 0.9888× |
| 64 | 169.681 | 163.554 | 1.0375× | 161.218 | 0.9857× |
| 128 | 175.617 | 169.650 | 1.0352× | 166.961 | 0.9841× |
| 256 | 183.634 | 177.441 | 1.0349× | 174.482 | 0.9833× |
| 512 | 188.434 | 182.209 | 1.0342× | 178.178 | 0.9779× |
| 1024 | 198.946 | 194.689 | 1.0219× | 188.754 | 0.9695× |
| 2048 | 222.482 | 215.697 | 1.0315× | 209.186 | 0.9698× |
| 4096 | 284.467 | 274.339 | 1.0369× | 265.603 | 0.9682× |
| 8192 | 406.020 | 391.636 | 1.0367× | 368.916 | 0.9420× |
| 16384 | 671.990 | 649.958 | 1.0339× | 605.414 | 0.9315× |

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
| per-tensor | fused | 1 | 0.046528 | 1.893062 |
| per-tensor | fused | 2 | 0.052497 | 3.355667 |
| per-tensor | fused | 4 | 0.076688 | 4.594190 |
| per-tensor | fused | 8 | 0.099504 | 7.081520 |
| per-tensor | fused | 16 | 0.107745 | 13.079829 |
| per-tensor | fused | 32 | 0.155937 | 18.075071 |
| per-tensor | fused | 64 | 0.204993 | 27.499138 |
| per-tensor | fused | 128 | 0.211793 | 53.232461 |
| per-tensor | fused | 256 | 0.217650 | 103.600176 |
| per-tensor | fused | 512 | 0.224290 | 201.066283 |
| per-tensor | fused | 1024 | 0.238370 | 378.379466 |
| per-tensor | fused | 2048 | 0.296963 | 607.444788 |
| per-tensor | fused | 4096 | 0.407684 | 884.943370 |
| per-tensor | fused | 8192 | 0.766759 | 941.044716 |
| per-tensor | fused | 16384 | 1.504655 | 959.096279 |

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
<summary>baseline/per-tensor-fused.log</summary>

SHA-256: `79e4c3348f9074de7445e39f4acd643ba34691658ec75e077837573a701f877a`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A16 | 1 | 0.046528 | 1.893062 |
| CuteDSL W4A4 | 1 | 0.032753 | 2.689272 |
| CuteDSL W4A16 | 2 | 0.052497 | 3.355667 |
| CuteDSL W4A4 | 2 | 0.038256 | 4.604728 |
| CuteDSL W4A16 | 4 | 0.076688 | 4.594190 |
| CuteDSL W4A4 | 4 | 0.054224 | 6.497460 |
| CuteDSL W4A16 | 8 | 0.099504 | 7.081520 |
| CuteDSL W4A4 | 8 | 0.070640 | 9.975128 |
| CuteDSL W4A16 | 16 | 0.107745 | 13.079829 |
| CuteDSL W4A4 | 16 | 0.079984 | 17.619601 |
| CuteDSL W4A16 | 32 | 0.155937 | 18.075071 |
| CuteDSL W4A4 | 32 | 0.110401 | 25.530315 |
| CuteDSL W4A16 | 64 | 0.204993 | 27.499138 |
| CuteDSL W4A4 | 64 | 0.143409 | 39.308028 |
| CuteDSL W4A16 | 128 | 0.211793 | 53.232461 |
| CuteDSL W4A4 | 128 | 0.147585 | 76.391836 |
| CuteDSL W4A16 | 256 | 0.217650 | 103.600176 |
| CuteDSL W4A4 | 256 | 0.155617 | 144.897912 |
| CuteDSL W4A16 | 512 | 0.224290 | 201.066283 |
| CuteDSL W4A4 | 512 | 0.157185 | 286.904963 |
| CuteDSL W4A16 | 1024 | 0.238370 | 378.379466 |
| CuteDSL W4A4 | 1024 | 0.162897 | 553.689222 |
| CuteDSL W4A16 | 2048 | 0.296963 | 607.444788 |
| CuteDSL W4A4 | 2048 | 0.179377 | 1005.636863 |
| CuteDSL W4A16 | 4096 | 0.407684 | 884.943370 |
| CuteDSL W4A4 | 4096 | 0.211074 | 1709.245349 |
| CuteDSL W4A16 | 8192 | 0.766759 | 941.044716 |
| CuteDSL W4A4 | 8192 | 0.293586 | 2457.723723 |
| CuteDSL W4A16 | 16384 | 1.504655 | 959.096279 |
| CuteDSL W4A4 | 16384 | 0.441908 | 3265.632239 |

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
<summary>baseline/per-token-fused.log</summary>

SHA-256: `99bef320d28ef4d1e455fd1061cf105a2b3495d5589ed5ecc5576d4ed33c0146`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.039201 | 2.246891 |
| CuteDSL W4A4 | 2 | 0.049889 | 3.531054 |
| CuteDSL W4A4 | 4 | 0.068913 | 5.112593 |
| CuteDSL W4A4 | 8 | 0.085520 | 8.239464 |
| CuteDSL W4A4 | 16 | 0.094080 | 14.979657 |
| CuteDSL W4A4 | 32 | 0.127713 | 22.069667 |
| CuteDSL W4A4 | 64 | 0.161218 | 34.966084 |
| CuteDSL W4A4 | 128 | 0.166961 | 67.526281 |
| CuteDSL W4A4 | 256 | 0.174482 | 129.231915 |
| CuteDSL W4A4 | 512 | 0.178178 | 253.101711 |
| CuteDSL W4A4 | 1024 | 0.188754 | 477.841805 |
| CuteDSL W4A4 | 2048 | 0.209186 | 862.336038 |
| CuteDSL W4A4 | 4096 | 0.265603 | 1358.332748 |
| CuteDSL W4A4 | 8192 | 0.368916 | 1955.880156 |
| CuteDSL W4A4 | 16384 | 0.605414 | 2383.674978 |

</details>

<details>
<summary>combined-v2/per-tensor-unfused.log</summary>

SHA-256: `1cefc632c0d80ffcbd17e52d588d4a2c8f2f3013457d8c87cab9a0b37edace45`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.030176 | 2.918889 |
| CuteDSL W4A4 | 2 | 0.039889 | 4.416330 |
| CuteDSL W4A4 | 4 | 0.055872 | 6.305869 |
| CuteDSL W4A4 | 8 | 0.072576 | 9.709037 |
| CuteDSL W4A4 | 16 | 0.081889 | 17.209712 |
| CuteDSL W4A4 | 32 | 0.112912 | 24.962447 |
| CuteDSL W4A4 | 64 | 0.145825 | 38.656782 |
| CuteDSL W4A4 | 128 | 0.150033 | 75.145396 |
| CuteDSL W4A4 | 256 | 0.158193 | 142.537957 |
| CuteDSL W4A4 | 512 | 0.160754 | 280.535207 |
| CuteDSL W4A4 | 1024 | 0.168385 | 535.643396 |
| CuteDSL W4A4 | 2048 | 0.178482 | 1010.685289 |
| CuteDSL W4A4 | 4096 | 0.214226 | 1684.096482 |
| CuteDSL W4A4 | 8192 | 0.305522 | 2361.706603 |
| CuteDSL W4A4 | 16384 | 0.480772 | 3001.646333 |

</details>

<details>
<summary>combined-v2/per-token-unfused.log</summary>

SHA-256: `1ce73c219089a2f8b21bae4ca7fccdae9d5146bafeea4c4d71f709328cedde07`

| Backend | Tokens | Latency (ms) | TFLOPS |
| --- | ---: | ---: | ---: |
| CuteDSL W4A4 | 1 | 0.040192 | 2.191490 |
| CuteDSL W4A4 | 2 | 0.050400 | 3.495253 |
| CuteDSL W4A4 | 4 | 0.070897 | 4.969519 |
| CuteDSL W4A4 | 8 | 0.086337 | 8.161542 |
| CuteDSL W4A4 | 16 | 0.095873 | 14.699510 |
| CuteDSL W4A4 | 32 | 0.129154 | 21.823345 |
| CuteDSL W4A4 | 64 | 0.163554 | 34.466670 |
| CuteDSL W4A4 | 128 | 0.169650 | 66.456169 |
| CuteDSL W4A4 | 256 | 0.177441 | 127.076483 |
| CuteDSL W4A4 | 512 | 0.182209 | 247.501676 |
| CuteDSL W4A4 | 1024 | 0.194689 | 463.273802 |
| CuteDSL W4A4 | 2048 | 0.215697 | 836.303742 |
| CuteDSL W4A4 | 4096 | 0.274339 | 1315.080650 |
| CuteDSL W4A4 | 8192 | 0.391636 | 1842.413432 |
| CuteDSL W4A4 | 16384 | 0.649958 | 2220.311176 |

</details>
