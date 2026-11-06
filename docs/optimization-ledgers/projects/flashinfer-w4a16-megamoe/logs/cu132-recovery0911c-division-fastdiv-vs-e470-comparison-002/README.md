# Fast-divmod versus immediate e470 F4

Immediate whole F4 sourcee470 versus the single requested repeat of fast-divmod source3da on hu-pdx-59, each a complete 1–8192 run using the same ordered public four F4 candidates and a fresh knob cache. The candidate changes only owned scheduler division lowering; the prior e470 epilogue and padding behavior remain. Both use separate ordered FP32 reduction, the same full-forward scorer and 100-sample cold-L2 CUPTI protocol. No split, old-node control, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency. The first candidate result remains separate and immutable; no minima or cross-run row selection.

8–8192: Dispatch/retained geometric ratio 1.002937807 (+0.293781%); Dispatch lower on 6/11 rows.
All14: Dispatch/retained geometric ratio 0.996325418 (-0.367458%); Dispatch lower on 9/14 rows.

| Tokens | Retained cold ms | Dispatch cold ms | Dispatch/retained change | Retained selected | Dispatch selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.084801 | 0.084096 | -0.831% | N64/F4/epi | N64/F4/epi |
| 2 | 0.104528 | 0.100608 | -3.750% | N64/F4/epi | N64/F4/epi |
| 4 | 0.120817 | 0.116401 | -3.655% | N64/F4/epi | N64/F4/epi |
| 8 | 0.138897 | 0.138193 | -0.507% | N64/F4/epi | N64/F4/epi |
| 16 | 0.148577 | 0.146977 | -1.077% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180545 | 0.179329 | -0.674% | N64/F4/epi | N64/F4/epi |
| 64 | 0.201537 | 0.202642 | +0.548% | N64/F4/epi | N64/F4/epi |
| 128 | 0.203297 | 0.209442 | +3.023% | N64/F4/epi | N64/F4/epi |
| 256 | 0.210081 | 0.208738 | -0.639% | N64/F4/epi | N64/F4/epi |
| 512 | 0.215041 | 0.213170 | -0.870% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.229794 | 0.234385 | +1.998% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.312563 | 0.310692 | -0.599% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.468308 | 0.469092 | +0.167% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.775576 | 0.790761 | +1.958% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.1 | +0.000% |
| 2 | 83.6 | 83.5 | -0.120% |
| 4 | 93.8 | 93.8 | +0.000% |
| 8 | 114.2 | 114.3 | +0.088% |
| 16 | 130.7 | 130.4 | -0.230% |
| 32 | 160.3 | 159.4 | -0.561% |
| 64 | 183.9 | 183.9 | +0.000% |
| 128 | 190.1 | 190.1 | +0.000% |
| 256 | 195.4 | 196.2 | +0.409% |
| 512 | 202.2 | 200.3 | -0.940% |
| 1024 | 220.7 | 220.9 | +0.091% |
| 2048 | 296.4 | 296.6 | +0.067% |
| 4096 | 463.6 | 463.4 | -0.043% |
| 8192 | 788.1 | 786.0 | -0.266% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 75.4 | 75.4 | +0.000% |
| 2 | 89.7 | 89.6 | -0.111% |
| 4 | 99.7 | 99.8 | +0.100% |
| 8 | 121.3 | 122.5 | +0.989% |
| 16 | 137.5 | 136.8 | -0.509% |
| 32 | 167.3 | 167.4 | +0.060% |
| 64 | 193.9 | 194.2 | +0.155% |
| 128 | 204.3 | 204.4 | +0.049% |
| 256 | 208.5 | 210.1 | +0.767% |
| 512 | 218.6 | 216.8 | -0.823% |
| 1024 | 241.2 | 242.1 | +0.373% |
| 2048 | 290.3 | 292.4 | +0.723% |
| 4096 | 444.4 | 443.9 | -0.113% |
| 8192 | 739.1 | 745.6 | +0.879% |

## N64 / epi_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 63.7 | 63.1 | -0.942% |
| 2 | 80.4 | 81.1 | +0.871% |
| 4 | 89.7 | 89.6 | -0.111% |
| 8 | 109.2 | 108.2 | -0.916% |
| 16 | 122.4 | 122.5 | +0.082% |
| 32 | 149.9 | 149.1 | -0.534% |
| 64 | 173.7 | 172.5 | -0.691% |
| 128 | 179.7 | 179.7 | +0.000% |
| 256 | 181.9 | 181.8 | -0.055% |
| 512 | 187.9 | 188.0 | +0.053% |
| 1024 | 209.6 | 209.3 | -0.143% |
| 2048 | 315.8 | 315.0 | -0.253% |
| 4096 | 501.4 | 503.9 | +0.499% |
| 8192 | 892.9 | 891.1 | -0.202% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Dispatch hot us | Dispatch/retained change |
|---:|---:|---:|---:|
| 1 | 74.2 | 74.0 | -0.270% |
| 2 | 87.7 | 87.7 | +0.000% |
| 4 | 96.7 | 95.9 | -0.827% |
| 8 | 114.3 | 116.1 | +1.575% |
| 16 | 129.4 | 128.7 | -0.541% |
| 32 | 158.0 | 157.4 | -0.380% |
| 64 | 183.5 | 181.8 | -0.926% |
| 128 | 190.1 | 190.0 | -0.053% |
| 256 | 196.3 | 197.8 | +0.764% |
| 512 | 206.0 | 205.9 | -0.049% |
| 1024 | 231.0 | 229.3 | -0.736% |
| 2048 | 328.8 | 327.2 | -0.487% |
| 4096 | 501.2 | 500.9 | -0.060% |
| 8192 | 871.3 | 867.2 | -0.471% |
