# R9 register-policy capture

R9's C80/G128/E256 policy passes the prelaunch register-pool guard for both
N3U TP8 T16384 MXFP8 and MXFP4x8 winners, but increases local spills. No broad
R9 tests were launched. Instrumented benchmark timings are diagnostic only.

| FC1 measurement | R6 | R9 |
|---|---:|---:|
| Initial registers per thread | 168 | 168 |
| Stack bytes | 208 | 488 |
| Static LDL sites | 26 | 114 |
| Static STL sites | 46 | 112 |
| Gather-region maximum GPR | R165 | R77 |
| Gather-region LDL / STL sites | 0 / 0 | 12 / 12 |
| Epilogue-region maximum GPR | R163 | R77 |
| Epilogue-region LDL / STL sites | 26 / 46 | 102 / 100 |

The budget change reduces the emitted GPR range of both gather and epilogue
to the smallest declared control budget, despite their larger G128/E256
targets. A likely explanation is compiler register-budget propagation across
the join after the three setmaxnreg branches. This is an inference from the
control flow and machine-code resource usage; it is not a compiler root-cause
proof.

The policy emits at SASS PCs 0x790 (deallocate80), 0x7e0 (allocate256), and
0x820 (deallocate128), then reconverges at 0x830 before the actual role
dispatch. Later thread-id checks identify gather as tid>=256 and epilogue as
128<=tid<256. R9's gather body occupies [0x1db0,0x8e90), and epilogue occupies
[0x8eb0,0x1bef0). R6's corresponding ranges are [0x1cc0,0x9370) and
[0x9390,0x1ae70). `spill-roles.json` records every local-load/store address and
source SASS line within those regions. All72 R6 and226 R9 local instruction
sites fall within the reported role ranges; control roles have none.

Prefer testing a structured top-level warpgroup dispatch that keeps these
register regions separate until final cleanup. Control warp specialization
must remain nested inside its whole-warpgroup policy; placing independent
setmaxnreg calls in individual warp0/1/2/3 branches does not establish the
required full-warpgroup execution contract.

R9 source kernel SHA256:
`b8454839eb271c108772f85b723bc2acae9d1a97815d6db56b318bf6e8aa16f5`.
All513 source hashes, full patch, winner-cache bytes, routing identities and
the nine persistent native-cache links passed checks before/after execution.
FC2 remains256threads, has no setmaxnreg instructions and no local spills.
The new-cubin guard ran synchronously before returning each compiled callable:
reqntid384, exact policy, donors<=R0<=256, and required59392<=initial64512
register pool. Other shapes are not qualified by this one passing geometry.

Artifacts are in `evidence/0-tp-nemo3-ultra-mxfp/capture/000-fc1.*` and
`002-fc1.*`; the sibling `bindings.json` and `driver-receipt.json` bind them to
the saved public API winners. Archive SHA256:
`7570fb4ea2b89ac12e507a6fd1755697feef56c15bb9d9406681f269198cf2b8`.

`register_guard_plugin.py` is a prepared, syntax-checked external pytest
plugin that applies the same guard to every compiled specialization. It has
not been deployed or executed. It requires explicit source, repository,
artifact destination, expected kernel SHA and all three register budgets.
It does not modify repository files or authorize unguarded launches.
