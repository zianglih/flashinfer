# Current N64 / three decoded-stage profile audit

The completed global-256 capture passes the integrity and resource checks. It provides no evidence of transform spilling. Most sampled barrier sleeps occur while scheduler consumers wait for work publication. Collective profiling and strong rank skew prevent interpreting that distribution as production latency or proof of the limiting pipeline stage. No additional profile is required to report this iteration.

## Exact scope and source

- Workload: H7168, I2048, E256, top-k8, EP8, global256 tokens (local capacity32); B300 ×8, CUDA13.2, DSL4.7.1, NCU2026.1.1.
- Tactic: M256/N64/K256, physical cluster(2,1,1), two-CTA MMA, exactly two transform warpgroups, raw5/decoded3/activation2/accumulator2, flag4, group512, atomic scheduler, epilogue flags(2,4), `epi_warps`, in-kernel FC2 reduction false.
- Capture source ID: `580a9e677385cfca90db51c50ee5e0b0962d577aba00f34ce3fa1d048c12dc97`; kernel SHA256 `34bbdfba91e4743a7079d436c3181e3825ca771fe584f910c4ee1c37a4165152`, matching local committed source6315f94. The remote Git HEAD remainsfe4f8132 plus the attested source overlay; it is not the tested local commit ID. Both NCU and Nsys pre/post source dictionaries match exactly and match each other. No source edits were made by this audit.
- The canonical extractor, SASS exporter, codegen audit and NCU launcher were left unchanged; hashes are checked in `../../n64-profile-audit-plan/helper-integrity-after.json`.

## Integrity and resources

All eight raw reports match the canonical extractor's SHA256 values and contain one matched action each. Embedded source hashes agree across all ranks, including the frozen shim and unchanged local W4A16 transform helper. Every correlated metric conserves aggregate, instance and PC sums. The capture has 9,374,121 total samples, zero sampler overflow and zero dropped bytes. The interval is 4096 cycles; the reports expose sampler `aggregated_passes=2` and `profiler__replayer_passes=1`. These are recorded separately rather than inferred from each other.

| Rank | Samples | Unmapped samples |
| --- | ---: | ---: |
| 0 | 1,055,965 | 194 |
| 1 | 2,639,757 | 219 |
| 2 | 3,262,201 | 35 |
| 3 | 13,499 | 251 |
| 4 | 1,455,243 | 199 |
| 5 | 55,860 | 199 |
| 6 | 733,251 | 191 |
| 7 | 158,345 | 194 |

The 1,482 unresolved samples occupy 174 per-rank PC rows without SASS/source correlation, including PCs outside the exported function extent. They remain explicit in `analysis.json`; they were not assigned to the nearest source line. See `rank-integrity.csv` for all per-rank metadata.

The independently queried Nsys SQLite contains 16 fused launches, exactly two on each GPU: 640 threads, 96 registers/thread, 183,808 dynamic shared bytes, zero static shared bytes, zero local-memory bytes/thread, grid(2,1,74), cluster(2,1,1). NCU reports the same thread/register/dynamic-shared values on all eight ranks. The separate strict Nsys stage audit has 16 rows for each of routing, workspace reset, fused MegaMoE and top-k reduction. Its preserved `../../tmem-n64-stage3-current-nsys-001/diagnostics.json` contains generic NVTX/CUDA event warnings; zero errors and no dropped/incomplete/lost diagnostics were reported. This audit does not overwrite that file.

The current rank-0 full disassembly has 5,520 contiguous instructions, 104 NOPs, 16 `UTCHMMA.2CTA` instructions, and **no LDL/STL instructions anywhere**. All mapped sampled instructions agree across all eight reports after normalizing function-relative branch targets. Full unsampled disassembly was inspected only for rank0; this audit does not claim all-rank full-binary equality. The earlier all-rank M256/N64 stage3 codegen audit also found 5,520 instructions and no locals; that separate global4096/max512 artifact does not substitute for current global256 source/PC mapping.

## Source-specific waits

