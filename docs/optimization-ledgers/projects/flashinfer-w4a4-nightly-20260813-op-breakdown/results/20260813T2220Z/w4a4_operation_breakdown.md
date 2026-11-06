# W4A4 per-token Nsight Systems operation breakdown

Values are mean staged GPU-kernel time per rank per captured iteration in milliseconds: each raw Nsight aggregate is divided by 8 ranks x 20 iterations. Concurrent kernels are not subtracted; totals are diagnostic kernel-time sums, not application wall-clock spans.

Each parenthetical percentage is that operation's share of the total staged GPU kernel time in the same column, computed from unrounded reduced values.

## 32 global tokens

| Operation | W4A4 per-token EP8 | W4A4 per-token TP8 | W4A4 per-token 4over6 EP8 | W4A4 per-token 4over6 TP8 |
|---|---:|---:|---:|---:|
| Input communication | 0.040 (16.3%) | 0.026 (10.5%) | 0.025 (11.0%) | 0.042 (15.6%) |
| Routing | 0.003 (1.1%) | 0.003 (1.2%) | 0.003 (1.2%) | 0.003 (1.1%) |
| Input activation quantization | 0.007 (2.8%) | 0.004 (1.8%) | 0.006 (2.6%) | 0.006 (2.0%) |
| Route indices | 0.004 (1.5%) | 0.004 (1.5%) | 0.004 (1.6%) | 0.004 (1.4%) |
| Permute | - | - | - | - |
| GEMM1 | 0.072 (29.6%) | 0.074 (29.5%) | 0.072 (31.7%) | 0.074 (27.3%) |
| Activation | 0.001 (0.5%) | 0.001 (0.5%) | 0.001 (0.6%) | 0.001 (0.5%) |
| Intermediate quantization | 0.009 (3.8%) | 0.036 (14.5%) | 0.008 (3.6%) | 0.036 (13.5%) |
| GEMM2 | 0.032 (13.1%) | 0.039 (15.6%) | 0.032 (14.0%) | 0.039 (14.5%) |
| Unpermute | 0.009 (3.8%) | 0.018 (7.3%) | 0.009 (4.0%) | 0.018 (6.8%) |
| Output communication | 0.067 (27.4%) | 0.044 (17.6%) | 0.068 (29.6%) | 0.047 (17.4%) |
| **Total staged GPU kernel time** | **0.244 (100.0%)** | **0.249 (100.0%)** | **0.228 (100.0%)** | **0.270 (100.0%)** |

## 4096 global tokens

| Operation | W4A4 per-token EP8 | W4A4 per-token TP8 | W4A4 per-token 4over6 EP8 | W4A4 per-token 4over6 TP8 |
|---|---:|---:|---:|---:|
| Input communication | 0.072 (15.7%) | 0.138 (16.9%) | 0.073 (15.3%) | 0.138 (16.5%) |
| Routing | 0.003 (0.7%) | 0.008 (1.0%) | 0.003 (0.7%) | 0.008 (1.0%) |
| Input activation quantization | 0.022 (4.9%) | 0.019 (2.4%) | 0.024 (5.0%) | 0.032 (3.9%) |
| Route indices | 0.007 (1.6%) | 0.009 (1.1%) | 0.007 (1.6%) | 0.009 (1.0%) |
| Permute | - | - | - | - |
| GEMM1 | 0.109 (23.7%) | 0.127 (15.5%) | 0.109 (23.1%) | 0.127 (15.2%) |
| Activation | 0.002 (0.5%) | 0.001 (0.2%) | 0.003 (0.5%) | 0.001 (0.2%) |
| Intermediate quantization | 0.060 (12.9%) | 0.070 (8.5%) | 0.063 (13.4%) | 0.075 (9.0%) |
| GEMM2 | 0.061 (13.3%) | 0.144 (17.7%) | 0.061 (13.0%) | 0.144 (17.4%) |
| Unpermute | 0.034 (7.3%) | 0.117 (14.3%) | 0.034 (7.1%) | 0.117 (14.0%) |
| Output communication | 0.089 (19.4%) | 0.183 (22.5%) | 0.096 (20.3%) | 0.181 (21.8%) |
| **Total staged GPU kernel time** | **0.461 (100.0%)** | **0.816 (100.0%)** | **0.474 (100.0%)** | **0.832 (100.0%)** |
