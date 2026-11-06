# Uniform benchmark rerun

Validated 12 sweeps / 180 native rows on `GPU-e32ead05-f360-d139-903a-f38cf17eecb8`.

## Unfused optimization speedup

Ratio = base unfused / head unfused; greater than1 means the denominator is faster.

| Tokens | W4A4 per-tensor | W4A4 per-token | W4A16 |
| ---: | ---: | ---: | ---: |
| 1 | 1.1118× | 1.0745× | 1.0783× |
| 2 | 1.1396× | 1.0644× | 1.0519× |
| 4 | 1.0606× | 1.0414× | 1.0356× |
| 8 | 1.0432× | 1.0353× | 1.0228× |
| 16 | 1.0428× | 1.0383× | 1.0363× |
| 32 | 1.0409× | 1.0366× | 1.0209× |
| 64 | 1.0421× | 1.0347× | 1.0198× |
| 128 | 1.0400× | 1.0350× | 1.0203× |
| 256 | 1.0403× | 1.0355× | 1.0202× |
| 512 | 1.0371× | 1.0321× | 1.0122× |
| 1024 | 1.0244× | 1.0223× | 1.0065× |
| 2048 | 1.0390× | 1.0321× | 1.0211× |
| 4096 | 1.0473× | 1.0374× | 1.0201× |
| 8192 | 1.0468× | 1.0394× | 1.0194× |
| 16384 | 1.0472× | 1.0349× | 1.0506× |

## Head unfused versus fused

Ratio = head fused / head unfused; greater than1 means the denominator is faster.

| Tokens | W4A4 per-tensor | W4A4 per-token | W4A16 |
| ---: | ---: | ---: | ---: |
| 1 | 0.9465× | 0.9576× | 1.0757× |
| 2 | 1.0249× | 1.0931× | 1.0619× |
| 4 | 0.9738× | 0.9699× | 1.0601× |
| 8 | 0.9772× | 0.9865× | 1.0536× |
| 16 | 0.9755× | 0.9777× | 1.0298× |
| 32 | 0.9802× | 0.9867× | 1.0267× |
| 64 | 0.9832× | 0.9822× | 1.0226× |
| 128 | 0.9823× | 0.9865× | 1.0330× |
| 256 | 0.9791× | 0.9849× | 1.0241× |
| 512 | 0.9766× | 0.9780× | 1.0143× |
| 1024 | 0.9676× | 0.9702× | 1.0169× |
| 2048 | 0.9801× | 0.9688× | 1.0710× |
| 4096 | 0.9834× | 0.9653× | 1.0533× |
| 8192 | 0.9525× | 0.9395× | 1.1070× |
| 16384 | 0.9205× | 0.9329× | 1.0907× |

## Fused control speedup

Ratio = base fused / head fused; greater than1 means the denominator is faster.

| Tokens | W4A4 per-tensor | W4A4 per-token | W4A16 |
| ---: | ---: | ---: | ---: |
| 1 | 0.9989× | 0.9996× | 1.0024× |
| 2 | 0.9373× | 0.9048× | 0.9924× |
| 4 | 1.0029× | 0.9991× | 0.9853× |
| 8 | 0.9960× | 1.0041× | 1.0125× |
| 16 | 0.9996× | 1.0000× | 1.0000× |
| 32 | 1.0009× | 1.0002× | 1.0009× |
| 64 | 1.0000× | 0.9998× | 0.9967× |
| 128 | 0.9988× | 0.9993× | 0.9998× |
| 256 | 1.0003× | 1.0004× | 1.0009× |
| 512 | 0.9999× | 1.0003× | 0.9989× |
| 1024 | 0.9989× | 1.0007× | 0.9992× |
| 2048 | 0.9988× | 0.9998× | 1.0009× |
| 4096 | 1.0001× | 0.9996× | 1.0004× |
| 8192 | 1.0000× | 0.9997× | 1.0141× |
| 16384 | 1.0018× | 0.9998× | 1.0199× |

## Unfused regression points

No measured unfused regression point in this single sweep.

## Complete native benchmark rows

