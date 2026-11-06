EP4; decode 4–512 geometric-mean speedup: **1.0187×**.

| Tokens | Before µs | After µs | Speedup | Before tactic | After tactic |
|---:|---:|---:|---:|---|---|
| 1 | 76.624 | 74.048 | 1.0348× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N128/C2/G512/S2/atomic/epi/flags(2,4) |
| 2 | 97.617 | 98.529 | 0.9907× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N128/C2/G1024/S2/atomic/epi/flags(2,4) |
| 4 | 116.945 | 114.240 | 1.0237× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 8 | 151.025 | 145.266 | 1.0396× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 16 | 206.929 | 198.593 | 1.0420× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 32 | 261.698 | 253.043 | 1.0342× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 64 | 296.435 | 288.866 | 1.0262× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 128 | 322.963 | 320.338 | 1.0082× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 256 | 327.634 | 331.779 | 0.9875× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 512 | 346.818 | 350.340 | 0.9899× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 4096 | 788.296 | 801.654 | 0.9833× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |
| 8192 | 1466.411 | 1460.465 | 1.0041× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |
| 16384 | 2859.730 | 2857.503 | 1.0008× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |

100 cold-L2 CUDA-graph CUPTI samples per row. Median of per-iteration rank-MAX activity spans; no trimming. Both arms stage runtime unit FP32 alphas and tune from an empty knob cache. 1/2 tokens are reported but excluded from retention. Check prefill rows individually. Paired outputs match bit for bit; this is not independent reference or weight-sync validation.
