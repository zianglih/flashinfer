# PR #5319 numerical and memory contract audit

Audited base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095` to head `ca2692a62679336301758d1b83b193b3c5b1170c`, following `CLAUDE.md` and `docs/code_review_guidance.md`. Read all five changed files, the native finalizer, JIT flags, W4A4 and W4A16 callers, and retained validation scripts/results. No GPU work was performed in this audit.

## Findings

**No blocking numerical or memory-correctness defect found in the new BF16 finalizer.** Confidence is high for the statically verified contracts and exercised B300 configurations; this is not proof for every architecture or every tactic.

- **Vector bounds and layout:** `moe_finalize.py:99–151` maps each CTA to one token and hidden tile. Each lane starts on a multiple of eight BF16 elements; the host requires hidden size divisible by eight and aligned contiguous storage (`:191–209`). Therefore the start-column predicate also covers the complete 128-bit access, including H264 tails. Vectors and CTAs partition the hidden dimension without overlapping stores.
- **Routing:** expanded mode uses the mapping only as a signed validity mask and computes `token * top_k + slot`; permuted mode uses the actual nonnegative row address, including row zero (`:116–139`). Invalid rows are rejected before pointer dereference. All-masked tokens store exact positive zero. Data row offsets are promoted to int64 before multiplication (`:103,129,138,150`). Valid mapping values remain an internal caller precondition, matching native behavior; `moe_sort` owns this contract.
- **Numerics:** the ordered per-slot FP32 `fma.rn.ftz.f32` (`:27–33,128–145`) matches native `moeUnpermuteKernel`'s ordered float accumulation and the default fast-math compilation (`csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:160–209`; `flashinfer/jit/core.py:692,721–722`). There is one BF16 conversion after the reduction. NaN-poisoned unavailable rows do not participate.
- **Dtypes:** W4A16 runner explicitly requires BF16 input/output and FP32 scales (`tuner.py:1047–1048,1221–1226`). W4A4's FC2 already requires BF16 output via `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:588–596`; the new helper's BF16 check does not introduce an FP16-output regression. The helper also permits FP16/BF16 scales, but these are helper-level contracts, not a claim that W4A16 accepts those scale dtypes.
- **Cache and graphs:** kernel cache includes device, hidden size, top-k, scale dtype, thread/vector geometry, PDL, and layout (`moe_finalize.py:217–226`). Token count and all addresses remain runtime parameters. The current-device guard precedes current-stream lookup and launch (`:227–265`). Host checks read tensor metadata only. The output and scratch buffers used by current callers are separate.
- **PDL boundary:** every expert-output read follows the dependency wait, and the terminal dependent signal follows the output stores (`:123–154`). Metadata prefetch relies on the documented earlier routing completion invariant; a separate pipeline audit covers that producer-chain invariant.

## Evidence inspected and limits

- Final shared helper: all **200** standalone permuted cases have `passed=true`: 192 nonempty byte-exact native comparisons and eight zero-token no-op cases. Cases cover token boundaries 8/9 and 1024/1025, H264/H7168, top-k 3/8, FP32/BF16 scales, cancellation/random data, EP8/all-masked routing, row zero, NaN padding, graph replay with changed mapping/data, and PDL off/on.
- All **52** final W4A16 pipeline phase cases record exact baseline/candidate, graph/eager, and PDL-on/off equality. Native accuracy is also checked for **40** small/partial phase cases; the 12 production/4096-token phases are exact comparisons without a separate numerical oracle. Input hashes and identical configuration checks prevent unmatched A/B comparisons.
- The 30 native test run is retained; the two cluster-padding native cases are fused controls. The separate eight unfused H384/N17 pipeline phases cover partial-tile behavior directly.
- Historical W4A4 standalone artifacts include subnormal/FP16 coverage (963 cases on an earlier helper revision), plus 96 later geometry-boundary cases. These must remain labeled historical; the final shared helper did not rerun the full FP16/subnormal matrix. This limitation is already in the PR.
- No compute-sanitizer run, full suite, non-B300 GPU, or exhaustive CTA-tactic matrix is established by these artifacts. These are validation limits, not demonstrated defects.

## Small cleanup opportunities

1. **P3 / high confidence, clarity only:** rename `_fma_rn` to `_fma_rn_ftz` or explicitly call out FTZ in its local rationale (`moe_finalize.py:27–33`). The explicit FTZ is intentional native-parity behavior and should remain visible to a future maintainer who might replace the inline assembly.
2. **P3 / high confidence, formatting only:** reflow the split sentence “Negative mapping entries skip their / row entirely” in the helper docstring (`:171–173`).
3. No native fallback, alias-overlap scan, or device-side route-bound scan is warranted for this private helper: current callers establish separate buffers and valid routes. Adding speculative recovery would expand the scope and graph/launch cost without fixing an observed defect.
