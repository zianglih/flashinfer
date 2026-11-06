# Coalesced SF with warp-private payload coordinates: rejected

Candidate `15d6eb18` was rejected after the complete 56-cell screen: −0.014834% overall, −0.128760% at T32 and +0.099222% at T16384, with all 33 negatives retained. N3U TP W4A4 T16384 loses 4.687648% at normal clocks and tight repeats, while its EP arm gains 4.748737%. No source change was retained.

The original R1 coalesced SF mapping/Int64 offsets combined with warp-private shared payload coordinates passed 22 fresh exact calls and 33 native pairs in the adopted `moe_utils046552b8` cohort. Its two warp joins close publication and reuse; shared bytes were included in all existing planner paths. The unchanged Gather4 task order adds per-K LDS coordinate dependencies. The bounded paired NCU diagnostic is separate from the primary timing decision.

- [Full qualification](QUALIFICATION_RESULTS.md), [native results](NATIVE_RESULTS.md), [source proof](source-proof.json).
- [All 56 performance rows](PERFORMANCE_RESULTS.md), [decision](DECISION.md), [independent data peer](../../audits/sf-coordinate-cache-data-peer.json).
- [Paired NCU diagnostic](ncu-diagnostic/RESULTS.md), [cache recovery/cohort boundary](CACHE_RECOVERY.md).
- [Retirement receipt](retirement/receipt.json): exact source/patch/status checked before removing only this local review and branch. All remote snapshots/caches and local evidence/helpers remain. [Original design README](retirement/README-before.md) is preserved.
