# R4 asynchronous SF relay: independent review

Source `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a`, base d35fcfda. Read-only source review and CPU proofs; no GPU commands or production edits.

**No source-level blocker found.** FC2 kernel/load_weight_stage partially evaluate exactly to the retained AST under gather=False and its unchanged 256-thread domain. Flattened payload coverage and cached coordinates remain correct across 40 geometry combinations, 4,008 live-row states and 3,348 shared byte intervals.

## Completion, phases and reuse

Each of the 128 gather threads enqueues exactly one `cp_async_mbarrier_arrive_noinc` on its local stage barrier after its SF copies. Initialization count 128 therefore matches the asynchronous arrivals; there is no second ordinary arrival or missing arrival for predicated/zero-filled copies. No gather commit_group/wait_group is required for this mbarrier completion mechanism. The official PTX contract says the instruction tracks prior copies issued by that thread and triggers an asynchronous arrival on completion; the noinc count must already be included in initialization. [PTX cp.async.mbarrier.arrive](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive)

Warp 1's consumer state starts at index 0 / phase 0, matching initialized local barrier parity. Its successful local wait acquires SF completion, then the existing async-proxy fence precedes one elected arrival to leader SF-ready. One CTA uses a local arrival; two CTA use an explicit cluster-scoped release to CTA 0. Leader-ready count 1/2 matches exactly those elected arrivals. Only leader MMA consumes it.

All stage states persist across tile boundaries. Existing operand-empty wait prevents a gather warp from reusing slot S until MMA has consumed the previous generation. MMA cannot release that slot until leader-ready, S2T and dependent MMAs complete. Consequently local completion and relay publication of the old generation are necessarily consumed before a new generation can overwrite either barrier or SF storage. There is no separate empty ring to keep in sync. Early SF completion is safe even if payload TMA remains outstanding: MMA independently waits operand-ready.

The CPU event model passes 1,536 schedules / 126,208 events across one/two CTA, ring depths 1–16, zero/one/three tiles and several K-stage counts, including wraparound and asymmetric producer/relay progress. This is bounded phase arithmetic evidence, not a hardware memory-model proof.

## Scheduler and teardown

CLC consumer counts are 352 leader / 320 follower: weight 32 + relay 32 + gather 128 + epilogue 128 + leader MMA 32. Each relay consumes the same tile stream and releases its metadata entry through existing next_work. It performs no SF wait for the terminal ticket. Static no-work and CLC no-routed-work paths go directly to the original final 384-thread rendezvous. A live tile with zero valid rows still has all SF completion arrivals through predicated copies.

Gather can reach the final join with asynchronous copies pending, but relay cannot finish until its last local completion, and MMA cannot finish until both SF readiness and operand completion. Thus the existing full-block join and operand producer tail still drain the new work before SMEM/TMEM teardown.

## Capacity and staging

The additional local barrier array is 8 bytes per stage. The source planner now reserves four operand/SF barrier words per stage (`2 + 2*gather_input`), matching operand full/empty plus local-SF and leader-ready arrays. The source-extracted planner and struct-alignment arithmetic pass 4,480 cases at modeled SM100 capacity 232,448 bytes; the 2,240 FC2 cases are unchanged. The checked R3→R4 capacities have no stage-count changes (up to 11 stages). Actual layout-size equality and final SharedStorage capacity guards remain in production and authoritative at compilation.

This removes gather's explicit SF completion wait while retaining operand-empty as the only reuse authority. It permits latency overlap, but does not guarantee a speedup. Generated register/spill usage, realized stage counts, broad numerical correctness and performance remain separate GPU evidence.
