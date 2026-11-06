# Upstream wiring integration audit

Read-only comparison of review working tree at `74388819899d0abfd1a12102f7cc108bda13c812` plus cleanup, old base `a65d5b09e7e4c4c5c160b0161c48becd100b3970`, and canonical clone `origin/main = 84fb433aaec9ef3e978fbb7874c729257626d599`. Review clone's remote ref was still at old base when inspected; use canonical clone's fetched object. No source edits or Git mutations made.

## Must preserve from current upstream

- `b92f1129554c2dfc5c9c993867ddc50f4b6aedd5` (#6793) publishes MXFP8×MXFP8 as `quant_mode="mxfp8"`, adds unified `CuteDslRunner` registration/packing, `CuteDslConfig.prepare_activations`, shared `convert_row_major_sf_to_mma_layout`, unified benchmark support, and tests. Our branch uses `w8a8`; accepting only that string breaks both newly upstream public calls and the unified runner. Normalize the upstream alias into our canonical internal mode (or adopt the upstream canonical mode with the branch spelling retained as an alias) at functional, wrapper, tuner and trace boundaries. Do not duplicate kernel paths for the aliases.
- Keep main's `CuteDslConfig.prepare_activations` and activation quantization contract: E4M3 `[M,H]`, row-major E8M0 `[M,H/32]`, no swizzled activations. Keep upstream `runners.py`, `flashinfer/cute_dsl/utils.py`, design docs and unified benchmark changes unless a targeted integration adjustment is necessary.
- `5240384d` (#6950) adds deterministic Rubin finalize. The retained host `_get_compiled_finalize_kernel` still rejects `use_fused_finalize=False`; remove that stale rejection and pass the flag into the main Rubin constructor. Keep the Rubin kernel byte-identical to main. Keep upstream removal of the Rubin unfused-finalize test skips. Do not restore our older host factory wholesale.
- Preserve unrelated main additions in API Frost docs, SM120 FP16 scale handling, CAKE, and grouped Frost. They are not ours to revert.

## Full Blackwell implementation replacement

- Keep our shared `Sm100BlockScaledGroupedGemmKernel`, FC1 capability adapter, activations on physical MMA N, up16/gate16 Blackwell gated weights, private independent K depths, CLC schema and `blockscaled_route_n_v4` cache identity. Do not restore upstream's old gather kernel to preserve its newly added N192 tactic.
- Upstream's FC1 channel-N192 tests encode the old operand orientation. Their tactics `(routing_tile, ((routing_tile,192),...),...)` are invalid under the replacement physical contract. Update those existing tests to exercise current channel-M/routing-N tactics and retain the numerical ReLU2 + 2688 intermediate workload. The generic old `is_valid_mma_tiler_and_cluster_shape(...,gated=...)` test needs to be rewritten against current `can_implement`, not emulated by keeping stale code. Current M128 supports the 2688 workload (21 channel tiles).
- Main's direct MXFP8 tests use `quant_mode="mxfp8"`; keep those as alias/API coverage. Their input rejection regex expects `float8_e4m3fn weights`; our stronger check currently says `torch.float8_e4m3fn GEMM1 and GEMM2 weights`, so align the assertion or message without weakening validation.
- Use one weight preparation implementation, not separate main and branch copies. Reuse upstream's small shared quantizer closure if helpful while preserving our architecture-selected 16/64 gate interleave and explicit MXFP8 scale bytes. Delete stale docs claiming unified MoELayer does not support MXFP8×MXFP8.
- Do not add upstream's optional private `weight_dtype` override to our core merely to satisfy conflict markers: our dtype is already validated from both weight tensors and inferred without a second override policy. The unified runner does not pass this new argument.

## Unified runner policy needs deliberate reconciliation

Upstream `CuteDslRunner` advertises per-format activation matrices and rejects both SiTU and unfused finalize for MXFP8 activations (W4A8 and MXFP8×MXFP8). Our replacement supports both. If exposing the replacement consistently via unified API, remove those obsolete restrictions, preserve SM107 rejection, and add SiTU for the two MX pairs. Existing `tests/moe/test_unified_moe.py` has explicit expectations at the support matrix and `test_cute_dsl_w4a8_requires_fused_finalize`; update those tests to the new accepted contract rather than leave registry tests inconsistent. This is a necessary small `runners.py` delta, not a second wiring implementation.

## Trace cleanup must survive

The cleanup reference fixes are broader than upstream's MXFP8 addition: decode all MMA-layout weight scales, reinterpret NV E4M3 bytes, undo architecture-correct gated interleave for all quant modes, and honor local expert offset. Keep this implementation and normalize the `mxfp8` alias before its existing `w8a8` branches. Taking main's reference wholesale would restore the NV/W4A16 layout bug.

## Focused validation

- CPU/static: alias normalization at all entry points, unified support matrix/activation preparation registration, source-conflict scans, private tactic parsing/cache v4, direct-parent and single-commit diff assertions.
- Targeted GPU if available: upstream ReLU2 MXFP8 workload on current tactics; unified MXFP8 call through main runner; one gated W4A8/W8A8 SiTU unfused case if enabling the unified matrix; existing cleanup trace CPU harness.
- Existing six benchmark tables remain historical evidence for `74388819`; do not relabel them as measured at the rebased commit.
