# SM100-family versus native SM103 on B300

Both arms use the same source. A is `sm_100f`; B is native `sm_103a`. The normal B300 trace already uses SM103a. This study does not add an SM103 enablement patch.

Decision: keep the current automatic native target. Both native decode geometric means and the uniform128 ratio change direction between the first and reverse orders; the pooled uniform result is not a reproducible speedup claim. See [order/tactic details](final-summary-1.md) and [the decision](DECISION.md).

Tested HashInfer `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`.

Each arm pools all 200 cold-L2 CUDA-graph CUPTI rank-MAX samples from its two ABBA runs. Speedup = SM100f latency / SM103a latency; above 1 favors native SM103a. No samples are trimmed. Native AUTO runs freshly for every shape and sweep; winners may differ.

| Global tokens | EP4 SM100f µs | EP4 SM103a µs | Ratio | EP8 SM100f µs | EP8 SM103a µs | Ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 73.152 | 74.049 | 0.9879× | 71.456 | 77.345 | 0.9239× |
| 2 | 93.008 | 98.417 | 0.9450× | 95.041 | 94.385 | 1.0070× |
| 4 | 116.785 | 118.481 | 0.9857× | 107.377 | 104.576 | 1.0268× |
| 8 | 153.089 | 151.985 | 1.0073× | 126.338 | 126.337 | 1.0000× |
| 16 | 207.506 | 203.762 | 1.0184× | 139.889 | 146.577 | 0.9544× |
| 32 | 265.763 | 265.954 | 0.9993× | 171.681 | 164.418 | 1.0442× |
| 64 | 292.995 | 302.210 | 0.9695× | 188.050 | 190.001 | 0.9897× |
| 128 | 321.428 | 325.522 | 0.9874× | 198.673 | 192.450 | 1.0323× |
| 256 | 326.755 | 331.091 | 0.9869× | 200.338 | 198.993 | 1.0068× |
| 512 | 353.268 | 352.435 | 1.0024× | 201.568 | 202.752 | 0.9942× |
| 4096 | 794.312 | 796.054 | 0.9978× | 466.564 | 471.986 | 0.9885× |
| 8192 | 1440.299 | 1451.868 | 0.9920× | 775.844 | 800.708 | 0.9689× |
| 16384 | 2861.127 | 2854.070 | 1.0025× | 1505.209 | 1494.422 | 1.0072× |

| Summary | SM100f / SM103a |
|---|---:|
| EP4, native decode 4–512 geometric mean | 0.994497× |
| EP8, native decode 4–512 geometric mean | 1.005684× |

Separate trace workload: EP4 H6144/I2048/E256/top8, uniform routing,128 global tokens (32 per rank).

| Workload | SM100f µs | SM103a µs | Ratio |
|---|---:|---:|---:|
| Uniform128 | 279.842 | 287.251 | 0.9742× |

Standard sweep: H7168/I2048/E256/top8 with precomputed seeded grouped routing. Full forward includes runtime alpha copies, staging, collective compute/communication and finalization. Preparation, routing, compilation, tuning, graph capture and L2 flushing are excluded.

Independent reference checks cover global128 in each workload; every row also has finite/repeated output checks and paired cross-arm output hashes. Timed replays are not individually reference checked. This is a B300 compilation-target comparison, not a B200 hardware benchmark.

See the input audit JSON/Markdown for raw per-run distributions, first/reverse order ratios, selected tactics, source and binary proof, and limitations.
