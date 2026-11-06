# native EP4 comparison

H7168 / I2048 / E256 / top-8; A1 → B1.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67.889 | 71.553 | 0.9488× | 100 / 100 | 0.816 | 0.767 |
| 2 | 95.041 | 94.913 | 1.0013× | 100 / 100 | 1.024 | 1.375 |
| 4 | 116.368 | 114.545 | 1.0159× | 100 / 100 | 1.488 | 2.112 |
| 8 | 159.569 | 146.289 | 1.0908× | 100 / 100 | 1.360 | 0.848 |
| 16 | 195.458 | 207.905 | 0.9401× | 100 / 100 | 0.944 | 1.215 |
| 32 | 262.723 | 262.498 | 1.0009× | 100 / 100 | 1.312 | 1.232 |
| 64 | 289.122 | 295.458 | 0.9786× | 100 / 100 | 1.136 | 1.183 |
| 128 | 323.779 | 321.523 | 1.0070× | 100 / 100 | 1.472 | 0.993 |
| 256 | 324.131 | 329.747 | 0.9830× | 100 / 100 | 1.312 | 3.040 |
| 512 | 344.452 | 343.763 | 1.0020× | 100 / 100 | 1.200 | 0.976 |
| 4096 | 787.415 | 775.191 | 1.0158× | 100 / 100 | 8.912 | 5.264 |
| 8192 | 1458.622 | 1441.626 | 1.0118× | 100 / 100 | 37.168 | 64.481 |
| 16384 | 2858.552 | 2860.121 | 0.9995× | 100 / 100 | 11.969 | 15.684 |

Decode geometric speedup: **1.0015×**, global tokens 4, 8, 16, 32, 64, 128, 256, 512.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1 | A1 | 67.889 | 0.816 | 67.489, 67.777, 68.001, 68.096 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1 | B1 | 71.553 | 0.767 | 70.881, 71.520, 71.904, 71.553 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | A1 | 95.041 | 1.024 | 94.241, 96.033, 95.296, 94.784 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | B1 | 94.913 | 1.375 | 94.881, 94.945, 93.697, 95.937 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A1 | 116.368 | 1.488 | 116.929, 116.609, 116.545, 115.073 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 114.545 | 2.112 | 112.321, 113.185, 115.426, 116.481 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | A1 | 159.569 | 1.360 | 156.833, 159.777, 160.161, 160.289 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | B1 | 146.289 | 0.848 | 146.913, 146.209, 146.113, 146.144 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | A1 | 195.458 | 0.944 | 195.234, 195.426, 195.554, 195.586 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | B1 | 207.905 | 1.215 | 204.962, 208.706, 208.450, 208.034 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | A1 | 262.723 | 1.312 | 260.450, 263.587, 263.010, 263.938 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | B1 | 262.498 | 1.232 | 263.522, 262.690, 262.210, 262.050 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | A1 | 289.122 | 1.136 | 289.827, 289.603, 288.354, 288.642 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | B1 | 295.458 | 1.183 | 295.426, 294.850, 295.619, 295.874 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | A1 | 323.779 | 1.472 | 320.611, 325.156, 324.419, 324.164 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | B1 | 321.523 | 0.993 | 322.178, 321.955, 320.770, 320.963 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | A1 | 324.131 | 1.312 | 324.482, 323.683, 324.099, 324.867 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | B1 | 329.747 | 3.040 | 330.403, 329.122, 329.570, 329.955 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | A1 | 344.452 | 1.200 | 345.315, 344.483, 343.939, 344.420 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | B1 | 343.763 | 0.976 | 343.747, 343.587, 343.843, 343.875 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4096 | A1 | 787.415 | 8.912 | 781.351, 781.575, 793.415, 814.854 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 4096 | B1 | 775.191 | 5.264 | 773.064, 770.216, 775.880, 800.966 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | A1 | 1458.622 | 37.168 | 1337.582, 1422.351, 1467.983, 1510.895 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | B1 | 1441.626 | 64.481 | 1328.458, 1409.418, 1504.363, 1506.988 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | A1 | 2858.552 | 11.969 | 2612.538, 2865.785, 2864.249, 2859.609 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | B1 | 2860.121 | 15.684 | 2477.081, 2868.117, 2860.469, 2864.821 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 52; independent-reference rank checks: {'A1': 4, 'B1': 4}.

- Repeated AUTO sweeps may select different tactics; pooled timing compares the complete policy.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- One sweep per arm; no within-EP reverse-order confirmation.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
