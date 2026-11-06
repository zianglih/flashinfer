# Retained-head EP/TP refresh complete

- Source: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`, clean and pushed.
- 15 workers / 30 passes / 468 cases / 936 medians / 93,600 strict CUPTI samples. Saved external controls and83df winner caches/routes reused unchanged.
- Source, timing, route/cache, raw CSV, tables, plots and publication independently verified. See `RESULTS.md`, `scheduler-*-review.json`, and `publication/publication.json`.
- PR #7290 contains fresh EP/TP tables, both immutable heatmaps and all15 fresh native A2 blocks. Body readback is exact.
- Retained cleanups are near-neutral in scoped timing. Significant TP prefill gaps remain; no broad performance-win claim.
- No sanitizer or broad pytest rerun this iteration. No active experiment/GPU work remains. Persistent native caches and all helpers/evidence preserved.
