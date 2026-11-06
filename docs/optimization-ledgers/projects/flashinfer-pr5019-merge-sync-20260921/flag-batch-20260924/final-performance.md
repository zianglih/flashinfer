# Fixed F4 versus F8: W4A16 MegaMoE

Each EP host runs F4 sweep 1, F8 sweep 1, F8 sweep 2, F4 sweep 2 (ABBA). Each sweep uses a fresh knob cache and the same eight native AUTO candidates; the external experiment wrapper changes only flag_batch. All other candidate fields, native graph-event autotuning, forward and benchmark timing are unchanged.

Latency is the pooled median of 200 untrimmed rank-MAX CUPTI cold-L2 CUDA-graph activity spans (100 per sweep, three warmups). Native AUTO scores use hot CUDA-graph GPU-event timing and are recorded separately. Workload: global tokens, H7168/I2048/E256/topk8, BF16 inputs, NVFP4 weights, precomputed FP32 routes, unit runtime alpha arrays, routing in FC2 and in-kernel FC2 reduction disabled.

F4/F8 above 1 means F8 is faster. Decode retention uses 4–512 tokens; 1/2 are reported but excluded. Inspect 4K/8K/16K prefill separately. The best-arm estimate selects the lower final pooled median after measurement; it is optimistic and does not demonstrate how a joint 16-candidate AUTO run would select.

## EP4

| Global tokens | F4 µs | F8 µs | F4/F8 | Estimated best arm | Estimated best/F4 speedup |
|---:|---:|---:|---:|---|---:|
| 1 | 73.3445 | 72.4810 | 1.0119× | F8 | 1.0119× |
| 2 | 93.7280 | 92.1775 | 1.0168× | F8 | 1.0168× |
| 4 | 112.7685 | 115.0250 | 0.9804× | F4 | 1.0000× |
| 8 | 151.4900 | 155.3770 | 0.9750× | F4 | 1.0000× |
| 16 | 201.2495 | 203.7465 | 0.9877× | F4 | 1.0000× |
| 32 | 261.6985 | 260.0665 | 1.0063× | F8 | 1.0063× |
| 64 | 293.4265 | 294.0990 | 0.9977× | F4 | 1.0000× |
| 128 | 317.0900 | 320.4990 | 0.9894× | F4 | 1.0000× |
| 256 | 330.2755 | 326.6435 | 1.0111× | F8 | 1.0111× |
| 512 | 341.6510 | 343.7150 | 0.9940× | F4 | 1.0000× |
| 4096 | 828.3890 | 860.1700 | 0.9631× | F4 | 1.0000× |
| 8192 | 1545.8840 | 1590.9090 | 0.9717× | F4 | 1.0000× |
| 16384 | 2927.2830 | 2956.5930 | 0.9901× | F4 | 1.0000× |

Decode geometric mean F4/F8: **0.9926×**. Estimated best-arm gain over fixed F4: **1.0022×**, not a measured joint-AUTO gain.

