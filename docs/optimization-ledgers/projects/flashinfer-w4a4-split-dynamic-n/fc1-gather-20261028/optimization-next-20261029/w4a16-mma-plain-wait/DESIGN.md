# W4 MMA plain A wait

Independent unstaged candidate based on retained e780f02c. Replace the MMA warp's cached `peek_trans2mma_full_status` with `trans2mma_pipeline.consumer_wait(state)`. Preserve the DQ raw-load and decoded-slot peeks: those overlap useful decode/store work. Preserve every barrier, arrival, release, state advance, allocation/free, stage, quota, tactic and API. Applies uniformly to FC1/FC2, static/CLC, full/partial K, and one/two CTA. No new condition.

## Evidence and mechanism

Retained N128 two-CTA SASS in `w4a16-batched-route-ids/evidence/resources-control/172339-000.sass` (kernel source b8f124f1) has next-A `TRYWAIT` at0x2480 immediately after both UTCBAR releases at0x2460/2470. Only phase bookkeeping/loop branch follows, before the cached-token branch at0x1f80. No independent MMA/TMA issue overlaps this read. On false, a second poll appears at0x1fa0. The cached form also carries a last-K predicate and separate counter. Initial A peek at0x1ea0 precedes accumulator acquire, but it has no reservation side effect and merely saves a future barrier read when already ready.

The prior iKET A/B readiness observations support scrutinizing issue overhead, not weakening synchronization. Its markers were sampled from374, before the retained6c static Gather4 loop interchange: A-ready87.6/240.5ns, B-ready194.6/174.6ns for K3EP4K/8K. These program-ordered waits are not independent operand arrival times; traces are not retention timing.

Rubin's `block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1476–1482` explicitly uses plain waits for independent weight/token pipelines, avoiding the doubled readiness-state machinery. Its combined pipeline path does genuine lookahead before S2T/MMA issue; W4's cached A peek is after MMA issue instead. Existing CUTLASS mixed-input examples retain the same inherited W4 peek pattern; this is an optimization hypothesis, not a claimed CUTLASS correctness defect.

## Dependency proof

`PipelineAsyncUmma` inherits `PipelineAsync.consumer_wait` (`references/cutlass/python/CuTeDSL/cutlass/pipeline/sm90.py:280–310`). `consumer_try_wait` only queries the full barrier. `consumer_wait(state, None)` waits on the same stage index and phase; a cached true token previously skipped that query. The candidate performs the actual readiness check immediately before reading A. Both A/B stage releases remain after the complete MMA issue and both state advances remain in place. The initial accumulator acquire remains before the A wait. No producer can overwrite A before its unchanged consumer release.

Codegen gate: pair N16/N128/N192 on GPU3, verify fewer poll/control sites and no new local spills. Then33 existing exact cases, including FC2. Only after that propose a fresh bounded CAAC covering all four models EP/TP; never reuse rejected batching timings. No sanitizer or clock changes.

Trace interpretation: a future `mma_a_ready` range now contains the actual direct readiness poll. The old cached poll occurred near the previous iteration end, outside that range. Compare full stage/chain timing rather than treating any isolated A-ready range change as altered operand-arrival latency. Existing marker placement itself is unchanged.
