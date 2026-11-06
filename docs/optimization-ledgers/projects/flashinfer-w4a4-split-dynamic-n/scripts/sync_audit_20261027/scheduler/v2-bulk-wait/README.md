# Delay the bulk-store reuse wait to the overwrite boundary

Independent candidate at `9334cb34fe9c81653dc4748632f44449e9aecd8d`. V1 terminal-barrier removal is **not composed**. The immutable V1 patch/receipt and deployed source remain available; the same active local scheduler clone now contains only this V2 edit to `blackwell/utils.py`.

The bulk epilogue previously waited for the next shared stage at the beginning of a slab, before loading its accumulator from TMEM and applying scaling/conversion. Those operations only touch TMEM and registers. V2 moves the existing bulk-read completion wait and128-thread reuse join immediately before the first `stmatrix` write into that shared stage. There is no new state, tuning choice, specialization or participant change.

## Ordering proof

1. The current slab's TMEM accumulator address and packed registers do not alias the shared buffer used by the prior bulk copy. Merely constructing the shared tensor view does not read or write storage.
2. TMEM loads, scaling, conversion, register recasting and warp shuffles produce the same register values as before. They can execute while the earlier shared-to-global copy continues reading its old stage.
3. Immediately before any `_bulk_stmatrix4` write, the exact same `cp_async_bulk_wait_group(stages - 1, read=True)` still completes the relevant prior reads for each issuer. The same named barrier6 joins all128 epilogue threads before any writer can overwrite any issuer's shared source.
4. Current-stage shared stores, async-proxy fence, publication barrier, row copies and commit-group are unchanged. The terminal wait0/read and128-thread join are unchanged. Group count, group order and stage parity are identical.
5. The condition `group * tokens < valid_tokens` is unchanged and CTA-uniform. `step >= stages` is the same compile-time condition; padding and reverse traversal do not add/remove a wait or group. Skipped slabs execute the original overlap release rule outside this conditional.
6. The protected64-column early accumulator release still follows both protected TMEM loads and their completion fence. Moving the unrelated shared-stage reuse wait later allows that release to occur sooner, but does not move it ahead of a protected read. Later MMA reuse affects only the protected TMEM region already copied to registers. It cannot alter the previous slab's SMEM or the current slab's packed registers.

## Resources and coverage

The packed output values now remain live across the shared reuse wait/barrier. This can increase register pressure or affect compiler scheduling; codegen/resource evidence is required before a performance claim. Allocation size, bulk slab size/stages and MMA geometry are unchanged.

The changed block compiles only when a tile revisits a bulk stage. With the preferred64-token/two-stage scratch, this requires a wide tile such asN256. The32-token/one-stage fallback reuses its stage sooner. Existing fixed gate config1 covers N256/twoCTA/overlap; emitted code must verify the reuse-wait path is present. Add a bounded fallback case only if the existing gate never generates32/one-stage reuse. Both normal and reverse overlap directions, PDL on/off, per-token and uniform scaling, live and padded rows retain the original algebra. FC1 paths without bulk stores should remain unchanged.

## Validation

Python AST, exact single-block motion check, `git diff --check` and scoped pre-commit pass. Source receipt records the original freeze and hashes. Independent source review and GPU gates subsequently passed: 88 main and 16 bounded extra exact replays per source, with unchanged instruction/register counts and no spills. [The codegen audit](codegen-audit.md) distinguishes the moved 128-thread join from the per-issuer wait that ptxas still schedules early. V1's evidence must not be attributed to this separate source. The completed scheduler clone was released for cleanup; its patch, source and receipts remain here.
