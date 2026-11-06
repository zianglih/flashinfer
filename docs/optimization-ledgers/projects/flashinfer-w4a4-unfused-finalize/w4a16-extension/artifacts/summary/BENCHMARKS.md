**W4A16 speedup:** baseline unfused / candidate unfused. The second ratio is baseline fused / candidate unfused. Values above 1 favor the candidate unfused path. Each entry is derived from that configuration's native median in one forward sweep.

| Tokens | Unfused speedup | Fused/candidate-unfused |
|---:|---:|---:|
| 1 | 1.0814× | 1.0710× |
| 2 | 1.0573× | 1.0307× |
| 4 | 1.0296× | 1.0440× |
| 8 | 1.0266× | 1.0604× |
| 16 | 1.0271× | 1.0435× |
| 32 | 1.0184× | 1.0242× |
| 64 | 1.0202× | 1.0232× |
| 128 | 1.0163× | 1.0316× |
| 256 | 1.0203× | 1.0252× |
| 512 | 1.0116× | 1.0151× |
| 1024 | 1.0066× | 1.0163× |
| 2048 | 1.0217× | 1.0711× |
| 4096 | 1.0257× | 1.0578× |
| 8192 | 0.9880× | 1.0861× |
| 16384 | 1.0361× | 1.1511× |

<details>
<summary>Complete W4A16 native benchmark CSV (all 45 rows)</summary>

```csv
arm,finalize,backend,tokens,latency_ms,tflops
baseline,unfused,CuteDSL W4A16,1,0.046337,1.900886
baseline,unfused,CuteDSL W4A16,2,0.053472,3.294418
baseline,unfused,CuteDSL W4A16,4,0.075552,4.663299
baseline,unfused,CuteDSL W4A16,8,0.094928,7.422882
baseline,unfused,CuteDSL W4A16,16,0.106561,13.225159
baseline,unfused,CuteDSL W4A16,32,0.154354,18.260501
baseline,unfused,CuteDSL W4A16,64,0.205090,27.486199
baseline,unfused,CuteDSL W4A16,128,0.208146,54.165293
baseline,unfused,CuteDSL W4A16,256,0.215922,104.429277
baseline,unfused,CuteDSL W4A16,512,0.222386,202.787750
baseline,unfused,CuteDSL W4A16,1024,0.234866,384.024564
baseline,unfused,CuteDSL W4A16,2048,0.276355,652.743583
baseline,unfused,CuteDSL W4A16,4096,0.382915,942.185033
baseline,unfused,CuteDSL W4A16,8192,0.675767,1067.756351
baseline,unfused,CuteDSL W4A16,16384,1.329309,1085.608804
candidate,unfused,CuteDSL W4A16,1,0.042848,2.055624
candidate,unfused,CuteDSL W4A16,2,0.050576,3.483056
candidate,unfused,CuteDSL W4A16,4,0.073377,4.801525
candidate,unfused,CuteDSL W4A16,8,0.092465,7.620646
candidate,unfused,CuteDSL W4A16,16,0.103745,13.584136
candidate,unfused,CuteDSL W4A16,32,0.151569,18.595968
candidate,unfused,CuteDSL W4A16,64,0.201026,28.041868
candidate,unfused,CuteDSL W4A16,128,0.204802,55.049702
candidate,unfused,CuteDSL W4A16,256,0.211618,106.553467
candidate,unfused,CuteDSL W4A16,512,0.219841,205.135332
candidate,unfused,CuteDSL W4A16,1024,0.233330,386.551750
candidate,unfused,CuteDSL W4A16,2048,0.270498,666.874775
candidate,unfused,CuteDSL W4A16,4096,0.373316,966.413805
candidate,unfused,CuteDSL W4A16,8192,0.683990,1054.919671
candidate,unfused,CuteDSL W4A16,16384,1.283037,1124.760246
baseline,fused,CuteDSL W4A16,1,0.045889,1.919423
baseline,fused,CuteDSL W4A16,2,0.052128,3.379389
baseline,fused,CuteDSL W4A16,4,0.076609,4.598958
baseline,fused,CuteDSL W4A16,8,0.098048,7.186679
baseline,fused,CuteDSL W4A16,16,0.108257,13.017968
baseline,fused,CuteDSL W4A16,32,0.155234,18.156926
baseline,fused,CuteDSL W4A16,64,0.205697,27.405022
baseline,fused,CuteDSL W4A16,128,0.211282,53.361333
baseline,fused,CuteDSL W4A16,256,0.216946,103.936124
baseline,fused,CuteDSL W4A16,512,0.223154,202.089842
baseline,fused,CuteDSL W4A16,1024,0.237123,380.370118
baseline,fused,CuteDSL W4A16,2048,0.289731,622.608343
baseline,fused,CuteDSL W4A16,4096,0.394884,913.627283
baseline,fused,CuteDSL W4A16,8192,0.742903,971.263416
baseline,fused,CuteDSL W4A16,16384,1.476862,977.145469
```

</details>
