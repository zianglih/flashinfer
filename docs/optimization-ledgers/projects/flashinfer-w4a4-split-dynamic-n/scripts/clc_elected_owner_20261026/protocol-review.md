# Independent elected-owner CLC protocol review

**Disposition: no blocking source issue; approve the focused source-paired exact and codegen gate.** This is a source review, not a claim of runtime correctness or speedup. No candidate source was edited and no GPU work was launched by this reviewer.

Reviewed frozen base `9b4721b08057d0a488c1f0236467acb75c48cd00`, device-only patch `5da2bd3f6217a3b72d17fedadaf61214279e632c6f84135657070fbe1ccb2c5e`, in `flashinfer-clc-elected-owner-20261026`. The separate shared-FC1/FC2-flag benchmark is unchanged.

Sources: the CUTLASS/FlashMLA reports and exact SDK4.7.1 snapshots in `../clc_reference_audit_20261026/`; plus the exact installed4.7.1 helper bodies captured here in `sdk-sync-source.json` and `sdk-*.py`. The supplementary capture imported source objects only and verified CUDA was not initialized. It covers `MbarrierArray`, `PipelineState`, `make_pipeline_state`, `CooperativeGroup`, the sync-object constructor, raw arrive/wait operations and `if_generate`.

In the references below, **K** means the candidate `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`; **P** means its `blackwell/custom_pipeline.py`.

## Counts and ownership

| Barrier | One CTA | Two CTAs | Evidence |
|---|---|---|---|
| Local CLC full | One elected owner arrives and adds16expected bytes; hardware completes16bytes | Same independently in each CTA | P87–112; exact `sdk-mbarrier_arrive_and_expect_tx.py`: one executing thread decrements pending arrivals by1 and adds16tx bytes |
| CTA0 CLC empty | One owner releases per response | Exactly two owners release per response, each to CTA0 | P90/101; SDK `PipelineAsync.consumer_release` directly invokes `MbarrierArray.arrive` with `consumer_mask=0` |
| Local metadata full | One owner writes and commits each published item | One per CTA; no cross-CTA metadata handoff | K1401–1408,2133–2139 |
| Local metadata empty | Existing160 or288worker threads | Same local worker count in each CTA | K1405–1406; `next_work` K1243–1248 is unchanged |

The helper reuses SDK construction but deliberately does **not** reuse its lane-distributed `producer_acquire`. The original SDK expects CTA0 lanes0…cluster_size−1 to arm remote full barriers; that would be wrong inside a single elected lane. The override instead has each CTA owner arm its own local full barrier. Only CTA0 waits for the shared empty barrier and issues the multicast query. `cute.size(cluster_layout)` equals the launched CTA group size, so the empty count is1 or2, not32 or64. The peer's allocated empty barrier is unused, as in the original topology; it is never waited on.

Initialization still executes before role election. SDK `MbarrierArray.mbarrier_init` uses warp0/election there, outside the elected loop. The existing initialization fence,2CTA cluster rendezvous, and all-thread TMEM allocation rendezvous remain at K1426–1440. There is no new path from the elected owner to an uninitialized barrier.

## Phase and response-reuse proof

`make_pipeline_state(ProducerConsumer,1)` starts at index0/phase1; the consumer starts index0/phase0. `PipelineState.advance` flips phase on each one-slot wrap. For query q, both owners advance producer state once and consumer state once; the peer producer phase is harmless bookkeeping because only CTA0 waits for empty. The first empty wait passes on the initialized empty phase. Later CTA0 waits cannot pass until every owner has consumed and released the previous response.

A valid current work item causes exactly one query. Both owners publish the full expectation, wait for the multicast response, decode it, and release CTA0's empty barrier. A peer can reach its local expectation before or after the asynchronous response completion. This is permitted: the pending software arrival prevents early full-phase completion, and the transaction counter can temporarily be negative before expectation is added. NVIDIA's [mbarrier count and phase specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier) permits negative transaction counts and requires both pending arrivals and transaction count to reach zero. The captured FlashMLA owner loop uses the same local-expectation pattern.

Every owner calls `sched.get_current_work()` before releasing empty. Exact SDK4.7.1 `work_tile_info_from_clc_response` retains its `fence.proxy.async.shared::cta` after the generic128-bit response load. Thus the next hardware write cannot reuse the response slot before both local readers have fenced and acknowledged it. The candidate retains the SDK's existing remote-empty-arrival scope/encoding; this review does not claim to strengthen that inherited contract or substitute the newer CUTLASS source for4.7.1.

## Single-lane call-graph audit

- The outer `elect_one` at K2092 is entered by the full scheduler warp. Election identity stays within this region for the complete state machine. No loop state escapes to the non-elected lanes.
- Raw `cute.arch.issue_clc_query` is used at K2114. It contains no election or warp collective. The old `sched.advance_to_next_work` would contain a nested election and is correctly bypassed. Its other effect was incrementing a diagnostic tile counter; this kernel never reads that counter, and response decoding does not depend on it.
- `PipelineAsync` acquire, commit, consumer wait/release, get-barrier and producer-tail dispatch to per-thread `MbarrierArray` methods. The actual metadata op is `AsyncThread`; it does not invoke the `TCGen05Mma` elected-arrival branch. Full expectation directly calls the raw arch operation, avoiding `MbarrierArray.arrive_and_expect_tx`'s internal election.
- `MbarrierArray.wait` lowers to a scalar mbarrier parity retry operation. `if_generate` constructs an ordinary conditional. State construction/advance and response coordinate arithmetic contain no ballot, shuffle, warp sync, CTA barrier, or hidden election.
- `get_current_work` performs a local response load, query extraction, fence, and coordinate mapping. The mapping parameters are unchanged. Both CTAs derive the same route and logical tile after the existing CTA-group division, retaining startup-prefetch agreement.
- Scheduler-item IKET push/pop remain paired inside the same elected region for every iteration, including invalid termination. Normal builds omit them. An instrumented build should still be checked if the focused gate includes IKET; ordinary exact/codegen success is not evidence about instrumentation lowering.

## Queue order, terminal state and PDL

The original metadata acquire still precedes cancellation (K2109–2117). Valid padded routes issue/consume a query without publishing a worker item; they do not advance the metadata state. Routed work publishes exactly one item. Invalid work acquires a metadata slot, publishes the `tile=-1` sentinel, issues no new query, and exits. Thus this patch does not reintroduce the rejected request-overlap or deeper-queue behavior.

CTA0 retains `clc_pipe.producer_tail` at K2150–2151 after the last query's producer advance. Its inherited implementation directly waits the empty phase, draining the peer's last remote acknowledgement before CTA0 can exit. No local metadata-tail wait was reintroduced; the final all-thread CTA join at K2154–2156 still drains terminal consumers. Existing TMEM teardown and2CTA deallocation synchronization remain unchanged.

The startup payload wait remains role-dependent at K1520–1532. Only the already-authorized scheduler path can bypass it. The delayed `griddepcontrol_wait` is **outside** the elected region at K2152–2153, so all32scheduler lanes execute it after reconvergence. Startup dependent signaling and routing release are unchanged. PDL-off/static paths retain their existing behavior.

## Focused gate boundary

Proceed with the planned1-/2CTA source-paired exact replay and actual PTX/SASS/resource gate. It should cover routed, empty, padded, persistent and reactivated routes; PDL on/off; both FC phases; and enough work to reuse each response/metadata phase. In codegen, verify one outer owner election, one local full expectation perCTA/query, one empty release perCTA/query, CTA0-only query/tail, and preserved proxy fence. Check for spills and register growth. No wider timing or retention approval follows from this source review alone.
