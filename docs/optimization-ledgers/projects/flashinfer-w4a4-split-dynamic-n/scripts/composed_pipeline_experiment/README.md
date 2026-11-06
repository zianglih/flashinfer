# Composed pipeline validation at 442d2aa53

The immutable candidate snapshots match the committed production AST after import normalization. Control is1904964; the enclosing remote checkout was13ca1475, and explicit overlay hashes in every JSON identify the executed implementations. These are fixed-tactic diagnostics, not original-baseline AUTO retention evidence.

72 paired phase cases passed across six dtype/scale configurations, tails and per-token variants. All15 native configurations (three formats, N128 at4K/8K/16K and N256 at128/16K) matched final output bytes across the three adjacent arms. Each timing has10 warmups and all100 cold-L2 CUDA-graph CUPTI samples.

| Mode / N | Tokens | Order | Arm1 us | Arm2 us | Arm3 us |
|:---|---:|:---|---:|---:|---:|
| mxfp4-n128 | 4096 | B/A/B | 258.752 | 253.680 | 259.089 |
| mxfp4-n128 | 8192 | B/A/B | 431.362 | 417.825 | 428.625 |
| mxfp4-n128 | 16384 | B/A/B | 776.210 | 759.281 | 791.810 |
| mxfp4-n256 | 128 | A/B/A | 214.369 | 218.528 | 214.897 |
| mxfp4-n256 | 16384 | A/B/A | 727.346 | 792.611 | 799.506 |
| mxfp8-n128 | 4096 | B/A/B | 334.336 | 331.680 | 335.408 |
| mxfp8-n128 | 8192 | B/A/B | 494.817 | 455.760 | 485.440 |
| mxfp8-n128 | 16384 | B/A/B | 849.680 | 810.368 | 862.224 |
| mxfp8-n256 | 128 | A/B/A | 261.680 | 262.880 | 262.720 |
| mxfp8-n256 | 16384 | A/B/A | 800.112 | 826.096 | 802.032 |
| nvfp4-n128 | 4096 | B/A/B | 207.487 | 202.784 | 208.335 |
| nvfp4-n128 | 8192 | B/A/B | 321.839 | 305.056 | 321.760 |
| nvfp4-n128 | 16384 | B/A/B | 564.990 | 535.519 | 564.111 |
| nvfp4-n256 | 128 | A/B/A | 157.440 | 157.247 | 157.951 |
| nvfp4-n256 | 16384 | A/B/A | 568.671 | 576.239 | 570.943 |

B=current1904964 control; A=composed442d2aa53. B200 C1, nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, Torch2.12.0a0+5aff3928d8.nv26.05, CuTe DSL4.7.1. Native DeepSeek preparation/routing, seed42, H7168/I2048, top-k8,32 local experts; unfused finalizer and no per-token NVFP4. N128 uses FC1 logical M512/N128 and FC2 M256/N128; N256 uses M256/N256 for both. PDL enabled. No original B1 data was rerun.
