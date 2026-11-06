# Full-prefetch weight FIRST / activation LAST experiment

Local source: `flashinfer-pdl-cache-tier-review`; separate unstaged copy based on frozen SFA-only candidate. Full patch `dddd7db2146b2f6acbcdbf6868a9d6248052c49da6c89b5cf8937a1801ad611b`, receipt `evidence/pdl-cache-tier-r1/source.json`; delta versus SFA-only is `sfa-to-tier.patch` there. Neither production nor the frozen SFA/integrated copies is modified.

- Adds direct private `activation_cache_policy`, default0, to the compile key/constructor and only the B payload TMA copy. FC2 host selects LAST with exactly the same actual-prefetch/oneCTA/k_steps8 admission as SFA FIRST. SFB remains normal (no cp.async assembly change); producer stores/combine/FC1/wide/default-false paths remain unchanged.
- This protects repeated FC2 activation reads from subsequent weight traffic after the first B read. It cannot protect FC1 output before that read and does not implement consumer retirement. This is different from the rejected historical FC2-store-LAST/combine-read-FIRST experiment.
- Scoped pre-commit and the eight-combination source-extracted admission proof pass. The same72 full-chain byte-exact replays pass. Named NV narrow PTX differs from integrated policy0 only in nine SFA FIRST and ten B LAST policy immediates; all other instructions, waits/barriers and arithmetic match.
- Fixed screen uses six arms C1-S1-A1-A2-S2-C2, where C is integrated full-prefetch, S is SFA-only, A is SFA+B-tier. Same model/format/GPU/tokens/timer as the SFA screen, same observer with actual public wiring. Both direct integrated/tier and SFA/tier ratios will be calculated from these medians, without multiplying ratios from another run.

Raw receipts/results and status: `evidence/pdl-cache-tier-r1-fixed/`. This is an experiment; no native AUTO retention or production integration yet.
