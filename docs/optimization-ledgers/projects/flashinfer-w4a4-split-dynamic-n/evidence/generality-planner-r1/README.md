# Automatic K / accumulator resource planner candidate

Based on the frozen general-PDL source. Only the shared core and its two host launchers differ. The source remains unstaged; root owns retention and performance evidence.

- `k_steps=None` chooses K8 or K4 from derived operand bytes, shared pipeline metadata, epilogue scratch, a minimum two-slot automatic operand ring, and the actual TMEM capacity from `cute.arch.get_max_tmem_alloc_cols("sm_100")`. Explicit K4/K8 and requested stage counts retain their diagnostic role.
- Both launchers request dedicated epilogue execution directly. The activation launcher requests automatic overlapping accumulator ownership; the scatter launcher preserves its existing bulk-store ownership protocol. No activation-type or FC1 identity inference is added.
- Accumulator stages are derived from remaining hardware TMEM columns with a maximum two-buffer pipeline. The existing 64-column early-release constraint remains explicit because epilogue reads, not storage capacity alone, determine safe reuse.
- The linear per-stage storage calculation is checked against the actual compiled CuTe layout on every specialization. The 480-case census proves it matches all existing admitted operand/scale/tile/depth modes; the new automatic 90-case SDK check validates actual SharedStorage.
- This does not admit narrow two-CTA geometries. That synchronization change is separate and must account for its extra per-stage metadata in both planning and final allocation.

Proofs: `cpu-check.json`, `sdk-check.json`, `validation.json`. Isolated delta: `planner-only.patch`. Complete source binding: `source.json` (86 pins; full patch b794603468f4db3727fc67d6f14897be6a67c8202b6dd88d709dd7583587322a). CPU validation rejects invalid K, nonpositive depth, impossible automatic depth, and explicit unsafe overlapping-accumulator geometry. No GPU timing was performed by this subtask.
