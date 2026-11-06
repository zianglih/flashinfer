# Proposed current-W4 output-acquire diagnostic

The old traces cannot resolve the target wait: `w4a16-iket/ranges.json` and all eight decoded trace summaries contain `epi_acc_wait`/`epi_body`, but no nested output-acquire scope. Their roughly3µs epilogue bodies combine TMEM loads, SiTU/SwiGLU math, shared output, barriers and stores. The later `iket-fc1-epilogue-detail` is swap-AB, not W4, and cannot substitute. Exact prior-marker evidence is in `prior-trace-audit.json`.

## Frozen scope

- Retained b52e4e09649dc180fc7583a25ec35ff55f04654d; W4 kernel de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58.
- Only task-local instrumented module. Add `epi_cstore_acquire` push/pop directly around the two existing `c_pipeline.producer_acquire()` calls. No wait, barrier, store, operation order or ring state moves. Preserve existing scopes; no source repository mutation.
- Strip all marker statements and empty marker conditionals, compare full-module AST against retained source; hash both modules and all514 source paths. Sampling guards must also disappear in this proof.
- K3 EP8 T4096 and V41F TP4 T4096; both frozen native FC1 and FC2 tactics are `((256,128,256),(2,1),True)`, shared CLC. Saved route hashes are8c5c7466… andb7d82625… respectively. Use their exact winner caches and expected rows from retained6be-full (W4 closure unchanged throughb52). No autotuning or timer invocation.
- FC1 only instrumentation, selected by its existing `gather_input` behavior. Both source sites are marked for completeness; these two gated workloads execute the gated site, not the nongated branch. FC2 stays native/uninstrumented; the closed FC2 late-wait experiment is not repeated.

## Qualification before any workload launch

Use the public profiler path and the existing modern NativeDump guard from `iket-fc1-epilogue-detail/probe_iket.py`, transplanted into the W4 harness. Keep native maxrregcount96. Instrumented compilation alone uses `iket --keep-ptx --keep-cubin`, `no_cache=True`, and an explicit existing dump directory; normal native caches remain persistent. Inspect the actual NativeDump CUBIN before returning its callable in both tracker and recorder processes: REG/LOCAL/STACK, LDL/STL, required CTA size, and unchanged register-allocation policy must pass. No unguarded tracker workload is allowed. Archive actual binaries and source/cache/route receipts. If instrumentation causes spills or exceeds the native physical-register budget, stop and report.

## Capture and interpretation

After parent approval, GPUs6/7, stock clocks unchanged. Capture two complete CTA clusters per workload separately with the flattened-cluster source predicate and `--enabled-cluster`, preventing trace allocation over the full padded CLC grid. Retain one public profiler graph iteration and its existing warmups; no full benchmark or baseline rerun. Explicit selection of the final graph launch must distinguish warmups.

Report issuer-warp acquire mean/median/p95/max and per-tile summed acquire span, beside that same warp's enclosing epilogue body. These diagnostic spans include marker/instruction overhead and do not directly measure the following all-writer join, nor do they establish removable end-to-end time. Compare relative placement to next TMEM/accumulator progress, preserving raw traces and variability. If acquire is near the32ns timestamp floor or an insignificant fraction, close the lead without a kernel candidate.

The same captures retain the existing `transform_wait_tmem_slot_free` marker, so they can assess the separate proposal to load raw packedA/scales before the decoded-slot acquire without adding another marker. Saved374 K3 EP4K/8K traces show this wait averaging25.2–25.5ns, median/p95=32ns (maximum64–96ns), versus309–314ns for load/decode. That provides no positive evidence for decoded-slot staging yet; do not implement it based on the presence of a wait in source.
