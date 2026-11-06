# N3U TP8 W4A4 T16384 pipeline profile

Base `82254e20`, C2 B300 original-node GPU3, `nvcr.io/nvidia/pytorch:26.05-py3`, native functional swap-AB/unfused backend with input quantization. Frozen native choice/routes; no retuning or production source change. GPU3 is released.

## Native chain, reused fresh controls

All200 strict-CUPTI samples from the completed R1 control phases are preserved/replayed in `native-components.json`. Component extensions are interval-union contributions; median extensions need not sum to the median chain.

| Component | C1 duration µs | C2 duration µs | C1 extension µs | C2 extension µs |
|---|---:|---:|---:|---:|
| FC1 |472.675|472.451|472.259|472.051|
| FC2 |451.683|450.322|411.027|409.923|
| Combine |273.938|274.098|269.634|269.826|
| Initial quantization |16.864|16.832|—|—|
| End to end |1181.880|1180.295|1181.880|1180.295|

FC2 writes1.375GiB of live BF16 intermediate and combine reads the same; final output is64MiB. Scratch allocation is2,011,168,768bytes; allocation padding is not useful traffic. Fused legacy paths avoid that round trip, so the external baseline gap cannot be assigned solely to FC1 gather.

## Bounded NCU diagnostics

Five application replays per metrics capture and four for SourceCounters, no clock/cache control, unchanged native compile options and actual returned ELF capture. These durations are diagnostic and not retention timing. All actual images have zero local bytes.

| Metric | FC1 | FC2 |
|---|---:|---:|
| DRAM read bytes | 3.89265e+08 | 5.56002e+08 |
| DRAM write bytes | 1.54627e+08 | 1.45112e+09 |
| DRAM throughput % | 14.9 | 62.81 |
| L2 hit % | 76.46 | 45.48 |
| L2 throughput % | 39.96 | 52.63 |
| Tensor activity % | 16.24 | 19.9 |
| Issue activity % | 29.71 | 12.72 |
| Long scoreboard % | 54.44 | 47.45 |
| MIO throttle % | 9.81 | 2.6 |
| Barrier % | 8.9 | 28.17 |
| Initial registers/thread | 168 | 122 |
| Dynamic shared bytes | 222208 | 228352 |

FC1 is M128/N256/oneCTA with4 operand stages and Ktile256; FC2 M256/N256/twoCTA with5 stages and Ktile256. N3U TP has hidden2048, local intermediate640, top22, ReLU2,512 local experts. There are1667 route tiles and5 FC1 channel tiles:8335 FC1 work items. Legal N16 rounding adds1.0742% columns. FC1 executes8 K stages; FC2 has3, including a128-element K tail. The existing pipeline keeps stages across work tiles; this does not justify blindly capping stages to a tile’s K count.

Full FC2 slabs already use Ld16x256→BF16 conversion→stmatrix.trans→TMA. Compiled64-token/two-stage bulk buffers cover95.15% of live rows; only4.85% use SIMT tails. Rubin’s packed64 MOVM/TMEM scheme applies to a different output ownership, not a missing transpose optimization in this dominant full-slab path.

## Actual FC1 PC attribution

Every4104 NCU instruction address matches the exact returned ELF after explicit printer/address normalization; all four SourceCounters replays and the separate metric replays use the same FC1 cubin. No Python debug-line metadata was introduced. Mapping uses the4-stage/one-accumulator barrier layout and emitted branch/call targets. `MOV.SPILL` here transfers uniform registers, and the loaded function has zero local memory.

| Group | Long-scoreboard samples | MIO samples | Total samples |
|---|---:|---:|---:|
|epilogue_accumulator_full_probe|1651|0|1663|
|epilogue_accumulator_full_slow|256|0|272|
|mma_operand_ready_probe|62|0|85|
|mma_operand_ready_slow|0|0|0|
|mma_gather_ready_probe|1403|0|1410|
|mma_gather_ready_slow|0|0|0|
|gather_operand_empty_probe|1008|0|1078|
|gather4_issue|0|227|474|
|sf_cp_async|0|1731|1824|
|sf_cp_async_completion|0|255|301|
|epilogue_body|4926|354|9892|
|gather_body|4771|2270|9913|

Body/wait rows overlap. Samples are warp observations, not duration shares. The terminal CTA join accounts2765/2775 barrier samples; it is distinct from steady-state synchronization and cannot be removed while TMEM/shared state remains in use. SF cp.async plus completion contributes1986/2934 MIO samples, compared with227 at Gather4 issue. Epilogue and gather bodies have similar total samples, so this does not establish an exclusively epilogue-bound kernel.

Compared with V3 TP MXFP8, N3U FC1 has much lower DRAM throughput14.90% vs62.77% and tensor activity16.24% vs48.11%. The stronger scale-copy/issue signal is consistent with its shorter K,5 channel tiles, and repeated routed input transport. FC2 remains output/memory-heavy:1.451GB measured writes,62.81% DRAM throughput,19.90% tensor activity. Aggregate stalls alone do not justify new scheduler state or weaker barriers.

## Candidate boundary

No new kernel optimization is proposed by this profile. Prior shared-FP32 transpose, LD.RED, payload-before-SF issue, wider direct SF copies, and readiness-hint leads remain closed. Canonical SF layout places contiguous global words512bytes apart in shared memory, so wider direct cp.async/TMA is not a drop-in vectorization. The hypothetical64-token FP32 FC1 batch is assessed in `FC1_BATCH64_FEASIBILITY.md`: not previously measured in the searched ledgers, but it increases live values and complicates32-column early-release boundaries without an isolated bottleneck signal.

The first NCU attempt failed in argparse because the helper used an invalid profiler selector; it performed no GPU work. Corrected helpers use existing `--backends cutedsl --profile-backend cute-dsl`; the failed attempt and its receipts remain preserved. No sanitizer or new accuracy run was performed as part of profiling.
