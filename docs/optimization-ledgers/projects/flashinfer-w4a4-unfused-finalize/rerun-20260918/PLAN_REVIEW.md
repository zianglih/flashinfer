# Uniform PR #5319 benchmark rerun contract

Source-reviewed at PR head `f9dd3c10541e087b716772245a9d033499745048` and pre-PR base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`. Pinned official nightly runtime: `0.7.0.dev20260917`, build source `d233e27ddddbcfdc24eec38ab4dffda1f43ff49c`; CUDA 13.2 image selected and recorded by the parent run. This document records a plan, not completed measurements.

## Required matrix

Use **12 independent process sweeps / 180 native benchmark rows**:

| Mode | Base fused | Base unfused | Head fused | Head unfused |
| --- | --- | --- | --- | --- |
| CuTe DSL W4A4 per-tensor | 15 counts | 15 counts | 15 counts | 15 counts |
| CuTe DSL W4A4 per-token | 15 counts | 15 counts | 15 counts | 15 counts |
| CuTe DSL W4A16 | 15 counts | 15 counts | 15 counts | 15 counts |

Counts, in forward order only: `1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384`. No reverse sweep or aggregate-only summary. Use the same physical B300 and serialize timing runs. Keep separate per-arm/mode/finalize autotune cache files; a fresh process prevents in-memory kernel/tuner cross-contamination. Warmup and compilation are excluded from timing by the native benchmark.

All arms: H7168, I2048, 256 global experts, top-k8, EP8 (32 local experts, offset0), TP1, wrapper API, graphs on, PDL on, initial activation quantization included, cold L2, CUPTI, 10 warmups, 100 timed samples, native median. Native `create_inputs` sets seed42 for each count. The flag includes W4A4 initial quantization in the timed callable; W4A16 consumes BF16 directly and has no activation quantization to include. Routing is timed. This is simulated EP, not distributed all-to-all timing.

Set `FLASHINFER_DIST_AWARE_AUTOTUNE=0` explicitly: the benchmark's `_measure_or_profile` otherwise takes a CUDA-event branch when that environment variable is enabled, even if `use_cupti=True`. Leave JIT enabled. Verify CUPTI import/version and scan for fallback warnings; `enable_cupti=True` alone is not proof CUPTI was actually used.

## Native mode selection without patching the benchmark

The exact-head CLI only accepts `--backends cutedsl`, which runs W4A4 and W4A16 together. Its CLI requires `--profile-backend` to accompany `--profile-cuda`, so it cannot select one mode while timing normally. Do not silently add historical `cutedsl-w4a4` or `cutedsl-w4a16` CLI selectors.

The unmodified native Python function already supports selecting one mode: `run_benchmark(..., backends=("cutedsl",), profile_backend="cute-dsl" or "cute-dsl-w4a16", profile_cuda=False)`. `_benchmark_single` uses that selector independently of the timing/profiling choice. A small external launcher should load the exact-head script via `runpy.run_path`, call this function, and record arguments and returned `BenchResult` values. This calls the native benchmark/timing implementation without editing it or changing measurement semantics.

Illustrative copy-paste single-arm command after preparing an overlay and the exact-head benchmark file:

```bash
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
export PYTHONPATH="$TASK_ROOT/overlays/$ARM"
export BENCHMARK_FILE="$TASK_ROOT/bench_moe_deepseek.py"
export MODE=w4a4-per-tensor FINALIZE=unfused
export TACTIC_CACHE="$TASK_ROOT/artifacts/$ARM/$MODE-$FINALIZE-tactics.json"
unset FLASHINFER_DISABLE_JIT
python - <<'PYBENCH'
import os, runpy
bench = runpy.run_path(os.environ["BENCHMARK_FILE"])
mode = os.environ["MODE"]
assert mode in ("w4a4-per-tensor", "w4a4-per-token", "w4a16")
bench["run_benchmark"](
    token_counts=[2**i for i in range(15)],
    warmup=10, iters=100, ep_config=8, tp_config=1,
    do_autotune=True, verbose=True, use_cuda_graph=True, use_cupti=True,
    use_wrapper=True, routing_bias_scale=0.01,
    use_per_token_activation=(mode == "w4a4-per-token"),
    include_activation_quant=True,
    use_fused_finalize=(os.environ["FINALIZE"] == "fused"),
    profile_cuda=False,
    profile_backend="cute-dsl-w4a16" if mode == "w4a16" else "cute-dsl",
    backends=("cutedsl",),
    autotune_cache=os.environ["TACTIC_CACHE"],
)
PYBENCH
```

`run_benchmark` supplies geometry/EP and produces native per-token CSV when `backends` is specified. `CuteDslMoEWrapper`'s source default is `enable_pdl=True`. Record or assert this default at setup; the native benchmark does not expose a separate PDL override.

Use the **same exact-head benchmark file for both runtime arms**. Its PR diff only adds CUTLASS finalize forwarding and explanatory output; the CuTe DSL benchmark implementation is unchanged. CUTLASS is outside this requested CuTe-only matrix. If adding a separate CUTLASS control later, use the same head benchmark and call the setting `fused tactics permitted`, since True does not force a fused tactic.

## Overlay completeness and fair baseline

Both arms start from an identical copy of the pinned installed nightly Python package. Share one canonical nightly `flashinfer/jit` directory to reuse the same native modules and avoid needless C++ rebuilds. Overlay all PR-changed CuTe sources from the selected git revision:

1. `flashinfer/fused_moe/cute_dsl/fused_moe.py`
2. `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`
3. `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py`
4. `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`
5. `flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py` — **head only**, absent at base.

The baseline must take its first four files from the **PR base**, not leave W4A16 as installed-nightly source. A scoped git diff of the CuTe MoE tree and relevant benchmark/quantization/timing/autotune/native MoE dependencies confirms that the nightly-to-base drift in that scope is exactly the two W4A16 host/kernel files (37 additions, 15 deletions). Those changes include unrelated cache-key/cluster-alignment and tail-store work, and must exist on both sides. Overlaying these four/five files therefore isolates the PR CuTe delta fairly on the pinned runtime.

Do not use `fff0070` as the baseline for this full rerun: it already contains the W4A4 optimization. Do not carry the obsolete `expanded_finalize.py` from a previous overlay. Build fresh overlay directories, ignore/remove `__pycache__`, and assert base imports the native finalizer while head imports the new helper. Record file SHA-256, source git blob hashes, actual `flashinfer.__file__`, runtime version/build commit, shared JIT realpath, all installed package versions, GPU UUID, driver, and explicit image tag. These are exact base/head **CuTe-source overlays on the nightly runtime**, not complete source-built installations of either whole repository revision.

The native JIT wheels may lack first-use MoE/routing utilities. If a one-time C++ build occurs, record it and reuse it. Do not claim zero C++ compilation if setup builds missing modules; subsequent CuTe iterations still avoid rebuilding native sources.

## Evidence and body contract

- Parse exactly 15 unique, ordered counts in each of 12 arms. Reject missing rows, duplicates, nonfinite/nonpositive latency, incomplete sweeps, CUPTI fallback, or source mismatch.
- Retain complete native stdout/stderr plus per-arm tactics. If convenient, also save full-precision returned `BenchResult` values as JSON; native CSV prints six decimal places in milliseconds.
- Uniform primary speedup: `base unfused latency / head unfused latency`, greater than1 means this PR is faster. Show each count and all three modes, without latency-unit columns in this ratio table.
- Uniform head finalize comparison: `head fused latency / head unfused latency`, greater than1 means unfused is faster. Do not conflate this with optimization speedup.
- Fused controls: retain base/head fused raw results (and optionally their ratio) to expose unrelated run-to-run/tactic drift. A single sweep gives no statistical uncertainty estimate; do not dismiss a regression as noise without separate evidence.
- Include all180 raw native latency/TFLOPS rows in a compact CSV block/table. Native TFLOPS is a workload estimate under simulated uniform-local routing, not a measured count of actual locally selected routes.
- Replace previous mixed-revision benchmark tables in the PR body with this one campaign. Older correctness evidence can retain its clearly labeled validation revision/date, but must not be relabeled as freshly executed. If keeping performance/profile claims, remeasure them uniformly or identify them separately as historical; do not use old intervals to explain a new 8K result as established causality.
- Keep setup, exact base/head/runtime/image/hardware, launcher command, ratio definitions, raw evidence, known regressions, and one-sweep limitations self-contained in the body. Preserve the repository template and first-description `@humansand` convention.
