# Shared SM100 core performance iterations

Candidate checkpoint: `65392416`; C1 B200, 148 SMs. All probes below are task-local diagnostics, not retention evidence. Production benchmark baselines are unchanged.

The direct low-level phase harness `scripts/probe_core_perf.py` uses balanced 16384 local routes, 32 experts, hidden7168, intermediate2048, top-k1. FC1 has4096 output channels andK7168; FC2 has7168 output channels andK2048. Packed FP4 values0x22 and E4M3 scale0x38 avoid routing/quantizer native JIT. Timings use3 warmups,15 samples, coldL2, CUDAgraph and CUPTI. Real benchmark retention requires the13-token full-pipeline AUTO grid.

| Core | Stage | N | FC1 us | FC2 us |
| --- | ---: | ---: | ---: | ---: |
| checkpoint |3|64|890.718|471.712|
| checkpoint |3|128|1034.141|352.031|
| checkpoint |4|64|966.429|445.695|
| checkpoint |4|128|726.781|330.624|
| checkpoint |6|64|865.566|426.496|
| checkpoint |6|128|1026.112|334.463|
| hoist + SF row permutation |3|64|662.302|465.951|
| hoist + SF row permutation |3|128|488.414|348.574|
| hoist + SF row permutation |4|64|589.566|441.919|
| hoist + SF row permutation |4|128|427.838|333.311|
| hoist + SF row permutation |5|64|547.007|428.062|
| hoist + SF row permutation |5|128|432.766|333.184|
| hoist + SF row permutation |6|64|547.647|428.991|
| hoist + SF row permutation |6|128|455.199|336.896|

Increasing persistent CTA grid148→296 slowed FC1 N64 890.718→909.758us and FC2 N64 471.712→518.911us. No production grid change retained.

NCU checkpoint FC1 N64 (`logs/core-perf-ncu-fc1-01.log`, `-02.log`): 90 registers/thread,86.14KB dynamic SMEM, no spills, DRAM8.91%, compute28.81%. Only23.42% scheduler cycles have an eligible warp. Long-scoreboard stalls45.39%, fixed dependency stalls30.46%. The hoist removes route mapping and invariant address loads from each K iteration; the SF permutation maps four-byte stores to all32 banks instead of8 banks. Both preserve physical bytes and arithmetic.

The hoist/permutation passed30 NVFP4 and30 mixedW4A8 random mainloop comparisons exactly, covering partialN, Ktails, and reverse output scattering (`logs/core-hoist-phases-01.log`, `core-hoist-mixed-01.log`). Broader validation remains deferred until retained performance.

B-TMA additionallypassed30 NVFP4+30W4A8 exact random cases, includingN16 physicalN32 offsets and Ktails. FC2 atN128 improves from348.574→325.758us (3stages),333.311→296.992us (4stages),333.184→290.272us (5stages).

SFA-TMA additionallypasses the same60 random cases. Current narrow up16 FC1 probe passes20 perTensor/perToken cases. The first remote FC1 run used a stale up64 probe (hash e95114c6); its failure is invalidated and preserved in core-tma-sfa-fc1-01.log. Synced local narrow probe hash5e06e885 passed in core-tma-sfa-fc1-02.log.

| Core | Stage | N | FC1 us | FC2 us |
| --- | ---: | ---: | ---: | ---: |
| Hoist+TMA B+SFA |4|64|571.359|422.366|
| Hoist+TMA B+SFA |4|128|383.454|296.766|
| Hoist+TMA B+SFA |5|64|476.703|402.015|
| Hoist+TMA B+SFA |5|128|385.470|291.102|

Raw phase/NCU logs throughSFA are backed up in transfer/core-perf/phase-logs-through-sfa.tar.gz.

N256 core support passed12 NVFP4 +12 mixedW4A8 random FP32 comparisons exactly, including actualN1/129/255/257 and Ktails, plus8 perTensor/perToken gatedFC1 comparisons. TMA copies native activation B and preparedweightSFA; SFB uses explicit two128row blocks with independent stage stride. TMEM reserves256acc+16SFA+32SFB columns within512.

| N256 pipeline stages | FC1 us | FC2 us |
| ---: | ---: | ---: |
|3|365.344|260.543|
|4|468.063|247.872|

A sparse directphase diagnostic (4experts,1valid routeperexpert,capacity64,N16,grid148) gaveFC1/FC2 us: stages3=2.688/14.560, stages4=2.752/14.176, stages5=2.848/13.568. This is diagnostic only, not the end-to-end token4 benchmark.

Frozen core policy for the next fullgrid: N16/32/64=5stages;N128=4;N256FC1=3 andFC2=4. Core SHA256 `1e4cf7ce1b961751adf8e7d70ede6574d72726fa038379c41f3e827c309dfa81`. Pythoncompile,Ruffformat/check,andgitdiffcheck pass. No arithmetic/activation/combination change in this iteration.


## Isolated overlap and pipeline experiments after de4f1aa4

All variants live under `scripts/overlap_experiment`; production source was unchanged. These are balanced-route phase diagnostics, not retention results. The common harness uses 16,384 routes, 32 experts, H=7168, I=2048, top-k=1, 148 CTAs, 3 warmups, 15 cold-L2 CUDA-graph/CUPTI samples. The frozen source hash is `1e4cf7ce1b961751adf8e7d70ede6574d72726fa038379c41f3e827c309dfa81`.

