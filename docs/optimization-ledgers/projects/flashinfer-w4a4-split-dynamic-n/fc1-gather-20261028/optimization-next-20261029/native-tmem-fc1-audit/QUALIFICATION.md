# Native-TMEM FC1 qualification

Candidate `6a48e87c41f2635f44e42d2c4afeaccc3b87d37be7d6b1be33ea8b685c0a073b` remains unstaged in `flashinfer-native-tmem-fc1-review`, based on9037. Current6be differs from9037 only in the W4A16 kernel; swap execution is unchanged. No API, weight layout, tactics, FC2 arithmetic, register quotas or stage policy changed.

- Scoped precommit passed. CPU coordinate/packed-word/reduction proof and independent actual-helper emulation passed.
- Initial13paired compile-only cases: unchanged resources, zero local storage; both representative FC2 binaries identical. Static instruction growth is substantial in wide cases, documented inCODEGEN.md; performance remains a measurement question.
- Final paired exact gate:39/39control and39/39candidate,76captured kernels each. All candidate resources and local load/store sites are no greater than the exact matching retained kernel.
- Two additional existing-oracle MXFP4x8/MXFP8 ReLU2SF32 cases passed,4zero-local kernels. No reference implementation was modified.
- Baseline qualification: M512/N128/K8 FC1 MXFP4x8 andMXFP8 already have168B stack and21LDL+21STL sites. These occur in MMA S2T descriptor work, not the native epilogue; both candidate counts are unchanged. The first strict-zero guard stop is preserved.
- All37FC2PTX pairs identical.35CUBIN pairs identical;2have only a consistent4-UR register permutation across12MMA instructions. All FC2 resources unchanged.
- Reclaimed-run partial evidence and complete replacement gates are separate archives. No incomplete runs or timing samples are stitched. No sanitizer.

The next screen is `../native-tmem-fc1-screen/predeclared-screen.json`:14cells, same-GPU C-A-A-C, frozen native winners/routes,100strictCUPTI samples, coldL2, stockclocks, and the existing per-kernel/component/clock observer. Selected benchmark kernels have a strictzero-local driver guard before launch. All rows will be retained; no retuning or source cleanup during the screen.
