# PR5019 third history archive and rebase

- Archive: https://github.com/zianglih/flashinfer/pull/6 (OPEN/draft).
- Frozen six-commit head: `acbc0b1f389d34dbeea6b33e64eebfdcc54a0119`; base: `0f96675312288fc87ef8132a05304521584186e3`.
- Prior archives: https://github.com/zianglih/flashinfer/pull/3 and https://github.com/zianglih/flashinfer/pull/5.
- Both frozen branch refs, original description and archive description were verified remotely before rewriting. `original.bundle` provides a local backup; review comments, reviews and all formal threads are saved here.
- Target upstream main: `d97b1801cd9af6f2ea14d37c305ebe07a1bcbca2`.
- Completed: one commit `7ca3eb567a2400df70579d55e9bc717ea1784b0c` atop the target main; pushed with an exact `acbc0b1f` force-with-lease. PR5019 remains OPEN/non-draft and reports MERGEABLE. Both upstream W4A4 SiTU and PR W4A16 tests are preserved. The three-line NCU fix honors precomputed routing before warmup and during profiling.
- Validation: all 34 PR paths retained, 31 byte-identical to archive; only two shared tests and the benchmark differ. All 250 vendored source files match current upstream. Scoped pre-commit (including mypy/Ruff), 32 Python syntax checks, independent AST/dependency audit and before/after CPU NCU-stage checks pass.
- Bot replies posted with exact readback: the cache thread acknowledges intentional legacy-cache invalidation; the summary reply corrects the withdrawn FC2 finding, distinguishes the fixed autotune bug from the remaining shared recovery limitation, and documents the genuine NCU fix. Links are in `completion.json`.
- PR body adds only the third archive link and concise rebase validation. Existing screenshots, performance tables, tested-source pins and checklists are preserved.

Existing C2 pod `devbox-fi-w4a16-align256-r2-0926-0` was absent from namespace `infra` when checked during this operation. No devbox was deleted or released by this task. GPU evidence remains pinned to `acbc0b1f`; no new GPU run is claimed for this history operation. Production W4A16 byte equality and unchanged shared runtime dependencies will be checked independently.
