# K3 progressive performance comparison

Saved BEFORE and native intermediate use AUTO. Candidate screens reuse the native AUTO winner at each global token count; they do not retune.
CUPTI cold-L2 CUDA graphs, EP8 B300, precomputed routing, PDL, disabled fused TMA/FC2 reduction, deterministic combine. Every number is recomputed from untrimmed raw per-iteration rank-MAX spans.
No samples are pooled across runs or policies. All 13 points are reported; only T1/T2 are excluded from retention. No minimum-process requirement or automatic retention threshold is imposed.

| Arm | Policy | Source commit | Fresh processes per point | Samples per point |
|---|---|---|---:|---:|
| full-base-v2 | AUTO | `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1` | 1 | 100 |
| full-native-v2 | AUTO | `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1` | 1 | 100 |
| residual-prefix-v1 | fixed recorded native winner | `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1` | 1 | 100 |

| Tokens | Retention | full-base-v2 µs | full-native-v2 µs | Native speedup vs BEFORE | residual-prefix-v1 µs | vs BEFORE | vs native |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | no | 84.1930 | 84.9770 | 0.99077× | 81.6650 | 1.03096× | 1.04056× |
| 2 | no | 97.7445 | 93.8885 | 1.04107× | 97.9370 | 0.99803× | 0.95866× |
| 4 | yes | 108.1610 | 113.7610 | 0.95077× | 107.5370 | 1.00580× | 1.05788× |
| 8 | yes | 137.8255 | 136.7220 | 1.00807× | 134.2410 | 1.02670× | 1.01848× |
| 16 | yes | 160.0815 | 158.3220 | 1.01111× | 152.8335 | 1.04742× | 1.03591× |
| 32 | yes | 238.0665 | 235.4425 | 1.01114× | 232.5145 | 1.02388× | 1.01259× |
| 64 | yes | 321.8110 | 323.1070 | 0.99599× | 322.1950 | 0.99881× | 1.00283× |
| 128 | yes | 377.0445 | 376.1320 | 1.00243× | 376.0195 | 1.00273× | 1.00030× |
| 256 | yes | 400.7560 | 400.8210 | 0.99984× | 399.9715 | 1.00196× | 1.00212× |
| 512 | yes | 415.9410 | 411.9095 | 1.00979× | 411.7795 | 1.01011× | 1.00032× |
| 4096 | yes | 593.6060 | 601.4455 | 0.98697× | 580.1980 | 1.02311× | 1.03662× |
| 8192 | yes | 1069.0370 | 1086.7950 | 0.98366× | 1055.1945 | 1.01312× | 1.02995× |
| 16384 | yes | 2089.7810 | 2067.6530 | 1.01070× | 2055.3530 | 1.01675× | 1.00598× |

Speedup = comparator median / arm median; values above 1 mean faster.

## Raw-sample statistics and effective tactics

| Arm | Tokens | Fresh processes | Samples | Median µs | P25 µs | P75 µs | Effective tactic(s) |
|---|---:|---:|---:|---:|---:|---:|---|
| full-base-v2 | 1 | 1 | 100 | 84.1930 | 83.4570 | 84.9690 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 2 | 1 | 100 | 97.7445 | 96.6730 | 98.5050 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 4 | 1 | 100 | 108.1610 | 107.1050 | 109.5610 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 8 | 1 | 100 | 137.8255 | 136.9780 | 138.8570 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 16 | 1 | 100 | 160.0815 | 158.8652 | 160.9458 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 32 | 1 | 100 | 238.0665 | 236.9220 | 239.3942 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 64 | 1 | 100 | 321.8110 | 320.7630 | 322.7310 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 128 | 1 | 100 | 377.0445 | 375.9313 | 378.3490 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 256 | 1 | 100 | 400.7560 | 398.9477 | 402.6140 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 512 | 1 | 100 | 415.9410 | 414.3328 | 417.1242 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 4096 | 1 | 100 | 593.6060 | 588.9738 | 611.8143 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 8192 | 1 | 100 | 1069.0370 | 1026.1730 | 1135.9725 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-base-v2 | 16384 | 1 | 100 | 2089.7810 | 1969.1073 | 2105.1013 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| full-native-v2 | 1 | 1 | 100 | 84.9770 | 84.2403 | 85.7610 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 2 | 1 | 100 | 93.8885 | 92.8010 | 95.2738 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 4 | 1 | 100 | 113.7610 | 112.6970 | 114.9617 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 8 | 1 | 100 | 136.7220 | 135.3780 | 137.4500 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 16 | 1 | 100 | 158.3220 | 157.2010 | 159.7220 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 32 | 1 | 100 | 235.4425 | 233.9470 | 236.6900 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 64 | 1 | 100 | 323.1070 | 321.9070 | 324.0430 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 128 | 1 | 100 | 376.1320 | 375.2200 | 377.0592 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 256 | 1 | 100 | 400.8210 | 398.4370 | 405.3170 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 512 | 1 | 100 | 411.9095 | 411.0370 | 413.5892 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 4096 | 1 | 100 | 601.4455 | 597.5090 | 618.6470 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 8192 | 1 | 100 | 1086.7950 | 1018.1540 | 1120.7397 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| full-native-v2 | 16384 | 1 | 100 | 2067.6530 | 1942.4040 | 2076.6218 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 1 | 1 | 100 | 81.6650 | 80.9287 | 82.6723 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 2 | 1 | 100 | 97.9370 | 96.5050 | 100.0410 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 4 | 1 | 100 | 107.5370 | 106.7777 | 109.0252 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 8 | 1 | 100 | 134.2410 | 133.1857 | 135.8253 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 16 | 1 | 100 | 152.8335 | 151.7460 | 154.0260 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 32 | 1 | 100 | 232.5145 | 231.0900 | 234.0820 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 64 | 1 | 100 | 322.1950 | 320.5480 | 324.6920 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 128 | 1 | 100 | 376.0195 | 374.6278 | 377.1560 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 256 | 1 | 100 | 399.9715 | 397.7882 | 401.9478 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 512 | 1 | 100 | 411.7795 | 410.7720 | 413.0038 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 4096 | 1 | 100 | 580.1980 | 576.7100 | 607.6378 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 8192 | 1 | 100 | 1055.1945 | 1017.7785 | 1126.1862 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| residual-prefix-v1 | 16384 | 1 | 100 | 2055.3530 | 1900.9620 | 2069.7700 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,128,256],"num_sched_stages":2,"token_back_mode":"reuse_dispatch_warps","use_2cta_instrs":true}` |

Complete raw samples, per-process medians, metadata and file hashes are retained in the adjacent JSON.

## Validation

- Every timing record, all eight effective rank tactics, source allowlists, runtime/environment, source patch, saved summaries and recorded-map provenance were checked.
- Packing changes only the epilogue; its formatted native base must have identical AST to the exact measured native source. Count caching and residual-prefix screening each retain exact measured native epilogue bytes and change only their individually reviewed scheduler.
- These are performance receipts, not additional correctness validation. No benchmark or profiler is launched by this report.
