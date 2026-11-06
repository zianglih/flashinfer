# Producer-drain PDL boundary audit

Read-only source assessment against `flashinfer-pdl-allthread-review`, core
`adcc6506dd4ba28769cf7a5f65526e9dc927363847150de231eb850cc6c9b4b9`.
No implementation, GPU work, or timing was performed for this proposal.
Keep the already measured early preparation and FC1 signals unchanged.
Parent's subsequent adcc trace narrows the candidate to FC2: combine parks
for about145 microseconds of FC2, while most endpoint loss is after FC2.
The exact trace/result remains diagnostic evidence, not a new benchmark run
in this audit.

## Boundary and exact proposed placement

For FC2, signal once the payload producer warp has issued its final persistent
tile, before its operand rings drain. Keep the FC1 all-thread signal after
the prerequisite wait using a static `activation_type is not None` branch.
Move FC2's release/signal to the existing warp-0 tail branch at core1253.
Reorder the two independent operand drains as follows:

```python
# After the complete producer persistent loop, inside existing warp < 4 role.
if warp == 0:
    if cutlass.const_expr(self.activation_type is None):
        if cutlass.const_expr(self.enable_pdl and not self.use_fused_finalize):
            _blockscaled_release_gpu()
        griddepcontrol_launch_dependents()
    a_pipe.producer_tail(producer.clone())
if cutlass.const_expr(not self.tma_sfb):
    ab.producer_tail(producer.clone())
```

This reuses the existing warp predicate, without election, a new barrier,
per-tile last-iteration test, token threshold, or dtype/geometry eligibility.
The prerequisite wait at core1003 stays where it is. No input reads move
before it. Remove the original startup signal for FC2, otherwise the later
boundary would have no scheduling effect. FC1 retains its early signal;
this is a semantic producer/consumer distinction, not a workload-size policy.

**The cloned A state is required.** Installed CuTe4.7.1
`cutlass/pipeline/sm90.py:338–359` implements inherited
`PipelineAsync.producer_tail` by waiting every empty stage and advancing its
state `num_stages` times. Keeping the old `a_pipe.producer_tail(producer)`
before `ab.producer_tail(producer.clone())` would flip the phase in warp0 only;
its SF-tail wait would then differ from warps1–3 and can deadlock. Independent
clones preserve the original drain phases. The original state is unused
after these drains.

## Lifetime and participation proof

- A and AB empties are independent TCGEN-completion notifications issued
  after each stage's MMA (`core1517–1527`, custom pipeline238–249 and551–555).
  Neither final drain produces work needed by the other. Moving the A wait
  ahead of AB introduces no cycle: MMA/epilogue roles remain independent,
  and all operand-producing loop iterations have finished in the warp that
  starts its drain. Other SF producer warps can finish and wait on AB while
  warp0 waits on A.
- Every CTA has warp0 and reaches this loop-exit site, including a CTA with
  no assigned tiles and both members of a two-CTA group. Do not add a leader
  `cta_rank == 0` guard. Group2 empty notifications already reach both CTAs;
  the existing group2 relay and accumulator tails remain untouched.
- Zero-work CTAs execute the same initialized-empty drains as before, now
  with preserved cloned states. A signal from them alone cannot start the
  successor until all other CTAs signal or finish.
- FC2 nonfused triggering threads individually retain the prior prerequisite
  wait → GPU-release → trigger causal chain for routing metadata consumed
  before combine's wait. This does not publish unfinished FC2 output.
  Combine output reads remain after its dependency wait. FC1 needs no new
  release because FC2 reads its data only after waiting.
- Keep both operand drains, the separate accumulator/relay drains, the final
  all-thread barrier, and TMEM relinquish/free unchanged. A PDL scheduling
  signal neither releases buffers nor permits deallocation.

## Why before the drains

Producer-tail is not merely an issue-complete marker: its empty waits prove
the final operand MMAs have completed. Signaling after both tails leaves
only epilogue/free work, and inline-epilogue configurations have already
finished that epilogue in the producer loop. Before-tail placement leaves
the existing bounded operand/accumulator queue drain and final epilogue
available for overlap. The bound follows queue capacity, not an arbitrary
time offset or workload selector. There is no numerical guarantee of an
overlap duration or performance gain.

In all-TMA configurations producer warps1–3 may finish their bookkeeping
well before warp0 finishes issuing transfers. Therefore signaling from all
four producer warps, or from the first role reaching a common join, would
recreate prematurely early signaling. The existing warp0 branch identifies
the actual TMA issuer without an additional predicate.

For FC2 separate epilogue roles this can overlap combine startup with final
MMA/epilogue work. Inline-epilogue roles offer less overlap naturally; no
special-case disabling is proposed. The all-CTA trigger requirement makes
the slowest producer warp determine grid eligibility. One-CTA-per-SM large
SMEM still limits simultaneous GEMM residency; a zero-SMEM combine can share
resources during the drain. Its total overlap must be measured, not inferred
from kernel launch timestamps.

## Bounded next gate, if parent chooses this candidate

Compile the same FC1/FC2 N16/N256 source statics first. The reused predicate
does not prove unchanged compiler uniformity: verify registers, no spills,
mainloop election/reconvergence counts, and one signal per CTA path. Use the
existing exact/native T4 and T16384 diagnostic against frozen adcc, preserving
all input/source/cache receipts and full samples. This is a proposal only.

PTX [grid dependency control](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol)
defines the all-CTA scheduling and prerequisite-memory ordering. CUDA's
[PDL graph contract](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html#use-in-cuda-graphs)
continues to apply; no launch attributes or graph edges change.
