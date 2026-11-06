# SF coordinate-cache fresh qualification: independent peer

**Passed.** This receipt covers only the fresh `qualification-extra-r1` campaign on the explicitly adopted release cohort (`moe_utils` `046552b8`, cache `ad6b3a6d`, readiness `e466ac7c`). The older wide pilot and aborted continuation are preserved separately and contribute no calls to this gate.

Replayed all 419 archive members, 22 successful exact calls, 33 native pairs, 198 PTX/cubin/SASS hashes and 89,608 instruction lines. Both 13,245-file source inventories differ only by the qualified `15d6eb18` kernel. Source/cache preflight and closure, normal private-arm native loading, four-library hashes/no-op receipts, strict source guards and unchanged compiler options all join.

All 66 loaded kernels have zero driver LOCAL bytes. Paired register counts, maximum threads, static shared memory and binary version are equal. Operand stage counts and driver CTA capacity are unchanged; all GEMM capacities remain one. Actual shared-allocation differences below match the source struct alignment, including 1024-byte operand alignment for native MMA K96. They are not simply the raw coordinate-array size.

| FC1 case | Native MMA K | CTA group | Actual CLC | Stages | Shared delta B | Non-NOP delta |
|---|---:|---:|:---:|---:|---:|---:|
| pilot-mx8-wide-g2 | 32 | 1 | no | 2 | +1024 | -171 |
| pilot-nv-g4 | 96 | 1 | no | 9 | +1024 | +35 |
| mx4-g1-control | 32 | 1 | no | 10 | +128 | +7 |
| mx8-g1-n256-control | 32 | 2 | no | 6 | +512 | -53 |
| mx4-g2-partial-k | 32 | 2 | no | 5 | +128 | +37 |
| pt-g4-partial-k | 96 | 2 | no | 10 | +1024 | +41 |
| nv-g4-m512 | 96 | 2 | no | 4 | +1024 | +73 |
| pt-g4-native-clc1 | 96 | 1 | yes | 9 | +0 | +40 |
| nv-g4-native-clc2 | 96 | 2 | yes | 10 | +0 | +44 |
| nv-g4-w8-n256 | 96 | 2 | no | 2 | +1024 | +20 |
| pt-g4-w8-n256 | 96 | 1 | no | 2 | +1024 | -114 |

Native MMA K96 is used by NVFP4/per-token signatures and K32 by MX signatures; logical stage K is separately 128/256/512. This gate covers SF16/SF32, lane groups 1/2/4, one/two CTA, actual CLC and static scheduling, PDL on/off, partial rows and partial-K cases. Both requested native CLC cases are confirmed in the loaded configuration. No correctness override is represented as a selected production tactic.

All 22 FC2/finalizer PTX, cubin and SASS pairs in this **fresh** cohort are byte-identical. The older wide pilot’s descriptor-register renaming is not imported into this result. All FC1 deltas are retained: narrow cases add 7–73 static instructions, and three wider cases remove 53–171. No spill or capacity loss is hidden by those counts.

The qualification passes the source/native gate for the authorized performance screen. It does not demonstrate a speedup, and it does not justify retaining complexity without the full frozen screen. Added LDS/address/mask work in narrow cases remains a concrete performance risk. Driver capacity is not a measurement of actual residency.

Machine-readable receipt: [sf-coordinate-cache-qualification-peer.json](sf-coordinate-cache-qualification-peer.json), SHA `399faeec43888a2ae049e82b13960a1f6e1a9f619569a29b3888e429c7ec179d`. Replayer: [sf_coordinate_cache_qualification_peer.py](sf_coordinate_cache_qualification_peer.py). Final owner gate SHA `914ce08b421017aeee20cc025f6cdc5fcaef0523a48a988d87cc8ee100de32e4`.
