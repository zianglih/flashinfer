# MMA election-scope probe: rejected

Control374ed4c0 versus moving elected-lane scope around the static MMA-width loop. Both FC1/FC2 and all dtypes share the helper.23 existing exact tests per arm passed;44 generated kernels per arm passed executable register guards, with zero local memory.

The intended instruction reduction did not occur: every pair has unchanged election, branch, and MMA issue counts.29 pairs have identical non-NOP counts; six remove1–6 instructions, while nine add2–113 instructions. Two wide two-CTA MX FC2 instances add113 instructions and45 R2UR operations. Moving the source election scope perturbs register/uniform lowering without removing machine elections. Reject without end-to-end timing; do not add dtype/geometry exceptions.

The initial control helper retained a relay-specific assertion against an older historical FC2 binary and stopped before candidate launch. R1 removes that inapplicable assertion, keeps all current source/executable-register/exact-output guards, and performs a new paired capture. This was a helper failure, not a kernel numerical failure.

Raw paired evidence: gate-evidence,459file hashes verified; archive81cf2797d26a5f18cf52d9ed90a0d4db4c09c38e236142e73c36bd5c134ab47a. Regenerate comparison with compare_codegen.py. No sanitizer; no performance claim.
