# Retained pipeline synchronization audit

Read-only audit of production `aab93f854054de834447bdd8985b8bbd653fb3c8`, 2026-10-25. Source hashes are in [ownership_receipt.json](ownership_receipt.json). No production changes or GPU work occurred during this audit. The target remains **one resident CTA per SM**. [Register/role review](REGISTER_ROLES.md) covers resource policy separately.

## Current ownership and cardinality

Source links use the retained [core](../../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py) and [custom pipeline](../../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/custom_pipeline.py); paths are relative to the project root in the line references below.

| Object | Participants and purpose | Release / tail |
|---|---|---|
| `a_pipe` full, core908–923 | One elected leader TMA arrival; expected bytes cover A/SFA/B and, at routeN>=128, SFB. Group2 includes both CTAs' transfer bytes. MMA leader waits before SF copy/MMA. | TMA transaction completion satisfies full; producer commit is intentionally a no-op. |
| `a_pipe` empty | One TCGEN completion per stage, multicast to both CTAs for group2. Warp0 waits before overwrite. | Leader issues release after both NB2 MMAs, core1508; warp0 drains all stage empties,1238. |
| `ab` full,925–934 | For routeN<128, all128 producer threads submit `cp.async.mbarrier.arrive.noinc` after their SF copies. The full barrier is CTA-local, expected128. Zero-filled/invalid rows still participate. | MMA warp in each CTA waits,1398, then publishes generic-SMEM visibility through the retained async.shared proxy fence. |
| `ab` empty | SF SMEM is retained until the same MMA completion as payload. One leader TCGEN commit releases local/peer empties. | Core1507; all128 producer threads currently drain their cloned tail,1236. |
| `relay`,937–944 | Group2 + non-TMA SFB only:64 MMA-role threads total publish both CTA-local SF completions after proxy fences. Leader waits before S2T/MMA. | One group2 TCGEN completion,1512; both MMA warps tail-drain,1521. Absent from oneCTA. |
| `acc_pipe` full,945–953 | Leader UMMA producer commits after the final K tile; each epilogue warp waits before TMEM reads. Two accumulator stages on eligible narrow overlap path. | Producer tail waits for the last consumed stage,1523/custom_pipeline394–404. |
| `acc_pipe` empty |128 epilogue threads per CTA,256 for group2, arrive after TMEM reads. Overlapping accumulator windows may release at a proven earlier boundary inside epilogue. | Normal release at1229–1230/1321–1323 after load completion. Must not release a reused TMEM scratch rectangle before its final read. |
| Named barrier3 | All160/288 threads retrieve the allocated TMEM pointer. Barrier initialization fences precede it. | Startup only; also establishes the common rendezvous before role divergence. |
| Named barrier6 |128 epilogue threads join SF32 maxima across adjacent warps and protect shared scratch reuse. Also used by bulk FC2 staging. | Keep both exchanges where applicable; no SF16 dependency. |
| Named barrier1 | All160/288 threads join after producer/consumer tails and output work. | Prevents any role using TMEM/barrier storage after cleanup begins. |
| Named barrier2 |128 threads in warps0–3 after allocation-permit release, before TMEM free. | Keep collective allocation/free protocol; barrier1 occurs before permit release and is not a substitute. |

The copied helper `pipeline_init_wait` is named like a rendezvous but only issues `mbarrier_init_fence` (custom_pipeline70–80). Do not infer an extra CTA barrier from its name. The common allocator rendezvous and group2 cluster rendezvous provide the startup coordination. Storage reserves unused AB/relay entries even when those pipelines compile out; this is a small static footprint, not executed synchronization.

The persistent schedule is static cyclic `for tile in range(block,total_tiles,grid)` in each role (core1013/1243/1374), with identical task/K counts and state order. There is no CLC instruction in retained production. Grid is capped by existing active-cluster/SM count and launch specifies `min_blocks_per_mp=1` at848. No extra residency target is hidden in this launch.

## Proven small redundancy

`utils.py:1104` ends `epilogue.run` with `fence_view_async_tmem_load`; normal callers immediately repeat it at core1229 and1321. Matching98fd control PTX has adjacent `tcgen05.wait::ld.sync.aligned` at lines966–967. The retained utils hash is exactly the98fd hash. A single completion wait dominating accumulator release/free suffices when there is no intervening TMEM load. This is a source/PTX redundancy, not a measured performance claim. Overlap paths must retain whichever wait follows their final actual load; do not remove all caller fences indiscriminately.

