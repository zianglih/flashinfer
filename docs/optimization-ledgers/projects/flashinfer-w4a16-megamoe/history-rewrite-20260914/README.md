# PR5019 history archive, squash and rebase

- Original public PR: https://github.com/flashinfer-ai/flashinfer/pull/5019
- Archive fork PR: https://github.com/zianglih/flashinfer/pull/3
- Frozen archive head: `archive/pr5019-history-20260914` at `8c975512665ec5de80d44cc54d1c8ed94a14f9f9`.
- Frozen archive base: `archive/pr5019-base-20260914` at `91bda04c66f7cb851e1ab3b78b9fecea644b9844`. The archive PR retains exactly 58 original commits, excluding unrelated commits between fork main and the original PR base.
- Squash on original base: `b6de75631550ddc3fad0a93b96fcac2460d4e1b7`; tree identical to the original head.
- Rebased single commit: `9e36b1f8073a717288436ea087328a82a4f3e246`, parent `8c94f70f49fbe17adb5deae5b2b48ff467346863`.

Only the `moe_ep` export list needed manual conflict resolution. It retains both upstream rank-major and W4A16 import/export entries. Three other overlapping files merged automatically: the distributed benchmark, architecture document and layer-validation tests. The remaining 31 PR paths, including the W4A16 kernel/backend and shared decoder, are byte-identical to the archive. The PR continues to change 35 files.

Scoped pre-commit, including mypy/Ruff, and Python syntax/conflict checks passed. The independent rebase audit found no compatibility blocker. GPU tests and benchmarks were not rerun. Existing evidence stays pinned to its measured revisions, especially because upstream routing changes can affect split timing.

Artifacts include the before/after patches, complete original commit log, source-preservation manifest, range-diff, pre-commit log, archive/public body drafts and independent review. See `manifest.json` for publication status.

An initial local archive-readback validation ran before its asynchronous read finished and failed to parse an empty file. The following squash commit attempt then stopped because its message file had not been created; no commit was created by that attempt. After the read completed, both remote archive refs and its full PR body were verified, the staged tree was proved identical to the archived head, and the squash/rebase completed normally.
