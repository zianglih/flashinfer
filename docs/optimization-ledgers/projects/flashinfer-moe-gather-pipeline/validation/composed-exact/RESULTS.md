# Composed exact/resource qualification

The immutable `candidate-composed` snapshot is retained base `82254e20` plus the FC2 writer-only bulk commit, static SF-byte selector, and W4A16 PRMT-byte selector. Only the swap kernel (`788b7f58…`) and shared W4 conversion utility (`d3afcec4…`) differ from the base. All 13,245 source hashes passed before and after this campaign.

Six zero-tolerance calls using the existing repository oracle passed on original-node GPU0. All 18 captured kernels have zero stack/local memory, no LDL/STL, verified PTX/cubin/SASS hashes, and passing native register/resource guards. GPU0 is idle and released. No timing, autotuning, sanitizer, repository test edits, or compiler-option changes were introduced.

| Mode / existing helper case | Coverage | Actual FC1/FC2 CLC | FC1/FC2 registers |
|---|---|---|---:|
| W4A4 / 10 | K96, N256, one CTA, PDL | false / false | 168 / 118 |
| W4A4 / 11 | K96, N256, two CTA, partial K | false / false | 168 / 122 |
| MXFP8 / 8 | wide logical M512, two CTA, PDL | false / false | 168 / 118 |
| W4A16 / 1 | swap layout, one CTA, PDL, partial token tile | true / true | 96 / 128 |
| W4A16 / 5 | legacy layout, two CTA, partial token tile | true / true | 96 / 128 |
| W4A4 / added helper case 13 | 4096 tokens, native SM budget and production CLC selection | true / true | 168 / 76 |

The first five cases preserve the earlier correctness-only active-SM/cluster limits; W4A16 explicitly selects CLC in the helper. The final W4A4 case omits the helper's SM cap, provides enough allocated work for production dispatch to select CLC, and asserts `use_clc_scheduler=True` on both actual compiled kernel instances. It uses the same existing oracle and launch wrapper, with no production-source overrides. The bounded swap calls are not described as CLC coverage.

The six W4A16 GEMM/finalizer cubins are byte-identical to the corresponding earlier R2 qualification at the same cases. The combined swap changes therefore do not change those W4 native executables.

Evidence: `evidence/{receipt,guard,idle-postflight}.json`, per-case exact output/native resource/artifact receipts, `qualification.json`, and the source-bound helper copy. Archive SHA256: `94b321bd34c7a4abca30c23e9746eb5140f971a4a1b7651c6192be16234ade1d`.
