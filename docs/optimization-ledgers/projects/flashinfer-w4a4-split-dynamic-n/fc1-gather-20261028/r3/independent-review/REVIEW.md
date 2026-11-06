# R3 independent source review

Frozen kernel: `c259b6cb4b01037def6f1b8d4be09221f7abc36dd76e910660ced0179daebf75`, base `d35fcfda03875077b3af8455575cc1d20e866a8c`. No production edits or GPU commands were used.

## FC2 and role specialization

The new nested `const_expr` guards avoid tracing unavailable FC1/FC2 operands in the opposite specialization. Under `gather_input=False` and the unchanged 256-thread FC2 launch (warp IDs 0 through 7), `kernel()` and `load_weight_stage()` reduce exactly to the retained AST. The additional `warp >= 8` branch is unreachable for FC2. This proof does not claim PTX or SASS identity; compiler qualification remains necessary.

The FC1 metadata quorum remains weight 32 + gather 128 + epilogue 128 + leader MMA 32, yielding 320 leader / 288 follower arrivals. Warp 1 only publishes the startup PDL signal. All 384 threads still participate in TMEM retrieval and final rendezvous. SF completion/reuse and regular FC2 paths are unchanged by the R2-to-R3 task flattening.

## Flattened task mapping

The independent checker extracts the actual task expressions from the frozen kernel. It passes 40 admitted geometry combinations, 4,008 live-row states (including empty routing), and 3,348 issued shared-memory interval checks.

- Admitted row-group counts are 2 or multiples of 4. Thus the cached-coordinate slot selected by task-group modulo cache length exactly describes that task's row group.
- All row-group/K-chunk pairs are issued once; byte intervals do not overlap and remain inside their physical stage. Payload byte counts are unchanged.
- Four warps issue whenever at least four tasks exist. N16/two-CTA/Ksteps4 has only two tasks; N16/two-CTA/Ksteps8 has four. No extra transfers are introduced just to activate every warp.
- For a narrow dynamic-N tail in a larger nominal tile, a CTA can load valid rows outside its effective MMA partition. Those extra rows are unconsumed, as in the retained regular-TMA path. Only the runtime MMA partition is used to prove disjoint live-row consumption across CTAs; the checker does not incorrectly demand that all physical loads be globally unique.
- SF completion, fence, ready arrival and ring advance remain once per stage, outside the payload task loop.

## Register and issue pressure

Source-level state sizes are unchanged from R2: per-thread row-ID cache sizes are 4/8/16/32/64 Int32 values for one-CTA N16/32/64/128/256, and 4/4/8/16/32 for two CTA. SF row offsets need one or two Int64 values. This is a potential liveness cost at large N, especially in the new 384-thread launch, but it is not a measured register or spill result. R3 adds no coordinate-cache dimension.

All task divisors/moduli are compile-time powers of two. `first` is a compile-time cache index, so it should not introduce dynamic register-array indexing. Conversely, `k_chunk` now includes a warp-derived value instead of always coming directly from a constexpr loop; whether the compiler removes the redundant division for larger row-group counts needs inspection of emitted code. No claim of fewer instructions or zero spills is supported by this source review alone.

## SF completion relay boundary

The current gather lanes issue SF copies, commit them, issue payload Gather4 transfers, then wait for their own SF group before fence/arrival. The payload transfer can already overlap this SF wait. A relay is useful only if that wait actually delays issuing later free stages.

Warp 1 cannot wait for other threads' cp.async groups. The existing CUTLASS `cp_async_mbarrier_arrive_noinc` helper instead tracks each issuing thread's copies into a CTA-local barrier (`references/cutlass/python/CuTeDSL/cutlass/cute/arch/mbar.py:466`). A future relay would need all 128 producer threads to publish local asynchronous completion, then a warp-1 acquire/fence followed by the leader-ready publication. Two-CTA publication must remain cluster-scoped. This adds a local barrier ring and a relay role which must traverse exactly the same tile/stage stream, including CLC termination; its metadata quorum, stage count, memory budget and exit/reuse proof must be updated. Merely moving the existing wait/fence/arrival to warp 1 would be incorrect.

Recommendation: keep R3 fixed through the current correctness/performance gate. Do not add a relay solely because warp 1 is idle. Inspect actual SF wait/issue overlap and register resources if the result indicates a remaining producer bottleneck.
