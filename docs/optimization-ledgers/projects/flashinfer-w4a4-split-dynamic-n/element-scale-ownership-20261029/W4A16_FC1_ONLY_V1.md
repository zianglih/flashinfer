# W4A16 FC1-only producer split, prepared v1

- Workspace: `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-w4a16-fc1-producers-review`; branch `codex/w4a16-fc1-producers`, base `658a0c8942c7454050f990c0be3083aa61b6a89f`.
- Source: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`; SHA-256 `1debc908790cd7fc67f6b9f16f498adf5350053012ba7f913d07b0245d282484`.
- Patch: `w4a16-fc1-only-v1.patch`; SHA-256 `3f9d7703c89da48d19caa0be3af4a0936895d2adc95b996ba30b81da9bd950d7`.
- Source diff: +129/−96 lines (net +33), including the shared-loop reindent; whitespace-insensitive +46/−13. Only this kernel file is modified; all changes remain unstaged.

FC1 with gathered input assigns warp 6 to weight elements and warp 7 to weight scales. A constexpr role loop shares the existing metadata and K traversal. Warp 6 remains the single raw-full announcer and tail owner; warp 7 waits the existing raw-empty phase and issues SFA against that same full barrier. Both contributions keep the original expected byte count. Metadata consumption adds the now-active warp 7.

FC2 retains its original independently progressing A+SFA and B producers, original PDL wait/signal, and original stage lifetimes. There are no new helper methods, fast cursors, polling, buffers, register policies, public knobs or tactics. Both existing A/B review sources were hash-checked unchanged.

## Static validation

- Python compilation, `git diff --check`, scoped repository pre-commit hooks (including mypy, ruff-check and ruff-format) passed.
- `validate_w4a16_fc1_only.py` checks every method except `kernel` is AST-identical to base, regular B producer source is byte-identical, and the entire FC2 kernel AST is identical after folding the known `gather_input=False` / sole role-zero choices. Receipt: `w4a16-fc1-only-static.json`.
- Git worktree and common Git directories both resolve inside this project.

No GPU compile, correctness, liveness, register or performance run was performed. This is a prepared follow-up only; timing is deferred pending the full A/B evidence and authorization. Source specialization checks do not prove generated-code identity or GPU behavior.
