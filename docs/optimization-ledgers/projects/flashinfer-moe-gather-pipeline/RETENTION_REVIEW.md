# Retention decision at c1ac8ce7

Integration update: the selected revert and remaining retained changes are now
merged into upstream PR #7290's branch as `a620ce77` (tree-identical to `8bc69ee4`).
The user requested a complete benchmark refresh; its validation and performance
receipts are tracked separately under
[`integration/pr7290-refresh-20261030/`](integration/pr7290-refresh-20261030/PLAN.md).
The decision and experiment evidence below describe the earlier retention audit;
its idle and no-further-measurement statements apply to that paused checkpoint.

Optimization work is paused at the user's request. All eight GPUs are idle and
no benchmark/profiler controllers remain; the live check is recorded in
`experiments/w4-cumulative-prefill/paused-idle-check.json`. The PR branch remains
clean at `8bc69ee40cb383a88eadb4fd5ffd7bd0ff2694a4`. The selected W4 helper
change was dropped in that follow-up commit and pushed to fork PR9. All other
retained implementation files are unchanged from `c1ac8ce7`. The helper now
matches `82254e20` byte-for-byte; scoped pre-commit, syntax and diff checks pass.
No GPU validation or timing was run after the revert. See
[`retention-drop/validation.json`](retention-drop/validation.json).

Keep neutral changes when they simplify existing work without adding an
interface or policy. Added interface/kernel complexity needs a measured
benefit. Preserve the user's allowance for slight prefill losses when decode
gains justify them. Separate campaign percentages are not additive.

| Change | Decision | Benchmark evidence and implementation cost |
|---|---|---|
| W4 scale-byte selector in `02de7785` | **Drop this hunk only** | Isolated split +0.082% and GLM5 MegaMoE +0.032% are neutral within variation. Six fewer shifts do not justify a new `byte_index` helper parameter and assembly-string substitution. Restore the original low-byte helper contract; keep the other changes in this commit. |
| FC2 writer-only bulk commit in `02de7785` | **Keep** | +0.076% is neutral. One indentation removes empty commits from nonwriters without adding state, conditions or interfaces. |
| Static MMA scale-byte selectors in `02de7785` | **Keep** | −0.055% is neutral. Compute an existing invariant at compile time without a new helper, argument or policy. Preserve the observed −0.320% tight N3U TP MXFP4x8 T512 loss and the representative FC2 register increase; no throughput or universal resource-win claim. |
| Skip unused W4 dequant groups, `bf072d26` | **Keep** | Decode +1.701%, middle +2.110%; all 24 tested token4–512 cells improve with tight repeats. That pays for the private consumed-K/group-coordinate handoff and guarded data work. Six prefill cells lose 0.24–0.75%; retain those tradeoffs explicitly. |
| Wider nongated activation stores, `49c91adf` | **Keep** | All 18 quantized-prefill cells improve, +3.144% GM; affected retention GM +0.643%. This justifies 24 net lines and the conversion/store refactor, with no public argument or tactic axis. Decode/middle are neutral. Per-token EP8K/16K losses of 0.787%/0.544% are tight and remain accepted tradeoffs. |
| Packed W4 SiTU, `2b8eb9d8` | **Keep as simplification** | +0.275% overall and +1.103% prefill are modest/noisy, not dependable throughput claims. The implementation removes 13 net lines and replaces an existing scalar assembly helper with paired CuTe operations; no additional helper count, API or state. |
| Precomputed W4 transform cutoff, `c1ac8ce7` | **Keep, with explicit tradeoff** | All 15 affected decode cells improve, +0.422% GM with tight repeats; overall +0.159%, prefill −0.459%. N3U TP16K loses about 0.9–1.0% in both reported orders. It adds no interface, scheduling state or tactic and simplifies the stage predicate. Retention follows the user's accepted decode-versus-prefill tradeoff, not a claim of broad throughput improvement. |

Dropping the W4 helper selector is a complexity decision. It is not a claim
that this change explains every prefill regression or that removing it will
recover a particular percentage.

The fresh whole-branch 24-cell prefill comparison is −0.462% GM, with 12
negative cells. It measures `c1ac8ce7` against its original base, not the
post-revert source `8bc69ee4`. Every
negative has repeat spread above 0.5% in at least one arm; three still have both
candidate medians above both controls. Neither fact erases the other. No
further measurement is scheduled while optimization is paused.

Evidence:

- [Fresh cumulative comparison](experiments/w4-cumulative-prefill/RESULTS.md)
- [W4 helper native qualification](validation/w4-scale-selector-r2/RESULTS.md)
- [Shared-helper GLM5 comparison](validation/glm5-r2-attempt3/RESULTS.md)
- [Tail-group results](experiments/w4-tail-dequant/RESULTS.md)
- [Cutoff results](experiments/w4-tail-cutoff/RESULTS.md)
- [Packed SiTU primary](experiments/w4-paired-situ/PERFORMANCE.md) and [separate diagnostic](experiments/w4-paired-situ/ACCA.md)
- [Integer-store results](experiments/fc1-integer-store-performance/FULL_RESULTS.md)
- [Independent swap review](audits/retained-swap-benchmark-complexity-review.md)
- [Independent W4 assessment](audits/w4-retention-assessment-c1ac.md), which records the stricter alternative of dropping the cutoff; the decision above preserves the user's existing tradeoff preference.
