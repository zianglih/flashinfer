# Logical-stage MMA handoff qualification

- Frozen kernel `1caf4331`, patch `4f862f84`, base `fd72759b`; candidate changes only the blockscaled kernel. The final integer-contract follow-up has separate evidence in `../mma-integer-k/`.
- 160 candidate graph replay outputs match saved control storage bytes. Eight geometry/format configurations plus two native-K64 controls cover static/CLC, PDL off/on, one/two CTA, M512, N256, partial K, and balanced/skewed/nonlocal-empty/reactivated routes. Each source independently verifies caller mapping, compact prefixes and dense-index uniqueness.
- 80/80 GEMM PTX files are byte-identical. 78/80 SASS instruction streams are identical; two MXFP8 FC2 CLC N256 streams differ only by the independently reviewed live-range UR16:17/UR18:19 rename. Instruction order, resources and counts are unchanged. Zero local/stack spills. Existing uniform-register spill/fill sites in twelve MX FC1 pairs are unchanged (2–12 sites per affected kernel).
- Strict initial SASS-equality rejection is preserved; the reviewed analyzer proves the bounded register rename rather than claiming binary equality. No timing or sanitizer run.
- Raw PTX/cubin/SASS, source hashes, compile commands and exact results are in `gpu/evidence/`; all809 manifest entries were verified. Archive SHA256 `d4f77e7feda91a5c5b3c8258427bb52447d281849087be80c14b2fef745bf03c`.
