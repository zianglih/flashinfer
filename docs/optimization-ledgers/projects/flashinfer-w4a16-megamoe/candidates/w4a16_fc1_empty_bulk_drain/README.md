# Remove the empty FC1 bulk-copy drain — held candidate

Delete only the five-line FC1 bulk commit/wait block, including its adjacent dead fence comment in the maintained W4A16 epilogue. FC1 and FC2 both use ordinary BF16 global stores; these epilogue threads never issue a bulk-group producer. This is a cleanup opportunity, with no performance claim.

- Base repository HEAD: `8d7718c9a6c76e5722e1cf201395b0df538b081e`.
- Base epilogue SHA-256: `6026bd7a265c4be5e273c4c1af2cbe62dd4eda132ef0944b1f4f70489e69bfde`.
- Proposed epilogue SHA-256: `ee769bd01526a728cd582643337c649e53e608f3f8dfeb4dc5ba85196a0f2170`.
- Patch SHA-256: `1f90695c17f20592a97b49b0afea1c2afe98042b69e2b5857cb71ba12c13c29b`.
- The epilogue is byte-identical between retained HEAD8d and the separate, rejected d88c tail-fence trial. This package contains only epilogue.py; it does not include that kernel reorder or modify primary.

## Why the removed group is empty

1. `megamoe_kernel.py:1378–1399` invokes `W4A16Epilogue.run` only in warps0–3, with no FC1 TMA atom or epilogue SMEM. The constructor fixes BF16 output/combine and rejects bulk FC2, in-kernel reduction, or overlapping accumulators (`epilogue.py:80–95`).
2. FC1 `_run_fc1_bf16_subtile` uses `CopyUniversalOp` BF16 STG (`epilogue.py:634–636,705–721`). Its intermediate transpose consists of TMEM operations and register manipulation. FC2 likewise uses the owned `fc2_stg_store_function` (`tmem_epilogue.py:681–722`) for both peer output and local reused-dispatch output. No producer for a cp.async bulk group is reachable in these four warps; their only bulk-group calls are the removed lines238–239.
3. Bulk groups are per issuing thread; commit includes that thread's prior uncommitted operations using bulk-group completion. Ordinary STG, TMEM operations, and other warps' asynchronous work are not members of this group. With no such producer, the commit creates an empty group. See [PTX bulk-group commit/wait semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-commit-group).
4. Real transport bulk copies remain in dispatch warps8–11 (`megamoe_kernel.py:1404–1412`), with their existing full drains in `src/src/token_comm.py:1113–1114,1415–1416,1460–1461`. Weight/activation G2S TMA uses separate warps5/6 and mbarrier completion. The two decode WGs remain unchanged. No vendor source changes.

## Ordering retained

The patch leaves next-work consumption and all phase state intact, then retains the four-warp BAR1 before previous-work completion publication (`epilogue.py:234,241–252`). FC1's done slot and batching (`485–506`), the GPU-release atomic (`src/src/flag_batch.py:110–119`), and activation's acquire-GPU readiness wait (`megamoe_kernel.py:1229` and vendor `moe_utils.py:103–112`) remain in their current order. Ordinary FC1 writes are therefore still ordered through BAR1 and the release/acquire publication path. The removed bulk wait does not establish ordinary-STG completion.

All TMEM load fences, accumulator releases, tail flag flush, epilogue system fence, and common tail/reset barriers stay unchanged. Direct versus reused-dispatch return does not alter the epilogue's ordinary-store selection or its per-thread group emptiness.

## Saved current native evidence

The retained 640-thread N64/N128 direct fixtures are `profiles/cu132-recovery0910a-clc-removal-default-n{64,128}-001/codegen/`. Their PTX lists the only epilogue bulk instructions at N64 lines6462/6464 and N1287542/7544: commit plus read-wait, immediately before BAR1. There is no bulk-store instruction on the epilogue path. The real dispatch bulk-group producer/drain appears later at N64 lines7785/7818/7820 and N1288865/8898/8900. G2S tensor copies earlier in the kernel use mbarrier completion.

| Control sequence | N64 SASS PC | N128 SASS PC |
|---|---:|---:|
| Empty epilogue UTMACMDFLUSH | `b8c0` | `dab0` |
| Empty epilogue DEPBAR | `b8d0` | `dac0` |
| Preserved BAR1/count128 | `b8e0` | `dad0` |
| Separate dispatch flush/wait, preserved | `11ba0/11bb0` | `13da0/13db0` |

This is saved control evidence, not compilation of this candidate. Source proof covers both return modes; the cited current native pair consists of direct-return fixtures only.

## Prior trial status

The bounded search of `PERFORMANCE_LEDGER.md`, `w4a16_optimization_experiments.md`, the two existing empty-drain candidate notes, and matching local log/artifact names found no completed numerical or performance trial and no runtime rejection. The history is:

- `w4a16_optimization_experiments.md:756`: proposed, not applied.
- `candidates/w4a16_register_overlap_audit/EMPTY_BULK_DRAIN_REVIEW.md`: earlier source ownership proof; no new runtime claim.
- `profiles/cu132-recovery0908b-empty-bulk-drain-compileonly-001/analysis/README.md`: private 512-thread N128/N64 native captures removed eight instructions each, with REG128/STACK0/LOCAL0, preserving dispatch drains and release publication. These are historical source28a/private-candidate captures, not evidence for the current 640-thread source.
- `w4a16_optimization_experiments.md:1157` and `candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512_c1_static_fc2_release_empty_bulk_drain/README.md`: e9a725 runtime adapter frozen and unstaged; no installed-source numerical or latency result.
- Later entry1222 explicitly excludes empty-drain from the input-dispatch trial.

Keep this trial separate from the rejected tail-fence reorder; the retained kernel is restored8d. Existing native checks should establish removal of only the empty epilogue flush/wait/control overhead, preservation of BAR1/release order and actual dispatch drains, and stable resources. Existing numerical/AUTO adapters provide runtime evidence; this candidate creates no new test harness, public knob, or validation matrix.

The original four-line patch is preserved as `source-four-line.patch` (SHA-256 `e5b8e97288f5aaec3aa89bf9b9d32f2004ceebf20aa97acb63c5586c9c35eb26`). The final patch additionally deletes only the adjacent dead `# _fence_rel_gpu()` comment.

Preparation verified one exact deleted byte block and equality of the base epilogue to HEAD, then saved snapshots, diff and hashes. No tests, runtime imports, compilation, remote operation, GPU execution, primary edit, or staging was performed.
