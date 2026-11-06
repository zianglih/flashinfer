## Scope

@humansand

Track bit-exact, zero-tolerance reference testing for FlashInfer low-precision quantization and SM100-family CuTe DSL MoE/GEMM. This tracker includes only FlashInfer PRs authored by `zianglih` that introduce or extend the exact contract or its coverage.

Checked items are merged; unchecked items are open. Superseded PRs are listed separately.

## Tracked contract

- **Independent references:** compare quantized payload/scale bytes or final output storage bits against an independent arithmetic reference with zero tolerance. Backend parity and repeated-run determinism alone do not establish this contract.
- **Shared arithmetic:** reuse quantization oracles across standalone operators and MoE references. Document the supported APIs, backends, rounding modes, scaling inputs, and accumulation/combine order alongside each reference.
- **Explicit boundaries:** historical strict NVFP4/4over6 coverage does not imply that every fast-math configuration was exact. Per-token 4over6 uses the online AMAX; per-tensor quantization uses its supplied scale. Each PR defines its finite/non-finite coverage.

## Merged quantization foundations

- [x] https://github.com/flashinfer-ai/flashinfer/pull/3264 — Adds NVFP4 4over6 reference/testing for per-tensor and per-token quantization, with zero-tolerance agreement for strict-math configurations.
- [x] https://github.com/flashinfer-ai/flashinfer/pull/3387 — Adds exact MXFP8 reference checks, fixes CuTe subnormal scale conversion and scale-output initialization, and extends strict per-tensor NVFP4 exact tests to CuTe DSL.
- [x] https://github.com/flashinfer-ai/flashinfer/pull/3448 — Extends CUDA/CuTe exact coverage to per-token NVFP4 and 4over6, including MAE/MSE, full-dequant and FP16-domain candidate scoring, layouts, and zero inputs. Closes the CuTe per-token/4over6 coverage gaps left by #3387.
- [x] https://github.com/flashinfer-ai/flashinfer/pull/7501 — Unifies native MXFP4/MXFP8 quantization behavior and exact tests, consolidates standard/4over6 and strict/fast NVFP4 references, and fixes exposed quantization edge cases. Standalone quantization scope; no CuTe MoE end-to-end changes.

## Merged W4A16 exact references

- [x] https://github.com/flashinfer-ai/flashinfer/pull/5019 — Introduces the independent W4A16 reference and finite BF16 storage-bit assertions, including signed zero, for deterministic MegaMoE. Atomic FC2 reduction retains a separate rounding contract.
- [x] https://github.com/flashinfer-ai/flashinfer/pull/6277 — Extends the exact coverage to small-token/N32 tactics, routing boundaries, empty/refill behavior, and CUDA graph replay while preserving the shared reference.
- [x] https://github.com/flashinfer-ai/flashinfer/pull/7196 — Shares the W4A16 reference across deterministic MegaMoE, non-fused split CuTe DSL MoE, and full-K dense CuTe DSL W4A16 GEMM; aligns activation and standalone combine rounding. Fused TMA-reduce finalize and dense split-K/stream-K remain outside the exact contract.

## Active extensions

- [x] https://github.com/flashinfer-ai/flashinfer/pull/7976 — Ready for review. Hoists the independent global reciprocal in standard-fast CUDA NVFP4 while preserving #7501's encoded-byte zero-scale contract. Adds exact midpoint-boundary coverage for FP16/BF16, ordinary/TMA paths, and single/batched APIs. Performance follow-up for #7962; matched benchmark results, SASS analysis, and validation limitations are in the PR.
- [ ] https://github.com/flashinfer-ai/flashinfer/pull/7290 — Incorporates the shared bit-exact reference and zero-tolerance SM100/SM103 swap-AB CuTe DSL MoE coverage from #7372, including per-token NVFP4, for non-distributed execution with non-fused finalize. Reuses standalone quantization references and includes the manual all-tactic sanitizer script; current validation and remaining limitations are recorded in the PR.

The active work keeps fused TMA-reduce finalize, dense split-K/stream-K exactness, and CAKE backends outside the requested expansion. Validation details and remaining limitations belong to the individual PRs.

## Superseded standalone PRs

- https://github.com/flashinfer-ai/flashinfer/pull/7372 — Closed without merging; the bit-exact reference/testing and manual sanitizer script are consolidated into #7290.

## Related tracker

- #4561 — CuTe DSL W4A16 MoE implementation and follow-ups.
