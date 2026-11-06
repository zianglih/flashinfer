# Frozen CLC R2 versus retained fca resources

Compile-only regenerated kernels; no launches, performance measurement, or numerical validation. Static FC2 has CLC disabled in the candidate but shares refactored scheduler loops.

All 30 pairs match runtime, GPU, constructor/pointer contract, geometry and compile options; candidate adds only explicit scheduler constructor settings. Source and artifact hashes verified. All pairs have zero local bytes/LDL/STL, one CTA/SM, and 74 active two-CTA clusters. No pipeline-depth change.

| Model | Format | Phase | M/N | Threads | Regs | SMEM B | Stages | SASS instructions | SASS exact |
|---|---|---|---|---|---|---|---|---|---|
| v3 | nvfp4 | fc1 | 256/128 | 288→320 | 70→73 | 230272 | 4 | 1208→1368 | False |
| v3 | nvfp4 | fc1 | 256/256 | 288→320 | 80→84 | 195456 | 5 | 5384→5432 | False |
| v3 | nvfp4 | fc1 | 512/128 | 288→320 | 82 | 189312 | 4 | 5512→5528 | False |
| v3 | nvfp4 | fc2 | 256/128 | 288 | 110→106 | 207232 | 6 | 1712→1680 | False |
| v3 | nvfp4 | fc2 | 256/256 | 288 | 120→118 | 229760 | 5 | 2464 | False |
| v3 | mxfp8 | fc1 | 256/128 | 288→320 | 70→74 | 205696 | 4 | 1160→1336 | False |
| v3 | mxfp8 | fc1 | 256/256 | 288→320 | 88→86 | 206720→206848 | 6 | 5736→5760 | False |
| v3 | mxfp8 | fc1 | 512/128 | 288→320 | 86→84 | 213376 | 5 | 5680→5712 | False |
| v3 | mxfp8 | fc2 | 256/128 | 288 | 116→110 | 214528 | 7 | 1280→1288 | False |
| v3 | mxfp8 | fc2 | 256/256 | 288 | 124 | 206720 | 5 | 2064→2056 | False |
| v3 | mxfp4-mxfp8 | fc1 | 256/128 | 160→192 | 78→74 | 205696 | 4 | 1120→1272 | False |
| v3 | mxfp4-mxfp8 | fc1 | 256/256 | 160→192 | 78→74 | 206720→206848 | 6 | 1296→1448 | False |
| v3 | mxfp4-mxfp8 | fc1 | 512/128 | 160→192 | 82→76 | 213376 | 5 | 1528→1672 | False |
| v3 | mxfp4-mxfp8 | fc2 | 256/128 | 288 | 116→110 | 214528 | 7 | 1280→1288 | False |
| v3 | mxfp4-mxfp8 | fc2 | 256/256 | 288 | 124 | 206720 | 5 | 2064→2056 | False |
| v41-flash | nvfp4 | fc1 | 256/128 | 288→320 | 77→76 | 230272 | 4 | 1208→1360 | False |
| v41-flash | nvfp4 | fc1 | 256/256 | 288→320 | 87→92 | 195456 | 5 | 5368→5416 | False |
| v41-flash | nvfp4 | fc1 | 512/128 | 288→320 | 80→88 | 189312 | 4 | 5448→5480 | False |
| v41-flash | nvfp4 | fc2 | 256/128 | 288 | 110→106 | 207232 | 6 | 1760→1776 | False |
| v41-flash | nvfp4 | fc2 | 256/256 | 288 | 120→124 | 229760 | 5 | 1848→1864 | False |
| v41-flash | mxfp8 | fc1 | 256/128 | 288→320 | 72→78 | 205696 | 4 | 1152→1328 | False |
| v41-flash | mxfp8 | fc1 | 256/256 | 288→320 | 88→86 | 206720→206848 | 6 | 5704→5744 | False |
| v41-flash | mxfp8 | fc1 | 512/128 | 288→320 | 84 | 213376 | 5 | 5632→5672 | False |
| v41-flash | mxfp8 | fc2 | 256/128 | 288 | 110→104 | 214528 | 7 | 1128→1136 | False |
| v41-flash | mxfp8 | fc2 | 256/256 | 288 | 120 | 206720 | 5 | 1872→1880 | False |
| v41-flash | mxfp4-mxfp8 | fc1 | 256/128 | 160→192 | 76→74 | 205696 | 4 | 1104→1256 | False |
| v41-flash | mxfp4-mxfp8 | fc1 | 256/256 | 160→192 | 78→75 | 206720→206848 | 6 | 1288→1440 | False |
| v41-flash | mxfp4-mxfp8 | fc1 | 512/128 | 160→192 | 82→76 | 213376 | 5 | 1520→1672 | False |
| v41-flash | mxfp4-mxfp8 | fc2 | 256/128 | 288 | 110→104 | 214528 | 7 | 1128→1136 | False |
| v41-flash | mxfp4-mxfp8 | fc2 | 256/256 | 288 | 120 | 206720 | 5 | 1872→1880 | False |

Static FC2 codegen is not invariant: compare the per-row registers and SASS above before assigning end-to-end changes solely to CLC work balancing. Any latency attribution requires the separate static-refactor control/fixed-tactic measurements.
