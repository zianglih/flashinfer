# PR7290 interface audit

- Review checkout: `flashinfer-cleanup-review`, starting at `33b7e5260132eb4ba2fdfdd97bd71a892f04a481`.
- Reviewed the complete owned-file PR delta against merge base `002529e1`; did not import changes from newer upstream main.
- Changes remain unstaged. No source outside the assigned interface ownership was edited; no GPU, benchmark, sanitizer, commit, push, or GitHub action was performed.

## Retained cleanup

1. Removed the duplicate swap-AB tactic-parameter extractor. The five-field canonicalizer still validates the same input, and the runner forwards the two K depths and separate FC1/FC2 CLC behavior arguments. It then decodes the original three GEMM fields with the existing Blackwell/Rubin extractor. This introduces no reverse import: the parent tuner imports the child canonicalizer, then calls its own extractor.
2. In `launch_gather_gemm`, use the existing `quantize_output` argument directly instead of copying it to `generate_sfc`. Forward and return `out_scale` directly: the existing nonquantized branch rejects any non-None output/global scale, while the quantized branch allocates or validates the same scale buffer. The useful original explanation of explicit quantization remains.
3. Removed the unused explicit `swap_ab` parameter from private `CuteDslMoEWrapper._forward_with_tactic`. Its existing `**kwargs` accepts the runner keyword; execution still uses `self.swap_ab`. Public constructor, functional API, `run`, and configuration signatures remain unchanged.

## Scope decisions

| Component | Audit result |
| --- | --- |
| `blackwell/moe_swap_ab.py` | Only the redundant output-scale alias/conditionals changed. Kernel selection, pointer preparation, cache keys, PDL/cache policies, architecture admission, routed output shape, and FC2 validation are unchanged. |
| `blackwell/moe_swap_ab_tuner.py`, `cute_dsl/tuner.py` | Reuse the existing decoder. Preserve all 360 swap-AB tactics in exact order, the default automatic-depth tactic, all 23 W4A16 tactics, shared CLC selection, JSON canonicalization, cache keys and validity filters. |
| `cute_dsl/fused_moe.py` | Only the ignored private argument was removed. Core dispatch, wrapper resource lifetime, standalone per-token quantization contract, fused/unfused behavior and Rubin localized execution are unchanged. |
| `blackwell/moe_w4a16.py` | Keep shared preparation and explicit 16/64-row layout forwarding; no new heuristic or tactic change. Its existing low-level test caller also uses the explicit layout argument. |
| `api.py`, `__init__.py`, `prepare.py` | The public `swap_ab` option and row-interleave helper are needed to express and prepare the new weight-layout contract. Keep defaults, exports, device validation and both layout contracts. |
| `runners.py` | Keep bound-candidate lookup, legacy direct-runner default and swap-AB cache isolation. The Rubin availability fallback predates this PR and is not an unpublished compatibility shim. |
| `trace/templates/moe.py` | Keep same-dtype reference support, actual layout un-interleave and local-expert offset forwarding; they express changed execution contracts rather than cosmetic rewrites. |
| `docs/design_docs/flashinfer_moe_api.md` | Keep the small MX SiTU support qualification, including its swap-AB/Blackwell restriction. No prose or license churn. |

The upstream `ALL_MOE_TACTICS` alias, legacy graph-tuning configuration, and Rubin fallback remain because they existed at the PR base. No new API knob or fallback was introduced. No unresolved blocking interface issue was identified in the owned diff.

## Validation

`interface_proof.py` extracts the actual old/new source functions and runs CPU logic with dependency stubs; it does not import CUDA or replace the repository's GPU tests.

- Exact equality of the 360-tactic catalogue/order and default; 23-tactic W4A16 catalogue/order.
- 2,904 old/new swap-AB forwarding comparisons covering all tactics/defaults, Python/JSON forms, per-token/output arguments and caller override precedence.
- 27 identical invalid-tactic exception type/message results.
- 30 unchanged legacy Blackwell/Rubin forwarding cases.
- 288 mocked gather-launch output/scale forwarding cases, including successful and rejected dtype/quantization combinations.
- Four private-wrapper cases proving the wrapper-owned layout still determines dispatch.
- AST equality for the core/kernel-cache/finalize launchers, validity filters, public wrapper methods, unchanged tuner initialization/cache methods and the entire W4A16 runner methods.
- Scoped pre-commit passed all applicable hooks, including mypy, Ruff lint/format and whitespace checks. `git diff --check` passed.

Artifacts: `interface-proof.json`, `interface-precommit.log`, `interface-cleanup.patch`, and `interface-receipt.json`. The root's planned existing exact/API GPU suites remain the runtime validation boundary; this audit adds no repository tests.
