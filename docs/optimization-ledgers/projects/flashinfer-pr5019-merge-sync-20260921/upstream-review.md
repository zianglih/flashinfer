# PR #5019 merge integration review

Reviewed the merge of upstream `c62cf664` into PR head `ad0a5e5`, following
`flashinfer/AGENTS.md`, `CLAUDE.md`, and `docs/code_review_guidance.md`.

Scope: PR-added or modified W4A16 MegaMoE code, the SM100 vendor-package move,
shared MegaMoE helper exports, and inherited split W4A16 behavior. This was a
read-only source audit; the merge owner performed the fixes.

## Required integration fixes

- Replace PR-only `kernel_src.cutedsl_megamoe` imports with
  `kernel_src.sm100.cutedsl_megamoe`, including the relative import in
  `backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/weights.py`. Upstream
  `b549effe` moved the vendor package; the old path does not exist.
- Pass `m_cluster_aligned=False` from `Sm100W4A16MegaMoEKernel._make_mixed`
  to `_MegaMixedInput`. Upstream `0ef005a2` added that required constructor
  argument. `False` is conservative: MegaMoE inherits layout and decoder
  helpers, while the flag is consumed only by the split kernel epilogue and
  finalize paths that MegaMoE does not invoke.

## Checks and results

- Compared upstream `0ef005a2` changes to `moe_w4a16_kernel.py` and
  `moe_w4a16.py` against `_MegaMixedInput` and its call sites. The PR's
  `_finish_transform_stage` hook survived the automatic merge; the split
  default retains its original fence/release/commit order and MegaMoE
  retains its override.
- AST-scanned the PR's `cute_dsl/megamoe/bf16_nvfp4/*.py` imports after the
  path fixes: **52 imported symbols, 41 unique; zero missing public/lazy
  exports** in `kernel_src/sm100/cutedsl_megamoe/__init__.py` and its
  `shim/kernel_helpers.py` export map.
- AST-checked every entry in the helper module's `_LAZY` dictionary:
  **34 targets; zero missing target modules or symbols** under the moved
  vendor `src/` tree.
- Compared the merge-base-to-upstream changes in `moe_ep/core` and
  `backends/mega/kernel/sm100/common`: no core interface changes; the only
  shared-common change updates the MXFP8 weight helper's vendor imports.
- Inspected upstream `79caeb70` MiniMax SwiGLU additions. They extend the
  NVFP4/W4A4 backend and do not change the helper signatures consumed by
  the W4A16 implementation.
- No additional merge-introduced issue was found in this bounded scope.

## Limits

Static source and AST inspection only. This audit did not import CUDA/CuTe
modules, compile kernels, run GPU or multi-rank tests, or revalidate numerical
or performance claims. It did not review every upstream change or perform a
fresh full correctness audit of the pre-existing PR implementation. The three
text-conflicted test files were handled separately by the merge owner and
test reviewer.
