# Bot comment 4023300665: final FC2 transpose wait

**Finding is not valid for the current call chain. No source change recommended.** Reviewed clean native `4d183b836bb8ceefea2fcd723f078b3a4935e6b6`; exact comment and three source hashes are retained in `comment.json` and `assessment.json`. No GPU, new compilation, source edit, or public reply occurred.

## Register consumption

The [comment](https://github.com/flashinfer-ai/flashinfer/pull/5019#discussion_r4023300665) treats any use of the R4 results as requiring `fence_view_async_tmem_load()`. PTX ISA 9.4 §9.7.18.6.4.5 explicitly preserves same-thread true register dependencies without additional synchronization. This does not order memory accesses; `tcgen05.wait::ld` remains necessary at relevant memory anti-dependencies. [PTX memory-consistency model](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-memory-consistency-model).

The bot-linked [CuTe API](https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/cute_dsl_api/cute_arch.html#cutlass.cute.arch.fence_view_async_tmem_load) describes completing TMEM access before pipeline release/commit. It does not impose a fence before every dependent register use. The previously captured installed CuTe wrapper also maps this helper to `nvvm.tcgen05_wait(kind=load)` (`nvvm_wrappers.py:1299–1347`; hash recorded).

In `tmem_epilogue.py:270–319`, R4 loads populate per-thread `_src_regs`; `r4_perm()` reads those registers into per-thread `output`. In the sole production caller (`:522–582`), both outputs are copied into RMEM `packed_i32`, then RMEM `out`. These are true register data dependencies, with no cross-thread handoff or intervening TMEM overwrite. The later output STGs target global memory, not the TMEM scratch. The proposed wait is even after `r4_perm()` has already consumed the loads.

## Memory ordering and every release path

- `_transpose_pair():293/299/309` retains load-completion waits before R1/R2/R3 overwrite; `:296/302/312` retains store-completion waits before the following reads. R4 is read-only and ends this helper's TMEM use.
- The two scratch halves begin at `base` and `base+32` (`:554–561`), each within its own 32-column band. They do not alias. Per-warp rows are selected before the helper (`epilogue.py:309–312`).
- `epilogue.py:75–78` uses accumulator strides `(1<<16,1,N)`, two non-overlapping stages, and 64-column subtiles. For N128, the next subtile begins at `base+64`, so its raw reads and scratch stores cannot overwrite the previous subtile's final R4 reads. Its R1 load wait also drains earlier loads before its first stores. A simple integer address-set check covered N64/N128 and all four warp bands; this is address arithmetic, not new codegen validation.

| Supported case | Completion before accumulator release |
| --- | --- |
| N64, positive valid tokens | Last valid subtile waits at `epilogue.py:283`, then releases at `:284`. |
| N64, zero valid tokens | Final skipped branch waits at `:337`, then releases at `:338`. |
| N128, 1–64 valid tokens | First subtile does not release. Skipped second subtile waits at `:337`, then releases. |
| N128, 65–128 valid tokens | Second valid subtile waits at `:283`, then releases. |
| N128, zero valid tokens | Final skipped branch still waits and releases. |

Both supported return modes use this same reorder/release logic; their metadata/router selection does not bypass it. Output destination predicates occur after this release decision. The MMA producer acquires the accumulator stage before issuing into it (`megamoe_kernel.py:1303–1320`); its two-stage pipeline has the full epilogue consumer group (`:1035–1044`). Thus stage reuse cannot bypass the existing final load-completion boundary.

This conclusion is specific to this call chain. Moving/removing the existing caller wait, introducing aliasing scratch, releasing early, or transferring consumption to another thread would require a new ordering audit. Passing numerical tests alone is not the reason for rejecting this suggestion.
