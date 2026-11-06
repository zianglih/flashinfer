# Split CuTe DSL W4A16 layout compatibility benchmark

This mode measures the W4A16 consumer affected by the shared gated-weight
preparation change. It is separate from W4A4, per-token W4A4, W4A8, and the
homogeneous FC1/FC2 microbenchmarks. No prior W4A16 PR data is relabeled here.

- Native `benchmarks/bench_moe_deepseek.py`, with `backends=("cutedsl",)` and
  `profile_backend="cute-dsl-w4a16"`; profiler mode remains disabled. Only the
  `CuteDSL W4A16` row is accepted.
- H7168/I2048, E256, top-k8, groups8/top-groups4, routed scale2.5, seed42 and
  routing bias0.01. Single-GPU simulated EP8/TP1: 32 local experts, offset0.
- BF16 activations, NVFP4 weights, SwiGLU, BF16 output. Routing and split MoE
  are timed; weight preparation and inter-GPU communication are excluded.
  Deterministic unfused finalize only.
- Native CUDA-graph CUPTI timing: 10 warmups, 100 cold-L2 samples, median.
  The native timer is unchanged; individual samples are not returned by it.
  CUPTI13+ required; CUDA-event fallback warnings become failures.
- PDL on, distribution-aware tuning off, AUTO-cache file loading off, all
  `FLASHINFER_NVFP4_4OVER6*` overrides unset. Fresh process and normal AUTO for
  every sweep; native in-process caching across points is preserved.
- Exact token grid: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
  T1/T2 are reported and excluded from retention; T4 is included.
  Decode is T4..T512; prefill is T4096/T8192/T16384.
- Sequential ABBA: baseline R1, candidate R1, candidate R2, baseline R2 on
  the same GPU/runtime. Retain raw logs, JSON, per-point AUTO caches and
  source/environment hashes. Preserve completed data when resuming.
- Speedup is before/after per repeat. Paired speedup is sqrt(R1*R2), and
  aggregates are geometric means over the exact groups. Inspect pointwise
  regressions and tactic choices; no pooling, minima, or reduced grids.

Baseline is current upstream `a65d5b09e7e4c4c5c160b0161c48becd100b3970`.
The standalone helper requires committed production/benchmark sources and a
new output path. Baseline R1 can run before the candidate is finalized:

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=3  # use only the GPU assigned to this campaign
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1
"$project/.venv/bin/python" "$project/scripts/w4a16/run_split_benchmark.py" \
  --repo "$project/baseline" \
  --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --output "$project/results/w4a16-baseline-r1.json" \
  > "$project/results/w4a16-baseline-r1.log" 2>&1
```

`run_campaign.py` supports `--reuse-baseline-r1` and verifies source, runtime,
GPU, harness, raw-log completion, and cache hashes before copying evidence.
Its frozen summary intentionally rejects changes to the native benchmark.
Use the separate post-layout provenance verifier once the candidate weight
preparation contract is finalized; do not relax or rewrite saved baseline
data to accommodate that change.
