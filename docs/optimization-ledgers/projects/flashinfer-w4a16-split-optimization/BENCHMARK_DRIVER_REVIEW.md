# Split benchmark driver review and held profiler commands

Read-only review of `run_split_benchmark.py` against upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. Final reviewed driver SHA256: `3d0cc984d1550ca52b729e7e235173e9bbe3c3a7265122f90ad928d996c9aeda`. No benchmark, profiler or kernel execution was performed by this review.

## Fidelity and bounded findings

- The driver forwards directly to `bench_moe_deepseek._benchmark_single` (1143–1232), selects only `CuteDSL W4A16`, and preserves the upstream tensor factory, seeded routing, wrapper, autotune prewarm and original timer. `profile_backend="cute-dsl-w4a16"` filters the backend even during normal timing; it does not itself enable profiling. Routing through `fused_topk_deepseek` remains inside the timed callable (490–515). Weight preparation/tuning remain outside (452–488,563–585).
- The result correctly labels **single-GPU EP/TP simulation**, not distributed EP8. EP8 selects32 local experts; token count is the process's n, not n/8. H7168/I2048/E256/top-k8, TP1, ten warmups and100 iterations match this driver and upstream defaults. This differs from the earlier real-EP8 Mega publication protocol and must not be compared as equivalent.
- Normal `_measure_or_profile` (290–300) uses cold-L2 CUDA graphs with CUPTI. `testing/utils.py:1309–1314` measures each iteration's earliest-to-latest activity span, then the benchmark returns its median. The result stores medians only; it does not preserve the100 raw samples and should not claim saved-sample verification. The driver's explicit import and warning-as-error prevent the ordinary CUPTI-to-events fallback.
- **Timer bypass resolved:** truthy `FLASHINFER_DIST_AWARE_AUTOTUNE` selects an upstream event-timed path at benchmark256–288 without a fallback warning. The revised driver rejects exactly the same truthy values before execution. Keep `FLASHINFER_DIST_AWARE_AUTOTUNE=0` explicit in the environment.
- **Profiler tactic preservation resolved using existing APIs:** normal calls still pass `do_autotune=True` and no cache, preserving the upstream tuning behavior. Only after the measured row returns, `AutoTuner.save_configs` writes a distinct `<output-stem>.t<n>.autotune.json` snapshot, whose path and hash are attached to that row. Profile mode requires one token count and an existing cache, rejects a failed environment-compatible `load_configs`, and forwards that cache with `do_autotune=False` through upstream `_autotune_context` (105–113). The repeated load on context entry is harmless and does not retune or rewrite the cache. Use the exact row snapshot, not a later row's cumulative snapshot. An accepted cache file alone does not prove a particular lookup hit; check its W4A16 entry/tactic against the profiled configuration. When baseline/candidate normal winners differ, their profiles explain the actual runs but are not a same-tactic causal comparison.
- Source hashes for the two changed implementation files plus benchmark/timer disambiguate dirty candidate source from baseline `git_head`. Those four hashes are not a full source/environment manifest: retain the owner's setup/source records for tuner, helper, driver, exact image and loaded compiler. Record the dirty candidate as baseline commit plus these changed bytes until committed.
- Per-row garbage collection, synchronization and allocator release occur after measurement. The driver does not retain full-model input tensors between rows. Profile mode correctly emits null latency, converts the upstream NaN placeholder before strict JSON serialization, and keeps profiler wall time separate.

## Held one-row profiling recipe

These commands use the reviewed driver's `--profile --cache` flow, which disables tuning automatically. Set `SPLIT_NORMAL_CACHE` to the selected row's `tactic_cache` from its **completed** normal result, verify it against that row's `tactic_cache_sha256`, and set `SPLIT_PROFILE_PREFIX` to a fresh output prefix. Match source bytes, EP/TP, token count and finalize mode to that row; retain the owner's library paths and native cache settings. Choose T128 or T4096; do not launch both merely because both are listed as options. Baseline and candidate each use their own normally selected row snapshot. No cache merging, retuning, or minimum selection is needed.

Use fused finalize for the constexpr-top-k mechanism: do not add `--no-fused-finalize`. The existing profile path captures the graph before profiling, performs three fixed warmup replays, then brackets one cold replay with `cudaProfilerStart/Stop`; the `moe` NVTX range excludes its explicit L2 flush (`bench_moe_deepseek.py:302–333`).

```bash
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
SPLIT_PROJECT=/workspace/flashinfer-w4a16-split-optimization
SPLIT_PYTHON="$SPLIT_PROJECT/.venv/bin/python"
SPLIT_PROFILE_T=128

/usr/local/cuda/bin/nsys profile \
  --trace=cuda,nvtx --sample=none --cpuctxsw=none \
  --capture-range=cudaProfilerApi --capture-range-end=stop \
  --cuda-graph-trace=node \
  --output="$SPLIT_PROFILE_PREFIX-nsys" \
  "$SPLIT_PYTHON" "$SPLIT_PROJECT/run_split_benchmark.py" \
  --repo "$SPLIT_PROJECT/flashinfer" \
  --output "$SPLIT_PROFILE_PREFIX-nsys.json" \
  --tokens "$SPLIT_PROFILE_T" --ep 8 --tp 1 --warmup 10 --iters 100 \
  --profile --profile-iters 1 --cache "$SPLIT_NORMAL_CACHE"

/opt/nvidia/nsight-compute/2026.1.1/ncu \
  --profile-from-start off --replay-mode application \
  --app-replay-mode strict --graph-profiling node \
  --cache-control none --clock-control none \
  --nvtx --nvtx-include 'moe/' \
  --set full \
  --import-source yes --source-folders "$SPLIT_PROJECT/flashinfer" \
  --export "$SPLIT_PROFILE_PREFIX-ncu" \
  "$SPLIT_PYTHON" "$SPLIT_PROJECT/run_split_benchmark.py" \
  --repo "$SPLIT_PROJECT/flashinfer" \
  --output "$SPLIT_PROFILE_PREFIX-ncu.json" \
  --tokens "$SPLIT_PROFILE_T" --ep 8 --tp 1 --warmup 10 --iters 100 \
  --profile --profile-iters 1 --cache "$SPLIT_NORMAL_CACHE"
```

NCU application replay can relaunch the application to collect counters; `--profile-iters1` is one captured replay per application pass, not one physical kernel execution overall. Its last driver JSON is descriptive only, not a latency result. The profile includes the MoE graph's kernel nodes so GEMM2 can be identified from the actual trace/order/configuration; no unverified kernel-name regex is invented. The second W4A16 grouped-GEMM node is the relevant fused-finalize kernel. If reducing capture scope later, use its observed exact symbol/invocation and confirm the same tactic. Preserve the workload's own flush and avoid NCU's additional per-kernel cache flushing.

Compare baseline/candidate GEMM2's runtime argument list, constant top-k8 shift/mask lowering versus the old general quotient/remainder, SASS integer instruction work, register/local-memory footprint and its share of the timeline. Do not infer fewer loads from source expressions alone: the Mega pointer-reuse trial showed ptxas already combined duplicate metadata loads. Neither instrumented NCU nor Nsight Systems latency replaces the normal unprofiled full sweep.

Profiler option semantics were checked against NVIDIA's [Nsight Compute CLI documentation](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html) and [Nsight Systems user guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html). Installed versions recorded by the owner's environment inspection are NCU2026.1.1 and NSYS2026.2.1. No profiler option has been exercised remotely by this review.
