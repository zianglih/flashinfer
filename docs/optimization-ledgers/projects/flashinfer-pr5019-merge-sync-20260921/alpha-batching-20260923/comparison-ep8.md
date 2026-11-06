EP8; decode 4–512 geometric-mean speedup: **1.0096×**.

| Tokens | Before µs | After µs | Speedup | Before tactic | After tactic |
|---:|---:|---:|---:|---|---|
| 1 | 70.689 | 79.889 | 0.8848× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 2 | 92.784 | 86.897 | 1.0678× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 4 | 105.233 | 98.049 | 1.0733× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 8 | 124.001 | 123.474 | 1.0043× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 16 | 136.257 | 135.857 | 1.0029× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 32 | 167.986 | 164.273 | 1.0226× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 64 | 185.938 | 186.945 | 0.9946× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 128 | 190.865 | 192.097 | 0.9936× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) |
| 256 | 185.665 | 190.033 | 0.9770× | M256N64/C2/G512/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 512 | 201.186 | 198.994 | 1.0110× | M256N64/C2/G1024/S2/atomic/epi/flags(2,4) | M256N64/C2/G512/S2/atomic/epi/flags(2,4) |
| 4096 | 469.459 | 461.108 | 1.0181× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |
| 8192 | 784.965 | 774.599 | 1.0134× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |
| 16384 | 1504.896 | 1555.474 | 0.9675× | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) | M256N128/C2/G1024/S2/atomic/dispatch/flags(2,4) |

100 cold-L2 CUDA-graph CUPTI samples per row. Median of per-iteration rank-MAX activity spans; no trimming. Both arms stage runtime unit FP32 alphas and tune from an empty knob cache. 1/2 tokens are reported but excluded from retention. Check prefill rows individually. Paired outputs match bit for bit; this is not independent reference or weight-sync validation.
