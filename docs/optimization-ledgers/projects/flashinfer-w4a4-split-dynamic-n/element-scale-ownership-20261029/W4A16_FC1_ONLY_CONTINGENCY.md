# W4A16 FC1-only ownership contingency

Read-only design, 2026-10-29. No third workspace or source edits. Retained base `658a0c89`; frozen A `0ba17644` and B `b29cce29` remain unchanged.

**Recommendation if FC1 gains survive but FC2 regresses:** keep the original FC2 activation producer intact and share the original raw-weight producer loop between compile-time roles. This needs no new argument, tactic, queue, polling or fast cursor.

| Existing compile-time path | Warp 6 | Warp 7 |
| --- | --- | --- |
| `gather_input=True` | A elements; sole raw-full announcer and tail | SFA only; raw-empty wait and copy |
| `gather_input=False` | Original A + SFA producer | Original B producer, including its original PDL wait/signal |

`gather_input` expresses the actual absence/presence of the regular B stream; this does not introduce a model-, dtype-, shape- or FC-name-based policy.

## Minimal source structure

- Leave base lines 1715–1817 (regular B producer) unchanged.
- Wrap the existing raw-weight producer (base lines 1819–1920) in a compile-time role iteration of size two for gather and one otherwise. A `scale_only` constexpr role selects warp 7 versus warp 6. Metadata acquisition/release, work-tile traversal and K traversal remain one shared source body.
- Compile A slice/issue, raw `producer_acquire/commit`, original PDL publication and original tail only for the non-scale-only role.
- Compile SFA slice/issue when `scale_only or not gather_input`. The scale-only role waits for the existing raw-empty phase without announcing another transaction or committing another arrival.
- Change the existing metadata consumer count to `threads_per_cta - 32`: FC1 adds its now-active scale warp; FC2's count is unchanged.
- Keep role attributes, register targets, gather WG position, stage counts, CLC/static scheduler and all pipeline storage/byte counts unchanged.

For FC2 the role iteration has one compile-time iteration, all selection guards fold away, and the old two independently progressing producer loops remain. For FC1 there are two independent metadata consumers with the same raw stage progression; A+SFA still complete one existing full barrier. The A tail protects shared storage until both contributions have been consumed.

## Scope and review cost

Estimated logical addition is roughly 25–45 lines of compile-time role selection/guards plus the consumer-count simplification, with no added helper API. Actual `git diff` would show more changed lines from indenting the existing approximately 100-line weight block; this is an estimate, not an implemented patch.

A smaller textual-diff alternative is a new FC1-only SFA loop (approximately 55–75 lines) plus guards around SFA in the old weight loop. It keeps more existing indentation but duplicates the metadata/K traversal and scale-slice setup. Prefer the shared constexpr-role loop for implementation simplicity unless the reindent materially hurts review.

This contingency removes all FC2 two-cursor metadata state, global issued-count comparisons, optional test/vote polling, per-stage refill and empty-work PDL helper additions from A/B. It retains only the independently useful FC1 role split. No performance claim follows from the design: compare the already collected FC1/FC2 stage evidence and then validate any authorized implementation.
