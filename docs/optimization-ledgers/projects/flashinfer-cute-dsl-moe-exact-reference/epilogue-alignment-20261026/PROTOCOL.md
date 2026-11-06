# Fused per-tensor NVFP4 arithmetic alignment

Compare the rebased exact-test PR before the production arithmetic change with the candidate containing only that follow-up change. Keep both sources frozen throughout measurement. Existing PR7290 tables are historical context, not a current-device before arm.

## Workloads and timing

| Model | H | I | Experts | Top-k | Simulated EP | TP | Activation |
|---|---:|---:|---:|---:|---:|---:|---|
| `v3` | 7168 | 2048 | 256 | 8 | 8 | 1 | SwiGLU |
| `v41-flash` | 5120 | 2304 | 384 | 6 | 4 | 1 | SwiGLU, limit 10 |
| `kimi-k3` | 3584 | 3072 | 896 | 16 | 8 | 1 | SiTU, gate 4 / linear 25 |

Use the full token grid `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. This is standard per-tensor NVFP4 W4A4, no 4over6, with initial activation quantization timed and standalone deterministic finalize. Weight preparation, compilation, and native AUTO prewarm are outside measurement. PDL remains enabled. Every row uses 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. V4.1 and K3 routes are precomputed as in the public benchmark; communication is excluded.

The project-local driver imports the unchanged `benchmarks/bench_moe_deepseek.py` and calls `run_benchmark`. `backends=("cutedsl",)` plus `profile_backend="cute-dsl"` filters to W4A4, while `profile_cuda=False` preserves ordinary timing. The CLI's `cutedsl` selector also includes W4A16, and CLI profiling cannot be used for ordinary timings. The driver verifies that only W4A4 returned results.

Use a fresh process for every model/arm. AUTO starts without saved tactics: no `--cache`, no `load_configs`/`save_configs`, and `autotune_cache=None`. The driver clears 4over6 and tuner override environment variables, disables file loading/distribution-aware AUTO, and enables PDL and standard FP4 fast math. Keep source-specific build caches; compiled code caches are distinct from saved tactic caches. Set `FLASHINFER_WORKSPACE_BASE` and `CUTE_DSL_CACHE_DIR` to each source's pinned cache locations before launch. Record the explicit Docker image, dependency versions, source commit/patch, and GPU UUID in campaign receipts.

## Before/after sequence

For each model on the **same physical GPU UUID**, run **A1 before → B1 after → B2 after → A2 before**, with at least two full repetitions of each source. Separate GPUs may run different model campaigns concurrently, but never compare an A/B pair across GPUs or overlap processes on one GPU. Each invocation gets a fresh output directory. Example for one arm:

```bash
CUDA_VISIBLE_DEVICES=GPU_UUID FLASHINFER_CUDA_ARCH_LIST=10.3a \
  python scripts/run_epilogue_benchmark.py \
  --source /absolute/frozen/source --model v3 \
  --output epilogue-alignment-20261026/results/v3-A1
```

`results.json` retains every full-precision native `BenchResult`, all 100 returned CUPTI sample durations, model/environment/GPU metadata, native routing histogram, source hashes and before/after source identity. `source.patch` captures the measured tracked changes. Observation and JSON writes happen after the timing function returns. No tuner or kernel implementation is replaced. Existing outputs are never overwritten; incomplete runs retain an explicit failure receipt. CUPTI import/version failure or CUDA-event fallback is an error.

## Retention and reporting

Report all 39 model/token cells, including T1/2. Exclude only T1/2 from retention aggregates: eight decode points (4–512), three prefill points (4096/8192/16384), and 11 overall points per model. Each cell's paired speedup is `sqrt(A1 * A2 / (B1 * B2))`, with values greater than one favoring the aligned implementation. Use geometric means for model/decode/prefill summaries; retain both individual before/after comparisons and A2/A1, B2/B1 drift.

Updated retention decision: the user explicitly accepted minor performance differences for the shared quantization contract. Retain the arithmetic alignment and report the full measured shifts, including per-model and per-token behavior. Investigate unstable cells before presenting them as stable effects; do not invent a universal percentage threshold or infer statistical significance from two arm medians. Correctness and performance remain separate evidence. Final numerical results belong to the completed receipts and PR body.

## Exact-test integration

The rebased test commit preserves the prior 110 bounded blockscaled cases and adds independent bit-exact checks to all 12 unfused public MX cases (two formats, three activation configurations, two tactics). It preserves functional/wrapper parity, SiTU differentiation, and invalid-input assertions. Supported Rubin unfused tests retain their prior mathematical oracle; the new exact oracle remains SM100/SM103-specific. Existing fused MX tests remain approximate by design.
