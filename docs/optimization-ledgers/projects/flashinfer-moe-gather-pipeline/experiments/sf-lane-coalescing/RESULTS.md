# SF lane coalescing: rejected at the native pilot gate

Retained `2b8eb9d8` is unchanged. Both the lane-coalescing candidate **86836355** and the compact Int32 row-cache revision **377f0404** are rejected. No performance measurements were run.

The narrow NVFP4 N16/G4 candidate passed the existing exact oracle and kept 168 registers with zero local bytes, but added 31 static non-NOP instructions, two global loads and three shared loads. Its ordinary-TMA FC2 and finalizer were byte-identical to control. The wide MXFP8 N256/K8/G2 candidate failed the native resource guard **before FC1 launch**: driver local bytes rose from 0 to 64 at unchanged 168 registers. Its compiler artifact contains 43 LDL and 15 STL sites, and 3,691→4,112 non-NOP instructions. PTX has no explicit local depot; cuobjdump calls this STACK64 while the loaded function reports LOCAL_SIZE_BYTES64.

R2 cached Int32 source rows and kept the Int64 cast before stride multiplication. It reused both saved controls and reran only the two candidate pilots. Every available native image was byte-identical to R1, including the failed wide PTX/cubin: the compiler hoisted the pure address calculation back into the same live offsets and spills. Narrow exactness passed again; wide FC1 again never launched. The proposed `% G`→`& (G-1)` rewrite was also already folded in both pilots. Full-K channel predicates were already eliminated; the additional predicates guard the changed row ownership.

This closes the tested mapping and its simple compact-cache spelling. Do not relax register quotas, add a shape exception, introduce compiler-forcing workarounds, or launch the held timing screen to rescue it. The observed TP scale-memory issue signal remains real; this rejected candidate is not a successful remedy.

Evidence is preserved:

- R1 source/patch/proofs: `r1-preserved/`; detailed gate: [QUALIFICATION_RESULTS.md](QUALIFICATION_RESULTS.md), `pilot-gate.json`, `pilot-native-failure.json`.
- R1 raw qualification: `qualification-evidence/` (three completed exact calls including two controls; wide compilation rejected before launch).
- R2 source/patch/proofs: `r2/`; native identity and reused-control proof: `r2/pilot-gate.json`.
- R2 raw qualification: `qualification-r2-evidence/` (one new exact call, one prelaunch failure, two prior controls reused byte-for-byte).
- Native lowering follow-up: [MASK_AND_PREDICATE_AUDIT.md](MASK_AND_PREDICATE_AUDIT.md).
- Read-only full source/native-cache/idle closure: `pilot-closure-evidence/` and `pilot-closure-r2-evidence/`. Each verifies both 13,245-file inventories and unchanged persistent libraries/Ninja descriptions. GPUs 0/1 were released with no PIDs, zero utilization and zero MiB.
- The remaining nine exact pairs and the 56-cell/22,400-sample performance plan stayed unexecuted. `performance/` preserves the held configuration; existing historical baselines/caches are untouched.
- Original pre-GPU receipt-path error and immediate post-process rolling-telemetry stop remain in the original qualification receipts. They were corrected without changing source, numerical/compiler/resource helpers or rerunning successful controls.

Only the rejected source checkout/local branch is retired. Patches, helpers, runbooks, raw artifacts, failure records and immutable remote sources remain available.
