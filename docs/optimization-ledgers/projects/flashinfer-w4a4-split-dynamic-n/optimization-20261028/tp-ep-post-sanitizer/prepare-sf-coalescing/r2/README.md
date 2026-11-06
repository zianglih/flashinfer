# R2: unified row and scale ownership

Source: `840b116adba50f4418c591475ffed0fbe3c9701c55ed526b1781844e5ad61ba0`.
Base: pushed `d1767be1f42fdc371f90db4fb06598299ea32845`.
Review copy: project-local `flashinfer-prepare-sf-review`, unstaged.

Scaled prepare uses 128 threads as 32 rows × 4 lanes. Each lane retains a
256-bit payload copy. The payload loop has a static bound, but `unroll_full=False`
only removes a forced hint: generated code still fully unrolls its 28/56
iterations on the workload widths. This increases registers and static code.
The original SF preload/store surrounds that payload loop, so each routed row
performs one metadata traversal. No scratch, new barrier, extra kernel, model
switch, or tactic is introduced.

Rows are permuted within each at-most-128-row SF atom:

```
atom_rows = min(route_tile, 128)
row_groups = ceil(atom_rows / 32)
local = ordinal % route_tile
row = ordinal // route_tile * route_tile
    + local // atom_rows * atom_rows
    + local % row_groups * 32
    + (local % atom_rows) // row_groups
```

For the supported MMA route tiles 16/32/64/128/256, this is a permutation of
precisely the logical routed rows, with no physical-padding holes admitted as
logical rows. The final partial CTA is masked before reading limits/mappings.
Each row's four lanes retain source/payload/SF ownership and invalid-row rules.
Adjacent four-row groups and adjacent SF blocks now share output sectors;
input SF groups remain contiguous 16-byte segments per row. This avoids R1's
fully strided scalar scale loads and second global traversal.

Unscaled W4A16 retains one row per CTA and its original 256-thread ownership.
The byte gate confirmed all 30 unscaled SASS variants are identical to control.

Qualification completed: 480 exact graph replays per source, 80 generated
kernels per source, route tiles 16/32/64/128/256, PDL on/off, empty/partial/full
and reactivated graphs, invalid mapping poison, invalid payload canaries,
invalid logical SF zeros, unused physical padding canaries, and untouched tail
storage. Full source/codegen receipts are in `gate-evidence/`.

The completed retention screen rejected R2 as-is: K3 MXFP4x8 and V3 W4A4 in both EP and TP, tokens
4/64/16384, matched CAAC, fixed existing public winners, 10 warmups and 100
CUPTI samples with cold L2. This first screen decides whether broader format
and shape qualification is justified. No W4A16 benchmark is needed because
its generated instructions are unchanged.

The complete table is `perf-table.md`; all 4,800 raw samples, route/source/cache
identity, CUPTI counts and medians were verified in `perf-summary.json`.
TP prefill improved 1.29% (K3 MXFP4x8) / 2.56% (V3 W4A4), but all decode
cells regressed 2.74–24.86%. K3 EP prefill control passes differed 3.4%, so
its small aggregate regression is not isolated. No R2 retention.

Source review identified an ownership-completion error: the host grid still
used the old one-row-per-CTA capacity bound. R3 corrects this with
ceil(capacity/rows_per_cta) and explicitly prevents payload loop unrolling;
both derive from the new ownership instead of model or token heuristics.
