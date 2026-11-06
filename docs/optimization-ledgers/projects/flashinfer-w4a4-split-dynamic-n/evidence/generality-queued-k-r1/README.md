# Queued-K capacity candidate

This experiment evaluates both supported K-step sizes against actual staged operand bytes, metadata, epilogue scratch, TMEM capacity, and minimum ring constraints. It maximizes `tile_k * feasible_num_stages`, preferring larger K on a tie. Explicit K or stage-count overrides remain authoritative. There is no dtype/model/token branching and no tactic/API change.

The constructor has no actual reduction dimension. The policy therefore ranks maximum feasible cross-tile buffering; it does not claim that every stage is useful for a short reduction. The existing inline-epilogue reduction cap still applies later during storage configuration. This is a performance candidate, not retained code.

`cpu-census.json` exercises 1,320 automatic choices and proves 2,640 explicit-override resource plans unchanged. All automatically selected capacities are nondecreasing. It uses actual source planning methods with previously SDK-validated byte-layout stubs, not a GPU test.

Notable consequences:

- MX FC2 M256/N256 recovers K128 x 5 (640 queued K) instead of K256 x 2 (512).
- MX FC2 M256/N128 recovers K128 x 7 (896) instead of K256 x 3 (768).
- NVFP4 M128/N16 and N32 switches K512 x 4 -> K256 x 9. The increased instruction count may offset buffering, so decode must be measured.
- MX FC1 M256/N128 also switches K256 x 4 -> K128 x 9. The fixed FC2 diagnostic does not establish the performance of that separate change.

`source.json` is the integration-only snapshot: queued-K atop the generalized PDL, deduplicated planner, cluster-scoped narrow-CTA join and contemporaneous quantizer. Only `_select_k_steps` differs from `before.py`; `queued-k-only.patch` records it. Scoped pre-commit passed before the core was handed back for the next isolated admission experiment.

For causal performance attribution use `../generality-queued-k-isolated-r1/source.json` instead. It changes only `_select_k_steps` atop frozen planner `a9ef37a8`. A temporary private Git index/object directory produced the canonical patch; every other source hash and patch section is unchanged. `isolation-proof.json` checks 960 resource plans against the integration candidate on all previously admitted geometries. It excludes later narrow admission, planner deduplication, quantizer revisions and tactic expansion.
