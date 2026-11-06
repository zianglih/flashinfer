# Independent scheduler-candidate review

Reviewed the isolated scheduler candidate against retained `99f4d0c27`.
No source-level blocker found. Compilation, generated-code inspection and
source-paired runtime checks remain required; this is not a performance claim.

The local metadata queue has no remote producer/consumer mask. Its remaining
consumers are weight warp 0, activation warp 1 and epilogue warps 4–7 in both
CTAs, plus MMA warp 2 only in CTA 0. The candidate's counts are therefore 224
for CTA 0 and 192 for CTA 1. One-CTA launches have CTA rank zero and retain 224.
`CooperativeGroup(Thread, Int32)` and `MbarrierArray` accept the runtime uniform
count in the captured installed CuTe 4.8 source. Elected warp 0 initializes the
CTA-local count before the unchanged initialization fence/startup rendezvous.

Leader-only MMA dispatch preserves all hardware work: S2T scale copies,
accumulator acquire/commit/tail, dynamic MMA issue and operand release were
already guarded by `cta_rank == 0`. The eliminated follower work comprises
private descriptor/tensor construction, metadata reads/releases and local
pipeline-state arithmetic. Its metadata participation was the sole externally
visible operation, and the queue's empty quorum changes consistently with it.
Both follower TMA roles and all follower epilogue lanes remain active.

Accumulator empty count remains `128 * cta_group_size`: every CTA's epilogue
still fences and releases its own TMEM reads. Operand group-two signaling and
CLC raw-response consumer count remain unchanged. Both scheduler warps still
read each raw response and acknowledge it; the leader's response tail remains.

When startup prefetch is active, MMA and scheduler delayed PDL waits now occur
after dispatch. The now-idle follower MMA warp still executes its wait before
the final join. Weight's separate exit wait/publication remains unchanged;
activation and epilogue still wait before reading predecessor payload. Without
prefetch, the common startup wait still covers all threads. No branch bypasses
the final 256-thread join, allocator-warp permit release or peer-CTA free
handshake. Static scheduling omits the metadata queue as before.

The patch introduces one actual-ownership predicate and removes repeated
leader guards; it adds no model/dtype policy or autotune axis. Generated code
must verify that the dynamic count is initialized correctly in both CTAs and
that the one-CTA specialization does not acquire avoidable register/instruction
cost. No reason was found to alter the candidate before its isolated screen.
