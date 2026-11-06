# Fresh full exact/native qualification

Gate `914ce08b421017aeee20cc025f6cdc5fcaef0523a48a988d87cc8ee100de32e4` passes all 11 original signatures / 22 fresh exact calls / 33 native pairs on source `15d6eb18` and retained `c1ac8ce7`.

The adopted same-source release cohort uses `moe_utils` ELF `046552b8`; the other three C++ libraries and all four original Ninja descriptions are unchanged. Both actual private source arms passed normal native loads, exact library/build-description hashes, no-op, full source pre/post checks and fresh GPU release. The original wide pilot and stopped cache-path attempt remain separate; none of their exact calls is reused in this gate.

The controller completed in 144.7 seconds on eight disjoint GPU lanes. Canonical cache restoration took 371.0 seconds separately. All capture/oracle/resource helper bytes are unchanged from the planned continuation; only cache path binding/orchestration changed.

All native resource attributes match, including registers and LOCAL0. Driver CTA capacity is one before/after, not a measurement of achieved active residency. Stage count, bulk policy and compiler options are unchanged. Dynamic shared allocation includes the actual coordinate cache and alignment growth. The full 22 FC2/finalizer pairs are raw PTX/cubin/SASS identical in this fresh run; the historical wide FC2 descriptor renaming is not imported into this comparison.

| FC1 signature | Native MMA K / tile K | CTA / CLC | Stages | Shared bytes control → candidate | Non-NOP control → candidate | Added LDS128 sites |
|---|---:|---:|---:|---:|---:|---:|
| pilot-mx8-wide-g2 | 32 / 256 | 1 / False | 2 | 203520 → 204544 | 3691 → 3520 | 32 |
| pilot-nv-g4 | 96 / 256 | 1 / False | 9 | 222208 → 223232 | 1052 → 1087 | 1 |
| mx4-g1-control | 32 / 128 | 1 / False | 10 | 216064 → 216192 | 1212 → 1219 | 2 |
| mx8-g1-n256-control | 32 / 128 | 2 / False | 6 | 206720 → 207232 | 3646 → 3593 | 24 |
| mx4-g2-partial-k | 32 / 256 | 2 / False | 5 | 195456 → 195584 | 1347 → 1384 | 4 |
| pt-g4-partial-k | 96 / 256 | 2 / False | 10 | 226304 → 227328 | 1361 → 1402 | 2 |
| nv-g4-m512 | 96 / 256 | 2 / False | 4 | 189440 → 190464 | 3927 → 4000 | 16 |
| pt-g4-native-clc1 | 96 / 256 | 1 / True | 9 | 223232 → 223232 | 1239 → 1279 | 1 |
| nv-g4-native-clc2 | 96 / 256 | 2 / True | 10 | 227328 → 227328 | 1547 → 1591 | 2 |
| nv-g4-w8-n256 | 96 / 512 | 2 / False | 2 | 156672 → 157696 | 3507 → 3527 | 16 |
| pt-g4-w8-n256 | 96 / 512 | 1 / False | 2 | 222208 → 223232 | 3255 → 3141 | 32 |

SF async-copy site counts are unchanged in all signatures. The coordinate-cache loads remain hot-loop work; both source warp publication/reuse syncs remain required. Narrow G1 adds seven static instructions despite no SF-sector benefit; the larger narrow/full-M cases add up to 73. Wider cases remove 53, 114 or 171 static instructions. Extra SF row loads and predicates remain explicit in the JSON opcode records. These are code-generation observations, not a speedup claim.

The existing 56-cell T32/T16384 CAAC screen is the next authorized gate, with no retuning, W4 timing or new policy. Private roots and canonical generated/cubin identities are handed to the performance owner after qualification release.
