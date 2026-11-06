# Shared SF/payload metadata v1: gate failed

23 exactcases passed, but do not benchmark this version. Two N256/oneCTA/K4 FP4 instances introduce8B stack/local instructions. Other42 instances are spill-free; all21 FC2 cubins remain identical to retained475.

Static gather-tail code also grows despite fewer metadata LDGs. The scope runs from gather setmaxreg128 through common kernel tail; counts are static and not measured execution costs.

| Index | N | CTA | Ksteps | Type | Instructions | LDG | Branches | R2UR | Candidate stack/LDL/STL |
|---:|---:|---:|---:|---|---|---|---|---|---|
| 0 | 128 | 1 | 8 | Float4E2M1FN | 564→847 | 9→1 | 56→64 | 67→148 | 0/0/0 |
| 2 | 128 | 1 | 8 | Float4E2M1FN | 573→847 | 9→1 | 56→64 | 67→148 | 0/0/0 |
| 4 | 128 | 2 | 4 | Float8E4M3FN | 407→472 | 6→2 | 56→60 | 32→25 | 0/0/0 |
| 6 | 128 | 2 | 4 | Float8E4M3FN | 407→472 | 6→2 | 56→60 | 32→25 | 0/0/0 |
| 8 | 16 | 1 | 8 | Float8E4M3FN | 255→250 | 3→2 | 30→30 | 15→15 | 0/0/0 |
| 10 | 16 | 1 | 4 | Float4E2M1FN | 242→250 | 3→2 | 38→38 | 7→7 | 0/0/0 |
| 11 | 128 | 1 | 8 | Float4E2M1FN | 465→753 | 10→2 | 26→34 | 63→139 | 0/0/0 |
| 12 | 16 | 2 | 4 | Float4E2M1FN | 389→392 | 3→2 | 60→60 | 31→29 | 0/0/0 |
| 14 | 16 | 2 | 4 | Float4E2M1FN | 379→387 | 3→2 | 60→60 | 26→24 | 0/0/0 |
| 16 | 16 | 2 | 4 | Float8E4M3FN | 503→503 | 3→2 | 86→86 | 27→25 | 0/0/0 |
| 18 | 16 | 2 | 4 | Float8E4M3FN | 503→503 | 3→2 | 86→86 | 27→25 | 0/0/0 |
| 20 | 16 | 2 | 8 | Float4E2M1FN | 347→388 | 2→2 | 67→67 | 7→8 | 0/0/0 |
| 22 | 16 | 2 | 8 | Float4E2M1FN | 356→388 | 2→2 | 67→67 | 8→8 | 0/0/0 |
| 24 | 16 | 2 | 8 | Float8E4M3FN | 408→442 | 2→2 | 78→78 | 9→9 | 0/0/0 |
| 26 | 16 | 2 | 8 | Float8E4M3FN | 408→442 | 2→2 | 78→78 | 9→9 | 0/0/0 |
| 28 | 256 | 1 | 4 | Float4E2M1FN | 893→1437 | 19→3 | 39→55 | 225→352 | 8/8/1 |
| 30 | 256 | 1 | 4 | Float4E2M1FN | 870→1432 | 19→3 | 39→55 | 215→347 | 8/5/1 |
| 32 | 256 | 1 | 4 | Float8E4M3FN | 693→1027 | 19→3 | 53→61 | 164→248 | 0/0/0 |
| 34 | 256 | 1 | 4 | Float8E4M3FN | 693→1027 | 19→3 | 53→61 | 164→248 | 0/0/0 |
| 36 | 128 | 2 | 4 | Float4E2M1FN | 410→477 | 6→2 | 46→50 | 46→39 | 0/0/0 |
| 38 | 128 | 2 | 4 | Float4E2M1FN | 410→477 | 6→2 | 46→50 | 46→39 | 0/0/0 |
| 40 | 128 | 2 | 4 | Float8E4M3FN | 532→639 | 6→2 | 70→78 | 38→31 | 0/0/0 |
| 42 | 128 | 2 | 4 | Float8E4M3FN | 532→639 | 6→2 | 70→78 | 38→31 | 0/0/0 |

A liveness-only follow-up defers Int64 SF-offset and shared-offset formation until the payload cache is complete. V1 source/evidence stays immutable. A separate potential simplification is testing the original linear task eligibility before the row permutation; no such change is included in v1 or the liveness-only follow-up.

Archive SHA `c386a2c1d43602f878b24302e38cd50f8058c2cb08b8bda5061a19856e5be4f1`,147 files. No performance data was collected.
