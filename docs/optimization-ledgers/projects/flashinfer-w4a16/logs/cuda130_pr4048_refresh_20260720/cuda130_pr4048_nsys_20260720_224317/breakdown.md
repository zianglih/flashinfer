
### 32 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 12.4 | 40.9 | 35.0 | 66.1 | 66.3 | - | 75.1 | - | 19.3 | 31.3 | 15.0 | 38.8 | 398.4 |
| W4A16 EP8 | 11.9 | 39.9 | 69.4 | - | 21.5 | 42.8 | 209.1 | 6.2 | - | 104.3 | 19.4 | 13.7 | 544.7 |
| W4A16 TP8 | 70.1 | 96.1 | - | - | 24.4 | 44.5 | 177.4 | 12.2 | - | 117.4 | 16.1 | 85.9 | 643.6 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs

### 4096 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 12.4 | 56.8 | 21.3 | 69.4 | 65.2 | - | 117.0 | - | 217.1 | 55.7 | 43.0 | 89.4 | 749.2 |
| W4A16 EP8 | 12.5 | 57.0 | 58.7 | - | 23.0 | 44.4 | 407.3 | 14.3 | - | 203.7 | 45.9 | 80.5 | 943.7 |
| W4A16 TP8 | 7.6 | 188.4 | - | - | 11.4 | 119.1 | 391.0 | 36.7 | - | 314.3 | 100.6 | 184.4 | 1356.6 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs
