# R0 binary-tree qualification

Frozen candidate547f8778 on b139 passes the paired39-case existing exact gate:76 owned kernels per arm. All paired resource bounds pass; role quotas remain120/128/256. The two known M512/K8 MX control cases retain168-byte stacks and21LDL/21STL sites, without growth. All other captured cases have zero local/stack usage. Source AST proof isolates `_absmax`;55,184 actual-AST CPU cases cover max-number semantics including all-NaN, signed zero, infinities and subnormal inputs.

All37 FC2 PTX pairs are identical.35 CUBIN pairs are identical; the other two contain the same12-site UR16/17↔UR18/19 descriptor-register permutation previously documented, with all other instructions/resources unchanged. Captured per-token BF16 FC1 paths are unchanged. No claim is made that every CUBIN is byte-identical.

The candidate has a real static-cost tradeoff. The simplest gated NV block changes the reduction from8 serial `FMNMX3` instructions to11 maximum instructions; direct max-dependency depth decreases8→5. Wider gated paths show8→6 or9→7 including adjacent maximum work. Static epilogue cost increases3instructions per scale block, typically24 for unrolled M512. ReLU2 grows41–45 instructions across the captured epilogue. No performance measurement has been launched.

This supports a codegen-driven ternary-tree refinement before the predeclared44-cell screen:16 magnitudes plus final+0 are17 inputs, which fit8 ternary maxima with depth3. It must retain the same max-number identity and use ordinary compiler-visible fmax operations. The binary-tree source and all negative/cost evidence remain frozen; any refinement requires a new exact/source-bound gate and cannot inherit this qualification silently.

Artifacts: `gate-evidence.tar.gz` SHA256bd4472c293b342b2cf55dcd3b92168f02eac2fb667d8655cc2e35a61871739fc,17,151,135bytes,785 semantic files hash-verified. `paired-exact-analysis.json` verifies every captured artifact/resource pair. `reduction-codegen.json` records all static reachable epilogue sites and straight-line FMNMX dependency evidence. Dependency depth is not a complete hardware latency model or measured speedup.
