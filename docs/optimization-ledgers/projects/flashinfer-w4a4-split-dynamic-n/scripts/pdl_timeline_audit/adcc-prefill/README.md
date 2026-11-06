# Fully all-thread PDL: final prefill timeline

The all-thread candidate restores both GEMM register counts to the control values, but its combine kernel still starts well before FC2 ends. In this one warmed replay, most of the remaining graph-span difference falls after the FC2 endpoint. This identifies where the visible tail remains; it does not establish slower useful combine work or a cache cause.

## Frozen source and method

Read-only diagnostic on 2026-10-25, GPU3 of `fi-w4a4-narrow-1025`, c1/ziangli, B200 UUID `GPU-8f15506e-8209-ef53-6b00-b04ece9e69d3`. Control is clean `profile-aab93f`, commit `aab93f854054de834447bdd8985b8bbd653fb3c8`. Candidate is actual `pdl-allthread-review`, the same base with exactly two unstaged files: core SHA256 `adcc6506dd4ba28769cf7a5f65526e9dc927363847150de231eb850cc6c9b4b9`, preparation `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. All sources, supporting imports and source-owner FC1/FC2 exact receipts passed before execution. No kernel or production source was changed.

Native DeepSeek NVFP4 T16384, H7168/I2048, 32 local experts, top-k8, seed42 routing, unfused finalization. Both GEMMs use M256/N256/two-CTA geometry, a persistent grid of 148 CTAs (74 clusters), and the established one-CTA-per-SM launch policy. The route has 77 tiles and 16,280 valid rows. The helper is byte-identical to the preceding ac1 trace helper: `5573c1f111005aa7eb7c0803582fb3c87673f2781a46083bcf1c792e4e7d8cc5`.

Ten ordinary warmups and ten graph replays precede **one profiler-range replay per arm**, control then candidate, in the same process with actual module dispatch and independent caches. Native input hashes and final output bytes match before/after each trace; source hashes remain unchanged. These are warm diagnostic Nsight timestamps, **not cold-L2 benchmark medians**, and no primary measurements were repeated. `command.json` in the raw archive records the exact invocation/environment. Nsight Systems is 2026.2.1.210; CUDA 13.2.78, CuTe 4.7.1, and the existing candidate native-cache epoch are unchanged.

## Observed intervals

Microseconds relative to each arm's routing-kernel start:

|Kernel|Control start|Control end|Control duration|Candidate start|Candidate end|Candidate duration|
|---|---:|---:|---:|---:|---:|---:|
|Routing|0.000|25.120|25.120|0.000|25.152|25.152|
|Sort initialization|24.128|25.888|1.760|24.160|25.728|1.568|
|Sort|25.696|33.664|7.968|25.632|33.376|7.744|
|Routed preparation|33.472|60.512|27.040|33.152|59.584|26.432|
|FC1|59.520|260.993|201.473|55.424|262.080|206.656|
|FC2|260.417|405.121|144.704|232.512|408.256|175.744|
|Combine|404.545|485.185|80.640|263.264|496.192|232.928|

Kernel-lifetime overlap grows from 0.992 to 4.160 us for preparation→FC1, 0.576 to 29.568 us for FC1→FC2, and 0.576 to 144.992 us for FC2→combine. Those intervals include dependency waits and setup. They do not measure concurrent useful tensor computation.

The graph span is 485.185→496.192 us, a diagnostic difference of **11.007 us**. Exact endpoint arithmetic partitions that difference as follows:

|Endpoint segment|Control|Candidate|Difference|
|---|---:|---:|---:|
|Routing start → FC1 end|260.993|262.080|+1.087|
|FC1 end → FC2 end|144.128|146.176|+2.048|
|FC2 end → combine end|80.064|87.936|+7.872|

The final segment contributes most of this observed span difference. It is **not** a direct measure of combine's post-wait useful work: individual consumer CTAs can perform setup before the producer's last CTA exits, and no per-CTA/PC dependency-wait timestamps were collected. The candidate combine launch near FC1 completion is consistent with the early FC2 trigger opening its downstream launch window while FC2 remains in flight.

## Resources and interpretation boundary

FC1 registers are **80/80**, FC2 **120/120**, combine **80/80**, and preparation **32/32**. FC1 requests 195,584 B dynamic shared memory; FC2 requests 229,888 B. Both use 288 threads, cluster `(2,1,1)`, 148 CTAs and a reported maximum of 74 active clusters. Their respective `sharedMemoryExecuted` fields are 200,704 and 233,472 B. All of these fields match between arms. Both GEMMs report zero local memory per thread. The raw `localMemoryTotal` field is retained but is not interpreted as spilled bytes.

The two GEMMs' shared-memory demands cannot fit together on one B200 SM, so their kernel-lifetime overlap does not imply same-SM GEMM co-residency. Combine requests zero static/dynamic shared memory and 128 threads, but Nsight reports `sharedMemoryExecuted=32768` for it in both arms; that field is preserved without inventing per-CTA residency semantics. The trace cannot distinguish combine admission on freed SMs from any co-residency elsewhere. All QMD completion timestamps are NULL.

There is no current evidence here of future payload loads before the GEMM dependency waits. The unchanged combine source preloads mapping/scales before its wait, then reads FC2 payload afterward. This trace supports investigating *when* the producer signals downstream startup, rather than attributing the remaining gap to the repaired register counts. It does not prove that waiting combine CTAs caused the regression, or identify instruction/cache/DRAM contention. The parent's producer-drain signaling audit remains a separate, source-checked hypothesis.

## Evidence and closure

- [summary.json](summary.json) contains all node names, raw timestamps, resources, exact source identities and endpoint arithmetic; [summarize.py](summarize.py) reproduces it from the SQLite exports.
- [source-manifest.json](source-manifest.json), [source-snapshots](source-snapshots), `remote-program.py`, `remote-command.json`, and `run.log` preserve execution provenance.
- [evidence/fetch-receipt.json](evidence/fetch-receipt.json) verifies all 14 raw files, including both `.nsys-rep` reports, SQLite exports, graph DOTs, source-owner exact gate and pre/post GPU receipts. Archive SHA256: `24e892d8218b87d8e59bc2f3032bd529e4104e67d593e5b921dfb5fa75859af9`.
- CUDA graph edge-type/port metadata was deliberately **not queried** because the earlier binding extraction was invalid. DOT/node identities and actual observed overlap remain evidence; no complete edge-type claim is made.
- The postflight process list is empty. GPU3 is released. Earlier traces and all frozen sources are preserved.
