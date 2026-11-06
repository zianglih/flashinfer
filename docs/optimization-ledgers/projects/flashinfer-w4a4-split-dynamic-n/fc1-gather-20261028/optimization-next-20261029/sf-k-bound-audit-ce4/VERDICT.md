# SF K-bound audit: keep the current loop

No producer-side K peeling is justified by the inspected generated code. The compiler already removes the repeated problem-K comparison; a separate full/tail loop would duplicate source without removing that work. No source edit, new compilation, GPU launch, or performance claim was made.

## Current retained code

The ce4 kernel is `77a5495cca8dedef5bccfaacde64a1004b9a7c421175511f12ffef2d996439b3`. In `moe_swap_ab_kernel.py:3516–3540`, each SF word uses `(row < valid) & (channel < weights.shape[1])`; `_copy_gather_sf` at lines94–114 implements this as the cp.async ignore-source operand. `row < mma_n` separately controls whether a participating row issues the copy at all.

The saved final41-case gate contains **41 FC1 captures** and39 FC2 captures. All374 inline SF-copy sites in those41 FC1 PTX files have a source-validity input defined by either a single `setp.lt.s32` row comparison or literal zero. No combined K comparison survives. Captures002/004/012/013 contain constant-zero SF words for partial K; these preserve zero-fill rather than skipping the necessary write. The coverage includes SF16/SF32, FP4/FP8 inputs, N16–256, one/two-CTA, static/CLC and native K96 cases.

Representative current `000-fc1` SASS has one row-valid comparison at`0xc430` reused by eight LDGSTS words, then another at`0xc720` reused by the next eight. The issue predicate remains separate and necessary. [Saved excerpts](sass-excerpts.txt) and [replayable predicate/hash audit](audit.py) preserve exact artifacts and definitions; [full result](predicate-audit.json) binds every inspected PTX/SASS/CUBIN to its capture receipt.

## Full-model corroboration and boundary

The saved native V3 EP8 MXFP8 T16384 capture uses H7168 and stageK128, hence56 K stages. Its loop is unrolled four stages: `UR15 +=4`, comparison against`0x38`, branch back to`0xd800`. All four static LDGSTS sites reuse P1, established by the row-valid comparison at`0xd590` outside that K loop. There is no per-stage source-K comparison.

This full-model binary is explicitly the older77391 source (`dca375bb…`), **not** a fresh ce4 full-model capture. It corroborates optimization of the same SF channel-bound expression in a genuine long K loop. Current ce4 conclusions are scoped to its41 saved exact captures; no claim that every possible future shape/compiler version has been exhaustively checked. Standard K-loop termination and ring-state comparisons still exist and are not redundant SF source bounds.

The prior `sf-payload-linear-guard*` experiments changed route ownership/indexing to reuse SF IDs; they did not peel this K loop. The current lead is closed on generated-code evidence rather than inherited timing from those rejected experiments.
