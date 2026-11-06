# Swap accumulator terminal drain audit

The swap-only `acc_pipe.producer_tail(producer)` can be removed while preserving the final CTA join, the two-CTA deallocation handshake, all operand tails, and every steady-state acquire/release. W4A16 is excluded: its deallocation happens inside the epilogue role, without the swap kernel's final all-thread join.

Bound source: `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`, swap kernel `f41712327504ba6bc4c1c2c28aeb7d38536fa0d59400f9c977ddf2eb2f041e4a`. This is a source/memory-model argument, not runtime qualification.

## Lifetime argument

1. Every epilogue iteration waits for its accumulator full phase before TMEM reads. It fences TMEM loads and issues its empty arrival before finishing the tile. Early overlap release can precede remaining unprotected reads, but the epilogue does not reach the final join until all those reads and output work finish.
2. `PipelineUmmaAsync` uses `AsyncThread` empty arrivals. The actual CuTe4.8 implementation resolves `consumer_release` to ordinary `cute.arch.mbarrier_arrive`, not asynchronous `cp.async.mbarrier.arrive` or a pending UMMA commit. The captured two-CTA PTX confirms `mbarrier.arrive.shared::cluster.b64` on the leader's accumulator empty barrier.
3. Swap's final `NamedBarrier(1, threads_per_cta).arrive_and_wait()` includes the epilogue, MMA, scheduler, weight, relay and gather roles. Prior ordinary memory operations are ordered before the allocator warp leaves this join. No accumulator barrier is reinitialized or reused afterward.
4. For two-CTA MMA, the actual `TmemAllocator.free` implementation makes every allocator-warp thread arrive on the peer's dedicated deallocation barrier and wait on its own before `tcgen05.dealloc`. Thus the peer's full CTA join also precedes deallocation/exit. The peer handshake remains necessary; a local join by itself is not the two-CTA proof.
5. MMA and TMA asynchronous accesses remain covered by full-phase consumer waits and the unchanged operand producer tails. Accumulator empty arrivals are ordinary thread operations and do not require a second asynchronous drain.

For an empty tile sequence, the same joins execute with no accumulator traffic. For static and CLC schedules, all roles finish their existing work/metadata loops before joining; no new work can be published afterward. PDL release/signals and final dependency waits are unchanged. The producer's terminal state is dead after the removed call.

## Runtime and PTX evidence

`runtime-source.json` was read from the exact deployed CuTe4.8 runtime with no CUDA work. It records unwrapped source paths and file SHA256 for `TmemAllocator.free`, `_init_dealloc_mbarrier`, `PipelineAsync.consumer_release`, `MbarrierArray.arrive_mbarrier`, and `NamedBarrier.arrive_and_wait`. The common producer-tail docstring explicitly describes its normal use preventing dangling arrival signals; the joins above provide that lifetime boundary here.

Existing matched b139 control PTX: `../two-epilogue-wg-audit-b139/compile-feasibility/evidence/control/mx8-n256-relu.ptx`, lines1319/1683 accumulator remote arrivals,4736 full CTA join,4745 allocator peer arrival,4757 two-CTA deallocation. The full source and CUBIN receipts remain in that diagnostic; no inference from an unrelated variant.

[PTX13.2.2 barriers](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-bar): CTA barriers order prior ordinary memory accesses among participating threads. [Mbarrier arrival](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-arrive) is a normal synchronization operation; asynchronous copy arrival is a separate instruction. [TMEM access rules](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-memory-access-restrictions) require peer accesses to finish before deallocation and permit exit afterward.

The earlier `pipeline-tail-f63` experiment preserved accumulator overrides by design; it did not test deleting this terminal wait. No prior equivalent rejected experiment was found in the bounded ledger search.

## Qualification boundary

First pair existing39 cases and codegen under the unchanged runtime, with exact outputs and no new local traffic/resources. Include one/twoCTA, static/CLC, accumulator overlap, partial token/K tiles and all supported activation/quantization contracts. Check a zero-work case and graph routing changes if existing cases do not cover them. Only after this gate should a bounded source-paired CAAC screen be proposed. No W4 edit, new tactic, timing claim, or sanitizer run is part of this audit.
