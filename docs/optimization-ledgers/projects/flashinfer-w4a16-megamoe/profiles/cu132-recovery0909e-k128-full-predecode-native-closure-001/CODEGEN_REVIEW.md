# Full K128 decode-before-acquire scheduling: native review

The unchanged `934d2db47f5ff8dcd1d5df639972cb57bb7648ce23d4cbc1d42c3b963907630a`
candidate is a useful isolated scheduling trial. PTX places all scaled pairs
before acquire, but final SASS preserves mixed FC1/FC2 ordering. No synthetic
fence, barrier, arithmetic dependency, early raw release, or compilation-cache
prototype is included. Root reviewed and authorized existing numerics after
this review; native capture itself performed no callable launches.

Evidence directories are `../cu132-recovery0909e-k128-full-predecode-m256n64c2-002`
and `../cu132-recovery0909e-k128-full-predecode-m256n128c2-001` (each contains
`codegen/sass.txt`, source-annotated `codegen/dsl/*.sass`, PTX, cubin,
resources and result JSON). Both managed captures exited true zero. The
original N64 attempt failed on a missing existing helper before compilation;
its failure was preserved under the original `native-n64` log prefix. Only
unchanged transitive helpers were staged for the successful retry.

Both geometries remain 640 threads, REG 96, STACK 0, LOCAL 0. Neither PTX local
loads/stores nor SASS LDL/STL occur. Each phase has 32 FP4 pair conversions and
32 BF16 pair scale operations; neither slow wait repeats decode. Across the
kernel there are 64 FP4 and 8 scale-factor conversions, unchanged from B6.

| Geometry / phase | Decoded wait PC | Scale placement | Slow-path scratch | Four STTM.x8 PCs |
|---|---|---|---|---|
| N64 FC1 | 0x68f0 | 20 pairs before; 12 at 0x6920-0x6a00 after | R6/R7 | 0x6a80, 0x6b10, 0x6be0, 0x6cf0 |
| N128 FC1 | 0x68b0 | 20 pairs before; 12 at 0x68e0-0x69c0 after | R6/R7 | 0x6a40, 0x6ad0, 0x6ba0, 0x6cb0 |
| N64 FC2 | 0x7570 | All 32 before; last scale 0x7520 | R4/R5 | 0x7640, 0x76d0, 0x77a0, 0x78d0 |
| N128 FC2 | 0x7530 | All 32 before; last scale 0x74e0 | R4/R5 | 0x7600, 0x7690, 0x7760, 0x7890 |

FC1 has all 32 FP4-unpacked pairs before the wait. Its 20 already-scaled pairs,
12 unscaled pairs, and two remaining scale operands remain live across the
slow path. FC2 has the complete 32 scaled pairs live across the slow path.
Slow waits only use the scratch registers listed above; no payload register
is overwritten. FC1 slow paths start at N64 0x13bd0 / N128 0x15ec0; FC2 at
N64 0x13c90 / N128 0x15f80. Decoded publication/fence and raw release retain
the prepared source order.

PTX last-scale / decoded-wait lines are N64 FC1 3165/3197, FC2 3663/3695;
N128 FC1 3161/3193, FC2 3659/3691. These describe PTX only, not final SASS.

| Geometry | B6 MOV | Trial MOV | B6 IMAD.MOV | Trial IMAD.MOV | B6 UMOV | Trial UMOV | Non-NOP delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| N64 | 234 | 264 | 203 | 230 | 109 | 105 | +57 |
| N128 | 294 | 324 | 238 | 265 | 114 | 110 | +57 |

Here MOV means the exact MOV opcode; MOV plus IMAD.MOV grows by 57 in each
geometry. The whole-kernel non-NOP counts are N64 5262 to 5319 and N128 5808
to 5865. The decode-to-fourth-store region contains 28 payload register copies
per phase in the trial versus zero in B6: ptxas repacks the decoded registers
through R4-R11 for each STTM.x8. Counts are static instructions, not measured
runtime cost. Source placement by itself did not force complete FC1 scaling
before acquire. Evaluate this version with existing numerics/AUTO before any
separate stronger scheduling or register-packing experiment.
