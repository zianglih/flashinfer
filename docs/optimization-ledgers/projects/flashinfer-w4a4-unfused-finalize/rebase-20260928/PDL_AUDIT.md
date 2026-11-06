# PR 5319 synchronization audit after 2026-09-28 rebase

- Reviewed old base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`, new base `07e519fcc149f39e6dd00264149c092c2e37767e`, and rebased candidate `bde427290b33c55489e39c75d7e2a25365358ca0`.
- Read `flashinfer/docs/code_review_guidance.md`; kernel implementation, masking, bounds, synchronization, and comment accuracy were in scope.
- This was a read-only source review. No source edits, GPU execution, GitHub operations, or environment changes were made by this reviewer. GPU validation is owned by the root task.

## Conclusion

No substantiated synchronization defect introduced by the rebased PR. Confidence is high in the source-level dependency chain, metadata readiness, zero-work CTA coverage, and preservation of producer tails. Compiler lowering and device execution still require current-head GPU validation. Historical September 18 timing and test evidence must not be presented as current-base measurements.

The conflict resolution correctly preserves upstream dual-tile routing, `gemm2_partial_out`, `skip_unpermute`, prepared-callable capture, TMEM fences, unaligned named barriers, and worklist changes. The diff remains six files, 306 additions and eight deletions. W4A16 host/kernel files were unchanged upstream between the old and new bases, so the previous W4A16 ordering proof carries over.

## Relevant upstream changes

| Change | Relevance | Rebase disposition |
| --- | --- | --- |
| `05ebb2d7`, #5430, Kimi-K3 W4A8 MXFP4 SiTU MoE | Shared FC1/FC2 changes, optional pre-wait PDL hint, row-group worklists, dual-tile core, prepared plans, native routing ABI, TMEM synchronization | Preserved; new hint remains separately after FC2 wait |
| `97b3bd80`, #5609 | Per-token NVFP4 quantizer now has register-resident row processing, early launch signaling, thread-count dispatch, and kernel-side padded-scale initialization | FC2 still waits before consuming quantizer output; current-base tests/performance required |
| `7d967939`, #5504 | Per-token alpha and optional quantizer `out_scale` fold | MoE call retains default fold behavior; not superseded by this PR |
| `6870e3ff`, #5108 | FC1 K-tail load guards and existing coverage | Preserved, unrelated to finalizer replacement |
| `07e519fc`, #5456 | CUDA 13.4 CI image changes | New upstream base; no synchronization-code consequence |

Native `cuteDslKernels/moeUtils.cu` is unchanged over this range. The native sort binding in `csrc/moe_utils_binding.cu` did change: new Python passes extra dual-tile arguments. A September 17 native `moe_utils` module is not an assumed-compatible overlay target for this base. Use a matching current native ABI/nightly or rebuild the specific required native module. Do not interpret an ABI mismatch as a regression in this PR.

## PDL contract

CUDA requires every primary CTA to signal or finish before its dependent grid may begin. Signaling alone does not make the unfinished output safe; the dependent wait establishes primary completion and global-memory visibility. Overlap is opportunistic, and correctness must not depend on overlap. See [CUDA Programming Guide: Programmatic Dependent Launch](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html). This PR preserves those boundaries.

## W4A4 per-tensor and per-token

Current lines refer to rebased candidate source.

1. Core sorting remains a non-PDL launch by default: `fused_moe.py:419–430` does not pass `enable_pdl`; `moe_utils.py:586` defaults it to false. Supported core and prepared-plan callers supply routing buffers rather than an override. The routing metadata and route weights are ready before the FC1/FC2 chain begins.
2. FC2 retains its unconditional wait at `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1649`. The new elected MMA-warp hint is after that wait, at `1653–1656`, and outside every tile-validity predicate. It therefore covers zero-work CTAs and empty expert-parallel shards.
3. Existing cluster initialization precedes the wait/hint. The rebase preserves all `UnalignedNamedBarrier` conversions and TMEM fences around accumulator production/reuse. Bulk-copy commit/wait and epilogue synchronization remain at `2446–2448`; no FC2 store or producer tail moved.
4. The shared finalizer reads routing metadata before its wait (`moe_finalize.py:115–125`) but every BF16 expert-row read is after that wait (`129–145`). Negative mappings are masked before dereference. All-masked tokens still wait and then write zeros.
5. For per-token activation, current upstream quantization waits before input reads, includes padded-row scale initialization, and may signal after loading its row into registers while quantization/stores continue. This earlier hint does not weaken FC2's wait: FC2 still waits for the quantizer's completed outputs and scales. The quantizer does not mutate the finalizer's route mapping or weights.
6. The old W4A4 tail hint remains. Repeated hints from the same CTA have no further scheduling effect; removing it is unnecessary churn without measured benefit.

## New upstream early-hint option is not equivalent

Upstream's optional `pdl_trigger_early` executes at FC2 lines `1647–1648`, **before** the existing wait at `1649`. Its wrapper documentation says after the dependency wait, which does not match the code. This is an upstream documentation mismatch, not a demonstrated runtime bug.

The rebased PR correctly keeps its after-wait hint separately. Simply substituting `pdl_trigger_early=True` would change the ordering being justified. Current explicit use of that option for this FC2 is the MXFP4 split-wide **fused** path (`mxfp4.py:1256–1259`), where the new unfused hint and new standalone helper are not used. Other similarly named early options belong to FC1 or swap-AB kernels and are untouched.

## Dual-tile and prepared MXFP4 paths

- Core base and alternate FC2 launches preserve their original order and shared output/worklists (`fused_moe.py:615–684`). Each kernel keeps its wait. The new hint is after that wait even for the zero-work variant selected by routing.
- If the main `enable_pdl` is true, the alternate FC2 waits for the preceding grid before signaling. If only `dual_alt_pdl` is true, the standalone helper launches without PDL, retaining full ordinary stream serialization. Neither combination allows its routing preloads to precede the non-PDL sort.
- `skip_unpermute` remains the first branch at `687–691`. The generic helper runs only in the following branch; its callable and kwargs are retained at `705–709`, so prepared replay captures the new helper without losing the output buffer reference.
- The current public dense MXFP4 plan's optional two-stage path uses `skip_unpermute=True` and `gemm2_partial_out` (`mxfp4.py:2414–2416`); `Mxfp4MoEPlan._prepare` constructs `plan_finalize_rows(..., expanded_rows=True)` from that buffer, and replay runs it after the FC2 calls. That separate finalizer does not enable PDL, so the new FC2 hint cannot relax its ordinary stream ordering.
- Small prepared routing can bypass native sort only when the plan supplies fused routing without PDL. Under PDL it retains the captured non-PDL sort before GEMMs (`mxfp4.py:779–802,826–843`).
- Internal W4A8 core now supports unfused output upstream, although `CuteDslMoEWrapper(quant_mode="w4a8")` still rejects it. Do not claim all internal W4A8 unfused paths are impossible. The current public MXFP4 two-stage plan bypasses our helper as described above.

No introduced metadata-read hazard was found in these supported call paths.

## W4A16

1. W4A16 sort passes its PDL setting, unlike W4A4. Native permute waits before reading sorting metadata (`moeUtils.cu:79–80`) and signals outside its per-route loop (`101–102`), including no-local-route cases.
2. FC1's existing weight-warp early signal remains at `moe_w4a16_kernel.py:1477–1479`. Routing is already ready through native permute.
3. FC2's activation warp retains its dependency wait at `1397–1398`; the new elected hint follows at `1401–1405`, before the work loop. Thus every launched CTA reaches it, including invalid work tiles.
4. FC2 only reuses the hidden/permuted-input workspace after waiting for FC1, which has finished reading it. No stores moved. The unfused TMA `producer_tail()` remains at `2334–2335`; the old tail hint is now limited to fused FC2.
5. Shared finalizer permuted mode uses the actual nonnegative mapping as row index and 64-bit expert-row offsets. It waits before expert output reads and retains native ascending-top-k FP32 FMA with FTZ before BF16 conversion. Metadata preparation can overlap FC2, not its output consumption.

## Separate upstream finalizer is not a drop-in replacement

`mxfp4_finalize.py::plan_finalize_rows` has a planned API with eager warmup, no PDL launch/wait, FP32-only routing weights, additional split-route accumulation options, and non-FTZ FMA. The PR helper supports native FP32/BF16/FP16 scales, uses FTZ to match native fast math, and accepts runtime token count in its cache. Consolidation would require an explicit contract and performance project; it is not a minimal rebase cleanup or evidence that this helper is redundant.

## Suggested existing validation

Use current base/native ABI and the rebased candidate. These are recommendations, not results from this audit.

- `tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy`: W4A4 per-tensor/per-token and W4A16 unfused numerical checks.
- `...::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles`: existing padding/partial-cluster checks (W4A4 existing cases are fused; W4A16 includes unfused).
- `...::TestExpertParallelism::test_functional_with_ep` and `...::TestCuteDslMoEWrapper::test_wrapper_cuda_graph`: EP8 and captured unfused paths.
- `...::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy`: route-tile boundaries in both finalize modes; these cases explicitly disable PDL, so retain independent PDL-on coverage.
- With `MXFP4_DENSE_TWO_STAGE=1`, `tests/moe/test_cute_dsl_mxfp4_situ.py::test_dense_dual_tile_routing_follows_rows_per_expert` and `::test_dense_gemm1_cluster_split_k_matches_plain` cover upstream prepared unfused FC2 plus `skip_unpermute` and routing-changing CUDA graphs. The latter parametrizes PDL both ways.
- With default dense finalize settings, `test_dense_route_preprocess_pdl_matches_torch` covers PDL/prepared dual-tile replay. Do not enable `MXFP4_DENSE_TWO_STAGE=1` for that test: its assertions intentionally require the fused-path memset contract.
- Keep the previous direct native-vs-new finalizer equivalence and repeated routing/PDL stress harnesses if they still match current APIs. GPU execution must establish current-head evidence; no new test files are required by this audit.

## Opportunities and limitations

No extra scheduling change is recommended during this rebase. Unifying upstream pre-wait hints, shifting the W4A16 hint to the static-weight warp, changing FC2 output layout, or consolidating MXFP4 finalizers are unmeasured performance/design opportunities, not correctness repairs. Current tests and benchmarks should record this new base and dependency versions. The previous environment, helper speedups, and static proof do not establish current-head speedups after the large upstream FC1/FC2/quantizer changes.
