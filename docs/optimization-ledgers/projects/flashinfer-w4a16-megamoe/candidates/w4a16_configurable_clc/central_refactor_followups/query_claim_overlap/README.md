# Held query / FC2-claim overlap

Base is the held task-or-terminal proposed `clc.py`, SHA256 `882dc6242fa511e5c02f693d1bde28fac6ead84113f73a370b5c507bb44a512b`. This patch is not directly based on primary `clc.py`; apply task-or-terminal first. Primary and all runtime artifacts are untouched.

Only `run()` changes. Once the existing cluster broadcast supplies a nonterminal outcome, the leader warp issues the existing CLC query, then both owner warps publish the ready FC2 claim if one was popped. The existing wait/decode/fence/release follows. Bundle initialization stays after FC2 publication, so no decoded bundle lives across that blocking operation or the loop header. There is no new state, knob, response slot, pipeline stage or synchronization primitive.

The `-2` branch issues nothing and follows an iteration whose response was already consumed/released. A successful queue pop is still published even if it is the last FC2 task. An ordinary empty pop follows the existing query/fallback path. An observed negative CLC response still permanently clears `clc_enabled` before any later loop iteration can issue another request. The query's leader/elect-one scope, producer phase advance, all-CTA wait/release and consumer phase advance are unchanged. The single response buffer cannot be reused before its consumers release it.

If FC2 claim publication blocks, warp 7 can consume prior claims and the independent compute/epilogue roles can retire them without the new response. Dispatch already completed, FC2 tasks only come from published ready rows, and CLC epilogue completion precedes NEXT consumption. The response remains encoded in its own shared buffer until the unchanged cancellation decoder and exact-once ownership path run. No successful cancelled tile is dropped; first-failure fallback, initial ownership, queue termination, local submitted-work drain and fixed finish/reset remain unchanged. Exactly two decode warp groups / five total warp groups remain intact.

The available overlap is only on iterations with an FC2 task while CLC remains enabled. Empty polls and software-fallback-only iterations do not gain this overlap. Native instruction ordering, register allocation and timing are untested; this is a source-only scheduling candidate, not a performance result. It remains separate from bundle-size experiments, row metadata, SF cleanup and payload overlap.

`checks.json` records one syntax/Ruff/format/read-only apply check, identical AST outside `run`, unchanged run signature/name set and unchanged call multiset. No numerical, benchmark, GPU or source installation was run. Independent source review is recorded separately when complete.

Proposed file SHA256: `b9ce042f14a5e6d179a4d130f9d3e608c7eb86c4e28bea8b8549e2d3b868c25f`.

Patch SHA256: `2130620b43ae92bf1cddfb02be6040c81f91d1bb1a029e290b4e05baf4172657`.

Checks SHA256: `d4d39e1756953f99702c64e17bf9c7cb16c68eef80f4443cd50456aabd5d938e`.
