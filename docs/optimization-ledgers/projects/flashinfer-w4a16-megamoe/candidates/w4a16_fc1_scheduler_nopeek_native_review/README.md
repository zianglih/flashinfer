# FC1 scheduler no-peek: independent native schedule review

**PASS for both N64 and N128; no native-quality blocker to the planned numerical trial.** These are sealed compile-only captures, with no numerical or performance claim. The raw5 control kernel `4208…` changes only the scheduler extension's optional FC1-ready pointer to `None` in candidate `bed24597…`. Source installation and GPU execution remain parent/performance-owned.

Actual captures are `profiles/fc1-scheduler-nopeek-0909b-m256n{64,128}c2-001`. `evidence.json` pins their summaries, native files and result/resources, references performance's original owner/resource/process gate, and records the source-attributed comparisons. N64 summary is `e15b88ce…`; N128 is `b3ec5817…`.

## Dependency change verified

Both static scheduler FC1 acquire sites (`custom_ext.py:394`) disappear, together with their FC1 threshold/readiness-bit selection. The first and repeated enrichment paths now guard the **remaining FC2-only** peek on valid work with phase2. For FC1, the base phase value1 survives in R7, with bit16 clear, and is written by the unchanged work-metadata store. Invalid work still skips the counter load. No readiness poll was moved into another scheduler loop.

| Site | N64 control → candidate | N128 control → candidate |
|---|---|---|
| FC1 scheduler acquire, first/repeated | 0x26b0,0x4050 → absent | 0x2690,0x4030 → absent |
| FC2 scheduler acquire, first/repeated | 0x26e0,0x4080 → 0x2680,0x3fa0 | 0x26c0,0x4060 → 0x2660,0x3f80 |
| FC1 activation initial/retry acquire | 0x5260,0x52b0 → 0x5150,0x51a0 | 0x5240,0x5290 → 0x5130,0x5180 |
| Following B-stage acquire | 0x5390 → 0x5280 | 0x5370 → 0x5260 |
| First FC1 activation TMA | 0x54e0 → 0x53d0 | 0x54c0 → 0x53b0 |
| FC2 activation initial/retry acquire | 0x5710,0x5760 → 0x5600,0x5650 | 0x56f0,0x5740 → 0x55e0,0x5630 |

PTX confirms the exact acquire semantics: the two `ld.acquire.gpu.global.b32` sites attributed to custom-ext line394 become zero; line409 retains two FC2 peeks; token-comm line596 retains two FC1 activation loads; kernel line1130 retains two FC2 activation loads. The remaining FC1 activation loop loads the real counter indexed by cumulative token-block count plus tile_n, compares against valid-row threshold, sleeps1000 on failure, and retries. It remains before B-stage acquire/TMA; MMA still consumes the activation pipeline. Its runtime readiness-bit skip branch remains because metadata is loaded from shared memory; the candidate's FC1 producer always publishes that bit clear. Thus previously peek-ready tiles now execute the real activation acquire, which is the intended tradeoff.

For N64, candidate activation load0x5150 is compared at0x5170; success branches at0x5180, failure sleeps at0x5190, reloads at0x51a0 and loops from0x51d0. N128 has the corresponding sequence shifted−0x20. The FC2 peeks retain the real FC1-done pointer and threshold32; their conditional branches preserve invalid-tile safety. Work slot stores, shared fences, publication arrivals and consumer barriers remain.

## Schedule and resource quality

The complete shared decoder's587 source-attributed instructions are identical after branch-label relocation in each pair, including registers. Both FC1 and FC2 raw/decoded waits, packed/SF loads, conversion/store interleaving, TMEM fence, raw release, decoded commit and tail logic retain their prior schedule. No decode materialization, extra loads, packet gathers or loop/MMA cloning appear.

Private epilogue, vendor epilogue and dynamic-MMA source sequences have the same instruction order and all non-uniform-register operands; only uniform-register allocation and relocated labels differ. Alpha, accumulator waits, TMEM scratch load/store/fence/release and output ordering remain. This does not treat register renaming as a regression. All TMA, LDS/STS, TMEM, MMA, named-barrier, mbarrier and reconvergence counts are unchanged.

Listed rows are N64 5528→5512 and N128 5856→5840:18 source-attributed custom-extension instructions removed, with two additional unreachable trailing padding NOPs. The remaining FC2 constant-bit construction can use `HFMA2` to materialize an immediate bit pattern; this is not new floating-point activation/dequant arithmetic. Both actual resources remain REG96/640, STACK0/LOCAL0, no LDL/STL,16 MMA and caps80/144/64; two decode groups retain96 registers. No stage or shared-memory layout change is introduced.

No additional capture is requested. Actual numerical/lifecycle behavior and controlled timing remain separate gates; the removal of an earlier scheduler load does not itself establish a latency gain.
