# Read protected TMEM first, store outputs in row order

Base: retained d9dee2dae50fef5d14c609e277fbc29d48df08b4. This is a separate
follow-up to the rejected wider cyclic interval; its code/results remain frozen.

The rejected candidate was correct but exposed FC2 store latency. At K3 TP8K
per-token, the entire94us regression appeared in FC2's completion-frontier
extension. With128–191 live rows and a128-column shared interval, phase0 reads
and stores the SIMT tail first, then issues full TMA slabs0/1 and immediately
drains. Monotonic output stores can hide the same TMA drain behind the SIMT tail.
This is a source-grounded mechanism to test, not yet a causal profiling result.

The proposed implementation separates private bulk-output loading/packing and
storing. It first snapshots the protected interval in registers using existing
loads/conversions. Full slabs keep native Ld16x256/stmatrix ownership. Partial
slabs keep `_scale_pack_transpose`'s row-owned BF16/FP16 values after its existing
TMEM transpose. This is a union of two formats selected by the unchanged full-
slab predicate; there is no additional transpose, conversion, or CTA barrier.
Only after all protected TMEM reads/transposes finish does the epilogue fence
and release accumulator ownership.

The output loop then traverses groups in increasing row order. Protected groups
come from the snapshot; other groups load from the disjoint live TMEM interval.
Full TMA stores are contiguous before the partial SIMT tail, so the original
constant shared-stage ring and full-only commit policy are sound. Each TMEM
element is read once and each live output element is stored once. The existing
terminal read-drain/barrier remains.

Snapshot indices are compile-time constants. For a group in the low protected
interval, the low-phase index is `group`; for a group in the high interval the
index is `group-(groups-protected_groups)`. If the intervals overlap, select
between these two constant fragments. Do not use a modulo shortcut: it fails
for a192-column protected interval. The prefetch loop's physical group uses
the existing CuTe phase arithmetic, preserving the TMEM pointer alignment proof.

Each32-token SIMT fragment has32 half elements/thread (16registers); each64-
token native fragment has64 half elements/thread (32registers). A protected
interval ofP columns therefore needsP/2 packed registers per thread in either
format. Current public K4/K8 geometries cap FC2's protected interval at128,
requiring at most64 additional packed registers. FC2 has256 threads with
one-CTA launch bounds and **no** setmaxnreg donation policy; the256-register
epilogue donation belongs to gathered FC1 only. Actual compiled register/local
resource checks are required before launch; this arithmetic is not a spill-free
claim. No new tactic, model/dtype gate, scratch allocation, or public argument.

References inspected locally: CUTLASS `sm100_epilogue_tma_warpspecialized.hpp`
lines729–738 and880–888 protect the read/release boundary; Rubin's
`block_scaled_swap_ab_fc12_epilogue.py` separates BF16 register values from its
store callback. Neither supplies this multi-slab snapshot directly.

Qualification must cover both phases,192/224-row tails, both shared staging
layouts, one/two CTA, nongated/SiTU/GeGLU, per-token and MX formats, including
actual CUBIN register/spill guards. The next bounded CAAC must retain all prior
negative cases and N3U TP per-token. No GPU run has started for this design.
