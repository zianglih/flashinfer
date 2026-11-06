# Split top-k baseline native review

Read-only review of completed capture59138, source `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. No callable was invoked; no GPU work, recompile or profiler action was performed by this reviewer. Integration owns detailed divisor/SASS source attribution; this note establishes the independent resource/control facts for the later candidate comparison.

Capture paths: `baseline-fixed-{fused2,fused3,ordinary0}/` beside this note. Result hashes:
- fused2 `eaf9cf09714501998d4ca57114676c94296cf7709940cacf4d25cfed4d808297`
- fused3 `245b64281b6221a7d7975d1500f119af267e590d89d1648a34a50d121e44a73e`
- ordinary0 `ad679854feea3cc4f978bcad2f69afb0d922742fcfe20ed8fb52d72ad52eab0f`

All use real `_get_compiled_kernel`, M256/N256/K512/group8, C1 MMA128×64×256, M-major, activationNone, PDLFalse and CLCFalse; normal occupancy helper returns148. Fused num_tokens65/top_k2 or3; ordinary num_tokens0/top_k0 and absent optional pointers. Each result records `returned_callable_invoked:false` and the same source hashes. The successful capture precreated dump/cache directories, used KEEP=ptx,cubin, and disassembled separately. The earlier KEEP-SASS export failure remains separate evidence and produced no completed native admission.

| Fact | fused2 | fused3 | ordinary0 |
| --- | --- | --- | --- |
| SASS instruction rows | 1640 | 1640 | 1664 |
| registers / stack / local | 128 / 0 / 0 | 128 / 0 / 0 | 128 / 0 / 0 |
| static shared bytes | 1024 | 1024 | 1024 |
| constant bank0 / bank2 bytes | 1904 / 12 | 1904 / 12 | 1856 / 12 |
| GPU parameter declarations | 25 | 25 | 23 |
| PTX runtime div/rem sites | div.s32×3, rem.s32×1 | same | div.s32×1, rem.s32×1 |

All PTX targets are9.3/sm_103a, require512 threads, and declare extern dynamic shared memory aligned1024. Actual dynamic-shared launch size is **not recorded** by these exports. Cuobjdump's SHARED1024 is static storage, not the total. Role redistribution is four control `setmaxnreg.dec80` sites and epilogue `inc176`; transform warps keep the128-register launch allocation. No maxrregcount option was added.

**Baseline correction to the planning note:** the emitted runtime top-k arithmetic is signed32-bit division, despite the wrapper's Int64 annotation. Fused PTX sites2675 and2958 use `div.s32`; the scale remainder is lowered through arithmetic around the first division. The shared scheduler's `div.s32`/`rem.s32` at300/350 also occurs in ordinary0 (288/338), so a future candidate must not be judged by disappearance of every divide. Integration is tracing these sites to actual source and machine instructions; the planning phrase “runtime I64 division” must not be reused as an observed fact.

Fused2 and fused3 are byte-identical in both exported PTX and raw SASS, as expected from the baseline dynamic top-k parameter:
- PTX `76f19c2025f684ba7ca1dc4378282181857f99a04c2cd8d1713469ec3c6b3255`
- SASS `c7921e16d01ff84fd6ff79bf375a813b23c666823df04a2d6e0e73421e633dc8`

Ordinary0 comparison anchors:
- PTX `7116e64842c957a0d640e51e525f62589963d0f171826fe4e965636329ba83f5`
- SASS `6fbd931aceb7fe9b4549ac2764aa95b4b42744474c59a56523737c8e440550ed`

The source-fitter table predicts raw/B4, decoded3, ACC2, C1 fused or C2 ordinary for this geometry. Those counts are planning/source facts here, not a captured dynamic allocation report. For candidate comparison, preserve the same fixture and toolchain; check constant-divisor lowering at both fused division sites, GPU parameters, resources, and ordinary0 instruction/encoding/schedule identity while allowing intentional host ABI and source-line/symbol differences. No candidate or numerical result is yet established by this baseline review.
