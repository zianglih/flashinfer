# Kernel and custom-pipeline concision review

Frozen against `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2` in the shared independent `flashinfer-simplicity-review-20261027` clone. Only the grouped blockscaled core and Blackwell `custom_pipeline.py` were edited; changes remain unstaged. Their combined diff is **+28/−76 lines**.

- Removed the unused `PipelineCpAsyncUmma._compute_is_leader_cta` and the fence-only `pipeline_init_wait` forwarding helper. The latter's two callers now issue the same `cute.arch.mbarrier_init_fence()` directly; neither default behavior nor deferred-fence behavior changes.
- Centralized bulk-output scratch eligibility in one host scalar used by K admission and final storage planning. Reused the existing scale-column sum for TMEM allocation, removed the one-use `_metadata_bytes` forwarding method, and kept the accumulator layout local to `__call__` rather than saving redundant object state.
- Removed the physical-M validation already implied by the immediately preceding logical-M validation and channel decomposition: logical 128/256/512 produces physical 128/256/256.
- Merged five adjacent identical compile-time IKET guards. Marker call order and enabled/disabled operations remain identical.
- Preserved original useful comments/docstrings. The only standalone text correction replaces the stale cp.async A/SFA gather claim with its current narrow activation-SF role. Comments attached to removed helpers disappear with those helpers.

The full operand, accumulator, CLC, startup PDL, epilogue, and teardown paths were read. Their existing ownership and special-case explanations remain; no new abstraction, dtype/shape branch, tactic, numerical change, pipeline change, or synchronization removal is introduced. The local cp.async publication fence, count-three cluster join, aligned metadata layout, common empty owner, terminal joins and bulk-store wait ordering remain intact.

## Completed local evidence

- Read `CLAUDE.md`, `docs/code_review_guidance.md`, and the retained synchronization receipts. Repository reference searches found no caller of the removed CpAsync helper, and only the two replaced callers of the local fence wrapper. Rubin imports its own pipeline module.
- `check_kernel_cleanup.py`: **67,500 constructor configurations**, including **4,500 identical rejections** and **63,000 identical final host storage plans**, across five operand formats, all fifteen admitted M/N geometries, K4/K8/AUTO, explicit/AUTO stages, static/CLC, inline/dedicated epilogues and bulk/fused/quantized-output flags. All original constructor attributes and epilogue configuration remain equal; the sole added host scalar equals the former scratch predicate.
- After splitting adjacent IKET guards and normalizing the removed temporary object attribute, all remaining core AST is identical outside the explicitly checked host constructor/planner edits. Pipeline AST is identical after docstring removal and replacing the old fence wrapper call with its exact body; only the dead helper is excluded.
- Scoped pre-commit passed, including mypy, Ruff check/format; Python compilation and `git diff --check` passed. `kernel-static-equivalence.json` pins exact source hashes. The dtype/capacity stubs exercise real extracted host methods; they do not substitute for actual CuTe layout compilation.

## Required emitted-code validation

Before integrating the combined cleanup, reuse the existing source-paired gate against `ed67c485`; no new upstream tests or performance sweep are required for this cleanup. Check the current 60-core matrix (including static/CLC, 1/2 CTA, narrow/wide SFB, M512 two-channel, both PDL modes and bulk/tail epilogues): source-paired output bytes, selected K/stage/TMEM/shared-memory values, spill counts, UMMA/barrier counts and normalized PTX/SASS should remain equal for these two-file changes. Symbol/source-location differences are not executable differences; explain any actual instruction difference instead of treating it as intended.

Additionally, one existing 1-CTA and one 2-CTA IKET diagnostic build should preserve marker order and source-paired outputs, since only enabled marker guards were combined. The default nondeferred custom-pipeline fence is source-equivalent by exact inline-body comparison; the production core uses the unchanged deferred path. No GPU run, timing claim, or sanitizer claim was made by this subtask.
