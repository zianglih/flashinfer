# Narrow two-CTA follow-up audit

Read-only audit against clean `0c1e00fc3e4f913c8c241796c70a29673737c542`. No two-CTA change is included in the reuse candidate.

- The earlier `scripts/decode_geometry_experiment/RESULTS.md` campaign tested two-CTA M256 at logical N16/32/64 with physical N at least64. All162 paired exact cases passed, but sparse phase timings lost versus one-CTA overlapping epilogues: homogeneous formats were roughly neutral to2% slower, mixed roughly4–6% slower in the32-expert examples. Those results used Gather4, V3-sized K, B200 and the older fixed-stage implementation. They are evidence against blindly repeating that implementation, not a proof about regular TMA/B300.
- `decode_trial/small_core.py` used `allocated_n=max(32*cta_group_size, route_tile)` and retained an additional `PipelineAsyncUmma` SF-publication relay. Both CTAs waited on their cp.async completion, fenced generic→async shared visibility, and only then allowed the leader to issue scale copies/MMA.
- Current `PipelineCpAsyncUmma` still supports grouped release, but its async-load completion is CTA-local. The current core removed the unreachable relay when supported two-CTA tactics exclusively used bulk-TMA SFB. Its non-TMA SF consumer fence is explicitly one-CTA only.
- Therefore adding narrow two-CTA tactics now requires a deliberate SF-publication design as well as admission/layout changes. Merely adding entries or widening `can_implement` is insufficient. A bulk-SFB alternative would need to account for narrow logical route starts inside128-row scale atoms.
- Keep this follow-up deferred until the one-CTA channel-reuse and pipeline profiles establish a remaining opportunity. The current candidate reuses B/SFB inside one CTA and introduces none of these cross-CTA requirements.
