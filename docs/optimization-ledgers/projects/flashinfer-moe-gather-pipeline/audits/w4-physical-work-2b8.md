# W4 physical-work audit at2b8

Read-only audit of retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`; the W4 kernel SHA is `5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d`. No source/GPU experiment is implied by this audit. The separately authorized output-ring prototype has its own folder and receipts.

## New concise instruction lead: output-slot index

Both TMA epilogue branches increment `num_prev_subtiles` and divide by `num_c_stage` to recover the physical shared slot. This count is otherwise unused. A bounded residue has the same initial slot0, first write1%stages, store order, and lifetime. It stays unchanged on SIMT tails, fused-finalize paths, work-tile/expert transitions and empty output paths, exactly as before. PipelineTmaStore's own commit counter is independent and must remain unchanged.

The existing paired-SiTU wide SwiGLU native capture (`experiments/w4-paired-situ/qualification/evidence/1793379350474754000/data/candidate-w4a16-5/codegen/00-Sm100W4A16GroupedGemmKernel.ptx`) emits signed division-by7 bookkeeping: increment, mul.hi, two adds, two shifts, multiply-by7 and subtraction before shared addressing. This is actual emitted code, not an assumed cost of a Python modulo. The compact residue recurrence may or may not let the compiler remove that division; native qualification is required. Power-of-two stages may already have a cheaper retained sequence and must be compared too.

History search distinguishes the old rejected W4 “modulo” trial: `flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/full-20261029/w4a16-gather-ledger.md` identifies it as **gather warp_idx−16→warp_idx%4**, with more SASS/R2UR and EP prefill−1.03%. That is unrelated to the epilogue slot. No output-slot trial was found in the July W4 optimization ledger, October split ledger, gather-next CLOSED_LEADS, or current effort audits. Rubin's regular grouped kernel inherits the same monotonic-count/modulo epilogue; the installed PipelineState.advance instead uses a bounded index and wrap.

## M-side padded CTA: algebraic independence is insufficient by itself

For the current public M128-per-CTA geometry, a CTA whose entire output-channel interval is outside logical M contributes no valid output:

- BF16 MMA reduces K, independently for each M row. Two-CTA execution does not reduce one CTA's M rows into the other CTA's rows.
- W4 scales are decoded per row/K block into BF16 A; there is no separate blockscale-MMA metadata coupling neighboring M rows after dequantization.
- Gate/up blocks16 and64 occupy32 and128 physical rows respectively, so complete pairs fit inside128-row CTA boundaries. The old-layout in-kernel transpose only rearranges those local rows.
- Gated epilogue folds each local gate/up pair to its corresponding output channel. Nongated output retains local rows. TMA's logical M extent and SIMT predicates discard the invalid channel interval; combine never reads that interval.

Examples are the wholly padded second CTA of the last M256 tile for N3U TP FC1 M640 and V41F TP gated FC1 M1152. This is a **public-layout** argument, not an unrestricted proof for private M64 layouts or another packing contract.

However, a simple M-valid predicate around decode **and TMEM stores** can leave allocated BF16 A TMEM uninitialized on a CTA's first work item. Current K-group skipping is different: the peeled MMA never reads the skipped K columns. M-side MMA still reads the skipped A rows. The mathematical output noninterference does not independently establish that reading arbitrary/uninitialized allocated TMEM is an allowed architectural operation. The PTX allocation/TCGEN sections reviewed do not explicitly promise initialized allocation contents or bless this usage. The documented Compute Sanitizer TMEM guardrails cover allocation/bounds/alignment/operation validity; documented initcheck address spaces are global/shared, so a clean guardrail run would not by itself prove TMEM initialization legality.

References: [PTX TCGEN allocation and MMA](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-mma), [Compute Sanitizer tensor-core guardrails](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html#tensor-core-mma-guardrails). Current online ISA is9.4; deployment is CUDA13.2, so no newer-ISA facility is proposed.

A defined-value alternative would retain TMEM stores and write zero fragments on the M-invalid branch, removing raw reads/conversions while retaining initialization. It adds a branch/value path and an M handoff to the shared transform helper. This is not the same simple guard and is not proposed for implementation without a cost/complexity review. A one-time initialization state would add further lifetime complexity and is not justified by this audit.

## Other inspected work is already useful or requires ownership changes

- The retained packed FP4 decoder uses one direct scale PRMT, one E4M3→BF16x2 conversion and the necessary E2M1 conversions/multiplies per16 values. The two-scale scalar path remains deliberately untouched by the packed-word selector. No new duplicate conversion was found.
- The retained wholly unused K-group skip remains useful. Finer partial-group clipping is closed: the completed V41F TP screen did not justify57 extra source lines and native dispatch growth. This audit does not reopen it.
- Gated W4 shared stores look scalar, but adjacent packed arithmetic results map to different token rows: the representative PTX pair writes shared offsets1024 and1152, not adjacent16-bit channels. Native BF16 packing is already present. Recasting those two values to a32-bit shared store is incorrect without a new ownership/transpose step. Nongated/FC2 already use the existing collective R2S matrix-store path. Rubin's regular gated R2S path has a different accumulator/output orientation; it is not a drop-in replacement for the gate-folded W4 view. MegaMoE's W4 epilogue writes globally after its own TMEM ownership transpose, so it also supplies no free local-store substitution.
- Register redistribution, raw/B pipeline splitting, late output-acquire motion, scale-before-decoded-acquire motion and route/gather unrolling were checked against the local closed-lead index; no rebranded experiment is proposed.
- Symmetric clamp/fclip is owned by the integration agent and excluded here.
