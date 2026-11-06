# Shared SF/payload metadata: typed gate passed

23 exactcases passed;44 generated kernels have zero STACK/LOCAL/LDL/STL and all21 FC2 cubins remain identical to retained475. Extra branches from the signed/XOR-permuted bound are gone. One active local review copy remains unstaged.

The wideN256 setup reduces instructions and metadata LDG sites; some N128 and narrowK8 cases add integer-address instructions despite fewer loads. A bounded fixed-tactic screen is warranted; codegen alone does not establish a performance gain.

| Index | N | CTA | Ksteps | Type | Gather-tail instructions | LDG | Branches | R2UR |
|---:|---:|---:|---:|---|---|---|---|---|
| 0 | 128 | 1 | 8 | Float4E2M1FN | 564→601 | 9→1 | 56→56 | 67→56 |
| 2 | 128 | 1 | 8 | Float4E2M1FN | 573→601 | 9→1 | 56→56 | 67→56 |
| 4 | 128 | 2 | 4 | Float8E4M3FN | 407→441 | 6→2 | 56→56 | 32→25 |
| 6 | 128 | 2 | 4 | Float8E4M3FN | 407→441 | 6→2 | 56→56 | 32→25 |
| 8 | 16 | 1 | 8 | Float8E4M3FN | 255→242 | 3→2 | 30→30 | 15→13 |
| 10 | 16 | 1 | 4 | Float4E2M1FN | 242→244 | 3→2 | 38→38 | 7→7 |
| 11 | 128 | 1 | 8 | Float4E2M1FN | 465→499 | 10→2 | 26→26 | 63→50 |
| 12 | 16 | 2 | 4 | Float4E2M1FN | 389→387 | 3→2 | 60→60 | 31→29 |
| 14 | 16 | 2 | 4 | Float4E2M1FN | 379→386 | 3→2 | 60→60 | 26→25 |
| 16 | 16 | 2 | 4 | Float8E4M3FN | 503→498 | 3→2 | 86→86 | 27→25 |
| 18 | 16 | 2 | 4 | Float8E4M3FN | 503→498 | 3→2 | 86→86 | 27→25 |
| 20 | 16 | 2 | 8 | Float4E2M1FN | 347→371 | 2→2 | 67→67 | 7→7 |
| 22 | 16 | 2 | 8 | Float4E2M1FN | 356→379 | 2→2 | 67→67 | 8→6 |
| 24 | 16 | 2 | 8 | Float8E4M3FN | 408→438 | 2→2 | 78→78 | 9→9 |
| 26 | 16 | 2 | 8 | Float8E4M3FN | 408→438 | 2→2 | 78→78 | 9→9 |
| 28 | 256 | 1 | 4 | Float4E2M1FN | 893→831 | 19→3 | 39→39 | 225→208 |
| 30 | 256 | 1 | 4 | Float4E2M1FN | 870→808 | 19→3 | 39→39 | 215→195 |
| 32 | 256 | 1 | 4 | Float8E4M3FN | 693→657 | 19→3 | 53→53 | 164→149 |
| 34 | 256 | 1 | 4 | Float8E4M3FN | 693→657 | 19→3 | 53→53 | 164→149 |
| 36 | 128 | 2 | 4 | Float4E2M1FN | 410→450 | 6→2 | 46→46 | 46→41 |
| 38 | 128 | 2 | 4 | Float4E2M1FN | 410→450 | 6→2 | 46→46 | 46→41 |
| 40 | 128 | 2 | 4 | Float8E4M3FN | 532→571 | 6→2 | 70→70 | 38→33 |
| 42 | 128 | 2 | 4 | Float8E4M3FN | 532→571 | 6→2 | 70→70 | 38→33 |

Counts are static from gather setmaxreg128 through common tail, not dynamic execution counts. Source kernel `dac7f44c8203c364a4bb0b2f945f5508ca1f4d97df35405582b9380a1be46812`, patch `7ef957625147f370697511557b04d31c1386614fd1140c1dc743018800555216`. Archive SHA `1e1fe1a8fc27d52cb16a72b0686b46b1a66b1355aa9440323a7df007337d1733`,147 files. Gates use uncached diagnostic compilation; timings use normal persistent caches and executable guards.
