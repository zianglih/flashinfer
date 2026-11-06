# W4 partially live transform group

Prototype only, unstaged in `flashinfer-w4-partial-group-review`, based on retained `49c91adf`. Final source hash: `b25dacfac38c3193a4368e87be2ec058f0da71fbc76db6b56490679b42676851`. Only `moe_w4a16_kernel.py` changes; no signature, public option, tactic, pipeline state or Mega call site changes. The full/generic transform body is written once.

## Mechanism

The retained optimization skips wholly unused 128-K transform groups. Actual CuTe ownership records from the prior retained qualification prove that each thread owns a contiguous logical K interval in units of complete 16-value TMEM store atoms. A live64 prefix therefore needs four of the existing eight `St32x32bOp(Repetition(8))` atom copies;96 needs six. These are fewer repetitions of the same warp-wide instruction, not smaller lane masks or a new unsupported PTX repeat qualifier.

For stageK256:

| Final logical remainder | WG0 transform/store K | WG1 transform/store K |
|---:|---:|---:|
| 64 | 64 | skipped |
| 96 | 96 | skipped |
| 128 | 128 | skipped |
| 192 | 128 | 64 |

The prototype computes the partial group's extent from existing `consumed_k` and group geometry. It rounds to the decoder's existing minimum32-value/two-SF16-block unit, bounded by the full group. This preserves generic M-major K16 acceptance without adding a16-value decoder or a layout whitelist. A remainder that rounds to the full group retains the old padded transform; no partial dispatch is emitted. Public K-major weights require K32 alignment, so64/96 remain exact.

Two compile-time variants select full or clipped views around the same source body. The choice is uniform for the entire transform warpgroup: only the final K stage's partially live group selects the clipped variant. In K192, WG0 selects the original128 view and WG1 the64 view. A wholly unused group still takes the existing no-decode branch and advances once. Aligned stages/Mega's explicit padded consumed extent have only the full variant.

`gcd(existing_fragment_width, clipped_extent)` picks an already-supported32/64/128 decode width. It allows96 values to use three32-value fragments even where the full group used a128-value fragment. Compact register load/scale views reuse their original allocations. Payload and TMEM destination views use `cute.composition`, preserving the actual partition mapping rather than inventing a positive stride. This matters: the saved per-thread physical source layouts have eight forms, including nested/negative strides after swizzle folding. The small original full-group SF preload remains unchanged.

## Phase and scheduling preservation

The original raw-full wait, decoded-empty acquire, raw-state clone, decoded fence/release/commit, decoded-state advance and lookahead remain common and unchanged. Exactly one variant executes per group/stage.

Within that selected variant, raw state still advances immediately after its last required payload load and before decoding that fragment. The full variant uses the original tensor views and exact statement ordering. A clipped variant can occur only on the last K stage; its advance therefore never starts a next-stage raw peek. No inactive fragment contains a required advance. Existing iKET load/store ranges still push/pop exactly once.

`source-proof.json` reconstructs the full variant by deleting compile-time view-selection aliases and proves its AST equals the retained `_transform_tile`, including the original advance/peek placement. All other22 methods and the private signature are unchanged. This is a source proof, **not** a guarantee of identical compiler scheduling.

## Coordinate proof and capability boundary

`source_proof.py` replays the saved actual-CuTe ownership proof (`experiments/w4-tail-dequant/layout-proof-summary.json` and5,120 records). It checks2,949,120 clipped logical/physical prefix coordinates, all eight source-layout forms, and15,872 stage/group cases at16-aligned logical K. Saved private ownership probes cover CTA-M128 with stageK32/64/128/256; stageK512's ownership passed but its complete kernel is resource-rejected. CTA-M64 already fails retained `transform_partition`. No new whitelist is added, and this proposal does not claim those previous unsupported cases work.

The new composition/recast views have **not yet been compiled**. Arithmetic replay does not establish CuTe lowering acceptance. A failed lowering/resource gate should be preserved, not repaired with special-case geometry branches.

## Required bounded native qualification

Scoped pre-commit, Python syntax and whitespace checks pass. Before timing, reuse the existing exact/native harness for K576 (final64), K448 (final192), K352 (final96), alignedK512 and the shared Mega padded-K path. Exercise both layouts/CTA counts where the saved harness already supports them; preserve existing numerical oracles and compiler options. Inspect actual zero-local/resource records, shortened store/decode regions and unchanged full-K/Mega images. Add a generic M-major K16-tail direct call if the retained direct kernel supports it, comparing control and candidate rather than relying only on the host `can_implement` predicate.

No correctness result, native instruction reduction, timing benefit, or retention decision is claimed at this stage. Net source growth requires a meaningful measured gain if qualification succeeds.
