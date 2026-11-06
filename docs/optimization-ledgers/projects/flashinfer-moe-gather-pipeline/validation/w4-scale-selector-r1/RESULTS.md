# W4 scale-selector r1: exact/resource qualification passes; mixed codegen

Four paired cases passed on C2 B300 GPU7. Both source manifests were verified before/after the campaign; the 14 directly relevant source files were verified before/after every process with a derivative manifest bound to the full source-manifest hash. All eight exact calls used the existing zero-tolerance repository oracle. Tests cover one/two CTA, static/CLC scheduling, PDL on/off, swap and legacy layouts, FC1 gather and FC2 regular TMA. The correctness-only active-cluster cap and explicit CLC override were not used for any performance measurement; no timing was run.

The candidate is immutable `candidate-r1`, base82254e with the scale helper40111f87 and an independently owned swap-AB FC2 writer change. W4 launches only the W4 kernels/finalizer; the shared helper is its only changed executed production path. Native compiler arguments were unchanged; PTX/cubin retention is artifacts-only. All12 paired captures have equal resources, zero local allocation, and zero LDL/STL instructions. FC1 uses96 initial registers and640 threads; FC2 uses128 and512. Finalizer cubins are byte-identical.

| Case | FC1 non-NOP C→A | FC2 non-NOP C→A | Relevant changes |
|---|---:|---:|---|
| 0: one CTA, static, swap, T1 |1431→1425|1383→1391|FC1 removes6 SHF; FC2 adds8 net instructions|
| 1: one CTA, CLC, swap, T129 |1427→1421|1365→1373|FC1 removes6 SHF; FC2 adds8 net instructions|
| 2: two CTA, static, swap, T129 |1742→1737|1625→1633|FC1 removes6 SHF/adds1 R2UR; FC2 adds8 net instructions|
| 5: two CTA, CLC, legacy, T129 |1669→1663|1561→1569|FC1 removes6 SHF; FC2 adds8 net instructions|

FC1 uses already-packed32-bit scale words, so the new immediate selector removes six shifts while preserving eight duplication PRMTs. FC2's two-scale fragment constructs a16-bit packed word from its scalar byte values; native lowering adds four `IMAD.SHL.U32` and four `LOP3.LUT` packing operations. It also swaps one `LEA` for one `IMAD`. Total FC2 PRMT/SHF counts are unchanged. This is not an unconditional instruction-count win.

Recommendation: before timing r1, preserve the original two-scale scalar representation (pass byte index0) while using the selected-byte permutation for existing32-bit words. This keeps an existing representation branch rather than adding a model/dtype policy; it should avoid the newly introduced repacking. New source freeze/native qualification is required for that r2. No r1 performance or retention claim.

Artifacts: `evidence/receipt.json`, per-process exact/resource/source receipts and complete native code under `evidence/runs/`, `evidence/codegen-summary.json`, paired FC2 scale excerpts, analyzer and fetch helper. Archive SHA256 `34c6589889dec7b1319038d8520293fa345cfea5cff6602f8c444b99e24eb5ee`,958088 bytes. Initial native routing setup genuinely rebuilt within the persistent CPP cache (~7.2minutes); subsequent source-arm/test processes reused it and took about8seconds. GPU7 was idle after qualification.

An initial quick counter included `NOP;` in its non-NOP total. The final analyzer strips the mnemonic terminator and explicitly excludes NOP; the table above and saved JSON are corrected. Full raw code remains available.
