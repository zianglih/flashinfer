# Bounded physical CLC tickets with balanced runtime work

Isolated experiment implemented;96-replay source-paired exact gate passed. Fixed-tactic three-arm performance screen is running. No retention claim.

## Motivation and prior evidence

The fresh V41 mixed T16384 diagnostic has235 live N128 route tiles but863 allocated route slots. Existing CLC cancels every padded slot: FC2 has4,700 real work clusters and17,260 physical tickets. Same-geometry CLC loses overlap and lowers FC2 tensor activity despite less DRAM traffic and slightly fewer total instructions. See `perf-general-20261026/v41-mixed-prefill-diagnostic/README.md`. This establishes a structural opportunity, not proof that padded cancellation dominates.

W4A16 history at `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:2506` rejected fixed2/4-route bundles because the coarser balancing cost outweighed query reduction; later one-slot queues and acquire-before-cancel improved results. This experiment must preserve one metadata slot and avoid reserving a whole future group before the current group has been dispatched. It must be rejected promptly if fixed control comparisons reproduce those losses.

## Mapping

Let R be the existing occupancy bound in complete CTA groups: `max_active_clusters // cta_group_size`. Let S be the existing tile-info ring depth (one in production). Use a bounded physical ticket count Q=R×(1+S), with launch grid `(Q×cta_group_size,1,1)`. This is a first experiment with one current resident wave plus the existing scheduler lookahead; it is not a claim that two waves are optimal. It adds no model, dtype, route-count or dimension threshold.

The live logical work count is T=`num_tiles[0]×total_m_tiles`, using the existing published routing metadata contract. For each physical ticket j, compute once:

```
b = T // Q
r = T % Q
start = j*b + min(j, r)
end = start + b + (j < r)
```

Publish logical work `start … end−1` in the existing route-major order. The number of route/channel tiles remains unchanged; only ownership changes. These balanced contiguous groups differ in size by at most one and keep all intermediate products/endpoints within T, avoiding an extra overflow corner from `j*ceil(T/Q)`. Q is a compile-time occupancy/depth constant.

## Coverage and lifecycle proof

- Ticket0 starts0. Each interval ends exactly where the next begins. Ticket Q−1 endsT. Therefore every logical tile0…T−1 appears exactly once, independent of cancellation order.
- Both CTA ranks map to ticket `work.tile_idx[0] // cta_group_size`, because the installed CLC scheduler adds the rank to the same cluster-aligned X coordinate. Grid Y/Z are one. Both CTAs therefore publish the same work sequence and retain their original local channel offset.
- The scheduler keeps publishing one tile at a time through the unchanged one-slot queue. It acquires the queue slot before preparing each tile. It requests the next CLC ticket only at the current group’s final tile, after that acquisition, and overlaps the response with final-tile publication/work. It does not acquire a whole future group on entry.
- An empty interval does no operand prefetch and publishes no work. It still cancels another ticket until the hardware reports exhaustion. With T=0, all intervals are empty and each resident scheduler eventually publishes the existing single terminal−1 entry.
- Exhaustion publishes−1 exactly once per resident cluster and the existing all-role metadata consumers release it before teardown. CLC response producer/consumer tails remain unchanged; only the frequency of requests changes.
- The initial weight-prefetch tile is the initial ticket’s `start`, with the same interval-validity predicate. The producer’s existing `tile == first_tile` skip applies only to that tile. Later cancelled groups acquire all operand stages normally. Initial preload still reads A/SFA only; B/SFB remain after the payload dependency wait.
- Routing count publication already precedes the current pre-wait weight path. The experiment must preserve the existing prerequisite release/signal contract and read the same immutable count for initial prefetch and post-wait scheduling. No new payload access may move before the wait.
- Static scheduling is untouched. Reduced-SM reservations keep their existing static fallback. Because the CLC physical grid is bounded X with Y=1, the former capacity-derived grid-Y fallback becomes irrelevant and may be removed only in this experimental copy.

`mapping_proof.py` checks212 boundary configurations, including zero work, partial groups, Int32 maximum, arbitrary ticket order and both CTA ranks. This is CPU algebra only; it does not prove the CLC/pipeline implementation.

## Gate and screen

1. Independent source clone based on the current all-CLC candidate; leave unstaged, pin full diff/source before GPU work.
2. Reuse the existing task-local source-paired scheduler exact gate: NVFP4, per-token NVFP4, MXFP8, mixed; PDL on/off; one/twoCTA; N16/N128; changing/skewed/empty/reactivated routes; persistent multi-group work. Extend only task-local diagnostic cases to force multiple complete work groups and final partial intervals. No upstream tests.
3. Fixed V41 mixed T16384 at the traced geometry, with current static, old all-CLC and bounded CLC, public10warmup100cold-L2 CUPTI and paired repetitions. Record native-cache override as diagnostic; do not claim AUTO selection.
4. Before broad tuning, bounded decode checks for V3/V41/K3 and all affected formats. Historical coarse-bundle regressions are the stop condition. Keep static/current-CLC comparisons separate from the parent’s independently tested elected-publisher optimization.
