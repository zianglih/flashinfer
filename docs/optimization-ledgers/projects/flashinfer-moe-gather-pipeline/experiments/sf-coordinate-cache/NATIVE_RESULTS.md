# Wide stress pair passed; performance remains untested

Source `15d6eb18`, retained control `c1ac8ce7`. Both existing MXFP8 N256/K8
Relu2 exact calls passed. Source inventories and native-cache postflight passed;
GPU2 is released. No timing or other signatures ran in this pilot.

| FC1 | Retained | Candidate |
|---|---:|---:|
| Registers / driver local bytes | 168 / 0 | 168 / 0 |
| Dynamic shared bytes | 203,520 | 204,544 |
| Operand stages / driver CTA capacity | 2 / 1 | 2 / 1 |
| Static non-NOP instructions | 3,691 | 3,520 |
| SHFL / R2UR sites | 64 / 289 | 0 / 256 |
| R2UR.FILL / MOV.SPILL sites | 24 / 24 | 8 / 8 |
| LDS.128 / coordinate STS sites | 0 / 0 | 32 / 2 |
| Gather4 / SF LDGSTS sites | 32 / 4 | 32 / 4 |
| Global scalar LDG sites | 13 | 15 |

The candidate has no LDL/STL or local storage. MOV.SPILL/R2UR.FILL here are
uniform/general-register transfers, not evidence of local-memory spilling.
Two additional global metadata-load sites come from the original R1 SF mapping.

All 32 packet loads are actual `LDS.128`, elected-lane predicated, inside the K
loop at `0xc640`–`0xd420`; each feeds its existing Gather4. The backedge
`0xd4b0 -> 0xc220` repeats them per stage. They are not hoisted into persistent
register state. This adds 2 KiB of logical shared reads per CTA/stage. Both explicit
cache `bar.warp.sync -1` operations survive PTX; PTXAS emits no additional native
WARPSYNC sites for this specialization. Source synchronization remains required.

The static reduction is 171 instructions, with compiler scheduling/control churn
included: ordinary BRA falls by14 while BRA.U rises by14; election count stays11.
No executed-work or performance improvement is inferred from these static counts.

FC2 retains identical PTX, resources and opcode counts. Its cubin/SASS differ at12
uniform descriptor-register renaming sites (UR16/17 versus UR18/19), with identical
instruction addresses and control words. The finalizer PTX/cubin/SASS are raw
identical. The resource capacity is a driver calculation, not sampled residency.

Raw archive `77cc10ca174c81fc67b1800b6c67f69dee0e0419933fe01d8e2fd0370e109ba5`;
full artifacts under `qualification/evidence/`. `native-summary.json` and
`analyze_native.py` preserve complete instruction counts and the native comparison.
