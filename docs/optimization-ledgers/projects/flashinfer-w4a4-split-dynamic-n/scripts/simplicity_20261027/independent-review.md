# Independent simplification review

**No actionable findings. Approved for the planned focused validation.** Reviewed all seven final file diffs against `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`, after restoration of the separate FC1/FC2 scheduler plumbing. The exact full-index patch SHA is `d7cb185e35f55c39c67eb3ae0a0edaf5f9aa1838a777cdd26d6afd39bf4c1087`.

The checkout has only the seven expected unstaged source changes, no staged changes and no untracked files. [independent-review.json](independent-review.json) pins every source file, repository guidance and supporting static receipt. The review followed `CLAUDE.md` and `docs/code_review_guidance.md`, including kernel logic, allocation, interface and cache scrutiny. Original useful comments are preserved; no cosmetic trimming is requested.

## Device metadata and layout

- In `blackwell/utils.py:840`, `_scatter_metadata` is the former direct-scatter calculation extracted without changing its route mask, expanded-row mapping, per-token lookup, multiplication order or BF16/FP16 scale rounding. Both register tensors retain their previous initialization for inactive lanes. The helper returns register tensors; it adds no shared buffer, barrier or runtime policy.
- The bulk call at `blackwell/utils.py:915` safely passes `None` for final routing scales. `bulk_tokens > 0` is derived by storage planning from the constructor's bulk eligibility at core line 304, which requires scattering, a BF16/FP16 output, no output-scale generation, and **no fused finalize**. The only `token_final_scales` dereference is inside `cutlass.const_expr(self.use_fused_finalize)`. That branch is absent from the bulk specialization. Uniform scaling still uses its original separately rounded `uniform_scale`; per-token scaling retains the old operation order.
- No store/transposition, TMEM release, tail masking or bulk-group wait moves in this refactor. The direct fused branch remains the old calculation, while bulk execution cannot select it. No new fused-path coverage is required by this source review.
- `blackwell/moe_prepare.py:165` centralizes the same packed-FP4/FP8 reduction-to-scale-column conversion used by allocation and preparation. Allocation still rounds capacity to canonical 128-row SF atoms; `prepare` retains its source/destination counts, pointer alignment, dtype and routing checks. The common validation now rejects invalid scale geometry before division. For admitted inputs, preparation arguments and the generated kernel are unchanged.

## Launcher and tactic invariants

- `_run_blockscaled_gemm` has exactly two repository callers: FC1 and FC2. Both previously passed `num_stages=None`, `overlap_epilogue=True`, `num_tile_info_stages=1`, and `prefetch_weights_before_wait=enable_pdl`. Supplying these constants directly to the constructor at common-wrapper lines 280–286 removes duplicated plumbing without removing a currently varying behavior.
- Deleting those constants from the compiled-kernel key is safe. `enable_pdl` remains keyed and determines prefetch. Deleting `prepare_input` from that key is also safe: it selects host-side routing preparation before pointer creation, not a constructor or compile argument. The resulting activation dtype/alignment contract is unchanged, and all actual device specializations remain keyed, including scattering, routed per-token scales, activation, PDL boundary, routing publication, cache hints and scheduler choice.
- `tuner.py:356` only deduplicates construction of phase-specific parameter dictionaries. Blackwell and Rubin sub-tactic decoding remain explicitly separate; tuple/list values and the two `gemm1_use_clc_scheduler`/`gemm2_use_clc_scheduler` keys are preserved. `fused_moe.py`, `prepare.py` and `runners.py` are byte-identical to the baseline, so independent phase scheduler controls remain available outside the shared autotune flag.

## Core and pipeline cleanup

- The centralized bulk-byte predicate matches the old final planner. The additional route-width term does not change automatic K selection: `_select_k_steps` and `_k_stage_capacity` already exclude bulk scratch for route tiles below 128.
- Logical M128/M256/M512 validation and channel decomposition imply physical M128/M256, so the removed second physical-M guard was redundant. The reused scale-column sum is identical to the former TMEM allocation expression.
- The accumulator layout is passed directly from the same fragment construction; no consumer requires its former temporary object attribute. The metadata-size forwarding function and the leader helper have no remaining callers.
- Each removed `pipeline_init_wait` call is replaced with the helper's exact fence-only body under the same `defer_sync` condition. No synchronization is removed. Combining adjacent identical compile-time IKET conditions preserves marker order and enabled/disabled behavior.

The helper abstractions have specific purposes and reduce actual duplication. None introduces a new mutable policy, dtype/shape branch or tuning axis. No unrelated API, MegaMoE, Rubin kernel, benchmark or test changes are present.

## Validation boundary

Supporting receipts report 67,500 constructor cases, 2,176 tactic extractions, 2,160 launcher cases and 51 admitted SF geometries; those checks were performed by the implementation agents, not rerun during this review. This review independently read the final source and verified the exact freeze hashes. CuTe lowering can still change resources after extracting a JIT helper, so the already planned source-paired compilation/output/codegen gate remains the completion criterion. No source edits, tests, GPU launches, new clones or performance claims were made here.