The newly retained SF proxy fence at core1401 is **not** redundant: it orders completed generic-proxy cp.async writes before async-proxy TCGEN scale reads. Neither accumulator-load completion nor a TMA transaction wait replaces it.

The first `a_pipe` initialization fence could be deferred to the final `acc_pipe` initialization fence: all barriers are created before either the explicitgroup2 cluster rendezvous or allocator retrieval, and no producer/consumer accesses them between constructors. A default-false optional defer flag must preserve other callers and group2 ordering. This saves one startup fence, **not** an additional CTA barrier; it is excluded from the initial merged-ring candidate. Also, core1181–1184 retains an empty `producer_gather4_issue` iKET push/pop after regularTMA replacedGather4. That marker should be removed or renamed to actual work in a separate instrumentation cleanup; empty-marker duration is not evidence of Gather4 work.

## Bounded substantive candidate: one mixed full/empty operand ring

For oneCTA, routeN<128, dedicated epilogue only, combine payload/SF readiness and their already-common post-MMA lifetime. Preserve288 threads. Reuse the frozen distributed producer roles: warp0 A, warp1 SFA, warp2 B; all128 producer threads retain SFB cp.async. Initialize each full barrier to **131 arrivals =128 cp.async completions +3 elected TMA arrivals**. Each TMA issuer atomically arrives and announces only its own bytes before its own transfer. Every producer thread commits its own prior cp.async operations with `.noinc` to that same barrier. All producers independently wait the same empty phase before writing. MMA waits one full barrier, executes the retained proxy fence, copies SF, issues MMA, and commits one empty completion. Warp0 alone drains all empty stages; the final whole-CTA rendezvous still joins all roles.

Happens-before argument: the phase cannot finish before an unannounced issuer because that issuer still owns a pending arrival. An announced transfer contributes pending bytes until completed. The128 SF arrivals cannot complete before their own preceding copies. Thus full completion requires all SF copies and all three TMA transfers. After that wait+proxy fence, S2T/MMA consume exactly those bytes. The single empty TCGEN commit follows all such reads, and only then permits overwrite. Shared pipeline state advances once perK across persistent tiles; tail draining covers every most-recent stage phase without announcing unused transactions.

[CPU count model](ownership_receipt.json) checks3,483 progress states, including SF completion before any TMA announcement and arbitrary issuer completion order. This is not a hardware or compiler proof. Installed4.7.1 constructor/count/arrival excerpts and hashes are preserved in [the distributed-TMA receipt](../producer_roles_experiment/distributed_tma/receipt.json). They confirm group-derived arrival count and internally elected `arrive_and_expect_tx`. The retained control PTX confirms `.noinc` on all SF producers. Before launch, newly emitted code must show exactly131 initialization, three elected arrivals with separate byte counts,128 SF arrivals, one full wait and one post-MMA empty commit per stage, and a wait-only tail.

The proposal is deliberately excluded from group2: CTA-local cp.async completion cannot simply be folded into the leader's TMA barrier. TMA-SFB N>=128 already has one full/empty operand ring and gains nothing here. Inline epilogue/mixed FC1 remains unchanged. No new TMEM stage, producer warp, register cap, standalone transform, or public layout change is required.

Official references: [cp.async arrive-on/noinc semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive) and [mbarrier completion phases](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier). These define arrival/transaction ordering; they do not predict performance.

## Closed axes and compile budget

- [Single completion](../single_completion_experiment/README.md) removed duplicate **empty** wait/release/tail but kept both full waits; it was sub-percent on7829. The mixed full+empty design above is different.
- [Producer roles](../producer_roles_experiment/README.md) tried extra warps/separate payload rings and then three elected TMA issuers with SF still separate. Those results remain closed and unretained; this candidate specifically removes the remaining duplicated full/empty ring.
- Independent SF publication, early source release, five stages, compact producer roles and paired-row copies were already screened. No replay of those axes is implied.
- [Register reallocation](../register_budget_experiment/README.md) was exact but neutral/slower, and invalid policies hung because the CTA allocation pool was smaller than physical64K. Current64-register/no-spill N16 code has no demonstrated spill problem. Do not add a register sweep or occupancy experiment.

Recommended compile budget: one new131-count source candidate, one narrow NVFP4 N16 exact specialization first, source/codegen review, then bounded T32/T128 adjacent controls. Broaden only after a useful result. The epilogue layout experiment is separate so compiler failures or timing changes stay attributable.
