# Static scale-factor selector experiment: rejected

Both variants are rejected before candidate launch. The static arithmetic proof is valid, but generated code spills shared common state and increases local loads. No numeric or performance result exists for either candidate; no quota or shape exception was added.

| Captured M512/N128/K8 MXFP4x8 FC1 | Retained 6be | R0 | R1 |
|---|---:|---:|---:|
| Initial registers | 168 | 168 | 168 |
| Stack bytes | 168 | 144 | 144 |
| LDL / STL sites | 21 / 21 | 48 / 19 | 48 / 19 |
| Non-NOP instructions | 4189 | 3974 | 3974 |

R0 replaces the two runtime scale-selector extractions with the statically known relative K byte. R1 additionally folds both selectors into the Python descriptor before the runtime N OR. R1 changes only one LOP3 immediate in the generated instruction stream compared with R0; resources and the new common-state spills are unchanged. The PTX, SASS and CUBIN files are not byte-identical.

The retained control passed all 39 exact cases and produced 76 captures. Both candidates failed the strict no-new-local guard on the first FC1 before its callable was returned. The smaller stack is not a benefit: common shared-storage, grid-stride and tile-count state now reloads from local memory in multiple roles and waits. R0 details are in `R0-RESULTS.md` and `r0-codegen-analysis.json`; R1 is bound by `r1/result.json` and its hash-verified evidence archive.

Source snapshots and patches preserve R0 `34fc7ac0` and R1 `a860045c`. The original 6be comparisons remain separate from later retained changes. The inactive local review copy was removed after all 514 guarded source hashes, the exact patch and the snapshot matched, with no untracked or staged files. See `retirement-proof.json`. All diagnostic scripts and raw evidence remain here; no GPU work is active for this experiment.
