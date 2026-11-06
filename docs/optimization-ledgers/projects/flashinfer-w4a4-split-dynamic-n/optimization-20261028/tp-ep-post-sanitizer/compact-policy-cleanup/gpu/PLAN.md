# Bounded policy-cleanup GPU qualification

Status: revised four-file patch3027b1b40824 is frozen against retained9e3cb4d5 and deployed to separate source-bound control/candidate snapshots. Paired gates use primary GPUs0/1; eight existing public API tests use GPU2. Every GPU was checked idle immediately before its process launch. No benchmark timing is needed if emitted code matches.

The gate reuses `fc2-tma/eligible-r3-k96/probe_pair.py` and `run_gate.py`, adapting observations to the final private metadata interface. No production source edits or new timing baseline.

- Frozen source patch/hashes against retained9e3cb4d5; source-bound control and candidate snapshots.
- Eight pairwise format/geometry cases: N64/128/256, M512N128 and M256N256, standard/per-token NVFP4, MXFP8 and MXFP4x8. Static/CLC and PDLoff/on; changing balanced/skewed/empty/reactivated routes.
- Target64 paired FC1/FC2 compiled specializations and128 paired output-storage-bit comparisons. Fixed K4 stages expose the overlap predicates; exhaustive automatic-planner proof is separate.
- Assert matching compiled planner/overlap/metadata states. Capture PTX, cubin, SASS and resource reports with a private compiler CWD per process. Compare instruction streams and resources; distinguish exact raw artifacts from normalized debug metadata. Include MOV.SPILL/R2UR.FILL, local/stack loads, barriers and waits.
- Reuse persistent native compilation caches through existing links, without clearing cache or modifying retained source snapshots.
- No full benchmark when emitted code is identical. No sanitizer claim from this bounded gate.

The candidate uses `_get_output_workspace` through the real public API. Observers inspect `workspace.offsets` and `workspace.indices`; FC1 has no dense indices, N64 has no workspace, and N128/256 cover compact full/tail stores. Additional generic combine checks omit the workspace for expanded/permuted layouts with PDLoff/on. Eight unchanged repository tests cover MXFP4x8/MXFP8 public APIs (N16 and two-CTA N128), NVFP4 standard/per-token wrapper accuracy, and CUDA graphs.