| MXFP8 variant | FC1 N128 us | FC1 N256 us | FC2 N128 us | FC2 N256 us |
| --- | ---: | ---: | ---: | ---: |
| Frozen core | 539.777 | 481.120 | 390.529 | 312.896 |
| Epilogue omitted (invalid outputs; lower bound only) | 549.121 | 468.577 | 255.488 | 173.600 |
| Separate loader/epilogue warps, one accumulator | 547.808 | 487.009 | 347.521 | 288.993 |
| Separate warps, two accumulators at N<=128 | 527.233 | 486.399 | 266.400 | 288.066 |
| Doubled K, stages3 at N128/2 at N256 | 485.441 | 547.489 | 374.592 | 344.704 |
| Single MMA completion barrier | 537.407 | 479.680 | 386.944 | 311.423 |

FC1 is dominated by the mainloop. The FC2 epilogue is a substantial cost, and two accumulator buffers at N128 hide most of it; the current shared routing-N contract prevents combining the best FC1 N256 and FC2 N128 results directly. The separate-warps experiment reserves a dedicated 512-byte SF32 reduction scratch buffer because reusing weight SMEM becomes unsafe when loaders advance. Each overlap variant and the doubled-K variant passed 30 paired raw NVFP4 cases, including persistent multi-tile reuse, partial routes and K tails; this is focused evidence, not broad validation. The two-accumulator option remains experimental pending the independent FC2 epilogue comparison.

N256 FC1 stage3→4 regresses MXFP8 481.120→608.928 us; FC2 remains 312.479 us. The earlier NVFP4 stage3→4 regression is consistent. No wider-K or new stage tactic was retained.

NCU (`overlap-ncu-mxfp8-fc1-01.log`) reports 116 registers/thread, no spills, 152.19 kB dynamic SMEM, 34.92% DRAM throughput, 53.53% compute throughput, and 0.24 eligible warps/scheduler. SourceCounters (`overlap-ncu-mxfp8-fc1-source-01.csv/.ncu-rep`) refines the aggregate long-scoreboard interpretation: 7,874 of 13,432 long-scoreboard samples are at the producer AB-empty wait, shared byte offset0x48 for stage3. MMA AB-full waits contribute ~2,307, and accumulator-full waits904. Ordinary LDGSTS/LDG dependency sites are much smaller. SharedStorage puts A barriers at0, AB barriers at48, and AB-empty at72 bytes, confirming the wait identity.

The single-completion variant registers TMA-full expectation after AB acquire, skips the redundant A-empty wait/release/tail, and drains the shared lifetime through AB. It passed30 paired raw cases, but only changes phase timings by about0–3%; the dominant wait reflects underlying MMA/SF progress rather than duplicate completion instruction cost. NVFP4 N128/N256 times are FC1 373.312/366.881 us and FC2 288.897/245.376 us.

Raw overlap/NCU logs through the first completion sweep are archived at `transfer/core-perf/overlap-through-completion-first.tar.gz`; later logs remain labeled on the devbox until the next archive.

Explicit NCU pipe counters (`overlap-ncu-{mxfp8,nvfp4}-pipes-01-raw.csv`) distinguish the generic compute percentage from tensor utilization:

| FC1 N256 frozen core | MXFP8 | NVFP4 |
| --- | ---: | ---: |
| Profile duration, us | 480.832 | 372.896 |
| Tensor pipe active, % of sustained elapsed peak | 46.466 | 29.488 |
| TMEM active, % | 50.664 | 35.557 |
| TC shared data wavefront throughput, % | 35.938 | 24.881 |
| LSU data wavefront throughput, % | 12.005 | 43.907 |
| L1TEX aggregate throughput, % | 39.368 | 43.907 |
| Registers/thread | 116 | 128 |
| Dynamic SMEM, decimal kB | 152.192 | 166.016 |
| Configured SMEM, decimal kB | 167.936 | 167.936 |

The pipes have substantial throughput headroom; these counters do not support a tensor- or shared-bandwidth saturation claim. SourceCounters execute344,064 UTCCP scale-copy instructions and458,752 UTCQMMA instructions for MXFP8, i.e. three SF copies per four MMAs. Mega GenPhase uses the same Cp4x32x128b atom and a single SF buffer; its mainloop additionally prechecks the next full barrier. No SF-buffer redesign was made based on these counters.


## Rejected synchronous SF-vector experiment

`scripts/sfload_experiment/README.md` records an isolated two-CTA overlap FC1 loader experiment. For aligned SF16 K, synchronous128-bit row loads followed by four32-bit shared stores regress NVFP4 N128281.472→496.641us and N256286.400→338.305us. Moving the load before stage acquire improves the variant to354.113/325.471us, still slower. Both variants pass8 paired FC1/per-token byte comparisons; neither was integrated.

The fast baseline's current profile is288.832us,38.776% tensor activity,51.709% TMEM activity and60.614% LSU data throughput. It has94registers/thread andzero observed local-load/store sectors. Its main stall sites remain producer AB-empty and epilogue accumulator-full waits; the MMA/TMA full waits are small. Group2 Gather4 composition should be profiled before more SF-loader changes, since this snapshot still uses cp.async B.
