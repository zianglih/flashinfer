# Compact cached routed indices

Read-only assessment of frozen `86836355`; no source file or compiler behavior was changed.

Caching `Int32` routed row indices is legal and concise. The illustrative, unapplied change in `row-index-feasibility.diff.txt` is **5 added / 6 removed lines**: change the existing register tensor to `Int32`, store `source_row`, and move the existing `Int64(row) * sf_row_stride` expression into address construction. Keep the cast **before** multiplication; multiplying in Int32 then widening can overflow for large row/stride products. No new helper, interface, state, predicate, layout or barrier is required. The current zero row for invalid tokens and the existing ignore-source predicate remain unchanged.

The source representation would use four fewer 32-bit values in the failing N256/G2 specialization, or eight fewer for N256/G4, **if** the compiler retains compact indices through the K loop. These are arithmetic live-value counts, not a measured register reduction.

The native evidence does not establish that it will:

- Current candidate PTX emits four `mul.wide.u32` operations at lines 3880/3887/3894/3901 before the dynamic K loop at line 3922. Each loop iteration adds the same channel offset to those four invariant 64-bit values.
- Actual SASS retains those offset pairs at R60/R58/R56/R54 while it spills several Gather4 row indices produced by `SHFL` and `R2UR` (`c540`–`c750`). This confirms competing long-lived coordinate state, but does not isolate all 64 local bytes to SF offsets.
- Merely spelling the pure multiply inside the loop does not constrain placement. Loop-invariant motion can recover the same four wide values; alternatively, rematerialization can trade those registers for repeated wide multiply/address work at every K stage. The existing inline copy only constrains the final address operand, not where its pure arithmetic is calculated.

Therefore this is a small general-purpose source experiment, **not a reliable spill fix by inspection**. A single unchanged-option native comparison could determine whether compact state survives. Avoid source-level compiler forcing, register quota changes, new PTX, or geometry-specific fallbacks. If the compiler restores the same live offsets or local memory remains, this approach provides no reason to reopen the performance screen.

`row-index-feasibility.json` binds the source, native PTX/SASS, illustrative diff, and boundary arithmetic checks. The failed wide specialization remains an explicit native resource failure before launch; no numerical or timing result exists for that candidate.
