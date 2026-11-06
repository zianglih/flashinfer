
### 32 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 12.6 | 41.5 | 35.0 | 64.0 | 67.5 | - | 78.0 | - | 21.9 | 33.2 | 16.4 | 39.6 | 404.7 |
| W4A16 EP8 | 13.4 | 40.7 | 69.4 | - | 22.6 | 44.1 | 121.3 | 6.0 | - | 60.4 | 19.8 | 44.2 | 425.8 |
| W4A16 TP8 | 68.4 | 93.3 | - | - | 24.6 | 46.0 | 120.5 | 12.6 | - | 93.6 | 15.6 | 31.1 | 505.5 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs

### 4096 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 13.2 | 54.3 | 22.9 | 69.9 | 64.8 | - | 128.3 | - | 214.9 | 59.2 | 46.6 | 63.0 | 735.2 |
| W4A16 EP8 | 12.5 | 55.6 | 55.2 | - | 21.9 | 44.2 | 240.6 | 15.4 | - | 125.1 | 52.3 | 61.8 | 687.6 |
| W4A16 TP8 | 7.5 | 190.4 | - | - | 10.6 | 118.8 | 251.7 | 41.0 | - | 279.4 | 112.5 | 189.6 | 1206.4 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs
