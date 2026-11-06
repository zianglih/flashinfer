# Seeded-uniform synthetic routing: read-only proposal

Audited clean `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. No source changes or GPU work. [Source/hash/arithmetic receipt](source-audit.json).

**Recommendation:** test Hopper's seed-515 global uniform top-k draw as the swap-AB blockscaled routing initializer. It is independent of serving warmup contents and removes three separate distortions in the shared balanced helper. This is a candidate policy, not a measured Blackwell improvement; wait for the current actual-input holdout and separate native eager/graph comparison before launching it.

## Minimal integration

- Put a private initializer in `blackwell/moe_swap_ab_tuner.py`, selected once by the existing `swap_ab` mode in the blockscaled runner constructor. Generate FP32 scores of shape `(profile_tokens, num_experts)` on the supplied device with a **private** `torch.Generator(device=device).manual_seed(515)`; return `scores.topk(profile_top_k, dim=-1).indices.to(dtype)`. Explicit FP32 avoids global default-dtype changes affecting memory or random selection. The private generator leaves global RNG state unchanged.
- Use this initializer for input #2 and set `inputs_pre_hook=None` only for swap-AB. This avoids first creating random IDs and then overwriting them. Both public wrapper and functional APIs already share this tuning config; no callsite wrapper, actual-input capture, public option, tactic, or cache axis is needed. This would supersede the experimental actual-input hook, not stack with it.
- Legacy/Rubin retain their current initializer and balanced hook; W4A16 has a separate runner and remains unchanged. Reuse Hopper's algorithm, not its graph-mode, arena, or value-aware-cache options. Avoid touching Hopper merely to deduplicate its short implementation.
- Existing `tuner.py:574–576,617–631,673` are the integration points. Hopper's source is `sm90_tuner.py:275–298`. The new generator is dtype independent: one ID policy covers NVFP4, per-token NVFP4, MXFP4x8, and MXFP8.

## Distinct defects and limits

For `T` tokens, global `E` experts, local `L` experts, top-k `K`, the balanced helper first raises this rank's quota from mean `mu=T*K/EP` to `Q=ceil(mu+sqrt(mu*log(EP)))`, then spreads Q almost perfectly across L experts (`_inputs_helper.py:93–110`). These are two different choices: an approximate maximum-rank workload bias and suppressed expert-count variance. The latter can create artificial row-tile boundaries even when total local work is similar.

Its zero-quota loop is a third issue: it writes an assignment before checking the quota (`:161–173`). At T4 all requested per-expert quotas below are zero or one, so it assigns one route to every local expert until all top-k slots fill:

| Model/default EP | Uniform expected local rows | Intended balanced quota | Current actual helper rows |
|---|---:|---:|---:|
| V3/8 | 4 | 7 | 32 |
| V41F/4 | 6 | 9 | 24 |
| K3/8 | 8 | 13 | 64 |
| N3U/8 | 11 | 16 | 64 |

Uniform top-k uses distinct global IDs per token, has expected local work `T*K*L/E`, and does not force work into a zero-quota expert or rank. It naturally supports nonzero local offsets. A tiny seeded draw can legitimately have zero local work; do not silently retry or force a minimum, which would introduce a different workload bias. Check actual seed-515 local histograms at tiny buckets and multiple rank offsets before retention. The statistical zero-local probability at T4 is about 1.31% for V3 and 0.000604% for N3U; a single seeded draw is not an expectation guarantee. Uniform routing also does not reproduce learned expert skew or grouped-router correlations.

Row allocation is distinct from executed MMA width. Local tile count is `sum_e ceil(count_e/route_tile)`. The current kernel rounds MMA token width to `8*cta_group_size` (`moe_swap_ab_kernel.py:167–171`), while route allocation and tile startup still use the routing tile. Extra padded tiles can add scheduling, loading, and epilogue overhead without performing a full routing-tile-width MMA. The older audit's blanket 16-column statement does not apply to current one-CTA tactics.

## Allocation, device, and timing constraints

- The input initializer receives the profile shape, original device, and original routing dtype (`autotuner.py:4212–4255`); use those values, not the initiating serving request's shape. Require the existing valid top-k domain `0 < K <= E`; top-k yields distinct indices even if scores tie. No CPU/GPU or cross-version bit-identical RNG claim is needed.
- Initialization runs once before each missing profile's tactic loop, outside tactic timing. It cannot begin during an active outer graph capture (`autotuner.py:2833–2853`). Existing cold-batch handling retains these inputs for blockscaled profiling. Do not import Hopper's arena configuration or change NV eager/MX graph native timing as part of the routing experiment.
- Current K3 and N3U full native caches verify maximum profile T16384. FP32 scores require 56 MiB/32 MiB; top-k values, int64 indices, and int32 result account for another 4 MiB/5.5 MiB in a conservative simultaneous visible-tensor sum. Thus **60 MiB K3 / 37.5 MiB N3U**, plus backend-specific top-k scratch/allocator overhead. This is an analytical tensor-payload bound, not a measured total allocator peak. Top-k values may be freed before the final cast, reducing actual live payload.
- It generates/scans 14,680,064/8,388,608 score elements for those maximum profiles: O(T*E) score generation plus top-k selection. Existing CPU code creates O(T*L) permutations (1,835,008/1,048,576 int64 elements), converts each to Python lists, performs rejection/slot loops, and copies only the final IDs to the GPU. Its tensor payload is about 15.06 MiB/9.44 MiB on CPU, plus Python objects and temporary selection lists; final H2D IDs are 1 MiB/1.375 MiB. No wall-time advantage is claimed without measuring setup time and GPU allocator peak.
- Workspace bounds already cover any local distribution with at most T*K routed rows (`moe_utils.py:137–201`), including all-local or zero-local work. `get_valid_swap_ab_tactics` uses shapes and capacities, not route values; the same admitted tactic set must be verified. Larger future profiles scale score storage linearly; do not hardcode a model-size cutoff.

## Local history and required boundaries

**The zero-quota guard was retained previously, but did not survive into the current add-on source.** Commit `1a33d30c93400a8eff26f09cf9a3586ae66cb26a` added `if num_tokens_j <= 0: continue`; final historical `fca8462cbd9096059d0019a206aa760fb34ca8c4` still contains it. [Archived exact commit patch](historical-zero-quota-guard.patch). Current 1e69 helper is byte-identical to PR base `002529e17` and lacks that guard. The receipt proves both states; the audit does not infer why it was removed during scope/rebase work.

[`scripts/stage_capacity_experiment/AUDIT.md`](../../scripts/stage_capacity_experiment/AUDIT.md) records 49 focused passes and retained paired results, but those results combine the guard with stage-capacity changes and do not isolate its speedup. [`scripts/perf_round_20261027/v3-mxfp8-prefill/autotune-profile-audit.md`](../../scripts/perf_round_20261027/v3-mxfp8-prefill/autotune-profile-audit.md) found the balanced routes narrowed N256's advantage (1.0861x actual versus 1.0178x synthetic) without reversing its ranking; it did not test or reject seeded-uniform routing. The older [routing profile audit](../../scripts/auto_routing_profile_audit/AUTO_ROUTING_PROFILE_AUDIT.md) showed 96 versus 77 N128 tiles for synthetic versus actual V3 T8192 routes. A search of project `scripts`, `evidence`, and current optimization Markdown found no prior Blackwell seeded-uniform experiment or rejection; existing mentions are Hopper source and proposals.

Any subsequent comparison should hold source, admitted tactics, native timer/graph policy, workload, and caches apart from the initializer constant; use fresh selection caches and frozen matched CUPTI measurements. Verify no global RNG mutation, same shapes/device/dtype, distinct in-range IDs, local-count conservation across offsets, existing zero-work behavior, and finite unchanged-API results. Report tiny/held-out route sensitivity and setup allocation/time separately. None of these proposed checks was run by this read-only audit.
