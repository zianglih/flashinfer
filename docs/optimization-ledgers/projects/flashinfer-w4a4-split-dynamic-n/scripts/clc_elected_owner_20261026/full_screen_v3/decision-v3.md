# V3 helper-isolated elected ownership: reject

All 48 points passed source, cache, six-field True/True tactic, routing, PDL, label and raw100 checks. Opening controls are exact same-GPU/source/tactic final controls from the completed V2 screen; each is followed by fresh V3 candidate/candidate/control. Reused control path, source receipt, raw result hash, and timestamps are recorded and validated. No V2 candidate timing is reused.

Control/candidate geomean: **0.98316x overall, 0.99485x decode, 0.97160x prefill**. Per-model V3 0.98405x, V4.1-Flash 0.98903x, K3 0.97643x. All twelve model/backend aggregates are slower. 41/48 points are slower by paired median and 39/48 are slower in both temporal comparisons. Maximum absolute opening-to-closing control drift is 5.26%; isolated tiny differences are not conclusive.

V3 solves the compiler dominance failure and removes V2 query peeling, but the tested owner-loop policy remains slower than the existing full-warp scheduler. Static instruction count remains +197 summed over 32 core variants, with some register increases and no local-memory spills. The user allows neutral instruction cleanup, but this candidate neither reduces overall static code nor demonstrates a useful timing benefit. No production commit or PR performance update is justified.

The source-bound local audit and benchmark evidence are preserved. The rejected local review clone was removed after exact96cf source verification; see `../local-source-cleanup.json`. No timing rerun is needed to establish rejection.
