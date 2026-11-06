# September 30 PR5319 rebase

Rebased onto upstream main `82e8eb1410c0e55f738b63f3638950a30726e863`, pushed head `b42dddd80322e180426d9eea5ac30884180fbefc` with an exact force-with-lease against `9c39a45529c4bbffd866f7ae6255b19eaf835aa7`. Backup branch: `backup/pr5319-before-rebase-20260930`.

The only conflict was #5682 moving FC2's dependency wait before scheduler routing reads. Preserve that upstream move and retain our unfused finalizer launch hint at the original point after cluster synchronization. #5497 now forwards PDL into W4A4 routing, so the finalizer docstring no longer claims non-PDL sorting. No other local behavior was changed; all upstream NVFP4 recipe changes and routing forwarding are retained.

Validation: all changed-file pre-commit hooks pass, including mypy/Ruff; `git diff --check origin/main...HEAD` passes; eight existing mocked CUTLASS CLI wiring cases and CLI help pass. Source comparison verifies the merged FC2 file equals upstream with only our existing seven-line hint inserted, the wait precedes routing reads, W4A16 and benchmark files are byte-identical to the previous head, and finalizer executable AST is unchanged. No GPU tests or benchmarks were rerun. Earlier C2 and benchmark evidence remains revision-specific; prior GitHub run36482176398 completed successfully at9c39a455.

Artifacts contain range-diff, full pre-commit/wiring output, upstream overlap diff, source checks, GitHub before/after snapshots and body validation. PR-body historical performance section is unchanged. The PR retains its four commits and six-file scope.

Commands (repository cwd):

```bash
pre-commit run --files $(git diff --name-only origin/main...HEAD)
git diff --check origin/main...HEAD
python3 ../audit/validate_cutlass_wiring.py
git range-diff a31c72523ae37d82fd657de36ce2b35156c3c559..backup/pr5319-before-rebase-20260930 origin/main..HEAD
```
