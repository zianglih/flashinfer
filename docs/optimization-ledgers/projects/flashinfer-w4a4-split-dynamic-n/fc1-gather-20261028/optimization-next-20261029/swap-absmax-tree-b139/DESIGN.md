# Balanced FC1 absolute maximum

One unstaged change on retained b139, in `flashinfer-swap-absmax-tree-review`: replace the serial 16-element `_absmax` fold with a compile-time balanced tree. The original values stay untouched for quantization/store. The final `fmax(+0, tree)` preserves the all-NaN and signed-zero identity. No tactic, dtype dispatch, allocation, synchronization, API, weight layout, quantization conversion, or FC2 behavior changes.

This is a dependency experiment, not a claim that 32 scalar instructions become fewer. Existing captured SASS already combines `fmax(maximum, fmax(v,-v))` pairs into eight `FMNMX3` instructions with absolute operands, but the destination feeds the next reduction. A balanced tree could shorten that chain while retaining compiler fusion; it can also increase instructions or register liveness. Reject if generated cost/resources worsen without a compelling mechanism.

References:

- Current `moe_swap_ab_kernel.py:666–671`, `_absmax`; gated calls at855 and nongated calls940/945. Per-token BF16 FC1 does not generate scales and should compile unchanged; it is a useful control, not an affected arm.
- Rubin MegaMoE `kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_epilogue.py:421–441` uses a serial `max.xorsign.abs` fold with final sign clear. It supports optimizing reduction representation, but copying it directly would discard the existing FMNMX3 compiler fusion and is not proposed.
- Retained control sample `native-tmem-fc1-audit/codegen-evidence/codegen-control/capture/002-fc1.sass` shows the R21/R22 serial FMNMX3 chains around0x3e70–0x4360. This is a prior source-equivalent `_absmax`, not fresh b139 codegen evidence.

The exact extracted Python ASTs pass55,184 CPU cases under IEEE fmax-number semantics, including signed zero, subnormal, infinities, all-NaN and mixed NaN. Actual GPU compilation/numerics still require the paired gate.

Qualification: run39 existing exact cases on b139 and candidate, capture all owned kernels, compare exact test+geometry resource records before candidate launch. No new stack/local/LDL/STL, unchanged120/128/256 role quotas, FC2 identity, unchanged per-token BF16 output kernels, and actual max-dependency/instruction accounting are required before any timing. Known wide-MX M512/K8 baseline spill is recorded and cannot grow. No sanitizer or new repository tests.

## Separate next mechanism for root

Rubin's `TmemTranspose32x32Inplace.from_r1_perm_until_last_store` at710–755 interleaves two fragments by transpose phase. Current helper423–474 fully executes top then bottom at paired callsites824–826 and899–902. It can preserve the existing ownership/atoms while issuing independent work earlier. Source halves are disjoint16x32 row slices; destination halves are disjoint32x16 column slices, but both R2 loads must complete before either R2 store because destination slices overlap the other source half. All initial accumulator reads must precede R1 scratch writes; retain the final fence/release after both R4 loads. Root owns this separate prototype, so it is not included here.
