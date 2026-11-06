# FC2 pointer-pair reuse versus latest whole3da F4

Latest whole F4 source3da repeat6060 versus the pointer-pair source5e9c candidate on hu-pdx-59, each one full 1–8192 run using the same ordered public four F4 candidates and a fresh knob cache. The candidate changes only owned direct FC2 return pointer/validity reuse for adjacent stores; local reuse-return, scheduling and numerical behavior remain. Both use separate ordered FP32 reduction, the same full-forward scorer and 100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency.

8–8192: Dispatch/retained geometric ratio 0.997044018 (-0.295598%); Dispatch lower on 7/11 rows.
All14: Dispatch/retained geometric ratio 0.989023984 (-1.097602%); Dispatch lower on 9/14 rows.

| Tokens | Retained cold ms | Dispatch cold ms | Dispatch/retained change | Retained selected | Dispatch selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.084096 | 0.074672 | -11.206% | N64/F4/epi | N64/F4/epi |
| 2 | 0.100608 | 0.097392 | -3.197% | N64/F4/epi | N64/F4/epi |
| 4 | 0.116401 | 0.119873 | +2.983% | N64/F4/epi | N64/F4/epi |
| 8 | 0.138193 | 0.137410 | -0.567% | N64/F4/epi | N64/F4/epi |
| 16 | 0.146977 | 0.151217 | +2.885% | N64/F4/epi | N64/F4/epi |
| 32 | 0.179329 | 0.179298 | -0.017% | N64/F4/epi | N64/F4/epi |
| 64 | 0.202642 | 0.199826 | -1.390% | N64/F4/epi | N64/F4/epi |
| 128 | 0.209442 | 0.205074 | -2.086% | N64/F4/epi | N64/F4/epi |
| 256 | 0.208738 | 0.209858 | +0.537% | N64/F4/epi | N64/F4/epi |
| 512 | 0.213170 | 0.213874 | +0.330% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.234385 | 0.232210 | -0.928% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.310692 | 0.313059 | +0.762% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.469092 | 0.465828 | -0.696% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.790761 | 0.775094 | -1.981% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 64.1 | -1.536% |
| 2 | 83.5 | 83.6 | +0.120% |
| 4 | 93.8 | 93.8 | +0.000% |
| 8 | 114.3 | 114.2 | -0.087% |
| 16 | 130.4 | 130.5 | +0.077% |
| 32 | 159.4 | 159.4 | +0.000% |
| 64 | 183.9 | 185.1 | +0.653% |
| 128 | 190.1 | 190.0 | -0.053% |
| 256 | 196.2 | 194.2 | -1.019% |
| 512 | 200.3 | 202.4 | +1.048% |
| 1024 | 220.9 | 220.8 | -0.045% |
| 2048 | 296.6 | 296.4 | -0.067% |
| 4096 | 463.4 | 462.5 | -0.194% |
| 8192 | 786.0 | 785.6 | -0.051% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 75.4 | 75.4 | +0.000% |
| 2 | 89.6 | 89.7 | +0.112% |
| 4 | 99.8 | 99.9 | +0.100% |
| 8 | 122.5 | 121.2 | -1.061% |
| 16 | 136.8 | 136.8 | +0.000% |
| 32 | 167.4 | 166.3 | -0.657% |
| 64 | 194.2 | 194.1 | -0.051% |
| 128 | 204.4 | 206.3 | +0.930% |
| 256 | 210.1 | 208.7 | -0.666% |
| 512 | 216.8 | 215.7 | -0.507% |
| 1024 | 242.1 | 241.7 | -0.165% |
| 2048 | 292.4 | 291.5 | -0.308% |
| 4096 | 443.9 | 442.5 | -0.315% |
| 8192 | 745.6 | 738.3 | -0.979% |

## N64 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 63.1 | 63.1 | +0.000% |
| 2 | 81.1 | 79.5 | -1.973% |
| 4 | 89.6 | 89.7 | +0.112% |
| 8 | 108.2 | 110.1 | +1.756% |
| 16 | 122.5 | 122.3 | -0.163% |
| 32 | 149.1 | 150.6 | +1.006% |
| 64 | 172.5 | 172.7 | +0.116% |
| 128 | 179.7 | 179.7 | +0.000% |
| 256 | 181.8 | 181.9 | +0.055% |
| 512 | 188.0 | 187.3 | -0.372% |
| 1024 | 209.3 | 208.7 | -0.287% |
| 2048 | 315.0 | 315.1 | +0.032% |
| 4096 | 503.9 | 504.5 | +0.119% |
| 8192 | 891.1 | 893.1 | +0.224% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 74.0 | 73.4 | -0.811% |
| 2 | 87.7 | 88.1 | +0.456% |
| 4 | 95.9 | 94.8 | -1.147% |
| 8 | 116.1 | 116.4 | +0.258% |
| 16 | 128.7 | 130.6 | +1.476% |
| 32 | 157.4 | 159.4 | +1.271% |
| 64 | 181.8 | 181.9 | +0.055% |
| 128 | 190.0 | 190.1 | +0.053% |
| 256 | 197.8 | 198.3 | +0.253% |
| 512 | 205.9 | 205.4 | -0.243% |
| 1024 | 229.3 | 230.3 | +0.436% |
| 2048 | 327.2 | 329.2 | +0.611% |
| 4096 | 500.9 | 500.3 | -0.120% |
| 8192 | 867.2 | 867.6 | +0.046% |
