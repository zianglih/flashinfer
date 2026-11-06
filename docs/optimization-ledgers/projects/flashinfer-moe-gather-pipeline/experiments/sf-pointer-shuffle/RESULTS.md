# SF pointer shuffle: rejected at the native gate

Root rejected candidate `371510e6a745e8c7845d0918a7d5984386b07ff7eea3eb4749f3f5f8fe6ad6e4` on retained c1ac. Both affected wide FC1s compiled normally but the unchanged no-native-local guard rejected them **before FC1 invocation**. These are resource failures, not numerical mismatches. No wide candidate numerical result or performance measurement exists; no full matrix, retry, quota/compiler change or shape-specific rescue followed.

| Existing pilot | Exact candidate outcome | Initial registers | Driver local bytes C→A | cuobjdump candidate | Static non-NOP C→A | Added SHFL | Candidate local instructions |
|---|---|---:|---:|---|---:|---:|---|
| MXFP8 N256/K8, G2 | Stopped before FC1 invocation | 168→168 | 0→48 | STACK48, LOCAL0 | 3691→4112 (+421) | 8 | 40 LDL, 12 STL |
| Per-token N256/K8, G4 | Stopped before FC1 invocation | 168→168 | 0→16 | STACK16, LOCAL0 | 3255→3669 (+414) | 32 | 26 LDL +5 LDL.LU, 9 STL |
| MXFP4x8 N16/K4, G1 | Existing exact oracle passed | FC1 168→168 | 0→0 | STACK0, LOCAL0 | 1212→1212 | 0 | none |

The CUDA driver local-size attribute includes the stack allocation that cuobjdump reports separately. The guard correctly caught actual LDL/STL spilling despite cuobjdump's `LOCAL0` field. Existing control/gather/epilogue register quotas remain 128/128/248, the initial pool remains 64512 registers, and normal compile options remain unchanged. Failed wide driver capacity/dynamic shared fields were not collected after the early guard; no residency claim is made. The original storage/planner source is unchanged.

The three G1 images (FC1, FC2, finalizer) are raw PTX/cubin/SASS-identical to their controls, with equal captured resources/configuration. Its constexpr identity branch works in actual compilation, not just the source-string check.

## Actual pointer lowering

Both pointer halves are exchanged in the K loop: MX8 adds eight SHFL sites at `0xdc10–0xdee0` inside the `0xd1d0→0xf980` loop, and per-token adds 32 at `0xb6f0–0xc0a0` inside `0xb430→0xdfb0`. This did not become a whole-loop-hoisted G-way address cache. It nevertheless creates enough address/predicate/uniformization pressure to spill and grow native code. The result does not establish that every temporary address has minimal lifetime.

Whole-image global-load sites remain 13/13 for MX8 and 29/29 for per-token; async SF-copy sites remain 4/4 and 16/16. Original payload register coordinates, one Int64 SF offset per lane/block and pre-loop route/division source are intact. The selected existing fixtures use top_k2, so they do not measure N3U's top_k22 division cost. The two-wide result adds no coordinate-SMEM loads, scratch or warp barriers, but still fails the general native gate. No DRAM-byte or coalescing performance benefit is claimed.

## Evidence and closure

- [Exact source/patch](candidate.patch), [static/source receipt](source-proof.json), [scoped hooks](precommit.log), [independent source peer](../../audits/sf-pointer-shuffle-source-peer.json).
- [Native summary](native-summary.json) and [replayer](analyze_native.py): 14 captured/failed native images, complete address-line instruction parsing, all artifact hashes and three G1 identities.
- [Qualification evidence](qualification/evidence), [fetch receipt](qualification/fetch.json), archive SHA `a3170fe306e838e7a7b748a3c35f2e847805a7a490ff8a4cb99a335fd2aa1ed4` (3,500,781 bytes).
- Three controls were reused unchanged from fresh046 `sf-coordinate-cache/qualification-extra-r1`, with exact source/helper/runtime/native bindings in [control-reuse.json](qualification/evidence/control-reuse.json). Only three candidate calls ran. All four oracle/capture/resource/native helpers are byte-identical to that corrected harness.
- [Closure](qualification/evidence/closure.json) verified both 13,245-file source inventories, unchanged current046 ELF/Ninja hashes and no-op, and GPUs2/4/6 at zero memory/utilization with no compute processes. Original failed receipt is preserved.

Controller wall time was 56.80 seconds: 41.07 seconds before the first candidate subprocess, then 10.80/11.35/15.71-second candidate subprocesses in parallel. These include imports/compilation/validation and are not GPU timing measurements. No broader launch was made.

[Independent native peer](../../audits/sf-pointer-shuffle-native-peer.json) `b531a8a0` confirms the source/native/cohort and failure boundary. [Source retirement](retirement/receipt.json) removes only the inactive local review/branch after exact guards; all artifacts and remote caches remain.
