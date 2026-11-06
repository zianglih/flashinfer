# Current five-warpgroup NSYS findings

PASS for the expected saved capture scope on source f377, hu-pdx-115, eight B300 SM103 GPUs, NSYS2026.2.1.210. Original execution exited0 in137.482s; source and all76 native cache entries remain unchanged. The sorted profile native JSON has different bytes from the completed owner but identical entry objects, including the JIT log. No native inventory entry is excluded.

Both SQLite files pass integrity checks. Each token count contains all eight devices with two Mega actions per device, 16 routing kernels, 16 input-ID copy kernels, 16 reducers and32 correlated memcpy actions; 32 expected NVTX stage ranges are present. Device/PID pairs match all16 worker records. The actual function records independently pass REG96/640/two decode/pool61440/local0 and the original nested shared/MRO gate. The single parent replaces exactly one benchmark-script argument in each of its two original launches.

| Global tokens | Routing mean µs | Input-ID kernel mean µs | Mega mean µs | Reducer mean µs | Mega share of kernel time | Two memcpy actions mean µs/rank/iteration |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 3.546 | 1.800 | 430.749 | 2.492 | 98.213% | 3.306 |
| 4096 | 4.130 | 3.170 | 804.663 | 9.794 | 97.920% | 6.072 |

The source mapping is the existing W4A16 backend staging call into `bf16_bf16_bf16_cutedsl/staging.py`: BF16 hidden-state copy, top-k ID copy into the integer workspace, and FP32 top-k weight copy. The two memcpy sizes independently match hidden states plus weights:57,344/128 bytes at T32 and7,340,032/16,384 bytes at T4096, each16 times. The ID copy is the single elementwise staging kernel. This excludes work executed internally by the fused Mega kernel.

Shares use the sum of the four kernel categories across ranks/actions, not wall time; memory copies and host/launch gaps are separate. The external routing, input-ID copy and reducer kernels total7.838µs at T32 and17.094µs at T4096 on average. The reducer is0.568% /1.192% of summed kernel time. This supports keeping external reducer arithmetic a secondary lead in this trace; it does not bound the internal fused roles or establish primary-performance savings.

| Global tokens | Iteration | Mega start spread µs | Mega finish spread µs | Fastest rank duration µs | Slowest rank duration µs |
| --- | ---: | ---: | ---: | ---: | ---: |
| 32 | 0 | 693.007 | 0.472 | 186.050 | 878.950 |
| 32 | 1 | 274.131 | 0.314 | 184.673 | 458.690 |
| 4096 | 0 | 842.296 | 1.253 | 473.029 | 1314.506 |
| 4096 | 1 | 582.012 | 1.384 | 470.885 | 1052.168 |

The much wider launch spread than finish spread is consistent with inter-rank rendezvous contributing to the apparent duration of early-arriving kernels. This is an inference from timestamps, not a stall attribution. Mean input-ID-copy-end→Mega-start gaps are382.227µs /410.900µs; Mega-end→reducer-start gaps are64.585µs /17.878µs. These instrumented host/launch gaps cannot be assigned to primary overhead, subtracted from latency or used as a four-versus-five-warpgroup comparison. The trace lacks internal decode/MMA/dispatch/epilogue ranges, so role-specific memory/SASS evidence is still needed to select a general kernel optimization.

All eight workers in each capture warn that not all NVTX events may have been collected. The expected stage/action counts and rank mappings above were independently checked despite that warning. Other CUDA/NVTX-start warnings belong to auxiliary non-worker PIDs. There are no severity3 errors or reported CUDA loss/overflow diagnostics; this is not a universal assertion that every event was captured. Profiler CUPTI comes from the NSYS injection stack and these two eager, instrumented actions are separate from the100-sample CUDA-graph CUPTI benchmark. No primary latency or historical4WG speedup claim follows.

All raw stage kernels, memory actions, GPU metadata, diagnostics and32 per-rank iteration records are retained in [details.json](details.json). Exact input hashes, distributions and counts are in [receipt.json](receipt.json).
Receipt SHA `0af81d6ac0c5f869529a9547a1e64a81a40dbf36704360d4409214c1cc44f901`; details SHA `05c407899710d87590a7baacfdf7f79d9c2c485a1586f47690a0814c862f6622`.
