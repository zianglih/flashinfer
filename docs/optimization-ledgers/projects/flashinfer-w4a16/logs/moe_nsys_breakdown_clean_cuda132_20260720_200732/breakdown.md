
### 32 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 100.8 | 34.4 | 145.4 | 69.3 | 75.2 | - | 82.4 | - | 16.8 | 35.4 | 25.5 | 50.5 | 636.9 |
| W4A16 EP8 | 96.2 | 36.5 | 135.2 | - | 25.7 | 48.0 | 121.8 | 6.5 | - | 59.5 | 23.9 | 57.7 | 613.3 |
| W4A16 TP8 | 66.4 | 94.3 | - | - | 24.5 | 47.1 | 120.4 | 12.6 | - | 93.8 | 15.8 | 32.8 | 506.6 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs

### 4096 global tokens (median critical-rank GPU span, us)
| Configuration | Routing | Input communication | EP setup | Input quant | Route indices | Permute | GEMM1 | SwiGLU | Intermediate quant | GEMM2 | Finalize | Output communication | Application span |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W4A4 EP8 + quant | 109.7 | 99.7 | 91.9 | 104.5 | 57.8 | - | 573.0 | - | 221.3 | 312.4 | 115.0 | 168.0 | 1851.8 |
| W4A16 EP8 | 104.7 | 105.8 | 84.4 | - | 28.3 | 119.0 | 1147.9 | 81.6 | - | 574.5 | 121.8 | 122.1 | 2488.4 |
| W4A16 TP8 | 7.5 | 192.9 | - | - | 10.3 | 118.9 | 263.3 | 42.6 | - | 281.4 | 112.7 | 189.5 | 1219.5 |
Input/output communication means EP dispatch/combine or TP all-gather/all-reduce. W4A4 GEMM1 fuses gather and SwiGLU.
Profiles: W4A4 EP8 + quant=20 iterations x 8 GPUs, W4A16 EP8=20 iterations x 8 GPUs, W4A16 TP8=20 iterations x 8 GPUs
