# Explicit split-kernel behavior controls

Read-only inventory against `flashinfer-pdl-producer-drain-review` (core `fe188d180960c90bbd7d5e1d436cc180ef8b1b4171b8146af3061e47be506417`). The intermediate `is_fc1` clone was not GPU tested and was rejected by the user's interface correction; preserve it as an unmeasured draft.

The shared implementation should receive effects directly, while the existing FC1/FC2 public wrappers select their configurations. No new public API argument, role enum, monolithic configuration object, or default inferred from activation is required.

| Required internal control | Effect and current caller configuration |
|---|---|
| `prepare_input` | Host-only raw-token payload/linear-SF preparation; FC1 true, FC2 false. |
| `scatter_output` | Epilogue output mapping and final-scale metadata; FC1 false, FC2 true. Existing `use_fused_finalize` distinguishes expanded scatter from reduced output. |
| `per_token_scale_is_routed` | Original-token versus routed per-token scale indexing and pointer extent; FC1 false, FC2 true. Do not silently derive it from activation or scatter. |
| `k_steps` | Operand K tile choice selected with existing tile/dtype policy at the caller. |
| `num_stages` | Operand ring depth, including logical-M512/SF32 override, selected at the caller. |
| `overlap_epilogue` | Dedicated epilogue role/288 versus 160 threads, selected at the caller. |
| `overlap_activation_accumulators` | Existing transposed activation epilogue's overlapping-window/early-release mechanism. Keep this scheduling choice explicit rather than inferring it from scatter or activation. Core validates actual geometry/SF footprint. |
| `pdl_signal_at` | Required `startup` or `producer_exit`; FC1 startup, FC2 producer_exit. The latter signals before final ring drains. Validate exact choices, with no silent default. |

The bulk row-scatter implementation may still require `scatter_output`, a supported output type, sufficient SMEM, and its existing route geometry: those are capabilities of that memory operation. Its accumulator ownership remains associated with the actual bulk path. The separate activation-transpose overlap mechanism needs its own explicit control above.

Keep true activation semantics intact: gated channel count is membership in SwiGLU/GeGLU; ReLU2 remains ungated; `_activate` and all rounding retain their existing ordering. None can remain the mathematical identity activation, but must not choose routing, scheduling, scale indexing, or PDL placement.

Public FC2 capability adapter already rejects M512. The private common core can validate logical M512 structurally as group2/N128; this does not promise new public FC2 combinations. Existing public signatures, Hopper/Rubin/MegaMoE/W4A16 paths, and external tactic vocabulary remain unchanged.

Source inventory requiring replacement:

- Shared host `_run_blockscaled_gemm`: input preparation, M512 policy, independent cache entries for every behavior affecting generated code; two public wrappers pass explicit configuration.
- Shared Blackwell core: logical-M512 check; K steps, stages, epilogue roles; activation-window overlap; per-token scale extent; output extent; bulk-scatter capability; startup versus producer-drain signal.
- Shared epilogue: scatter metadata preload, route output identity, routed versus original-token scales; actual activation arithmetic remains activation-controlled.
- `fused_moe.py` activation normalization/gated dimensions are genuine math semantics; no role-driven edits identified there.

Before compilation, compare the new caller-selected configurations against the frozen producer-drain constructor for the supported tile/dtype/activation grid. Check K steps, stages, threads, accumulator stages/window overlap, SF/TMEM footprint, payload/SF layouts, output/scale extents, and signal placement. This is a CPU policy-refactor audit, not a reason to compile every combination. Runtime/codegen boundaries remain explicit afterward.
