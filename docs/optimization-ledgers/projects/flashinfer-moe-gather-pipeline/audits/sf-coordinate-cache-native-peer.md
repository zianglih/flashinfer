# SF coordinate-cache wide pilot: independent native review

**Pass for the next existing exact/native matrix; no performance or retention conclusion.** Source `15d6eb18` resolves the prior wide coalescing spill while reducing static instruction work. If the remaining existing correctness/resource cases pass, the held 56-cell screen is justified.

Bound inputs and all six loaded-image records are in [the peer receipt](sf-coordinate-cache-native-peer.json). Independently checked all 18 PTX/cubin/SASS hashes, both exact results, source/cache closure and the emitted instruction streams. Captured scope is **MXFP8, SF32, G2, N256/K256, one CTA, actual static scheduling, PDL enabled**. The smoke-case CLC request does not make this capped capture an actual CLC case.

| FC1 fact | Control | Candidate |
|---|---:|---:|
| Whole-kernel non-NOP sites | 3,691 | 3,520 |
| Gather K mainline non-NOP sites | 352 | 296 |
| Gather4 sites per K mainline | 32 | 32 |
| SF 4-byte LDGSTS sites | 4 | 4 |
| Coordinate LDS.128 sites inside K | 0 | 32 |
| SHFL.IDX | 64 | 0 |
| R2UR / R2UR.FILL | 289 / 24 | 256 / 8 |
| LDG.E | 13 | 15 |
| Registers / driver LOCAL bytes | 168 / 0 | 168 / 0 |
| Dynamic shared bytes | 203,520 | 204,544 |
| Driver active-CTA capacity | 1 | 1 |

The candidate's coordinate stores at `0xbfa0/0xbfb0` precede K. Its 32 elected `LDS.128` instructions at `0xc640–0xd420` are inside the `0xc220–0xd4b0` loop. Each reuses `R4–R7`, then transfers four coordinates to uniform registers before the corresponding Gather4 issue. The compiler did **not** hoist the shared array back into 64 persistent coordinate registers. The two 16-packet rounds preserve the existing row/K task order. Mainline counts exclude out-of-line blocking waits; whole-kernel count changes also include scheduling/uniformization changes outside this loop.

Each elected aligned 16-byte coordinate load accesses four consecutive banks, without inter-lane conflict in that instruction. This is a source/address and active-lane observation, not a measured wavefront or throughput result. Coalesced G2 SF copies retain two distinct destination words per bank in the canonical layout. Fewer per-instruction SF sector requests do not imply fewer unique bytes or lower DRAM traffic. New per-K LDS dependencies and uniform-register transfers remain costs to measure.

Both publication/reuse `bar.warp.sync` operations remain in PTX (lines 3814 and 4271). There is no additional dedicated native `WARPSYNC`; native NOP/control scheduling remains. This does **not** establish missing synchronization or zero synchronization cost. Preserve both source syncs.

FC2 has identical PTX, resources, instruction addresses, predicates, opcode sequence and upper encoding/control words. Its native cubin/SASS are **not raw-identical**: 12 sites rename the paired descriptors `UR16/17` and `UR18/19`. The finalizer's PTX/cubin/SASS are all raw-identical. `MOV.SPILL`/`R2UR.FILL` changes are register-file transfers, not local-memory spills; both native FC1s have no LDL/STL and driver LOCAL is zero.

The remaining matrix must establish G1/G4, SF16, two-CTA, actual CLC and partial-K/row behavior. No new source, GPU launch, compiler option or timing was introduced by this review.
