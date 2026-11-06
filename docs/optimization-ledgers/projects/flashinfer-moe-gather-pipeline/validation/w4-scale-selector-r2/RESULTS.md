# W4 scale-selector r2: ready for the bounded production screen

Unstaged helper `d3afcec4f966c4a30afc4bae528633f96dd4a9a787d712fa8333b1519cbb9ac3` on base82254e. The source diff is6 additions/3 deletions. R2 restores the original two-scale scalar path exactly and uses the fused byte selector only for already-packed32-bit words. It adds no runtime argument, pipeline state, tactic axis, register quota, or model/dtype policy.

CPU proof passes6,584 actual-wrapper AST cases and4,232 selector cases. Both original two-scale extraction branch ASTs are unchanged apart from assigning the constant byte index0. Decoder math and both toolkit instruction sequences are unchanged apart from the PRMT immediate. Scoped pre-commit and diff checks pass.

Four fresh candidate exact/resource runs passed on C2 B300 GPU7, using the existing zero-tolerance repository oracle and cases0/1/2/5. Their four control captures are reused from the completed r1 campaign with identical full source-manifest hashes; no stale-source timing or numerical result is relabeled. Both full manifests were verified before/after this campaign; per-process guards checked14 directly relevant files against derivative manifests bound to those full records. Source/copy provenance is in `evidence/source-manifests/` and `evidence/receipt.json`.

| Case | FC1 non-NOP control→r2 | FC2 | Finalizer |
|---|---:|---|---|
| 0: one CTA, static, swap, T1 |1431→1425|Raw cubin identical|Raw cubin identical|
| 1: one CTA, CLC, swap, T129 |1427→1421|Raw cubin identical|Raw cubin identical|
| 2: two CTA, static, swap, T129 |1742→1737|Raw cubin identical|Raw cubin identical|
| 5: two CTA, CLC, legacy, T129 |1669→1663|Raw cubin identical|Raw cubin identical|

Each FC1 removes six scale-selection SHFs; case2 also adds one R2UR. All FC1 cubins are byte-identical to r1's corresponding FC1 captures. All12 paired captures preserve resources; all24 loaded functions have zero local allocation, no LDL/STL, and zero reported stack. FC1 launch resources remain96 registers/640 threads; FC2 remains128/512. No register reduction is claimed.

The candidate-r2 snapshot is a full copy of immutable r1 with only this utility overlaid; its manifest records the parent manifest hash and exact one-file delta. The unrelated swap-AB FC2 writer experiment remains present in r2 but is not executed by these W4 tests. All actual captured W4 FC2/finalizer images are unchanged from822.

No performance or retention decision follows from this gate alone. Proceed with the authorized compact frozen-winner EP/TP production screen. If retained, the shared MegaMoE inherited-helper path still requires the GLM5 regression comparison described in `../GLM5_PLAN.md`. No sanitizer or distributed GPU work was run here. GPU7 was verified idle after qualification.

Raw artifact archive: `evidence.tar.gz`, SHA256 `f621ec13b30f105bef7182b5bc00b7416ac48c02b8a836471840108ec8467d27`,2,890,058bytes. `evidence/codegen-summary.json` contains complete resources/opcode deltas and raw cubin hashes. `fc1-r1-equivalence.json` proves FC1 reuse across r1/r2. The first freeze helper invocation had a Python quoting syntax error before executing any remote statements; its log is preserved, and the corrected invocation completed before validation.
