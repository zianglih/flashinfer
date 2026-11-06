# Gather FC1 synchronization audit

Audited `flashinfer-fc1-gather-review` at `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`.
Kernel references below are to `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`.
This is a source/ledger audit, not a proof for every compiled tactic.

## First candidate: weight-scale publication before gather readiness

At lines 3273–3306 the MMA warp acquires weight TMA completion, then gathered B
completion, then issues all scale S2T copies. SFA depends only on the first wait.
Issue SFA0 and (when present) SFA1 between those waits; keep SFB after the gathered
shared-memory acquire. The scale destinations are disjoint. The same MMA warp
continues issuing TCGEN05 copies and MMA, and the operand stage remains held until
the existing completion release after both channel tiles. This does not require
a new fence, buffer, pipeline stage, scheduler consumer or tactic.

There is a direct scheduling precedent in the local CUTLASS SM103 grouped kernel:
`references/cutlass/examples/python/CuTeDSL/cute/blackwell/kernel/blockscaled_grouped_gemm/sm103_grouped_blockscaled_gemm.py:1228–1246`
issues SFA/SFB S2T from its acquired SF pipeline before acquiring the independent
A/B payload pipeline. Our candidate only moves weight SFA; gathered SFB still
needs its existing generic/async proxy and cluster publication chain.

Implemented as an isolated unstaged experiment in
`flashinfer-fc1-gather-sfa-overlap-review`, one file, +20/−8. Final FC2 specialized
AST is identical after folding `gather_input=False`; FC1 preserves 1/2-channel and
1/2-CTA ownership. Details and source proof are in `sfa-overlap/`.

## Dependencies to retain

| Resource | Ownership and minimum completion boundary |
| --- | --- |
| Weight TMA stage | Weight warp announces expected weight/SFA bytes for both CTAs; MMA acquires before SFA or weight consumption. |
| Gather local stage | Each CTA's 128 gather threads publish their SF cp.async completion, plus one transaction arrival accounts for Gather4 bytes. The relay must acquire both before publication. Count 129 and phase progression are intentional. |
| Gather cluster publication | Relay retains local wait and async-proxy fence, then shared-only cluster release/relaxed arrival. Leader MMA retains cluster acquire. The explicit cluster scope covers the peer CTA. |
| Shared operand empty ring | Weights and gathered inputs are reused together only after the leader's final channel-tile MMA completes. Both producers can issue independently once their shared stage is empty. |
| Accumulator ring | Only leader CTA issues the MMA full notification; all 128 epilogue threads per CTA acknowledge empty. Early release covers the overlapping accumulator interval, not necessarily every later TMEM read. |
| CLC response | Both scheduler warps consume the multicast response and release its stage; leader tail protects the peer acknowledgement. |
| CTA-local tile info | Consumer count is 352 threads for gather leader and 320 for follower (`32*(6+4+is_leader)`); follower MMA does no work. All consumers release after copying metadata to registers and consume the terminal sentinel. |
| Initialization and teardown | Initial barrier fence/cluster join, TMEM allocation retrieval and final 384-thread join are separate lifetime boundaries. Final TMEM free retains its two-CTA handshake. |

The current `operand_pipe.producer_tail` protects the independent weight/gather
producers collectively. Removing it because a gather issuer has returned would
confuse issue completion with asynchronous read completion. Similarly, the outer
epilogue TMEM-load fence at line 3477 cannot be removed solely because an earlier
accumulator interval was released: the overlapping path may continue reading and
transposing non-overlapping slabs afterward.

## PDL and register scopes

Gather FC1 consumes `moe_sort` routing directly. Its current producer does not
publish completed routing at its early PDL launch signal; therefore the FC2-style
weight/scheduler run-ahead must not simply be enabled for FC1. The host deliberately
sets `prefetch_weights_before_wait=enable_pdl and not gather_input`.

A later general candidate is to move role-local, data-independent descriptor
partitioning/pipeline-state setup before each role's dependency wait, while keeping
all `num_tiles`/mapping reads after it. This needs a small restructuring because
`num_routed_tiles` is currently loaded before role dispatch. It is less attractive
than the SFA scheduling change until a startup trace shows a visible bubble.

The 80/128/256 register policy is scoped inside non-reconverging control/gather/
epilogue regions. Preserve that structure. R9 donated before reconvergence and
increased spilling; R11's scoped policy eliminated the captured N3U spills. The
prior broad 144-cell campaign still had 52 FC1 instances with 8–16 bytes of local
storage, so do not assume every remaining local allocation is eliminated or that
arbitrarily lowering the control budget is safe. Actual cubin resource guards
remain necessary when a candidate is compiled.

## Directions already rejected or not justified by this audit

- Do not repeat CLC request-before-info-acquire blindly. The local scheduler
  audit (`optimization-20261028/warp-polish/scheduler/README.md`) records this
  direction as rejected in `perf-general-20261026/clc-request-overlap`; it can
  reserve a new item while metadata consumers are stalled. The W4A16 scheduler
  retains info acquire before CLC request (`moe_w4a16_kernel.py:1487–1495`).
- Do not centralize ordinary-scheduler metadata in another shared queue: prior
  static-metadata lookahead was slower, and this introduces a new synchronization
  dependency where independent role reads currently suffice.
- Do not remove gather proxy/acquire fences. R12 already replaced the expensive
  broad GPU publication with the shared-only release/acquire protocol; the ledger
  measured K3 GPU-wide fences falling 29→1. Its remaining proxy ordering is a
  distinct correctness requirement, not the original broad-fence overhead.
- Do not repeat R8's SF-completion publication reorder alone: it did not retain
  a gain. New issue-overlap changes should be measured against `fb66a27e`, not the
  much slower R6 prototype.

No new model/dtype/TP/EP heuristics are proposed. The minimal SFA candidate is first
because it exposes already independent work without changing storage ownership.
