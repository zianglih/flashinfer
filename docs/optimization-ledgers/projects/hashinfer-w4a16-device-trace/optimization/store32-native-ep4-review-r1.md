# native EP4 comparison

H7168 / I2048 / E256 / top-8; A1 → B1.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.841 | 66.385 | 1.0219× | 100 / 100 | 1.168 | 1.264 |
| 2 | 93.936 | 88.577 | 1.0605× | 100 / 100 | 1.071 | 0.993 |
| 4 | 119.185 | 116.337 | 1.0245× | 100 / 100 | 1.503 | 1.840 |
| 8 | 159.138 | 147.345 | 1.0800× | 100 / 100 | 1.600 | 1.025 |
| 16 | 196.258 | 201.362 | 0.9747× | 100 / 100 | 1.088 | 1.041 |
| 32 | 269.443 | 259.874 | 1.0368× | 100 / 100 | 1.120 | 1.248 |
| 64 | 294.435 | 302.755 | 0.9725× | 100 / 100 | 1.760 | 1.727 |
| 128 | 320.212 | 320.323 | 0.9997× | 100 / 100 | 1.008 | 2.016 |
| 256 | 330.323 | 331.507 | 0.9964× | 100 / 100 | 0.896 | 1.792 |
| 512 | 346.707 | 344.692 | 1.0058× | 100 / 100 | 1.472 | 1.056 |
| 4096 | 795.143 | 781.735 | 1.0172× | 100 / 100 | 14.624 | 7.040 |
| 8192 | 1484.748 | 1432.588 | 1.0364× | 100 / 100 | 95.921 | 46.447 |
| 16384 | 2857.385 | 2848.677 | 1.0031× | 100 / 100 | 20.319 | 12.577 |

Decode geometric speedup: **1.0108×**, global tokens 4, 8, 16, 32, 64, 128, 256, 512.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1 | A1 | 67.841 | 1.168 | 68.513, 69.824, 66.497, 67.648 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1 | B1 | 66.385 | 1.264 | 68.609, 66.177, 66.113, 66.016 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | A1 | 93.936 | 1.071 | 93.793, 93.697, 93.985, 94.049 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | B1 | 88.577 | 0.993 | 90.049, 88.320, 88.288, 88.320 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A1 | 119.185 | 1.503 | 116.833, 119.041, 119.746, 120.097 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 116.337 | 1.840 | 117.953, 116.769, 115.009, 116.193 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | A1 | 159.138 | 1.600 | 156.354, 158.914, 159.681, 160.930 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | B1 | 147.345 | 1.025 | 148.065, 147.105, 147.330, 147.105 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | A1 | 196.258 | 1.088 | 197.346, 196.258, 195.489, 196.258 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | B1 | 201.362 | 1.041 | 200.705, 201.857, 201.473, 201.346 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | A1 | 269.443 | 1.120 | 268.803, 268.547, 270.531, 270.307 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | B1 | 259.874 | 1.248 | 258.946, 260.450, 260.642, 260.387 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | A1 | 294.435 | 1.760 | 295.586, 292.387, 293.859, 294.882 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | B1 | 302.755 | 1.727 | 301.250, 302.883, 304.067, 303.331 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | A1 | 320.212 | 1.008 | 319.395, 321.347, 320.675, 320.035 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | B1 | 320.323 | 2.016 | 317.347, 320.451, 321.347, 320.707 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | A1 | 330.323 | 0.896 | 330.275, 329.795, 330.243, 330.659 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | B1 | 331.507 | 1.792 | 328.484, 331.299, 333.123, 332.099 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | A1 | 346.707 | 1.472 | 348.356, 346.723, 345.123, 346.211 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | B1 | 344.692 | 1.056 | 344.099, 344.515, 344.675, 345.763 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4096 | A1 | 795.143 | 14.624 | 779.176, 779.592, 805.447, 812.551 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 4096 | B1 | 781.735 | 7.040 | 776.838, 777.222, 784.551, 810.087 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | A1 | 1484.748 | 95.921 | 1329.867, 1424.908, 1495.244, 1581.133 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | B1 | 1432.588 | 46.447 | 1326.666, 1422.539, 1466.380, 1481.643 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | A1 | 2857.385 | 20.319 | 2486.999, 2870.168, 2861.499, 2852.375 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | B1 | 2848.677 | 12.577 | 2491.475, 2845.653, 2851.094, 2859.765 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 52; independent-reference rank checks: {'A1': 4, 'B1': 4}.

- Repeated AUTO sweeps may select different tactics; pooled timing compares the complete policy.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- One sweep per arm; no within-EP reverse-order confirmation.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
