# Split CuTe DSL core branch classification

Read-only audit of the generality review core after the narrow group2/M512 gates, while explicit per-phase K tactic propagation is being developed. The source remains unstaged; notes distinguish implementation ownership from hardware limits. The authoritative experiment snapshots are under `evidence/generality-*`, not the changing review checkout.

## Hardware or format contracts

- MMA instruction kind and descriptor fields depend on FP4 versus FP8 payload formats, scale vector16/32, and E4M3 versus E8M0 scale encoding. These are real ISA/representation differences, not model-specific performance policies.
- Physical M128/group1 and M256/group2 reflect instruction ownership. Logical M512 is two physical M256 instructions reusing B/SFB. The code explicitly implements one or two channel tiles; accepting M768 simply by integer division would be incorrect.
- Canonical activation scale storage has128-row atoms. Aligned N128/N256 routes use TMA; smaller routes use cp.async because a route can start inside an atom. Group2 cp.async requires the now-added cluster-release/acquire readiness join before the leader's S2T reads peer scales. This is a data dependency, not a reason to reject narrow group2 tactics.
- Logical B-copy rows are routeN/group while physical B/accumulator allocation retains at least32 rows for the current transpose epilogue. The extra physical rows are an epilogue ownership requirement; they no longer imply extra activation TMA traffic.
- FP4 mixed operands need byte storage and their own descriptor format; the scale byte offsets and finite output conversion branches are numerical/representation contracts.

## Explicit implementation ownership limits

- Accumulator stages are bounded by the SDK TMEM capacity and at most two producer/consumer windows. The maximum two is tied to current phase/overlap ownership, not an occupancy heuristic.
- Early overlapping accumulator release is currently limited to64 scale columns: the existing activation or bulk epilogue reads/releases at most one/two32-column slabs or one64-column slab. `_accumulator_storage` documents this separately from hardware capacity. Extending that limit requires epilogue/pipeline ownership work, not removing a can-implement check.
- Epilogue scratch supports64-token/two-stage or32-token/one-stage slabs. Capacity chooses between these supported implementations. The widths/stages are implementation options with measured history, not model-specific constants.
- The channel-tile==2 device branches explicitly create the second SFA view, issue the second MMA, and release the shared B/SFB stage after both consumers. They are structural. A future arbitrary channel count would need corresponding scale/accumulator ownership and compile-time loops.
- FC2 mixed-output BF16 admission is stricter than common epilogue conversion support. Public W4A8/W8A8 APIs also explicitly require BF16. This remains an API/admission boundary; FP16/FP32 mixed output has not been gated here.

## Remaining performance policies

- FC1 `use_clc_scheduler=cluster_shape_mn==(1,1)` is a policy restriction with no remaining structural obstacle. Group2 forced gates passed. The isolated all-geometry request screen is near-neutral and supports simplifying toTrue while preserving capacity, SM reservation and grid limits. Evidence: `evidence/generality-clc-auto-r1/README.md`.
- Bulk scatter still prefers routeN>=128. This is not an ISA limit; N32/N64 have compatible slabs, while N16 needs a partial-slab loop. Prior direct-store→bulk and physical-N16 trials were neutral or regressed. Preserve the current measured policy until a new mechanism justifies expansion; do not invent a transaction-utilization threshold.
- Uniform weight/SFA evict-first and activation evict-last are explicit lifetime policies. They intentionally avoid dtype/model/token conjunctions. Their retention evidence is separate from scheduler/K selection.
- K4/K8 are supported instruction-loop choices. Maximizing stagedK alone lost NV decode while recovering MX prefill; the pending explicit per-phase K tactic field moves selection to measured autotuning instead of another dtype/shape threshold.
- Static metadata depth1 and CTA role counts are direct pipeline behavior/configuration. Deeper metadata queues remain an optional measured axis after the all-geometry CLC policy, not an admission requirement.

## Tiny cleanup proposed to the current core owner

Remove the stale module claim that logicalM512 is FC1-only. Replace constructor's M512 special-case count with `max(1, logical_m // 256)` after explicitly requiring logicalM in128/256/512. This matches planner/capability geometry without silently admitting M768 orM1024. No change to accepted policies or emitted code is intended.

No source changes or new GPU work were performed for this branch-classification audit.
