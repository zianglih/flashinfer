# Host and staging compile-time dispatch audit

Source: clean retained commit `586994d8a054470a17c3dab05be8209c75a33128`. Read-only review of the eight assigned owned files, following repository AGENTS.md → CLAUDE.md and the agent code-review guidance. No source changes, compiler imports, GPU execution, or new validation.

## Conclusion

No new actionable compile-time dispatch omission found in this scope. The one clear static-trip-count device loop was already implemented, validated and measured as the rejected static-rounds staging experiment. Retaining its loop is a documented code-size/register tradeoff, not an overlooked constant. Plain Python configuration, validation and cache branches must not be described as GPU runtime branches.

Paths below are relative to `flashinfer/flashinfer/moe_ep/`. Short frontend/autotune/workspace names refer to the owned `cute_dsl/megamoe/nvfp4_w4a16` leaf; short backend/config/staging/weights names refer to `backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl`.

| Location | Constant provenance and execution phase | Finding |
|---|---|---|
| `cute_dsl/megamoe/nvfp4_w4a16/frontend.py:23–97,178–245` | Frozen config holds geometry, world/rank, H/I/top-k, scheduler/return mode and clamp. `_ensure_compiled` constructs the kernel, workspaces and launch geometry only on a compile miss. | These Python branches already run outside the device kernel. Setters release the old compilation before changing specialization. No runtime dispatch conversion needed. |
| `frontend.py:247–305,307–316` | Tensor pointers and CUDA stream are launch state; the kwargs cache rebuilds conversions only when they change. The explicit thunk captures validated arguments once. | Cache checks and optional `sync` are host operations. Moving tensor validation behind a pointer-only hit would weaken the public contract for changed views; no such change proposed. |
| `frontend.py:318–378` | Expected dimensions derive from frozen config, but current tensors remain caller inputs. | Rebuilding small Python shape tuples is host overhead, not GPU control flow. Hoisting them would add state without a demonstrated benefit; the validation checks themselves must remain. |
| `frontend.py:380–414,530–580` | Reducer H/top-k/format are fixed; output n and pointers can change each call. Empty outputs skip a zero-block launch. Nonempty first capture rejects missing reducer compilation. | H/K specialization is already explicit in `TopkReduce`; only n is dynamic. Converting n/capture/cache conditions to compile-time would break changing-batch and empty-rank contracts. Repeated DLPack wrapping is per-forward host work, absent from graph replay, not a GPU branch. |
| `autotune.py:19–40,112–237` | Four candidate dictionaries are host policy. The collective sweep applies/compiles each config, captures a private full-forward graph, and selects MAX of rank medians. | Candidate/exception/barrier loops are host autotuning work. They do not execute in the compiled Mega kernel or replay graph. Keep metric and graph-lifetime behavior unchanged. |
| `workspace.py:24–71` | Region sizes/strides/offsets are Python integers from constructor-created specs. Kernel constructor materializes them at `megamoe_kernel.py:283–297`; `get_workspace_sizes` only returns totals at1548–1550. | Python layout loops already evaluate during setup/JIT construction. They are not GPU loops. |
| `backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py:39–43,95–132,134–214`; `config.py:17–31` | Config parsing and workspace selection are host setup. `_autotune_pending` is consumed on first compute; input validation/staging and output size are per-forward host state. | The first-forward autotune guard is not an emitted GPU branch. Current n, input dtype/strides and capture state cannot safely be frozen for all forwards. |
| `weights.py:17–165` | Prepared/unprepared format and optional global scales are resolved at preprocessing/validation. `modes/mega_layer.py:82–103` validates supplied weights or preprocesses once, retaining transformed buffers. | Host branches select preparation operations, not per-forward dequantization kernels. Actual FP32 alphas are tensor values and must remain runtime operands; specializing them to1 would change supplied-scale behavior. |
| `staging.py:27–50,86–127` | H, top-k, ID dtype and device key the compiled stager. Live n/capacity and view pointers/strides remain dynamic. Empty, strided, misaligned, aliased, gradient and first-seen-capture cases preserve the Torch fallback. | Fast-path eligibility is per-forward host validation. Freezing it globally would discard legal fallback behavior. |
| `staging_kernel.py:53–76` | H/top-k are `Constexpr`; tid and row/live n are device values. | `row < hidden.shape[0]` and lane `< topk` are necessary runtime predicates. The copy `while` at63–68 has a statically bounded trip count and is the previously measured exception below. |

## Previously evaluated exception: staging copy loop

`staging.py:92–94,123` fixes H at stager construction. `Bf16InputStage` stores it at `staging_kernel.py:13–15`, then binds `width: Constexpr[int]` at53. Thus H7168 gives seven full 128-thread rounds of eight BF16 values per lane. H7200 adds four tail vectors; H288 has only36 tail vectors. A minimal static replacement is complete `range_constexpr` rounds plus a compile-time-selected partial round retaining the required lane predicate.

This exact idea was already evaluated. `candidates/w4a16_bf16_staging_static_rounds/README.md` identifies the retained runtime backedge and original proposal. `w4a16_optimization_experiments.md:4412–4462` records the corrected source,11 passing copy/graph/fallback cases and actual native removal of the copy backedge. Registers increased18→30; threads128, shared/local0 stayed unchanged. The completed historical comparison reports +1.742299% latency GM over8–4096,4/10 lower rows, and rejection. This is historical evidence, not a current-head measurement or a fixed-tactic causal proof.

[Historical complete comparison](../../logs/cu132-recovery0909d-bf16-staging-vs-static-rounds-independent-comparison-001/README.md).

No native validation is needed for this no-change audit. If root deliberately reopens the staging alternative, reuse its existing H7168 native capture and H288/H7200 exact copy/graph/fallback cases, inspect backedge removal and register pressure, then require measured benefit rather than assuming unrolling is faster. No such work is requested here.

## Boundary checks

The frontend's dynamic descriptor conversion does not make model H/I/K or weight layouts dynamically selected in the Mega kernel: `_launch_fc12` reconstructs weights/scales and H/I strides from `static_expert_shape` at `megamoe_kernel.py:657–689`. The shared `TopkReduce.__call__` similarly reconstructs static H/K at `kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/topk_reduce.py:279–305`, with compile-time BF16 format selection and runtime n for grid sizing. Shared/vendor code was read only for these call boundaries and is outside this audit's edit scope.
