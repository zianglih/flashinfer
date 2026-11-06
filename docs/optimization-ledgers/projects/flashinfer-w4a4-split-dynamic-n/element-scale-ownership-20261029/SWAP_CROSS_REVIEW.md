# Swap-AB producer ownership cross-review

Read-only review, 2026-10-29. Frozen source was not edited.

| Variant | Swap kernel SHA-256 | Ownership |
| --- | --- | --- |
| A | `02031c5fe86a2c40591272feb4953da113e8e345eaf7915b089ff411dba2b1c7` | Warp 0: A + FC2 B. Warp 1: SFA + FC2 SFB, or FC1 gather relay. |
| B | `15d9533fac47677348ea161edaeca850ce4b49e0130fe465808d1ec0c7ef6259` | Warp 0: A + FC2 SFB, or FC1 gather relay. Warp 1: SFA + FC2 B. |

Sources: `flashinfer-element-scale-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py` and corresponding crossed-producers review file; retained control `658a0c8942c7454050f990c0be3083aa61b6a89f`.

## Findings

No concrete correctness blocker found in the public FC1/FC2 call paths. This is a source/protocol review, not a substitute for current-hash runtime correctness, liveness, resource or performance results.

- **Barrier announcement:** `load_static_stage` (A lines 2523–2590) keeps exactly one operand-full announcer, the A-elements producer. Expected bytes remain CTA-group-size times the original A + SFA total and, for FC2, B + SFB total. The other producer only waits for the existing empty phase and issues its copies. FC1 gather completion still uses its existing local-to-cluster relay. One original operand tail remains on A; no second full arrival or second tail was added.
- **Metadata ownership:** The fast cursor copies metadata without releasing it; the dependent cursor copies and releases each item once before any payload/relay wait. The fast cursor caches tile/expert/cache hint while processing a K tile. Scheduler reuse therefore cannot alter a current fast item after the slow cursor releases it. The full-barrier phase bounds fast advancement even with one metadata stage; no extra queue or consumer arrival is needed.
- **Forward progress:** `pending` counts static stages issued by this role minus dependent stages issued by this role. Optional refill polls metadata/operand readiness only while pending work exists; it blocks only at pending zero, after all older dependent operations from this role have issued. The operand empty phase bounds lookahead even when K is one stage. Before a dependent stage is issued, the refill call either already has its static stage or blocks to issue that required stage.
- **Termination:** A negative fast cursor marks the observed sentinel/no remaining static work. Positive pending work drains before loop exit. CLC terminal metadata is released once by the slow cursor after the fast cursor observes it; an empty-work CTA follows the same single terminal release. Static scheduling has no terminal metadata obligation.
- **PDL:** FC2's static A/SFA issue runs before its first dependent wait. Each dependent producer waits before B/SFB use. Startup publication follows the gather-relay/SFB owner when ownership moves, while producer-exit publication and the original tail stay with A. Empty-work CTA fallbacks preserve dependency acquisition/publication. The public host continues to select FC1 startup and FC2 producer-exit signals.
- **One/two CTA:** The original CTA-group byte multiplier, B coordinate partition, SFB row-block addressing, gather peer arrivals and leader-side MMA/full-barrier protocol remain intact. Producer reassignment does not add a leader condition to the SFA copies or alter group transaction volume.
- **Uniform readiness:** Both new refill-control predicates use `vote_all_sync(test_wait(...))` before branching/cursor advancement. This is essential because raw per-lane readiness cannot safely control elected copies or shared warp cursors. Blocking required-stage waits remain ordinary acquire/wait operations.

## Retention considerations

Both variants add a second metadata cursor, a pending count and per-K readiness/vote control. They preserve one existing stage lifetime and metadata ring rather than introducing a separate framework. The difference is which producer's static work shares progress with the dependent operation/FC1 relay; a blocked dependent role cannot refill static stages that become ready after it enters the wait. Compare source simplicity, resource pressure and measured performance; activation of an idle SF warp alone does not establish a gain.

## Benchmark harness cross-review

Reviewed `harness/run_perf.py`, `guard_observer_adapter.py`, the relevant observer/guard portions, and A/B `triage/perf-config.json`. No stale source/provenance blocker found.

- Both configs contain 31 jobs / 72 cells at tokens 4 and 4096, for the supported EP/TP combinations. Variant source seals match all four current swap/W4 kernel hashes; observer dependency hashes match.
- Driver verifies retained base 658a plus tracked source contents, C-A-A-C phases on the same GPU UUID, frozen native winners and route identities, zero fresh tactic profiling, unchanged managed caches, exact recorded median agreement, 100 positive CUPTI samples and runtime register guards.
- Observer verifies selected backend labels and the requested quantization timing contract; requires graph timing, cold L2 and CUPTI without event fallback. Wrapper only observes native timing and does not substitute a timing implementation.
- Persistent compiler/driver storage under the earlier integration directory is deliberate cache reuse; source paths are rebound to the current frozen experiment copies.
- The new 900-second process-group watchdog changes timeout/failure handling only. The driver records its own helper hash separately from observer hashes.

No files in either source worktree or the frozen benchmark capture were changed by this review.
