# Independent TMEM startup protocol review

Approved for the focused exact-output/codegen gate; no source protocol blocker found. This is not GPU validation or a performance-retention decision.

Reviewed clean `9b4721b08057d0a488c1f0236467acb75c48cd00` plus frozen patch `be8a12bb3090703aea918d3d0b72e7cd4cd0a678de97a25ab1ea5f83d3f36373` in `flashinfer-clc-tmem-startup-20261027`. Kernel SHA256 is `0e1a6c2c498eecffbfc78fbff1ffaaa2cdb072ed68916c767ae811e55945079e`. The live diff, saved patch, source receipt and kernel hash agree. Only the blockscaled Blackwell kernel changes. Reversing the explicit wait/count/pointer changes in memory reproduces the complete HEAD AST, so scheduler protocol, PDL, producer/epilogue arithmetic, host policy, Rubin and W4A16 code are otherwise unchanged. The independent identity/count result is in `protocol-review.json`.

## Allocation publication and participants

Exact CuTe DSL4.7.1 `TmemAllocator` source establishes that `allocate` issues the hardware operation only from allocator warp0, `wait_for_alloc` is the supplied named barrier, and `retrieve_ptr` performs an unsynchronized shared load. Common allocation and bookkeeping remain before the worker wait. Every actual TMEM reader must therefore retain that wait; merely deleting a scheduler pointer use would not be sufficient.

| Epilogue | Scheduler | Total threads | Barrier3 participants |
|---|---|---:|---:|
| Inline | Static | 160 | 160 |
| Inline | CLC | 192 | 160 |
| Overlap | Static | 288 | 288 |
| Overlap | CLC | 320 | 288 |

`schedule_warp` is calculated before adding the CLC warp. Consequently `32 * schedule_warp` exactly counts workers, and the CLC-only predicate includes all of them exactly once. Static kernels take an explicit compile-time fallback with the original unconditional wait and unchanged participant count. No worker can reach a TMEM pointer read before this wait.

The producer pointer is declared and consumed only for inline epilogues. The dedicated epilogue and MMA pointers remain inside their respective existing role branches. Scheduler threads neither wait on barrier3 nor retrieve a pointer. No dummy pointer, branch-exported pointer or early shared holding-buffer read was introduced. Moving the reads can still alter lifetimes and register allocation; the planned static codegen comparison is necessary.

## Initialization and barrier phases

The existing initialization fence remains. Two-CTA relaxed cluster arrival remains and qualified SDK `pipeline.pipeline_init_wait(cluster_layout)` resolves to the same cluster wait. One-CTA CLC now receives a common full-CTA initialization join before physical allocation: this replaces the initialization ordering previously supplied by the all-thread TMEM barrier. Static one-CTA kernels get no additional initialization join. The repository's similarly named fence-only custom helper is not used.

Named barrier0 is the one-CTA initialization join, barrier1 remains the final all-thread join, barrier2 remains the 128-thread freeing-role join, barrier3 is TMEM publication, and the existing epilogue transpose uses barrier6. The initialization phase completes before role divergence; no new concurrent reuse of a named barrier is introduced. Deferred info/CLC barrier initialization and two-CTA scale-join initialization are covered before the scheduler can proceed.

## PDL and teardown

PDL waits, routing-publication prerequisites and dependent-grid signals are unchanged. Where startup prefetch publishes routing early, scheduler progress may now precede worker TMEM readiness; otherwise the scheduler still executes the existing dependency wait before reading payload-dependent metadata. Metadata acquire-before-claim, full-warp response accounting, response tail and terminal publication are unchanged.

All threads still join barrier1 after their role finishes. The first128threads still relinquish the allocation permit and join barrier2. Their fresh pointer retrieval follows completed allocation and the final joins; only allocator warp0 issues the actual free. SDK two-CTA deallocation retains its independent32-thread peer-arrival/local-wait handshake. No scheduler participation in that handshake was removed.

## Remaining validation boundary

Proceed with the unchanged eight-case CLC source-paired replay/codegen gate, plus static cases covering one-CTA inline and two-CTA overlap with PDL off/on. Inspect actual barrier counts, absence of scheduler TMEM loads/waits, register/spill/resource changes, and the potentially additional final pointer load. The source review does not establish that the one-CTA initialization barrier or pointer lifetime changes are profitable. No production source edits or GPU launches were made by this reviewer.
