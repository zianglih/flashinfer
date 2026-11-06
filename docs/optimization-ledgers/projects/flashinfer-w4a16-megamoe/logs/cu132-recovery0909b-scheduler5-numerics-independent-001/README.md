# Scheduler5 reference numerics passed

All five original saved validators pass once: **18 rank-tests, 54 test-phase reports and 72 compiled objects**. Every observed kernel and scheduler-params depth is5; configNone resolves to that source default. All72 raw depths are5, with REG96 /640 threads /two decode groups /pool61440 /local0.

| Geometry / EP | Rank-tests | Objects | Result SHA prefix |
|---|---:|---:|---|
| m256n64-c2-ep1 | 2 | 8 | 04bb4e78 |
| m256n64-c2-ep2 | 4 | 16 | 2a587943 |
| m256n128-c2-ep2 | 4 | 16 | 61409bb2 |
| m128n64-c1-ep2 | 4 | 16 | 79072b13 |
| m128n64-c2-ep2 | 4 | 16 | 005b544b |

Actual allocation observations from the original CuTe fitter trace:

| Tile | H / I / E | Objects | Control bytes | Total bytes |
|---|---|---:|---:|---:|
| M256/N64/K256 | 256 / 256 / 4 | 18 | 480 | 127616 |
| M256/N64/K256 | 288 / 448 / 4 | 6 | 480 | 127872 |
| M256/N128/K256 | 256 / 256 / 4 | 12 | 464 | 160256 |
| M256/N128/K256 | 288 / 448 / 4 | 4 | 464 | 160512 |
| M128/N64/K256 | 256 / 256 / 4 | 24 | 480 | 160384 |
| M128/N64/K256 | 288 / 448 / 4 | 8 | 480 | 160640 |

Each full observation retains actual control/communication alignment, all packed-A/scale/B byte counts, raw/B/decoded layout depths and TMEM/accumulator counts. The original validator checks deepest-fitting raw5, actual S5 kernel/params agreement and source allocation reconstruction. Control480 B appears56 times; control464 B appears16 times on N128. These are observed layouts at the successful reference shapes, not whole-domain stage5 admission.

Both returns keep the unchanged ordinary empty/refill, H288/I448/M257 partial-K, exact scale/routing and stable/changed graph assertions. The separate large-H S3-accepted/S5-over-capacity boundary remains unexecuted by this numerical subset.

Original83083 exits0 with exact UUID1add7c9d030a4c02b06fe62049b62360 and all five ordered completion paths; final fetch4573 closes0. Summary SHA `70d84f34d140cadbd0ca509e14f20381ffa2b47d1e7299728ba70ad61ff6c5ac`; launcher SHA `6602ea0926c2025e1c9734eed20279b8225a0564782440fed360f97b7f5f3196`.

Exact source8f116a49, runtime7dd9eb3c and preflight2eb7cd3c, 59 summary evidence files and108 direct hashes pass. All five saved native before/after inventories remain byte-identical055618ec, including22 entries and the JIT log. No live hostname/cache/native lookup or baseline recursion was performed.

The first staging alias failure is separately preserved as transport-only; no numerical attempt occurred there. AUTO performance and retention remain independent and may proceed alongside this saved audit.

[Audit JSON](audit.json), SHA `3f1cf7c7a374e70d739b1395475dd3d50de620247cff3721121937c926d4ef05`, retains every direct evidence hash and the complete observed allocations. [Original-validator output](validation-check.log) is saved alongside it.
