# Independent tiny epilogue-release codegen review

Both versions already issue the accumulator arrival one NOP after the final TMEM load. The candidate moves the load and release earlier, rather than removing that NOP or a synchronization instruction.

| Core | Registers C→A | Forward encoded span C→A | Reverse encoded span C→A |
|---|---:|---:|---:|
| config0-fc1-pdl0 | 104→120 | 709→586 | 711→588 |
| config0-fc1-pdl1 | 108→118 | 703→579 | 702→578 |
| config6-fc1-pdl0 | 118→118 | 361→346 | 362→349 |
| config6-fc1-pdl1 | 120→120 | 365→348 | 368→353 |

Both sources already release one NOP after the final protected TMEM load. Candidate moves that final load earlier. In the2CTA SiTU specialization,98 activation math instructions from the last protected slab and dependent token-scale work now follow release; in1CTA SwiGLU, activation math was already after release and only a small amount of address/metadata work moves.

Real scheduling opportunity warrants only the parent-approved bounded four-cell timing, not a speedup or retention claim.2CTA adds16/10 registers for PDLoff/on;1CTA register count is unchanged. Count differences measure encoded spans, not cycles or dynamic executed instructions.

All16GEMM+6Prepare pairs have unchanged static instruction counts and storage; the18 unaffected pairs are encoded-identical. No spills. Exact output checks pass32 comparisons/source. Full per-direction PCs, hashes and work categories are in `independent-codegen-review.json`.
