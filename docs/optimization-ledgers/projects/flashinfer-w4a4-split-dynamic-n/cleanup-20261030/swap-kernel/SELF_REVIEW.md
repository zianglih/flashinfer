# Retained swap-AB kernel cleanup

Base: `658a0c8942c7454050f990c0be3083aa61b6a89f`. Frozen edited file: `194b903854c74fc79a422ec67a0539d9f57414987c8cc0a3325e94226d642eb4`, 28 additions / 45 deletions. Changes remain unstaged.

- Consolidate the duplicated channel-tile MMA calls into one compile-time-unrolled loop. Tile 0 and tile 1 retain their original accumulator, weight fragment and scale pointer; activation operands remain shared. The operand release still follows all channel-tile MMAs. iKET marker names/order are preserved.
- Discard the MMA warp's unused returned expert ID without changing metadata reads, waits, release or cursor advancement.
- Remove the unused kernel output-dtype field. Reuse the epilogue's gated classification instead of storing/recomputing the same activation configuration in the kernel wrapper.
- No new helpers, interfaces, knobs or tactic axes. All existing comments and license text remain identical. No rejected experiment is imported.

## Fix before claiming validation

- **High confidence:** GPU compilation, loaded-resource comparison and existing exact tests have not been run by this agent. A source-level static proof does not establish identical generated code or performance. Root owns the frozen source qualification.

## Reviewer notes

- **High confidence:** `prove_cleanup.py` enumerates the one/two-channel-tile and iKET off/on cases. It expands static aliases and folds only literal zero/one arithmetic; both versions have identical ordered MMA/marker calls and arguments. After normalizing these exact edits, the whole module AST is identical. Stage planning, layouts, synchronization, barriers, PDL, budgets and epilogue arithmetic are untouched.
- **High confidence:** the old wrapper gated expression is AST-identical to the epilogue's existing expression after substituting its constructor argument. The constructor supplies the same activation type. The host launcher and existing tests do not read the removed private fields.
- **High confidence:** syntax compilation, whitespace validation and scoped pre-commit (including mypy/ruff) pass. Formatting changed line wrapping once; the final frozen hash passed the second run.
- **Boundary:** no speedup, SASS identity or unchanged-resource claim is made until the parent qualification finishes. M512 exercises the newly consolidated second tile; single-channel paths and optional diagnostic markers also need compiler coverage.

Artifacts: `cleanup.patch`, `validation.json`, `static-equivalence.json`, `before.py.txt`, `after.py.txt`, `precommit.log`. No commit, push, GPU or PR operation was performed.
