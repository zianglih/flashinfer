# FlashInfer #5319 rebase and current-upstream audit

Rebased `codex/w4a4-unfused-finalize-pdl` from `f9dd3c10541e087b716772245a9d033499745048` onto upstream `07e519fcc149f39e6dd00264149c092c2e37767e`. Candidate: `bde427290b33c55489e39c75d7e2a25365358ca0`. Backup branch: `backup/pr5319-pre-rebase-20260928`. Rebase changes only the integration of the original four commits; six-file scope retained.

## Conflict resolution

Preserved new upstream `skip_unpermute`, `gemm2_partial_out`, dual-tile launch sequence, and `_prepared_launches` callback/kwargs retention. The generic unfused branch now selects the shared CuTe reducer. Kept the PR's after-wait PDL hint distinct from upstream's optional before-wait hint. Existing native barriers, fences, epilogue stores, and producer tails remain in place.

See `PDL_AUDIT.md`, `NUMERIC_AUDIT.md`, `BENCH_RUNTIME_AUDIT.md`, and `artifacts/range-diff.txt` for source-level evidence and boundaries. No introduced static blocker was found. Optional scheduling/layout consolidation is unmeasured and was not added to this rebase.

## GPU validation setup

- c2 bare devbox `fi5319-rebase-0928`, namespace `ziangli`, eight B300 SXM6 GPUs allocated; native tests use GPU0, independent supplemental correctness checks use GPU1. EP8 is simulated on one GPU in each process; no distributed transport claim.
- Explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, newest NGC release providing CUDA13.2 at provisioning. Newer26.06-26.08 use CUDA13.3/13.4. Driver590.48.01, toolkit13.2.78.
- Python3.12.3, Torch2.12.0a0+5aff3928d8.nv26.05 (package metadata2.12.0a0+5aff3928d8.nv26.5.50603568); matching FlashInfer Python/cubin0.7.0.dev20260923 and jit-cache/SM103a0.7.0.dev20260923+cu130; CuTeDSL4.7.1, TVMFFI0.1.11, pytest9.1.1.
- Full source archive at candidate SHA, with full current Python/JIT/csrc/include. Gitlinks for cutlass/cccl/spdlog match nightly build b395280a, so only those vendor trees come from the wheel. No stale nightly build metadata is copied; source version sentinel0.0.0+unknown is expected.
- Nightly lacks the needed native MoE helper. Current native routing ABI differs, so current helpers compile once with JIT enabled. Current artifact registry also downloads matching BMM headers. Prebuilt compatible modules remain available.
- The full source archive hash and six changed-file hashes are recorded remotely. All task helpers remain outside the upstream patch.

## Commands and evidence

`install_nightly.sh`, `prepare_source.py`, `test_env.sh`, `run_native_tests.sh`, `run_supplemental.sh` under `scripts/` reproduce setup and tests. Native phases preserve original test tolerances and record per-case output plus JUnit XML. Supplemental checks use current native reduction as exact-bit oracle; FP16 scales promote exactly to FP32 for the oracle because native BF16 input has no FP16-scale specialization. Zero-token checks exercise only the new helper's no-op contract.

Host changed-file pre-commit and eight mocked benchmark CLI wiring cases pass. GPU results are recorded in artifacts upon completion; do not infer pass from this setup note. September18 performance tables remain historical f9dd3c-versus-eb5f05 measurements; this rebase does not rerun or relabel them as current-head timings.

## Completed results

- Candidate `bde427290b33c55489e39c75d7e2a25365358ca0` passed **155 upstream tests**: core129, prepared15, prepared-unfused11. Zero failures/errors/skips. Raw summaries: `129 passed, 3016 warnings in 349.30s`; `15 passed, 713 warnings in 25.03s`; `11 passed, 470 warnings in 16.55s`. Warnings are retained in full logs.
- Standalone expanded107 and permuted107 cases pass (104 nonempty +3 zero-token no-ops per layout). Includes FP16 scales using exactly promoted FP32 native oracle and FP32/BF16 matching native scales; subnormal and cancellation matrices, poisoned unused rows, launch transitions, eager/graph and PDL off/on.
- W4A8 unfused: 12 configurations,48 phases,96 exact native-oracle comparisons pass, with graph/eager and PDL off/on equality and all-nonlocal zeros.
- Full remote logs, JUnit, source/runtime hashes, and exact helper scripts: `c2-evidence.tar.gz`, SHA256 `ed21f540e4768e398be4727fc70e773049fba90cf36f14b02576973476e0a39f`; extracted under `c2/`.
- All six tested changed-file hashes match the clean local checkout. Rebased branch pushed with explicit lease on old head `f9dd3c10541e087b716772245a9d033499745048`; push confirmed replacement by `bde42729`.
- No additional source changes or upstream test files were needed. Historical benchmark tables are retained as pre-rebase evidence; no fresh performance claim is made.

## Publication and cleanup

PR #5319 body was updated and read back byte-for-byte: SHA256 `7e4243bbba1e3fc8e1a7b8df71f17d18d1c3aaf53a093dd9f40b9bf4e42bfc20`. GitHub confirms head `bde42729`, base `07e519fc`, ready (`isDraft=false`), and `MERGEABLE`. GitHub pre-commit and Public API/documentation checks pass. PR Test did not execute its GPU matrix: current run36468930841 reports `CI skipped — pending authorization`, so its summary check is red. Build Docs was still running at final readback; the c2 tests above are independent actual GPU results.

After the full evidence archive was recovered and publication verified, the temporary c2 devbox was released with managed `/usr/local/bin/h delete fi5319-rebase-0928 -c c2 -n ziangli --force`. Cleanup output is retained in `artifacts/devbox-cleanup.log`. Repository working tree is clean, and GitHub CLI identity remains `zianglih`.
