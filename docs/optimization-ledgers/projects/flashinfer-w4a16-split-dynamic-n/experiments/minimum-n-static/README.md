# Optional minimum-N static variant

Prepared from `9ec90d0696752c72ff826c8880e58515ace84e60`. This candidate has **not** been applied, GPU-compiled, or benchmarked. The checkout remains unchanged.

Patch: `../minimum-n-static.patch`.

Changes:

- Compile-time disable dynamic-N issue for one-CTA N8 and two-CTA N16. Positive token counts round to these exact capacities, so the branch cannot sacrifice MMA work reduction. The existing static fallback remains in use; two-CTA N16 also avoids computing the always-zero B-load shift.
- Preserve a compile-time epilogue trip count for capacities fitting one N subtile. Larger capacities retain runtime tail shortening. Empty private tiles still process/release one accumulator subtile.
- No shared helper or MegaMoE changes.

## Static accumulation comparison

The fallback is numerically equivalent to the original static `cute.gemm` sequence, but not source/codegen-identical:

- Original base `316faec`: set `ACCUMULATE=False` once before the routed tile's K256 loop. After each K16 MMA, set it True. Only the first K16 atom initializes the accumulator.
- Current fallback: at entry to each `_issue_mma_tile` K256 call, set `ACCUMULATE=(k_tile_idx != 0)`; after each K16 MMA, set it True. The first K256 call starts False; every later call starts True. The same atom initializes, and all subsequent atoms accumulate.
- The current fallback may retain an extra K-index comparison at each K256 iteration. Whether it does is a generated-code question. This minimal variant does not claim to reproduce the exact baseline lowering.

If exact baseline static issue lowering is required later, put the original `cute.gemm` loop directly in a compile-time static branch of the outer MMA loop, with `ACCUMULATE=False` before that loop. Avoid assuming that mutable `TiledMma.set` state propagates across a nested `@cute.jit` helper boundary without explicit carried values.

## Validation before retention

Preparation checks passed: Python AST compilation, Ruff, format check, and `git apply --check` against the clean `9ec90d0` checkout. No GPU workload was run.

After a decision to try this variant, first run the new low-level grouped tests for M128/N8 and M256/N16 with K512, tails and empty private tiles. Include a gated one-subtile case and a larger-N case to exercise the unchanged dynamic branch. Compare fixed tactics separately from AUTO; preserve R1 results for the original candidate.
