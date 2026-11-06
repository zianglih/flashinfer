# Scheduler follow-up mechanisms and trace scope

Read-only source reasoning while the existing group-scan A/B/A runs. No additional patch, tactic, GPU launch, or sealed-bundle change is prepared.

## Residual scan elimination: exact restricted identity

The beginning of `_advance_group` walks unvisited experts left in the old group and pushes the last expert, solely to recover the next group's global padded-row and token-block prefixes. [Current residual walk](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:743).

For each expert before the group boundary, let `b[e] = ceil(tokens[e] / C)`, with `C = params.cluster_tile_m`, and let `F1 = _num_fc1_intermediate_blocks`. Existing group construction already maintains:

```
cumulative_fc1_tiles_at_group_end = F1 * sum(b[e])
```

When `token_padding_block == C`, padded rows per expert equal `C * b[e]`. Therefore the state needed immediately before the new group-start checkpoint is exactly:

```
blocks_at_boundary = cumulative_fc1_tiles_at_group_end // F1
current_token_block_cumul = blocks_at_boundary
current_data_cumul = blocks_at_boundary * token_padding_block
```

This replaces the residual loop and final push with an exact constant division and multiplication. No new metadata, buffer, count load, synchronization or persistent field is needed. The first group uses zero cumulatives and remains correct. Empty experts contribute zero; skipping an entire group does not change the identity. It uses the existing nonnegative-count, positive-feature-width and Int32-representable-work contract.

The other fields modified by the residual walk are transient: later in the same function, group priming resets phase, expert index, expert tile end and previous-expert caches, and `_advance_expert_within_phase` rewrites the selected expert's start/end/count. The residual walk has no side effects beyond scheduler state and plain count reads. Its data/token-block prefixes are the only results that survive into the checkpoint. Greedy boundaries, phase order, work IDs, atomics and publication are unaffected by this identity.

The production frontend sets token padding to MMA N. Supported clusters split features, so scheduler swap-AB makes `cluster_tile_m` equal that same N. [Frontend binding](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:259); [coordinate swap](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/moe_persistent_scheduler.py:323). **A constexpr equality guard is required**: the raw kernel permits smaller padding divisors, for which padded rows cannot be recovered from token-block totals. Preserve its scalar fallback. [Raw constructor boundary](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:196).

The mechanism removes redundant metadata traversal rather than changing its granularity. Its benefit is limited to transitions between multiple groups. It cannot improve a single-group T4/T32 run, and may be small when a cluster is already near the old group's final expert. Do not stack it onto the running boundary-scan trial before that trial is assessed.

## Sparse expert seek: larger potential, more code

Even with cooperative group construction, `_gen_work_from_cluster_idx` still invokes a scalar loop to seek the expert containing each claimed tile. FC2 rewinds to the group start and repeats that traversal. [Seek loop](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:968); [FC2 rewind](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:710). Current SM100 W4A4 has the same sequential structure; this is not evidence that its scheduler is inherently more efficient.

There is an existing implementation precedent in SM107: `_seek_expert_for_work_id` loads a warp of counts, prefixes phase tile counts, ballots the first containing expert, and broadcasts its counts and preceding padded prefixes. [SM107 mapper](flashinfer/flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/schedulers/fc12_mapping.py:652). A W4A16-owned version can be simpler under the same equal-padding guard because a single token-block prefix determines both work and padded-row offsets. Preserve the current no-seek fast path when the claimed tile remains in the cached expert.

The saved K3 histogram gives a specific sparse-decode reason to investigate this. Modeling the original seek for each valid FC1 claim among initial IDs 0–73 (74 clusters on 148 SMs, N64/M256/G1024) yields:

| Global tokens | Mean expert entries read per initial FC1 claim | Maximum |
|---:|---:|---:|
| 4 | 24.57 | 79 |
| 8 | 12.78 | 42 |
| 16 | 6.78 | 22 |
| 32 | 4.45 | 16 |
| 128 | 2.10 | 5 |
| 512 | 2.05 | 4 |
| 4096 | 1.40 | 3 |

