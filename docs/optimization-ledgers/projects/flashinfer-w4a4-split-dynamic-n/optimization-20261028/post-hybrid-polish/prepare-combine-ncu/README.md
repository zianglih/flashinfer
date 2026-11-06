# Retained prepare/combine NCU diagnosis

Retained source61c2c367, B300/CUDA13.2, `nvcr.io/nvidia/pytorch:26.05-py3`, Nsight Compute2026.1.1. TP8/EP1, V3 and K3, MXFP4x8,16384 tokens, PDL on, unfused swapAB. Remote source has Git61249 plus the retained patch; its348-file manifest is byte-identical to61c2 and verified before/after collection. Reuse the prior public profile harness, frozen managed winners/routes, and persistent native compilation caches. No backend edits, new timing benchmark, sanitizer or autotuning.

GPU7 was explicitly released by the producer experiment and independently checked idle before launch. Other GPUs remain assigned to retention benchmarks. Reports are diagnostic; application replay/counter instrumentation can serialize kernels and perturb PDL/cache behavior. Instrumented durations are never used for retention. The existing NSYS trace remains the source of normal overlapping-stage duration.

Collection is limited to `PrepareRouted` and `_MoeFinalizeKernel`, one captured graph replay per application pass, application replay/grid matching, no clock/cache control. Fifteen requested metrics cover DRAM read/write/throughput, L2 read/write sectors/hit rate/throughput, LSU global load/store sectors, instructions, long-scoreboard stalls, issue-active, registers and shared memory. This is not a full section sweep. Raw `.ncu-rep`, CSV, logs, receipt and source/winner/route hashes are preserved.

`run_remote.py` implements sequential source-bound cases. `profile_entry.py` is byte-identical to the retained NSYS harness. `fetch.py` archives and SHA-verifies evidence; `analyze.py` parses saved wide CSV without GPU reruns. See `RESULTS.md`, `summary.json` and `pc-attribution.json` for the completed captures and one bounded unsigned-index candidate.
