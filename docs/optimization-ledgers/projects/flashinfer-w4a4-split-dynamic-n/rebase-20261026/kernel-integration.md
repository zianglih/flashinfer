# Kernel integration audit for PR #7290 rebase

Compared old merge base `a65d5b09e7e4c4c5c160b0161c48becd100b3970` with current upstream `84fb433aaec9ef3e978fbb7874c729257626d599`, and inspected retained implementation `74388819899d0abfd1a12102f7cc108bda13c812` plus the audited review checkout. Read repository CLAUDE.md review guidance and docs/code_review_guidance.md. Read-only source audit; no repository edits, Git ref changes, or GPU runs.

## Required reconciliations

- **Preserve upstream Rubin deterministic finalize (#6950).** The upstream Rubin FC2 kernel now accepts `use_fused_finalize` and emits a plain store to expanded rows when false. Keep that upstream kernel unchanged. In the PR's host `_get_compiled_finalize_kernel`, remove the old Rubin `not use_fused_finalize` rejection and pass the flag into `_sm107_finalize_kernel_cls()`. Keep its separate per-token and final-scale-dtype guards: upstream did not remove those limitations.
- **Fully replace old Blackwell FC1 implementation.** #6793 only changes its capability checker to permit channel N=192 for non-gated activation. This is a legacy A=activation/B=weight tile convention; it does not apply to the new A=weight/B=activation kernel. Keep the new capability adapter/shared core, not pieces of the old 4,000-line implementation. Do not add gated-specific N=192 branches to the new pipeline.
- **Update newly upstream tests to the new tactic contract.** `tests/moe/test_cute_dsl_mxfp8_moe.py` adds legacy `(tile,192)` FC1 tactics, a partial-channel rejection expectation, and direct calls to removed `is_valid_mma_tiler_and_cluster_shape(gated=...)`. Convert these to current `(channel_M,route_N)` tactics and valid partial channel coverage. Retain its ordinary ReLU2 cases, input-validation checks, and row-major scale-conversion test.
- **Retain new unified API wiring with current capabilities.** `runners.py` gained MXFP8 weight support but also copies old MX SiTU/unfused-finalize restrictions. The new shared Blackwell core supports these, so reconcile the runner activation capability map and `_check_support` with the replaced implementation. Preserve the upstream public `quant_mode="mxfp8"` spelling as an alias for the PR's `"w8a8"`, including runner/trace paths; do not silently discard newly merged call sites.

## Why legacy 192-channel tiles are unnecessary here

The shared kernel accepts output channel M tiles 128/256/512, routed-token N tiles 16/32/64/128/256, and requires logical channel dimension only divisible by 128. It does not require channels to divide the selected M tile. Thus upstream Nemotron width 2688 can use M256/M512 with its final partial channel tile, unlike the old FC1 whose N192 path avoided a missing partial-output predicate. `blackwell/utils.py` bounds every 16-channel write by output width; bulk epilogues skip an entirely inactive second CTA and preserve accumulator release. No new special-case numerical/device implementation is required by this upstream addition.

## Upstream changes to preserve without rewriting

- `flashinfer/cute_dsl/utils.py::convert_row_major_sf_to_mma_layout` converts checkpoint scales into the existing 6D MMA SF view. It does not choose gated weight row interleave; retain it unchanged. Its only new direct source consumer is the upstream layout test.
- `blackwell_sm12x/moe_w4a16_prepare.py` retains FP16 NVFP4 subnormal scales (#7433). This is an independent SM12x fix and should remain upstream, untouched by SM100/103 replacement.
- `flashinfer/cute_dsl/fp4_common.py::zero_swizzled_sf_padding` and fused norm callers are independent upstream work; retain unchanged.
- Cake grouped MXFP8 quantizer optimizations and Frost/Cake MoE changes are unrelated and should remain upstream unchanged.

There are **no upstream deltas** in the PR's shared Blackwell FC2 core, Blackwell `utils.py`, `moe_prepare.py`, `moe_finalize.py`, `moe_w4a16_kernel.py`, CuTe MoE `common/`, or `quantization/kernels/nvfp4_quantize.py`. The retained pipeline, resource planner, dynamic N, PDL, cache hints, combine numerics, and quantizer implementation can therefore remain byte-identical through this rebase.

## Import scan and validation boundary

Scoped upstream `git grep` over FlashInfer, MoE tests, benchmark routines, and examples found no new legacy-kernel consumers beyond the new MXFP8 test's capability assertion. Existing imports remain the host wrappers, tuner, package exports, and existing capability tests; their compatibility adapters are retained by the PR.

A first whole-tree grep in the partial clone encountered a missing promisor object (`6c3fdea87500227a66c7b8ed3cdcd2127c43293b`, requested via `37febb80a57f3a49e46d9e2ffff4efccda7aa138`). The narrower scan and all relevant `git show`/diff reads succeeded. No fetch repair was attempted by this audit.

This is static integration evidence, not a new GPU correctness or performance claim. After merge resolution, compare retained device ASTs, run host/selector/trace checks, and explicitly validate the changed upstream public alias and unified runner forwarding. A GPU smoke for the newly integrated MXFP8/ReLU2 partial-channel cases is useful if available; broad performance reruns are not implied by a kernel-identical rebase.

## Resolution applied in review checkout

On the later rebase of squashed `d3127e94` onto freshly fetched `f45e1d6fdd62833ff8aa922f9eb139d590002ff8`, resolved the owned three files without staging or changing Git refs:

- Restored the complete new Blackwell FC1 adapter from archived cleanup `6c3fdea87500227a66c7b8ed3cdcd2127c43293b`.
- Restored the host FC1 launcher from that archive, removing the auto-merged legacy `gated` capability-check argument that the new adapter does not take.
- Kept the archived shared host FC2 launcher with only the necessary upstream Rubin integration: remove obsolete unfused rejection and forward `use_fused_finalize` into the Rubin constructor.

`kernel-integration-validation.json` records byte and full AST equality of all seven Blackwell/quantizer source files against the archive, byte equality of the Rubin kernel against new upstream, and byte equality of host FC1 against the archive. A CPU test executing the extracted host `_get_compiled_finalize_kernel` with constructor/compiler stubs verified both fused and unfused forwarding, separate cache entries and reuse, plus unchanged per-token and non-FP32 router-scale rejections. The three edited files parse cleanly. No GPU runs were performed.
