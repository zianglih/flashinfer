# Receive-counter banking: bounded source review

Read-only review of `COUNTER_BANK_LIFETIME_PROPOSAL.md`; no code or GPU work.
Two counter banks are a plausible smaller change than per-expert return
readiness. The reuse-distance argument is sound if every mode uses the same
device-maintained bank sequence: a fast rank cannot publish invocation n+2
before completing n+1's input barrier, which requires the slow rank to have
finished invocation n and its bank-n clear. Current combine data remains safe
because a fast next invocation cannot pass input publication until slow current
reducers finish and enter that invocation.

Concrete implementation/proof boundaries:

1. **All aliases move together.** Owned `megamoe_kernel.py:522–541` constructs
   `expert_recv_count`, `expert_recv_count_sum`, and the Int32 stride-2
   `expert_token_sizes` alias. The latter is embedded into scheduler parameters
   in `_launch_fc12` (line722). Selecting only transport views would leave the
   scheduler reading the wrong bank. Bank selection must occur in the device
   kernel for graph replay, including a corresponding scheduler-parameter/view
   reconstruction. It cannot be a host launch-time tensor choice.
2. **Retain a stable pointer snapshot.** The bank word must remain outside the
   bulk-zero prefix, initialized with both banks. Every actually used view must
   capture the old bank before the tail toggle and retain it through reset.
   A load performed lazily in cleanup after the toggle would clear the next
   bank. The existing first all-role rendezvous can prove that live bank readers
   have passed their capture point; inspect generated loads and pointer uses.
   No additional startup barrier is needed merely to toggle an already stable
   per-invocation word, but the implementation must establish this domination.
3. **Reset one contiguous bank.** Current shared prefix contains precisely the
   two receive-count arrays before source-token metadata
   (`megamoe_kernel.py:1682–1706`). Arrange each bank as the same aligned pair,
   pass only the current bank's reset view, and preserve the existing offset
   mapper for peer accesses. Do not double the old whole-prefix clear: that
   would recreate the next-launch race. `expert_recv_count_sum` accumulates
   packed counts via a remote reduction, so its zero lifetime is essential.
4. **Production parity is compatible.** Dispatch publication contributes two
   software-grid phases; drain contributes two. Removing cleanup publication's
   two leaves four, with the grid counter zero after the final phase. Resetting
   that zero while slower local participants finish the same final grid read
   does not change the observed value. The two-slot NVLink phase counter is
   persistent outside the zero prefix; two calls per invocation advance it by
   two and self-cancel over two invocations. The next drain prevents a fast rank
   cycling the same signal slot while a slower rank still waits on its old use.
5. **Raw, IKR and profiling need explicit treatment.** Both return tactics and
   explicitly pre-staged/zero-output paths currently share the same transport
   ordering. They must agree on bank evolution; do not choose a bank protocol
   from rank-local output shape or fused-input eligibility. The old
   `MEGA_USE_NCU=1` padding is one extra drain: after removing cleanup it would
   produce three calls, breaking its four-call self-cancellation rationale.
   Either retain the existing unbanked protocol consistently for that compiled
   profiling mode, or prove an adjusted padding/bank-state replay protocol.
   Application replay with `MEGA_USE_NCU=0` is the currently qualified method;
   it does not validate the optional kernel-replay branch.

No remaining counter outside the proposed banks is a remote next-invocation
write target requiring that cleanup publication: the local prefix contains
arrival/send/grid/FC1/FC2/scheduler counters; the persistent NVLink signals and
phase counter are deliberately not zeroed. Source-token metadata is overwritten
for live routes and is consumed before drain. These statements depend on the
current source layout and should be rechecked against the actual patch.

The proposal can shorten a cross-rank cleanup dependency; whether it improves
kernel completion is unmeasured. First use the profiling-only phase plan in
`local-reduce-ready/NEXT_OVERLAP_INDEPENDENT.md` to distinguish cleanup-limited
from reduction-limited cases. Existing NCU counters are insufficient. This
review is a feasibility assessment, not approval of an implementation.
