# Proposed W4A16 shared-output wait placement

`w4-late-store-acquire.patch` is applied as the source04 experiment on top of verified full-gate-03. Only `moe_w4a16_kernel.py` differs; there are no tactic, layout, stage-count or compile-key changes. AST parsing, diffcheck and scoped pre-commit passed; 10 focused existing W4 tests and four paired fused-finalize cases passed; broader graph/performance gates remain pending. Base/new source hashes and patch hash are in `source04-local-overlay.json`; the original proposal hashes remain in `w4-late-store-acquire.json`.

Current W4A16 TMA epilogues commit a store, immediately wait until at most `num_c_stage - 1` groups remain, then block all epilogue warps at a named barrier. This establishes safety for a later shared-stage overwrite early: the next tile's TMEM loads and register work cannot start until that barrier completes. CUTLASS `TmaStoreFence.wait` implements exactly `cp_async_bulk_wait_group(num_stages - 1, read=True)`.

The proposal moves that existing wait and barrier immediately before the next shared-stage writes. Gated FC1 can load/release the next accumulator and obtain its up/gate register fragments before waiting. Non-gated FC1/FC2 can additionally perform conversion to the output dtype before waiting. The gated activation loop writes shared values as it computes each pair; moving all activation arithmetic ahead of the wait would require a separate register-output pass and is deliberately outside this minimal patch.

Correctness invariants:

- The selected ring slot remains `(num_prev_subtiles + 1) % num_c_stage`. Before its overwrite, the issuing warp's acquire guarantees that the oldest conflicting TMA read has completed; the reuse barrier makes every writer wait for that guarantee.
- The existing async.shared fence and pre-TMA publication barrier remain after the new writes. They cannot share the reuse barrier: the reuse barrier must precede writes, while publication must follow them. There are still two named barriers per emitted store.
- Store issue and commit remain in the same issuing warp. Non-issuing warps may advance toward the next tile while it issues; the next reuse barrier or final epilogue barrier reunites them before any conflicting use.
- Final `producer_tail()` remains unchanged and drains every outstanding shared read before kernel completion. Removing the earlier last-store partial drain does not remove this tail.
- The first acquire is an empty-group wait and does not stall. It is intentionally unconditional, avoiding a new first-iteration branch, counter, peeled loop or tactic. Total acquire count remains one per store; the empty first acquire replaces the old partial acquire after the last store. Splitting acquire from commit repeats the existing issuing-warp guard at its new location; it does not add a first-iteration or shape policy.
- For one stage, acquire is wait-group0 and protects that single slot; for multiple stages, it permits the existing number of in-flight groups. The current unfused W4 policy allocates at least two C stages. Fused FC2 uses its separate reduction path and is untouched.

The proposal is general across activation types, old/swap weight layouts, static/CLC, and one/two-CTA execution. It is not a claim of a speedup. Before retaining it, complete the source-bound descriptor correctness gates, inspect register/spill changes, and compare representative small TP and EP shapes after the full-gate-03 outlier has a stable paired baseline.
