# Primary benchmark and paired scorer timing boundaries

Read-only source audit on 2026-09-08. This is a design review, not a new measurement or a recommendation to change the ongoing five-shape experiment. Production source and frozen timing helpers were not edited.

## What the two measurements contain

| Boundary | Primary full benchmark, CUPTI | Paired GPU graph scorer |
|---|---|---|
| Closure | `route()` then `layer.forward(tensors)` | `w4a16_mega_moe` on already staged workspace inputs |
| GPU work | Routing, BF16 activation/route staging, Mega, external TopkReduce | Mega and external TopkReduce |
| Output ownership | Public layer allocates its output during graph capture | Reuses the fixture's output tensor |
| Cache policy | Zeros a 2×L2 byte buffer outside the measured span before every replay | Hot cache, fixed inputs; `cold_l2_cache=False` |
| Replay pacing | Local synchronization before and after each replay | Queues ten event-bracketed replays, then synchronizes once |
| Per-replay rank barrier | None | None; one barrier before each scorer |
| Distributed statistic | Median of per-index rank maxima | Maximum of rank-local medians |

The primary CUPTI span starts at the first correlated GPU kernel/memcpy/memset activity and ends at the last. It includes gaps between those activities; it excludes the L2 flush and host preparation outside the launch window. Its ordinary CUDA-event alternative adds a rank barrier before every replay, so it is another distinct policy.

The paired graph utility also does its own side-stream warmup and estimate replays. The CLI timing method on the diagnostic worker does not select its scorer: the worker replaces the primary `_run_distributed_iterations` path and explicitly invokes the two saved scorer functions.

## Minimal reuse choices

1. **Metric-only change on staged operator inputs:** keep `autotune_knobs` candidate dictionaries, ordering, compilation/warmup barriers, winner application and cache callback. A narrow optional measurement callback could replace only its wall-clock loop for W4A16, with other backends retaining the current behavior. The callback must capture an asynchronous `w4a16_mega_moe(..., sync=False)` call, including TopkReduce, after eager compilation. This would measure the staged operator; it would not reproduce the full benchmark closure.
2. **Match the public operator span:** supply a narrow asynchronous stage-and-compute closure from the backend, where the original `MoEEpTensors` are still available. Staging currently runs before the backend enters autotuning, so changing the low-level timer alone cannot include it. Do not invoke `layer.forward` recursively from its pending-autotune compute path. The benchmark's router is outside the public MoE operator contract; adding router-logit inputs to the production tuner merely to mimic this benchmark would expand the API unnecessarily.
3. **Use the exact full benchmark span for an effort-level ranking diagnostic:** reuse the benchmark's existing `run_once` closure and primary utility, holding an explicit candidate fixed outside capture. This is the direct way to compare candidate rankings under the already published timing policy without changing product APIs. It should remain separately labeled from the current paired hot/staged scorer.

The ongoing five-shape results should first establish whether GPU-oriented rankings help under the tested staged/hot policy. They cannot alone show which of omitted staging, cache policy, pacing, or aggregation explains a disagreement with primary timings.

## Implementation pitfalls to preserve in any future patch

- **A cold-cache Boolean is insufficient.** `bench_gpu_time_with_cudagraph` implements cold cache by rotating explicit tensor arguments. With the paired closure's empty argument lists it warns and disables cold mode. Symmetric workspaces captured by a closure cannot be transparently cloned or rotated. An explicit flush outside a captured single-call graph is needed to reproduce the primary policy. Reusing `bench_gpu_time_with_cuda_event` around an already captured graph's `replay` can reuse its flush mechanism, but its queued replay pacing still differs from primary CUPTI.
- **Do not replace the wrapper with `make_launch_thunk`.** That thunk omits the external reducer. Warm up the reducer before capture, including empty-rank behavior; captured execution must use `sync=False` and the current CUDA stream.
- **Release graph ownership before applying the next candidate.** `apply_knobs` can replace/finalize local workspace state. Synchronize and reset the graph first; do not retain every frontend or compiled object merely to cache observations. A callback should complete graph cleanup in `finally`, without attempting recovery after a GPU fault.
- **Choose aggregation explicitly.** `MAX(median(samples))` and `median(MAX_per_index(samples))` are not interchangeable. The latter can reuse the primary utility's list aggregation and then the median. If every rank already receives the same aggregated score, the generic final MAX is redundant but numerically harmless; its printed statistic must describe the selected policy accurately.
- **Keep collectives aligned.** All ranks must use the same candidate and scorer order, including empty ranks, and complete the same capture/measurement lifecycle. The current generic exception path assumes deterministic candidate failures; it does not establish safe recovery from rank-local resource failures or runtime faults. Do not broaden score-and-continue semantics as part of a timing change.
- **Do not make CUPTI a silent product requirement.** Its activity callbacks, finalization and optional dependency can conflict with another profiler. The utility's CUDA-graph fallback has different cold-cache behavior with zero-argument closures. A product scorer must make any fallback policy explicit and verify it, rather than silently claim the primary CUPTI metric.
- **Keep cache evidence separate.** The current winner cache is keyed by capacity, while this benchmark can tune different actual token counts at one capacity. Any repeat must record its actual resolved candidate and measured token count; no row-minimum substitutions into an earlier full sweep.

## Source references and identity

Paths are relative to the effort root. Line references identify the audited current source, not an API stability promise.

- `flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py`: 828–892 (primary timers), 1202–1218 (flush, routing, full closure, warmup).
- `flashinfer/flashinfer/testing/utils.py`: 751–771 (per-index aggregation), 914–934 (CUDA-event loop), 1178–1250 (CUPTI graph setup/replay), 1284–1313 (activity span), 1441–1453 (empty-input cold-cache disable), 1484–1544 (graph capture and queued replays).
- `flashinfer/flashinfer/moe_ep/modes/mega_layer.py`: 225–245 (output allocation before staging, then compute).
- `flashinfer/flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py`: 171–214 (staging and pending-autotune entry).
- `flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/frontend.py`: 310–341 (current-stream Mega launch), 343 onward (raw launch thunk), 575–628 (wrapper and external reducer).
- `flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/autotune.py`: 153–241 (generic lifecycle), 429–489 (W4A16 synchronized wrapper and winner cache callback).
- `candidates/w4a16_tuner_metric_experiment_five_shapes_512_recovery0908b/worker.py`: 164–217 (staged wrapper and reducer guard), 258–277 (scorer warmup/barrier/sample reduction), 381–388 (primary loop replacement).
- Same folder `timers.py`: 30–39 (single-call hot graph scorer); `protocol.py`: 35–49 (MAX of local medians).

Attested source hashes:

- Primary benchmark: `b4e845f3b43805e8056be2ac32dc87c452bed8211bfe612f74b04feb65681a09`
- Testing utilities: `3a7515a237a3c6531ffa15829a5d46e3d399b3c23f7d3dba853f9e6be46da490`
- Paired timers: `057fe6e081f10a7d36c936ffd1ca95f7df266648775f160553bb34f205d7cc2d`
- Paired worker: `7387b57c48e61a25dbf429f27c57d915c4927ed8f54bf92e585164530d848741`

Primary benchmark/testing utilities match git6315; the C1 and 512 paired timer bytes are identical. Current e2d88 source is frozen during the five-shape diagnostic. No result from that unfinished run is claimed here.
