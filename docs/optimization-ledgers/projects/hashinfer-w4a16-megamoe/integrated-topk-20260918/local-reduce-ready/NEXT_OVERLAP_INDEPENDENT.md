# Earlier FC2 consumption: source and measurement boundary

Read-only review against c2b93f5 and retained 7dc. No implementation or GPU work.
The existing `NEXT_OVERLAP.md` identifies the right dependency: local FC2
production is not completed return to the source rank. No small relocation of
the current readiness flag establishes per-expert completion for both modes.

- In owned `bf16_nvfp4/epilogue.py:197`, `signal_fc2_done` publishes only for
  dispatch return. The epilogue rendezvous and proxy fence precede a batched
  **GPU-scope** release to `fc2_done_counter[expert]`. This certifies the local
  BF16 pool for dispatch TMA reads. Shared `token_comm.py:1332` waits on that
  threshold before issuing the return. It is too early for source-rank combine.
- Shared `token_comm.py:1415–1416` commits and fully waits each outgoing data
  chunk. The caller uses `chunk_bytes=self.hidden_bytes` at line1667, so the
  current BF16 data path has one complete hidden-row transfer per token route.
  A return certificate must occur after this wait, before advancing the token.
  There is no existing per-expert completed-return counter to reuse.
- Epilogue return writes remote slices directly. `signal_fc2_done` suppresses
  FC2 publishing in this mode; `megamoe_kernel.py:1330` performs the system
  fence only after the whole epilogue loop. A per-expert certificate needs a
  new system publication point and an exact count of all token/hidden tiles.
  The existing batching helper stores one counter address per completed tile
  in rotating lanes and later issues one integer reduction per nonnull slot
  (`flag_batch.py:46–90,111–120`); it is not one aggregate increment per expert.

A bounded protocol could count completed returns locally on the expert owner,
then send one generation-tagged integer certificate per active
expert/source-rank pair. For dispatch, that adds at least one local accounting
event per returned route (or proven warp/expert batch) plus up to
`experts × EP` remote certificates. For epilogue, it adds tile completion
accounting and system release ordering before the same certificate stage.
These are not per-vector remote atomics, but they are more than reusing the
current FC2 counter. A last-publisher relay needs cumulative acquire/release
semantics that carry every producer's data, not just its own writes.

Retired roles can only start after their own pipeline tails and final scheduler
consumption. c2b also retains a CTA rendezvous with dispatch; in dispatch mode
that CTA's assigned token returns have already completed before it passes.
d4 may expose an earlier local retirement window, but it does not certify any
remote data. Tokens need all their routed experts, in unchanged route order;
waiting on the first assigned unready token can hide available work elsewhere.
Empty experts, uneven ranks, generation reuse, and nonblocking producer
progress remain essential. This is a separate transport protocol, as already
recorded in `NEXT_OVERLAP.md`, not another score-prefetch trial.

The useful next diagnostic is a small profiling-only timestamp variant before
implementing that protocol. Retained 7dc already overlaps reduction with
cleanup; c2b additionally overlaps the local drain broadcast. Earlier reduction
cannot shorten completion when cleanup remains longer.

Record fixed per-CTA slots, with one lane per role and no new atomics or
barriers: role retirement, first rendezvous entry/exit, dispatch drain acquire,
local broadcast end, shared reset end, cleanup publication end, local reset
end, and each reducer warp's first/last work. Separate graph replay records
using host-owned output slices; do not reuse a live record. Use per-device
timestamps and compare local maxima of reducer completion and dispatch cleanup;
do not subtract timestamps across GPUs. A diagnostic `%globaltimer` read is
supported by the pinned target but its behavior is target-specific, so this is
not a portable production API. [CUDA13.2 PTX9.2](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#special-registers-globaltimer)

Inspect generated placement/resources and measure instrumentation overhead
against the same uninstrumented source. These timestamps can identify whether
cleanup or reduction is last, but they still perturb scheduling. NCU128's
replay stall percentages and millisecond durations cannot supply these phase
durations or establish an early-consumption speedup. No diagnostic run is
authorized by this note.
