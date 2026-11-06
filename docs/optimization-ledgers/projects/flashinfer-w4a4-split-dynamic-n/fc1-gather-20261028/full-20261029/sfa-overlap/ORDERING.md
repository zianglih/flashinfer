# SFA S2T overlap candidate

Source: base `fb66a27e`; candidate kernel SHA256
`04c92e1fbea8222c58ae968e627790366c41ca1a8338ecf52c543b12d1864104`.

FC1 per-stage order becomes:

1. Acquire the weight/SFA TMA stage.
2. Issue SFA0 S2T and SFA1 when two channel tiles are present.
3. Acquire gathered B/SFB publication from the CTA/cluster relay.
4. Issue SFB S2T, then the unchanged MMA sequence.
5. Release the shared operand stage after the final channel MMA completion.

Weight and activation scale TMEM regions are disjoint. SFA copy source visibility
comes from the existing weight TMA completion wait. Moving those copies earlier
does not consume gathered B/SFB or weaken its publication. The group-one/group-two
S2T atoms, issuing leader warp, stage phases, tail-K copy extent, TCGEN05 issue
ordering and final operand release are unchanged. FC2 keeps its original copy
order; compile-time specialization of the complete module has identical AST.

Local CUTLASS precedent: SM103 grouped blockscaled GEMM issues S2T scale copies
before waiting on independent payload readiness at lines 1228–1246 of
`references/cutlass/examples/python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/sm103_grouped_blockscaled_gemm.py`.
That is an ordering precedent, not a replacement for our gather relay protocol.

Local parsing, Ruff lint/format, diff whitespace and specialized FC2 AST checks
passed. Source and patch hashes are recorded in `source-proof.json`. Runtime
correctness/codegen/performance results belong in the separate campaign receipts.
