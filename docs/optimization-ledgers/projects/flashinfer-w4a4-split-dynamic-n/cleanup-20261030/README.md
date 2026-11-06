# Retained PR7290 implementation cleanup

Base: `658a0c8942c7454050f990c0be3083aa61b6a89f` on `codex/w4a4-split-dynamic-n`.
Cleanup is committed as `a1abebf1`; the table/CSV output extension is committed as `326c4a79`. Both are pushed to the upstream PR branch, and the primary `../flashinfer/` checkout is clean.

## Changes

- Swap-AB kernel: use the epilogue's existing activation state, discard an unused scheduler return binding, and express the repeated channel-tile MMA calls as one compile-time loop. Instruction order, accumulator offsets, iKET marker names and release placement are preserved.
- W4A16 kernel: build regular activation TMA views and select its atom only in the existing non-gather branch. Gather FC1 no longer constructs unused regular-TMA views.
- Finalizer: keep the original route mapping and test its sign directly, instead of first encoding validity as 0/1 for expanded input. Correct the stale comment referring to a standalone W4A16 permutation.
- Launchers: remove six full-extent W4A16 workspace views and their repeated sizing, reuse the existing CUDA stream helper, move swap-AB compilation-only calculations behind its cache miss, and remove duplicate alignment/layout work.
- Sanitizer harness: remove the one-value `apply_topk_in_fc1=False` parametrization. The worker contract and coverage stay the same. No sanitizer execution is requested.

## Audit boundaries

Reviewed PR kernel, launcher, tuner/API, benchmark, shared helper/quantizer, and accuracy/reference changes. Shared quantizer/helper changes are all live and remain untouched. Existing tuning policy, cache keys, numerical contract, public APIs, weight layout, register targets, pipeline barriers and PDL signaling remain unchanged. No rejected producer ownership experiment is included. Preserve existing comments and licensing; no broad documentation rewrite.

The old ownership experiment review copies have been retired. Their data and decisions remain in `../element-scale-ownership-20261029/`.

## Validation

- All 26 PR Python files parse successfully.
- Full PR scoped pre-commit passes, including mypy and Ruff: `pr-precommit.log`.
- W4A16 host contract: 480 configurations produce identical allocations and GEMM/finalize calls; every removed slice spans its entire tensor. See `check_host_contract.py` and `host-contract.json`.
- Swap-AB static proof: both channel-tile counts and iKET states preserve the MMA argument/call/marker trace; unrelated module AST is unchanged. See `swap-kernel/static-equivalence.json`.
- W4A16/finalizer static and peer review: see `W4A16_FINALIZE_REVIEW.md` and `w4a16-finalize-cleanup.json`.
- All 36 focused candidate exact cases and all 92 existing accuracy tests pass. All 48 paired kernels produce identical raw cubins, normalized PTX/SASS including encoded scheduling words, and native resources, with zero local memory. Sanitizer collection retains all 150 cases; none were executed. No performance claim is made by the cleanup alone.

A fresh full EP/TP performance run at `326c4a79` is being prepared, reusing existing baseline measurements. The PR refresh will keep heat maps, remove duplicate numerical speedup tables, and render native result table views directly rather than folding CSV blocks. Existing benchmark numbers are not relabeled as fresh measurements.
