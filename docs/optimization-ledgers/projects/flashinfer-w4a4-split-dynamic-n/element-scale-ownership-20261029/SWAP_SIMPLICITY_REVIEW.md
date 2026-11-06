# Swap A/B producer simplicity review

Read-only review against658a. Frozen A: `02031c5fe86a2c40591272feb4953da113e8e345eaf7915b089ff411dba2b1c7`; B: `15d9533fac47677348ea161edaeca850ce4b49e0130fe465808d1ec0c7ef6259`. No source edits or GPU work. The two static-copy/refill helpers are identical between variants.

## Minimum required mechanism

- A merged warp needs distinct independent and dependent stage cursors. Otherwise waiting on payload, gather relay or stage reuse can stop ready weight work; blocking on a future raw slot before issuing older dependent stages can deadlock.
- Fast tile/K/expert/cache-hint fields must remain cached across dependent work. They cannot refer back to released metadata. A separate fast metadata cursor and one slow release cursor are necessary when lookahead crosses work tiles; the existing metadata ring avoids a new queue.
- `pending` identifies whether the warp owes dependent work. Only zero-pending acquisition may block; positive-pending refill must stop on backpressure. The voted nonblocking query is necessary for uniform cursor advancement. Successful tests already skip the subsequent blocking empty wait.
- Payload acquisition is once per warp, and A's producer-exit signal is once after A finishes and ancestor payload is acquired. Those state distinctions preserve early publication and empty-work behavior. A shared cursor or unconditional early wait would change the intended PDL contract.

This additional machinery is required by the merged ownership experiment, not by658a's original independent producer warps. FC1 also needs independent refill versus relay progress even though public FC1 does not prefetch before its startup dependency wait.

## Actual simplification opportunities and limits

1. **Three inlined refill call sites:** initial setup, each dependent K stage, and work-tile end. Initial and end calls implement the same outer-loop transition and could potentially be represented by one loop-top call plus a terminal guard. This is the clearest source-level duplication. Do not remove the refill after metadata release: releasing that slot can expose additional work before the first payload wait. Generated code must establish whether the present calls actually duplicate machine code and whether consolidating them improves it.
2. **Once-only PDL predicate checked per K:** `dependency_acquired` becomes permanently true after the first dependent stage, but its guard is written inside the K loop. A prologue could reduce repeated control only if it preserves initial metadata capture/release/refill ordering. Hoisting the wait directly after the first refill would shorten cross-tile prefetch. Producer-exit checks are less trivially movable because the fast cursor may finish during any refill.
3. **No proven redundant synchronization:** full-byte announcement, scale empty readiness, metadata acquire/release, gather relay, and terminal tails all protect distinct lifetimes. The vote cannot be replaced by a compiler uniformity assertion.
4. **`pending` is algebraically derivable from two global stage counts, but is not proven redundant machine state.** Currently unused PipelineState counts can disappear in DCE. Replacing one live pending counter with two live counts and subtraction may increase work. Similarly, recomputing K/tile from global counts adds divisions instead of removing state.

Both roles now independently compute the same per-work weight cache hint and source coordinates. That duplicates control relative to the old combined A+SFA producer, but sharing it would need additional publication/state or change cache policy; there is no demonstrated simpler replacement in this scope.

## A versus B

There is no structural state-machine advantage: FC1 has one simple producer plus one refill/relay producer in either variant; FC2 has two refill/dependent producers in both. A keeps the A announcer simple in FC1; B keeps SFA simple. In FC2, A groups A+B and SFA+SFB, while B groups A+SFB and SFA+B. This redistributes descriptor, byte and issue work without removing cursors or polling. B's few shorter terminal branches do not establish a performance or maintainability win; those differences mainly serve nondefault constructor combinations.

## Profile if timing regresses

Prioritize per-role registers/local memory, refill loop/test/vote/branch counts, repeated metadata probes at small K, duplicated cache-hint/source-coordinate work, and time between the first metadata release and payload wait. Then inspect whether an A/SFA owner stalls on dependent work while the opposite operand is ready. Preserve current stage/layout/tactic policies; do not hide regressions with shape-specific enablement. Neutral timing alone does not justify the extra state-machine complexity.