| Global tokens | F4 sweep 1 tactic | F4 sweep 2 tactic | F8 sweep 1 tactic | F8 sweep 2 tactic |
|---:|---|---|---|---|
| 1 | `G1024/M256N128K256/F4/epi` | `G512/M256N128K256/F4/epi` | `G512/M256N128K256/F8/epi` | `G512/M256N128K256/F8/epi` |
| 2 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G512/M256N64K256/F8/epi` |
| 4 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 8 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 16 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 32 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 64 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 128 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 256 | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 512 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 4096 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F8/dispatch` | `G1024/M256N128K256/F8/dispatch` |
| 8192 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F8/dispatch` | `G1024/M256N128K256/F8/dispatch` |
| 16384 | `G1024/M256N128K256/F4/dispatch` | `G512/M256N128K256/F4/dispatch` | `G512/M256N128K256/F8/dispatch` | `G512/M256N128K256/F8/dispatch` |

`G` = group_hint; `M/N/K` = MMA tile; `F` = flag_batch; `epi`/`dispatch` = token return mode. All ranks agree on each winner and every winner is verified against the native rank-MAX median candidate scores.

| Global tokens | F4 sweep 1 µs | F4 sweep 2 µs | F8 sweep 1 µs | F8 sweep 2 µs | F4/F8 sweep 1 | F4/F8 sweep 2 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 74.4010 | 72.3045 | 72.1290 | 73.0090 | 1.0315× | 0.9904× |
| 2 | 94.2090 | 92.9130 | 92.2245 | 92.1615 | 1.0215× | 1.0082× |
| 4 | 111.4730 | 114.2255 | 112.3690 | 117.2165 | 0.9920× | 0.9745× |
| 8 | 154.3700 | 145.9540 | 154.2095 | 156.4180 | 1.0010× | 0.9331× |
| 16 | 200.3695 | 202.9945 | 204.3860 | 203.3620 | 0.9803× | 0.9982× |
| 32 | 256.0340 | 263.7470 | 258.6420 | 261.5230 | 0.9899× | 1.0085× |
| 64 | 293.6035 | 293.1695 | 296.5790 | 286.3390 | 0.9900× | 1.0239× |
| 128 | 319.3775 | 312.3070 | 322.3390 | 318.7535 | 0.9908× | 0.9798× |
| 256 | 323.5555 | 332.5310 | 330.1145 | 321.5395 | 0.9801× | 1.0342× |
| 512 | 345.4910 | 337.6030 | 347.1230 | 337.9710 | 0.9953× | 0.9989× |
| 4096 | 832.9670 | 804.6470 | 848.4235 | 866.0100 | 0.9818× | 0.9291× |
| 8192 | 1546.5080 | 1543.3525 | 1591.4525 | 1578.2370 | 0.9718× | 0.9779× |
| 16384 | 2934.5690 | 2920.7535 | 2957.4125 | 2955.5725 | 0.9923× | 0.9882× |

Untimed output checks: 208/208 finite rank rows, 208/208 repeat-bit-equal rank rows. Output hashes match across all four runs on 13/13 token rows. These are two eager checks after each measured row, not an independent reference test or validation of every timed replay.

## EP8

| Global tokens | F4 µs | F8 µs | F4/F8 | Estimated best arm | Estimated best/F4 speedup |
|---:|---:|---:|---:|---|---:|
| 1 | 74.1920 | 75.9040 | 0.9774× | F4 | 1.0000× |
| 2 | 92.5605 | 96.6570 | 0.9576× | F4 | 1.0000× |
| 4 | 100.4325 | 106.9440 | 0.9391× | F4 | 1.0000× |
| 8 | 128.3365 | 130.1930 | 0.9857× | F4 | 1.0000× |
| 16 | 144.9920 | 146.6085 | 0.9890× | F4 | 1.0000× |
| 32 | 166.3850 | 164.7850 | 1.0097× | F8 | 1.0097× |
| 64 | 191.1375 | 193.9055 | 0.9857× | F4 | 1.0000× |
| 128 | 199.9525 | 200.0015 | 0.9998× | F4 | 1.0000× |
| 256 | 200.3380 | 197.6805 | 1.0134× | F8 | 1.0134× |
| 512 | 201.5840 | 205.4415 | 0.9812× | F4 | 1.0000× |
| 4096 | 467.2200 | 498.4190 | 0.9374× | F4 | 1.0000× |
| 8192 | 782.1320 | 836.4350 | 0.9351× | F4 | 1.0000× |
| 16384 | 1522.5385 | 1554.1690 | 0.9796× | F4 | 1.0000× |

Decode geometric mean F4/F8: **0.9877×**. Estimated best-arm gain over fixed F4: **1.0029×**, not a measured joint-AUTO gain.

| Global tokens | F4 sweep 1 tactic | F4 sweep 2 tactic | F8 sweep 1 tactic | F8 sweep 2 tactic |
|---:|---|---|---|---|
| 1 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G512/M256N64K256/F8/epi` |
| 2 | `G512/M256N64K256/F4/epi` | `G1024/M256N128K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 4 | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 8 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 16 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G512/M256N64K256/F8/epi` |
| 32 | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 64 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 128 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G512/M256N64K256/F8/epi` |
| 256 | `G1024/M256N64K256/F4/epi` | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 512 | `G1024/M256N64K256/F4/epi` | `G512/M256N64K256/F4/epi` | `G1024/M256N64K256/F8/epi` | `G1024/M256N64K256/F8/epi` |
| 4096 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F8/dispatch` | `G1024/M256N128K256/F8/dispatch` |
| 8192 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F8/dispatch` | `G1024/M256N128K256/F8/dispatch` |
| 16384 | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F4/dispatch` | `G1024/M256N128K256/F8/dispatch` | `G1024/M256N128K256/F8/dispatch` |

`G` = group_hint; `M/N/K` = MMA tile; `F` = flag_batch; `epi`/`dispatch` = token return mode. All ranks agree on each winner and every winner is verified against the native rank-MAX median candidate scores.

| Global tokens | F4 sweep 1 µs | F4 sweep 2 µs | F8 sweep 1 µs | F8 sweep 2 µs | F4/F8 sweep 1 | F4/F8 sweep 2 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 77.5675 | 70.6085 | 75.1845 | 77.1050 | 1.0317× | 0.9157× |
| 2 | 88.4480 | 94.6085 | 98.0965 | 94.0805 | 0.9016× | 1.0056× |
| 4 | 104.2405 | 92.2085 | 98.1930 | 111.0405 | 1.0616× | 0.8304× |
| 8 | 130.2090 | 125.9050 | 122.1605 | 133.1365 | 1.0659× | 0.9457× |
| 16 | 144.9765 | 145.0080 | 147.9845 | 145.6490 | 0.9797× | 0.9956× |
| 32 | 166.5620 | 166.0165 | 165.8895 | 163.8730 | 1.0041× | 1.0131× |
| 64 | 188.2405 | 192.9610 | 189.4255 | 195.6815 | 0.9937× | 0.9861× |
| 128 | 200.0175 | 199.9520 | 202.3845 | 198.2570 | 0.9883× | 1.0085× |
| 256 | 200.8490 | 200.0660 | 189.8730 | 199.8720 | 1.0578× | 1.0010× |
| 512 | 200.3365 | 202.7200 | 205.7300 | 204.3860 | 0.9738× | 0.9918× |
| 4096 | 469.4405 | 465.7480 | 498.2430 | 498.6430 | 0.9422× | 0.9340× |
| 8192 | 786.4190 | 779.2710 | 828.8035 | 855.2015 | 0.9489× | 0.9112× |
| 16384 | 1523.4140 | 1521.1640 | 1548.0410 | 1577.7540 | 0.9841× | 0.9641× |

Untimed output checks: 416/416 finite rank rows, 416/416 repeat-bit-equal rank rows. Output hashes match across all four runs on 13/13 token rows. These are two eager checks after each measured row, not an independent reference test or validation of every timed replay.

Full raw rank spans, native candidate scores, per-sweep medians, MADs, successive 25-sample medians, source/runtime identities and fixture/output hashes are retained in the JSON and evidence directories.
