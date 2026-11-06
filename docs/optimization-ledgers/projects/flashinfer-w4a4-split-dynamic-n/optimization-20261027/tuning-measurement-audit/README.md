# Tactic measurement audit and bounded experiment

Source: clean FlashInfer `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. No production source or defaults are changed.

## Findings

- `bench_moe_deepseek.py:791–793,836–838` sets `autotune_use_cuda_graph=False` for NVFP4 W4A4/per-token and uses graph profiling for MX. Both final measurements use cold-L2 CUPTI CUDA graphs (`:376–384`). Native AUTO uses cold-L2 CUDA events, normally 3 warmups and 10 samples; the final 10/100 CUPTI settings do not configure native AUTO.
- `cute_dsl/tuner.py:678–679` forwards the explicit graph flag to `TuningConfig`; `:699–740` includes it in the runner hash and adds a `cuda_graph` cache-key component. It does not change GPU execution in `forward`. An eager winner must not be relabeled as a graph-native winner.
- Native cold-L2 event timing (`autotuner/autotuner.py:3549–3647`) flushes twice L2 per sample, records the event interval, and measures the median. Graph mode captures one runner invocation; eager mode invokes the runner for each sample. Native delay defaults are 100 us for graph and 5,000 us for eager; those defaults remain intact in the experiment. This is the native execution-policy contrast, not a claim that capture is the only low-level mechanism changed.
- The final CUPTI timer flushes, synchronizes, replays a graph, and measures its first-to-last GPU activity span (`testing/utils.py:1240–1343`). Native tuning covers the MoE runner after input quantization and top-k selection; the NV public chain includes those operations. Graph tuning can improve deployment alignment, but cannot by itself remove the separate routing-distribution and profiling-boundary differences.
- Existing public `autotune_v2`/`MeasurementPolicy` can override execution mode while preserving runner keys; the policy partitions managed caches. `execution_mode="cuda_graph"` retains event timing. Diagnostic `_timer="cupti"` is a separate axis and is excluded here. Explicit `execution_mode="eager"` has different documented timer semantics, so it is not a synonym for the current default NV policy.
- Hopper's `sm90_tuner.py:266–272` already enables graph/cold profiling. Rubin contiguous MoE shares the optional public runner flag. Rubin MegaMoE's `TUNING.md` and `shim/tuning_measurement.py` implement explicit measurement-policy overrides while preserving default native event behavior. TRT-LLM public FP4/FP8 MoE already configures graph/cold AUTO in `fused_moe/core.py`.

## Why NV was kept eager

Commit `adf02fdd4` moved the existing graph-profiled MX assembly to the public API while preserving NV defaults. `PUBLIC_API_FINAL_BENCHMARK_PLAN_2026-10-25.md:22–29`, `scripts/public_mxfp_moe_experiment/README.md`, and `scripts/fc2_packed_transpose_20261026/W4A4_GRAPH_PROFILE_AUDIT.md` state this explicitly. The inspected history does not identify a Blackwell NV failure requiring eager AUTO. The older comment about tuning on the default stream concerns when prewarm happens, not a prohibition on internal graph profiling.

The public function/wrapper accepts graph AUTO for both legacy and swap-AB W4A4/per-token, and forwards the flag to both runners. Only W4A16 is explicitly excluded. Existing graph execution tests do not establish successful graph AUTO across every legacy tactic. If the causal result warrants a benchmark simplification, a bounded legacy graph-AUTO smoke must precede that change.

A historical K3 all-CLC T16384 graph search completed 160 profiles and selected the same winner as eager (`scripts/fc2_packed_transpose_20261026/k3-clc-graph-scores-20261027/README.md`). It is historical evidence against a universal cure, not timing evidence for the present source.

## SGLang boundary

Project-local SGLang HEAD `010eb729bea2b7ef2bcd572a72c171f75ad900fb`, both committed source and existing unstaged swap-AB demo, sets wrapper `use_cuda_graph=not cuda_graph_fully_disabled()` but omits `autotune_use_cuda_graph` (`python/sglang/srt/layers/moe/moe_runner/flashinfer_cutedsl.py`). Wrapper resource lifetime therefore follows serving mode while AUTO still defaults eager. Its warmup context nests `autotune(True)` and `autotune_v2(mode="tune", persistent_cache=False)` without `MeasurementPolicy` (`model_executor/runner/flashinfer_autotune.py:290–365`). No SGLang file was edited. A benchmark selection-policy gain will not automatically apply to this production call site.

## Authorized experiment

1. Use the immutable clean `1e69d0a39` remote source and unchanged balanced profiling-input helper, public functional API, native tactic set, input recipe, PDL and unfused chain. GPU3 runs N3U EP8 W4A4 T4096; GPU4 runs N3U EP8 per-token T4096, after live idle checks.
2. Use a task-local, explicitly recorded adapter to set the existing public `autotune_use_cuda_graph` argument to False or True. This diagnostic does not change the argument's default, reinterpret user input, modify production files, or enable W4A16. Freeze and compare all source/adapter/observer hashes.
3. Graph AUTO starts with an empty private selection cache and searches all profile buckets generated by the unchanged native policy. Do not narrow buckets, seed eager winners, force a tactic, or alter sample counts/delays/timer. Record profile flags, successful/failing candidates and balanced route identities. The original strict observer remains unchanged.
4. Reuse only the existing verified eager native winner cache for control selection, with its original source/config provenance. Both frozen arms get fresh C–A–A–C public timing: 10 warmups and 100 cold-L2 CUPTI graph samples, input quantizer included, same routing and tensor generation. Each arm must hit its corresponding key and exact saved tactic; graph keys are distinct from eager keys by design.
5. Retain native C++ artifacts in persistent storage and use a private CuTe workspace and private tuning caches. No CUPTI-native tuning, actual-route hook, kernel change, new tactic, or legacy smoke unless the causal screen first justifies it. Any gain is labeled **tactic-selection policy**, not kernel-source performance.

The current audit supports a plausible ranking mismatch for NV; it does not prove that mismatch caused a measured gap. MX already uses graph AUTO, so eager-vs-graph cannot explain its remaining gaps by itself.

## Closure

Completed diagnostic and bounded legacy compatibility checks; see `RESULTS.md`, `analysis.json`, `fresh-eager-crosscheck.json`, and the SHA-verified `evidence/` archive. Fresh graph-selected versus older retained eager-selected timings were +6.604% W4A4 and +0.597% per-token, but separate fresh eager searches selected the same faster N128/two-CTA geometry. Per-token matched the graph tactic exactly; W4A4 differed only in FC1 K8 versus K4 and its fresh eager frozen control measured 218.481 us. Those searches do not establish an execution-policy advantage. No benchmark, public default, SGLang, tactic, or kernel change is retained from this diagnostic. GPUs 3/4 are released. All evidence and helper scripts are preserved.
