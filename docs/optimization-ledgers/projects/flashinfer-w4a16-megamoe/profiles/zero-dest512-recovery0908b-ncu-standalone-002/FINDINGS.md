# Final512 profiling evidence, 2026-09-08

The ordinary EP8 NSYS capture passes16 worker resource/source records and32 expected Mega actions: T32/T4096, two per device on all8 GPUs. Source e2d88, actual REG128/512threads/two decode WGs/65536 initial CTA registers, raw5/decoded2/acc2. Full reports, SQLite and resource JSON are under the adjacent `zero-dest512-recovery0908b-nsys-001` folder.

- **NSYS scope:** no IKET. In this instrumented trace the fused kernel accounts for98.07%/97.13% of aggregate stage GPU time at32/4096; this supports continuing kernel work, not an end-to-end speedup estimate. Worker warnings about incomplete NVTX events are preserved; every expected GPU action is present. Cross-rank start skew is substantial. NSYS's zero local-memory field does not override the actual function query's112 bytes.
- **NCU recovery:** initial `ncu-001` failed before application startup with `Failed to start TCP communicator` for one peer. `ncu-standalone-002` removes only six multiprocess communicator/lockstep flags in an artifact-only parent adapter. It retains primary benchmark application replay, strict grid matching, one sampling pass, real EP1 descriptors, all source guards and actual REG128 prelaunch admission. CLI help identifies `none` as the default communicator. The unchanged primary source remains frozen.
- **NCU completion:** one workerPID56059, exactly two Mega actions on device0, one application replay pass, actual512threads/REG128 and216576 dynamic shared bytes. All source-correlated metric instance sums equal their aggregates. Both actions have identical embedded source hashes matching current source. Full exported SASS has4736instructions and the same21 FC2 router-metadata local accesses targeted by static unrolling.

| NCU action | Warp samples | Long-scoreboard samples | Selected samples | Wait samples |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 152544 | 86085 | 16888 | 14641 |
| 1 | 152909 | 86276 | 16979 | 14594 |

The two actions have similar PC distributions. The largest sampled sites include the FC1 epilogue accumulator-ready wait, the transform raw-weight-ready branch, raw-stage producer waits and decoded-TMEM stage waits. Inspected SASS confirms these are barrier/control paths: for example, the raw-weight branch atoffset0x8410 follows the precomputed wait predicate and leads to phase-check wait code; offset0x11f70 is the free-decoded-stage wait; offset0x12320 is the FC1 accumulator-ready sleep loop. A long-scoreboard sample on a predicate-dependent branch must not be described simply as an HBM stall.

The source-tagged MMA free-accumulator site has few samples in this EP1 control. This limits any prediction that earlier FC2 release will improve this case. The high-quality release candidate still proceeds to full performance validation; static unrolling independently removes metadata locals. Raw/decoded pipeline dependencies also remain a reason to test the already prepared first-FC2 packed-load preacquire candidate. Role sizes differ, so raw sample percentages cannot rank critical-path importance across roles.

These are mechanism diagnostics. EP1 owns256 local experts and4096 source rows versus EP8's32 experts and512 source rows per rank. Retention and PR tables continue to use complete1–4096 EP8/100-CUPTI sweeps. No profiler duration is a production result.

Artifact-only launch commands and the original/wrapped argv are preserved in `resources/parent-55956.json`, the driver logs and `candidates/w4a16_dispatch_decode_reuse512_ep1_ncu_standalone/run_ncu_002.sh`. `independent-audit-001.json` records source/native/sample conservation and exact top PCs; `pc-samples.json` retains every correlated value.
