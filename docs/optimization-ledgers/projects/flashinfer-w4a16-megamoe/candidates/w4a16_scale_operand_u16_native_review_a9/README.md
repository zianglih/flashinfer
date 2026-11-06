# UInt16 scale operand: matched a9 native review

Both completed matched pairs pass the source/native/process, resource and TMEM ownership checks. The narrower operand changes the generated schedule: the second x16 decode now precedes the first TMEM store, contrary to the prospective preference. This is explicitly admitted for a later numerical/performance trial as a changed schedule, not claimed to preserve that interleaving or improve runtime.

| Saved pair | Control instructions | Candidate instructions | FC1 body | FC2 body | Actual resources |
|---|---:|---:|---|---|---|
| profiles/scale-u16-first16-a9-m256n128c2-001 | 5864 | 5856 | 223 → 223 | 233 → 227 | Both REG96, STACK0, LOCAL0, 640 threads |
| profiles/scale-u16-first16-a9-m256n64c2-001 | 5536 | 5528 | 223 → 223 | 233 → 227 | Both REG96, STACK0, LOCAL0, 640 threads |

Bodies here span the raw-ready wait through the last of eight STTM.x8 stores. Counts are static instructions, not cycles or dynamic executions. Each pair has identical descriptors/configuration and unchanged source/native before/after, successful two-process exit, no remaining PGID members, exactly one real cute.compile per arm, and zero compiled launches/device allocations/collective initializations. The source is a9, only utility858→357 differs; nativebb367, common helper50dbe and bootstrap5c841 are recorded with each capture. REG96 is the initial cap: dynamic role caps remain control80/decode80/epi176/dispatch64 with two decode WGs, 640 threads and the same 61440-register pool. The reported static SHARED1024 belongs to this sealed fake-descriptor capture; it is not a substitute for a serving launch's dynamic shared-memory report.

## Replacement work and unchanged arithmetic

Both geometries have the same whole-kernel delta: PRMT −17, LOP3 +7, IMAD.SHL +1, IMAD +1, IMAD.U32 −1, LEA −1, MOV +1, NOP +1, SHF.L.U32.HI +2 and SHF.R.U32.HI −2, totaling −8 instructions. Labels and ordered branch/predicate skeleton are unchanged (472 labels for N128; 441 for N64), with no additional MMA copies, LDL or STL. Sixteen UTCHMMA.2CTA and four R2UR.BROADCAST remain.

The PTX u32→u16 conversion count increases 12→19 while u16→u32 drops 7→0; all sixteen scale unpack sites use mov.b16. This does not mean that all native masking vanishes. FC1 PRMT falls 17→9 but six byte masks and address/shift selection changes offset that saving, leaving 223 instructions. FC2 PRMT falls 24→16: its seven 0xffff masks disappear, replaced by seven 0xff masks; its first scale replication also uses one IMAD.SHL and one OR-form LOP3. Thus FC2 loses eight PRMTs and gains two instructions in aggregate, giving 233→227. The remaining whole-kernel −2 lies outside these body ranges.

Each FC body still has four LDS.128 packed loads, two scalar shared scale loads, 64 E2M1 pair conversions, eight E4M3 pair conversions, 32 HMUL2 and 32 HFMA2, and eight STTM.x8. No first-block conversion or scale load is duplicated. The wrapper's low8(trunc16(x)) equivalence remains the source contract, including upper-bit-bearing callers. This shared change also affects FC1 and later fragments; it is not limited to the first FC2 scale.

## Actual schedule and ownership

| Event | N128 control | N128 candidate | N64 control | N64 candidate |
|---|---|---|---|---|
| First x16 fully scaled | 0x75b0 | 0x7590 | 0x75d0 | 0x75b0 |
| Decoded-stage blocking wait | 0x7660 | 0x7640 | 0x7680 | 0x7660 |
| Second x16 decode starts | 0x7920 | 0x7820 | 0x7940 | 0x7840 |
| First TMEM store | 0x78b0 | 0x7b60 | 0x78d0 | 0x7b80 |
| Final TMEM store | 0x82a0 | 0x8220 | 0x82c0 | 0x8240 |
| Store fence | 0x82c0 | 0x8240 | 0x82e0 | 0x8260 |
| Raw release | 0x82e0 | 0x8250 | 0x8300 | 0x8270 |
| Decoded publication | 0x82f0 | 0x8260 | 0x8310 | 0x8280 |

The candidate's first sixteen BF16 values are fully scaled in R12–R19 before acquire. The N128 slow path at 0x15920–0x15970 uses R3 for its address and R4 for the phase, updating P0; N64 at 0x14420–0x14470 has the same register behavior. Both preserve R12–R19 and the remaining packed R6/R7. No payload register is overwritten before its first STTM and no TMEM write occurs before acquire.

There are still only the two packed-word relocations, not BF16 packet gathers: N128 moves R7→R11 at 0x7670 and R6→R3 at 0x7690 (N64 +0x20). The candidate completes three x16 payloads before the first store; the control has completed one there. Accordingly the first payload survives 92 intervening static instruction slots instead of 47. These are source-derived liveness intervals, not measured latency or a complete live-register peak. The candidate adds no RMEM buffer and produces no local allocation, but does keep more already-allocated decoded payload live simultaneously. A lower final body count does not establish whether this schedule is faster.

The same final store-fence → raw release → decoded publication protocol remains. Generated PTX retains two tcgen05.wait::st.sync.aligned operations and sixteen collective tcgen05.st.sync.aligned.32x32b.x8.b32 stores. The existing source pipeline/barriers and stage counts are byte-identical; the audit separately confirms the actual release/publication order and all stores after acquire.

`audit.py 128` and `audit.py 64` reproduce the saved evidence using an AST-sliced copy of the established parser/phase checks, avoiding the old script's top-level evidence write. The two JSONs include per-phase masks/counts, actual prologue/slow-path/publication PCs, all PTX/SASS/cubin/result/overlay hashes and source/native/process records. Historical evidence is unchanged. No numerical or performance claim is made; those gates and any eventual shared split/fallback compatibility coverage remain separate.
