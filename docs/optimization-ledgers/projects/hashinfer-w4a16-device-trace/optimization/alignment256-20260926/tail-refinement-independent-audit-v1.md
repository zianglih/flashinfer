# Tail-refinement fixed-diagnostic audit

PASS: both candidate sources, command/fixture/output hashes, four-rank reference checks, native SM103a artifacts and zero-spill signatures. No performance-retention claim.

| Source | BF16/worker | Span instructions/16 outputs | Score LDG/16 | Span includes scores | Span plus score LDG/16 | Whole kernel | Non-NOP |
|---|---:|---:|---:|---|---:|---:|---:|
| before | 8 | 294.0 | 4 | False | 298.0 | 5128 | 5014 |
| late-all96-candidate | 16 | 280.0 | 2 | False | 282.0 | 5256 | 5139 |
| late-no-prefetch-candidate | 16 | 287 | 8 | True | 287 | 5224 | 5107 |
| late-participant96-candidate | 16 | 280.0 | 2 | False | 282.0 | 5256 | 5138 |

Every candidate has REG96, STACK0, LOCAL0, no native LDL/STL, and no PTX local loads/stores. Each arm produces identical PTX/CUBIN/SASS across all four ranks. Both retain eight native256 route loads plus one native256 output store per16 BF16 outputs; all arms execute normalized FMUL2=8 and FFMA2=56 in the reducer.

The no-prefetch PTX has one scalar score read per route. Native scheduling hoists several score reads; it does not preserve a strict just-in-time score load order. Exact load PCs, pointers, offsets and issue order are recorded in JSON.

These are fixed-tactic source/codegen/numerical diagnostics, not native AUTO or retention timing.
Normalized instruction counts compare equal16-BF16 outputs per lane and are static estimates, not measured dynamic instructions.
WG maps are exact-binary static CFG/fixture predictions; unresolved maps are explicit and do not imply no spills.
Score-prefetch PTX/SASS checks bind the final initial-preparation site and next-worker site; dynamic execution depends on worker ownership.
No-prefetch span includes eight scalar score loads; vector-prefetch spans exclude their score loads. Compare explicit span-plus-score counts, not raw spans alone.
Span-plus-score counts add only score LDG instructions outside the span; initial address setup and subsequent loop progression remain excluded. Whole-kernel counts are static, not a runtime-speed prediction.
