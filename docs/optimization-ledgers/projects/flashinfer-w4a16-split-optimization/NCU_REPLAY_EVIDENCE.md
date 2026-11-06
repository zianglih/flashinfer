# Split W4A16 NCU replay evidence

2026-09-13. Read-only source/report/documentation audit; no profiler launch, remote query, or change to the running baseline application replay.

**Recommendation:** for a future candidate capture, reuse the current driver and filters with `--replay-mode kernel --graph-profiling node --set full`. This combination is documented for the current host-graph/driver configuration. Its successful completion remains to be demonstrated; historical success below is eager and must not be presented as current graph success.

## Current documented contract

- NCU 2026.1 CLI defines kernel replay as replaying individual launches within one application execution, and node graph profiling as treating individual graph nodes as ordinary kernels. Both are defaults; specifying them explicitly documents intent. [CLI](https://docs.nvidia.com/nsight-compute/2026.1/NsightComputeCli/index.html)
- Clustered graph nodes require driver 580 or newer. The separate known hang on drivers below 595 concerns **device-side graphs**. Saved `remote-prep/environment001.json` records driver 590.48.01 and NCU 2026.1.1.0. [Known issues](https://docs.nvidia.com/nsight-compute/2026.1/ReleaseNotes/topics/known-issues.html)
- Current `run_split_benchmark.py:93–99` selects CUDA graphs and profiling; `flashinfer/benchmarks/bench_moe_deepseek.py:306–325` creates `torch.cuda.CUDAGraph` in host code and profiles `graph.replay`. This is not a device-launched graph.
- No PDL-specific prohibition was found in the versioned CLI, profiling guide, or known issues. CUDA documents PDL graph support and makes concurrency optional. That supports serialization correctness for a conforming dependency chain; it is **not** an explicit NCU guarantee for this exact kernel. [CUDA PDL](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html)
- Node profiling isolates/serializes kernels, so it cannot establish production PDL overlap or whole-MoE latency. Whole-graph/range profiling is the alternative for mandatory concurrency or graph-level behavior, with different metric availability. [Profiling guide](https://docs.nvidia.com/nsight-compute/2026.1/ProfilingGuide/index.html)

Versioned official pages were fetched successfully with Python urllib after the web reader could not follow NVIDIA's archive redirect. Plain-text evidence is preserved in `reference/ncu2026.1/{cli,profiling,known-issues}.txt`; relevant CLI lines 629–671, known-issues lines 61–63. No installed help or live driver query was run in this audit.

## Actual historical success and limits

Paths below are relative to `../flashinfer-w4a16/`:

- `logs/w4a16_gemm2_fragment32_ncu_ep4096_20260724_182339/run.log:27` explicitly uses `--set=full --replay-mode=kernel`; the accompanying `reports/ep_w4a16_t4096.ncu.log` completes all six kernels through 40 passes and emits a report. Imported `logs/w4a16_gemm2_fragment32_ncu_import_20260724_182439/raw.csv` records GEMM2 ID4, grid `(2,1,74)`, block 512, cluster `(2,1,1)`, and 40 passes. Some unsupported metric warnings remain; successful full-set collection does not mean every requested metric exists.
- That import's `source.csv` includes executed `griddepcontrol_wait()` and `griddepcontrol_launch_dependents()` for GEMM2, not merely a host PDL flag. `logs/w4a16_gemm2_cstage1_scoped_ncu_ep4096_20260724_172441/` independently repeats completed full/kernel collection.
- The historical worker `flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py:894–984` simulates post-communication EP shape on one GPU and executes eager NVTX-wrapped stage calls. There is no concurrent rank communication and no CUDA graph in this profiling path. A bounded search found no historical explicit whole-graph profiling result.

Therefore these reports establish that clustered, PDL-enabled split GEMM2 can complete full kernel replay in the historical eager worker. They do not establish graph-node replay on the current driver, mandatory cross-rank progress, or preserved concurrency. Keep the current application replay untouched and treat the proposed future capture as the missing empirical check.
