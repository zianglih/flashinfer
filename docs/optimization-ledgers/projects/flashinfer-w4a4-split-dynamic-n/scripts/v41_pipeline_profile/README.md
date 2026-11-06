# V4.1-Flash pipeline diagnostics from final0c1e

Baseline is clean `0c1e00fc3e4f913c8c241796c70a29673737c542`, all83 recorded source files pinned. Execution uses GPUs0/1 on C2 `fi-v41-gap-c2-1025` (B300, CUDA13.2, CuTe4.7.1). No production edits or original-a65 reruns. The original B200-cache plan was prepared but never run: those caches are incompatible with B300 and remain unmodified.

`run_native_baseline.py` first collects fresh B300 AUTO choices with the unchanged public benchmark and existing observer. `prepare.py` copies those diagnostic outputs' exact caches and routes into a new immutable plan; it never changes device metadata or imports B200 tactic IDs. Initial jobs cover NVFP4 and mixed MXFP4×MXFP8 at T32/128/512, one GPU per format (0/1); each backend is sequential on its format's GPU. MXFP8 and T8192 can be added in a separate plan after the first evidence, without replacing completed results.

`observe_profile.py` calls the unchanged benchmark entrypoint with its existing model, family, backend, unfused-finalize and profiler flags. It verifies saved-cache metadata, checks each target cache hit against the exact archived tactic, and hashes the existing untimed routing tensors before and after backend execution. No route is recomputed for instrumentation. Runtime source and saved-cache bytes must remain unchanged.

Two separate processes per case avoid concurrent Nsight/native-CUPTI collection:

- `time`: the measurement hook switches only the public profiler selector to the native timer. Exactly10warmups/100cold-L2 CUDA-graph CUPTI iterations; only the selected backend executes. These saved-tactic medians are diagnostics, not fresh-AUTO retention evidence.
- `trace`: the unchanged public profiler path performs five cold-L2 graph replays under Nsight Systems, using CUDA graph node tracing, CUDA/NVTX and no CPU sampling/context switches. The existing `moe` ranges delimit each replay. Complete SQLite and `.nsys-rep` files are retained.

`summarize.py` keeps per-replay kernel names, launch resources, lifetime intervals and adjacent PDL overlap. Kernel lifetimes include dependency waits/startup and cannot identify useful MMA occupancy. Phase lifetimes are not additive to the full pipeline. Bounded iKET markers or selected NCU metrics will follow only where the whole-chain trace supports a concrete question.

Cache metadata mismatches, cache misses, tactic changes, route changes, source changes, CUPTI fallback and incomplete traces fail explicitly. No fallback measurements are silently accepted. All output directories must be new.
