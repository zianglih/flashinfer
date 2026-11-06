# Exact tail versus retained F4

Retained whole F4 source996 versus current exact-tail source0bf on hu-pdx-15, each one full 1–8192 run with four ordered F4 candidates and a fresh knob cache. The retained source's public eight catalog was filtered to these four; current public four is transformed only to in_kernel_fc2_reduce=True. Current source also includes the separately reviewed host/readiness cleanups and targeted tests. Both use the same full-forward scorer and 100-sample cold-L2 CUPTI protocol; the current forward incorporates ordered FP32 reduction into Mega's tail instead of a standalone reducer launch. No split, baseline replay, row replacement, drift adjustment or statistical-confidence claim. Hot printed scores remain separate from cold-L2 latency.

8–8192: Tail/retained geometric ratio 0.998246695 (-0.175331%); Tail lower on 6/11 rows.
All14: Tail/retained geometric ratio 0.983894246 (-1.610575%); Tail lower on 9/14 rows.

| Tokens | Retained cold ms | Tail cold ms | Tail/retained change | Retained selected | Tail selected |
|---:|---:|---:|---:|---|---|
| 1 | 0.086544 | 0.077776 | -10.131% | N128/F4/epi | N128/F4/epi |
| 2 | 0.107953 | 0.100960 | -6.478% | N64/F4/epi | N64/F4/epi |
| 4 | 0.122257 | 0.118144 | -3.364% | N64/F4/epi | N64/F4/epi |
| 8 | 0.137856 | 0.137344 | -0.371% | N64/F4/epi | N64/F4/epi |
| 16 | 0.151857 | 0.150274 | -1.042% | N64/F4/epi | N64/F4/epi |
| 32 | 0.180256 | 0.172641 | -4.225% | N64/F4/epi | N64/F4/epi |
| 64 | 0.203409 | 0.201184 | -1.094% | N64/F4/epi | N64/F4/epi |
| 128 | 0.205072 | 0.205969 | +0.437% | N64/F4/epi | N64/F4/epi |
| 256 | 0.208176 | 0.218721 | +5.065% | N64/F4/epi | N64/F4/epi |
| 512 | 0.214753 | 0.212257 | -1.162% | N64/F4/epi | N64/F4/epi |
| 1024 | 0.231153 | 0.232865 | +0.741% | N64/F4/epi | N64/F4/epi |
| 2048 | 0.306179 | 0.310657 | +1.463% | N128/F4/reuse | N128/F4/reuse |
| 4096 | 0.467649 | 0.469698 | +0.438% | N128/F4/reuse | N128/F4/reuse |
| 8192 | 0.793748 | 0.778577 | -1.911% | N128/F4/reuse | N128/F4/reuse |

Hot GPU-event scores below are printed to 0.1 us and aggregate maximum of per-rank medians; cold timings above are median of 100 per-iteration rank maxima. Each hot comparison holds geometry and return mode fixed.

## N128 / epi_warps

| Tokens | Retained hot us | Tail hot us | Tail/retained change |
|---:|---:|---:|---:|
| 1 | 65.1 | 65.1 | +0.000% |
| 2 | 83.6 | 82.5 | -1.316% |
| 4 | 95.7 | 93.8 | -1.985% |
| 8 | 114.3 | 114.3 | +0.000% |
| 16 | 131.3 | 128.6 | -2.056% |
| 32 | 161.3 | 159.4 | -1.178% |
| 64 | 184.0 | 185.4 | +0.761% |
| 128 | 190.6 | 189.5 | -0.577% |
| 256 | 194.2 | 192.4 | -0.927% |
| 512 | 202.3 | 199.3 | -1.483% |
| 1024 | 220.8 | 218.8 | -0.906% |
| 2048 | 297.1 | 296.6 | -0.168% |
| 4096 | 464.4 | 469.1 | +1.012% |
| 8192 | 781.8 | 786.5 | +0.601% |

## N128 / reuse_dispatch_warps

| Tokens | Retained hot us | Tail hot us | Tail/retained change |
|---:|---:|---:|---:|
| 1 | 77.4 | 75.5 | -2.455% |
| 2 | 89.7 | 88.5 | -1.338% |
| 4 | 100.0 | 99.8 | -0.200% |
| 8 | 124.4 | 120.4 | -3.215% |
| 16 | 137.8 | 136.8 | -0.726% |
| 32 | 167.6 | 168.5 | +0.537% |
| 64 | 196.1 | 195.5 | -0.306% |
| 128 | 200.3 | 199.2 | -0.549% |
| 256 | 209.1 | 208.5 | -0.287% |
| 512 | 218.7 | 216.6 | -0.960% |
| 1024 | 245.2 | 243.3 | -0.775% |
| 2048 | 293.9 | 292.4 | -0.510% |
| 4096 | 445.5 | 445.0 | -0.112% |
| 8192 | 730.3 | 737.4 | +0.972% |

## N64 / epi_warps

| Tokens | Retained hot us | Tail hot us | Tail/retained change |
|---:|---:|---:|---:|
| 1 | 65.2 | 65.1 | -0.153% |
| 2 | 81.5 | 81.2 | -0.368% |
| 4 | 91.8 | 91.6 | -0.218% |
| 8 | 110.2 | 108.2 | -1.815% |
| 16 | 123.5 | 120.5 | -2.429% |
| 32 | 151.1 | 149.1 | -1.324% |
| 64 | 172.5 | 171.6 | -0.522% |
| 128 | 179.7 | 177.7 | -1.113% |
| 256 | 182.0 | 179.8 | -1.209% |
| 512 | 188.1 | 186.0 | -1.116% |
| 1024 | 208.5 | 208.4 | -0.048% |
| 2048 | 317.0 | 314.9 | -0.662% |
| 4096 | 503.7 | 502.9 | -0.159% |
| 8192 | 893.5 | 896.0 | +0.280% |

## N64 / reuse_dispatch_warps

| Tokens | Retained hot us | Tail hot us | Tail/retained change |
|---:|---:|---:|---:|
| 1 | 75.2 | 75.2 | +0.000% |
| 2 | 87.7 | 87.5 | -0.228% |
| 4 | 97.9 | 96.8 | -1.124% |
| 8 | 119.3 | 116.4 | -2.431% |
| 16 | 130.6 | 128.6 | -1.531% |
| 32 | 159.3 | 157.3 | -1.255% |
| 64 | 184.9 | 182.9 | -1.082% |
| 128 | 189.9 | 188.3 | -0.843% |
| 256 | 196.2 | 194.0 | -1.121% |
| 512 | 206.5 | 203.2 | -1.598% |
| 1024 | 232.6 | 227.9 | -2.021% |
| 2048 | 329.0 | 326.0 | -0.912% |
| 4096 | 502.9 | 497.1 | -1.153% |
| 8192 | 855.3 | 857.2 | +0.222% |
