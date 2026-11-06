# Terminal barrier removal: emitted-code audit

Source: clean9334 versus kernel SHA `5e0f4a3efb21f68fa7202e7b136ed46ec9c2ba4242ded214853933f4b70b91e6`. Gate evidence is `scripts/sync_audit_20261027/validation/scheduler/evidence`; the exact source pair and immutable artifact hashes are recorded there. This audit does not attribute V2 bulk-wait results to V1.

All44 compiled pairs remove precisely the intended PTX `bar.sync 2,128` site. The final barrier1 arguments, TMEM wait/relinquish/dealloc/commit counts, raw CLC query count, bulk-read wait count and two-CTA deallocation arrive/wait sites remain unchanged. `v1-codegen-audit.json` records every core and its PTX/SASS evidence paths. The paired gate passed64 CLC plus24 static exact replays per source, with no local-memory spills or geometry/stage/storage changes.

| Metric | CLC32 cores | Static12 cores | Combined |
|---|---:|---:|---:|
| Non-NOP SASS instructions | −227 | −88 | −315 |
| Register delta range | −8…0 | 0 | −8…0 |
| Terminal barrier2 sites | −32 | −12 | −44 |

The combined listing additionally has13 fewer NOPs, making328 fewer instruction lines including NOPs. These are static code counts, not dynamic cycle savings.

The compiler removes more than one instruction per core because removing the intervening128-thread rendezvous lets it combine cleanup admission with the allocator-warp predicate. Across all44 cores, one `BAR`, one `BRA` and one `EXIT` disappear, while separate `ISETP.GT.U32.AND` admission becomes a combined `ISETP.GT.U32.OR`. Other changes depend on the specialization's register allocation and uniform address calculations.

For example, `clc-gpu2/{control,candidate}/config0-fc1-pdl1.sass` has final barrier1 at address0x4150 in both arms. Control exits non-epilogue warps at0x4170, branches non-allocator epilogue warps to barrier2 at0x4190, executes barrier2 at0x4210 and then exits those warps at0x4220. Candidate combines both predicates before one exit at0x4180. The now-adjacent permit/free lowering also shares CTA-id/address setup that the control repeats after barrier2 (`S2UR`/`UMOV`/`ULEA`). The control/candidate SASS line2097 anchors the common barrier1; control line2121 is the deleted barrier2.

For the wider `clc-gpu2/config1-fc2-pdl1`,30 non-NOP instructions disappear, including14 `R2UR` and seven `UIADD3`, with additional uniform-shift/predicate substitutions. This is broader compiler allocation/scheduling cleanup from the same one-line source change; it should not be summarized as30 synchronization instructions removed. No end-to-end speedup claim is made by this audit.
