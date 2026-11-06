# Rejected: inline SF address rematerialization still spills

Source `c631de18`, based on retained `c1ac8ce7`, compiled successfully but failed the unchanged native LOCAL0 guard **before candidate FC1 launch**. The fresh control passed the existing exact oracle. No candidate exact result, further cases, timing, quota change, or narrower-arithmetic workaround was attempted.

| FC1 native artifact | Registers | Driver local bytes | Non-NOP | LDL / STL sites | SF LDGSTS sites |
|---|---:|---:|---:|---:|---:|
| Fresh current control | 168 | 0 | 3,691 | 0 / 0 | 4 |
| Historical coalescing R1/R2 | 168 | 64 | 4,112 | 43 / 15 | 4 |
| Inline-address candidate | 168 | 48 | 4,094 | 39 / 11 | 4 |

The mechanism did change lowering. Candidate PTX retains four Int32 rows across the K loop and performs four signed widening/64-bit MAD operations inside the existing copy assembly; the former four pre-loop wide row products are gone. Native SASS retains the rows in R16/R15/R14/R5, but still computes four address pairs together with LEA/LEA.HI at `d5b0`–`d630`. Signed-high correction occurs near their LDGSTS uses (`e190/e230/e2c0/e350`). Thus compact persistent rows survived, but not the hoped-for fully short-lived address temporaries. The 16-byte local reduction is diagnostic only; Gather4 coordinate state and spills remain. Cuobjdump reports STACK48 while the loaded driver function reports LOCAL_SIZE_BYTES48; its separate static LOCAL field is zero.

The expected coalesced full-stage request reduction remains only an ideal per-instruction sector model (2x for this G2 case). Useful addresses/unique sectors are unchanged; no DRAM savings were measured. The exact signed-64 arithmetic and all copy masks/arrivals were preserved. No new compiler options or register budgets were used.

Existing timing records show where this bounded probe spent wall time:

| Interval | Seconds | Observation boundary |
|---|---:|---|
| Controller start → native preflight file | 12.47 | Python/native-description setup, current-library hashes and Ninja no-op checks |
| Native preflight → first idle sample | 31.65 | Both complete 13,245-file inventories plus the first idle query |
| First idle → control subprocess | 1.56 | Second sample/settle and per-arm idle check |
| Control subprocess | 18.41 | Includes 4.54 before guard startup; oracle wrapper 12.21 includes compilation/capture and exact work |
| Candidate subprocess | 11.70 | Includes 4.46 before guard startup; wrapper 5.73 stops on native local-memory guard |
| Complete controller | 77.41 | Includes inter-arm settle and process finalization |
| Read-only failure closure | 28.17 | Both source inventories, native hashes and fresh GPU idle verification |

Setup boundaries use existing file timestamps, not dedicated stage timers. Pure compilation and exact GPU-only time were not separately measured. Candidate preparation can execute helper/input operations, but the failed FC1 callable never returned from the prelaunch guard. These records support reducing repeated CPU verification in future tooling, without changing this run or its evidence.

All source/cache postflight checks passed; GPU2 was released with no PIDs, zero MiB and zero utilization. Raw archive SHA `dc6d44a24bf5e66a0824fd545acba523cb1e2db34f247fdd80799f314b0ae89b`; [native summary](native-summary.json), [raw evidence](qualification/evidence), [closure](qualification/evidence/closure.json), [source/patch](candidate.patch). Historical R1/R2 artifacts remain untouched. Only the owned review checkout/branch is retired after exact preservation; canonical production stays clean at c1ac.
