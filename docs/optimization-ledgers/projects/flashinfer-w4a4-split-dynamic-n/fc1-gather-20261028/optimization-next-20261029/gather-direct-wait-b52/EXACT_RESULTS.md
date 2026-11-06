# Exact qualification

- Candidate `c5373aa1` on retained `b52e4e09`: **41 existing cases passed**, 80 matched captures.
- Every geometry/quota/resource guard passed. 78 captures have no local storage; the two inherited synthetic M512/K8 MX captures retain128 B stack and16 LDL/16 STL sites.
- 10 affected one-CTA FC1 captures; all70 unaffected PTX files match.69 unaffected CUBINs match; FC2 capture35 has identical PTX/resources/opcode sequence with changed register assignments. Raw differences are preserved in `exact-fc2-register-assignment-difference.json`.
- Original26 compile-only captures independently showed8 affected kernels removing24–46 non-NOP instructions and6–14 branch/control sites; all18 unaffected binaries matched.
- Archive `86861ca7cabc021c84344b200795c1ac3e8f332aa4a74ec846cb90b16db9de1a` contains430 verified files. Candidate-only numeric qualification reused the immutable b52 control codegen; no numeric control rerun or sanitizer.
- Timing is a separate approved24-cell frozen-winner CAAC run. No performance claim follows from this gate.
