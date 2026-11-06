# Revised SM100 epilogue ownership plan

Original proposal after cleanup commit `1fab0dc8d9da5ac0f4ca81a9fecad7cda9e95729`. The references below are **only the CuTe DSL Rubin and Hopper implementations**, following the user's correction. Implemented as the separate follow-up recorded in `structure/README.md`; source and validation receipts are there.

## What Rubin and Hopper actually do

| Reference | Observed ownership |
|---|---|
| `rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:3341` | `_apply_swiglu_epilogue`, `_apply_situ_epilogue` (3413), `_apply_relu2_epilogue` (3512), and `epilog_*_copy_and_partition` (3540/3610/3648) remain methods of the kernel class in its implementation module. |
| `rubin/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:903` | The kernel owns output orchestration. It imports SDK epilogue partition primitives at lines 67–70 and defines local bulk-copy/reduction instruction helpers at 78–146. |
| `rubin/utils.py:32` | Utilities are pointer construction, scalar math, vector atomic primitives and PDL instructions. There is no complete epilogue class or phase implementation. |
| `rubin/inline_ptx.py:34` | Selected low-level gather/TMEM instruction wrappers are separated from the kernel, without moving full epilogue orchestration into generic utilities. |
| `hopper/contiguous_gather_grouped_gemm_act_fusion.py:978` | Activation, register layout/conversion, shared staging and output synchronization live in the kernel's epilogue block. Shared activation math is imported directly from `common.kernel_utils` at 76–83. |
| `hopper/contiguous_grouped_gemm_finalize_fusion.py:661` | The MMA/epilogue role owns per-subtile output processing and synchronization. Bulk copy/reduction helpers come from `.utils` at line 47. |
| `hopper/utils.py:25` | Shared SMEM layouts and TMA atom construction live here, followed by bulk instruction wrappers at 130–200. It does not contain a complete epilogue implementation. |

Neither architecture has a standalone `moe_epilogue.py`. Their consistent boundary is **kernel-specific epilogue orchestration belongs with the kernel; reusable low-level primitives belong in utilities**.

## Recommendation

Move `Sm100BlockScaledMoeEpilogue` and its six exclusive private helpers from `blackwell/utils.py` into the existing **`blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`** shared implementation module. Keep the epilogue as its own class and preserve all method bodies; do not inline its methods into the mainloop or duplicate it between FC1/FC2 adapters. Place the cohesive epilogue section before `Sm100BlockScaledGroupedGemmKernel`, after the existing private core helpers.

This is the closest match to Rubin/Hopper ownership and satisfies the concern about a general `utils.py` containing an entire backend phase. The shared implementation grows from about 2.2k to 3.2k lines, comparable to the existing architecture implementation style, while utilities shrink to primitive wrappers/reexports. It adds no file, wrapper, dependency cycle, or compatibility alias.

The previous dedicated `moe_epilogue.py` proposal is superseded as the primary recommendation. It remains a possible readability tradeoff, but would be a deliberate departure from these two architecture references rather than an existing pattern. Do not choose it solely to preserve the earlier proposal.

## Exact move boundary

| Definition | Current utils.py lines |
|---|---:|
| `_bulk_stmatrix4` | 102–118 |
| `_blockscaled_tmem_view` | 163–167 |
| `_blockscaled_rmem_view` | 170–174 |
| `_blockscaled_load16x32` | 178–187 |
| `_blockscaled_transpose16x32` | 191–242 |
| `_blockscaled_atomic_add_pair` | 246–267 |
| `Sm100BlockScaledMoeEpilogue` | 270–1184 |

The definitions contain 1,026 lines, excluding decorators/inter-definition comments. Preserve their original names, signatures, decorators, bodies and useful comments. Preserve copyright/license notices and carry any applicable provenance with the moved implementation.

Keep `release_gpu`, `blk_copy`, `blk_reduce_bf16`, and every existing common reexport in `blackwell/utils.py`. This specifically follows Hopper's shared bulk-primitive boundary. `release_gpu` serves prepare and the grouped core; W4A16 uses `blk_reduce_bf16`. The remaining existing callers need no edits. Remove only imports made unused by the move, and narrowly update the utility module description.

## Imports and dependency audit

The grouped core already imports all required SDK modules (`cutlass`, `cute`, `pipeline`, `ir`, `llvm`, `tcgen05`, `dsl_user_op`) and `ActivationType`. Add the same quantization dependencies the moved implementation already uses:

```python
from flashinfer.quantization.quantization_cute_dsl_utils import (
    _nvfp4_standard_quant_from_amax,
    float_to_ue8m0_fast,
    ue8m0_to_inv_scale_fast,
)
from ..common.kernel_utils import (
    f32_reciprocal,
    fmin,
    gelu_tanh_f32,
    situ_f32,
    tanh_f32,
    vectorized_atomic_add_fp32x2,
)
```

Replace the core's imported `Sm100BlockScaledMoeEpilogue` entry with `blk_copy` in its existing `.utils` import. The class name then resolves locally. The primitive dependency direction remains **grouped core → utils → common.kernel_utils**, plus direct common math imports like Hopper. There is no reverse edge.

Repo-wide searches found only one external reference to the epilogue class: this same grouped core. None of the six private helpers has a caller outside the current epilogue implementation. The FC1 adapter inherits the shared core. Package exports, W4A16, prepare, Rubin and Hopper utility callers remain unchanged. Therefore no alias reexport or compatibility shim is needed. There is no moved module-level mutable state or import-time initialization.

## Validation after authorization

Make this a separate structural commit on the newly committed cleanup. Verify byte/AST equality of all seven moved definitions and all retained utility definitions; preserve useful comments and confirm only import/header/module-description adjustments accompany the move. Run scoped lint/syntax/import checks. Use a fresh process and source-private DSL workspace so the old class module identity cannot mask import/lowering failures.

Reuse the existing source-paired core/codegen gate with cleanup commit `1fab0dc8` as control: output bytes, geometry/resources and normalized PTX/SASS should agree, allowing symbol/source-location changes. A short existing W4A16/prepare smoke confirms their utility dependencies remain intact. Adapt only active task-local diagnostics that directly import the old internal class location; preserve historical helpers and evidence. No numerical/tactic/cache-version changes, broad retuning, or new performance claim is justified by this structural move.
