# V3 TP8 MXFP8 T16384 attribution

The fresh native trace supports optimizing the whole chain, not treating the external fused-baseline gap as an FC1 gather regression. This audit does not establish a new kernel optimization beyond the separately qualified writer-owned FC2 commit.

## Fresh source-bound native trace

Control `82254e206a44b95d9925e4594fac936731f80d21`, public functional API, frozen winner, unfused finalize. Same supported V3 TP8 workload and100 strict CUPTI graph samples in each control phase; no new unprofiled baseline run. `analysis.json` independently verifies200 spans, interval-union extensions, routing hashes, native choices and source/receipt hashes against the final R1 evidence snapshot.

| Component | C1 duration µs | C2 duration µs | C1 extension µs | C2 extension µs |
|---|---:|---:|---:|---:|
| FC1 |480.629|481.476|480.212|481.028|
| FC2 |558.453|561.269|501.156|505.988|
| Combine |333.219|333.779|329.843|330.370|
| Entire chain |1353.868|1362.908|1353.868|1362.908|

Extension accounts for overlapping intervals; component medians must not be summed as an exact median dependency DAG. Routing contributes the remainder. The old326 trace gives the same interpretation; `git diff326c4a79..82254e20 -- flashinfer` is empty. Its benchmark-only selector change does not affect these explicit backend calls.

Every route is local in TP8. FC2 writes1,879,048,192 logical BF16 bytes (1.75GiB), then combine reads the same1.75GiB. The final output is224MiB. Actual padded scratch allocation is2,814,902,272bytes; padding capacity is not useful payload traffic. The old fused MX baseline avoids this explicit intermediate round trip. These logical counts are not measured DRAM bytes and do not by themselves quantify the baseline gap. Source: `blackwell/moe_swap_ab.py:543–574`, `blackwell/moe_finalize.py:162–181`.

## Bounded NCU diagnostics

GPU6 on the same C2 B300 node/image; Nsight Compute2026.1.1.0. Existing `--profile-cuda` benchmark path, frozen cache/routes, application replay, one selected GEMM, clock/cache control `none`; five application replays per stage. Native compiler options unchanged, loaded function resources checked before execution. NCU perturbs overlap, so its durations are not retention evidence.

| Metric | FC1 | FC2 |
|---|---:|---:|
| DRAM reads, bytes |2,162,362,880|590,928,896|
| DRAM writes, bytes |88,401,664|1,829,790,464|
| DRAM throughput, % sustained peak |62.77|68.08|
| L2 throughput, % sustained peak |49.08|49.94|
| Tensor activity, % elapsed peak |48.11|22.72|
| Long scoreboard, % active warp samples |65.72|51.89|
| Barrier, % active warp samples |13.39|20.84|
| Registers/thread |168|112|
| Dynamic shared bytes |206592|185088|
| Native local bytes |0|0|

Both kernels move substantial data. FC2's low tensor fraction and1.83GB measured writes are consistent with its short-K/output-heavy work. Aggregate scoreboard percentages alone do not identify an operand load or a removable synchronization.

## Actual FC1 PCs, not a lookalike specialization

One90-second SourceCounters capture used four application replays. The actual ELF returned by `cute.compile` is identical across all four processes. Driver-loaded function names/resources match NCU; every4376 instruction address maps to the saved native disassembly after explicit printer/address normalization. Original SASS encodings and all records are preserved. There is no Python line-debug metadata: source mapping uses the compiled3-stage/1-acc-stage shared layout and corresponding barrier offsets. See `fc1-pc/pc-proof.json`.

| Wait/issue group | Long-scoreboard samples | Other evidence |
|---|---:|---|
| Epilogue accumulator-full |6783|Barrier at shared+0x60; source3314|
| Gather operand-empty |4140|Three-slot empty ring at shared+0x18; source3474|
| MMA operand-ready first probe |394|Blocking slow path has0 sampled instructions|
| MMA gather-ready first probe |429|Blocking slow path has0 sampled instructions|
| Final CTA join |0|3557/3672 barrier samples; source3562|
| Gather4 issue |0|1551/1631 MIO samples;1706/27253 total samples|

Sample shares are warp observations, not duration shares. The terminal join is distinct from steady-state operand/accumulator synchronization. Static scheduling leaves the scheduler warp inactive in each CTA; only the leader CTA's MMA warp executes MMA. Thus three of24 warps per two-CTA cluster can reach the final join early by design. Removing the join would violate shared/TMEM lifetime protection.

The proposed early MMA readiness hint is **closed on this source**: no sampled blocking slow-wait work was observed, and extra query/cursor state is not justified by the aggregate scoreboard percentage. The accumulator-full and gather-empty waits protect real producer/consumer lifetimes.

## Selected geometry and simple-policy boundary

The native winner is routeN256; FC1 M256/twoCTA, stageK256 (eight native K32 instructions),28 K stages; FC2 M128/oneCTA, stageK128; shared CLC=False. There are632 routed-token tiles and two FC1 channel tiles:1264 work items distributed over74 clusters,17 or18 each. Live token rounding to legal MMA N adds only1.465% arithmetic columns. The source issues the eight K32 MMAs without an inter-instruction software barrier and releases the operand stage afterward (`moe_swap_ab_kernel.py:3165–3269`).

A static estimate from the verified expert histogram shows max rounded-N work13.1% above the mean, despite nearly balanced tile counts. That is a possible load-balance signal, not a measured per-SM critical path. Merely swapping to route-fast traversal raises this estimate to17.5% above the mean, so the simple fixed traversal alternative has no supporting balance evidence. Adding a rotating wave cursor or separate FC1 CLC axis would add policy/state and conflicts with the requested simplicity/search-space goal. No scheduler change is proposed here.

Prior closed leads were checked: payload-before-SF reorder, descriptor prefetch, live-group/row-outer gather, merged/crossed producer roles, lower control register budget, wide256/vector-outer combine and speculative physical stage caps. None is reopened by this trace. Current output TMA remains preferred; the one-line writer-only commit removes real empty work without adding state. Further large TP-prefill gains likely need a separately supported memory/dataflow or scheduling mechanism, not generic barrier deletion.

GPU6 is released. No kernel source was changed by profiling; no further GPU run is pending from this audit.
