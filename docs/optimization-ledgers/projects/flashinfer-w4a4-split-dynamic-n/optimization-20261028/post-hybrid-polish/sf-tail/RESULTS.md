# Final-stage SF-prefix qualification

The frozen candidate passes the focused source-paired gate: **532 storage-bit replay comparisons, 152 GEMM codegen pairs**, on one B300. This qualifies the scale-copy prefix change for the separate performance screen; it is not a retention or speedup claim.

- Retained source: `61c2c367009340ca0ed218511ed9382512860f1b`.
- Candidate kernel: `3b926e6ffb54542f8cd540a117bbfab7547c5c93f8d7bc747562d187538bf2c8`; patch: `8dc685ee1467d92c0a94114b67c6679144c8ddf3d220af202f257ee6877509bb`.
- Only `moe_swap_ab_kernel.py` is changed, unstaged, in `flashinfer-sf-tail-review`. Scoped pre-commit and whitespace checks pass.
- The remote checkout retains the earlier physical Git head `61249e0b`; all 348 source hashes explicitly match retained `61c2c367` before the candidate's single-file change. Source provenance does not rely on relabeling that Git head.
- Runtime: NVIDIA PyTorch 26.05, CUDA toolkit/ptxas 13.2.78, CuTe DSL 4.8.0, PyTorch `2.12.0a0+5aff3928d8.nv26.5.50603568`, Python 3.12.3, driver 595.91.07. GPU7 on `fi-moe-descriptor-recover-1028` was exclusively used and is released. Native compilation caches remain intact; compiler output directories are private.

The change copies only the complete four-scale words needed by the last logical K stage, while retaining all source/target strides and the K96 dynamic-N row-bank remap. All 67 synchronization, pipeline-state and fence call ASTs are unchanged. Operand TMA sizes and compiled TMA load-site counts are unchanged. This reduces SMEM-to-TMEM scale work, not global-to-shared TMA transfer volume.

| Gate | Shape H / I | Paired replays | GEMM pairs |
|---|---:|---:|---:|
| Four formats, N16/N256, one/two CTA | 640 / 640 | 140 | 40 |
| Remaining one-CTA formats and logical M512 | 640 / 640 | 140 | 40 |
| Aligned stage controls | 512 / 512 | 84 | 24 |
| NVFP4/per-token K64 FC2 tails | 640 / 576 | 112 | 32 |
| NVFP4/per-token K192 FC2 tails | 640 / 704 | 56 | 16 |
| **Total** | | **532** | **152** |

Each source executes those 532 CUDA-graph replays, for 1,064 executions total. Coverage includes CLC/static scheduling, PDL on/off, one/two CTA, route tiles N16/N64/N128/N256, logical M128/M256/M512, and balanced, skewed, empty, reactivated, full-tile, one-row-tail and half-tile-plus-one routes. Live FC1 outputs/scales, per-token requantization intermediates, final outputs and route metadata match exactly. The activation is SwiGLU; unchanged activation arithmetic is not independently requalified here. No full pytest or sanitizer run was added.

All 24 aligned pairs have byte-identical PTX and identical opcode/resource counts; 21 also have identical encoded SASS. Three MXFP8 FC2 pairs exhibit assembler variation from identical PTX. All 152 pairs' scale-copy-site changes exactly match the expected bank/word reduction. Static non-NOP counts change by −454…0 and general registers by −59…+2. Local-memory and stack usage remain zero. **Uniform-register spills are not uniformly improved:** one-CTA per-token N128 FC2 gains 26 spill/fill pairs with static scheduling and PDL off, and four pairs in each CLC variant. These exceptions remain part of the timing decision.

Two unchanged-control setup failures are preserved and excluded from the passing totals. The initial H=I=576 case failed the existing grouped SF-row layout admission before a kernel ran; H640/I576 retains the intended FC2 K64 tail with admitted output channels. The optional MX64-tail attempt failed the public MXFP8 requirement that H and I be divisible by128, before candidate compilation. No production admission rule was changed. The passed MX128 tail is the public-contract boundary.

The separate fixed-winner screen has **31 affected FC2 cells** (2 EP, 29 TP), **81 scaled aligned controls**, and 32 unchanged W4A16 controls. FC1 is aligned in every cell. `screen-classification.csv` records the explicit K-step/tile-K derivation and removed copy words for all112 scaled cells; no default or automatic K-step resolution was required.

Evidence: [qualification.json](qualification.json), [codegen summary](evidence/raw/codegen-summary.json), [raw verification](evidence/verified.json), [runtime](gate-runtime.json), [screen classification](screen-classification.md). The archive has 1,326 hash-verified files, SHA256 `71a3f3aa71fb9a98140fa7fd30c3fe7856f94186c9dcddaa83c4679feb2fa541`. Raw failed attempts and all compiler outputs remain in the archive. `qualify.py` and `analyze_codegen.py` reproduce the checks without GPU work.
