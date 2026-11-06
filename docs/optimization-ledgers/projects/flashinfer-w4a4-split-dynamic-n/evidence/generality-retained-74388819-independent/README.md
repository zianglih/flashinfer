# Retained source audit: 74388819

No blocking correctness, API, or maintainability finding. The clean retained commit `74388819899d0abfd1a12102f7cc108bda13c812` contains exactly the tested R5 patch over `dea2c065`; all 87 source hashes match. All 15 public functions/methods in the two launchers and MoE API retain their prior signatures, with no public K, scheduler, or prefetch controls added.

- **Tactics/cache:** private per-phase K4/K8 and the FC1 scheduler boolean form a flat search. Legacy manual tactics remain accepted, Rubin behavior stays separate, and strict scalar checks avoid accidental coercion. Cache namespace `blockscaled_route_n_v4` prevents pre-expansion persisted winners from suppressing the new search. Effective scheduler and all resource controls enter the compiled-kernel key.
- **Resources/ownership:** SMEM/TMEM limits come from architecture helpers; operand byte estimates are checked against real layouts. Narrow two-CTA SF readiness participates in the same capacity calculation. Remaining SF-atom, accumulator-release, and supported-MMA restrictions express layout/instruction ownership rather than model thresholds. CLC admission preserves SM reservations and grid limits; ancestor publication distinguishes physical CTA0 from executing CLC cluster leaders.
- **Evidence:** 68 focused tests, 72 scheduler replays, and the independent 75-point native screen support retention. The screen verifies actual final host forwarding against selected tactics; its native scheduler field is a request, while bounded replay compile records prove effective modes. The six clean full-token TRT tables are still pending.

Remaining boundaries, not new blockers:

1. Standalone low-level calls and legacy manual tactics use `K=None` resource-derived fallback. Maximizing queued K is feasible but not universally fastest; measured whole-MoE AUTO explicitly searches both K depths.
2. Profiling balances approximate-max expert counts, so actual routed workloads can prefer another scheduler. The retained screen recovered the prior recurring middle-decode losses; the helper contract remains unchanged.
3. When capacity/SM/grid admission makes CLC ineffective, static and CLC requests can compile to the same static launch. The resulting duplicate tuning work is accepted for a simple flat search.
4. The current epilogues release at most 64 columns early, and narrow bulk output stores remain a separately measured implementation boundary. Broad shape coverage and sanitizer validation remain deferred.

The exact source, public-signature, patch, and evidence bindings are in `review.json`; rerun with `python3 evidence/generality-retained-74388819-independent/audit.py` from the project root. No source edits or GPU work were performed for this audit.
