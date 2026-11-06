# FC2 per-token scale shuffle reuse: already eliminated natively

Read-only conclusion on retained `c1ac8ce7`: do not prototype a regrouped loop. In `_run_bulk` (`flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:1206`), adjacent packed multiplies and both TMEM halves request identical shuffle results. PTX retains repeated expressions, but PTXAS already shares the native results across all four multiplies. This is separate from pre-wait metadata motion; no source or GPU work was performed.

| Saved FC2 control | Full 64-token slab, inclusive PCs | SHFL.IDX | FMUL2 | TMEM loads | STSM |
|---|---|---:|---:|---:|---:|
| N128, two channel tiles, two CTAs, no overlap | `0x3d60–0x45d0` | 16 | 32 | 2 | 8 |
| N256, one channel tile, one CTA, accumulator overlap | `0x2ff0–0x3900` | 16 | 32 | 2 | 8 |

The ranges end at the first `UTMASTG.2D`, after both halves and all multiplies. Counting only through the first STSM would miss interleaved arithmetic. The sixteen native shuffles supply eight packed scale pairs; each pair feeds four packed multiplies (adjacent `i` pairs in both halves).

- **N128 witness:** `experiments/alpha-prefetch/qualification-extra/fetched/evidence/per-token-14-Relu2-control/codegen/01-Sm100BlockScaledGroupedGemmKernel.{ptx,cubin,sass}`. PTX repeats the same source/index shuffles at lines 1463/1465 and 1468/1469. Native `SHFL.IDX` at `0x3fc0/0x3fd0` produces R122/R123, then FMUL2 at `0x4040/0x4130/0x4140/0x4160` consumes that pair; its last use overwrites R122. Receipt records SF16/native K96, bulk64, PDL enabled, 128 registers and LOCAL0. Cubin SHA256 `d2ceb9514cb6b419481b7e54c49b1c336a1253fae87819f05929445b60cd6f25`; SASS `8ddbfa6caa5358534b401d11f542ccd643db87740138c99baf8728d7fb1c963a`; PTX `ed71c87f738941e8127dfb996e56d7864650ed2feb76bb3be9e52794fd7b9c2f`.
- **N256 historical witness:** `experiments/fc1-integer-store-gated/final-evidence/complete-evidence/per-token-10-SiTU-control/codegen/01-Sm100BlockScaledGroupedGemmKernel.{ptx,cubin,sass}`. Native shuffles `0x3110/0x3190` produce R124/R125, reused by FMUL2 at `0x3350/0x3360/0x3370/0x3390`. Receipt records SF16/native K96, bulk64, PDL enabled, 144 registers and LOCAL0. Cubin SHA256 `5c11b3841e22653a8f167595cdaf951aeeaabe9f7b437ce87fd0bba18bc31668`; SASS `8dc894c9247a709f3332b89e6808a1a3bef2710bdd36ad10c539b7a3f123983e`; PTX `c83f1ff06fb91d13b8de43721a3b4d7f3892b97658f2ca1f1c75ceee41118d7f`. This is an existing older capture, not a claim that the entire current kernel was freshly compiled at this geometry.

All listed artifact hashes were independently recomputed and matched their capture receipts. Both cases already achieve the proposed adjacent-pair and cross-half reuse, including the overlapping case's scale selection. A by-four source rewrite has no demonstrated duplicate native instruction to remove; retain the current loop.
