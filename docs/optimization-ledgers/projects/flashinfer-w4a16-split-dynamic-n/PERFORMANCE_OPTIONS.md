# Split W4A16 dynamic-N performance options

Read-only reasoning against candidate `9ec90d06` on October 24, 2026. These are hypotheses and possible ablations, not measured causes or retained changes. No kernel edits or GPU workloads were performed for this note.

## What can improve, and what stays fixed

The patch reduces issued BF16 MMA N on routed tail tiles and omits wholly invalid epilogue subtiles. It does not reduce the number of K16 instructions, weight/scale reads, FP4 decoding, activation TMA box size, SMEM/TMEM reservation, pipeline stage count, or scheduling barriers. Consequently, less MMA arithmetic can be hidden behind the existing weight-transform/load bottleneck. Full tiles have no arithmetic reduction.

The new scalar work is distributed across roles:

- MMA role: clip/round the valid count and form the instruction descriptor; the helper is called inside the K-tile loop, although the descriptor is invariant across that loop. Compiler hoisting is plausible but must be checked in emitted PTX/SASS.
- Activation role: the second CTA computes a shifted B origin once per routed tile. This is necessary for two-CTA correctness; the static TMA box size stays unchanged.
- Epilogue roles: runtime active-subtile counts replace compile-time capacity counts, adding loop-bound/release predicates and potentially inhibiting code simplification even on full tiles.
- MMA issue lowering changes from CuTe's intrinsic to inline PTX. Repeated election/predicate setup may differ after optimization; source-level instruction counting is insufficient to claim an overhead.

## Scoped options, in priority order

| Option | Why it could help | Boundary / evidence needed |
| --- | --- | --- |
| Compile-time static path at minimum N: one CTA N8, two CTA N16 | Runtime rounding always returns the full allocation, so these tactics cannot save MMA arithmetic. Avoid dynamic descriptors and, for two CTA N16, a shift that is always zero. | Preserve the exact original static accumulation sequence if doing this; the generic helper fallback currently recomputes `k_tile_idx != 0`. Validate min-N tail and empty-private-tile cases. This does not remove any possible dynamic-N gain. |
| Compile-time epilogue count when capacity has one subtile | The legal active count is always one, including the preserved empty-private-tile behavior. Explicitly bypass runtime clip/ceil/max/min and the dynamic loop bound. | LLVM may already fold the `min(1, max(1, ...))`; inspect generated code before claiming any reduction. Preserve release/fence placement. |
| Form runtime descriptor once per routed work tile, before the K loop | If LICM misses it, avoids repeated alignment/bitfield operations for every K256 tile. H7168 FC1 has 28 such tiles and I2048 FC2 has 8. | Keep the shared helper's default behavior for MegaMoE or use an optional precomputed descriptor. If generated code already hoists it, this only improves source clarity. |
| Elect once around the entire straight-line K16 atom sequence | The shared helper currently elects independently around each of 16 atoms per K256 tile. One elected lane can issue all atoms with no intervening warp collective. | Only useful if compiler does not already coalesce elections. Do not move pipeline waits/releases or warp-collective operations inside elected execution. Recheck both CTA groups and MegaMoE. |
| Specialize the accumulate-true atom form | Atoms after the first always accumulate; their inline-assembly `setp` may be replaceable with a fixed true predicate. | Low priority: ptxas likely folds constant flags already, and the baseline also contains this pattern. Require emitted-code evidence. |
| Full-tile static issue branch, dynamic only on tails | Can recover baseline issue code for dominant full tiles in prefill. | Higher code-size/control-flow cost and two mainloop bodies; not a first change. Keep matching B origin and epilogue behavior. Only consider after confirmed full-tile fixed-tactic regression. |

Do not remove the second-CTA B shift, round two-CTA N to 8, add a runtime static/dynamic dispatch without measuring it, or retune the tactic space just to conceal a fixed-tactic regression.

## Interpreting AUTO regressions

1. Match input/histogram and retain the full AUTO result; compare selected FC1/FC2 tactics separately.
2. If tactics changed, run separately labeled fixed-tactic diagnostics for the before and after winners. These do not replace the AUTO rows.
3. For a min-N winner, dynamic-N arithmetic savings are exactly zero; investigate scalar/issue/epilogue codegen first.
4. For a larger-N winner, count full vs partial expert tiles and estimate issued-N reduction from the saved histogram. Large global token count alone does not identify a full-tile workload.
5. If needed, inspect compiled register count/spills, loop structure and descriptor placement before broad profiling. Descriptor math and extra live values can change codegen even when absolute scalar instruction counts are small.

The current ISA permits single-CTA dense BF16 M128 N in multiples of 8 and two-CTA M256 N in multiples of 16; the older vendored C++ wrapper has a stricter M128 assertion, which is not used by the CuTe DSL implementation. Primary shape reference: https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-matrix-shape

## Resolved by retained generated code

`PTX_EVIDENCE.md` confirms descriptor calculation is already hoisted outside the K loop in both tested CTA groups. Do not pursue descriptor-hoisting as an optimization for this generated code. Optional minimum-N patch was never applied; retained source remains `9ec90d0`. Fused performance optimization was explicitly removed from the retention scope by the user.
