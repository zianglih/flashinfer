# FlashInfer CUB Top-K short-input audit

Read-only source audit, 2026-09-13. No GPU execution or new performance measurements.

## Revisions

- FlashInfer #4442: merged, merge commit `286eee4e2999a825716eab68e597cb1ee0881e1b`.
- FlashInfer #5185: open; audited head `62ff0a1751a537af89e5e2353ea1ca72954ba165`, base `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`.
- CCCL pinned by that FlashInfer head: `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116`.
- Separate CCCL checkout also inspected latest `b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4`; use the pinned revision for links below. The working checkout may be at latest; use `git show <pin>:<path>` for pinned reads.
- PR metadata and the #5185 diff are retained in `pr4442.json`, `pr5185.json`, and `pr5185.diff`.

## Finding

The `k > physical width` failure is a FlashInfer wrapper/padding integration gap. The pinned CUB implementation already accepts K larger than the segment, clamps to the segment size, and selects every element. No CCCL change is required for this specific issue.

Evidence:

- [Pinned CUB API contract](https://github.com/NVIDIA/cccl/blob/16bd510c9b712e82b0ab6cbb630d8e29ba1f7116/cub/cub/device/device_batched_topk.cuh#L305-L318): K has no algorithm-imposed maximum; declared argument bounds must still be truthful.
- [Cluster clamp and select-all fast path](https://github.com/NVIDIA/cccl/blob/16bd510c9b712e82b0ab6cbb630d8e29ba1f7116/cub/cub/agent/agent_batched_topk_cluster.cuh#L3339-L3360).
- [Baseline clamp](https://github.com/NVIDIA/cccl/blob/16bd510c9b712e82b0ab6cbb630d8e29ba1f7116/cub/cub/agent/agent_batched_topk.cuh#L220-L229).
- [Existing upstream oversized-K test](https://github.com/NVIDIA/cccl/blob/16bd510c9b712e82b0ab6cbb630d8e29ba1f7116/cub/test/catch2_test_device_segmented_topk_pairs.cu#L382-L440): segment size 384, requested K 385/484/768/3840, exactly 384 outputs. This audit inspected the test; it did not execute it.
- [FlashInfer rejection](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/csrc/cub_topk.cu#L441-L458): `CheckCUBTopKInput` requires `0 < top_k <= d`; workspace queries call this before CUB. The page-table execution entry duplicates the upper-bound check at lines 497-498.

## Scope of #5185

The [Python gate](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/flashinfer/topk.py#L649-L674) changes only automatic routing (`algo is None`) for K > `input.size(1)`. All existing dtype, architecture, mode, and performance gates still apply.

| Shape | Effect of #5185 |
| --- | --- |
| Physical width 64, K 2048 | Auto avoids the existing CUB wrapper error; validated filtered-native cases copy valid entries and pad. |
| Physical width 4096, K 2048, logical length 64 | New guard does not exclude CUB. |
| K equals physical width | New guard does not exclude CUB. |
| Explicit `FLASHINFER_TOPK_ALGO=cub` | Existing physical-width rejection remains. |
| Explicit `FLASHINFER_TOPK_ALGO=default` | All CUB calls are excluded, regardless of width. This is a broader workaround than #5185. |

The guard does not remove a working CUB case: these physical-short cases already errored in the wrapper. The #5185 PR reports 21 new regressions and 122 selected existing controls; those are prior PR validation, not runs performed by this audit. Its cited SGLang performance used explicit `default` and does not measure the new guard's performance.

## FlashInfer follow-up design

Two feasible approaches, based on source analysis:

1. Complete the CUB adapter. Preserve requested K for output allocations, row strides, and suffix filling. Pass `K_select = min(K, d)` to CUB (for positive d), consistently in workspace queries and execution. For valid logical lengths L <= d, `min(K_select, L) == min(K, L)`. Keeping K_select within d also satisfies the existing K argument's compile-time bound, which is currently tied to the physical-width tier (8192 or 2^21). Handle d=0 separately if supporting empty physical tensors.
2. Alternatively, add or extract a select-all copy/transform/pad path for d < K. Every valid element is selected; SMALL/LARGE cannot change the selected set. This can avoid the native filtered selector's K<=2048 limitation for these trivial shapes and potentially fuse all output writes in one launch. Performance is a hypothesis requiring measurement.

The current [transform tail kernel](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/csrc/cub_topk.cu#L157-L194) already fills -1 after valid logical outputs. Page-table and ragged writers use original K as their row stride. The [plain CUB entry](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/csrc/cub_topk.cu#L741-L782) has no tail fill and needs index -1/value 0 padding. Removing assertions alone is insufficient.

Both approaches must preserve valid-only page translation, raw-index output, ragged offsets, row windows, caller-provided output addresses, and CUDA graph replay with changing metadata. Tie-break is boundary membership; it does not require sorted or repeatable output order. Do not widen that ordering contract incidentally.

The native implementation already has a [select-all copy/pad branch](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/include/flashinfer/topk.cuh#L2595-L2627). Its [dispatch limit](https://github.com/flashinfer-ai/flashinfer/blob/62ff0a1751a537af89e5e2353ea1ca72954ba165/include/flashinfer/topk.cuh#L3648-L3650) is checked before reaching that branch, so the #5185 fallback alone does not extend strict-tie/graph-safe support above K=2048.

## Performance interpretation

Long physical rows with K<=d retain the existing CUB route. For physical-short rows there is no nontrivial boundary selection; the work is copying/translating valid outputs and padding. The correct optimization target there is low launch and write overhead, not maximizing the fraction of calls labeled CUB. Benchmark adapter completion versus copy/pad and current fallback, including full graph replay and suffix-fill cost; existing long-row tie-break speedups do not establish the winner here.

Broader engine limits, such as the pinned CUB single-segment ceiling 2^21 and SM90+ tie-break backend requirement, are separate from this issue. Extending those natively is upstream CCCL work; they do not explain width 64 / K 2048 rejection.
