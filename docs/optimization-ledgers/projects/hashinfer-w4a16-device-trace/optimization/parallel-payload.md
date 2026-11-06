# Candidate A: epilogue-WG payload staging parallel with dispatch preparation

Source-only candidate prepared on 2026-09-25. Worktree: [parallel_payload](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel_payload). Base is `002ef1454cbacde09972ed5e2ec7dcfe37e55749` plus the existing store16 change. The primary checkout and historical repositories are unchanged.

Artifacts: [complete patch against 002ef145, including store16](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel-payload.patch), [source audit](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel-payload-source-audit.json), [history audit](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/dispatch-history.md).

## Mechanism and intended window

Original: dispatch warps 8–11 copy BF16 activations, stage routing IDs/weights, run routing preparation, then enter the existing grid/count/NVLink publication. Epilogue warps 0–3 wait for their first scheduled work.

Candidate: epilogue warps 0–3 perform the same BF16 copy while dispatch warps 8–11 stage routing IDs/weights and perform the original routing preparation. Epilogue threads arrive on named barrier 11 after copying and each writer's existing async-global proxy fence. Dispatch threads arrive-and-wait on that barrier after inherited `dispatch_prep`, before the unchanged first grid synchronization in `dispatch_barrier`.

This overlaps source payload copy with **local routing preparation**. It does not make count-dependent work runnable during a still-pending cross-rank count exchange. Its possible benefit is to shorten the path to that exchange and/or reduce rank arrival skew. Current trace/timing must establish whether that helps the actual exposed window.

## Synchronization argument

1. `stage_payload` is the original BF16 staging body, with only the warp-group origin changed from `warp - 8` to `warp`. It still assigns the same flat 16-byte chunks to 128 threads per CTA, with the same CTA linear ID, total-CTA stride, vector/alignment condition and strided-source fallback.
2. `stage_routes` keeps routing IDs and weights on their original dispatch owners. Their staged-ID stores are consumed by the same lane in inherited preparation. Capacity-tail IDs are still set to `-1`; no new inter-CTA dependency is introduced for routing preparation.
3. Every actual BF16 writer retains its `fence_proxy("async.global")` before epilogue arrival. All 128 epilogue threads arrive, including threads that had no chunk to copy. All 128 dispatch threads execute one matching arrive-and-wait after preparation. The barrier expects 256 threads.
4. All CTAs therefore finish their local payload copies before their dispatch group enters the existing grid publication. Existing grid and NVLink publication still cover source payload, routing metadata and expert counts before any remote pull. There is no new source-ready flag, no extra NVLink publication, and no change to the bank/epoch protocol.
5. Epilogue arrival is nonblocking; dispatch is the waiting side. Epilogue then continues to its original register increase and scheduler consumer. Neither side needs scheduler publication, MMA, or FC1 output to complete the new handoff. The existing scheduler release remains after count publication.
6. The new arrival is outside the `staging_inputs is not None` branch, and the dispatch override always waits. Thus prestaged variants also participate; no live-work or valid-expert condition controls participation. An empty live input executes no payload copy but still participates. Existing inactive-capacity routing handling is unchanged.

Named barrier inventory in this source: ID1 epilogue wait, ID2 TMEM retrieval, ID8 kernel tail, ID9 dispatch-to-scheduler, ID10 dispatch-local/grid synchronization. ID11 is unused before this candidate. The new handoff does not change TMEM retrieval's 416-thread membership or common pipeline-init participation. Named barrier 11 is used once per CTA launch; no iterative phase state or shared allocation is added.

The owned `dispatch_wait_input_payload` subrange labels the NB11 wait on all four dispatch warps, outside the inherited per-token loops. On CTA0/warp8 it nests inside `dispatch_count_routes_send_ids`, so the new wait can be distinguished from actual routing preparation. No instrumentation was added to divergent token-level control flow.

The ordering above is a source-level argument. GPU compilation, generated barrier placement and runtime correctness remain to be verified; Python AST equality does not prove native memory ordering.

## Register and runtime costs

- Epilogue staging runs after its existing TMEM allocation/retrieval wait, at its initial 96-register allocation, **before** `setmaxregister_increase(144)`. Dispatch retains `setmaxregister_decrease(64)` and the control group retains 80; the original 144/80/64/96/96 register redistribution remains unchanged.
- The original payload body ran in the 64-register dispatch group; it now runs in the 96-register epilogue group. Native SASS must verify the copy's placement and whether compiler liveness/spills or register-allocation scheduling add costs. The declaration alone does not establish those properties.
- One additional CTA-local 256-thread handoff is paid even for prestaged variants. There are no new global atomics, cross-rank collectives, shared-memory buffers, CTA/cluster counts, or payload bytes.
- Dispatch can finish preparation first and wait for a slower TMEM-started copy; conversely, an early payload producer can finish while dispatch remains active. This may replace some existing copy/TMEM overlap with copy/routing overlap. Benefit is not assured.
- Store16 is deliberately stacked underneath A. Compare A with the existing store16 source for incremental attribution; comparing only with 002ef145 would mix changes.

## Previous attempts and validation boundary

The closest prior HashInfer trial, `772de58a`, used **two decoder WGs** to copy BF16 while dispatch prepared routing, then joined before publication. It was rejected at 0.999078× over historical T8–8192 against `7dc`. `b215a7d2` used three copy WGs and a 544-thread TMEM retrieval handoff and was rejected at 0.995738×. No exact epilogue-WG0/NB11 variant was found in the bounded historical audit. These results motivate a small isolated trial rather than a performance claim.

Completed local checks: Python syntax compilation; `git diff --check`; AST equality of the payload body after substituting the warp-group origin; exact AST equality of the routing body; one inherited preparation call; marker labels at most 32 characters. Only two owned W4A16 files differ, including store16. No GPU compilation, numerical run, sanitizer, generated-code audit, timing, or promotion is claimed.

For native validation, inspect (a) payload-copy instructions and writer fences before the epilogue arrival, (b) dispatch preparation before NB11 wait and the original first grid sync after it, (c) the register-increase position and stack/local resources, and (d) all fused/prestaged and zero-live-row participation. Then use the current workload's matched uninstrumented full-forward measurements and trace whether preparation/publication/first-MMA boundaries actually advance.
