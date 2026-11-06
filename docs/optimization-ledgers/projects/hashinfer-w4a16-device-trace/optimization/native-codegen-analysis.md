# Native W4A16 decoder audit — uniform256 / N64

The wider `store16` lowers **eight to four weight TMEM store instructions per K-step**, and lowers eight to four `R2UR` address transfers. All decode math and packing instruction counts stay identical, with no added moves or spills. This is stronger evidence than the whole-kernel count alone: all 16 removed static instructions belong to the two repeated decoder K-loops. Performance retention still requires the parent task's matched benchmark and native sparse/dense matrix; this audit does not explain the reported sparse T4 regression without that specialization's native artifact.

## Exact comparison boundary

These are uninstrumented **artifact 00** from each `optimization/codegen/<arm>/rank0/manifest.json`. Each manifest contains four compiled ABIs; 00 is the timed target's **Int32 routed IDs, contiguous BF16 hidden input, Int32 live-token count**, with FP32 routing weights. All five records have identical staging ABI and kernel configuration: EP4, 256 tokens/rank, H6144, static expert shape `(64, 4096, 6144)`, M256/N64/K256, group512, cluster `(2,1)`, epi-warps token back, 640 threads/CTA, five raw stages and three decoded stages. FC1 fragment128 and FC2 fragment32, except the explicitly changed FC1 fragment64 arm.

`analyze_native_codegen.py` checks the selected PTX and cubin against their manifest hashes, the source-tree hash against `source-manifest.json`, every current local Python source hash against the export manifest, the ABI, and the config. `native-codegen-analysis/comparison.json` preserves the resulting source/PTX/cubin/SASS/manifest hashes and instruction lists. The compiler target is `sm_103a`, CuTe DSL4.8.0, `--ptxas-options='-maxrregcount=96' --opt-level 3`. No PMTRIG instrumentation is present.

Reproduce locally without a GPU:

```bash
cd /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace
python3 optimization/analyze_native_codegen.py
```

Loop boundaries are the smallest backward branch enclosing each weight `STTM ... +0x80`. FC phase is identified from the K-loop bound (24 FC1 iterations, eight FC2 iterations), **not address order**. The no-peek native code puts FC2 before FC1. Fast-loop static counts include predicated instructions and the conditional exits to slow waits; those are not a dynamic instruction count or a time estimate. Out-of-line retry paths are dumped separately. `SHARED:1024` is static shared allocation only, not total dynamic SMEM.

| Arm | Whole static instructions | FC1 loop range/count | FC2 loop range/count | REG / STACK | LDL / STL, whole kernel |
|---|---:|---|---|---|---:|
| control | 5128 | e590–f410 / 233 | f4c0–103a0 / 239 | 96 / 0 | 0 / 0 |
| store16 | 5112 | e590–f390 / 225 | f440–102a0 / 231 | 96 / 0 | 0 / 0 |
| no_peek | 5088 | f340–10120 / 223 | e510–f310 / 225 | 96 / 0 | 0 / 0 |
| predecode | 5288 | e640–f730 / 272 | f7e0–10bd0 / 320 | 96 / 136 | 71 / 63 |
| fc1frag64 | 5144 | e4d0–f400 / 244 | f4b0–10450 / 251 | 96 / 0 | 0 / 0 |

The report is for each isolated arm versus control. It does **not** substitute for a cumulative `store16_no_peek` or subsequent stack comparison.

## Store16: exact per-K reduction

For both phases the complete opcode delta is `STTM.x8: -8`, `STTM.x16: +4`, `R2UR: -4`, with every other opcode count unchanged. Each K-step still has 64 E2M1-to-BF16 conversions, eight scale E4M3-to-BF16 conversions, 32 BF16-pair multiplies, 32 BF16-pair fused multiply-adds, four `LDS.128`, two scalar `LDS`, one TMEM store fence and two barrier arrivals. FC1 retains 18 PRMT and FC2 retains 26 PRMT. Neither loop has MOV/IMAD.MOV in either arm.

| Phase | Control stores | Store16 stores | Total registers supplied to TMEM stores per thread |
|---|---|---|---:|
| FC1 | e9d0, eb80, ee10, ee30, efd0, f110, f380, f3a0; x8 | eae0, edb0, f040, f310; x16 | 64 in each |
| FC2 | f930, fae0, fd70, fd90, ff30, 10080, 10310, 10330; x8 | f9a0, fc70, ff30, 10240; x16 | 64 in each |

The store16 compiler reuses `R4–R19` for each of the four stores. The original mostly reuses eight-register tuples at R4, R12 or R20. Stores are interleaved with conversion/math in both native builds, despite the source's final `store_transformed_a` and the instrumented trace's distinct decode/store scopes. For example FC1 control already issues its first store after 19 of 136 conversion/math instructions, while store16 issues its first after 34. All stores remain after the decoded-slot acquire, with raw release followed by the TMEM fence and decoded-full commit. No reduction in bytes transferred or decode arithmetic is claimed.

The whole kernel already had eight unrelated `STTM.x16` instructions for other work; store16 grows that total to16. Calling all16 new weight stores would be incorrect. Four other layout-qualified STTM instructions are also unchanged.

