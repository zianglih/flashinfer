# Independent private FC1/FC2 K-depth tuning

The experimental tactic/cache representation adds an optional fourth outer field `(FC1 K steps, FC2 K steps)`. Each step value is 4 or 8. This is internal autotuner state, not a new public FC API option. Both legacy Blackwell three-field entries and Rubin's existing three-field outer/four-field inner representation remain valid; legacy entries use automatic K depth. An explicit pair on a Rubin entry is rejected.

Public generic and deprecated NVFP4/MX FC signatures and defaults are unchanged. Their explicit thin adapters call shared private implementations with no K override. Full-MoE execution routes the selected pair to those private implementations, which retain one copy of shape validation, routing preparation, and launch logic. No thread-local state, signature rewriting, or public policy selector is used.

`_k_stage_capacity` shares the existing SMEM/TMEM calculation between automatic selection and explicit capability checks. Capability admission requires a minimum viable operand/accumulator slot; the constructor and actual SDK layout calculation retain the requested overlap/stage-policy validation. The CPU census verifies that all generated admitted choices fit their actual phase configuration, including cluster scale-join metadata. It does not replace GPU compilation/execution evidence.

There are 180 raw chain candidates and 160 admitted for each currently supported operand/scale configuration; M512/N256 is rejected by tensor-memory capacity. Independent K choices make four chain candidates per geometry pair, but only double the maximum unique phase/geometry/K specializations: 28 to 56 per dtype/output regime. Legacy caches remain parseable. W4A16 and Rubin tactic enumeration are unchanged.

The same candidate includes the separately reviewed all-geometry FC1 CLC request, preserving generic work-count, SM-budget, and grid-Y limits. The logical channel count uses validated M128/M256/M512 geometry rather than a special M512 branch. No core device method changed in this K plumbing patch. Previously frozen generalized-core/narrow-CTA work remains part of the combined experimental checkout.

CPU evidence is in `cpu-check.json`: 5,400 planner-equivalence cases, 672 explicit phase storage fits, 180 JSON round trips, six unchanged public signatures, and 1,086 executed runner-forwarding cases. Source-extracted CPU execution uses bounded SDK byte-layout stubs. `precommit-private-final.log` records scoped formatting/type/lint checks.

The new task-local `probe_explicit_k_chain.py` plans 210 candidate-only public replay comparisons (seven configurations, legacy plus four K pairs, MoE PDL off/on, three input/routing mutations). NV activation quantization is explicitly opted in; MX remains prequantized. This avoids relabeling the old prequantized-input replay hashes as a same-input control. GPU execution and native performance retention are pending at this snapshot.
