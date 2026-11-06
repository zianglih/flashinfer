# NVFP4 unified exact-reference review

Reviewer concern is valid by source. The unified typed-activation test calls the pure swap-AB reference without `mma_k_plans`; the default is K64 for NVFP4. On SM103, the actual launcher selects native K96 for E2M1×E2M1 with 16-element scale groups. Different accumulation update boundaries can change output bits. Static inspection establishes the mismatched contract, not which randomized cases fail at runtime.

## Correct plan contract

- Kernel stage depth is selected independently for FC1 and FC2 after automatic `k_steps`; observe the resulting `tile_k`, not only architecture or the public base tile.
- Native atom K64 and K96 give a 192-element group. Stage256 emits `(96,96,64)`; stage512 emits `(96,96,96,96,64,64)`. A final128-element tail emits `(64,64)`.
- The public NVFP4 contract requires K divisible by64, so the observer's per-stage decomposition agrees with the kernel's padded-stage formula. The local arithmetic audit checked128 K/stage combinations; GPU numerical validation is separate.
- FC1 is `scatter_output=False`, FC2 is `True`. Cache hits must update the selected phase plan, because compiled kernels can be reused after a different tactic was observed.

## Complete reference callsite scope

1. `tests/moe/test_cute_dsl_fused_moe.py`: the shared quant-mode reference helper and pinned per-token recipe test. Both already relied on the old observer and now use module-qualified reference calls.
2. `tests/moe/test_unified_moe.py`: typed activation test, the uncovered NVFP4 call. Its local reference import executes after the opt-in fixture is active.
3. `tests/moe/test_cute_dsl_mxfp8_moe.py`: MXFP8-only reference call explicitly uses SF32 and E4M3×E4M3. Native K32 matches the reference default; no K96 fix is needed there.

## Review of the three-file fix

No actionable issue found. Moving the unchanged observation machinery to an opt-in module-scoped conftest fixture and patching the reference module covers both binding forms. Main-module usefixtures retains its previous module-wide behavior; the unified test explicitly opts in. No unrelated MoE module is made autouse.

The fixture captures the original pure reference before patching, so the wrapper does not recurse or replace arithmetic. It observes compile metadata and cache hits without forcing tactics. Its temporary empty cache ensures every returned compiled object has recorded metadata. Missing selected phase data still fails rather than silently using K64. Module teardown restores `cute.compile`, the original cache, and the reference attribute. No production source, oracle arithmetic, tolerance, random input, or tactic selection changed.

SM100 uses the original reference unmodified. SM103 requires the separate hardware qualification requested by root; this audit performs no GPU run or public write.
