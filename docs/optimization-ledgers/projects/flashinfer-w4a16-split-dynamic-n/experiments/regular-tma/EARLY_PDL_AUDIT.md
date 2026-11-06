# Early PDL for routed BF16 preparation

Reviewed 2026-10-25, source and official documentation only. **The proposed trigger move is safe for the current split W4A16 dependency chain and is a reasonable separate performance experiment.** No GPU execution or production-source edit was performed by this audit. Runtime correctness and performance remain to be checked by the existing focused cases and paired benchmark.

## Reviewed delta

`early-pdl-v2-from-v1.patch` moves the preparation kernel's sole `griddepcontrol_launch_dependents()` from its end to immediately after `griddepcontrol_wait()`, before metadata loads and payload copies. It also adds the corresponding explanation. All pointers, loops, stores, launch options, cache keys, GEMM code and host calls are unchanged.

A literal source comparison independently reproduced v2 by exactly that move and comment insertion:

| Preparation source | SHA256 |
|---|---|
| v1 in `flashinfer-regular-tma` | `a514d309fe1647896eb7b9a68d6cb3da693cac7590eac853ca2ea909c818f0bb` |
| `prep256-early-pdl-v2` artifact | `400ef8b2c40548f619d7faa97d6ca01b90be7ff564db9670815c05047fd80f2c` |

The artifact's hash agrees with its manifest. The independently reviewed GEMM is the regular-TMA baseline at `36740c36a32a6c6d1c7d8162823fe823912de741`, not the separate unstaged Gather4 implementation.

## Official semantics

CUDA 13.2's [PTX ISA 9.2, `griddepcontrol`](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol) specifies that the trigger permits designated dependent grids to be scheduled after every prerequisite CTA has triggered or completed. It does not mean that the triggering grid has completed. Repeated triggers within a CTA add no effect. The wait blocks the executing thread until prerequisite grids complete and their memory operations become visible. The specification also describes release-fence publication before a trigger; this experiment does not use that mechanism to publish partially copied payload.

The [CUDA Programming Guide's Programmatic Dependent Launch section](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html#api-description) explicitly places primary-kernel work after its trigger and requires dependent work to synchronize before consuming primary results. Its CUDA Graphs section documents the corresponding programmatic edges produced by stream capture. Concurrent execution is permitted rather than guaranteed.

## Source-traced dependency argument

1. **Sort to preparation.** Preparation still executes its wait first. Consequently the sort grid has completed before any preparation CTA can issue the early trigger. FC1's scheduler can therefore read the sort-produced tile count, limits and expert IDs even though preparation is still copying payload. Moving the trigger before this wait would invalidate that argument.
2. **Preparation to FC1.** Preparation writes only its routed BF16 workspace. The scheduler and weight/scale loader do not consume those writes. FC1's activation loader executes `griddepcontrol_wait()` before its first activation TMA, so it waits for the entire preparation grid, including every payload store after the trigger. MMA consumes B only after that loader's TMA pipeline completes. No payload store is published merely by issuing the trigger.
3. **FC1 to FC2.** FC1 already triggers FC2 from its weight-loading role. Thus FC2 can also prepare metadata and static weights early. Its activation loader waits for full FC1 completion before loading the intermediate. The accumulator and epilogue dependencies prevent FC2 from writing its output before that input is available.
4. **Workspace reuse.** Standalone FC2 writes the same hidden workspace that preparation populated. This remains safe: FC2's wait requires completed FC1, and FC1's activation wait requires completed preparation. The earlier scheduling signal does not shorten either lifetime.
5. **FC2 to finalizer.** Standalone FC2 triggers the finalizer only after its activation-role wait. The finalizer may read routing metadata first, then waits before loading expert output. Routing was already complete before preparation's early trigger, so its existing contract is preserved.

Relevant baseline locations, relative to the repository:

| File | Lines | Role |
|---|---:|---|
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_prepare.py` (v2 artifact) | 75–79 | Wait before early trigger |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` | 1447–1453 | Scheduler reads routing without a separate wait |
| Same GEMM file | 1650–1658 | Activation wait and standalone FC2 trigger |
| Same GEMM file | 1737–1739 | FC1 early trigger from weight role |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py` | 475–510 | FC2 workspace reuse and standalone finalizer |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py` | 131–141 | Metadata prework followed by output dependency wait |

Every preparation CTA reaches the early trigger regardless of active route count; the trigger is outside all row predicates. Each triggering thread has executed its own prerequisite wait. No CTA barrier is needed to publish preparation output because publication still relies on full-grid completion and the consumer wait. The PDL-disabled specialization remains unchanged. The fused-finalize branch retains its existing memset and dependency sequence; it is not a performance target of this experiment.

## Performance hypothesis and bounded validation

The possible benefit is overlapping FC1 descriptor/setup, scheduler and static weight work with the remaining permutation. It does not let activation TMA consume incomplete rows or create per-row readiness. Preparation may occupy all thread slots, so FC1 admission can wait for preparation CTAs to retire; a trigger issued earlier does not establish actual overlap. Concurrent static weight traffic can also compete with the copy. No speedup is implied by this source audit.

Use v1 preparation as the immediate control to isolate trigger placement. Run the existing 24 exact boundary cases with PDL enabled, then the planned native AUTO screen with unchanged workload, timing and retention rules. Preserve the independent v1 and v2 source manifests. The original baseline and Gather4 results remain separate comparison arms, not substitutes for this isolated v1-to-v2 delta.
