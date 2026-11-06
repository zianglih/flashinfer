# Preparatory fence-placement audit

Native source: `7f1a093119f12b1f5b79d50bf6d0c951069224e5` → `8d1945e7483ba219bb2a4da746c0a249813a6635`. The entire diff is **14 inserted lines in two owned files**: two global proxy fences plus four comment lines in `epilogue.py`; six TMEM completion waits plus two comment lines in `tmem_epilogue.py`. No kernel edit, compilation, GPU execution, or performance claim was made for this audit. Changes below are candidates only if controlled before/after measurements show a regression.

## First candidate: remove the duplicate early FC1 load-wait

The current unconditional sequence inside `_run_fc1_bf16_subtile`, for **each** of its two compile-time halves, is:

1. Load gate and up from accumulator TMEM into registers (`epilogue.py:499–509`).
2. Existing `fence_view_async_tmem_load()` (`:512`).
3. Register-only alpha multiplication, optional clamp, SwiGLU, transpose construction and R1 register permutation (`:513–531`).
4. `transpose.r1_store()` (`:532`), whose first instruction is the newly added `fence_view_async_tmem_load()` (`tmem_epilogue.py:207`), followed by the first scratch TMEM store.

There is **no TMEM load, store, pipeline release, thread rendezvous, or done-flag publication between these two waits**. The old wait can therefore be removed while keeping the new centralized R1 wait, without introducing a new parameter or a special transpose variant. This moves completion to the existing overwrite boundary; it does not remove the required overwrite protection or move cross-warp synchronization.

The ISA basis is [PTX 9.3 §9.7.17.6.4.5](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#tcgen05-memory-consistency-model): true register dependencies from `tcgen05.ld` are respected, independently of other synchronization; those dependencies do not by themselves order subsequent memory accesses. The retained R1 `wait::ld` supplies the latter ordering before scratch reuse. [Current PTX 9.4](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tcgen05-memory-consistency-model) retains that distinction.

Branch audit:

- Both `half=0` and `half=1` execute this exact sequence unconditionally once the subtile body is entered.
- The optional gate/up clamp is a compile-time branch containing only register math; it does not bypass R1.
- For N128, prior valid subtiles and the final valid subtile invoke the same body. N64 invokes the final body directly (`epilogue.py:424–456`).
- Invalid/padded **tokens or feature rows** still reach both waits and R1; their `in_bound` guard only suppresses the later BF16 global store (`:554–578`).
- An entirely invalid last subtile does not enter the body, so it executes neither candidate wait. Its separate load-wait before accumulator release (`:461`) stays unchanged.
- The final-half load-wait before `acc_pipeline.consumer_release` (`:544–545`) also stays unchanged.

Expected source-level saving: one duplicate load-wait per 32-token half, or two per executed 64-token subtile per warp. Actual instruction savings require emitted PTX/SASS inspection because the compiler may already coalesce redundant waits. Numerical and performance validation remain required before promotion.

## Waits that must remain, and broader alternatives

The three store→load edges R1→R2, R2→R3 and R3→R4 overlap scratch memory. R2-load→R2-store and R3-load→R3-store also have overwrite anti-dependencies. The `wait::st`/`wait::ld` ordering at those edges cannot be removed just because the warp is synchronized or the stored registers depend on a preceding load. Final waits before accumulator-stage release and decode-store waits before producer commit protect ownership transfer and are outside the duplicate-wait candidate.

If wait cost is material, FC2 has a broader batching opportunity: its two transpose instances use disjoint column regions (`tmem_epilogue.py:529–536`, bases separated by 32 columns). Execute the same round for both regions, then one shared completion wait before their dependent next round. The register inputs are already prepared together. This would require explicit batching of the existing methods, not deleting their ordering edges; inspect register pressure/spills and preserve final release ordering. FC1 batching would additionally change activation/store scheduling and is a separate, larger experiment.

The split W4A16 implementation follows the ownership-boundary pattern: decoded TMEM stores wait before producer commit (`moe_w4a16_kernel.py:450–454`), and final accumulator reads wait before consumer release (`:1972–1975`). Those are not redundant with the transpose waits. The vendored NVFP4 transpose's unwaited sequence is shared ancestry, not an ISA guarantee.

## Global proxy fences

The current FC1 fence and compile-time dispatch-return FC2 fence occur after the existing 128-thread epilogue rendezvous and before done-counter batching/publication (`epilogue.py:158–169`, `:195–212`, `:342–365`). They order generic global stores for subsequent TMA reads and cannot be replaced by TMEM waits. Direct epilogue-return FC2 already emits no new global proxy fence.

A scheduling alternative is to execute each writer's fence after its stores but before the existing rendezvous, keeping publication after that rendezvous. This preserves the producer-side ownership model and might move fence cost earlier; it does not reduce the fence count. More aggressive fencing only at actual batched publication requires a separate proof covering every publisher, delayed flush, phase transition, and exit path. Do not move a fence to one arbitrary lane: release flags rotate among lanes. Avoid moving the fix into the shared transport solely to imitate BF16/MXFP8 consumers, which explicitly acquire and fence on the read side and have different scheduling.

Recommended order: measure the current exact diff; if needed, try only the simple FC1 duplicate-wait removal first and inspect the resulting PTX/SASS; consider batching or proxy-fence scheduling only when profiles identify meaningful remaining cost. No correctness requirement should be traded for a small timing change.
