# Swap elements/scales producer split

R0 is an intermediate source snapshot. Its raw readiness predicates are replaced by warp-wide nonblocking tests in R1; do not qualify R0 for launch.

The existing MMA, epilogue and Gather4 warp trees are AST-identical. The constructor changes only internal warp role names. No shared storage, stage count, barrier consumer count, layout, tactic or public API changes.

## Cursor and lifetime invariants

- `producer` and `cursor` identify the next independent A/SFA stage. `dependent` identifies the next B/SFB or FC1 gather relay. `pending` is the number of already-issued independent stages not yet paired with this warp's dependent work. Therefore `pending > 0` before every dependent issue, and both cursors advance exactly once per logical K stage.
- The fast metadata cursor waits/reads/advances without releasing. The dependent cursor reads its tile fields into registers and releases exactly once, before payload/relay waiting. At that point `pending > 0` proves the fast cursor has already cached that tile. Fast tile/expert/cache-hint values survive later metadata overwrite in registers. No new shared queue is needed.
- With pending work, refill only tests readiness. A failed future-metadata or empty-stage test returns to dependent issuing. With `pending == 0`, all this warp's older dependent work has issued, so blocking on its next independent stage cannot depend on this same warp issuing an omitted older operand. The independent stage capacity bounds lookahead, including K smaller than capacity and crossing work tiles.
- CLC's final sentinel is read by the fast cursor and released once by the dependent cursor. Empty-work CTAs follow the same rule. Static scheduling derives the unchanged block/grid sequence and has no metadata barrier operations.
- Only the elements role announces the full operand byte total. Scales observes the same empty phase and targets the same full barrier without an arrival. The byte expression is unchanged. A/SFA completion can run ahead of B/SFB or the gather relay, but the full/empty phases remain owned by the existing MMA release.
- B descriptor/partition construction remains once per work tile outside the K loop. Gather4/SF copying and the local-to-cluster relay instructions are unchanged; only SFA refill precedes the relay wait.

## PDL boundaries

FC1 keeps the existing startup dependency wait and scales-warp publication. FC2 lets both producers fill currently available A/SFA stages before their first dependent payload wait. Elements announces `producer_exit` as soon as its independent cursor finishes and the dependency has been acquired, even if B stages remain. Empty work still acquires/publishes the required dependency. Existing final MMA/scheduler dependency waits and CTA/TMEM teardown remain unchanged.

## Remaining qualification

The source has more cursor control than the baseline (+228 lines in R0 before the readiness correction), so performance and register costs must be measured rather than inferred from ownership. Required boundaries are CLC metadata depth 1, tiny K shorter than stage capacity, repeated work tiles, zero/one/many work items, 1/2 CTA, PDL off/on, and all existing dtype/K-tail modes. No GPU run was launched by the source owner.
