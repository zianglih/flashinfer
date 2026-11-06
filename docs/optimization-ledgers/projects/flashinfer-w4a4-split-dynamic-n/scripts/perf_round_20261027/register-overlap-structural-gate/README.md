# Structural cold-spill verifier

Frozen production source remains651b8a96 onf7182d5c. This task-local verifier generalizes the independently reviewed cold shared-base pair to renamed registers and relocated instruction addresses. It introduces no kernel policy or stack-size tolerance.

A nonzero stack is admitted only when all facts are proved: exactly one scalarSTL and one scalarLDL share the unchanged stack slot; the startup value is the immutable dynamic-SMEM base; final CTA join and the verified allocator-warp0 guard dominate the reload; the exact terminal phase-zero wait has one external entry, no alternate slow-block entry, and no path to payload transport/MMA or back into the mainloop/epilogue. Unsupported indirect CFG, larger/multiple/payload spills, altered phases, or unclear provenance fail closed.

The outer guard separately retains actual initialized-register, threadcount,96/240 direction, and physical-pool checks before returning a callable. Source/cache/helper identity remains checked by the runner. Both real cold artifacts pass,18unsafe mutations are rejected, and3outer-guard tests prove that the structural result cannot bypass invalid register pools or permit control spills. Raw stack/local observations and the complete proof are retained per kernel.

This criterion recognizes a measured cost: one four-byte startup store per CTAthread and one four-byte reload per allocator-warp lane per slow-wait iteration. It does not label those kernels zero-spill. Full exact and performance coverage is still required; no production resource guard or fallback is added. Original hash-only and strict evidence remains immutable.