Offsets below are relative to this report's function start, not historical offsets. Polling stubs were matched by TRYWAIT predicate, failed-predicate sleep, identical blocking-query address/phase, retry branch and valid return. An instruction can loop through a leading MOV that restores the same barrier pointer. The capture-specific `../reviewed-map.json` also checks exact report SHA and exact instruction text. Source-tagged branches without a verified predicate dependency remain separate.

| Pipeline boundary | Relevant sleep offsets | Sleep samples | Query samples | Reviewed query-result branch samples |
| --- | --- | ---: | ---: | ---: |
| Scheduler work publication | 0x13ca0,0x13dc0,0x14000,0x14120,0x14240,0x14420,0x145a0,0x14720,0x147d0,0x14940 | 6,863,792 | 60,054 | 35,812 |
| Weight TMA waits for free raw stage | 0x13d00,0x13d60 | 48 | 17 | 2,958 |
| Transform waits for raw weight/scale arrival | 0x142a0,0x14360 | 0 | 0 | 0 |
| Transform waits for free decoded TMEM stage | 0x14300,0x143c0 | 295 | 4 | 1,036 |
| Activation TMA waits for free activation stage | 0x14060,0x140c0 | 0 | 26 | 2,616 |
| MMA waits for free accumulator | 0x14600 | 0 | 2 | 9 |
| MMA waits for decoded weights | 0x14660 | 0 | 31 | 282 |
| MMA waits for activation | 0x146c0 | 16 | 19 | 911 |
| FC1 epilogue waits for accumulator | 0x14830 | 7,458 | 76 | 2,557 |
| FC2 epilogue waits for accumulator | 0x14890,0x148f0 | 13 | 2 | 2,596 |

Query and branch counts are separate PC samples, not additional elapsed wait time. A zero sleep count means no sample landed at that sleep instruction, not that the dependency never stalled. Transform peek queries separately have48 raw-ready and38 decoded-free samples. There are also1,537 raw-ready,114 decoded-free and1 FC2-acc source-tagged branch samples whose predicates were not fully traced; they are deliberately excluded from the reviewed branch column. Tail waits and other instructions remain in the machine-readable analysis.

Source anchors in the embedded source:

- Raw/decoded transform waits reuse `moe_w4a16_kernel.py:474–491`; the current kernel calls the existing helper for both FC1 and FC2. The transform function's other source-correlated instructions account for26,296 samples, excluding identified poll stubs. This is not a dequantization cycle count; source tags include address/setup/control operations.
- Weight and activation producer acquisitions are shim `kernel.py:811` and `:877`; scheduler consumer wait is vendor `moe_persistent_scheduler.py:184`, with generated stubs tagged at `:187`.
- The free-accumulator stub0x14600 is an important optimized-line-table correction: caller0x8860 is `kernel.py:1253` (`acc_pipe.producer_acquire`), queries `[UR11+0xb0]`, and enters a stub querying the same address via R3. Its stub line1256 misleadingly tags the following decoded wait. Shared prefix0xb0 is accumulator-empty stage0; decoded-full starts at0x50. The review uses caller/control flow and barrier allocation rather than the misleading line tag.
- FC1 accumulator consumer wait is shim `epilogue.py:295`; FC2 waits are vendor `epilogue_refactor.py:2090/2098`. This report retains post-FC2 routing weights and BF16 return semantics.

The largest individual samples are scheduler sleeps0x14240 (3,655,888) and0x147d0 (1,831,159). Other large PCs are token-communication control/synchronization, e.g0xd370 (`BSSY`, vendor `token_comm.py:867`). These are observations, not proof of a scheduler bug, communication bandwidth limit, or wasted production time. Rank2 has2,408,026 scheduler sleep samples while rank3 has714; that skew makes aggregate percentages particularly easy to misinterpret.

## Interpretation limit

Current timing compares the selected N64/three-decoded-stage tactic with N128/two-decoded-stage. It changes geometry and stage depth together and therefore **does not isolate the third-stage effect**. The PC capture neither establishes that a fourth stage would help nor justifies another raw-depth or transform-group experiment. Exactly two transform warpgroups remain fixed. Use the separate uninstrumented repeated timings for performance claims; NCU/Nsys durations and cross-capture sample ratios are excluded.
