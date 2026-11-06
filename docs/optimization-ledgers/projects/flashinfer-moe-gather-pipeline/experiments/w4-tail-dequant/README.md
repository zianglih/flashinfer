# W4A16 whole-group K-tail decode experiment

Base: retained `02de7785c10847b3528340840bed40bd405d85b4`. Review source: `flashinfer-w4-tail-dequant-review`, unstaged. The two-file source seal is `source.json`; exact patch is `candidate.patch`.

The split MMA already issues only the valid K16 atoms in the final stage. Dequantization still loads scales, decodes FP4, and stores BF16 for both complete K groups. The candidate skips a transform group's data work only when its entire interval is beyond the K extent consumed by MMA. It preserves all raw/decoded waits, acquires, releases, commits and state advances. The active group's next-raw peek stays at its original last-fragment position. A skipped group is necessarily in the last stage, so its branch needs only one raw-state advance.

The predicate is absent at compile time for full K and for partial tails touching every group. Partially live groups retain their existing padded decode. No allocation, stage count, scheduling, register target, public flag or tactic changes.

The shared internal argument becomes consumed K extent plus explicit transform-group coordinate. Split passes logical K. MegaMoE explicitly passes ceil-div stage count × stage K because its existing MMA loop consumes complete padded stages. Mega's arithmetic and padded output contract are preserved.

## Ownership proof

`layout-proof-summary.json` binds the actual pinned CuTe/CUTLASS probes and source. The public probe checks 655,360 coordinates: 10 current tiler geometries × two row layouts ×128 threads ×two groups ×128 values. Every group owns one contiguous half-stage K interval. `layout-proof-records.json` preserves the 5,120 partition records.

The private extension checks every stage-K multiple32 below512 with CTA-M128. K32/64/128/256 partitions satisfy the same formula; K512 also passes a separate partition probe but cannot fit the complete pipeline's minimum two decoded stages alongside accumulators. Other non-power-of-two stage K values fail the existing mode3 `logical_divide` before the new predicate. CTA-M64 paths fail the retained transform-partition/copy construction. These are bounds on existing constructibility, not new source restrictions or a claim that generic `can_implement` fully models compilation.

Probe V2 initially decoded nested K coordinates incorrectly; V3 used an unsupported arithmetic identity form. Both failures remain in their receipts. V4/V5 use the logical `(M,K,stage)` identity tensor instead. No probe launched a GPU kernel or measured performance.

## Qualification

- Scoped pre-commit passed before native qualification; final source has only the two intended files changed.
- Independent source/state review: `audits/w4-tail-dequant-peer.md` and `audits/w4-tail-dequant-peer-static.json`.
- Split exact/native qualification passed 12 control/candidate calls and 18 native pairs. Coverage includes both layouts, one/two CTA, static/CLC, PDL off/on, short K128, remainders64/128/192 and aligned K256. Registers remain96/128 for FC1/FC2 with zero local memory. Aligned kernels and all-live K448 FC2 are byte-identical. The combined gate is `qualification-summary.json`.
- Single-rank MegaMoE exact/native qualification passed all four calls under `mega-qualification/`, using the existing repository exact helper with `MEGA_NO_DIST=1`. Aligned H256/I256 and partial H384/I640 produce byte-identical control/candidate PTX, cubin and SASS. Both use96 registers and zero local/stack memory. Full13,245-file source pre/post guards passed. GPU0 was released. This is a representative native equivalence check, not a multi-rank test or timing claim; no eight-GPU rerun is needed for these unchanged executable paths.
- Authorized timing is complete for all39 affected cells, in two disjoint CAAC campaigns. `performance-remaining/AFFECTED_SCOPE.md` and its 104-cell source-derived inventory document why65 aligned W4 and all364 swap table cells are reusable. The original12 rows are preserved exactly; the extension adds27 cells. `combined39/` contains every raw phase median and the derived summary. Independent review of the combined evidence is required before retention; no source has been committed.