```csv
arm,mode,finalize,backend,tokens,latency_ms,tflops
base,w4a4-per-tensor,fused,CuteDSL W4A4,1,0.028544,3.085776
base,w4a4-per-tensor,fused,CuteDSL W4A4,2,0.038304,4.599018
base,w4a4-per-tensor,fused,CuteDSL W4A4,4,0.054945,6.412317
base,w4a4-per-tensor,fused,CuteDSL W4A4,8,0.071073,9.914357
base,w4a4-per-tensor,fused,CuteDSL W4A4,16,0.080193,17.573680
base,w4a4-per-tensor,fused,CuteDSL W4A4,32,0.111265,25.332066
base,w4a4-per-tensor,fused,CuteDSL W4A4,64,0.143969,39.155267
base,w4a4-per-tensor,fused,CuteDSL W4A4,128,0.147025,76.682803
base,w4a4-per-tensor,fused,CuteDSL W4A4,256,0.155569,144.942153
base,w4a4-per-tensor,fused,CuteDSL W4A4,512,0.157249,286.787281
base,w4a4-per-tensor,fused,CuteDSL W4A4,1024,0.163009,553.310491
base,w4a4-per-tensor,fused,CuteDSL W4A4,2048,0.175121,1030.079924
base,w4a4-per-tensor,fused,CuteDSL W4A4,4096,0.211906,1702.538409
base,w4a4-per-tensor,fused,CuteDSL W4A4,8192,0.293346,2459.738690
base,w4a4-per-tensor,fused,CuteDSL W4A4,16384,0.445395,3240.061948
base,w4a4-per-tensor,unfused,CuteDSL W4A4,1,0.033569,2.623900
base,w4a4-per-tensor,unfused,CuteDSL W4A4,2,0.045440,3.876777
base,w4a4-per-tensor,unfused,CuteDSL W4A4,4,0.059664,5.905045
base,w4a4-per-tensor,unfused,CuteDSL W4A4,8,0.076176,9.250198
base,w4a4-per-tensor,unfused,CuteDSL W4A4,16,0.085761,16.432812
base,w4a4-per-tensor,unfused,CuteDSL W4A4,32,0.118049,23.876291
base,w4a4-per-tensor,unfused,CuteDSL W4A4,64,0.152593,36.942354
base,w4a4-per-tensor,unfused,CuteDSL W4A4,128,0.155857,72.337394
base,w4a4-per-tensor,unfused,CuteDSL W4A4,256,0.165234,136.464932
base,w4a4-per-tensor,unfused,CuteDSL W4A4,512,0.167009,270.028302
base,w4a4-per-tensor,unfused,CuteDSL W4A4,1024,0.172754,522.098326
base,w4a4-per-tensor,unfused,CuteDSL W4A4,2048,0.185858,970.574911
base,w4a4-per-tensor,unfused,CuteDSL W4A4,4096,0.225650,1598.835599
base,w4a4-per-tensor,unfused,CuteDSL W4A4,8192,0.322371,2238.273622
base,w4a4-per-tensor,unfused,CuteDSL W4A4,16384,0.505780,2853.237451
head,w4a4-per-tensor,fused,CuteDSL W4A4,1,0.028576,3.082320
head,w4a4-per-tensor,fused,CuteDSL W4A4,2,0.040864,4.310851
head,w4a4-per-tensor,fused,CuteDSL W4A4,4,0.054784,6.431103
head,w4a4-per-tensor,fused,CuteDSL W4A4,8,0.071361,9.874344
head,w4a4-per-tensor,fused,CuteDSL W4A4,16,0.080225,17.566671
head,w4a4-per-tensor,fused,CuteDSL W4A4,32,0.111169,25.354055
head,w4a4-per-tensor,fused,CuteDSL W4A4,64,0.143969,39.155267
head,w4a4-per-tensor,fused,CuteDSL W4A4,128,0.147201,76.591118
head,w4a4-per-tensor,fused,CuteDSL W4A4,256,0.155521,144.986888
head,w4a4-per-tensor,fused,CuteDSL W4A4,512,0.157266,286.758104
head,w4a4-per-tensor,fused,CuteDSL W4A4,1024,0.163185,552.712034
head,w4a4-per-tensor,fused,CuteDSL W4A4,2048,0.175329,1028.857898
head,w4a4-per-tensor,fused,CuteDSL W4A4,4096,0.211874,1702.791531
head,w4a4-per-tensor,fused,CuteDSL W4A4,8192,0.293346,2459.738690
head,w4a4-per-tensor,fused,CuteDSL W4A4,16384,0.444579,3246.012545
head,w4a4-per-tensor,unfused,CuteDSL W4A4,1,0.030192,2.917342
head,w4a4-per-tensor,unfused,CuteDSL W4A4,2,0.039872,4.418157
head,w4a4-per-tensor,unfused,CuteDSL W4A4,4,0.056256,6.262826
head,w4a4-per-tensor,unfused,CuteDSL W4A4,8,0.073025,9.649406
head,w4a4-per-tensor,unfused,CuteDSL W4A4,16,0.082241,17.136053
head,w4a4-per-tensor,unfused,CuteDSL W4A4,32,0.113409,24.853162
head,w4a4-per-tensor,unfused,CuteDSL W4A4,64,0.146433,38.496540
head,w4a4-per-tensor,unfused,CuteDSL W4A4,128,0.149857,75.233650
head,w4a4-per-tensor,unfused,CuteDSL W4A4,256,0.158833,141.963618
head,w4a4-per-tensor,unfused,CuteDSL W4A4,512,0.161042,280.034380
head,w4a4-per-tensor,unfused,CuteDSL W4A4,1024,0.168642,534.827108
head,w4a4-per-tensor,unfused,CuteDSL W4A4,2048,0.178881,1008.428097
head,w4a4-per-tensor,unfused,CuteDSL W4A4,4096,0.215458,1674.466731
head,w4a4-per-tensor,unfused,CuteDSL W4A4,8192,0.307971,2342.933839
head,w4a4-per-tensor,unfused,CuteDSL W4A4,16384,0.482980,2987.927060
base,w4a4-per-token,fused,CuteDSL W4A4,1,0.039057,2.255204
base,w4a4-per-token,fused,CuteDSL W4A4,2,0.050657,3.477521
base,w4a4-per-token,fused,CuteDSL W4A4,4,0.068993,5.106627
base,w4a4-per-token,fused,CuteDSL W4A4,8,0.085825,8.210231
base,w4a4-per-token,fused,CuteDSL W4A4,16,0.093985,14.994799
base,w4a4-per-token,fused,CuteDSL W4A4,32,0.128192,21.987030
base,w4a4-per-token,fused,CuteDSL W4A4,64,0.161425,34.921137
base,w4a4-per-token,fused,CuteDSL W4A4,128,0.166849,67.571811
base,w4a4-per-token,fused,CuteDSL W4A4,256,0.175217,128.689077
base,w4a4-per-token,fused,CuteDSL W4A4,512,0.178801,252.219823
base,w4a4-per-token,fused,CuteDSL W4A4,1024,0.189474,476.026005
base,w4a4-per-token,fused,CuteDSL W4A4,2048,0.209697,860.232604
base,w4a4-per-token,fused,CuteDSL W4A4,4096,0.265282,1359.973812
base,w4a4-per-token,fused,CuteDSL W4A4,8192,0.368930,1955.800634
base,w4a4-per-token,fused,CuteDSL W4A4,16384,0.607012,2377.395872
base,w4a4-per-token,unfused,CuteDSL W4A4,1,0.043840,2.009133
base,w4a4-per-token,unfused,CuteDSL W4A4,2,0.054512,3.231566
base,w4a4-per-token,unfused,CuteDSL W4A4,4,0.074145,4.751791
base,w4a4-per-token,unfused,CuteDSL W4A4,8,0.089697,7.855815
base,w4a4-per-token,unfused,CuteDSL W4A4,16,0.099808,14.119972
base,w4a4-per-token,unfused,CuteDSL W4A4,32,0.134640,20.934060
base,w4a4-per-token,unfused,CuteDSL W4A4,64,0.170097,33.140764
base,w4a4-per-token,unfused,CuteDSL W4A4,128,0.175170,64.361986
base,w4a4-per-token,unfused,CuteDSL W4A4,256,0.184161,122.439154
base,w4a4-per-token,unfused,CuteDSL W4A4,512,0.188642,239.062755
base,w4a4-per-token,unfused,CuteDSL W4A4,1024,0.199522,452.051970
base,w4a4-per-token,unfused,CuteDSL W4A4,2048,0.223457,807.261454
base,w4a4-per-token,unfused,CuteDSL W4A4,4096,0.285202,1264.988509
base,w4a4-per-token,unfused,CuteDSL W4A4,8192,0.408259,1767.393997
base,w4a4-per-token,unfused,CuteDSL W4A4,16384,0.673509,2142.672201
head,w4a4-per-token,fused,CuteDSL W4A4,1,0.039072,2.254310
head,w4a4-per-token,fused,CuteDSL W4A4,2,0.055984,3.146627
head,w4a4-per-token,fused,CuteDSL W4A4,4,0.069056,5.101968
head,w4a4-per-token,fused,CuteDSL W4A4,8,0.085473,8.244043
head,w4a4-per-token,fused,CuteDSL W4A4,16,0.093985,14.994799
head,w4a4-per-token,fused,CuteDSL W4A4,32,0.128161,21.992434
head,w4a4-per-token,fused,CuteDSL W4A4,64,0.161457,34.914216
head,w4a4-per-token,fused,CuteDSL W4A4,128,0.166961,67.526281
head,w4a4-per-token,fused,CuteDSL W4A4,256,0.175154,128.735731
head,w4a4-per-token,fused,CuteDSL W4A4,512,0.178753,252.287551
head,w4a4-per-token,fused,CuteDSL W4A4,1024,0.189345,476.349062
head,w4a4-per-token,fused,CuteDSL W4A4,2048,0.209746,860.035741
head,w4a4-per-token,fused,CuteDSL W4A4,4096,0.265378,1359.484407
head,w4a4-per-token,fused,CuteDSL W4A4,8192,0.369027,1955.291844
head,w4a4-per-token,fused,CuteDSL W4A4,16384,0.607124,2376.959256
head,w4a4-per-token,unfused,CuteDSL W4A4,1,0.040800,2.158833
head,w4a4-per-token,unfused,CuteDSL W4A4,2,0.051216,3.439532
head,w4a4-per-token,unfused,CuteDSL W4A4,4,0.071200,4.948336
head,w4a4-per-token,unfused,CuteDSL W4A4,8,0.086640,8.132953
head,w4a4-per-token,unfused,CuteDSL W4A4,16,0.096129,14.660440
head,w4a4-per-token,unfused,CuteDSL W4A4,32,0.129889,21.699854
head,w4a4-per-token,unfused,CuteDSL W4A4,64,0.164386,34.292225
head,w4a4-per-token,unfused,CuteDSL W4A4,128,0.169249,66.613427
head,w4a4-per-token,unfused,CuteDSL W4A4,256,0.177841,126.790663
head,w4a4-per-token,unfused,CuteDSL W4A4,512,0.182770,246.743339
head,w4a4-per-token,unfused,CuteDSL W4A4,1024,0.195169,462.134423
head,w4a4-per-token,unfused,CuteDSL W4A4,2048,0.216498,833.213439
head,w4a4-per-token,unfused,CuteDSL W4A4,4096,0.274914,1312.330071
head,w4a4-per-token,unfused,CuteDSL W4A4,8192,0.392771,1837.087019
head,w4a4-per-token,unfused,CuteDSL W4A4,16384,0.650789,2217.476035
base,w4a16,fused,CuteDSL W4A16,1,0.045824,1.922145
base,w4a16,fused,CuteDSL W4A16,2,0.052320,3.366955
base,w4a16,fused,CuteDSL W4A16,4,0.076145,4.627012
base,w4a16,fused,CuteDSL W4A16,8,0.098752,7.135445
base,w4a16,fused,CuteDSL W4A16,16,0.106208,13.269052
base,w4a16,fused,CuteDSL W4A16,32,0.155553,18.119691
base,w4a16,fused,CuteDSL W4A16,64,0.205249,27.464840
base,w4a16,fused,CuteDSL W4A16,128,0.210881,53.462802
base,w4a16,fused,CuteDSL W4A16,256,0.216929,103.944269
base,w4a16,fused,CuteDSL W4A16,512,0.222818,202.394585
base,w4a16,fused,CuteDSL W4A16,1024,0.237138,380.346058
base,w4a16,fused,CuteDSL W4A16,2048,0.290403,621.167609
base,w4a16,fused,CuteDSL W4A16,4096,0.395891,911.304508
base,w4a16,fused,CuteDSL W4A16,8192,0.755494,955.076421
base,w4a16,fused,CuteDSL W4A16,16384,1.483531,972.752852
base,w4a16,unfused,CuteDSL W4A16,1,0.045825,1.922103
base,w4a16,unfused,CuteDSL W4A16,2,0.052224,3.373176
base,w4a16,unfused,CuteDSL W4A16,4,0.075489,4.667221
base,w4a16,unfused,CuteDSL W4A16,8,0.094688,7.441696
base,w4a16,unfused,CuteDSL W4A16,16,0.106880,13.185686
base,w4a16,unfused,CuteDSL W4A16,32,0.154529,18.239763
base,w4a16,unfused,CuteDSL W4A16,64,0.205345,27.452066
base,w4a16,unfused,CuteDSL W4A16,128,0.208321,54.119792
base,w4a16,unfused,CuteDSL W4A16,256,0.215906,104.437016
base,w4a16,unfused,CuteDSL W4A16,512,0.222625,202.570047
base,w4a16,unfused,CuteDSL W4A16,1024,0.234898,383.972248
base,w4a16,unfused,CuteDSL W4A16,2048,0.276626,652.102935
base,w4a16,unfused,CuteDSL W4A16,4096,0.383219,941.438845
base,w4a16,unfused,CuteDSL W4A16,8192,0.685990,1051.844825
base,w4a16,unfused,CuteDSL W4A16,16384,1.401035,1030.030664
head,w4a16,fused,CuteDSL W4A16,1,0.045713,1.926834
head,w4a16,fused,CuteDSL W4A16,2,0.052720,3.341441
head,w4a16,fused,CuteDSL W4A16,4,0.077280,4.559026
head,w4a16,fused,CuteDSL W4A16,8,0.097537,7.224367
head,w4a16,fused,CuteDSL W4A16,16,0.106209,13.268990
head,w4a16,fused,CuteDSL W4A16,32,0.155409,18.136480
head,w4a16,fused,CuteDSL W4A16,64,0.205921,27.375278
head,w4a16,fused,CuteDSL W4A16,128,0.210913,53.454564
head,w4a16,fused,CuteDSL W4A16,256,0.216737,104.036350
head,w4a16,fused,CuteDSL W4A16,512,0.223073,202.163223
head,w4a16,fused,CuteDSL W4A16,1024,0.237329,380.038357
head,w4a16,fused,CuteDSL W4A16,2048,0.290130,621.751030
head,w4a16,fused,CuteDSL W4A16,4096,0.395715,911.709824
head,w4a16,fused,CuteDSL W4A16,8192,0.744965,968.575041
head,w4a16,fused,CuteDSL W4A16,16384,1.454523,992.152762
head,w4a16,unfused,CuteDSL W4A16,1,0.042496,2.072650
head,w4a16,unfused,CuteDSL W4A16,2,0.049648,3.548159
head,w4a16,unfused,CuteDSL W4A16,4,0.072897,4.833142
head,w4a16,unfused,CuteDSL W4A16,8,0.092577,7.611468
head,w4a16,unfused,CuteDSL W4A16,16,0.103137,13.664281
head,w4a16,unfused,CuteDSL W4A16,32,0.151361,18.621523
head,w4a16,unfused,CuteDSL W4A16,64,0.201361,27.995215
head,w4a16,unfused,CuteDSL W4A16,128,0.204177,55.218213
head,w4a16,unfused,CuteDSL W4A16,256,0.211634,106.545411
head,w4a16,unfused,CuteDSL W4A16,512,0.219938,205.045327
head,w4a16,unfused,CuteDSL W4A16,1024,0.233377,386.474731
head,w4a16,unfused,CuteDSL W4A16,2048,0.270898,665.892548
head,w4a16,unfused,CuteDSL W4A16,4096,0.375683,960.324883
head,w4a16,unfused,CuteDSL W4A16,8192,0.672949,1072.227622
head,w4a16,unfused,CuteDSL W4A16,16384,1.333562,1082.145765
```

## Limits

- One forward sweep per configuration; no statistical uncertainty estimate.
- Autotuning may select different tactics between arms; this measures the complete selected path.
- Simulated EP8 has no inter-GPU all-to-all communication.
- TFLOPS is the native uniform-local-routing workload estimate.
