# SF/payload interleave native qualification

Frozen candidate `a014d6aa` on retained `2b8eb9d8`; main source unchanged. No performance result yet.

Two existing pilots passed the strict exact oracle. Their successful retained-source controls were reused after matching the four current native ELF/Ninja hashes. All six paired native kernels have equal registers, local storage, dynamic/static shared memory, launch capacity and occupancy. FC2 and finalizer raw cubins are identical in both pilots. Full 13,245-file source and native-cache checks pass before/after; GPUs0/1 were released.

| FC1 pilot | registers / local bytes / CTAs per SM | non-NOP sites | SF / Gather4 / completion sites | ELECT sites |
|---|---:|---:|---:|---:|
| NVFP4 N16 K256, K96 MMA | 168 / 0 / 1 unchanged | 1052→1058 | 4 / 1 / 1 unchanged | 5 unchanged |
| MXFP8 N256 K256, Ksteps8 | 168 / 0 / 1 unchanged | 3691→3690 | 4 / 32 / 1 unchanged | 11 unchanged |

Actual SASS keeps the proposed mixed issue order. Narrow changes `SF,SF,SF,SF,complete,TMA` to `SF,TMA,SF,SF,SF,complete`. Wide places one Gather4 site between each of the first four SF copies, then completes SF and issues the remaining Gather4 sites. Completion still follows the last SF copy. Static sites are not dynamic instruction counts or performance evidence.

Narrow overhead is explicit: one additional BRA/BSSY/BSYNC region around the final SF copy, plus three `@!PT LDS RZ,[RZ]` compiler-padding instructions. Those predicated-off LDS instructions add no shared-memory reads. Wide has no additional election/branch sites and one fewer net non-NOP instruction, with address/allocation opcode substitutions. No source rescue or shape policy is proposed.

[Complete parser replay](analyze_qualification.py), [pilot summary](qualification-summary.json), [native ordering/resource receipt](pilot-native.json), [sealed paired evidence](qualification/fetched/fetch.json). The remaining nine existing pairs also passed; the combined gate covers22 selected exact calls (20new,2reused controls) and33 native pairs. All resource fields and occupancy remain equal/LOCAL0. All22 FC2/finalizer cubins and the one-slot MX4 FC1 are raw-identical. Both leaves passed full source/native-cache postflight. The authorized56-cell timing screen is a separate leaf and has no results yet.

| All FC1 cases | non-NOP control→candidate | raw cubin identical |
|---|---:|---|
| pilot-nv-g4 | 1052→1058 | no |
| pilot-mx8-wide-g2 | 3691→3690 | no |
| mx4-g1-control | 1212→1212 | yes |
| mx8-g1-n256-control | 3646→3643 | no |
| mx4-g2-partial-k | 1347→1346 | no |
| pt-g4-partial-k | 1361→1362 | no |
| nv-g4-m512 | 3927→3928 | no |
| pt-g4-native-clc1 | 1239→1244 | no |
| nv-g4-native-clc2 | 1547→1547 | no |
| nv-g4-w8-n256 | 3507→3502 | no |
| pt-g4-w8-n256 | 3255→3224 | no |

Native CLC N16 has the same three predicated-off LDS plus BRA/BSSY/BSYNC overhead, offset by one removed IMAD. Other variants expose address/uniform-register allocation changes; `MOV.SPILL`/`R2UR.FILL` deltas are uniform-register transfer bookkeeping, with native local-memory usage still zero. No static instruction change is treated as a timing result. [Combined sealed gate](qualification-summary-combined.json), [join replay](combine_qualification.py).
