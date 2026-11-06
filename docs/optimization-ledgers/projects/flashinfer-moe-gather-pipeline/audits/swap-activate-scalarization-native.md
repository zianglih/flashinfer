# Swap FC1 packed activation: existing-profile boundary

The saved native profiles do **not** establish a packed-FP32 issue/pipe bottleneck that justifies scalarizing `_activate`. This is a feasibility conclusion from existing captures, not a measured rejection of a new source variant.

`moe_swap_ab_kernel.py:626–694` has identical `_activate` AST at measured822,49,2b8 and retainedc1ac (`5bd96f2b…`). Thus the gated V3 evidence applies to the current helper; V3 whole-kernel/source cohort remains historical. The N3U49 whole swap source is byte-identical to c1ac (`482b636a…`). N3U uses Relu2, not the gated helper branch. W4 is excluded.

| Actual FC1 capture | All FADD2/FMUL2 executed warp instructions / kernel | Packed instruction share | Packed math-throttle samples / all kernel math samples | Packed long-scoreboard / arithmetic-wait samples |
|---|---:|---:|---:|---:|
| V3 TP8 MXFP8 T16K, measured822 | 4,321,280 /110,720,905 |3.903%|0 /59|139 /29|
| N3U TP8 MXFP4x8 T32, retained49-equivalent |369,600 /10,528,041|3.511%|0 /6|41 /0|
| N3U TP8 W4A4 T16K, measured2b8 |11,041,920 /178,666,790|6.180%|3 /223|95 /28|
| N3U EP8 W4A4 T16K, measured2b8 |10,836,480 /134,174,159|8.076%|2 /101|93 /35|

These deliberately include **all** packed FP32 math, including output normalization/quantization, so they upper-bound `_activate` work. All four captures use168 initial registers and LOCAL0. Counts are replayed from their existing exact-ELF-bound `source-sass.csv`; they are warp instruction/sample counts, not runtime shares or a scalarization speedup estimate.

The apparent hot packed sites are input consumers:

- **V3 `FMUL2 0x5440`:117 long-scoreboard samples,0 math.** Its wait mask0x21 waits both expert-alpha `LDG 0x53d0` (barrier5) and TMEM load `0x5420` (barrier0). The data cannot uniquely attribute those117 samples to alpha or TMEM, much less to packed multiply throughput.
- **N3U TP T32 `FMUL2 0x44e0`:41 long samples**, with the already-audited scalar-alpha barrier2 from `LDG 0x3c60` and no intervening wait/reassignment.
- **Current N3U TP/EP prefill `FMUL2 0x3570/0x4880`:90/93 long samples**, waiting barrier5 from scalar-alpha `LDG 0x2e00/0x40a0`. Neither site has math-throttle samples. Alpha-prefetch itself is separately rejected and is not reopened here.

For the N3U prefill Relu2 branch, exact native alpha-multiply and square sites account for two-thirds of packed instructions. TP has128 alpha sites and128 square sites (3,680,640 executions each); their math samples are0 and3. EP has128+128 sites (3,612,160 executions each); math samples are1 and1. The remaining packed multiplies implement output scaling. This does not support treating a sampled arithmetic instruction as an arithmetic-pipe bottleneck.

The broader captures are dominated by required readiness/reuse, memory, and TMEM dependencies: gated V3 has17,900 long-scoreboard samples versus59 math; current N3U TP has15,294 versus223. Their prior source/PC audits describe those lifetimes and closed leads. A scalar spelling would increase arithmetic instruction count before backend optimization; these captures do not establish a register-allocation or independent-issue advantage that offsets it. Quantizer packed-error regressions occurred in a different, highly issue-active kernel and cannot supply that missing evidence.

No source edit, GPU operation, profiling, or new harness was performed. Exact CSV/ELF/resource bindings, control-word checks, and totals are in `swap-activate-scalarization-native.json`. The source/history owner independently assesses prior trials and helper simplification; this note makes no universal claim about unprofiled K3/SiTU or other tactics.
