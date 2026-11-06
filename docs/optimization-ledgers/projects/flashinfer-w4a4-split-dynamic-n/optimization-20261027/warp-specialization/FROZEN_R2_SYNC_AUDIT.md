# Frozen r2 synchronization review

Read-only review of patch `e78b8c48`, kernel `e14519f9`, source config `62da0622`, and installed CuTe DSL4.8. No source changes or GPU work. The runtime gate and generated-code artifacts are complementary evidence, not a substitute for the protocol trace below.

**No blocking correctness or maintenance finding.** I found no remaining scalar SFB copy, proxy publication, extra cross-CTA SF join, or predecessor-payload load on the MMA/scheduler path.

## Shared operand ring

`moe_swap_ab_kernel.py:2367` initializes each full barrier with two arrivals. The installed `PipelineTmaUmma.producer_acquire(expected_tx=...)` elects one lane in each calling producer warp and only announces on the leader CTA. Its empty wait remains local to each CTA. The actual byte terms are:

```
W = channel_tiles * (128 * tile_k * weight_bits / 8 + sf_stage_bytes)
B = b_copy_rows * tile_k * activation_bits / 8 + sfb_stage_bytes
leader expected bytes = cta_group_size * (W + B)
```

These are transferred bytes, not the expanded mixed-FP4 SMEM allocation or unused allocated-N padding. Every channel tile contributes A and SFA; each CTA contributes its compact B slice and a complete local SFB copy. For group2, A/SFA/B use group2 TMA atoms, and `_blockscaled_tma_sfb` clears the rank bit in the completion-barrier address. Both CTAs therefore complete the leader's announced total. The generated MXFP4x8 N16 example announces17408 weight bytes and3072 activation bytes, matching these formulas.

Both producer states enumerate the same tile/K sequence and persist across tile boundaries. Their two arrivals prevent an early full phase even if one producer completes first. Only the leader MMA waits on full and issues S2T/MMA; its single group2 UMMA empty commit releases both local empty stages after all channel MMAs. No valid-row predicate skips a role's arrival or transfer. Dynamic MMA N changes consumed columns, not the TMA byte contract.

The weight-only common tail is valid: the installed generic `PipelineAsync.producer_tail` directly waits every empty stage; it does not announce another full arrival. This installed method was independently read and pinned in `sdk48-pipeline-async-tail.json`. Empty completion also proves the activation producer has finished the corresponding stage. The final CTA join prevents either role from leaving while another still uses local storage.

## PDL and role-local work

Preparation waits on its ancestors, then republishes completed routing before its startup signal. FC1 repeats that publication from activation warp1 after its predecessor wait. FC2 weight warp0 performs its postponed dependency wait before producer-exit release/signal. Static CTA0 or each executing CLC leader provides the publication owner, so CLC cancellation does not depend on a canceled physical CTA0.

MMA2 and scheduler3 may read only that already-published routing before their wait. MMA setup, fragment addressing and accumulator-empty acquisition do not read predecessor payload. The payload ordering chain is predecessor completion → activation1 dependency wait → B/SFB TMA → shared full acquire → S2T/MMA. Alpha, normalization and per-token scales remain on epilogue warps after their startup wait. Weight0, MMA2 and scheduler3 still execute a dependency wait before leaving, including empty/follower/static-scheduler paths. FC2's signal permits combine startup; it does not claim FC2 payload completion.

This relies on CUDA's release-fence/PDL start synchronization and the grids sharing a memory-synchronization domain. The scoped wrappers preserve that domain; a future cross-domain launch contract would require a system-scoped publication or another explicit mechanism. See [CUDA13.2.2 PTX griddepcontrol](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol).

## Metadata, TMEM and remaining work

The CLC metadata ring counts224 consumers: weight, activation, MMA and four epilogue warps. Each consumes the terminal entry and releases metadata immediately after register loads. The scheduler is not a metadata consumer; its CLC response still counts32threads per CTA. The final CTA join drains terminal consumers, so an extra metadata producer tail is unnecessary. Static scheduling compiles out the CLC ring and loop.

MMA still performs SFA/SFB S2T copies. They are necessary with the current single TMEM SF lifetime: moving those copies to a producer would need another cross-thread publication and overwrite protocol. Follower MMA metadata consumption is required by the present224-consumer quorum even though only the leader issues group2 instructions. Removing it is a different asymmetric ownership design, not deletion of an accidental wait. No additional optimization is recommended from this audit alone.

Warp0 initializes barriers; the initialization fence, group2 cluster join and256-thread TMEM allocation/retrieval join remain. Epilogue physical warps4–7 and their128-thread scratch barriers are unchanged. Accumulator completion, TMEM-read fences, partial-release points and bulk-store drains remain in place. The final256-thread join precedes allocator warp0's peer deallocation handshake/free. One/two-CTA groups and fixed256-thread launch are required invariants.

Boundary: all supported layout formulas were traced, but runtime evidence is the bounded144-replay matrix, not an exhaustive dtype/shape cross-product or sanitizer proof. Routing metadata must be immutable once published, both producers must retain identical work/K ordering, and future copy-extent changes must update their expected-byte terms. Existing declared dependencies require CuTe DSL>=4.8, which provides the native expected-byte override used here.
