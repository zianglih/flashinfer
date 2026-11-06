# Dispatch versus retained F4

Retained whole F4 source2e3b versus the compile-time dispatch candidate on hu-pdx-59, each one full 1–8192 run using the same ordered public four F4 candidates and a fresh knob cache. The candidate retains static epilogue bounds and signed power-of-two decode while restoring the original two padding ceil divisions. Both use separate ordered FP32 reduction, the same full-forward scorer and 100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency.

8–8192: Dispatch/retained geometric ratio 0.995289265 (-0.471073%); Dispatch lower on 7/11 rows.
All14: Dispatch/retained geometric ratio 1.000534640 (+0.053464%); Dispatch lower on 8/14 rows.

| Tokens | Retained cold ms | Dispatch cold ms | Dispatch/retained change | Retained selected | Dispatch selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.089169 | 0.084801 | -4.899% | N64/F4/epi | N64/F4/epi |
| 2 | 0.098321 | 0.104528 | +6.313% | N64/F4/epi | N64/F4/epi |
| 4 | 0.115105 | 0.120817 | +4.962% | N64/F4/epi | N64/F4/epi |
| 8 | 0.134592 | 0.138897 | +3.199% | N64/F4/epi | N64/F4/epi |
| 16 | 0.152177 | 0.148577 | -2.366% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180081 | 0.180545 | +0.258% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203393 | 0.201537 | -0.913% | N64/F4/epi | N64/F4/epi |
| 128 | 0.206145 | 0.203297 | -1.382% | N64/F4/epi | N64/F4/epi |
| 256 | 0.212002 | 0.210081 | -0.906% | N64/F4/epi | N64/F4/epi |
| 512 | 0.211650 | 0.215041 | +1.602% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.235042 | 0.229794 | -2.233% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.311283 | 0.312563 | +0.411% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468500 | 0.468308 | -0.041% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.796709 | 0.775576 | -2.653% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.1 | +0.000% |
| 2 | 83.6 | 83.6 | +0.000% |
| 4 | 93.8 | 93.8 | +0.000% |
| 8 | 114.1 | 114.2 | +0.088% |
| 16 | 130.7 | 130.7 | +0.000% |
| 32 | 160.2 | 160.3 | +0.062% |
| 64 | 184.9 | 183.9 | -0.541% |
| 128 | 190.8 | 190.1 | -0.367% |
| 256 | 194.2 | 195.4 | +0.618% |
| 512 | 202.3 | 202.2 | -0.049% |
| 1024 | 220.8 | 220.7 | -0.045% |
| 2048 | 296.5 | 296.4 | -0.034% |
| 4096 | 466.2 | 463.6 | -0.558% |
| 8192 | 784.4 | 788.1 | +0.472% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 75.3 | 75.4 | +0.133% |
| 2 | 89.5 | 89.7 | +0.223% |
| 4 | 98.9 | 99.7 | +0.809% |
| 8 | 120.5 | 121.3 | +0.664% |
| 16 | 136.8 | 137.5 | +0.512% |
| 32 | 167.6 | 167.3 | -0.179% |
| 64 | 194.1 | 193.9 | -0.103% |
| 128 | 200.4 | 204.3 | +1.946% |
| 256 | 209.5 | 208.5 | -0.477% |
| 512 | 218.7 | 218.6 | -0.046% |
| 1024 | 243.3 | 241.2 | -0.863% |
| 2048 | 292.1 | 290.3 | -0.616% |
| 4096 | 446.5 | 444.4 | -0.470% |
| 8192 | 743.8 | 739.1 | -0.632% |

## N64 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 63.2 | 63.7 | +0.791% |
| 2 | 81.5 | 80.4 | -1.350% |
| 4 | 91.7 | 89.7 | -2.181% |
| 8 | 110.2 | 109.2 | -0.907% |
| 16 | 122.5 | 122.4 | -0.082% |
| 32 | 149.2 | 149.9 | +0.469% |
| 64 | 172.5 | 173.7 | +0.696% |
| 128 | 179.8 | 179.7 | -0.056% |
| 256 | 181.9 | 181.9 | +0.000% |
| 512 | 188.0 | 187.9 | -0.053% |
| 1024 | 210.4 | 209.6 | -0.380% |
| 2048 | 315.0 | 315.8 | +0.254% |
| 4096 | 505.9 | 501.4 | -0.890% |
| 8192 | 892.7 | 892.9 | +0.022% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 73.4 | 74.2 | +1.090% |
| 2 | 87.6 | 87.7 | +0.114% |
| 4 | 97.8 | 96.7 | -1.125% |
| 8 | 116.4 | 114.3 | -1.804% |
| 16 | 128.7 | 129.4 | +0.544% |
| 32 | 158.3 | 158.0 | -0.190% |
| 64 | 182.5 | 183.5 | +0.548% |
| 128 | 189.9 | 190.1 | +0.105% |
| 256 | 196.2 | 196.3 | +0.051% |
| 512 | 205.5 | 206.0 | +0.243% |
| 1024 | 229.9 | 231.0 | +0.478% |
| 2048 | 329.3 | 328.8 | -0.152% |
| 4096 | 504.4 | 501.2 | -0.634% |
| 8192 | 866.9 | 871.3 | +0.508% |
