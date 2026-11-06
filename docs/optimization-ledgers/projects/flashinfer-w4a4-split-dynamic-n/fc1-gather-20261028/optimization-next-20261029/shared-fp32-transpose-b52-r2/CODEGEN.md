# Shared FP32 transpose on retained b52: resource gate held

Frozen source: `f5b7124baa577784714a2bacdb1ccf2d2ec895d1aa95bb3c5946d080dc7e34cb` on `b52e4e09649dc180fc7583a25ec35ff55f04654d`; 66 added / 6 removed lines in the swap kernel. Both source and remote captures remain immutable.

Eight FC1 signatures and their eight FC2 counterparts compiled successfully without launching the owned MoE kernels. All 119 fetched evidence files passed hashes. The proposed 41-case numerical gate has **not run**, and no performance measurement has run.

| FC1 geometry | Operand stages | Stack bytes | Local load/store sites | Non-NOP SASS sites |
|---|---:|---:|---:|---:|
| matrix#0 M128 N256 K512 SF16 activation=3 | 2 → 2 | 0 → 0 | 0/0 → 0/0 | 3593 → 3419 |
| matrix#2 M128 N128 K512 SF16 activation=8 | 3 → 3 | 0 → 0 | 0/0 → 0/0 | 1479 → 1480 |
| matrix#4 M128 N16 K256 SF32 activation=3 | 5 → 5 | 0 → 0 | 0/0 → 0/0 | 1306 → 1349 |
| matrix#6 M256 N16 K256 SF16 activation=3 | 10 → 9 | 0 → 0 | 0/0 → 0/0 | 1448 → 1466 |
| matrix#8 M128 N256 K256 SF32 activation=3 | 2 → 2 | 0 → 0 | 0/0 → 0/0 | 3817 → 3612 |
| matrix#10 M512 N128 K256 SF32 activation=3 | 2 → 2 | 128 → 72 | 16/16 → 44/17 | 4056 → 3906 |
| matrix#12 M256 N256 K512 SF16 activation=6 | 2 → 2 | 0 → 0 | 0/0 → 0/0 | 4035 → 3577 |
| native-0#0 M256 N256 K256 SF32 activation=6 | 3 → 3 | 0 → 0 | 0/0 → 0/0 | 4141 → 3684 |

All FC1 captures retain REG168. Actual shared allocation fits the 232,448-byte hardware budget. The implementation emits 16 scalar shared stores, four vector128 shared loads and two warp barriers per exchanged fragment; these are transport counts, not a demonstrated speedup. Source-wide stage losses remain documented in `shared-fp32-transpose-audit-ce4/PLANNER_IMPACT.md`.

## Blocking case and attribution

The pre-existing M512/N128/K8 MXFP4x8 stress case changes STACK128 →72 bytes but **16 LDL +16 STL →44 LDL +17 STL**. This violates the matched no-new-local-sites gate. There is no new quota, dtype fallback, exclusion or guard relaxation.

`attribute_spills.py` traces candidate role branches and shared teardown in actual SASS. The matched control has all 16 loads/16 stores in the MMA role. The candidate has:

| Region | LDL sites | STL sites |
|---|---:|---:|
| Common startup | 1 | 3 |
| Weight producer | 6 | 0 |
| Activation relay | 5 | 0 |
| MMA | 22 | 14 |
| Epilogue | 4 | 0 |
| Gather producer | 5 | 0 |
| Shared teardown | 1 | 0 |

Three startup scalar slots hold the grid step, total work count, and shared barrier base (offsets 0x38/0x3c/0x40). Their reloads span roles and barrier slow paths. The 14 remaining scalar slots at 0x00–0x34 belong to MMA descriptor/instruction-id preparation and consumption. Epilogue local accesses reload common startup state; there are no spilled activation/quantization values in this capture. These are static site classifications, not executed traffic counts. Whole-kernel allocation changed; this does not establish that epilogue arithmetic alone causes the pressure.

## FC2 boundary

All eight FC2 PTX files are byte-identical and their resources, operand stages and dynamic SMEM match. Seven FC2 CUBIN/SASS pairs are byte-identical. The remaining wide one-CTA MX FC2 has the same bounded 12-site UR16/17 ↔UR18/19 permutation seen in R1, with unchanged instruction positions/opcodes/other operands.

## Decision

Keep f5 source frozen and hold numerical/performance work. No source fix is justified from these results alone. A separately qualified change to MMA descriptor lifetime may be evaluated independently by the parent; it is not composed here. R0 alignment failure and R1 ce4 qualification remain separate immutable evidence.
