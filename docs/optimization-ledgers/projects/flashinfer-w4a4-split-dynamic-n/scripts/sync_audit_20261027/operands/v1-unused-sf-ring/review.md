# V1: omit an unused scale-factor full ring

Base: `9334cb34fe9c81653dc4748632f44449e9aecd8d`. Independent patch
`d6c62fb8dedf7210da5056adeca334c9046d75a2be53ab16ad2386e3de76daa6`.

The kernel constructs `ab` and accesses `ab_barriers` only when `not self.tma_sfb`.
For TMA-SFB, the existing `a_pipe` full barrier already covers its transaction
bytes. V1 changes that unused array to zero length and gives the compile-time
planner the same transport predicate. It does not change any kernel method's
AST, arrival count, wait, release, tail, state, PDL operation or public argument.

Narrow one-/two-CTA paths retain the existing local cp.async full rings and
cluster readiness join. Wide one-/two-CTA paths omit only unused allocation.
Inline/overlapping epilogues, static/CLC scheduling and PDL on/off therefore
retain the same protocol. Changed shared-memory offsets and possible future
capacity admission are intentional and require actual compiler validation.

Checks: scoped pre-commit, Python syntax and `git diff --check` passed. The
CPU-only actual-method resource probe passed 1,152 metadata cases and 2,880
geometry/format/overlap/scheduler capacity cases. None of those capacity plans
changed; 288 metadata cases save an aligned slab. This does not claim that all
possible admitted shapes or physical struct sizes were exhaustively compiled.

Approved for a focused source-paired exact/codegen gate. No GPU result or
performance claim exists yet. Check actual storage offsets, stages and spills;
numerical output must match retained9334 exactly.

Prior history: `scripts/shared_empty_20261026/README.md` explicitly deferred
this wide-SFB allocation cleanup while retaining its common-empty-ring change.
This is allocation cleanup, not a revival of rejected producer-role or merged
TMA/cp.async publication experiments.
