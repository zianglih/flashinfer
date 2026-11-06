# Warp-uniform scheduler route metadata

Independent b85 clone `../../flashinfer-clc-route-uniform-20261027`. Apply the route metadata candidate and one additional `cute.arch.make_warp_uniform` around its scheduler-published route load in `next_work`. All active lanes in each participating role load the same metadata stage; the helper executes before the release arrival. Keep the existing converged consumer arrival count and all ownership unchanged. Only the newly published route is annotated; no extra fields, public policy or tactic changes.

The first unannotated candidate passed 40 exact replays but increased static SASS by 99 instructions with up to 10 more registers. This isolated follow-up must demonstrate actual codegen improvement rather than exchanging the division for shuffles or divergence. Reuse the completed clean b85 control with identical source/helper/config hashes. Preserve both previous candidates and receipts.

Deployment initially stopped before any GPU execution because the newly generated source receipt used abbreviated Git index lines. Regenerated the exact same source diff with full-index encoding required by `prepare_workspace_cache.py`, verified every source hash remotely, and completed cache setup. No source file changed during that correction.

## Result and decision

All 40 paired replays passed with 20 core pairs and unchanged source hashes. No local spills or pipeline/storage changes. The annotation does not improve codegen: 19 of 20 SASS files are byte-identical to the unannotated variant; the remaining no-PDL per-token FC2 file only reorders R2UR instructions and register-reuse flags. Static instruction totals and resources are identical to that variant: net +99 instructions versus b85 and maximum +10 registers. This is consistent with changed register allocation and uniform-path pressure from carrying the extra live metadata value, rather than a missing uniformity declaration. Both route variants are unretained; no E2E timing was run. GPU0 was verified idle after the gate. Raw results and provenance are in `results/`, independently verified by `validate.py`, with compact decision in `decision.json`.
