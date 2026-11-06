# R1 qualification before performance

Candidate `abd55f60f643e1e7c467edc4354b3f50e1cca3d9a5d06a34a6b954721b571a36`, only `_absmax`, based on b139. CPU extracted-AST proof: 55,184 vectors; all applicable precommit hooks pass.

Fresh paired compile-only gate: 15 control +15 candidate captures; all resource tuples unchanged. The two M512/K8 MX formats retain their existing 168-byte stack and21 LDL/21 STL sites; every other case is zero-local. FC2 (2 cases) and BF16 per-token FC1 (3 cases) have byte-identical PTX and CUBIN.

Actual SASS emits the same eight FMNMX3 operations per16-value absmax, now depth3 rather than8. MX SF32 retains its extra reduction: depth4 rather than9. Whole reachable epilogue instructions are unchanged in most cases; NV ReLU2 decreases10, M512 SiTU increases2, MX ReLU2 increases1. Static instruction/dependency counts are not latency estimates. The dependency analyzer explicitly clears every register defined by vector TMEM loads, avoiding stale dependencies from prior fragments.

All173 fetched files hash-verified; archive SHA c32841cf2aa26f283704f9b7717720724e55a04130bdc0a84adb9deb4fe6dfdf. Existing39 exact candidate cases passed, with76 captured kernels all within matched resources. All37 FC2 PTX pairs and36 CUBIN pairs are identical; the remaining1 retains the previously observed12-site uniform-register renaming, with no other SASS/resource changes. The unchanged b139 control39/76 qualification is reused fromR0 by full source/helper hashes. All candidate evidence was freshly fetched and hash-verified. No performance launched at qualification time.
