# W4A16 versus TRTLLM BF16 timing and API audit

Source review began at `a3fce87d5beec29775e9bc3917df99ba6bc4db9c` on 2026-09-05 UTC.
This document is a source audit, not a claim that Nsight experiments have passed.
The project-local `timed_control.py` adds an independent CUDA-event control;
its JSON records the exact source bytes and Git state when executed.

## Measurement scope

- `benchmarks/bench_moe_deepseek.py:_measure_or_profile` calls the shared
  `bench_gpu_time` with `enable_cupti=True`, `use_cuda_graph=True`,
  `cold_l2_cache=True`, and exactly the backend's `run` callable.
- `flashinfer/testing/utils.py:1659` gives CUPTI precedence over event graph
  timing. `bench_gpu_time_with_cupti` captures **one** `call_fn()` in a graph
  at lines 1169–1187; the graph is captured before activity collection.
- The CUPTI measured loop (lines 1229–1240) zeros a 2x-L2 buffer, synchronizes,
  records CPU timestamps around only `runner()`, and synchronizes afterward.
  Activity processing (lines 1274–1314) correlates device operations with host
  launches inside that CPU interval. The flush is launched before the start
  timestamp and excluded.
- Reported latency is **last device activity end minus first device activity
  start** for that replay. It includes GPU gaps and memcpy/memset nodes from
  the target graph, not merely the sum of kernel durations. Host graph-launch
  submission time before the first device activity is excluded. Nsight kernel
  sums are useful decomposition but are not the same metric.
- The main CLI explicitly sets `FLASHINFER_DIST_AWARE_AUTOTUNE=0` for logits
  routing. The specialized DA event/graph-lease branch cannot affect the
  published logits benchmark.
- No CUPTI-unavailable fallback warning was found in the checked original
  inference log, and the recorded environment includes installed CUPTI 13.

## API and preparation scope

- `bench_cute_dsl` constructs/prepares weights, quantization scales, outputs,
  wrapper resources and FP32 routing bias before measurement. The prewarm runs
  under `_autotune_context`, synchronizes, and exits tuning before calling
  `_measure_or_profile` (benchmark lines 552–576).
- W4A16's `prepare_activation` returns the original BF16 input and `None`
  scales immediately. Neither the initial activation-quantization flag nor
  per-token activation flag adds quantization to this path.
- `bench_trtllm` calls the public `TrtllmBf16Config.prepare_weights` before
  defining/capturing `run`, preserving the original BF16 weight values in
  shuffled BlockMajorK layout. It passes BF16 hidden states directly. The
  NVFP4-only quantization branch does not execute for BF16.
- `moe_kwargs` sets `do_finalize=True`; `routing_method_type=DeepSeekV3`,
  group counts, top-k, local expert offset/count, and routed scale are shared
  with the intended DeepSeek contract. The public BF16 API default enables
  PDL and requires BlockMajorK; benchmark preparation matches those defaults.
- Both the CuTe wrapper and TRTLLM Python/C++ launchers allocate or resolve
  output/workspace objects while capturing. Replay executes the resulting
  device graph and does not reconstruct Python dictionaries, wrappers, C++
  launchers, or CPU allocation/tactic-selection logic on each iteration.
- CuTe wrapper (`flashinfer/fused_moe/cute_dsl/fused_moe.py:956–1018`) chooses
  the W4A16 runner; this calls the same W4A16 implementation as the functional
  API. The published runs use the wrapper, as recorded in their logs.

## Expected captured work

W4A16:

1. `fused_topk_deepseek` from logits and routing bias.
2. Route sorting/metadata (`moe_sort`) and BF16 activation permutation.
3. W4A16 grouped FC1 with fused SwiGLU.
4. Inference: output zero and grouped FC2 with fused weighted atomic finalize.
   RL: grouped FC2 to intermediate storage followed by deterministic weighted
   unpermutation/finalize.

Source: benchmark `run`; `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:403–509`.

TRTLLM BF16:

1. Native DeepSeek routing and route/permutation metadata.
2. BF16 permute-fused FC1 with fused SwiGLU.
3. BF16 FC2.
4. Native weighted finalize.

Source: `csrc/trtllm_fused_moe_kernel_launcher.cu:1493–1543` and
`csrc/trtllm_fused_moe_runner.cu:530–637`. The separate activation kernel and
FC2 per-token quantization branches at runner lines 575–619 apply to FP8 or
NVFP4, respectively, not BF16. CuTe `--no-fused-finalize` does not control the
native TRTLLM finalize implementation.

The scopes cover complete local MoE but their fusion patterns and route-weight
storage precision differ; CuTe uses FP32 selected route weights, native TRTLLM
uses BF16. This comparison does not prove numerical equivalence of quantized
and unquantized MoE.

## Why equal tensor-core precision need not imply equal latency

For H=7168 and I=2048, one expert's up/gate/down weights contain
`3*H*I = 44,040,192` values. BF16 storage is 88,080,384 bytes (84 MiB).
Packed NVFP4 data plus one FP8 scale per 16 values uses 24,772,608 bytes
(23.625 MiB), ignoring tiny global scales: **3.556x smaller storage**.
For 32 local experts, these are 2,818,572,288 and 792,723,456 bytes.

Sparse token-to-expert assignment can require large weight reads for little
useful arithmetic. Weight compression can therefore save more memory traffic
than online decoding costs even when both paths issue BF16 tensor-core MMA.
This is a mechanism hypothesis, not proof of achieved bandwidth: active-expert
counts, tile reuse/padding, actual memory traffic and GPU-counter evidence
determine the realized effect. Nsight GEMM dominance and small gap/finalize
fractions can exclude simpler scope/host-overhead explanations.

## Controlled experiments

1. Trace the existing single-call profile graph at n=32 and n=4096 for W4A16
   and TRTLLM BF16. Attribute only target replay nodes; the profiler capture
   range also contains explicit L2 flushes and host synchronizations.
2. Compare per-replay first-to-last GPU spans with the published CUPTI numbers;
   separately report individual FC1/FC2/routing/finalize durations, overlap,
   inter-kernel gaps and graph-launch CPU duration. Do not divide total trace
   wall time by iteration count, because it includes flush/synchronization.
3. Run `timed_control.py` for the same configs. This uses one-call graphs with
   explicit cold flush before every event-timed replay, matching the CUPTI
   cache policy. Optional warm-cache results use the exact same graph.
4. Capture selected tactics before/after leaving autotune and during graph
   capture. The timing helper logs these without injecting device work.

**Why not simply `--no-cupti`:** `bench_gpu_time_with_cudagraph` (utils lines
1436–1502) records ten target calls per graph and rotates only input kwargs.
Expert weights live in closures and are not rotated. Its nominal cold-L2
policy is therefore not the same as flushing the whole cache before each
single-call graph; using it as the sole timer corroboration would confound
cache policy and graph launch amortization with timer choice.
