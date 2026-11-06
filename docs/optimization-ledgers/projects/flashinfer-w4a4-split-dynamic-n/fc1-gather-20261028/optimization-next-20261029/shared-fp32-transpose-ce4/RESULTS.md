# Initial shared-transpose compile attempt

Frozen source `e9801fb8` on ce4,58+/6−. Both matrix and native compile-only helpers stopped before producing any owned kernel because the dynamic warp-private pointer lost its alignment type: CuTe saw32-bit alignment for a128-bit CopyUniversal source. No owned MoE kernel ran, no numerical assertion was evaluated, and no timing exists.

The27-file archive is local and hash-verified (`fetch-receipt.json`, archive SHA`eb8d9abc8bd358c0a2e46442bc0fcade5fc849930632bda1b32b476839f1666b`). Source/patch/config/logs remain frozen here and remotely. R1 is a separate artifact, `../shared-fp32-transpose-ce4-r1`, with one explicit aligned pointer construction. Storage has128-byte base alignment,2048-byte warp stride and16-byte-aligned vector offsets; no shape restriction or runtime branch was added.
