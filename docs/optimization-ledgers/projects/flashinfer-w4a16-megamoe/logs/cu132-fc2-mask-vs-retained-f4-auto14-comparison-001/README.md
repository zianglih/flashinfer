# FC2 mask versus retained F4

Retained whole F4 source996 versus FC2 readiness-mask sourceb65b on hu-pdx-15, each one full 1–8192 run with the same four ordered F4 candidates and a fresh knob cache. The retained source's public eight catalog was filtered to these four; the candidate uses the current public four without a transform. The candidate replaces whole-row FC1 feature readiness with acquired per-K masks and preserves separate ordered FP32 reduction. Current source also includes the separately reviewed host/readiness cleanups. Both use the same full-forward scorer and 100-sample cold-L2 CUPTI protocol. No split, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency.

8–8192: Mask/retained geometric ratio 0.997980056 (-0.201994%); Mask lower on 4/11 rows.
All14: Mask/retained geometric ratio 0.992318000 (-0.768200%); Mask lower on 7/14 rows.

| Tokens | Retained cold ms | Mask cold ms | Mask/retained change | Retained selected | Mask selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.086544 | 0.084032 | -2.903% | N128/F4/epi | N128/F4/epi |
| 2 | 0.107953 | 0.102369 | -5.173% | N64/F4/epi | N64/F4/epi |
| 4 | 0.122257 | 0.121872 | -0.315% | N64/F4/epi | N64/F4/epi |
| 8 | 0.137856 | 0.126368 | -8.333% | N64/F4/epi | N64/F4/epi |
| 16 | 0.151857 | 0.157841 | +3.941% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180256 | 0.180897 | +0.356% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203409 | 0.201520 | -0.929% | N64/F4/epi | N64/F4/epi |
| 128 | 0.205072 | 0.205777 | +0.344% | N64/F4/epi | N64/F4/epi |
| 256 | 0.208176 | 0.212016 | +1.845% | N64/F4/epi | N64/F4/epi |
| 512 | 0.214753 | 0.212481 | -1.058% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.231153 | 0.242145 | +4.755% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.306179 | 0.309424 | +1.060% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.467649 | 0.469313 | +0.356% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.793748 | 0.762835 | -3.895% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Mask hot us | Mask/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.2 | +0.154% |
| 2 | 83.6 | 83.6 | +0.000% |
| 4 | 95.7 | 94.4 | -1.358% |
| 8 | 114.3 | 113.6 | -0.612% |
| 16 | 131.3 | 130.7 | -0.457% |
| 32 | 161.3 | 161.4 | +0.062% |
| 64 | 184.0 | 185.9 | +1.033% |
| 128 | 190.6 | 191.5 | +0.472% |
| 256 | 194.2 | 196.1 | +0.978% |
| 512 | 202.3 | 200.3 | -0.989% |
| 1024 | 220.8 | 220.8 | +0.000% |
| 2048 | 297.1 | 298.1 | +0.337% |
| 4096 | 464.4 | 465.9 | +0.323% |
| 8192 | 781.8 | 780.0 | -0.230% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Mask hot us | Mask/retained change |
|---:|---:|---:|---:|
| 1 | 77.4 | 78.4 | +1.292% |
| 2 | 89.7 | 89.7 | +0.000% |
| 4 | 100.0 | 100.0 | +0.000% |
| 8 | 124.4 | 124.5 | +0.080% |
| 16 | 137.8 | 136.9 | -0.653% |
| 32 | 167.6 | 168.5 | +0.537% |
| 64 | 196.1 | 196.1 | +0.000% |
| 128 | 200.3 | 200.8 | +0.250% |
| 256 | 209.1 | 208.4 | -0.335% |
| 512 | 218.7 | 217.6 | -0.503% |
| 1024 | 245.2 | 243.2 | -0.816% |
| 2048 | 293.9 | 294.5 | +0.204% |
| 4096 | 445.5 | 446.6 | +0.247% |
| 8192 | 730.3 | 735.3 | +0.685% |

## N64 / epi_warps

| Tokens | Retained hot us | Mask hot us | Mask/retained change |
|---:|---:|---:|---:|
| 1 | 65.2 | 65.2 | +0.000% |
| 2 | 81.5 | 81.5 | +0.000% |
| 4 | 91.8 | 90.6 | -1.307% |
| 8 | 110.2 | 108.5 | -1.543% |
| 16 | 123.5 | 123.1 | -0.324% |
| 32 | 151.1 | 150.1 | -0.662% |
| 64 | 172.5 | 173.7 | +0.696% |
| 128 | 179.7 | 179.1 | -0.334% |
| 256 | 182.0 | 181.9 | -0.055% |
| 512 | 188.1 | 188.0 | -0.053% |
| 1024 | 208.5 | 208.5 | +0.000% |
| 2048 | 317.0 | 315.0 | -0.631% |
| 4096 | 503.7 | 500.4 | -0.655% |
| 8192 | 893.5 | 892.0 | -0.168% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Mask hot us | Mask/retained change |
|---:|---:|---:|---:|
| 1 | 75.2 | 75.4 | +0.266% |
| 2 | 87.7 | 88.6 | +1.026% |
| 4 | 97.9 | 98.8 | +0.919% |
| 8 | 119.3 | 118.3 | -0.838% |
| 16 | 130.6 | 130.6 | +0.000% |
| 32 | 159.3 | 159.4 | +0.063% |
| 64 | 184.9 | 185.4 | +0.270% |
| 128 | 189.9 | 190.0 | +0.053% |
| 256 | 196.2 | 196.1 | -0.051% |
| 512 | 206.5 | 204.9 | -0.775% |
| 1024 | 232.6 | 231.1 | -0.645% |
| 2048 | 329.0 | 329.3 | +0.091% |
| 4096 | 502.9 | 503.9 | +0.199% |
| 8192 | 855.3 | 863.2 | +0.924% |
