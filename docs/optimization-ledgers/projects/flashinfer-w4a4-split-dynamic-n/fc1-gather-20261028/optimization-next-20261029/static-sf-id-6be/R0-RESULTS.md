# Static SF-ID R0: blocked by code-generation guard

The source-level change has a concrete instruction reduction, but is not qualified for launch or retention. All39 retained-control exact cases passed with76 captures. The candidate stopped at the first generated M512/N128/K8 MXFP4x8 FC1 before launching it because local-load sites increased. Candidate source34fc7ac0, base6be, remains unstaged/frozen. No candidate correctness or timing result exists.

|First paired FC1|Control|Candidate|
|---|---:|---:|
|Initial registers|168|168|
|Stack bytes|168|144|
|LDL sites|21|48|
|STL sites|21|19|
|Non-NOP instructions|4189|3974|
|SHF + USHF|150|121|
|LOP3 + ULOP3|185|149|
|R2UR sites|385|322|
|MMA / S2T sites|32 / 12|32 / 12|
|BRA / ELECT sites|116 / 9|116 / 9|

The original descriptor-only local traffic is not the complete story after this change. Candidate SASS adds32-bit common-state spills before the control-role branch: shared-storage base atPC0440, grid-stride value at04d0, and total-tile count at0ca0. Their reloads occur in multiple role and wait paths. The smaller stack is therefore insufficient evidence of improvement. No role quota changed (control120/gather128/epilogue256, initial168).

The complete local hash-verified control archive is2f2463aaa003bea06ca574447bb482af592d75120f6465a55795e8963ff9b909 (399files). The preserved failed candidate archive iscc60191cc2c95425ec45f3212587d97ccd8a0eb6603c3c921c49e7f3c1f78557 (24files). Resource/site details are inr0-codegen-analysis.json. The guarded callable was never returned; no guard relaxation or sanitizer was used.

The static arithmetic proof and full-module AST audit remain useful: only the two selector expressions changed. K96 dynamic SF word strides preserve the byte selector. This proves intended selector equivalence, not the quality of generated register allocation.
