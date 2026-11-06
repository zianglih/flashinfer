# Fixed normal weight-cache priority

Same independent base82254e20 and 12-cell screen as `../stream-weights`.
Remove route-neighbor metadata reads and select the default NORMAL TMA cache
priority unconditionally for weights and weight scales. Activations retain
EVICT_LAST. No new condition, tactic, public/private argument, barrier, pipeline,
or numerical operation. +0/-20 lines; the existing copy API supplies its default.

The earlier route-aware policy found useful weight reuse for prefill. This arm
keeps NORMAL priority for reused weights while removing runtime cache-policy
selection overhead for all tiles. Whether abandoning FIRST for unreused weights
hurts activation residency is unmeasured. Compare the whole chain against822,
retain all negative rows, and broaden only if the bounded screen qualifies.
Do not introduce model-specific policy selection to rescue either constant arm.
