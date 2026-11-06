# native EP8 comparison

H7168 / I2048 / E256 / top-8; A1 → B1.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 64.944 | 74.113 | 0.8763× | 100 / 100 | 0.992 | 1.264 |
| 2 | 90.945 | 95.201 | 0.9553× | 100 / 100 | 2.271 | 1.089 |
| 4 | 98.849 | 107.728 | 0.9176× | 100 / 100 | 2.144 | 1.232 |
| 8 | 122.961 | 127.329 | 0.9657× | 100 / 100 | 1.552 | 1.856 |
| 16 | 137.234 | 138.176 | 0.9932× | 100 / 100 | 1.408 | 1.728 |
| 32 | 164.977 | 167.730 | 0.9836× | 100 / 100 | 1.792 | 1.488 |
| 64 | 193.745 | 192.257 | 1.0077× | 100 / 100 | 1.760 | 2.224 |
| 128 | 193.522 | 190.209 | 1.0174× | 100 / 100 | 1.280 | 2.001 |
| 256 | 191.746 | 191.442 | 1.0016× | 100 / 100 | 1.984 | 1.584 |
| 512 | 203.169 | 202.464 | 1.0035× | 100 / 100 | 1.536 | 1.504 |
| 4096 | 460.692 | 453.220 | 1.0165× | 100 / 100 | 3.873 | 3.087 |
| 8192 | 786.690 | 778.165 | 1.0110× | 100 / 100 | 15.953 | 19.649 |
| 16384 | 1480.067 | 1495.976 | 0.9894× | 100 / 100 | 16.591 | 67.854 |

Decode geometric speedup: **0.9858×**, global tokens 4, 8, 16, 32, 64, 128, 256, 512.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1 | A1 | 64.944 | 0.992 | 64.576, 65.344, 64.288, 65.408 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1 | B1 | 74.113 | 1.264 | 73.793, 73.568, 73.985, 75.200 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | A1 | 90.945 | 2.271 | 88.737, 90.145, 92.865, 94.369 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 2 | B1 | 95.201 | 1.089 | 95.297, 94.560, 95.201, 95.488 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A1 | 98.849 | 2.144 | 95.809, 97.569, 101.217, 100.801 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 107.728 | 1.232 | 107.585, 107.905, 107.713, 107.744 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | A1 | 122.961 | 1.552 | 121.441, 122.625, 124.545, 124.193 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 8 | B1 | 127.329 | 1.856 | 123.361, 126.752, 128.737, 128.161 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | A1 | 137.234 | 1.408 | 135.105, 137.218, 138.113, 138.145 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 16 | B1 | 138.176 | 1.728 | 135.745, 137.793, 138.849, 139.233 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | A1 | 164.977 | 1.792 | 162.305, 164.417, 165.760, 166.016 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 32 | B1 | 167.730 | 1.488 | 165.761, 167.649, 168.802, 168.290 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | A1 | 193.745 | 1.760 | 189.410, 193.473, 195.489, 193.825 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 64 | B1 | 192.257 | 2.224 | 188.642, 192.673, 194.402, 192.129 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | A1 | 193.522 | 1.280 | 191.970, 193.410, 194.178, 193.442 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 128 | B1 | 190.209 | 2.001 | 187.072, 188.065, 191.424, 191.392 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | A1 | 191.746 | 1.984 | 191.298, 190.498, 190.658, 195.874 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 256 | B1 | 191.442 | 1.584 | 190.115, 191.809, 191.458, 191.522 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | A1 | 203.169 | 1.536 | 201.666, 203.554, 203.298, 203.362 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 512 | B1 | 202.464 | 1.504 | 198.944, 201.921, 202.880, 203.872 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4096 | A1 | 460.692 | 3.873 | 458.724, 460.644, 458.371, 462.595 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 4096 | B1 | 453.220 | 3.087 | 453.987, 452.612, 452.836, 451.555 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | A1 | 786.690 | 15.953 | 773.090, 772.290, 806.817, 810.275 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 8192 | B1 | 778.165 | 19.649 | 764.705, 765.729, 801.250, 819.138 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | A1 | 1480.067 | 16.591 | 1368.835, 1478.020, 1492.900, 1492.131 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| 16384 | B1 | 1495.976 | 67.854 | 1359.724, 1466.178, 1530.979, 1586.990 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 104; independent-reference rank checks: {'A1': 8, 'B1': 8}.

- Repeated AUTO sweeps may select different tactics; pooled timing compares the complete policy.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- One sweep per arm; no within-EP reverse-order confirmation.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
