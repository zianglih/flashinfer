# Exact negative-tactic native comparison

Both pairs use the original frozen K3 EP8 inputs, routes, public API, and actual compiled stage configurations. They were captured through the native profiler replay path without NCU or a latency measurement. Same compiler options and release C++ module bytes.

| Tokens | FC1 tactic | FC1 non-NOP | Registers | Local bytes | FC2 / combine |
|---:|---|---:|---:|---:|---|
| 16 | M128 N8 K256, 1 CTA, CLC | 1526 → 1502 (−24) | 96 → 96 | 0 → 0 | Raw PTX, cubin and SASS identical |
| 32 | M128 N16 K256, 1 CTA, CLC | 1588 → 1540 (−48) | 96 → 96 | 0 → 0 | Raw PTX, cubin and SASS identical |

Only FADD/FMUL versus FADD2/FMUL2 instruction counts change. Scalar EX2/RCP counts and FTZ modifiers remain unchanged, with explicit RN packed multiply/subtract and no FMA contraction. No added memory, barrier, scheduling-control or other opcode count, and no resource increase.

This is **not schedule identity**: the compiler interleaves SFU, address calculation, BF16 packing and shared stores differently within the epilogue. The non-arithmetic opcode order differs in these local regions:
- T16: control 0x3a90–0x4340; candidate 0x3ae0–0x41b0
- T32: control 0x3990–0x48a0; candidate 0x3ca0–0x4590

The early textual branch differences are address relocations after code size changes. The recorded routing delay begins before FC1 executes, whereas the new packed instructions are in FC1 epilogue. Captures therefore show arithmetic savings plus local scheduling changes; they do not prove those changes caused the observed end-to-end losses. The original losses remain in the result table. A separate six-cell reverse-order repeat tests stability without replacing that data.

The initial negative-native leaf failed in CPU-only preflight on a receipt path; R1 captured two candidate FC1/FC2 pairs but omitted the callable finalizer and correctly failed its whole-leaf gate. R2 fixes only capture introspection and contains four complete replay calls. All earlier logs and receipts remain preserved.
