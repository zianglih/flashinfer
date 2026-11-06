# T8 G512/G1024 raw-encoding audit

**All four selected rank pairs differ in exactly four CUBIN bytes.** Those bytes lie in the four expected immediate-bearing instructions. No other instruction bits, including scheduling controls, differ. This is an untimed local audit; the binaries are not identical and equal runtime latency is not established.

The audit reads each rank's `result.json` to select the actual O3 N64/epilogue int32/contiguous specialization (`compile-000` G512 versus `compile-004` G1024), checks captured hashes, then compares the full ELF and both 64-bit words of every SASS instruction. Concatenating all disassembly encodings reproduces the complete executable section byte-for-byte, so the result does not depend on stripped mnemonic text.

Per rank: **161,864-byte CUBIN; 29 ELF sections; one 82,816-byte executable section; 5,176 128-bit instructions.** All ELF headers, section metadata and non-executable bytes match. Every high 64-bit instruction word matches. Only bits 41/42 of each instruction below differ, within its 32-bit immediate field:

| PC | Operation | G512 low 64 bits | G1024 low 64 bits | Identical high 64 bits |
|---|---|---|---|---|
| `0x1c30` | `ISETP.GT.AND` bound `0x7ffffdff → 0x7ffffbff` | `0x7ffffdff0400780c` | `0x7ffffbff0400780c` | `0x000fc60003f04270` |
| `0x1c70` | `VIADD` threshold `0x200 → 0x400` | `0x0000020004087836` | `0x0000040004087836` | `0x000fe20000000000` |
| `0x33e0` | `ISETP.GT.AND` bound `0x7ffffdff → 0x7ffffbff` | `0x7ffffdff0f00780c` | `0x7ffffbff0f00780c` | `0x000fe20003f04270` |
| `0x3430` | `VIADD` threshold `0x200 → 0x400` | `0x000002000f077836` | `0x000004000f077836` | `0x000fe20000000000` |

The full-file changed offsets are `0x46b5`, `0x46f5`, `0x5e65`, `0x5eb5`: respectively `fd→fb`, `02→04`, `fd→fb`, `02→04`. The complete code difference is therefore the expected threshold and signed-overflow-bound immediates; there is no hidden stall/yield/barrier-control encoding difference or other binary-metadata difference to explain the earlier cold-timing variation. This does not exclude a runtime consequence of the changed thresholds or measurement/rank-arrival effects.

All **162 original collected artifact hashes** were verified before and after; original files were not modified. Reproducible local parser: `../audit_group_t8_encodings.py`. Complete per-rank selected paths, hashes, raw words and checks: `raw-encoding-audit.json`. No GPU, remote-node or GitHub operation was performed.
