# Mapper-loop versus selected whole BEFORE

Compare one explicitly selected whole BEFORE (retained2e3b or original07d7) with mapper-loop3071 on hu-pdx-59; source_ids and arm pins identify the pair. Each full1–8192 run uses identical public four F4 candidates, fresh knob caches, separate ordered FP32 reduction and unchanged hot scorer/100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement or statistical-confidence claim. The two prior diagnostics passed their oracles but observed zero reorders; no diagnostic was repeated for the mapper variant. Timing characterization only; promotion remains held.

8–8192: Mapper/before geometric ratio 0.993944762 (-0.605524%); Mapper lower on 6/11 rows.
All14: Mapper/before geometric ratio 0.994241004 (-0.575900%); Mapper lower on 8/14 rows.

| Tokens | Before cold ms | Mapper cold ms | Mapper/before change | Before selected | Mapper selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.078273 | 0.085297 | +8.974% | N64/F4/epi | N64/F4/epi |
| 2 | 0.105488 | 0.104545 | -0.894% | N64/F4/epi | N64/F4/epi |
| 4 | 0.131329 | 0.119905 | -8.699% | N64/F4/epi | N64/F4/epi |
| 8 | 0.154178 | 0.141777 | -8.043% | N64/F4/epi | N64/F4/epi |
| 16 | 0.157313 | 0.154721 | -1.648% | N64/F4/epi | N64/F4/epi |
| 32 | 0.175777 | 0.185553 | +5.562% | N64/F4/epi | N64/F4/epi |
| 64 | 0.202657 | 0.203250 | +0.293% | N64/F4/epi | N64/F4/epi |
| 128 | 0.209699 | 0.205265 | -2.114% | N64/F4/epi | N64/F4/epi |
| 256 | 0.210610 | 0.212946 | +1.109% | N64/F4/epi | N64/F4/epi |
| 512 | 0.218498 | 0.220593 | +0.959% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.233906 | 0.236178 | +0.971% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.315171 | 0.311890 | -1.041% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.472643 | 0.470676 | -0.416% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.818840 | 0.804536 | -1.747% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 65.2 | 65.2 | +0.000% |
| 2 | 85.6 | 85.5 | -0.117% |
| 4 | 95.9 | 95.9 | +0.000% |
| 8 | 118.4 | 118.4 | +0.000% |
| 16 | 134.7 | 132.8 | -1.411% |
| 32 | 163.5 | 163.4 | -0.061% |
| 64 | 190.0 | 188.0 | -1.053% |
| 128 | 196.3 | 194.2 | -1.070% |
| 256 | 202.3 | 200.4 | -0.939% |
| 512 | 210.5 | 208.5 | -0.950% |
| 1024 | 226.8 | 224.9 | -0.838% |
| 2048 | 300.5 | 300.6 | +0.033% |
| 4096 | 468.5 | 466.4 | -0.448% |
| 8192 | 791.7 | 790.1 | -0.202% |

## N128 / reuse_dispatch_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 76.9 | 76.9 | +0.000% |
| 2 | 91.8 | 91.7 | -0.109% |
| 4 | 102.9 | 103.6 | +0.680% |
| 8 | 126.6 | 124.7 | -1.501% |
| 16 | 140.9 | 139.1 | -1.278% |
| 32 | 171.6 | 169.6 | -1.166% |
| 64 | 198.2 | 198.0 | -0.101% |
| 128 | 208.5 | 204.3 | -2.014% |
| 256 | 217.3 | 214.7 | -1.197% |
| 512 | 229.0 | 226.9 | -0.917% |
| 1024 | 248.5 | 249.3 | +0.322% |
| 2048 | 292.5 | 291.5 | -0.342% |
| 4096 | 454.5 | 450.9 | -0.792% |
| 8192 | 749.6 | 748.8 | -0.107% |

## N64 / epi_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 64.9 | 63.7 | -1.849% |
| 2 | 81.5 | 82.4 | +1.104% |
| 4 | 91.6 | 91.8 | +0.218% |
| 8 | 114.2 | 114.2 | +0.000% |
| 16 | 124.5 | 124.6 | +0.080% |
| 32 | 153.2 | 152.7 | -0.326% |
| 64 | 175.6 | 173.7 | -1.082% |
| 128 | 181.9 | 180.8 | -0.605% |
| 256 | 186.0 | 183.9 | -1.129% |
| 512 | 192.2 | 190.8 | -0.728% |
| 1024 | 212.2 | 210.6 | -0.754% |
| 2048 | 319.2 | 318.7 | -0.157% |
| 4096 | 511.7 | 511.2 | -0.098% |
| 8192 | 901.9 | 903.9 | +0.222% |

## N64 / reuse_dispatch_warps

| Tokens | Before hot us | Mapper hot us | Mapper/before change |
|---:|---:|---:|---:|
| 1 | 75.2 | 75.3 | +0.133% |
| 2 | 89.9 | 88.7 | -1.335% |
| 4 | 97.9 | 97.9 | +0.000% |
| 8 | 118.4 | 119.2 | +0.676% |
| 16 | 132.5 | 130.7 | -1.358% |
| 32 | 159.4 | 159.4 | +0.000% |
| 64 | 185.9 | 184.0 | -1.022% |
| 128 | 193.2 | 192.1 | -0.569% |
| 256 | 201.0 | 202.1 | +0.547% |
| 512 | 212.6 | 210.4 | -1.035% |
| 1024 | 233.0 | 232.4 | -0.258% |
| 2048 | 329.8 | 330.4 | +0.182% |
| 4096 | 515.2 | 512.2 | -0.582% |
| 8192 | 893.4 | 891.5 | -0.213% |
