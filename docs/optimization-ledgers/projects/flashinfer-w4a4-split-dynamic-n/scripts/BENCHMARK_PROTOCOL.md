# Split CuTe DSL W4A4 dynamic-N benchmark

This standalone effort compares current upstream FlashInfer
`a65d5b09e7e4c4c5c160b0161c48becd100b3970` against the committed W4A4
operand-layout/runtime-N candidate built on that base. Do not use the W4A16 PR
branch as either source arm. Kernel changes, test coverage and PR publication are
managed separately; these scripts do not edit source or reserve GPU resources.

## Workload and timing

- Native `benchmarks/bench_moe_deepseek.py`, only its `CuteDSL W4A4` wrapper arm.
  The helper selects `backends=("cutedsl",)` and `profile_backend="cute-dsl"`
  without enabling profiler mode. Other benchmark arms are not invoked.
- H7168/I2048, 256 global experts, top-k 8, groups 8/top-groups 4, routed scale 2.5,
  seed 42 and native routing-bias scale 0.01. SwiGLU, NVFP4 activations and weights,
  FP32 accumulation and BF16 output. Per-tensor activation scaling, without an
  additional per-token or 4over6 variant.
- Single-GPU simulated EP8/TP1: 32 local experts at offset 0. Routing and local
  split MoE are timed. Initial activation quantization, weight preparation,
  allocations, compilation/autotuning and inter-GPU communication are excluded.
  This preserves the predecessor's native local-compute benchmark scope.
- Deterministic unfused finalize only. No fused-path performance campaign.
- Ten native warmups and 100 native cold-L2 CUDA-graph CUPTI samples per point;
  the native benchmark returns their median. The helper records that median and
  does not replace or wrap the timer. CUPTI 13+ is required; fallback warnings
  become errors. This helper does not claim to retain the individual 100 samples.
- PDL enabled, distribution-aware autotune disabled, saved AUTO-cache loading
  disabled. Each source/repeat is a fresh process with normal AUTO. In-memory
  native caching between rows remains unchanged. Recorded tactic caches are
  evidence, never input to a primary sweep.
- Run before R1 → after R1 → after R2 → before R2 (ABBA), sequentially on the
  same reserved GPU and runtime. Keep the native benchmark and timer identical
  across arms. Record the explicit CUDA 13.2 image tag, hardware, compiler/runtime
  versions, full commits and source hashes. Source trees must have committed
  production/benchmark changes before a primary sweep.

## Grid and retention

- Exact 13 points: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
- Report T1/T2 but exclude only these two from retention. T4 is included.
- Decode: `4,8,16,32,64,128,256,512`; prefill: `4096,8192,16384`.
- Per-repeat ratio is before/after. Paired ratio is
  `sqrt((before_r1*before_r2)/(after_r1*after_r2))`. Aggregate with the geometric
  mean across the specified points. Do not select minima, pool source-arm
  samples, substitute fixed-tactic diagnostics or reduce the required grid.
- Review every point, both repeat directions, selected tactics and prefill
  tradeoffs. No universal percentage threshold is prescribed by the #6277
  precedent. A small aggregate improvement from changed AUTO choices alone is
  insufficient. Two sweeps do not establish statistical significance.
- Performance screening precedes broad existing-test/sanitizer work. Preserve
  completed observations; no repeated measurement merely to change reporting.
  Earlier W4A16 medians and standalone W4A4 finalizer diagnostics are not W4A4
  full-MoE baselines and must not be relabeled or pooled.

## Commands

Inside the allocated CUDA 13.2 container, prepare independent baseline/candidate
checkouts and one Python environment. Set explicit absolute paths and full
commit hashes. The baseline SHA is supplied at invocation and verified against
the checkout; no helper hardcodes historical source hashes.

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=0
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1
python "$project/scripts/run_campaign.py" \
  --baseline-repo "$project/baseline" \
  --candidate-repo "$project/candidate" \
  --baseline-sha a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --candidate-sha "$candidate_sha" \
  --image "$explicit_ngc_image" \
  --output "$project/results/w4a4-primary-$candidate_sha"

python "$project/scripts/summarize_results.py" \
  "$project/results/w4a4-primary-$candidate_sha" \
  --output-prefix "$project/results/w4a4-primary-$candidate_sha-summary"
```

`candidate_sha` and `explicit_ngc_image` must be set to the actual committed
candidate and newly selected pinned image before invocation. A fresh output
directory is required. The campaign saves its exact scripts, source commits,
environment, GPU/process snapshots, separate logs and JSON for all four sweeps,
per-row routing histograms and AUTO-cache files with hashes. A failed sweep
stops the campaign and leaves its partial evidence intact. Native import checks
prevent accidentally benchmarking the installed source from another checkout.

For an explicitly bounded screening run, pass a smaller `--tokens` list to the
same campaign driver and label its summary with `--allow-partial`; incomplete
aggregate groups are printed as missing, never silently reduced. The one-sweep
helper can also run independently with `--repo`, `--expected-head`, `--image`,
`--tokens` and a fresh `--output` path. Do not overwrite a completed sweep when
resuming work.

## Later K3 scope, if requested

The native distributed driver already accepts `--model kimi-k3 --variants w4a4`
with SiTU(4,25). A corresponding EP8 campaign can reuse the same grid, warmups,
samples, ABBA and retention rules. It would include BF16 dispatch, activation
quantization and distributed combine, with CPU-precomputed routing excluded.
It must be a separate labeled result set; these single-GPU scripts neither
launch nor summarize that distributed workload.

## Reuse an already completed baseline R1

Baseline R1 may run while the kernel candidate is being developed. Keep its
same-stem successful stdout log beside its JSON and per-row cache files:

```bash
mkdir -p "$project/results"
unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
unset FLASHINFER_NVFP4_4OVER6_ERR_MODE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH
"$project/.venv/bin/python" "$project/scripts/run_split_benchmark.py" \
  --repo "$project/baseline" \
  --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --image "$explicit_ngc_image" \
  --output "$project/results/baseline-r1.json" \
  > "$project/results/baseline-r1.log" 2>&1
```

Then append `--reuse-baseline-r1 "$project/results/baseline-r1.json"` to the
campaign command. The driver verifies the source, original harness, token
grid, image, software/runtime, host/GPU identity, environment, successful log and
cache hashes, copies the complete raw artifacts, and runs only candidate R1,
candidate R2 and baseline R2. Original timestamps are preserved so the ABBA
chronology remains explicit. A mismatching baseline is rejected, never silently
rerun. Freeze the benchmark helper before collecting baseline R1.

## Existing correctness coverage

Use existing `tests/moe/test_cute_dsl_fused_moe.py` selections after a retained
optimization: `TestAllValidTactics`, `TestOddTileCountBoundsContract`, deterministic
finalize accuracy, W4A4 cluster-padding/partial-tile, SiTU, wrapper CUDA-graph and
functional-EP cases. This effort adds no test file and does not extend the
reference or zero-tolerance coverage.
