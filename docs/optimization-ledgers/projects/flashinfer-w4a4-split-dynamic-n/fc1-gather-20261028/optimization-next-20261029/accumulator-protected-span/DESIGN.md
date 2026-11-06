# Resource-derived accumulator protection

Candidate is an unstaged one-file change from retained374ed4c0 in `flashinfer-swap-ab-protected-span-review`. No API, tactic, dtype, scheduler, PDL, operand-ring, weight-prefetch or arithmetic change. W4A16 is unaffected.

The old SF<=64 eligibility rule describes one historical FC2 read slab, not the actual TMEM limit. FC1 already traverses a compile-time number of32-column transpose slabs before releasing the accumulator. This candidate derives the protected interval from the actual combined SFA/SFB footprint and the epilogue read granularity (32 for FC1; the existing32/64 bulk-token slab for FC2).

Let C be accumulator columns and S the combined SF columns. Overlap is used only when two full accumulator windows occupy the hardware capacity,2C=512; at least one accumulator plus scales must already fit. With release granularity G, P=ceil(S/G)*G. Windows are [0,C) and [C-P,2C-P), so their intersection has P columns. Scale storage begins at2C-P; S<=P guarantees all storage remains within512. The constructor's power-of-two allocation of C+S already reserves512. Current admitted geometries produce P<=128<C. All accumulator addresses remain32-column aligned, stronger than SF's4-column atom alignment. SF channel banks and native-K96 compacted SFB views remain entirely within their original scale footprint.

- FC1 reads high slabs first for the low window, then low slabs first for the high window. It already releases after P/32 slabs. Transpose scratch stays within each32-column slab; the existing async-TMEM-load fence follows its last read before release. Quantization/output arithmetic afterward uses registers or independent shared scratch.
- FC2 follows the same alternating direction, using its existing32/64-column full slabs. Release is moved from literal64 to P after the second channel-half load. Partial slabs still perform their existing32-column SIMT work; release follows the final subslab, including skipped subslabs. Empty groups release at the same static boundary. Shared output staging/TMA waits are unchanged.
- Both CTAs retain their existing consumer-release participation. The producer must acquire the same single accumulator pipeline stage before writing the alternate window. The interval proof therefore holds even if one CTA reaches release earlier.
- SF copies remain outside both accumulator windows and are still owned by the MMA warp with existing ordering. No scale publication or operand barrier changes.
- PDL signaling, CLC work publication, ring capacity, terminal drain, and all steady-state waits stay unchanged.

`prove_lifetime.py` source-loads the new eligibility helper and checks42 eligible geometry/slab cases, both directions and every valid-row count, including zero.20,052 lifetime checks assert exactly one release, no post-release TMEM read/transpose-write overlap with the next MMA, alignment, and total allocation bounds. This is an ownership proof, not a runtime correctness/performance claim.

The prior FC2 bulk32 path also derives P from32 rather than conservatively retaining64; this is deliberate resource policy generalization. Existing full bulk64 cases with S<=64 keep their previous windows. Newly admitted S96 cases use P96 for FC1 and P128 for bulk64 FC2. Automatic K-step selection may now admit its existing K8 candidate when this previously artificial limit was decisive; no tactic is added.

Reference: existing SM100 NVFP4 MegaMoE swap-AB epilogue computes `_iter_acc_early_release=ceil_div(_num_sf_tmem_cols,EpilogueTokenTile)` and subtracts scale footprint from its combined accumulator reservation. Its exact layout is not copied here.

Validation: frozen source hashes and local patch are in `local-source.json` and `candidate.patch`. GPU2 runs35 exact cases reusing existing test/reference functions with three additional local geometry parameterizations, then records compiled CUBIN SASS/resources and prelaunch physical-register-pool guards. No sanitizer, timings or retuning in this gate.

Local review checkpoint: after deployment, the active copy was bumped to22ffe662 plus this one-file delta; `review-bump.json` records it. Remote isolated qualification remains374+patch, byte-frozen. The new retained SF predication occupies a separate source region.
