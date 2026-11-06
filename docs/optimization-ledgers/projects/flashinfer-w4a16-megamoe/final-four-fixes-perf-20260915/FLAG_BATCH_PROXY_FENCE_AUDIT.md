# Conditional proxy fence batching audit

**Deferring the two owned global proxy fences to the existing batch `fire()` hook is source-level feasible**, provided the hook runs the fence for all128 epilogue threads before the per-lane address guard. It must cover every threshold, phase-change and final flush. This is lower-priority preparation conditional on a repeatable valid-row regression; no source edit, patch, compilation, new harness or GPU operation was made.

Source: native `a48e5706c2a7775b0b698aa8eccb4e124b02118c`. Owned paths below are under `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`; shared `flag_batch.py` is under `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/`. Source hashes are recorded in `flag-batch-proxy-fence-audit.json`.

## Ordering and participation

Each completed tile currently executes its generic stores, consumes the next work record, then reaches the existing **128-thread** named barrier (`epilogue.py:117–120,149–158`). Only afterward does it accumulate or publish completion (`:160–169`). Current FC1 and dispatch-return FC2 proxy fences are at348 and200. Direct-return FC2 has no such fence/publication.

For any tile i whose counter is published by lane p at a later flush tile k:

`all128 writers' stores for i → existing tile barriers through k → p's proxy fence at fire → p's release increment → existing consumer readiness/async read`.

Every writer has executed its earlier stores before reaching the final barrier, and every thread invokes the same flush hook. This retains the current barrier→proxy-fence→release ordering for each rotating publisher, while its fence covers earlier accumulated stores as well. The readiness counters remain unpublished during accumulation, so delaying the fence does not open an earlier read. There is no new buffer reuse, counter threshold or publication timing change.

PTX distinguishes generic synchronization from the proxy ordering needed for async accesses; `fence.proxy.async.global` supplies that global generic/async ordering. A generic barrier or GPU release increment alone is not a substitute. The proposal keeps the original synchronization/publication path and changes only when the required proxy transition occurs. [PTX9.3 proxy-fence contract](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-membar).

| Path | Existing call behavior that must remain |
|---|---|
| Threshold1 | `accumulate()` calls `fire()` for all128; tid0 alone holds the counter address (`flag_batch.py:53–67`). No fence-count saving. |
| Batched threshold | Uniform count increments; tids0 through count−1 retain distinct pending addresses. All128 enter `fire()` at the uniform threshold (`:69–88`), then the parent method predicates only the reductions (`:111–119`). |
| Phase change | The same uniform branch flushes before resetting state, even below threshold (`:75–88`). FC1→direct FC2 therefore publishes pending FC1 before FC2's `no_fire` applies. |
| Direct-return FC2 | `no_fire=True` suppresses internal fire calls; no proxy fence should be added to every direct-return tile. |
| End of loop | Keep the explicit `flag_tracker.fire()` at owned169 under the same hook. Current scheduler uses phase0 for invalid work, normally flushing/resetting at the preceding phase change; do not rely on that to bypass the final hook. |
| Null/OOB slots | Null addresses suppress reductions only. Do not predicate the all-writer fence on a lane's address. An all-null batch may conservatively issue an unnecessary fence. |

## Smallest owned-code shape and failure examples

Use **one owned subclass** of `GpuReleaseFlagBatchTracker` in the owned epilogue file. Override `_make()` to return that exact owned type, and override `fire()` with an all-thread proxy fence followed by the existing parent fire behavior. Initialize this type at owned123 and remove only the two per-tile fence calls. Leave shared `accumulate()` and its single threshold/phase predicate unchanged. A fire-only override is insufficient: the inherited factory explicitly constructs `GpuReleaseFlagBatchTracker` (`flag_batch.py:96–108`) and would discard the override on the first state transition.

No extra barrier or wrapper hierarchy is needed. An optional **uniform** `cumulated_flags != 0` guard can avoid the final empty fence; it is distinct from, and must not duplicate, the flush decision. The simplest unguarded hook is correct but pays one conservative terminal fence. CuTe handling of the owned factory/parent call and generated all128 participation still require compilation review before any implementation is promoted.

Concrete rejected shortcuts: fencing only when `count == threshold` misses a one-tile FC1 batch followed by a phase change; its counter would publish without the required fence. Fencing after `fire()` lets the consumer observe readiness before proxy ordering. Placing the fence inside the per-lane nonzero-address guard abandons the required128-writer participation and is not this proposal. Omitting `_make()` silently restores unfenced publication after state reconstruction.

## Priority versus earlier placement

The simpler alternative is still moving each existing fence to the end of its owned FC1/dispatch-FC2 store body, before the existing rendezvous. That preserves fence count and needs no tracker specialization; it offers only scheduling overlap. Publication batching changes more structure but can reduce counts: the current four-tactic catalog sets epilogue batches **(2,4)** (`autotune.py:29`), suggesting up to roughly half the FC1 and one quarter of dispatch-FC2 tile fences during long same-phase stretches, before short batches/phase changes/null slots. These are count bounds, not latency predictions.

Prefer earlier placement if a modest scheduling adjustment suffices. Consider the single-hook batching shape only when measured fence cost justifies its added factory/lowering proof. Judge identical tactics and all individual token rows, preserve current correctness gates and raw baselines, and inspect emitted publication/fence control flow before making any performance claim. Independent source review by `gpu_preparation` agreed with the ordering and participation argument; no candidate execution was performed.
