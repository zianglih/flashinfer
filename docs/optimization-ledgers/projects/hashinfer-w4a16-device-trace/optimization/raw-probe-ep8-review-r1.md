# native EP8 comparison

H7168 / I2048 / E256 / top-8; A1 → B1.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64.944 | 79.360 | 0.8183× | 100 / 100 | 0.992 | 1.136 |
| 2 | 90.945 | 95.008 | 0.9572× | 100 / 100 | 2.271 | 2.896 |
| 4 | 98.849 | 98.561 | 1.0029× | 100 / 100 | 2.144 | 1.504 |
| 8 | 122.961 | 125.281 | 0.9815× | 100 / 100 | 1.552 | 1.823 |
| 16 | 137.234 | 137.312 | 0.9994× | 100 / 100 | 1.408 | 1.888 |
| 32 | 164.977 | 170.224 | 0.9692× | 100 / 100 | 1.792 | 2.592 |
| 64 | 193.745 | 195.008 | 0.9935× | 100 / 100 | 1.760 | 2.608 |
| 128 | 193.522 | 197.233 | 0.9812× | 100 / 100 | 1.280 | 3.775 |
| 256 | 191.746 | 191.680 | 1.0003× | 100 / 100 | 1.984 | 1.648 |
| 512 | 203.169 | 203.617 | 0.9978× | 100 / 100 | 1.536 | 1.824 |
| 4096 | 460.692 | 461.187 | 0.9989× | 100 / 100 | 3.873 | 3.809 |
| 8192 | 786.690 | 786.658 | 1.0000× | 100 / 100 | 15.953 | 16.944 |
| 16384 | 1480.067 | 1508.264 | 0.9813× | 100 / 100 | 16.591 | 74.532 |

Decode geometric speedup: **0.9907×**, global tokens 4, 8, 16, 32, 64, 128, 256, 512.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1 | A1 | 64.944 | 0.992 | 64.576, 65.344, 64.288, 65.408 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1 | B1 | 79.360 | 1.136 | 76.512, 78.816, 80.192, 79.936 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | A1 | 90.945 | 2.271 | 88.737, 90.145, 92.865, 94.369 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | B1 | 95.008 | 2.896 | 91.968, 92.480, 96.128, 99.264 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A1 | 98.849 | 2.144 | 95.809, 97.569, 101.217, 100.801 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 98.561 | 1.504 | 95.489, 97.217, 98.945, 99.393 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | A1 | 122.961 | 1.552 | 121.441, 122.625, 124.545, 124.193 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | B1 | 125.281 | 1.823 | 123.010, 124.321, 126.625, 127.522 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | A1 | 137.234 | 1.408 | 135.105, 137.218, 138.113, 138.145 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | B1 | 137.312 | 1.888 | 135.169, 136.129, 137.889, 139.264 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | A1 | 164.977 | 1.792 | 162.305, 164.417, 165.760, 166.016 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | B1 | 170.224 | 2.592 | 164.800, 167.936, 171.712, 172.128 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | A1 | 193.745 | 1.760 | 189.410, 193.473, 195.489, 193.825 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | B1 | 195.008 | 2.608 | 193.920, 194.720, 195.489, 196.673 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | A1 | 193.522 | 1.280 | 191.970, 193.410, 194.178, 193.442 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | B1 | 197.233 | 3.775 | 192.834, 199.522, 197.089, 199.521 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | A1 | 191.746 | 1.984 | 191.298, 190.498, 190.658, 195.874 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | B1 | 191.680 | 1.648 | 187.073, 191.361, 192.514, 192.770 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | A1 | 203.169 | 1.536 | 201.666, 203.554, 203.298, 203.362 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | B1 | 203.617 | 1.824 | 198.112, 203.585, 204.641, 204.352 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4096 | A1 | 460.692 | 3.873 | 458.724, 460.644, 458.371, 462.595 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 4096 | B1 | 461.187 | 3.809 | 465.124, 460.993, 460.483, 459.811 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | A1 | 786.690 | 15.953 | 773.090, 772.290, 806.817, 810.275 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | B1 | 786.658 | 16.944 | 777.314, 777.346, 813.858, 819.266 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | A1 | 1480.067 | 16.591 | 1368.835, 1478.020, 1492.900, 1492.131 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | B1 | 1508.264 | 74.532 | 1372.553, 1480.970, 1547.658, 1589.484 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 104; independent-reference rank checks: {'A1': 8, 'B1': 8}.

- Repeated AUTO sweeps may select different tactics; pooled timing compares the complete policy.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- One sweep per arm; no within-EP reverse-order confirmation.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
