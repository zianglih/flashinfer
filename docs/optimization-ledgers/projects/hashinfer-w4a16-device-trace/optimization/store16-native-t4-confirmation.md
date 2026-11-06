# native EP4 comparison

H7168 / I2048 / E256 / top-8; A1 → B1 → B2 → A2.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 122.017 | 112.385 | 1.0857× | 200 / 200 | 1.696 | 1.632 |

Decode geometric speedup: **1.0857×**, global tokens 4.

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 4 | A1 | 121.665 | 1.520 | 121.793, 121.601, 121.665, 121.441 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B1 | 113.713 | 1.232 | 113.249, 114.561, 113.504, 113.697 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | B2 | 111.010 | 1.248 | 110.016, 110.625, 111.233, 111.617 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 4 | A2 | 122.641 | 1.680 | 120.129, 122.081, 123.585, 124.769 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 4; independent-reference rank checks: {'A1': 0, 'B1': 0, 'B2': 0, 'A2': 0}.

- Fixed-tactic diagnostic. Native benchmark emits a null AUTO winner in explicit-knob mode; knobs are attested by the preserved driver and source contract, not a runtime winner record.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- Partial native token matrix; decode summary covers only the listed points.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
