# Cyclic epilogue traversal, retained overlap policy

Source: detached `22ffe662`, one unstaged file in `flashinfer-swap-ab-cyclic-epilogue-review`. The qualified R3 kernel is `e252156b43d359f89121f611a341aa200f6bf07ea721a6f93c022f82a1b16101`; `r3/local-source.json` binds all514 source files. No W4A16 change or additional tactic/eligibility.

The prior protected-span experiment is rejected: six newly overlapping native cells regressed geometrically2.089%, including K3 TP per-token5.555%. See sibling `accumulator-protected-span-screen/RESULTS.md`. Its overlap-policy expansion is absent here.

The retained implementation emits two complete epilogues for forward/reverse accumulator phases. This candidate emits one cyclic ascending traversal, starting at the shared interval in phase0 and at zero in phase1. MegaMoE uses the corresponding cyclic-subtile approach in `moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/epilogue.py`, particularly `_subtile_local_tmem_tensor` and the FC1/FC2 subtile loops.

- FC1 still releases after the scale footprint rounded to32-column slabs. A logical M512 tile is one virtual column range across two channel tiles.
- FC2 still releases after64 columns. Its shared TMA store ring remains64tokens×2stages or32tokens×1stage.
- Both phases consume the complete shared interval before the existing TMEM load fence and release. Remaining TMEM reads and transpose scratch are disjoint from the next MMA window.
- Per-token scale register indices remain compile-time literals. Only the value is selected by phase; no dynamic register-memory indexing.
- All stage counts, scheduler/PDL behavior, MMA/TMA synchronization, output format and overlap eligibility remain unchanged. AST evidence:33 unchanged methods; only two epilogue methods changed and their two direction wrappers removed.

R0/R1/R2 did not execute the failing N256 FC1: CuTe's Int32 slab select discarded constrained-integer alignment metadata before TMEM pointer arithmetic. R3 instead computes the cyclic index directly from the existing CuTe pipeline phase. This preserves the `cute.assume` metadata and needs no added helper, shape fallback or pointer re-creation. Failed revisions and IR are retained locally.

## Qualification

- Control33/33, candidate33/33 exact cases passed. These include four formats, one/twoCTA, M512, partialK, both scheduler modes, and forced-multiwave ReLU²/GeGLU/SiTU per-tensor/per-token output. The native MMA plan determines the unchanged oracle.
-64 compiled kernels per arm, actual-CUBIN register-pool guard passed before launch.
-38 kernels have identical PTX and byte-identical CUBIN. All26 changed kernels remove1,421–4,065 static non-NOP instructions and13–34 static branches. FC1 remainsREG168. FC2 needs2–6 additional registers; no new local-memory/spill sites. The two pre-existing MX M512/K8 stack168B cases are unchanged.
-35 TMEM geometries and16,710 phase/valid-row ownership cases pass the CPU proof. The two actual shared-store-ring layouts pass1,028 phase/valid-row cases. These are lifetime proofs, not substitutes for GPU exactness.
- Scoped precommit passed, including mypy andruff. Sanitizer deferred as requested.

## Performance

Sibling `cyclic-epilogue-screen` runs12 fixed-native-winner cells:10 affected prefill cells across allfour models, EP/TP andfour swap formats, plus2 unaffected controls. Same physical GPU for each C-A-A-C,100strictCUPTI samples/phase,10warmups,coldL2 CUDAgraphs, publicAPI, inputquantization included forNVFP4; noAUTO, no clocks changed, persistent native/CuTe caches. Runtime source, cache, route, tactic, pool and NVML telemetry guards are unchanged. GPUs1/2.

Static code-size reductions are established; runtime instruction-count or instruction-cache benefit is not inferred without measurements. Results remain pending.
