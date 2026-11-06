# Independent companion synchronization review

Read-only review of the active `flashinfer-pipeline-tail-review` and `flashinfer-per-token-warp-reduce-review` copies. Exact source hashes are in `companion-review-source.json`. No source edits or new GPU work.

## Operand terminal drain

No correctness concern found in the current three-file revision. The runtime audit in `../pipeline-tail-f63/evidence/method-audit-v2.json` resolves the actual method: every changed operand pipeline uses `PipelineAsync.producer_tail`, whose entire contract is to wait each empty slot then advance its local terminal state. The custom and SDK accumulator overrides remain outside this helper.

For next-write state `(i,p)`, the old N-step traversal visits slots i..N−1 at p, then0..i−1 at p XOR1. The new helper's `p XOR(stage<i)` waits the identical slot/phase set. This includes i=0, N=1 and a producer that had no tiles. Every changed call follows its role's terminal scheduler result and final producer publication. No producer acquire, copy, commit or dependent release remains after the helper; consumers can drain independently. Reordering terminal waits therefore introduces no circular wait. It does not change which stages protect weight, dequantized weight or activation lifetime.

Reviewed call-site boundaries: swap weight producer after final work loop and its PDL publication; W4 activation-TMA producer, weight-TMA producer, transform producer, and fifth gather-WG producer after their final tile. The relevant states are dead after their respective calls, so omitting the old state mutation has no later effect. CLC metadata, accumulator leader-only drain, TMA-store completion and final CTA/cluster resource joins are preserved. This argument does not justify using the helper for any pipeline with a specialized tail, or reordering steady-state waits.

## One-warp per-token quantizer reduction

No hidden barrier requirement found. The constructor enforces a positive multiple of32 threads and defines `warps=threads//32`, so `warps==1` is exactly one complete warp. Both register-resident and two-pass paths reach `warp_reduce` with all32 lanes: row validity and loop-row selection are uniform, and no lane exits early. The existing butterfly shuffle reduction returns the same row maximum to every lane. Amax is built from nonnegative absolute values starting from+0, so the old second reduction with identity0 does not add a needed numerical operation.

With one warp, bypassing `block_reduce` removes its lane0 shared write, CTA barrier, shared reload, and second shuffle reduction. The reduction buffer is then unused in that compiled specialization. The row-end barrier only protects reuse of that buffer across rows; output payload, scale and per-token scalar writes use disjoint row locations and do not create a cross-lane communication dependency. Inactive routing holes only clear their own SF slots. Register-held values do not require a CTA barrier between rows. The multi-warp specialization keeps both barriers and the shared reduction exactly as before.

The quantizer's grid dependency wait, ancestor publication and dependent launch signal are unchanged, so this does not weaken the FC1/FC2 handoff. No claim is made that a barrier can generally be removed merely because a CTA has one warp: the absence of shared-memory communication in this particular specialization is the reason.
