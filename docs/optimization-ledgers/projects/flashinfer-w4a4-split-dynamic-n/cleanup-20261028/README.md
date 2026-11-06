# PR7290 implementation cleanup

Retained and pushed `d35fcfda03875077b3af8455575cc1d20e866a8c` on
`33b7e526`. All 28 PR paths were audited against merge base `002529e1`;
the nine-file cleanup is +50/−88. No new repository test or tuning knob.

- Reuse the existing tactic decoder instead of maintaining a swap-AB copy.
  Preserve all360 swap-AB tactics, defaults, ordering and W4A16 tactics.
- Remove an unused private wrapper argument and redundant output-SF aliases.
- Simplify two host resource-planner expressions with equivalent results/errors.
  All28 swap-AB device-function ASTs remain unchanged.
- Reuse the existing exact multiply helper in three reference expressions and
  consolidate the sanitizer's identical kernel lists.
- Fix benchmark support notices and missing-result checks to use the actual
  swap-AB and finalize flags. Columns, timing, quantization and winner logic stay
  unchanged. Remove one stale quantizer comment; its entire AST is unchanged.

## Validation

All95 existing selected GPU tests passed:33 accuracy and62 API/wrapper/graph/
autotuner, zero failures/errors/skips. Two B300 GPUs ran in parallel using
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2 and CuTe DSL4.8.0. Nine native
compilation-cache links remain on persistent cluster storage. No sanitizer or
full benchmark rerun.

[Runtime results](validation-RESULTS.md), [independent audit](validation-audit.json),
[frozen source](source.json), and [committed-source binding](retained-source.json)
preserve the exact evidence. Each test group rechecked3,070 tracked Python/shell
files;513 frozen files and the full-index patch matched before/after.

Full-PR and commit pre-commit passed. CPU/source proofs cover1,779,592 planner
cases,2,904 tactic forwards,27 identical invalid rejections,30 legacy forwards,
288 output-SF cases,32 printed tables,24 sanitizer option combinations, and
expanded exact-reference AST equality. These are not fresh codegen/timing claims.

Component audits: [kernel](kernel-audit.md), [interfaces](interface-audit.md),
[benchmarks/tests](bench-test-audit.md), [independent cross-review](interface-cross-review.json).

## Publication and workspace

[PR7290](https://github.com/flashinfer-ai/flashinfer/pull/7290) remains draft.
Its component counts and validation now describe the cleanup. All41 prior
fenced blocks, EP/TP speedup tables and plot URLs are unchanged; the performance
source remains `33b7e526`. [Publication receipt](publication.json).

The canonical checkout is clean. The completed local review clone was removed
after matching all513 source files to the retained commit. The remote source is
clean at the same commit; validation evidence, data link and native caches are
unchanged. [Local cleanup](local-review-cleanup.json) and
[remote advance](validation-workspace-bump.json).
