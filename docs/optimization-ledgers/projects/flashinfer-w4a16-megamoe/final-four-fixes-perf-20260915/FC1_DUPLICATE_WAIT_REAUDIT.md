# FC1 duplicate load-wait: bounded re-audit

The existing candidate remains justified at the source/ISA level: remove only the early FC1 load-wait at `epilogue.py:513`, while preserving centralized R1 load completion at `tmem_epilogue.py:207` and all release/transpose waits. **No patch, compilation or GPU launch was made.** This is conditional preparation, not a measured optimization or authorization to change the active baseline.

Exact native source is `a48e5706c2a7775b0b698aa8eccb4e124b02118c`. Both inspected files were byte-compared against this Git commit; hashes and representative PTX locations are in `fc1-duplicate-wait-reaudit.json`. Paths below are relative to `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`.

## Dependency argument

For each compile-time half, `epilogue.py:501–510` loads gate/up fragments from this warp's TMEM band. The early wait at513 is followed by alpha multiplication, optional register clamp, register SwiGLU (`:370–393`), register-fragment construction/permutation, then unconditional `transpose.r1_store()` at533. The constructor's copy and R1 permutation (`tmem_epilogue.py:179–202`) operate on RMEM fragments. No pipeline release, thread synchronization, publication or scratch-memory overwrite intervenes.

PTX9.3 §9.7.17.6.4.5 guarantees intra-thread true register dependencies for `tcgen05.ld` even without another synchronization operation. It explicitly separates that guarantee from memory ordering. Consequently the arithmetic can consume the loaded registers without the early wait; it cannot justify deleting the later overwrite protection. The retained `wait::ld` completes the thread's prior TMEM loads and retains its warp participation requirement before R1 stores reuse the scratch band. [Register dependency contract](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#tcgen05-memory-consistency-model), [wait contract](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-wait).

Both halves reach R1 unconditionally once the subtile body is entered. Optional clamp is compile-time register math. The valid-token branch surrounds the entire subtile (`epilogue.py:432/446`); the per-token/feature store predicate appears only later at554–560. No lane skips the retained central wait due to that predicate. N64/N128 share the same body. An invalid final subtile retains its separate wait/release at462–463; the valid final half retains wait/release at545–546. The corrected FC2 row slice and elected scheduler publication do not modify these FC1 edges.

## Existing emitted evidence and limits

The already collected guarded Hash224b representative `rank0/compile013/kernel.ptx` retains early/central wait pairs at3670/3791 and3885/4005, followed by scratch stores at3801/4015. This re-audit checked every intervening instruction: only `mov`, `mul`, `add`, `rcp` and `ex2` families occur. This supports the stated register-only interval for this artifact. It is not the ordinary native performance winner's SASS and does not establish saved cycles.

If a valid fresh ABBA row shows a repeatable regression, this remains the smallest candidate: potentially two source waits per executed64-token subtile per warp. Keep every R1→R2, R2→R3 and R3→R4 completion edge, both load-before-overwrite edges, accumulator release waits, proxy fences and ownership fixes. Require candidate codegen plus strict correctness and matched-tactic performance evidence before accepting a change. No register-budget increase or broader batching is part of this candidate.
