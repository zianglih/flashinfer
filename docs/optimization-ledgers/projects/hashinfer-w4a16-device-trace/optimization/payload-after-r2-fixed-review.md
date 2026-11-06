# uniform-target EP4 comparison

H6144 / I2048 / E256 / top-8; A1 → B1 → B2 → A2.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 330.499 | 331.650 | 0.9965× | 200 / 200 | 1.392 | 2.017 |

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1024 | A1 | 330.851 | 1.440 | 330.595, 331.043, 330.819, 330.723 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1024 | B1 | 333.203 | 1.552 | 331.075, 333.923, 332.867, 333.251 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1024 | B2 | 330.291 | 1.232 | 330.147, 330.082, 330.562, 330.530 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1024 | A2 | 330.226 | 1.392 | 330.914, 330.178, 330.243, 330.242 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 4; independent-reference rank checks: {'A1': 4, 'B1': 4, 'B2': 4, 'A2': 4}.

- Fixed-tactic diagnostic. Native benchmark emits a null AUTO winner in explicit-knob mode; knobs are attested by the preserved driver and source contract, not a runtime winner record.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- Separate uniform trace workload; excluded from native decode geometric mean.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
