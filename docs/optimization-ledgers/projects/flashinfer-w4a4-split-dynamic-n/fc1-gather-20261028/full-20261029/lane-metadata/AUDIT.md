# Lane-distributed Gather4 row metadata

Base: measured control112 source (`d9af059b…`). Candidate: `bb8958ea…`.
One candidate, no dtype/model/topology policy or new tactic.

For each existing four-row group, lanes use `lane & 3` to load/decode one
mapping index, then shuffle from lanes0–3 into the same four warp-uniform
Gather4 coordinates. All lanes execute the shuffles after the guarded load.
Invalid rows retain the existing TMA OOB sentinel; no invalid mapping slot is
read. Existing row/K ownership, scale-factor loads, stages, barriers and PDL
remain unchanged. The vector-full/scalar-tail branch is removed.

Static enumeration checked219,820 row groups: routing tiles16–256, one/twoCTA,
every valid-row count including0, all four gather warps and top-k1/4/8/22/32.
Current mapping results and all four coordinates match exactly. Pre-commit
passed. All seven selected exact cases passed with no failures/skips. The paired
performance screen completed successfully; see`RESULTS.md`.

Fresh codegen against112:

| Case | Instructions before→after | Branches | R2UR | Stack/local |
|---|---:|---:|---:|---:|
| N3U EP W4A4 T4096 |7448→6784|166→149|563→383|0→0|
| N3U EP per-token T4096 |1864→1672|163→158|151→115|0→0|
| V3 TP MXFP8 T16384 |6448→6160|186→177|267→203|0→0|
| V3 TP MXFP4x8 T16384 |6448→6160|186→177|267→203|0→0|

The new instructions include four SHFLs per group. R2UR.FILL sites rise
slightly, but total R2UR and instruction counts fall; no local spills appear.
All binary register/pool guards pass. Four FC2 instruction streams remain
identical. Full CUBIN/SASS artifacts are under `codegen-evidence/`.

Controls for the completed44-cell C-A-A-C screen are fresh measurements of112,
so its result isolates this metadata change. Both sources use the original
frozen winners/routes and100 strict-CUPTI cold-L2 samples per phase.

## Why SF mapping stays independent

Payload warp `w` owns four-row runs `4*w + 16*g + cta_offset`; its SF lanes
own rows `8*w + 32*q + r` before the full-N row-block offset. These sets do
not line up, especially with the dynamic two-CTA midpoint. A warp shuffle
cannot share coordinates across warps. Merging them would require changing
SF ownership or adding shared storage/synchronization; it is not needed for
this smaller instruction simplification.

MegaMoE's256-bit index load owns eight-row runs. Directly adopting that
layout here would also change the flattened row/K ownership and can reduce
issuing-warps participation on narrow tiles. This candidate preserves the
current four-row ownership, uses one coalesced scalar instruction per warp
for four unique contiguous addresses, and keeps exactly the existing number
of cached coordinates.
