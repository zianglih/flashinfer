# R9: three-warpgroup register redistribution

Isolated candidate from frozen R6 (`deba8b63`), preserving the384-thread FC1
gather layout and every data/scheduling pipeline. No review checkout edits.

Immediately after common TMEM retrieval and before PDL/role dispatch, complete
warpgroups choose control80, epilogue256, and gather128 registers/thread. FC2
compiles out the entire policy. There are no new barriers, buffers, tactics,
geometry conditions, arithmetic changes, or additional reconfiguration sites.

The candidate requires59,392 registers. The GPU harness must validate the new
candidate's actual launch allocation and instruction policy before allowing
launch; source validation alone cannot establish a valid CTA register pool.
At emitted initial168 registers/thread, the384-thread CTA owns64,512 and has
5,120 registers of headroom. The initial allocation must also satisfy both
decrease targets and the increase direction.

`build.py` reconstructs `candidate-kernel.py`, writes `candidate.patch`, and
verifies byte-for-byte reversal to R6, FC2 constexpr elimination, other-source
AST identity, full-WG target agreement, and unchanged review source. Results
are in `source-proof.json`. No GPU correctness or performance result is claimed.
