# FC2 native16 bulk offset correction

Source: `flashinfer-fc2-narrow-bulk16-offset-review`, independent unstaged clone at clean0c. R1 remains frozen. Two inherited files from bulk16 R1 plus generic routing/scaling metadata offsets fix16-token slabs used within N32+ tiles. For32/64-token slabs the changed formulas are algebraically identical.

Patch: `3d09bce11b296e205a93ee538c1080d6cb949feeb3877fce75b7a215acc793e4`; source pins in `evidence/fc2-narrow-bulk16-offset-r1/source.json`.

Gate on C2 B300 GPU7 passed81 byte-exact initialized-output comparisons against clean0c:45 existing cases plus36 forced16-slab cases for N32/64/128, all three formats, BF16/FP16, per-token scales on/off, and reversed row mapping. Candidate-only task-local policy instrumentation forces16 for the extra cases with explicit3 operand stages; it does not edit source. The control uses the same cases and3 operand stages with its original epilogue. Every forced choice was observed during compilation. Full output includes untouched padded bytes. Source hashes remain unchanged before/after. Scoped pre-commit passes.

Evidence: `gate.json`, `control.stdout`, `candidate.stdout`, `*.stderr`, `candidate.patch`, and `pre-commit.log` under the evidence directory. No repository tests added, no sanitizer, no performance run for this correction. Parent's R1 fixed timing showed only tiny gains, so this remains a correct reviewable local experiment, not retained production.
