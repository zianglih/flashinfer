# Accumulator-derived metadata lookahead

Keep one logical tile per CLC ticket and the current acquire-before-cancel order. Only default metadata queue sizing changes; callers may still request a positive explicit depth. Public FC1/FC2 wrappers use None for automatic sizing.

The metadata consumers release a queue entry immediately after loading its tile/expert/valid values. The slowest epilogue role does not request its next entry until its current tile has completed. With a one-slot ring, this can prevent the operand producers from receiving the tile after their next tile while MMA/epilogue occupy multiple accumulator slots. A queue with depth equal to accumulator stages permits that lookahead without adding a problem-specific policy.

The automatic count is resolved both in the kernel constructor and in shared-memory byte accounting, including automatic K selection and final operand ring sizing. Explicit stage counts remain authoritative. The pipeline already uses arbitrary ring depth and matching producer/consumer states; work mapping, cancellation, terminal publication, PDL, accumulator ownership and arithmetic are unchanged. Every consumer reads values before releasing its slot, so extra slots cannot overwrite still-unread metadata. A terminal entry is ordered after all issued work and producer_tail waits for its consumers exactly as before.

Caveat: acc_stages=1 can still allow two overlapping TMEM windows through overlap_acc. This first experiment intentionally leaves those geometries at depth1. A separate acc_stages+1 policy may test one additional operand-lookahead slot, if justified by the first results. Do not claim acc_stages alone fully represents partial-window concurrency.

Historical risk: scripts/clc_regular_tma_experiment/AUDIT.md reports prior fixed depth2 V3 decode losses (NV3.13%,MXFP8 3.19%,mixed9.27%); W4A16 history shows excess queue depth can reserve work too early. Current pipeline/PDL differs, but any prefill gain must be checked against decode, not retained from one large shape.

Gate: reuse the 64-replay matched-b85eff41 all-CLC source-paired four-format PDL/on-off N16/N128 one/twoCTA changing-route exact gate, with observed metadata depth equal to acc_stages and depth2 actually exercised. No upstream tests. Screen K3 at both published and native-CLC geometry and V41 mixed first, same public100sample cold-L2 fixed tactics.
