# uniform-target EP4 comparison

H6144 / I2048 / E256 / top-8; B1 → A1.

cold-L2 CUDA-graph CUPTI; median of all pooled per-iteration rank-MAX samples. A is before; B is after.

| Global tokens | Before µs | After µs | Speedup | Samples/arm | Before MAD µs | After MAD µs |
|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 336.163 | 337.299 | 0.9966× | 100 / 100 | 1.552 | 1.343 |

## Individual sweeps and dispersion

| Global tokens | Sweep | Median µs | MAD µs | Quarter medians µs | Tactic |
|---:|---|---:|---:|---|---|
| 1024 | B1 | 337.299 | 1.343 | 337.219, 338.594, 336.515, 336.994 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |
| 1024 | A1 | 336.163 | 1.552 | 333.923, 336.739, 336.995, 336.162 | `{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}` |

## Evidence and limits

Weight and input/routing fixture hashes match across every sweep.
Paired output rank/shape rows: 4; independent-reference rank checks: {'B1': 4, 'A1': 4}.

- Fixed-tactic diagnostic. Native benchmark emits a null AUTO winner in explicit-knob mode; knobs are attested by the preserved driver and source contract, not a runtime winner record.
- Fixture parity is not independent numerical validation, and logs alone do not prove source/process closure.
- No samples trimmed or selected; ABBA does not guarantee removal of temporal drift.
- One sweep per arm; no within-EP reverse-order confirmation.
- Separate uniform trace workload; excluded from native decode geometric mean.

Raw samples, complete tactic dictionaries and log SHA256 hashes are preserved in the companion JSON.
