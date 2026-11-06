# Mixed Gather4 row-count specialization

`branch-hoist-cache48.patch` is an off-tree incremental patch against `cache48-prefix.patch`. The complete kernel is under `branch-hoist-proposal/`. Production V6 is unchanged.

## Evidence and change

Root's SASS audit confirms mixed row-count guards remain inside K: N128 branches around the fallback-only suffix; N192 retains per-group guards. The candidate moves this selection to one explicit `active_cluster_m == 4` / `elif == 2` dispatch per routed tile. Other values assert, matching the launcher-supported physical sizes.

Only the Gather4 K loop moves into `_load_gather_tile`. `rows_per_cta` and `cached_rows` are compile-time parameters. Its row-group range and destination-row multiplier are therefore static, while pipeline/state, source rows, destination storage, issuer and physical multicast mask are passed through. Uniform tactics call the same helper once with their already-static geometry.

## State and cached-row contracts

- The helper resets only the per-tile producer count, then acquires, issues, commits and advances exactly once for each K tile. It explicitly returns the resulting `PipelineState`; the caller keeps its index and phase across routed tiles. This follows the existing `_transform_tile` return pattern.
- PDL, routed metadata acquisition/release, mapping loads, index conversions, election, pipeline construction and producer-tail remain in their existing locations. No CTA/warp role or synchronization protocol changes.
- The helper cache length is `min(outer_cached_rows, physical_rows)`. For N128 preferred4 the outer allocation is48 but only32 entries are initialized, and the helper uses exactly32. Fallback2 uses48 cached entries and64 total rows. N192 uses48 cached entries in either branch, with48 or96 total rows.

## Expected tradeoff

Runtime guards and dynamic destination-row scaling leave the K loop. Source-row shuffles follow the existing cache48 policy; this change does not promise to remove `R2UR`/`UMOV` operand packing. The generated binary now contains separate preferred/fallback K loops: N128 has32+64 static Gather4 sites, and N19248+96, compared with64 or96 in the shared guarded body. The larger producer code may affect instruction-cache behavior, so compare actual SASS and forced mixed timings.

Root's current codegen results already show why source counts alone are insufficient: cache48 reduces uniform N128 row shuffles but increases hot-loop total instructions454→480/482 through operand packing, while uniform N192 drops966/1012→682/690. Full96 mixed N192 spills220 bytes locally. These are reported codegen results from root, not measurements produced by this helper preparation.

## Local checks

Python syntax, Ruff, and patch application against the cache48 snapshot pass. Structural checks confirm explicit PipelineState return, absence of runtime cluster-width/count variables inside the helper, and initialized cached-prefix bounds for both physical widths and N128/N192. GPU compilation, exactness, SASS and timing remain pending.
