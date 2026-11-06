# Stream weights through L2 with one fixed priority

This independent experiment starts at82254e20. It removes the adjacent-expert
lookahead and uses evict-first for weight payloads and scales in every swap-AB
FC1/FC2 tile. Activation payloads retain evict-last. W4A16 already follows that
priority pairing and is not changed here. No new condition, tactic, argument,
barrier, stage, or numerical operation is introduced; the source diff is +2/-20.

This is a simplification hypothesis, not a predicted gain. The prior regular-TMA
implementation measured about8% prefill gains from the route-aware NORMAL/FIRST
weight policy (`optimization-20261027/cache-route/README.md` in the old project).
Do not erase that evidence. The new gathered FC1 reuses original input rows
across experts, and current V3 TP MX8 NCU shows2.162GB DRAM reads with62.77%
DRAM throughput. Its activation working set competes with reusable weights in
L2. Whether simpler streamed weights improve that whole-chain tradeoff is
unmeasured; lower route-metadata instruction count alone does not justify a
prefill regression.

First screen: fresh control/candidate codegen and exact calls, then a bounded
12-cell CAAC across V3/N3U EP/TP, standard/per-tokenNVFP4, MX4x8 andMX8,
tokens4/16384, using the existing frozen native choices and strict CUPTI harness.
If the old weight-reuse advantage persists, reject promptly. Broaden to all
four models and token bands only if the targeted screen is promising. Preserve
all negative rows. No GPU work may overlap the reserved distributed GLM5 run.

The main composed source remains frozen and unaffected by this review copy.
