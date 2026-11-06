# Isolated K640 paired-error NCU comparison

The rejected packed-error implementation has an intrinsic execution cost on this captured K640 workload: fewer instructions do not translate into higher issue throughput. The previously sealed isolated CAAC is **430.106 → 488.915 µs (+13.673% duration; −12.029% speedup)** with no successor FC2. This two-report NCU diagnostic points to changed arithmetic scheduling / execution-pipe pressure; it does not establish a hardware latency model or explain every whole-chain effect.

| Counter | Retained c1ac | Rejected 5f232629 |
|---|---:|---:|
| Executed warp instructions | 392,910,772 | 353,294,644 |
| Issue active (%) | 78.96 | 73.64 |
| Math-pipe throttle (%) | 5.82 | 8.62 |
| Fixed-latency dependency wait (%) | 12.99 | 14.39 |
| Long scoreboard (%) | 24.35 | 24.4 |
| Short scoreboard (%) | 6.97 | 6.84 |
| Barrier (%) | 4.77 | 5.34 |
| Active warps / SMSP | 6.72 | 6.9 |
| DRAM read bytes | 462,422,784 | 463,108,096 |
| DRAM write bytes | 173,547,264 | 173,473,280 |
| L1 global-load sectors | 30,414,976 | 30,414,976 |
| DRAM peak throughput (%) | 19.13 | 16.77 |
| L2 hit rate (%) | 16.42 | 16.38 |

Native resources: **61 → 48 registers**, LOCAL/STACK0, theoretical active-block cap16 →20. The grid remains2368 blocks (148×16), block64, so the higher capacity does not automatically provide more independent CTAs. Measured active warps rise only6.72 →6.90. Static instructions768 →720, non-NOP743 →695, NOP25 in both. The independent application replay durations433.248/494.848 µs are profiler observations, not new production timing samples.

## Actual PC evidence

Every decoded PC matches the actual loaded native image:768 control and720 candidate PCs. PC samples use the same sampling interval4096 cycles; they are warp observations and dependent-consumer attribution, **not execution-time fractions**. The two reports have30,379/29,740 total samples.

| Sites | Static count C/A | Math-stall samples C/A | Dependency-wait samples C/A |
|---|---:|---:|---:|
| Scalar subtract → packed subtract |32 /16|1 /112|23 /79|
| Scalar ordered accumulation → packed accumulation |32 /16|10 /160|107 /93|
| Error square: scalar self-multiply → packed square |32 /16|3 /110|31 /51|
| Existing HMUL2 conversion arithmetic |16 /16|31 /253|9 /79|

The square row matches the32 scalar self-multiplications in the control error region to16 candidate packed squares. Both versions also retain52 scalar multiplies outside this recurrence. These counts are not instruction latency measurements. Exact groups/PCs and dynamic instruction counts are in `pc-opcode-groups.json`.

The final packed accumulator at0x21d0 (`FADD2 R4, R4.F32x2.HI_LO, R10.F32x2.HI_LO`) has33 math /26 wait samples; packed subtract at0x1f70 has16 /15. The packed squares also show pressure (e.g.0x2060:22 math samples). Existing HMUL2 at0x1a10 has146 math samples, so the change perturbs surrounding scheduling as well. The principal long-scoreboard consumer remains the loaded-input `LOP3` at control0x7c0 /candidate0x7e0 (7159/7419 samples); global-load sectors are exactly equal and DRAM byte traffic changes <0.15%. No evidence supports additional loads, spills, NOP growth, or a new barrier as the explanation.

The measured aggregate arithmetic/issue changes support an intrinsic execution-pressure explanation. Whether packed instruction issue restrictions, the paired dependency chains, register allocation/scheduling, or their combination dominates is **not established by sampling**. In particular, packed accumulation has fewer raw wait samples than both original scalar accumulators combined; these data cannot isolate accumulator latency as the sole cause. NVIDIA defines fixed-latency dependency wait and math-pipe throttle separately in its [Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html).

## Method and closure

- Exactly two Nsight Compute2026.1.1 reports, control then candidate on recovery GPU3 (`GPU-ee4aef4a-e7f5-91fb-213c-d87a88482df1`), application replay/grid matching, one selected quantizer kernel,17 application invocations per arm. SourceCounters/compute/memory counters were collected together; no extra PC campaign.
- Every invocation normally loads the arm-private cached object, extracts its installed `kernels_binary` symbol, and matches cubin control `ff00cf52bf25550ace511512220c9baf801c3cfd55d29524e6026c1cfec05ba0` or candidate `83a6345e216e785a56e0d9a01269639584808dfa81581d2c48ad1604bd1bcfab`. No compiler execution was observed. Cache-hit PTX/options are not directly observed; unchanged source specifies normal `--enable-tvm-ffi`, and no flags were added.
- Same captured FC1 BF16 input `[491008,640]`,360448 live routed rows,426752 processed/padded rows,1918 row-limit groups of256. Input tensor SHA `73a6ee6a9c49b0171d5f246785f488a70416445ae37f805f9edb9db1f8d75bb6`, exact arguments/effective recipe/base-math environment,PDLtrue,grid2368/block64, identical defined-output hashes across all34 invocations. Unspecified inactive packed/per-row output capacity is not compared.
- Graph contains only quantization;10 warmups and the native twice-L2-size flush precede profiling. `--clock-control none --cache-control none`; source/helper options unchanged. Full13,245-file inventories per arm and four release ELF/Ninja identities match before/after. GPU3 was0MiB/0%/noPIDs at final postflight.
- Root explicitly authorized startup56 timing on the other seven GPUs while these reports continued; GPU3 remained exclusive. This cross-GPU concurrency and two-report ordering are retained limitations. No NCU duration is substituted for either existing timing campaign.
- Original42-cell whole-chain data, failed first isolated attempt and corrected400-sample CAAC remain unchanged. The successful CAAC receipt, summary and closure hashes were rechecked. No source change, retention change, new benchmark, or follow-up prototype is part of this diagnostic.

Evidence: `summary.json`, `pc-opcode-groups.json`, `evidence/{control,candidate}/`, `evidence/receipt.json`, `fetch.json`. Archive SHA `49858af394ab514817ccfb3287ee27494100c605523b8a2eb448fcc0bc908842`. All285 fetched files are retained.
