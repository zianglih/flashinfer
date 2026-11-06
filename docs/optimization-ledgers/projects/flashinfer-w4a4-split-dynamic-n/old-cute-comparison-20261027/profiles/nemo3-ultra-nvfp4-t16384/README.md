# Nemo3 Ultra T16384 standard NVFP4 pipeline trace

Old `002529e1` versus retained `0b7fe901`, EP8, both unfused, public functional API, input quantization included. The routed experts use latent D=2048, I=5120, 512 experts, top-k 22, and ReLU2. Sigmoid routes are prepared outside timing, as in the primary campaign. Surrounding latent projections are excluded.

The same source-bound native AUTO winners and source snapshots were replayed with `--no-autotune`. Each trace contains 20 CUDA-graph replays with the public L2 flush. These Nsight diagnostics do not replace the primary 100-sample CUPTI CAAC timings.

| Phase | Old start–end (µs) | Current start–end (µs) | Old duration (µs) | Current duration (µs) |
|---|---:|---:|---:|---:|
| input_quant | 0.000–16.752 | 0.000–16.816 | 16.752 | 16.816 |
| routing_init | 14.081–17.520 | 14.080–17.552 | 3.552 | 3.392 |
| routing_indices | 17.344–28.208 | 17.360–28.256 | 10.800 | 10.817 |
| prepare | N/A | 28.016–50.368 | N/A | 22.528 |
| fc1 | 27.953–262.033 | 47.169–306.962 | 234.369 | 259.633 |
| fc2 | 259.889–451.794 | 287.761–520.995 | 191.760 | 233.361 |
| combine | 263.201–504.514 | 517.538–575.938 | 241.217 | 58.480 |

Median graph spans: **504.514 µs old / 575.938 µs current**. Primary CAAC medians: **505.843 / 580.323 µs**, or **-12.83%** current speedup.

The added prepare lasts 22.53 µs and moves FC1 start later by 19.22 µs. Unlike the V3 trace, FC1 duration also grows by 25.26 µs, making FC1 finish 44.93 µs later. FC2 finishes 69.20 µs later, and final output finishes 71.42 µs later. The trace therefore points to preparation plus both GEMM phases for this workload; it does not isolate compute throughput or prove a particular optimization.

| Derived interval, per-replay median | Old (µs) | Current (µs) |
|---|---:|---:|
| FC2 starts before FC1 ends | 2.144 | 20.144 |
| FC2 completion tail after FC1 ends | 189.584 | 214.737 |
| Final completion tail after FC2 ends | 52.816 | 54.848 |

PDL makes raw kernel duration different from isolated work: current FC2 starts substantially earlier relative to FC1 completion, and old combine starts while almost all of FC2 is still running. The old 241.22 µs combine versus current 58.48 µs therefore mostly reflects different waiting intervals. Compare completion tails as well as raw durations; neither trace identifies the exact dependency-wait instruction interval.

| Native winner | Old | Current |
|---|---|---|
| Token tile | 256 | 128 |
| FC1 / FC2 tiler | 256×256 / 256×256 | 256×128 / 256×128 |
| FC1 / FC2 cluster | 2×1 / 2×1 | 2×1 / 2×1 |
| FC1 / FC2 K steps | Original implicit policy | 8 / 4 |
| Shared CLC | Original static schedule | Off |

Full per-replay timestamps, register counts, shared memory, grid/cluster geometry, exact cache keys and tactics are in `kernel-timeline.json`. `receipt.json` records profile commands, source and cache identities, and artifact hashes. Raw `.nsys-rep`, SQLite exports, and logs are retained alongside this report. No source edits, new tuning, or timing replacement were performed.
