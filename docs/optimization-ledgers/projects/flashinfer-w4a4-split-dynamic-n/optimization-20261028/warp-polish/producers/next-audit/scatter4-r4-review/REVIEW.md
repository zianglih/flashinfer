# Independent scatter4 r4 review

Frozen kernel SHA: `8d8af2711d10f66751c708cd57735556add97a64bc70734222954e4960f14480`.

**Main gate/source/codegen audit passed; r4 was rejected after the matched screen was neutral.** All 192 compiled-artifact hashes and 96 exact replay hashes independently checked against the reused control; source and frozen snapshot agree. No repository source edits or GPU runs were made by this reviewer.

## Source and lifetime

Relative to r3, the AST differs exactly in the row-group loop changing from `range_constexpr` to `range(..., unroll=1)` and removal of the unused `blk_copy` import. Formatting changes do not change the AST (`source-proof.json`).

The loop retains the same warp-uniform two/four-iteration row-group sequence for bulk32/64. Four warps own disjoint consecutive row ranges, all four coordinate shuffles precede elected issue, and each group issues both channel halves. Enumeration covers every row/half pair exactly once (64/128 pairs, `ownership.json`). All per-thread bulk commits, source-read waits, shared-memory reuse/publication barriers, sentinels and accumulator releases remain identical to r3. No lifetime blocker found.

## Independent generated-code result

All 96 rolled issue loops across 24 FC2 variants contain exactly four SHFL and two SCATTER4 instructions. Every scatter command belongs to one of these loops. Each loop ends with a uniform `BRA.U`, followed immediately by the slab's bulk commit. There are no implicit lane-arbitration backedges (`BRA.U.ANY`), no `R2UR.OR`, and no uniform-to-GPR spill/fill inside the issue bodies. See `issue-loops.json`.

| Sum across the same 24 FC2 variants | cb35 control | r2 lane-owned | r3 unrolled | r4 rolled |
| --- | ---: | ---: | ---: | ---: |
| Registers | 2686 | 3207 | 3862 | 2619 |
| Text bytes | 616320 | 686208 | 782976 | 650496 |
| Static non-NOP instructions | 37938 | 42318 | 48371 | 40081 |
| Uniform-to-GPR spill/fill pairs | 200 | 193 | 803 | 184 |

These aggregate resource sums describe code generation, not performance. R4 restores bounded uniform-register live ranges and removes r3's new issue-region spills. Relative to cb35, however, text grows 5.55% and static non-NOP instructions grow 5.65%; dynamic loop work is different, so static count is not an executed-count comparison. Whole-kernel spill/fill still exists outside the issue loops. Config5 static PDL-off has 38 pairs versus 37 in cb35; retain this exception. All variants have zero LOCAL/STACK and no local-memory load/store sites. Full per-variant records are in `audit.json`.

## Qualification boundary

The main six-config gate naturally exercises bulk64/stages2. The separate supported-constructor-stage-override gate completed 64 BF16 control replays with naturally selected bulk32/stages1, but its candidate was stopped on root instruction after r4 was rejected; no bulk32 candidate runtime/codegen qualification is claimed. Its attempted public FP16 output was rejected by the existing BF16-only unfused finalizer before candidate execution; this is not a candidate failure. Earlier standalone copy probes cover FP16 storage only. Native benchmark winners and constructor/storage qualification remain distinct.

The scheduler independently checked the matched screen and root rejected r4 at approximately +0.0043% overall and −0.0024% prefill. This reviewer independently checked source/gate/codegen, not timing aggregation. No retained source change or speedup claim results from this experiment. R2/r3 were also rejected. The gate evidence remains useful closed history; no further GPU work is proposed.

Reproduce the main read-only audit with `python3 optimization-20261028/warp-polish/producers/next-audit/scatter4-r4-review/audit.py`.
