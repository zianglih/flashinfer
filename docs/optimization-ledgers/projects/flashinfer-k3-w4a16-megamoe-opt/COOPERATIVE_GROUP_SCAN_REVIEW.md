# Cooperative greedy group scan candidate

The standalone [patch](evidence/candidates/cooperative-group-scan.patch) changes only the group-boundary scan in the W4A16-owned scheduler. It is based on upstream commit `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; the active repository has not been edited. `git apply --check` passed. The candidate is gated to a statically known local expert count greater than 32, so the existing GLM5/DeepSeek EP8 path and dynamic-count path retain their original scalar loop.

This is an uncompiled performance hypothesis. The CPU integer audit passes; no GPU correctness, synchronization validation, or performance result is claimed.

## Why this differs from the failed tactic probes

At K3 EP8 the scheduler has 112 expert slots, compared with GLM5's 32. Opening a group currently walks the counts serially until the FC1 tile budget is met, including empty experts. At small K3 decode counts a normal budget often leaves all experts in a single group, so every persistent cluster's scheduler must traverse all 112 entries before its first descriptor. Raising the budget or buffering more descriptors does not remove that initial traversal. [Original scan](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:773); [saved-route model](evidence/tactics/secondary/routing-group-model.json).

The candidate distributes one 32-expert chunk over the scheduler warp. It replaces up to 32 serial count-load/update steps with one coalesced, stride-8-byte count load per lane, five inclusive-prefix shuffle steps, a ballot/popcount, and one broadcast of the selected prefix. K3's full 112-entry scan takes four such chunks. This is a source operation-count comparison, not a measured latency reduction: cache behavior, compiler uniform-load lowering, shuffle latency, extra registers and how much of the scheduler is exposed still matter.

## Exact group-boundary argument

Let `b[e] = ceil(count[e] / token_tile)`, `F1` and `F2` be the existing feature-tile counts, and `B1`, `B2` the existing cumulative tile counts before this chunk. Every `b[e]` is nonnegative. The scalar implementation consumes complete experts until `B1 + F1 * sum(b[e]) >= threshold`, or the expert array ends.

1. Each valid lane loads one expert count. Invalid lanes in a short final chunk contribute zero and do not load memory.
2. Five shuffle/add rounds compute the inclusive token-block prefix at every lane. FC1 and FC2 need the same prefix because their only difference here is multiplication by `F1` or `F2`.
3. The ballot marks valid lanes whose FC1 cumulative is strictly below the existing threshold. Nonnegative counts guarantee those lanes form a contiguous prefix. Popcount is consequently the index of the first threshold-reaching expert.
4. `min(popcount, valid_lanes - 1)` selects either that expert or the last valid expert when the whole chunk is below threshold. Its prefix is broadcast to every lane; both cumulative counts and the next expert cursor are updated identically to the scalar walk.
5. Equality, zero-count experts after a crossing, leading/trailing zero runs, thresholds larger than total work, and a final partial chunk all follow the original stopping rule. A group cannot stall on zero work: a chunk with no crossing consumes all its valid experts.

The proof assumes valid nonnegative counts and Int32-representable cumulative work, as required by the existing scheduler's signed Int32 work indices. It does not promise equivalent behavior on overflowing/malformed counts. The extra speculative count loads within a chunk do not mutate anything.

## Warp convergence and metadata readiness

- The kernel invokes generation only under `warp == 7`; all 32 scheduler lanes participate. Its static block index or existing atomically claimed/broadcast work index is warp-uniform. The new loop's cursor/cumulative values are warp-uniform on entry and after every broadcast. [Kernel entry](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1245); [existing atomic broadcast](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:565).
- The count-load bounds branch and prefix-add predicates contain no warp collective. Every lane subsequently executes every shuffle. The shuffle member mask is explicitly `0xFFFFFFFF`, with clamp 31; source indices below zero are clamped to lane zero, and those values are ignored by lanes below the current scan offset. The ballot uses the same full-warp API already used by token communication; every lane reaches it. The final shuffle's selected lane is uniform and is always a valid participating lane.
- The scheduler waits on the existing dispatch-to-scheduler named barrier before reading counts. Dispatch publishes all count metadata, completes its existing grid/NVLink barrier, and only then signals that named barrier. Therefore loading counts from later experts in the same 32-entry chunk requires no new readiness protocol. [Scheduler wait](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:570); [dispatch publication ordering](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:1597); [raw sizes load](flashinfer/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/moe_utils.py:364).

Residual-expert advancement, padded data prefixes, phase changes, tile ordering/decoding, atomic claims, cluster broadcasts, descriptor publication, readiness peeks, counters and final sentinel creation are unchanged. An empty local count array would not enter the scan; all-zero expert counts still advance to the end and produce the same zero-work group/sentinel behavior in the unchanged caller. The existing sentinel initialization and termination conditions remain in place. [Caller](flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:914).

## Integer audit and artifacts

The [audit script](evidence/candidates/check_cooperative_group_scan.py) models the five simultaneous 32-lane scan rounds and actual ballot/popcount/broadcast selection, then compares the resulting expert cursor and both cumulative counts with the original scalar loop. It performs 174,792 passing boundary comparisons, including:

- Exhaustive four-expert value patterns with leading padding around warp boundaries.
- Zero-length/all-zero arrays, every single populated-expert position across 20 lengths, nonzero starting indices, equality/first-lane/last-lane crossings and partial chunks.
- 4,000 seeded cases with counts up to a million, plus valid cumulative work near the Int32 limit.
- 3,520 complete groupings using the exact 11 saved K3 token-count histograms, all eight EP ranks, both 64/128 token tiles and 128/256 feature geometries, with ten budgets.

The [result JSON](evidence/candidates/cooperative-group-scan.integer-audit.json) records the source histogram hash and scope. The [generation script](evidence/candidates/prepare_cooperative_group_scan.py), [original source snapshot](evidence/candidates/cooperative-group-scan.baseline.py), [candidate snapshot](evidence/candidates/cooperative-group-scan.candidate.py) and [hash manifest](evidence/candidates/cooperative-group-scan.source-audit.json) are retained. The audit is project-local and is not an upstream activation tolerance test.

```bash
python3 evidence/candidates/prepare_cooperative_group_scan.py
python3 evidence/candidates/check_cooperative_group_scan.py
git -C flashinfer apply --check ../evidence/candidates/cooperative-group-scan.patch
```

## Next decision

Compile the isolated candidate and inspect lowering/resource use before interpreting timing: full-mask collectives must remain outside divergent branches; count loads must remain in bounds; all group-state updates must use the broadcast prefix; scheduler register growth must fit its 80-register role budget without spilling. Fixed existing N64/G1024 and N128/G1024 tactics make a suitable initial A/B/A comparison. A changed outcome requires the usual post-speedup GPU correctness validation; the integer audit cannot establish GPU synchronization safety.

The patch only accelerates the initial/group-boundary scan. The subsequent `_advance_expert_within_phase` and residual-cursor loops still traverse expert counts serially. Even a large scan micro-improvement may have little whole-kernel effect if count traversal is hidden by compute or dominated by those other loops. No claim that this is the current measured bottleneck is made.
