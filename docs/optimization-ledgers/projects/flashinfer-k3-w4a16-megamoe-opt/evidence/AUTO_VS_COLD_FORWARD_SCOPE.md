# AUTO score versus reported layer latency

The selector and the reported benchmark intentionally time different scopes. **AUTO includes fused hidden-state/routing-input staging inside MegaMoE; it omits the adapter's separate expert-alpha staging copies.** Its repeated graph/event score also differs from the benchmark's cold-L2 CUPTI span and aggregation order. These source facts permit different rankings; they do not establish the cause of any M128 result.

Audited commit: `48fce528a70b7bc10c26307dfd2155491d50cfe9`. Exact inspected-file hashes are in `auto-versus-cold-forward-source.json`. All paths below are relative to the FlashInfer checkout. No compilation, GPU work, profiling, timing changes or source edits were performed.

## Call path and staging boundary

1. `benchmarks/bench_cute_dsl_moe_distributed.py:1350–1389` builds tensors with runtime FP32 `fc1_alpha` and `fc2_alpha`, calls routing once, then `layer.warmup(tensors)`. Its timed `run_once` calls `layer.forward(tensors)`; with precomputed routing it does not rerun top-k selection.
2. `flashinfer/moe_ep/modes/mega_layer.py:300–360` warmup invokes one full forward. `forward`, at373–440, gets prepared weights/workspace, allocates the output, calls backend `stage_inputs`, then `compute`.
3. `flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py:222–279` stages supplied FP32 expert alphas (and optional norm constants) using one `torch._foreach_copy_` launch for the normal non-aliasing case. It **does not copy hidden states/IDs/weights here**: it records their source tensors in `workspace._staging_inputs`.
4. That backend's `compute`, at281–330, invokes AUTO once if pending. AUTO repeatedly calls the lower-level `bf16_nvfp4_mega_moe` wrapper directly, not `layer.forward`. Therefore the expert-alpha copy already happened before the sweep and is outside each candidate's timed graph. The source pointers survive the whole sweep; `_staging_inputs` is cleared only in `compute`'s final cleanup.
5. `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:865–914` passes `_staging_inputs` into the frontend; `run`, at455–515, selects the corresponding staging specialization. The kernel at `megamoe_kernel.py:1484–1494` calls `token_comm.stage_inputs` from dispatch warps before exchange. `token_comm.py:23–103` copies live BF16 hidden states plus top-k IDs/weights and pads unused IDs. **This GPU staging is inside both AUTO and measured forwards**, even though AUTO reuses the same source tensors.

During a measured graph replay, `layer.forward`'s separately captured alpha-copy operation precedes the Mega kernel again. The kernel still reads the same FP32 alpha semantics in both paths. These alpha copies are distinct from loading NVFP4 E4M3 block scales or decoding weights, which remain kernel work in both. Runtime normalization is not supplied by this benchmark.

## What each score measures

| Dimension | Candidate AUTO score | Reported distributed layer latency |
|---|---|---|
| Timed call | Lower-level Mega wrapper, including fused input staging, dispatch, FC1/activation/FC2, return and deterministic combine | CUDA graph captured from `layer.forward`, including runtime expert-alpha copies and the same Mega work |
| Cache policy | Repeated graph replay with no explicit L2 flush; “hot” describes that policy, not a guarantee all weights fit in cache | L2 flush buffer, twice the queried L2 size, zeroed before each sample and excluded from its measured span |
| Samples | Default10 CUDA-event samples per candidate, after3 eager preparation calls and6 graph warmup replays |100 CUPTI samples per point after the configured3 outer warmups; the utility also performs its own graph preparation and estimation calls |
| Rank reduction | `max_rank(median_iteration(event_elapsed))` | `median_iteration(max_rank(activity_span))` |
| Selection versus report | Choose the smallest reduced candidate score | Report the selected tactic's full-forward latency using the second protocol |

The AUTO defaults and graph loop are in `bf16_nvfp4/autotune.py:48–109,116–157,196–229`. The backend does not override its10-sample default. Graphs are reset before a later tactic reallocates workspace. There is no cold-L2 option used in this selector.

The benchmark at `bench_cute_dsl_moe_distributed.py:937–1040` requests CUPTI, CUDA graphs, `cold_l2_cache=True`,100 repeats, and `aggregate_op=max`, then takes the sample median. `flashinfer/testing/utils.py:1182–1256` prepares the graph and flushes/synchronizes before starting each iteration's CPU correlation window. At1145–1152 it collects concurrent-kernel, memcpy and memset activities; at1290–1318 it reports latest GPU activity end minus earliest start and then reduces samples across ranks. The flush is outside the correlation window. This is a GPU activity span, not Python `forward` wall time: ordinary validation/allocation/capture preparation should not be counted as per-replay host overhead.

The rank/median operations need not commute, and the cache policy, timed alpha copy and timing instrument are also different. No source-only argument determines their contribution to a particular regression, or proves which tactic would win a cold full-forward tuning sweep. This note is local methodology context and is not added to the clean PR by default.
