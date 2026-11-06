# Gather relay proxy fence: keep

Read-only follow-up against retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`; no kernel edit, compile, launch or timing claim.

The relay's `fence_view_async_shared()` is not redundant with its preceding completion wait. Non-bulk `cp.async` uses the generic proxy, whereas `tcgen05.cp` reads shared memory through the async proxy. TMA bulk completion has an implicit cross-proxy fence; the non-bulk scale-copy path does not acquire that property merely because payload TMA completes on the same barrier. CUDA 13.2.2 PTX explicitly distinguishes these operations: [cp.async](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async), [bulk async proxy](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#asynchronous-data-movement-and-conversion-instructions-async-proxy), [TCGEN05 shared accesses](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-memory-consistency-model-shared-memory-accesses).

Current source sequence:

- The gather threads issue four-byte non-bulk SF copies and attach their completion to the local barrier; Gather4 payload transactions complete on that same barrier.
- The activation-control warp waits for local completion, executes the existing proxy fence, then publishes the CTA's gather arrival.
- The MMA leader acquires all contributing CTA arrivals before SFB's shared-to-TMEM copy. The two-CTA path also retains its scoped release/acquire publication.

Thus the local completion wait, proxy fence and remote publication have different purposes. Removing this fence because the payload uses TMA would conflate payload and scale transport. The previous `swap-gather-publication-followup.md` conclusion stands. This audit does not introduce another producer join or fence, and does not claim a sampled fence instruction is measurable end-to-end overhead.
