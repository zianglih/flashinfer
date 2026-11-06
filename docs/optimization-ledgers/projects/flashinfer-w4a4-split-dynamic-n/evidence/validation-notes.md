# Validation during development

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. The latest pushed review checkpoint is `d9074cb6e9e934d387e358a069e90ddf084f5ef7`; earlier checkpoint-specific checks below retain their original scope. These are development checks, not retained performance evidence. Subsequent load-path experiments must be checked separately.

- Existing capability suite: 18 passed (remote `logs/capability-01.log`).
- Existing `test_gather_gemm_k_tail`: 48 passed after retaining K64/K192 alongside K128/K256/K384/K512, token counts 1/17, route capacities 16/32/64/128 (`logs/smoke-19.log`).
- Repository-wide `pre-commit run --all-files`: passed; complete output in `evidence/pre-commit-all.log`.
- The old up64/gate64 bring-up failed its SwiGLU numerical assertion (63.81% within atol 0.05), `logs/smoke-20.log`. The up16/gate16 epilogue resolves this warp-ownership error. The failed log remains diagnostic history, not evidence for the final layout.
- Mainloop phase probe: 30 configurations gave exact FP32 FC2 results with random FP4 codes, power-of-two scales, reverse scatter, K tails and persistent reuse. Gated FC1 is being diagnosed separately.
- Final up16/gate16 synthetic epilogue probe: 8192 coordinate checks, 44 full variants, and 374 poisoned-tail/masking checks passed. Quantized scales/codes had zero mismatches; nonuniform per-token scales and reverse mappings passed. See `TMEM-layout-audit.md` and remote `logs/probe-epilogue-05.log`, `logs/probe-epilogue-06.log`.
- Existing full-MoE smoke at `00e4ff61`: deterministic SwiGLU per-tensor, ReLU2 per-token, and W4A8 N128 bias-off: 3 passed in 291.93 seconds, including native JIT, remote `logs/smoke24-up16.log`.
- Existing invalid-tactic rejection cases at `65392416`: 6 passed in 0.52 seconds, remote `logs/tactic-guard-65392416.log`.
- Shared-layout W4A16 compatibility: six bit-exact old64/new16 cases across 1-CTA, 2-CTA and cluster2 tactics, SwiGLU/SiTU and counts17/33/65. W4A16 arithmetic is unchanged.
- New benchmark helper: both homogeneous MXFP8 and mixed MXFP4×MXFP8 candidate T4 unfused pipelines completed with native dynamic-bucket AUTO. These are runtime smokes, not numerical reference checks or comparative performance evidence.

The first full NVFP4 checkpoint sweep regresses and is not retained. Raw artifacts and summary are preserved under `evidence/nvfp4-screen-65392416/`. Broad correctness and sanitizer runs remain deferred until an optimization passes performance retention, as requested.

Resolved bring-up issues: restore vector-copy offset alignment; issue TMA copies with whole-warp participation; use separate tail pipeline states; count packed GMEM bytes for mixed FP4 TMA transfers; mask SF selector bits without sign extension. These fixes are internal implementation details and do not change the logical quantization contract.

Per-token audit: FC1 retains `alpha[expert] * input_row_scale[original_token]` before activation. FC2 retains `alpha * (routing_weight * intermediate_row_scale[permuted_route])`, including its BF16/FP16 routing-dtype rounding point. The external per-token quantizer and high-level orchestration are unchanged.

At `de4f1aa4`, the existing capability and tactic-enumeration targets passed 31 cases (4 warnings, 0.30s), remote `logs/capability-tactics-de4f1aa4.log`. Its three complete full-grid performance screens are preserved and still regress, so broad validation remains deferred. See the project README for the screening ratios and raw evidence paths.


## Integrated checkpoint d9074cb6

Committed/deployed/pushed d9074cb6e9e934d387e358a069e90ddf084f5ef7. Separate read-only review found no actionable correctness issues in geometry, dynamic-N B offsets, full-N SFB replication, local-to-cluster completion relay, accumulator/TMEM lifetimes, scratch separation and cache/tactic contracts. All seven changed files passed pre-commit.

Remote existing checks: `tests/moe/test_cute_dsl_moe_can_implement.py`, `tests/moe/test_cute_dsl_fused_moe.py::TestTacticEnumeration`, and `tests/moe/test_cute_dsl_fused_moe.py::TestKernelInputValidation::test_tactic_matches_weight_layout_architecture`:49passed,4deprecation warnings,0.48s; log `logs/capability-tactics-d9074cb6.log`. Focused unified raw/activation smokes and the102 paired epilogue comparisons are detailed in the two-CTA and epilogue experiment notes. These do not replace broad existing numerical/sanitizer validation, which remains deferred until retained full-pipeline performance.

Full13token screens for all3 requested modes use the frozen original helpers and existing B1s. Fused finalize is disabled, NVFP4 is per-tensor, normalAUTO and10/100cold-L2 CUDAgraph/CUPTI are retained. Checkpoint source remains frozen during measurements.

All three d907 full-grid screens completed and failed aggregate retention (NVFP4 0.897578x, MXFP8 0.973208x, mixed 0.942054x). No A2/B2 rerun. The 39 rows and all 78 B1/A1 cache hashes were verified; raw archive SHA256 `c50a783a371618573554901177c5641d46d7c8cafe1814224bd1d725557f61dc`. Full tables: `combined-screen-d9074cb6/summary.md`.

## Small-N overlap checkpoint 94be9a71

Committed/deployed/pushed `94be9a712a46ab34b902605c4a34d26a4c570692`. Changed-file pre-commit passed; 306 focused paired exact cases across all six formats, per-token FC1, partial tiles, tails, pipeline wrap and sentinels passed. Existing d907 capability/tactic checks are reused with their original commit scope. Full three-mode AUTO screens completed with old B1s reused; overall NVFP4 0.924794x, MXFP8 0.996456x, mixed 0.973007x. No A2/B2 or broad sanitizer runs. Verified 39 rows and 78 cache hashes; archive SHA256 `fac140b23d53b99932fe050c651ad7f4bf167d687ed5108ec0cdc3f1a65658b1`. Current public draft: https://github.com/flashinfer-ai/flashinfer/pull/7290.

## Combined load/store checkpoint 7829fc00

Committed/deployed/pushed `7829fc00dc7121341cc40cd4190660507e006490`. Both changed files passed commit hooks. FC1 reordering passed 24 dtype/SF/per-token/short-K paired cases and exact native FC1 output/SF checks; N256 improved 2.54–2.86% in paired phase timings, N128 was neutral. FC2 bulk epilogue passed 50 output/metadata + 24 all-format + 24 channel-tail cases, with exact native pairs; strongest gains are NVFP4, other formats have geometry-dependent tradeoffs. Separate read-only review checked shared-memory bounds/ownership, bulk-copy completion, PDL visibility and metadata rounding; identified inactive-channel guard was fixed before integration. Primary three-mode screening launched; previous B1 remains unchanged.

Final 7829 full-grid screening completed and verified: 39 rows and 78 cache hashes. Overall B1/A1 NVFP4 0.933210x, MXFP8 1.002184x, mixed 0.975097x; not retained as a performance win. No A2/B2. Raw archive SHA256 `c1be0474ee40d6c1abc52651bf4b1092644fd892d4069b20c3dcdb8c28430843`, 82 files / 1,543,316 bytes. Full current evidence is in `combined-screen-7829fc00/`; all prior observations remain archived. GPU benchmark/profiling processes have completed.
