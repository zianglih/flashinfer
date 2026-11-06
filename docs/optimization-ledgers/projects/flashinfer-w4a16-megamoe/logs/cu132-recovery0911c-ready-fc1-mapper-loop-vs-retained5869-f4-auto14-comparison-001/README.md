# Mapper-loop versus selected whole BEFORE

Compare one explicitly selected whole BEFORE (retained2e3b or original07d7) with mapper-loop3071 on hu-pdx-59; source_ids and arm pins identify the pair. Each full1–8192 run uses identical public four F4 candidates, fresh knob caches, separate ordered FP32 reduction and unchanged hot scorer/100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement or statistical-confidence claim. The two prior diagnostics passed their oracles but observed zero reorders; no diagnostic was repeated for the mapper variant. Timing characterization only; promotion remains held.

8–8192: Mapper/before geometric ratio 1.014702223 (+1.470222%); Mapper lower on 2/11 rows.
All14: Mapper/before geometric ratio 1.015721440 (+1.572144%); Mapper lower on 3/14 rows.

| Tokens | Before cold ms | Mapper cold ms | Mapper/before change | Before selected | Mapper selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.089169 | 0.085297 | -4.342% | N64/F4/epi | N64/F4/epi |
| 2 | 0.098321 | 0.104545 | +6.330% | N64/F4/epi | N64/F4/epi |
| 4 | 0.115105 | 0.119905 | +4.170% | N64/F4/epi | N64/F4/epi |
| 8 | 0.134592 | 0.141777 | +5.338% | N64/F4/epi | N64/F4/epi |
| 16 | 0.152177 | 0.154721 | +1.672% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180081 | 0.185553 | +3.039% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203393 | 0.203250 | -0.070% | N64/F4/epi | N64/F4/epi |
| 128 | 0.206145 | 0.205265 | -0.427% | N64/F4/epi | N64/F4/epi |
| 256 | 0.212002 | 0.212946 | +0.445% | N64/F4/epi | N64/F4/epi |
| 512 | 0.211650 | 0.220593 | +4.225% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.235042 | 0.236178 | +0.483% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.311283 | 0.311890 | +0.195% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468500 | 0.470676 | +0.464% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.796709 | 0.804536 | +0.982% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.2 | +0.154% |
| 2 | 83.6 | 85.5 | +2.273% |
| 4 | 93.8 | 95.9 | +2.239% |
| 8 | 114.1 | 118.4 | +3.769% |
| 16 | 130.7 | 132.8 | +1.607% |
| 32 | 160.2 | 163.4 | +1.998% |
| 64 | 184.9 | 188.0 | +1.677% |
| 128 | 190.8 | 194.2 | +1.782% |
| 256 | 194.2 | 200.4 | +3.193% |
| 512 | 202.3 | 208.5 | +3.065% |
| 1024 | 220.8 | 224.9 | +1.857% |
| 2048 | 296.5 | 300.6 | +1.383% |
| 4096 | 466.2 | 466.4 | +0.043% |
| 8192 | 784.4 | 790.1 | +0.727% |

## N128 / reuse_dispatch_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 75.3 | 76.9 | +2.125% |
| 2 | 89.5 | 91.7 | +2.458% |
| 4 | 98.9 | 103.6 | +4.752% |
| 8 | 120.5 | 124.7 | +3.485% |
| 16 | 136.8 | 139.1 | +1.681% |
| 32 | 167.6 | 169.6 | +1.193% |
| 64 | 194.1 | 198.0 | +2.009% |
| 128 | 200.4 | 204.3 | +1.946% |
| 256 | 209.5 | 214.7 | +2.482% |
| 512 | 218.7 | 226.9 | +3.749% |
| 1024 | 243.3 | 249.3 | +2.466% |
| 2048 | 292.1 | 291.5 | -0.205% |
| 4096 | 446.5 | 450.9 | +0.985% |
| 8192 | 743.8 | 748.8 | +0.672% |

## N64 / epi_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 63.2 | 63.7 | +0.791% |
| 2 | 81.5 | 82.4 | +1.104% |
| 4 | 91.7 | 91.8 | +0.109% |
| 8 | 110.2 | 114.2 | +3.630% |
| 16 | 122.5 | 124.6 | +1.714% |
| 32 | 149.2 | 152.7 | +2.346% |
| 64 | 172.5 | 173.7 | +0.696% |
| 128 | 179.8 | 180.8 | +0.556% |
| 256 | 181.9 | 183.9 | +1.100% |
| 512 | 188.0 | 190.8 | +1.489% |
| 1024 | 210.4 | 210.6 | +0.095% |
| 2048 | 315.0 | 318.7 | +1.175% |
| 4096 | 505.9 | 511.2 | +1.048% |
| 8192 | 892.7 | 903.9 | +1.255% |

## N64 / reuse_dispatch_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 73.4 | 75.3 | +2.589% |
| 2 | 87.6 | 88.7 | +1.256% |
| 4 | 97.8 | 97.9 | +0.102% |
| 8 | 116.4 | 119.2 | +2.405% |
| 16 | 128.7 | 130.7 | +1.554% |
| 32 | 158.3 | 159.4 | +0.695% |
| 64 | 182.5 | 184.0 | +0.822% |
| 128 | 189.9 | 192.1 | +1.159% |
| 256 | 196.2 | 202.1 | +3.007% |
| 512 | 205.5 | 210.4 | +2.384% |
| 1024 | 229.9 | 232.4 | +1.087% |
| 2048 | 329.3 | 330.4 | +0.334% |
| 4096 | 504.4 | 512.2 | +1.546% |
| 8192 | 866.9 | 891.5 | +2.838% |
