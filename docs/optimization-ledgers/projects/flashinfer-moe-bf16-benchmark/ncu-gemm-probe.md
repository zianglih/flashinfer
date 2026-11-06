# Minimal Nsight Compute probe

Read-only CLI/capability checks on the retained devbox found:

- `/usr/local/bin/ncu`, Nsight Compute **2026.1.1.0**, build 37634170.
- All six requested metrics below are available in the tool's `gb100` and
  `gb102` chip descriptions; the query used `--chips` and did not profile GPU
  work. Full CLI help and metric definitions are preserved in
  `artifacts/ncu-investigation/ncu-capabilities.txt` and
  `ncu-selected-metrics.txt`.
- `--graph-profiling node`, `--replay-mode kernel`, `--profile-from-start off`,
  `--launch-count 2`, `--clock-control none`, `--cache-control all`,
  `--kernel-name-base demangled`, and NVTX include filtering are supported by
  the installed version.

Run only after other GPU benchmarks finish. These commands run from
`/workspace/flashinfer-moe-bf16-benchmark/flashinfer`; the output directory is
the existing project artifact directory. Keep the original source and caches.

```bash
env -u FLASHINFER_NVFP4_4OVER6 \
  -u FLASHINFER_NVFP4_4OVER6_E4M3_USE_256 \
  -u FLASHINFER_NVFP4_4OVER6_ERR_MODE \
  -u FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH \
  -u FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH \
  CUDA_VISIBLE_DEVICES=0 FLASHINFER_DISABLE_VERSION_CHECK=1 MAX_JOBS=8 \
  /usr/local/bin/ncu --target-processes all \
  --profile-from-start off --replay-mode kernel --graph-profiling node \
  --nvtx --nvtx-include 'moe/' --kernel-name-base demangled \
  --kernel-name 'regex:.*Sm100W4A16GroupedGemmKernel.*' --launch-count 2 \
  --cache-control all --clock-control none \
  --metrics dram__bytes_read.sum,dram__bytes_write.sum,dram__throughput.avg.pct_of_peak_sustained_elapsed,gpu__time_duration.sum,sm__throughput.avg.pct_of_peak_sustained_elapsed,sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed \
  --csv --page raw --print-units base \
  --export ../artifacts/ncu-investigation/inference-w4a16-t32 \
  --log-file ../artifacts/ncu-investigation/inference-w4a16-t32.ncu.log \
  python3 benchmarks/bench_moe_deepseek.py --num-tokens 32 --ep 8 --tp 1 \
  --warmup 10 --iters 100 --routing-input-mode logits \
  --use-per-token-activation --include-activation-quant \
  --profile-cuda --profile-backend cute-dsl-w4a16 --profile-iters 1

env -u FLASHINFER_NVFP4_4OVER6 \
  -u FLASHINFER_NVFP4_4OVER6_E4M3_USE_256 \
  -u FLASHINFER_NVFP4_4OVER6_ERR_MODE \
  -u FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH \
  -u FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH \
  CUDA_VISIBLE_DEVICES=0 FLASHINFER_DISABLE_VERSION_CHECK=1 MAX_JOBS=8 \
  /usr/local/bin/ncu --target-processes all \
  --profile-from-start off --replay-mode kernel --graph-profiling node \
  --nvtx --nvtx-include 'moe/' --kernel-name-base demangled \
  --kernel-name 'regex:^bmm_Bfloat16_Bfloat16Bfloat16_' --launch-count 2 \
  --cache-control all --clock-control none \
  --metrics dram__bytes_read.sum,dram__bytes_write.sum,dram__throughput.avg.pct_of_peak_sustained_elapsed,gpu__time_duration.sum,sm__throughput.avg.pct_of_peak_sustained_elapsed,sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed \
  --csv --page raw --print-units base \
  --export ../artifacts/ncu-investigation/inference-trtllm-bf16-t32 \
  --log-file ../artifacts/ncu-investigation/inference-trtllm-bf16-t32.ncu.log \
  python3 benchmarks/bench_moe_deepseek.py --num-tokens 32 --ep 8 --tp 1 \
  --warmup 10 --iters 100 --routing-input-mode logits \
  --use-per-token-activation --include-activation-quant \
  --profile-cuda --profile-backend trtllm-bf16 --profile-iters 1
```

The kernel filters are derived from the verified Nsight Systems names. In
execution order, matching launch 1 is FC1 with SwiGLU and matching launch 2
is FC2. For CuTe the names are identical, but their grid and position differ;
use report execution order and compare grid dimensions with the Nsight trace.
`--launch-count 2` counts matching kernel launches only. No `--set full` is
requested; selecting `--metrics` without `--set` limits the collection.

Interpretation:

- Compare DRAM bytes, achieved DRAM throughput and tensor-pipe/SM activity.
  High BF16 DRAM throughput with substantially larger read bytes and modest
  tensor-pipe activity would support a bandwidth explanation.
- Nsight Compute kernel replay isolates nodes and controls their caches;
  the PDL overlap and preceding-stage cache state differ from normal replay.
  Treat these metrics as kernel diagnostics, not replacement MoE latencies.
- `--clock-control none` avoids intentionally changing the clocks. Cache
  control `all` makes each isolated profile replay cold, independently of
  the script's excluded L2 flush. It does not clear compilation caches.
- Check both report kernel names/configurations against the Nsight Systems
  trace; autotuning under another profiler can choose a different tactic.
- If whole-graph traffic is needed, a separate `--graph-profiling graph`
  capture can preserve cache interactions between nodes. That reports metrics
  for the graph, not two FC kernels; the node command above answers the
  requested minimal two-GEMM question first.

The documented distinction between node and whole-graph profiling is in
[NVIDIA's Nsight Compute profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#graph-profiling).
The command options and metric query procedure are documented in the
[CLI guide](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html).