## No-peek: exact removed waits and control

Original FC1 begins with raw/decoded initial lookaheads at e570/e580. The repeated loop has explicit raw wait e600, decoded-slot wait e660, next-raw lookahead e800, and next-decoded-slot lookahead f3f0. FC2 equivalents are initial f4a0/f4b0 and repeated f500/f580/f740/10380.

The raw lookahead is natively scheduled after all four packed-weight and two scale shared loads but **before current-K decode arithmetic**. The decoded-slot lookahead remains after the current tile's store/fence/publication. Both return a predicate consumed in the next iteration. No-peek removes both initial lookaheads and both per-K lookaheads; its only remaining repeated waits are raw+decoded at f380/f3c0 for FC1 and e550/e590 for FC2. All output stores/fences/releases remain.

The emitted PTX identifies the original lookahead as `mbarrier.try_wait.parity.acquire.cta.shared::cta.b64` with no explicit timeout. This may suspend until the phase completes or an implementation-defined limit. It is not the guaranteed nonblocking `test_wait` instruction. See [NVIDIA PTX ISA9.1, mbarrier wait semantics](https://docs.nvidia.com/cuda/pdf/ptx_isa_9.1.pdf) and [NVIDIA CuTe primitives documentation](https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/primitives.html). This permits the next-raw peek to delay current decode; static SASS does not establish how often that happens on this workload.

Phase-aware instruction deltas:

- FC1: -2 TRYWAIT, -2 branches, -2 LEA, -2 left shifts, -1 comparison, -1 S2R = **-10** instructions in the K-loop body.
- FC2: those same removals plus -1 IADD3, -1 additional comparison and -2 LOP3 = **-14** instructions.
- Conversion, scale math, PRMT, x8 stores and R2UR counts are identical to their correct control phase. No additional memory traffic or resource requirement appears. The remaining -16 whole-kernel instructions are outside these two bodies, including initial-lookahead setup and surrounding control.

The loop order reversal is material: comparing first-loop to first-loop would falsely report changed packing math.

## Full predecode: actual spill localization

Both phases complete all136 conversion/math instructions **before** their decoded-slot wait (FC1 f350, FC2 10580). Control executes zero conversion/math instructions before that wait and can recycle decoded registers after each early TMEM store. The predecode native result has a136-byte stack frame versus zero, 25 LDL +18 STL instructions inside the FC1 K-loop and28 LDL +18 STL inside FC2. Counts are instructions, not bytes; FC1 includes eight64-bit local loads and four64-bit local stores. There are also45 local-memory instructions outside these bodies, including transform setup/state handling, out-of-line wait paths, and later control code. It would overstate the evidence to call all134 local-memory instructions decoded-payload spills.

There is direct payload evidence for FC1:

```text
e800 HMUL2.BF16_V2 R25, R16, R8
e830 HFMA2.BF16_V2 R11, R15, R8, -RZ
e880 HMUL2.BF16_V2 R10, R14, R8
e940 STL [R1], R25             # decoded payload, followed by offsets4..1c
...
f350 SYNCS.PHASECHK.TRANS64.TRYWAIT P1, [R3+URZ+0x68], R2
f360 @!P1 BRA 0x146b0          # decoded-slot slow wait
...
f3d0 LDL.LU.64 R4, [R1]       # reload the first eight decoded registers
f3e0 LDL.LU.64 R6, [R1+0x8]
f3f0 LDL.LU.64 R8, [R1+0x10]
f400 LDL.LU.64 R10, [R1+0x18]
...
f480 STTM.x8 tmem[UR8+0x80], R4
```

These payload values live in stack slots across the decoded-slot wait, so the spill explanation is source- and native-code-grounded. FC1 additionally swaps the last decoded R4–R11 tuple into stack offsets60–7f after waiting so it can reload/store the first tuple; FC2 adds40 MOV/IMAD.MOV instructions repacking its post-wait register payload for x8 stores. This matches a plausible cost mechanism for the parent's large measured regression, while not assigning its full magnitude to any single effect without runtime stall counters. No register-pool enlargement is proposed.

## FC1 fragment64

This arm retains the same eight x8 stores, eight R2UR and136 conversion/math operations per phase, with no resource or spill reduction. Native FC1 gains four VIADD, four right shifts and four LOP3, while losing one IMAD (+11 loop instructions). FC2 also gains four each of VIADD/right-shift/LOP3 (+12), despite its source fragment remaining32; these are address/index calculations introduced or moved into the repeated body by the compiler's changed code organization. Whole-kernel growth is16 because some setup moves between prologue and loops. There is no instruction-reduction argument for retaining this arm, and the parent's isolated target result was not promising.

## What remains open

- Sparse T4 and N128 matched native artifacts are required before extrapolating the uniformN64 store effect or explaining sparse regressions.
- Wider x32/x64 must be compared in the native decoder regions for added moves/spills, not solely fewer STTM mnemonics.
- Combined arms need their own artifacts and incremental performance comparison. This isolated no-peek result cannot certify a store16+no-peek stack.
- IKET event durations include instrumentation and scope boundaries constrain code motion. The native interleaved stores here show why instrumented scope timing cannot by itself specify native register lifetimes or exact store ordering.
