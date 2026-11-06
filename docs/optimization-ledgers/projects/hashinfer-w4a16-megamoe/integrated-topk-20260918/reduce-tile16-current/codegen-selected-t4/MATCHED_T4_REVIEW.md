# Matched T4 width8 / adjacent-width16 codegen

The bounded capture passed. There is no spill or extra synchronization defect to fix in L1. Widening changes both reduction work assignment and compiler scheduling, so this capture cannot establish which caused the recorded T4 speedup.

Both sources ran serially on hu-pdx-59 / boot dc868539-2ac3-4565-a1d9-3580f5164d0c, eight B300 GPUs, CUDA13.2, CuTe4.7.1, O3/maxrregcount96. Sources are retained3de81245 and L1d9d510f7. The actual completed L1 T4 winner is candidate index2, `[256,64,256]`, `epi_warps`; hu15 timing selects the tactic only. This capture is not timing evidence or a cross-host latency comparison.

The exported304a fixture is unchanged. L1's a82f benchmark source includes the published534 documentation/default-token change; the source review binds that difference explicitly. The capture executes global4/H7168/I2048/E256/K8/EP8 and the canonical int32-vector ABI. Public warmup naturally compiles four staging ABIs. All16 rank records pass eager repeat and two graph replays. All8 cross-source raw outputs match: ranks0–3 each have one7168-element row, ranks4–7 are empty. Thus there are28672 nonempty BF16 output elements per source, without tolerance.

| Generated metric | Width8 retained3de | Adjacent-width16 L1 |
| --- | ---: | ---: |
| Selected reducer body instructions, inclusive first route load through final store |147|287|
| Route loads per worker |8 ×128-bit|16 ×128-bit|
| Output stores per worker |1 ×128-bit|2 ×128-bit|
| Packed FP32 multiply / FMA |4 /28|8 /56|
| Packed BF16 result conversions |4|8|
| Route-vector loads issued before first multiply |7|9|
| Whole-kernel non-NOP instructions |5540|5681|
| Whole-kernel instructions including NOP padding |5664|5800|
| All32 ABI resource reports per source: REG /STACK /LOCAL |96 /0 /0|96 /0 /0|
| Reported SHARED bytes |1024|1024|
| Local spill LD/ST instructions, all32 SASS files per source |0|0|

The exact selected rank0 body is SASS0x13050–0x13970 before and0x13050–0x14230 after. All8 ranks have identical selected SASS within each source. `codegen-counts.json`, `whole-kernel-comparison.json` and the compact `*-reducer.sass.txt` files preserve the count definitions and boundaries. Explicit reducer register operands extend toR52 before andR61 after; this is not a liveness or occupancy measurement. Launch96 and the existing role register policy remain unchanged.

L1 issues all eight first-half route loads at0x13050–0x130c0, then route0's second-half load at0x130d0. The other second-half loads are interleaved at0x13360–0x138c0. Output stores remain separate128-bit operations at0x14200 and0x14230. For adjacent16 mapping each lane advances32bytes and each operation covers one16byte half: the complementary half-sector issue described in REDUCER_HEAD_BULK_REVIEW still applies. There is no generated256-bit combine operation and no evidence of fewer sector requests or DRAM transactions. Cache reuse between the halves may matter; do not combine width16 with L1-no-allocation hints on the assumption that their effects are independent.

The source width change also alters register allocation and instruction scheduling in the dequant role. The first non-branch-target instruction difference is0xfe80 (`CS2R R44` versus`R54`); much of0x10000–0x12220 is rescheduled before the reducer. Before0xfe80 instruction text is equal after ignoring only branch/reconvergence/call target addresses. Opcode counts outside the measured reducer are nearly equal, but that does not mean identical scheduling. This is a plausible contributor, not causal attribution. Both PTX files retain two640-thread barrier8 sites and twelve128-thread barrier10 sites for the selected epi tactic; SASS synchronization, fence, tensor-memory and tensor-core opcode counts match exactly.

No alignment contract changes were made: source output marking remains16bytes and each combine copy atom is128bits. T4 active reduction work halves from896 to448 workers per nonempty rank under the inherited striped assignment; that saves repeated score/address work but also changes available reduction parallelism. Existing full13 timing decides retention; this diagnostic adds no benchmark repetition, sanitizer or full numerical suite.

Full422-member archive SHA256: `f81c5dabf328f965420c3ad068ffa63d6a697b56983e23f2cc1515eeba9ea508` (18048131bytes). Every archive member and helper/source/output hash was verified locally. Fresh closure proves groups58129/58134/60550 empty and no GPU processes. The initial staging attempt rejected safe directory entries before any kernel launch; its log and the narrowly corrected resume are preserved. hu59 is idle after capture.

Independent CPU audit passed: `independent-codegen-audit.json`, SHA256 `6f4579335872c839b8ec285930e5bbb572dd86902765089508619f7579da8747`. It rechecked the original archive and all422 members, both exact104-file source identities, all16 rank records,64 resource reports, output pairs, measured body/whole-kernel counts and closure. No source or GPU rerun was needed.