These are CPU counts from the exact saved B300 routing histogram, not measured time or a simulation of subsequent atomic claim order. T4 contains 590 valid FC1 IDs across eight ranks; the remaining two initial IDs enter FC2 and are excluded. Source: `../nvfp4-w4a16-blog-draft/runs/kimi-k3-ep8/c2-b300/sweep-1.log`, SHA256 `968661c55bdd82cea030b9435c4cdd2326911652d7ba403d88d6a16700fbdbbc`.

This points to T4–16, not a blanket replacement for dense prefill: a five-shuffle scan can cost more than the one to four scalar count reads seen in dense cases. A safe implementation requires exact work-ID/prefix state comparison across phase/group changes, zero experts and skipped tiles. It should follow exposed-time evidence or a clear win in the currently running boundary-scan probe.

## What the pending IKET trace can establish

The SM100 W4A16 source has **one broad `scheduler_select_next_work_tile` range**, not distinct group, residual and expert-scan ranges. Do not label its full duration as count scanning: it also includes the atomic claim, cluster broadcast/waits, state advancement and the nonblocking readiness peek. SM107's finer `scheduler.group_scan`, `scheduler.residual_scan` and `scheduler.expert_scan` names are not present in this kernel.

| Actual marker / role | Evidence and interpretation |
|---|---|
| `sched_wait_dispatch_metadata`, warp 7 | Separates waiting for routing counts from scheduler work after metadata is published. A long span here does not support a faster count scan. |
| `scheduler_select_next_work_tile`, warp 7 | Look for long selections after metadata readiness, especially the first selection, FC1→FC2 rewinds and FC2→FC1 group transitions. It bounds scheduler selection cost but does not isolate the three scans. |
| `sched_publish_work_record`, warp 7 | Payload is `(phase << 16) | expert`; `-1` is terminal. FC2→FC1 identifies a new group. A long publication can mean the queue is full and compute is behind, rather than scheduler starvation. |
| `weight_wait_sched_record`, warp 5; `activation_wait_sched_record`, warp 6; `transform_wait_sched_record`, warps 12–19; `mma_wait_sched_record`, warp 4 | Establish whether a long selection is actually exposed to consumers. Queued records and overlapping GEMM work can hide scheduler time. |
| `mma_wait_weight_tmem_ready` versus `mma_wait_activation_smem_ready` | If downstream issue stalls, distinguish a missing decoded-weight pipeline from unavailable activations. Trace weight/decode availability back to scheduler starvation before assigning causality. |
| `dispatch_stage_local_inputs` and `dispatch_exchange_tokens`, warps 8–11 | The latter wraps inherited transport, including dispatch count exchange and token pulls. Current inherited `Dispatch_Prep`, `Dispatch_Barrier`, `Dispatch_Pull` are narrower markers on their selected CTA/warp. Do not confuse CPU top-k routing—which the adapter completes before launch—with device dispatch metadata work. |

Useful evidence is a long selection that delays the next descriptor while the associated consumers have exhausted their records, followed by delayed weight/decode/MMA progress. A long selection overlapped with useful GEMM work or a long queue-publication wait is not exposed scheduler overhead. Within-group expert changes and phase transitions help localize the broad range; they do not separate atomic latency from scan instructions.

The pending sealed cases are T512/N64 and T4096/N128. Both can reveal multi-group transition/residual behavior, but they **do not cover sparse T4–16**, where the seek-count model is most compelling. No conclusion that sparse seek is hidden should be drawn from those dense traces. The recording filter captures one CGA of the full native grid, so its initial atomic claim and useful-work assignment must be checked. Analyze each GPU's clock separately, preserve instrumentation caveats, and confirm any change with the uninstrumented native CUPTI benchmark.

Current source marker locations: [scheduler selection](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:1015), [scheduler/consumer roles](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1245), [inherited dispatch ranges](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:1562).
