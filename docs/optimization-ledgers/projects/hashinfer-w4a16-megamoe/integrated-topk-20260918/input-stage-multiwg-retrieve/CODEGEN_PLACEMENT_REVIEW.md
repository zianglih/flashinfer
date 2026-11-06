# Three-WG staging generated-code review

**Pass for native and queued validation**, source `b215a7d2`. All32 canonical rank outputs are finite and bit-exact against sealed `7dc`; all128 compiled ABI artifacts pass integrity checks.

- **Common rendezvous:** every fused entry has exactly one `bar.sync 2, 544` and one SASS `BAR.SYNC ... 0x2, 0x220`. Its predicate skips exactly warps5–7; warps0–4 and8–19 participate. All384 staging threads are included. The existing earlier cluster-init arrive remains relaxed. Explicit raw416 behavior is source-reviewed; raw is not one of the four captured fused ABIs.
- **Copy and publication:** vector ABIs retain one `LDG.E.128`/`STG.E.128` pair per iteration. Generic ABIs retain eight16-bit loads and one128-bit store. WG/grid striping uses56832 chunks per loop step (`148×384`) and preserves the dispatchWG's first strip. An actual writer executes `FENCE.VIEW.ASYNC.G` only after its final store; all paths then reconverge at the shared barrier before dispatch enters existing publication. Empty writers skip data accesses and the fence, not participation.
- **Progress:** the widened rendezvous and copy occur before control80, dispatch64 and epilogue144 redistribution. Decode WGs retain96. No register-budget or progress-cycle change was found.

| Tactic | All four ABI resources | Static local-memory SASS instructions | Change from7dc |
|---|---|---:|---|
|N128 / epilogue return|REG96, STACK8, LOCAL0, SHARED1024|7|None|
|N128 / dispatch return|REG96, STACK0, LOCAL0, SHARED1024|0|None|
|N64 / epilogue return|REG96, STACK0, LOCAL0, SHARED1024|0|None|
|N64 / dispatch return|REG96, STACK0, LOCAL0, SHARED1024|0|None|

The PTX named-barrier inventory changes only416→544 at barrier2. Other barrier/fence counts and role budgets match. Fifteen of16 tactic/ABI groups have byte-identical generated artifacts across all8 ranks. The remaining N128 dispatch/int32-vector group has a rank5 compiler variation (virtual b32 count3760→3751), with the same reviewed staging/control-flow facts and resource usage. Raw artifacts are preserved; no whole-kernel byte-identity claim is made for this scheduling change.

Capture executes int32/vector at128 global tokens; it does not replace the existing larger/empty/generic native tests or queued/raw-thunk validation. Performance retention remains pending. Per-entry line numbers, raw hashes, widths and resource inventories are in `codegen-generated-facts.json`; the hash-bound verdict is `codegen-placement-review.json`.
