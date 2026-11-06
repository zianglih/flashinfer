# native EP8 comparison

H7168 / I2048 / E256 / top-8; A1 → B1 → B2 → A2.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 104.416 | 107.201 | 0.9740× | 200 / 200 | 3.216 | 1.759 |

Decode geometric speedup: **0.9740×**, global tokens 4.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 4 | A1 | 102.177 | 1.008 | 101.856, 101.504, 102.561, 102.593 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 106.657 | 1.473 | 104.288, 106.305, 107.457, 107.201 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B2 | 107.793 | 1.856 | 106.369, 106.849, 108.992, 109.792 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A2 | 109.216 | 1.888 | 104.960, 107.937, 110.752, 110.337 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":1024,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 8; independent-reference rank checks: {'A1': 0, 'B1': 0, 'B2': 0, 'A2': 0}.

- Fixed-tactic diagnostic. Native benchmark emits a null AUTO winner in explicit-knob mode; knobs are attested by the preserved driver and source contract, not a runtime winner record.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- Partial native token matrix; decode summary covers only the listed points.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
