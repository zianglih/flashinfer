# Fast-divmod versus immediate e470 F4

Immediate whole F4 sourcee470 versus the fast-divmod source3da candidate on hu-pdx-59, each one full 1–8192 run using the same ordered public four F4 candidates and a fresh knob cache. The candidate changes only owned scheduler division lowering; the prior e470 epilogue and padding behavior remain. Both use separate ordered FP32 reduction, the same full-forward scorer and 100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency.

8–8192: Dispatch/retained geometric ratio 1.008015069 (+0.801507%); Dispatch lower on 5/11 rows.
All14: Dispatch/retained geometric ratio 0.988777915 (-1.122209%); Dispatch lower on 8/14 rows.

| Tokens | Retained cold ms | Dispatch cold ms | Dispatch/retained change | Retained selected | Dispatch selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.084801 | 0.069488 | -18.058% | N64/F4/epi | N64/F4/epi |
| 2 | 0.104528 | 0.102033 | -2.387% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120817 | 0.118129 | -2.225% | N64/F4/epi | N64/F4/epi |
| 8 | 0.138897 | 0.137745 | -0.829% | N64/F4/epi | N64/F4/epi |
| 16 | 0.148577 | 0.150881 | +1.551% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180545 | 0.179346 | -0.664% | N64/F4/epi | N64/F4/epi |
| 64 | 0.201537 | 0.197057 | -2.223% | N64/F4/epi | N64/F4/epi |
| 128 | 0.203297 | 0.222610 | +9.500% | N64/F4/epi | N64/F4/epi |
| 256 | 0.210081 | 0.209169 | -0.434% | N64/F4/epi | N64/F4/epi |
| 512 | 0.215041 | 0.215234 | +0.090% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.229794 | 0.234546 | +2.068% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.312563 | 0.308452 | -1.315% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468308 | 0.469108 | +0.171% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.775576 | 0.786245 | +1.376% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.0 | -0.154% |
| 2 | 83.6 | 83.5 | -0.120% |
| 4 | 93.8 | 93.8 | +0.000% |
| 8 | 114.2 | 114.3 | +0.088% |
| 16 | 130.7 | 130.4 | -0.230% |
| 32 | 160.3 | 161.1 | +0.499% |
| 64 | 183.9 | 184.6 | +0.381% |
| 128 | 190.1 | 190.1 | +0.000% |
| 256 | 195.4 | 195.1 | -0.154% |
| 512 | 202.2 | 200.3 | -0.940% |
| 1024 | 220.7 | 220.8 | +0.045% |
| 2048 | 296.4 | 296.6 | +0.067% |
| 4096 | 463.6 | 462.4 | -0.259% |
| 8192 | 788.1 | 780.4 | -0.977% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 75.4 | 75.3 | -0.133% |
| 2 | 89.7 | 89.7 | +0.000% |
| 4 | 99.7 | 99.9 | +0.201% |
| 8 | 121.3 | 121.4 | +0.082% |
| 16 | 137.5 | 136.8 | -0.509% |
| 32 | 167.3 | 167.2 | -0.060% |
| 64 | 193.9 | 193.8 | -0.052% |
| 128 | 204.3 | 205.5 | +0.587% |
| 256 | 208.5 | 210.4 | +0.911% |
| 512 | 218.6 | 217.6 | -0.457% |
| 1024 | 241.2 | 243.2 | +0.829% |
| 2048 | 290.3 | 291.5 | +0.413% |
| 4096 | 444.4 | 443.0 | -0.315% |
| 8192 | 739.1 | 742.2 | +0.419% |

## N64 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 63.7 | 63.0 | -1.099% |
| 2 | 80.4 | 79.5 | -1.119% |
| 4 | 89.7 | 89.8 | +0.111% |
| 8 | 109.2 | 110.2 | +0.916% |
| 16 | 122.4 | 122.5 | +0.082% |
| 32 | 149.9 | 149.0 | -0.600% |
| 64 | 173.7 | 173.6 | -0.058% |
| 128 | 179.7 | 179.3 | -0.223% |
| 256 | 181.9 | 181.9 | +0.000% |
| 512 | 187.9 | 188.0 | +0.053% |
| 1024 | 209.6 | 208.5 | -0.525% |
| 2048 | 315.8 | 315.0 | -0.253% |
| 4096 | 501.4 | 505.3 | +0.778% |
| 8192 | 892.9 | 893.5 | +0.067% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 74.2 | 74.1 | -0.135% |
| 2 | 87.7 | 87.5 | -0.228% |
| 4 | 96.7 | 95.9 | -0.827% |
| 8 | 114.3 | 117.3 | +2.625% |
| 16 | 129.4 | 128.6 | -0.618% |
| 32 | 158.0 | 157.2 | -0.506% |
| 64 | 183.5 | 182.3 | -0.654% |
| 128 | 190.1 | 190.0 | -0.053% |
| 256 | 196.3 | 196.3 | +0.000% |
| 512 | 206.0 | 205.4 | -0.291% |
| 1024 | 231.0 | 229.0 | -0.866% |
| 2048 | 328.8 | 329.2 | +0.122% |
| 4096 | 501.2 | 502.3 | +0.219% |
| 8192 | 871.3 | 868.0 | -0.379% |
